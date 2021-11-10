import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, Follow, Comment

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        Group.objects.create(
            title='Тестовый заголовок группы',
            description='Тестовое описание группы',
            slug='test-group'
        )

        Group.objects.create(
            title='Тестовый заголовок группы 2',
            description='Тестовое описание группы 2',
            slug='test-group2'
        )

        Group.objects.create(
            title='Тестовый заголовок группы 3',
            description='Тестовое описание группы 3',
            slug='test-group3'
        )

        Post.objects.create(
            text='Тестовый пост 0 admin',
            author=User.objects.create_user(username='admin'),
            group=None,
        )

        Post.objects.create(
            text='Тестовый пост в группе 0 admin2',
            author=User.objects.create_user(username='admin2'),
            group=Group.objects.get(slug='test-group'),
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        Post.objects.create(
            text='пост с изображением в группе',
            author=User.objects.create_user(username='Andrey'),
            group=Group.objects.get(slug='test-group2'),
            image=uploaded
        )

    def setUp(self):
        self.guest_client = Client()

        self.anonymous_user = AnonymousUser()

        self.user = User.objects.get(username='Andrey')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_leo = User.objects.create(username='leo')
        self.authorized_client_leo = Client()
        self.authorized_client_leo.force_login(self.user_leo)
        self.user_admin = User.objects.get(username='admin')
        self.authorized_client_admin = Client()
        self.authorized_client_admin.force_login(self.user_admin)

    """
    Проверяем используемые шаблоны
    """
    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': (
                reverse('group', kwargs={'slug': 'test-group'})
            ),
            'post_form.html': reverse('new_post'),
            'post.html': (
                reverse('post', kwargs={
                    'username': Post.objects.get(pk=2).author.username,
                    'post_id': Post.objects.get(pk=2).id
                })
            ),
            'profile.html': reverse(
                'profile',
                kwargs={'username': Post.objects.get(pk=2).author.username}
            ),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # <editor-fold desc="Test context">
    def test_home_page_shows_correct_context(self):
        """Шаблон home (index) сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))

        first_object = response.context['page'][2]
        task_text_0 = first_object.text

        self.assertEqual(task_text_0, 'Тестовый пост 0 admin')

    def test_group_pages_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-group'})
        )
        self.assertEqual(
            response.context['group'].title, 'Тестовый заголовок группы'
        )
        self.assertEqual(
            response.context['group'].description, 'Тестовое описание группы'
        )
        self.assertEqual(
            response.context['group'].slug, 'test-group'
        )

    def test_new_post_page_shows_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_home_with_group_page_shows_correct_context(self):
        """
        Шаблон home (index) с группой сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(reverse('index'))

        first_object = response.context['page'][0]
        task_text_0 = first_object.text
        task_group_title_0 = first_object.group.title
        task_group_desc_0 = first_object.group.description

        self.assertEqual(task_text_0, 'пост с изображением в группе')
        self.assertEqual(task_group_title_0, 'Тестовый заголовок группы 2')
        self.assertEqual(task_group_desc_0, 'Тестовое описание группы 2')

    def test_post_in_group_page_shows_correct_context(self):
        """
        Шаблон post в группе сформирован
        с правильным контекстом на странице с группой.
        """
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-group2'})
        )

        first_object = response.context['page'][0]
        task_text_0 = first_object.text
        task_group_title_0 = first_object.group.title
        task_group_desc_0 = first_object.group.description

        self.assertEqual(task_text_0, 'пост с изображением в группе')
        self.assertEqual(task_group_title_0, 'Тестовый заголовок группы 2')
        self.assertEqual(task_group_desc_0, 'Тестовое описание группы 2')

    def test_post_in_other_group_page_not_shows_context(self):
        """
        Шаблон post в группе сформирован с правильным контекстом и
        не отображается на странице другой группы.
        """
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-group3'})
        )

        first_object = response.context['page']
        if len(first_object) == 0:
            self.assertEqual(len(first_object), 0)
            return 1
        task_text_0 = first_object.text
        task_group_title_0 = first_object.group.title
        task_group_desc_0 = first_object.group.description

        self.assertEqual(not task_text_0, 'Тестовый пост в группе')
        self.assertEqual(not task_group_title_0, 'Тестовый заголовок группы')
        self.assertEqual(
            not task_group_desc_0,
            'Тестовое описание группы'
        )

    def test_home_page_search_shows_correct_context(self):
        """Шаблон home (index) с поиском сформирован
        с правильным контекстом."""
        response = self.authorized_client.get(reverse('index') + '?q=в группе')

        first_object = response.context['page'][0]
        task_text_0 = first_object.text
        task_group_title_0 = first_object.group.title
        task_group_desc_0 = first_object.group.description

        self.assertEqual(task_text_0, 'пост с изображением в группе')
        self.assertEqual(task_group_title_0, 'Тестовый заголовок группы 2')
        self.assertEqual(task_group_desc_0, 'Тестовое описание группы 2')

    def test_edit_post_shows_correct_context(self):
        """
        Шаблон редактирования поста (post_edit)
        сформирован с правильным контекстом.
        """
        response = self.authorized_client_admin.get(
            reverse(
                'post_edit', kwargs={'username': 'admin', 'post_id': '1'}
            )
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        first_object = response.context['is_edit']

        self.assertTrue(first_object)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_shows_correct_context(self):
        """
        Шаблон профайла пользователя (profile)
        сформирован с правильным контекстом.
        """
        response = self.authorized_client_admin.get(
            reverse('profile', kwargs={'username': 'Andrey'})
        )

        first_object = response.context['profile']
        second_object = response.context['page'][0]

        task_username = first_object.username
        task_text_0 = second_object.text
        task_group_title_0 = second_object.group.title
        task_group_desc_0 = second_object.group.description
        self.assertEqual(task_username, 'Andrey')
        self.assertEqual(task_text_0, 'пост с изображением в группе')
        self.assertEqual(task_group_title_0, 'Тестовый заголовок группы 2')
        self.assertEqual(task_group_desc_0, 'Тестовое описание группы 2')

    def test_post_user_shows_correct_context(self):
        """
        Шаблон отдельного поста пользователя (post)
        сформирован с правильным контекстом.
        """
        response = self.authorized_client_admin.get(
            reverse('post', kwargs={'username': 'Andrey', 'post_id': 3})
        )

        first_object = response.context['profile']
        second_object = response.context['post']

        task_username = first_object.username
        task_text_0 = second_object.text
        task_group_title_0 = second_object.group.title
        task_group_desc_0 = second_object.group.description
        self.assertEqual(task_username, 'Andrey')
        self.assertEqual(task_text_0, 'пост с изображением в группе')
        self.assertEqual(task_group_title_0, 'Тестовый заголовок группы 2')
        self.assertEqual(task_group_desc_0, 'Тестовое описание группы 2')

    def test_img_index_shows_correct_context(self):
        """
        Проверяет, что при выводе поста с картинкой на главной странице
        изображение передаётся в словаре context
        """
        response = self.authorized_client_admin.get(reverse('index'))

        first_object = response.context['page'][0]
        task_image_0 = first_object.image.path

        i = Post.objects.get(
            text='пост с изображением в группе'
        ).image.path
        self.assertEqual(task_image_0, i)

    def test_img_profile_shows_correct_context(self):
        """
        Проверяет, что при выводе поста с картинкой на странице профиля
        изображение передаётся в словаре context
        """
        response = self.authorized_client_admin.get(
            reverse('profile', kwargs={'username': 'Andrey'})
        )

        first_object = response.context['page'][0]
        task_image_0 = first_object.image.path

        i = Post.objects.get(
            text='пост с изображением в группе'
        ).image.path
        self.assertEqual(task_image_0, i)

    def test_img_group_shows_correct_context(self):
        """
        Проверяет, что при выводе поста с картинкой на странице группы
        изображение передаётся в словаре context
        """
        response = self.authorized_client_admin.get(
            reverse('group', kwargs={'slug': 'test-group2'})
        )

        first_object = response.context['page'][0]
        task_image_0 = first_object.image.path

        i = Post.objects.get(
            text='пост с изображением в группе'
        ).image.path

        self.assertEqual(task_image_0, i)

    def test_img_post_shows_correct_context(self):
        """
        Проверяет, что при выводе поста с картинкой на отдельной странице поста
        изображение передаётся в словаре context
        """
        post = Post.objects.get(text='пост с изображением в группе')
        response = self.authorized_client_admin.get(
            reverse(
                'post',
                kwargs={'username': post.author.username, 'post_id': post.id},
            )
        )

        first_object = response.context['post']
        task_image_0 = first_object.image.path

        i = post.image.path
        self.assertEqual(task_image_0, i)
    # </editor-fold>

    # <editor-fold desc="Test user follow">
    def test_user_follow_profile(self):
        """
        Проверяет, что авторизованный пользователь может подписываться
        на других пользователей
        """
        author = self.user
        response = self.authorized_client_admin.get(
            reverse(
                'profile_follow',
                kwargs={'username': author.username},
            )
        )
        following = Follow.objects.filter(
            author=author, user=self.user_admin
        )

        self.assertRedirects(
            response, f'/{author.username}/', status_code=302,
            target_status_code=200, fetch_redirect_response=True
        )
        self.assertTrue(following)

    def test_user_unfollow_profile(self):
        """
        Проверяет, что авторизованный пользователь может удалять
        пользователей из подписок
        """
        author = self.user
        response = self.authorized_client_leo.get(
            reverse(
                'profile_follow',
                kwargs={'username': author.username},
            )
        )
        self.assertRedirects(
            response, f'/{author.username}/', status_code=302,
            target_status_code=200, fetch_redirect_response=True
        )

        response = self.authorized_client_leo.get(
            reverse(
                'profile_unfollow',
                kwargs={'username': author.username},
            )
        )
        following = Follow.objects.filter(
            author=author, user=self.user_leo
        )

        self.assertRedirects(
            response, f'/{author.username}/', status_code=302,
            target_status_code=200, fetch_redirect_response=True
        )
        self.assertFalse(following)

    def test_guest_no_follow_profile(self):
        """
        Проверяет, что гость не может подписываться
        на других пользователей
        """
        author = self.user
        response = self.guest_client.get(
            reverse(
                'profile_follow',
                kwargs={'username': author.username},
            )
        )
        following = Follow.objects.filter(author=author)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(following)

    def test_guest_no_unfollow_profile(self):
        """
        Проверяет, что гость не может удалять
        пользователей из подписок
        """
        author = self.user
        response = self.guest_client.get(
            reverse(
                'profile_follow',
                kwargs={'username': author.username},
            )
        )
        self.assertEqual(response.status_code, 302)

        response = self.guest_client.get(
            reverse(
                'profile_unfollow',
                kwargs={'username': author.username},
            )
        )
        following = Follow.objects.filter(
            author=author
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(following)

    def test_author_no_follow_to_himself(self):
        """
        Проверяет, что авторизованный пользователь не может подписываться
        на себя
        """
        author = self.user
        response = self.authorized_client.get(
            reverse(
                'profile_follow',
                kwargs={'username': author.username},
            )
        )
        following = Follow.objects.filter(
            author=author, user=author
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(following)
    # </editor-fold>

    # <editor-fold desc="Test comment">
    def test_user_comment_auth_user(self):
        """
        Проверяет, что только авторизированный пользователь
        может комментировать посты.
        """
        author_user = self.user
        author_username = author_user.username
        post_id = Post.objects.filter(author=author_user)[0].id
        form_data = {
            'text': 'Тестовый комментарий к записи',
        }
        response = self.authorized_client_admin.post(
            reverse(
                'add_comment',
                kwargs={
                    'username': author_username,
                    'post_id': post_id,
                },
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response, f'/{author_username}/{post_id}/', status_code=302,
            target_status_code=200, fetch_redirect_response=True
        )
        self.assertEqual(
            Comment.objects.all().filter(text=form_data['text']).count(), 1
        )

    def test_user_comment_guest_user(self):
        """
        Проверяет, что только авторизированный пользователь
        может комментировать посты.
        """
        author_user = self.user
        author_username = author_user.username
        post_id = Post.objects.filter(author=author_user)[0].id
        form_data = {
            'text': 'Тестовый комментарий к записи2',
        }
        response = self.guest_client.post(
            reverse(
                'add_comment',
                kwargs={
                    'username': author_username,
                    'post_id': post_id,
                },
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Comment.objects.all().filter(text=form_data['text']).count(), 0
        )
    # </editor-fold>

    def test_follow_index_page_shows_correct_context(self):
        """
        Шаблон Избранные авторы (follow_index) сформирован
        с правильным контекстом.

        Новая запись пользователя
        появляется в ленте тех, кто на него подписан
        и не появляется в ленте тех, кто не подписан на него.

        user_leo подписан на user
        user_admin не подписан на user
        """
        Follow.objects.create(author=self.user, user=self.user_leo)

        r_follow = self.authorized_client_leo.get(reverse('follow_index'))
        r_nofollow = self.authorized_client_admin.get(reverse('follow_index'))

        first_object = r_follow.context['page']
        second_object = r_nofollow.context['page']

        task_text_follow = first_object[0].text
        count_follow = len(first_object)
        count_nofollow = len(second_object)

        self.assertEqual(
            task_text_follow, 'пост с изображением в группе'
        )
        self.assertTrue(count_follow >= 1)
        self.assertEqual(count_nofollow, 0)


# <editor-fold desc="Test Errors">
class ErrorsViewsTest(TestCase):
    """Проверка ошибок на страницах"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()

    def test_page_not_found(self):
        """Страница blablabla сформирован с правильной ошибкой."""
        response = self.guest_client.get('/sdsdasdads/')

        self.assertEqual(response.status_code, 404)
# </editor-fold>
