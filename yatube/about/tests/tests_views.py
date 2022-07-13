from django.test import TestCase, Client
from django.urls import reverse


class TestingViewsInAbout(TestCase):
    urls_and_templates = {
        reverse('about:author'): 'about/author.html',
        reverse('about:tech'): 'about/tech.html'
    }

    def setUp(self):
        """ Создать не авторизированного пользователя. """
        self.guest_client = Client()

    def test_pages_uses_correct_templates(self):
        """ Проверка корректности шаблонов. """
        for url, template in self.urls_and_templates.items():
            response = self.guest_client.get(url)

            with self.subTest(url=url):
                self.assertTemplateUsed(
                    response,
                    template
                )
