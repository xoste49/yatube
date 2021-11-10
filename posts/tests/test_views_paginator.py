from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    """Здесь создаются фикстуры: клиент и 13 тестовых записей."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='admin')

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

        """Всего 16 постов, 14 постов в группе и 2 поста без группы"""
        Post.objects.create(
            text='Тестовый пост',
            author=User.objects.get(username='admin'),
            group=None,
        )

        Post.objects.create(
            text='Тестовый пост2',
            author=User.objects.get(username='admin'),
            group=None,
        )

        """ 14 постов в группе"""
        for post_number in range(14):
            Post.objects.create(
                text=f'Тестовый пост в группе {post_number}',
                author=User.objects.get(username='admin'),
                group=Group.objects.get(slug='test-group'),
            )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create_user(username='Andrey')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_containse_ten_records(self):
        """Проверка: количество постов на первой странице равно 10."""
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        """Проверка: на второй странице должно быть три поста."""
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 6)

    def test_first_page_group_containse_ten_records(self):
        """проверка: количество постов на первой странице равно 10."""
        response = self.client.get(
            reverse('group', kwargs={'slug': 'test-group'})
        )
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_group_containse_three_records(self):
        """Проверка: на второй странице должно быть три поста."""
        response = self.client.get(
            reverse('group', kwargs={'slug': 'test-group'}) + '?page=2'
        )
        self.assertEqual(len(response.context.get('page').object_list), 4)
