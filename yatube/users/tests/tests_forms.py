from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User


class TaskCreateFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

        self.urls = {
            'signup': reverse('users:signup'),
            'index': reverse('posts:index')
        }

    def test_check_form_creation_user(self):
        """ Проверка формы создания пользователя. """
        post_count = User.objects.count()

        form_data = {
            'first_name': 'Рустам',
            'last_name': 'Рахимов',
            'username': 'andpigge',
            'email': 'rustamaaa@bk.ru',
            'password1': 'andpigge1andpigge1',
            'password2': 'andpigge1andpigge1'
        }

        response = self.guest_client.post(
            self.urls['signup'], data=form_data, follow=True)

        # Проверяем, сработал ли редирект
        self.assertRedirects(response, self.urls['index'])

        # Проверяем, увеличилось ли число авторов
        self.assertEqual(User.objects.count(), post_count + 1)

        # Проверяем, появился ли созданный автор
        self.assertTrue(
            User.objects.filter(
                first_name='Рустам',
                last_name='Рахимов',
                username='andpigge',
                email='rustamaaa@bk.ru'
            ).exists()
        )
