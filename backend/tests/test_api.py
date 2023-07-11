from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from recipes.models import (
    Tag,
    Ingredient,
)
from users.models import (
    FollowingAuthor
)


User = get_user_model()


class ApiTest(APITestCase):

    def setUp(self):
        User.objects.create(
            email="qwerty@yandex.ru",
            username="ya",
            first_name="ya",
            last_name="ya",
            password="Qwerty123qwe123"
        )
        Tag.objects.create(
            name="Завтрак",
            color="#E26C2D",
            slug="breakfast"
        )
        Ingredient.objects.create(
            name="Капуста",
            measurement_unit="кг"
        )

    def test_get_tags(self):

        response = self.client.get(
            '/api/tags/',
            format='json'
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.json()), 1)

    def test_get_tag(self):

        response = self.client.get(
            '/api/tags/1/',
            format='json'
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json()['id'], 1)
        self.assertEquals(response.json()['name'], "Завтрак")
        self.assertEquals(response.json()['color'], "#E26C2D")
        self.assertEquals(response.json()['slug'], "breakfast")

    def test_get_ingredients(self):
        response = self.client.get(
            '/api/ingredients/',
            format='json'
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.json()), 1)

    def test_get_ingredient(self):
        response = self.client.get(
            '/api/ingredients/1/',
            format='json'
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json()['id'], 1)
        self.assertEquals(response.json()['name'], "Капуста")
        self.assertEquals(response.json()['measurement_unit'], "кг")

    def test_users(self):
        # create user
        data = {
            "email": "vpupok@yandex.ru",
            "username": "vasya",
            "first_name": "Вася",
            "last_name": "Пупкин",
            "password": "Qwerty123qwe123"
        }
        response_create_user = self.client.post(
            '/api/users/',
            data,
            format='json'
        )
        self.assertEquals(
            response_create_user.status_code, status.HTTP_201_CREATED
        )
        self.assertEquals(User.objects.count(), 2)
        res = response_create_user.json()
        self.assertEquals(res['id'], 2)
        self.assertEquals(res['email'], data['email'])
        self.assertEquals(res['username'], data['username'])
        self.assertEquals(res['first_name'], data['first_name'])
        self.assertEquals(res['last_name'], data['last_name'])

        # get users
        response_get_users = self.client.get(
            '/api/users/',
            format='json'
        )
        res = response_get_users.json()
        self.assertEquals(len(res['results']), 2)
        self.assertTrue(
            'email' in res['results'][0]
            and 'id' in res['results'][0]
            and 'username' in res['results'][0]
            and 'first_name' in res['results'][0]
            and 'last_name' in res['results'][0]
            and 'is_subscribed' in res['results'][0]
        )
        self.assertEquals(response_get_users.status_code, status.HTTP_200_OK)

        # get user
        response_get_user = self.client.get(
            '/api/users/2/',
            format='json'
        )
        res = response_get_user.json()
        self.assertTrue(
            'email' in res
            and 'id' in res
            and 'username' in res
            and 'first_name' in res
            and 'last_name' in res
            and 'is_subscribed' in res
        )
        self.assertEquals(response_get_user.status_code, status.HTTP_200_OK)

        # create token
        data = {
            "password": "Qwerty123qwe123",
            "email": "vpupok@yandex.ru"
        }
        response_create_token = self.client.post(
            '/api/auth/token/login/',
            data,
            format='json'
        )
        self.assertEquals(
            response_create_token.status_code,
            status.HTTP_200_OK
            # HTTP_201_CREATED
        )

        token = f'Token {response_create_token.json()["auth_token"]}'
        self.client.credentials(HTTP_AUTHORIZATION=token)

        # get user me
        response_get_me = self.client.get(
            '/api/users/me/',
            format='json'
        )
        res = response_get_me.json()
        self.assertTrue(
            'email' in res
            and 'id' in res
            and 'username' in res
            and 'first_name' in res
            and 'last_name' in res
            and 'is_subscribed' in res
        )
        self.assertEquals(response_get_user.status_code, status.HTTP_200_OK)

        # update password
        data = {
            "new_password": "Qwerty123qwe1234",
            "current_password": "Qwerty123qwe123"
        }
        response_update_password = self.client.post(
            '/api/users/set_password/',
            data,
            format='json'
        )
        self.assertEquals(
            response_update_password.status_code, status.HTTP_204_NO_CONTENT
        )

        # post subscribe
        response_subscribe_user = self.client.post(
            '/api/users/1/subscribe/',
            {},
            format='json'
        )
        self.assertEquals(
            response_subscribe_user.status_code, status.HTTP_201_CREATED
        )
        self.assertEquals(FollowingAuthor.objects.count(), 1)
        res = response_subscribe_user.json()
        self.assertTrue(
            'email' in res
            and 'id' in res
            and 'username' in res
            and 'first_name' in res
            and 'last_name' in res
            and 'is_subscribed' in res
            and 'recipes' in res
            and 'recipes_count' in res
        )

        # my subscribers
        response_my_subscribers = self.client.get(
            '/api/users/subscriptions/',
            format='json'
        )
        res = response_my_subscribers.json()
        self.assertTrue(
            'count' in res
            and 'next' in res
            and 'previous' in res
            and 'results' in res
        )
        self.assertEquals(len(res['results']), 1)
        self.assertTrue(
            'id' in res['results'][0]
            and 'email' in res['results'][0]
            and 'username' in res['results'][0]
            and 'first_name' in res['results'][0]
            and 'last_name' in res['results'][0]
            and 'is_subscribed' in res['results'][0]
            and 'recipes' in res['results'][0]
            and 'recipes_count' in res['results'][0]
        )

        # remove subscriber
        response_remove_sub = self.client.delete(
            '/api/users/1/subscribe/',
            format='json'
        )
        self.assertEquals(
            response_remove_sub.status_code, status.HTTP_204_NO_CONTENT
        )

        # remove token
        response_remove_token = self.client.post(
            '/api/auth/token/logout/',
            {},
            format='json'
        )
        self.assertEquals(
            response_remove_token.status_code, status.HTTP_204_NO_CONTENT
        )

    def test_valid_err_create_user(self):
        data = {
            "username": "vasya",
            "password": "Qwerty123qwe123"
        }
        response = self.client.post(
            '/api/users/',
            data,
            format='json'
        )
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
