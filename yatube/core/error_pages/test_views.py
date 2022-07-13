from django.test import TestCase, Client

from http import HTTPStatus

from posts.models import User


class TestingViewsInPosts(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(
            username='leo'
        )

        cls.TEMPLATE_FOR_NOT_FOUND_PAGES = 'core/404.html'

        cls.URL_FOR_NOT_FOUND_PAGES = 'page_not_found'

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()

        # Авторизировать пользователя.
        self.authorized_client.force_login(TestingViewsInPosts.user)

    def test_not_found_pages_uses_correct_templates(self):
        """ Проверка статус код 404 для несуществующей страницы. """

        # Авторизированный пользовать, запрос к несуществующей странице
        response_authorized = self.authorized_client.get(
            self.URL_FOR_NOT_FOUND_PAGES
        )

        self.assertEqual(response_authorized.status_code, HTTPStatus.NOT_FOUND)

        # Неавторизованный пользовать, запрос к несуществующей странице
        response_guest = self.guest_client.get(self.URL_FOR_NOT_FOUND_PAGES)

        self.assertEqual(response_guest.status_code, HTTPStatus.NOT_FOUND)

    def test_check_template_for_match_not_found_pages(self):
        """ Проверка соответствие шаблонов для не найденных страниц. """
        response = self.guest_client.get(self.URL_FOR_NOT_FOUND_PAGES)

        self.assertTemplateUsed(response, self.TEMPLATE_FOR_NOT_FOUND_PAGES)
