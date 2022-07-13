from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from posts.models import User


class TestingViewsInUsers(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Создать таблицы. """
        super().setUpClass()

        # Создать пользователя.
        cls.user = User.objects.create(
            username='leo'
        )

        cls.urls = {
            'signup': reverse('users:signup')
        }

    def setUp(self):
        """ Создать авторизированного пользователя. """
        self.authorized_client = Client()

        # Авторизировать пользователя.
        self.authorized_client.force_login(TestingViewsInUsers.user)

    def test_correct_show_signup_form(self):
        """ Тестируем форму для регистрации. """
        response = self.authorized_client.get(self.urls['signup'])

        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]

                self.assertIsInstance(form_field, expected)
