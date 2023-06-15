import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = [
        (ADMIN, 'admin'),
        (MODERATOR, 'moderator'),
        (USER, 'user')

    ]
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
    email = models.EmailField(unique=True)
    bio = models.TextField(
        'Биография',
        blank=True, null=True
    )

    role = models.CharField(
        max_length=10,
        choices=ROLES,
        default=USER,
    )
    confirmation_code = models.TextField(default=uuid.uuid4)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)