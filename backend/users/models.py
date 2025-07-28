from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator, RegexValidator
from django.db import models

from api.constants import (EMAIL_MAX_LENGHT, FIRST_NAME_MAX_LENGHT,
                           LAST_NAME_MAX_LENGHT, LOGIN_ERROR_MESSAGE,
                           PASSWORD_MAX_LENGHT, USERNAME_MAX_LENGHT)
from api.validators import validate_username


class User(AbstractUser):
    """Модель пользователя, используемая в проекте."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    username = models.CharField(
        verbose_name='Логин',
        max_length=USERNAME_MAX_LENGHT,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=LOGIN_ERROR_MESSAGE
            ),
            validate_username,
        ]
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=EMAIL_MAX_LENGHT,
        unique=True,
        validators=[EmailValidator, ],
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=FIRST_NAME_MAX_LENGHT,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LAST_NAME_MAX_LENGHT,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=PASSWORD_MAX_LENGHT,
    )
    avatar = models.ImageField(
        verbose_name='Аватар пользователя',
        upload_to='media/avatars/',
        blank=True,
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель для подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='prevent_self_subscription',
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}.'
