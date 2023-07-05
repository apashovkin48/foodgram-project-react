from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):

    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=(
                    'Required. 150 characters or fewer.'
                    'Letters, digits and @/./+/-/_ only.'
                ),
            ),
        ]
    )
    first_name = models.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=(
                    'Required. 150 characters or fewer.'
                    'Letters, digits and @/./+/-/_ only.'
                ),
            ),
        ]
    )
    last_name = models.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=(
                    'Required. 150 characters or fewer.'
                    'Letters, digits and @/./+/-/_ only.'
                ),
            ),
        ]
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class FollowingAuthor(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='На автора можно подпписаться только 1 раз!'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} -> {self.author.username}'
