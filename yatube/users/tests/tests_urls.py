from django.test import TestCase, Client
from django.urls import reverse

from http import HTTPStatus

from posts.models import User


class TestingUrlsInPosts(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Создать таблицы. """
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='leo'
        )

        cls.urls_private = (
            reverse('users:reset_form'),
            reverse('users:reset'),
            reverse('users:reset_done'),
            reverse('users:change'),
            reverse('users:done')
        )

        cls.urls_public = (
            reverse('users:login'),
            reverse('users:signup'),
            reverse('users:logout')
        )

    def setUp(self):
        """ Создать авторизированного и не авторизированного пользователя. """
        self.guest_client = Client()

        self.authorized_client = Client()

        # Авторизировать пользователя.
        self.authorized_client.force_login(TestingUrlsInPosts.user)

    def test_check_status_code_for_not_authorized_user(self):
        """ Проверка доступности публичных адресов,
            неавторизированным пользователям. """
        for url in self.urls_public:
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_check_redirect_not_authorized_user(self):
        """ Проверка перенаправления неавторизированного пользователя. """
        login = reverse('users:login')

        for url in self.urls_private:
            response = self.guest_client.get(url, follow=True)

            redirect = f'{login}?next={url}'

            with self.subTest(url=url):
                self.assertRedirects(
                    response,
                    redirect
                )

    def test_check_status_code_for_authorized_user(self):
        """ Проверка доступности приватных адресов,
            авторизированным пользователям. """
        for url in self.urls_private:
            with self.subTest(url=url):
                self.assertEqual(
                    self.authorized_client.get(url).status_code,
                    HTTPStatus.OK
                )
