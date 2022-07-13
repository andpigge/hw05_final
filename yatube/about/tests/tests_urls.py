from django.test import TestCase, Client
from django.urls import reverse

from http import HTTPStatus


class StaticPagesURLTests(TestCase):
    urls_and_templates = {
        reverse('about:author'): 'about/author.html',
        reverse('about:tech'): 'about/tech.html'
    }

    def setUp(self):
        """ Создать не авторизированного пользователя. """
        self.guest_client = Client()

    def test_check_status_code(self):
        """ Проверка доступности адресов. """
        for url in self.urls_and_templates:
            response = self.guest_client.get(url)

            with self.subTest(url=url):
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )
