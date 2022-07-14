from django.test import TestCase

from posts.models import Post, Group, User, Follow, Comment


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Создать таблицы. """
        super().setUpClass()

        # Создать пользователя.
        cls.user = User.objects.create_user(
            username='leo'
        )

        # Создать группу.
        cls.group = Group.objects.create(
            title='Котики',
            slug='category-cats/',
            description='Мир котиков уникальный',
        )

        # Создать пост.
        cls.post = Post.objects.create(
            text='Проверить правильно ли отображается имя объекта.',
            author=cls.user,
            group=cls.group
        )

        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.post.author,
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

    def test_correct_fields_verbose_name_in_posts(self):
        """ Проверка корректности verbose_name полей в постах. """
        post = PostModelTest.post

        fields_verboses = {
            'text': 'Описание',
            'post_edit': 'Изменен ли пост',
            'group': 'Группа',
            'author': 'Автор'
        }

        for field, value in fields_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    value
                )

    def test_correct_fields_help_text_in_posts(self):
        """ Проверка корректности help_text полей в постах. """
        post = PostModelTest.post

        fields_help_texts = {
            'text': 'Введите описание поста',
            'group': 'Выберите группу',
            'author': 'Выберите автора'
        }

        for field, value in fields_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    value
                )

    def test_check_relation_one_to_many(self):
        """ Проверка связи один ко многим. """
        post = PostModelTest.post

        comment = PostModelTest.comment

        follow = PostModelTest.follow

        expected_and_current_values = {
            post.group: PostModelTest.group,
            post.author: PostModelTest.user,
            comment.post: PostModelTest.post,
            comment.author: PostModelTest.user,
            follow.user: PostModelTest.user,
            follow.author: PostModelTest.user
        }

        for expected, current in expected_and_current_values.items():
            with self.subTest(current=current):
                self.assertEqual(expected, current)

    def test_check_fields_max_length_in_group(self):
        """ Проверка полей на превышение максимальной длинны в группах. """
        group = PostModelTest.group

        fields_max_length = {
            'title': 200,
            'slug': 40
        }

        for field, value in fields_max_length.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).max_length,
                    value
                )

    def test_check_field_default_in_posts(self):
        """ Проверка поля на результат по умолчанию в постах. """
        post = PostModelTest.post

        post_edit = post.post_edit

        self.assertEqual(post_edit, False)

    def test_check_field_default_in_groups(self):
        """ Проверка поля на результат по умолчанию в группах. """
        group_junior = Group.objects.create(
            title='Новички',
            description='Новичек всегда прав'
        )

        self.assertEqual(group_junior.slug, 'category-')

    def test_correct_object_name(self):
        """
        Проверка на корректность возвращаемого
        значения методом __str__.
        """
        group = PostModelTest.group

        post = PostModelTest.post

        comment = PostModelTest.comment

        follow = PostModelTest.follow

        expected_and_current_values = {
            group.title: PostModelTest.group,
            f'Описание: {post.text[:15]}...': PostModelTest.post,
            f'Описание: {comment.text[:15]}...': PostModelTest.comment,
            follow.user.username: PostModelTest.follow
        }

        for expected, current in expected_and_current_values.items():
            with self.subTest(current=current):
                self.assertEqual(expected, str(current))
