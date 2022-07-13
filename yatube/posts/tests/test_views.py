from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.core.cache import cache

from posts.models import Post, Group, User, Follow


class TestingViewsInPosts(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Создать таблицы. """
        super().setUpClass()

        # Создать пользователя. Автор поста.
        cls.user = User.objects.create(
            username='leo'
        )

        # Создать пользователя. Не автор поста.
        cls.user_other = User.objects.create(
            username='other'
        )

        cls.group = Group.objects.create(
            title='Котики',
            slug='category-cats',
            description='Мир котиков уникальный',
        )

        cls.post = Post.objects.create(
            text='Описание поста',
            author=cls.user,
            group=cls.group
        )

        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.post.author,
        )

        cls.urls = {
            'post_detail': reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.pk}
            ),
            'post_edit': reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.pk}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': cls.post.author.username}
            ),
            'group_posts': reverse(
                'posts:group_posts',
                kwargs={'slug': cls.post.group.slug}
            ),
            'follow_author': reverse(
                'posts:follow_author',
                kwargs={'username': cls.follow.author}
            ),
            'follow_index': reverse('posts:follow_index'),
            'index': reverse('posts:index'),
            'post_create': reverse('posts:post_create')
        }

        cls.urls_pagination = (
            cls.urls['index'],
            cls.urls['group_posts'],
            cls.urls['profile'],
            cls.urls['follow_index'],
            cls.urls['follow_author']
        )

        cls.urls_and_templates_public = {
            cls.urls['index']: 'posts/index.html',
            cls.urls['group_posts']: 'posts/group_list.html',
            cls.urls['post_detail']: 'posts/post_detail.html',
            cls.urls['profile']: 'posts/profile.html'
        }

        cls.urls_and_templates_private = {
            cls.urls['post_create']: 'posts/create_post.html',
            cls.urls['follow_index']: 'posts/follow.html',
            cls.urls['post_edit']: 'posts/create_post.html',
            cls.urls['follow_author']: 'posts/follow.html'
        }

    def setUp(self):
        """ Создать авторизированного пользователя. """
        self.authorized_client_other = Client()

        # Авторизировать пользователя, не автора поста.
        self.authorized_client_other.force_login(
            TestingViewsInPosts.user_other
        )

        self.authorized_client = Client()

        # Авторизировать пользователя автора поста.
        self.authorized_client.force_login(TestingViewsInPosts.user)

    def test_pages_uses_correct_templates_for_public_urls(self):
        """ Проверка соответствие шаблонов для публичных адресов. """
        for url, template in self.urls_and_templates_public.items():
            response = self.authorized_client.get(url)

            with self.subTest(url=url):
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_templates_for_private_urls(self):
        """ Проверка соответствие шаблонов для приватных адресов. """
        for url, template in self.urls_and_templates_private.items():
            response = self.authorized_client.get(url)

            with self.subTest(url=url):
                self.assertTemplateUsed(response, template)

    def test_correct_form_when_creating_posts(self):
        """ Тестируем форму при создания поста. """
        response = self.authorized_client.get(self.urls['post_create'])

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]

                self.assertIsInstance(form_field, expected)

    def test_correct_form_when_editing_posts(self):
        """ Тестируем форму при редактирования поста. """
        response = self.authorized_client.get(self.urls['post_edit'])

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]

                self.assertIsInstance(form_field, expected)

    def test_correct_show_context_posts(self):
        """ Проверка корректности контекста post. """
        urls = (
            self.urls['post_detail'],
            self.urls['post_edit']
        )

        for url in urls:
            response = self.authorized_client.get(url)

            with self.subTest(url=url):
                self.assertEqual(
                    response.context.get('post'),
                    TestingViewsInPosts.post
                )

    def test_correct_show_context_is_edits(self):
        """ Проверка корректности контекста is_edit. """

        urls_and_values = {
            self.urls['post_edit']: True,
            self.urls['post_create']: False
        }

        for url, value in urls_and_values.items():
            response = self.authorized_client.get(url)

            with self.subTest(url=url):
                self.assertEqual(
                    response.context.get('is_edit'),
                    value
                )

    def test_correct_show_context_group(self):
        """ Проверка корректности контекста group, на странице групп. """
        response_group = self.authorized_client.get(self.urls['group_posts'])

        self.assertEqual(
            TestingViewsInPosts.group,
            response_group.context.get('group')
        )

    def test_correct_show_context_is_author_if_user_authorized(self):
        """ Проверка корректности контекста author,
            если пользователь автор поста. """

        # Пользователь автор поста
        response_author = self.authorized_client.get(self.urls['post_detail'])

        self.assertEqual(
            response_author.context.get('author'),
            TestingViewsInPosts.user
        )

    def test_correct_show_context_is_author_if_user_not_authorized(self):
        """ Проверка корректности контекста author,
            если пользователь не автор поста. """

        # Пользователь не автор поста
        response_other = self.authorized_client_other.get(
            self.urls['post_detail']
        )

        self.assertNotEqual(
            response_other.context.get('author'),
            TestingViewsInPosts.user
        )

    def test_correct_show_context_posts_count(self):
        """ Проверка корректности контекста количество постов. """
        urls = (
            self.urls['post_detail'],
            self.urls['profile']
        )

        for url in urls:
            response = self.authorized_client.get(url)

            with self.subTest(url=url):
                self.assertEqual(
                    response.context.get('post_count'),
                    Post.objects.count()
                )

    def test_correct_show_context_post_authors(self):
        """ Проверка корректности контекста в авторах поста. """
        urls = (
            self.urls['profile'],
        )

        for url in urls:
            response = self.authorized_client.get(url)

            with self.subTest(url=url):
                self.assertEqual(
                    response.context.get('author'),
                    TestingViewsInPosts.post.author
                )

    def test_correct_show_context_groups(self):
        """ Проверка корректности контекста в группах. """
        urls = (
            self.urls['group_posts'],
        )

        for url in urls:
            response = self.authorized_client.get(url)

            with self.subTest(url=url):
                self.assertEqual(
                    response.context.get('group'),
                    TestingViewsInPosts.post.group
                )

    def test_correct_show_context_authors(self):
        """ Проверка корректности контекста авторов. """
        urls = {
            self.urls['follow_index'],
            self.urls['follow_author']
        }

        for url in urls:
            response = self.authorized_client.get(url)

            with self.subTest(url=url):
                self.assertEqual(
                    response.context.get('authors')[0],
                    TestingViewsInPosts.follow.author
                )

    def test_check_display_posts_on_pages(self):
        """ Проверить наличие постов на страницах где они отображаются. """
        new_post = Post.objects.create(
            text='Описание поста',
            author=TestingViewsInPosts.user,
            group=TestingViewsInPosts.group
        )

        pages = {
            'page_index': self.authorized_client.get(self.urls['index']),
            'page_group_posts':
                self.authorized_client.get(self.urls['group_posts']),
            'page_profile': self.authorized_client.get(self.urls['profile'])
        }

        for page, response_page in pages.items():
            with self.subTest(page=page):
                self.assertIn(
                    new_post,
                    response_page.context.get('page_obj').object_list
                )

    def test_check_missing_new_group_on_pages_posts(self):
        """ Проверить отсуствие созданной группы в постах,
            если ее никто не выбрал. """
        new_group = Group.objects.create(
            title='Лидеры',
            slug='category-leader',
            description='Лидеры вперед',
        )

        response = self.authorized_client.get(self.urls['group_posts'])

        self.assertNotIn(
            new_group,
            response.context.get('page_obj').object_list
        )

    def test_correct_show_pagination(self):
        """ Проверка корректности работы пагинатор. """
        old_posts = Post.objects.all()
        old_posts.delete()

        AMOUNT_POSTS = 18

        FIRST_TEN_POSTS = 10

        SECOND_EIGHT_POSTS = 8

        # Создать количество постов
        for i in range(AMOUNT_POSTS):
            Post.objects.create(
                text='Описание поста',
                author=TestingViewsInPosts.user,
                group=TestingViewsInPosts.group
            )

        for url in self.urls_pagination:
            response_page_one = self.authorized_client.get(url)

            # Тестируем первую страницу
            with self.subTest(url=url):
                self.assertEqual(
                    len(response_page_one.context.get('page_obj').object_list),
                    FIRST_TEN_POSTS
                )

            response_page_two = self.authorized_client.get(url + '?page=2')

            # Тестируем вторую страницу
            with self.subTest(url=url):
                self.assertEqual(
                    len(response_page_two.context.get('page_obj').object_list),
                    SECOND_EIGHT_POSTS
                )

    def test_check_cache_template(self):
        """ Проверка кэша в шаблоне. """

        old_posts = Post.objects.all()
        old_posts.delete()

        post_cash = Post.objects.create(
            text='Тестирование кэша',
            author=TestingViewsInPosts.user,
            group=TestingViewsInPosts.group
        )

        response_one = self.authorized_client.get(reverse('posts:index'))

        post_cash.delete()

        response_two = self.authorized_client.get(reverse('posts:index'))

        self.assertEqual(
            response_one.content,
            response_two.content
        )

        response_three = self.authorized_client.get(self.urls['index'])

        cache.clear()

        self.assertNotEqual(
            response_one.context.get('page_obj').object_list,
            response_three.context.get('page_obj').object_list
        )
