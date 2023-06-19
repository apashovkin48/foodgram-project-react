from django.db import models

# Create your models here.
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
    last_name = models.CharField(
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    def __str__(self):
        return self.email
