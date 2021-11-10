import tempfile
from random import randint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(
            dir=settings.BASE_DIR, prefix='test_'
        )

        Group.objects.create(
            title='Тестовый заголовок группы',
            description='Тестовое описание группы',
            slug='test-group'
        )

        cls.group1 = Group.objects.get(id=1)

    def setUp(self):
        self.user = User.objects.create_user(username='Andrey')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        """Проверка создания нового поста"""
        random_text = str(randint(1000, 9999))
        form_data = {
            'text': 'Тестовый текст записи ' + random_text,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        self.assertTrue(
            Post.objects.get(text='Тестовый текст записи ' + random_text)
        )
        self.assertEqual(response.status_code, 200)

    def test_create_new_post_with_group(self):
        """Проверка создания нового поста в группе"""
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст записи',
            'group': self.group1.id,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertEqual(response.status_code, 200)

    def test_create_new_post_empty(self):
        """Проверка отправки пустого поста"""
        form_data = {
            'text': '',
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        self.assertFalse(response.context.get('form').is_valid())
        self.assertEqual(response.status_code, 200)

    def test_edit_post_with_group(self):
        """Проверка редактирования поста"""
        tasks_count = Post.objects.count()
        Post.objects.create(
            text='Тестовый текст записи',
            author=User.objects.get(username=self.user.username),
            group=self.group1,
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)

        post = Post.objects.get(pk=1, author__username=self.user.username)
        form_data = {
            'text': 'Тестовый текст измененной записи',
            'group': self.group1.id,
        }
        response = self.authorized_client.post(
            reverse(
                'post_edit',
                kwargs={'username': self.user.username, 'post_id': post.id}
            ),
            data=form_data,
            follow=True
        )

        task_username_0 = response.context['profile'].username
        task_text_0 = response.context['post'].text

        self.assertEqual(task_username_0, self.user.username)
        self.assertEqual(task_text_0, form_data['text'])
        self.assertRedirects(
            response, f'/{self.user.username}/{post.id}/', status_code=302,
            target_status_code=200, fetch_redirect_response=True
        )

    def test_create_new_post_with_image(self):
        """Проверка создания нового поста с картинкой"""

        posts_count = Post.objects.count()
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

        form_data = {
            'text': 'Тестовый текст записи с картинкой',
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True,

        )

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                image='posts/' + form_data['image'].name,
            ).exists()
        )


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='andrey')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
