from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from recipes.models import Recipe


class CreateDestroyObjMixinRecipe:
    """
        Используется для action методов RecipeViewSet.
        Используется для свяви между pk - рецепта и пользователем.
    """

    def mixin_create(self, request, serializer, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = serializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def mixin_destroy(self, request, model, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if not model.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            return Response(
                {
                    "error": "Удаляемой информации не обнаружено!"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
