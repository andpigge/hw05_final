from django.db import models
from django.contrib.auth import get_user_model

from core.general_models.models import Date

User = get_user_model()


class Post(Date):
    text = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание поста'
    )
    post_edit = models.BooleanField(
        default=False,
        verbose_name='Изменен ли пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Выберите автора'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
        null=True,
        help_text='Загрузите картинку'
    )

    class Meta:
        ordering = ['-edited']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return f'Описание: {self.text[:15]}...'


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Заголовок'
    )
    slug = models.SlugField(
        max_length=40,
        unique=True,
        default='category-',
        verbose_name='Путь'
    )
    description = models.TextField(
        verbose_name='Описание'
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        return self.title


class Comment(Date):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
        help_text='Выберите пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
        help_text='Выберите автора'
    )
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Введите комментарий'
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return f'Описание: {self.text[:15]}...'


class Follow(Date):
    # Текущий пользователь
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    # Автор поста
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return self.user.username
