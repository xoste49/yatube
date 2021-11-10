from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Group.objects.create(
            title='Тестовый заголовок группы',
            description='Тестовое описание группы',
            slug='test-group'
        )

        Post.objects.create(
            text='Тестовый пост',
            author=User.objects.create_user(username='pavel'),
            group=Group.objects.get(slug='test-group'),
        )

        cls.templates_url_names = {
            '/': 'index.html',
            '/group/test-group/': 'group.html',
            '/new/': 'post_form.html',
            '/pavel/1/edit/': 'post_form.html',
        }

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create_user(username='Andrey')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.user_pavel = User.objects.get(username='pavel')
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user_pavel)

    """
    Проверяем общедоступные страницы
    """
    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_exists_at_desired_location(self):
        """Страница /new/ не доступна любому пользователю."""
        response = self.guest_client.get('/new/')
        self.assertEqual(response.status_code, 302)

    def test_group_url_exists_at_desired_location(self):
        """Страница /group/test-group/ доступна любому пользователю."""
        response = self.authorized_client.get('/group/test-group/')
        self.assertEqual(response.status_code, 200)

    def test_user_url_exists_at_desired_location(self):
        """Страница /<username>/ доступна любому пользователю."""
        response = self.guest_client.get('/' + self.user.username + '/')
        self.assertEqual(response.status_code, 200)

    def test_post_user_url_exists_at_desired_location(self):
        """Страница /<username>/<post_id>/ доступна любому пользователю."""
        post = Post.objects.select_related(
            'author'
        ).filter(author__username='pavel').order_by("-pub_date")
        username = post[0].author.username
        post_id = post[0].id
        response = self.guest_client.get(f'/{ username }/{ post_id }/')
        self.assertEqual(response.status_code, 200)

    def test_edit_post_guest_user_url_exists_at_desired_location(self):
        """
        Страница редактирование (/<username>/<post_id>/edit/)
        не доступна любому пользователю.
        """
        post = Post.objects.select_related(
            'author'
        ).filter(author__username='pavel').order_by("-pub_date")
        username = post[0].author.username
        post_id = post[0].id
        response = self.guest_client.get(f'/{ username }/{ post_id }/edit/')
        self.assertEqual(response.status_code, 302)

    """
    Проверяем доступность страниц для авторизованного пользователя
    """
    def test_urls_exists_at_desired_location_authorized(self):
        """Страницы доступны авторизованному пользователю."""
        for reverse_name, template in self.templates_url_names.items():
            with self.subTest():
                response = self.authorized_client_author.get(reverse_name)
                self.assertEqual(response.status_code, 200)

    def test_edit_post_author_user_url_exists_at_desired_location(self):
        """
        Страница редактирование (/<username>/<post_id>/edit/)
        доступна автору.
        """
        post = Post.objects.select_related(
            'author'
        ).filter(author__username='pavel').order_by("-pub_date")
        username = post[0].author.username
        post_id = post[0].id
        response = self.authorized_client_author.get(
            f'/{ username }/{ post_id }/edit/'
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_post_other_user_url_exists_at_desired_location(self):
        """
        Страница редактирование (/<username>/<post_id>/edit/)
        не доступна другому пользователю.
        """
        post = Post.objects.select_related(
            'author'
        ).filter(author__username='pavel').order_by("-pub_date")
        username = post[0].author.username
        post_id = post[0].id
        response = self.authorized_client.get(
            f'/{ username }/{ post_id }/edit/'
        )
        self.assertEqual(response.status_code, 302)

    def test_redirect_edit_post_other_user_url_exists_at_desired_locat(self):
        """
        Редирект со страницы /<username>/<post_id>/edit/
        для тех, у кого нет прав доступа к этой странице.
        """
        post = Post.objects.select_related(
            'author'
        ).filter(author__username='pavel').order_by("-pub_date")
        username = post[0].author.username
        post_id = post[0].id
        response = self.authorized_client.get(f'/{username}/{post_id}/edit/')
        self.assertRedirects(
            response, f'/{username}/{post_id}/', status_code=302,
            target_status_code=200, fetch_redirect_response=True
        )

    """
    Проверка вызываемых шаблонов для каждого адреса
    """
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_url_names.items():
            with self.subTest():
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)
