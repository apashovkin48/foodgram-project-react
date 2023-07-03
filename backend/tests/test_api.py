from rest_framework import status
from rest_framework.test import APITestCase
from recipes.models import (
    Tag,
    Ingredient,
)


class ApiTest(APITestCase):

    def setUp(self):
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
