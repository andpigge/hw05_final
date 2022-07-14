from django.test import TestCase, Client
from django.urls import reverse

from http import HTTPStatus

from posts.models import Post, Group, User, Comment


class TestingUrlsInPosts(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Создать таблицы. """
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

        # Создать комментарий.
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Комментарий. Мне понравился этот котик.'
        )

        cls.urls = {
            'post_edit': reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.pk}
            ),
            'post_create': reverse('posts:post_create'),
            'follow_index': reverse('posts:follow_index'),
            'follow_author': reverse(
                'posts:follow_author',
                kwargs={'username': cls.user.username}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            ),
            'post_detail': reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.pk}
            ),
            'index': reverse('posts:index'),
            'login': reverse('users:login'),
            'page_not_found': '/no_correct/'
        }

        cls.urls_redirect = {
            reverse(
                'posts:profile_follow',
                kwargs={'username': cls.user.username}
            ): cls.urls['profile'],
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': cls.user.username}
            ): cls.urls['profile'],
            reverse(
                'posts:add_comment',
                kwargs={'post_id': cls.post.pk}
            ): cls.urls['post_detail'],
            reverse(
                'posts:comment_delete',
                kwargs={'comment_id': cls.comment.pk}
            ): cls.urls['post_detail'],
            reverse(
                'posts:post_delete',
                kwargs={'post_id': cls.post.pk}
            ): cls.urls['index']
        }

        cls.urls_public = (
            reverse('posts:index'),
            reverse(
                'posts:group_posts',
                kwargs={'slug': cls.post.group.slug}
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.pk}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': cls.post.author.username}
            )
        )

        cls.urls_private = (
            reverse('posts:post_create'),
            reverse('posts:follow_index'),
            reverse(
                'posts:follow_author',
                kwargs={'username': cls.user.username}
            )
        )

    def setUp(self):
        """ Создать авторизированного и не авторизированного пользователя. """
        self.guest_client = Client()

        self.authorized_client = Client()

        # Авторизировать пользователя.
        self.authorized_client.force_login(TestingUrlsInPosts.user)

    def test_check_status_code_for_not_authorized_user(self):
        """
        Проверка доступности публичных адресов,
        неавторизированным пользователям.
        """
        for url in self.urls_public:
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_check_redirect_not_authorized_user(self):
        """ Проверка перенаправления неавторизированного пользователя. """
        urls_and_redirects = (
            self.urls['post_edit'],
            self.urls['post_create'],
            self.urls['follow_index'],
            self.urls['follow_author']
        )

        # Адрес на который должен вести редирект
        login = self.urls['login']

        for url in urls_and_redirects:
            response = self.guest_client.get(url, follow=True)

            # Полный адрес на который должен вести редирект
            redirect = f'{login}?next={url}'

            with self.subTest(url=url):
                self.assertRedirects(
                    response,
                    redirect
                )

    def test_check_status_code_for_authorized_user(self):
        """
        Проверка доступности приватных адресов,
        авторизированным пользователям.
        """
        for url in self.urls_private:
            with self.subTest(url=url):
                self.assertEqual(
                    self.authorized_client.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_check_status_code_for_author_post(self):
        """ Проверка доступности редактирования поста, для автора поста. """
        response = self.authorized_client.get(
            self.urls['post_edit'],
        )

        # Пользователь автор
        self.assertIs(TestingUrlsInPosts.user, TestingUrlsInPosts.post.author)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_check_redirect_follow_and_unfollow_author(self):
        """ Проверка редиректа. Авторизированные пользователи. """

        for url, redirect in self.urls_redirect.items():
            response = self.authorized_client.get(url, follow=True)

            with self.subTest(url=url):
                self.assertRedirects(
                    response,
                    redirect
                )
