from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class AboutURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }

    def setUp(self):
        self.guest_client = Client()

    """
    Проверяем общедоступные страницы
    """
    def test_urls_exists_at_desired_location(self):
        """
        Страница /about/author/ и /about/tech/
        доступна любому пользователю.
        """
        for template, url in self.templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    """
    Проверка вызываемых шаблонов для каждого адреса
    """
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
