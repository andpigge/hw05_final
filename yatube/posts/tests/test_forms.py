import tempfile
import shutil
import os

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, User, Comment


# Создать временную папку для медиа-файлов;
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создать пользователя.
        cls.user = User.objects.create(
            username='leo'
        )

        # Создать группу.
        cls.group = Group.objects.create(
            title='Котики',
            slug='category-cats',
            description='Мир котиков уникальный',
        )

        # Создать пост.
        cls.post = Post.objects.create(
            text='Описание поста',
            author=cls.user,
            group=cls.group
        )

        cls.urls = {
            'post_create': reverse('posts:post_create'),
            'post_edit': reverse(
                'posts:post_edit',
                kwargs={'post_id': TaskCreateFormTests.post.pk}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': TaskCreateFormTests.post.author.username}
            ),
            'post_detail': reverse(
                'posts:post_detail',
                kwargs={'post_id': TaskCreateFormTests.post.pk}
            ),
            'add_comment': reverse(
                'posts:add_comment',
                kwargs={'post_id': TaskCreateFormTests.post.pk}
            )
        }

        # Тестовая картинка из 2 пикселей в байт-коде
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        # Удалить временную папку для медиа-файлов
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()

        # Авторизировать пользователя автора поста.
        self.authorized_client.force_login(TaskCreateFormTests.user)

    def get_name_with_hash(self, name):
        salt = os.urandom(8).decode('latin-1')

        hash_int = hash(salt)

        return f'{name}_{str(hash_int)[1:8]}.gif'

    def test_check_form_page_creation_post(self):
        """ Проверка успешного создания поста, после успешной валидации. """
        post_count = Post.objects.count()

        # Эмуляция файла картинки
        uploaded = SimpleUploadedFile(
            name=self.get_name_with_hash('small_gif'),
            content=self.small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Описание поста',
            'group': TaskCreateFormTests.group.id,
            'image': uploaded
        }

        response = self.authorized_client.post(
            self.urls['post_create'], data=form_data, follow=False)

        # Проверяем, сработал ли редирект
        self.assertRedirects(response, self.urls['profile'])

        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)

        # Проверяем, что создалась запись с нашим слагом
        self.assertTrue(
            Post.objects.filter(
                text='Описание поста',
                group=TaskCreateFormTests.group,
                author=TaskCreateFormTests.user,
                pk=Post.objects.latest('id').id,
                image=f'posts/{uploaded}'
            ).exists()
        )

    def test_check_form_page_edit_user(self):
        """ Проверка успешного редактирования поста,
            после успешной валидации. """
        group_loser = Group.objects.create(
            title='Лузеры',
            slug='category-loser',
            description='Записываемся в лузеры',
        )

        post_count = Post.objects.count()

        # Эмуляция файла картинки
        uploaded = SimpleUploadedFile(
            name=self.get_name_with_hash('small_gif'),
            content=self.small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Изменить пост',
            'group': group_loser.id,
            'image': uploaded
        }

        response = self.authorized_client.post(
            self.urls['post_edit'], data=form_data, follow=False)

        # Проверяем, сработал ли редирект
        self.assertRedirects(response, self.urls['post_detail'])

        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count)

        # Проверяем, что изменилась запись
        self.assertTrue(
            Post.objects.filter(
                text='Изменить пост',
                group=group_loser,
                author=TaskCreateFormTests.user,
                pk=Post.objects.latest('id').id,
                image=f'posts/{uploaded}'
            ).exists()
        )

    def test_check_form_page_creation_comment(self):
        """ Проверка успешного создания комментария,
            после успешной валидации. """
        comment_count = Comment.objects.count()

        form_data = {
            'post': TaskCreateFormTests.post,
            'author': TaskCreateFormTests.user,
            'text': 'Тестовый комментарий'
        }

        response = self.authorized_client.post(
            self.urls['add_comment'], data=form_data, follow=False)

        # Проверяем, сработал ли редирект
        self.assertRedirects(response, self.urls['post_detail'])

        # Проверяем, увеличилось ли число постов
        self.assertEqual(Comment.objects.count(), comment_count + 1)

        # Проверяем, что изменилась запись
        self.assertTrue(
            Comment.objects.filter(
                post=TaskCreateFormTests.post,
                author=TaskCreateFormTests.user,
                text='Тестовый комментарий'
            ).exists()
        )

    def test_correct_creating_group_without_slug(self):
        """ Проверка что группа создается без slug. """
        Group.objects.create(
            title='Любители',
            description='Страна чудес'
        )

        group_count = Group.objects.count()

        # Проверяем, увеличилось ли число постов
        self.assertEqual(Group.objects.count(), group_count)

        # Проверяем, что запись создана без slug
        self.assertTrue(
            Group.objects.filter(title='Любители').exists())
