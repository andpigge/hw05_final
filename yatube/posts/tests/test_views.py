from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.core.cache import cache

from posts.models import Post, Group, User, Follow


class TestingViews(TestCase):
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

    def setUp(self):
        """ Создать авторизированного пользователя. """
        self.authorized_client_other = Client()

        # Авторизировать пользователя, не автора поста.
        self.authorized_client_other.force_login(
            TestingViews.user_other
        )

        self.authorized_client = Client()

        # Авторизировать пользователя автора поста.
        self.authorized_client.force_login(TestingViews.user)

    def test_check_display_posts_on_pages(self):
        """ Проверить наличие постов на страницах где они отображаются. """
        new_post = Post.objects.create(
            text='Описание поста',
            author=TestingViews.user,
            group=TestingViews.group
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
        """
        Проверить отсуствие созданной группы в постах,
        если ее никто не выбрал.
        """
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

    def test_check_follow(self):
        """ 
        Новая запись пользователя появляется в ленте тех, 
        кто на него подписан и не появляется в ленте тех, кто не подписан.
        """

        old_follow = Follow.objects.all()
        old_follow.delete()

        new_user = User.objects.create(
            username='andpigge1',
        )

        # Создать пользователя. Автор поста.
        new_post_follow = Post.objects.create(
            text='Тестирование появления в ленте автора. Первый пост.',
            author=new_user,
            group=TestingViews.group
        )

        new_post_not_follow = Post.objects.create(
            text='Тестирование появления в ленте автора. Второй пост.',
            author=TestingViews.user,
            group=TestingViews.group
        )

        follow = Follow.objects.create(
            user=TestingViews.user,
            author=new_post_follow.author,
        )

        response = self.authorized_client.get(TestingViews.urls['follow_index'])

        # Автор, не может подписаться сам на себя
        if not follow.user == follow.author:
            self.assertIn(
                new_post_follow,
                response.context.get('page_obj').object_list
            )

        self.assertNotIn(
            new_post_not_follow,
            response.context.get('page_obj').object_list
        )


class TestingViewsCheckTemplate(TestingViews):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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


class TestingViewsCheckContext(TestingViews):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.urls_for_check_post_context = (
            cls.urls['post_detail'],
            cls.urls['post_edit']
        )

        cls.urls_and_values_for_check_is_edit_context = {
            cls.urls['post_edit']: True,
            cls.urls['post_create']: False
        }

        cls.urls_for_check_post_count_context = (
            cls.urls['post_detail'],
            cls.urls['profile']
        )

        cls.urls_for_check_author_context = (
            cls.urls['profile'],
        )

        cls.urls_for_check_group_context = (
            cls.urls['group_posts'],
        )

        cls.urls_for_check_authors_context = (
            cls.urls['follow_index'],
            cls.urls['follow_author']
        )

    def test_correct_show_context_posts(self):
        """ Проверка корректности контекста post. """

        for url in self.urls_for_check_post_context:
            response = self.authorized_client.get(url)

            with self.subTest(url=url):
                self.assertEqual(
                    response.context.get('post'),
                    TestingViews.post
                )

    def test_correct_show_context_is_edits(self):
        """ Проверка корректности контекста is_edit. """

        for url, value in self.urls_and_values_for_check_is_edit_context.items():
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
            TestingViews.group,
            response_group.context.get('group')
        )

    def test_correct_show_context_is_author_if_user_authorized(self):
        """ 
        Проверка корректности контекста author,
        если пользователь автор поста.
        """

        # Пользователь автор поста
        response_author = self.authorized_client.get(self.urls['post_detail'])

        self.assertEqual(
            response_author.context.get('author'),
            TestingViews.user
        )

    def test_correct_show_context_is_author_if_user_not_authorized(self):
        """
        Проверка корректности контекста author,
        если пользователь не автор поста.
        """

        # Пользователь не автор поста
        response_other = self.authorized_client_other.get(
            self.urls['post_detail']
        )

        self.assertNotEqual(
            response_other.context.get('author'),
            TestingViews.user
        )

    def test_correct_show_context_posts_count(self):
        """ Проверка корректности контекста количество постов. """

        for url in self.urls_for_check_post_count_context:
            response = self.authorized_client.get(url)

            with self.subTest(url=url):
                self.assertEqual(
                    response.context.get('post_count'),
                    Post.objects.count()
                )

    def test_correct_show_context_post_authors(self):
        """ Проверка корректности контекста в авторах поста. """

        for url in self.urls_for_check_author_context:
            response = self.authorized_client.get(url)

            with self.subTest(url=url):
                self.assertEqual(
                    response.context.get('author'),
                    TestingViews.post.author
                )

    def test_correct_show_context_groups(self):
        """ Проверка корректности контекста в группах. """

        for url in self.urls_for_check_group_context:
            response = self.authorized_client.get(url)

            with self.subTest(url=url):
                self.assertEqual(
                    response.context.get('group'),
                    TestingViews.post.group
                )

    def test_correct_show_context_authors(self):
        """ Проверка корректности контекста авторов. """

        for url in self.urls_for_check_authors_context:
            response = self.authorized_client.get(url)

            with self.subTest(url=url):
                self.assertEqual(
                    response.context.get('authors')[0],
                    TestingViews.follow.author
                )


class TestingViewsCheckPagination(TestingViews):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.urls_pagination = (
            cls.urls['index'],
            cls.urls['group_posts'],
            cls.urls['profile'],
            cls.urls['follow_index'],
            cls.urls['follow_author']
        )

        cls.GENERAL_AMOUNT_POSTS = 18

        cls.AMOUNT_POSTS_ON_FIRST_PAGE = 10

        cls.AMOUNT_POSTS_ON_SECOND_PAGE = 8

    def test_correct_show_pagination(self):
        """ Проверка корректности работы пагинатор. """
        old_posts = Post.objects.all()
        old_posts.delete()

        # Создать количество постов
        for i in range(self.GENERAL_AMOUNT_POSTS):
            Post.objects.create(
                text='Описание поста',
                author=TestingViews.user,
                group=TestingViews.group
            )

        for url in self.urls_pagination:
            response_page_one = self.authorized_client.get(url)

            # Тестируем первую страницу
            with self.subTest(url=url):
                self.assertEqual(
                    len(response_page_one.context.get('page_obj').object_list),
                    self.AMOUNT_POSTS_ON_FIRST_PAGE
                )

            response_page_two = self.authorized_client.get(url + '?page=2')

            # Тестируем вторую страницу
            with self.subTest(url=url):
                self.assertEqual(
                    len(response_page_two.context.get('page_obj').object_list),
                    self.AMOUNT_POSTS_ON_SECOND_PAGE
                )


class TestingViewsCheckСache(TestingViews):
    def test_check_cache_template(self):
        """ Проверка кэша в шаблоне. """

        old_posts = Post.objects.all()
        old_posts.delete()

        post_cash = Post.objects.create(
            text='Тестирование кэша',
            author=TestingViews.user,
            group=TestingViews.group
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


class TestingViewsCheckForm(TestingViews):
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
