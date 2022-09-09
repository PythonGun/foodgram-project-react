from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def create_delete_object(request, pk, model, model_serializer):
    user = request.user
    recipe = get_object_or_404(Recipe, id=pk)

    if request.method == 'POST':
        model.objects.create(user=user, recipe=recipe)
        serializer = model_serializer(
            recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        recipe_object = get_object_or_404(
            model,
            user=user,
            recipe=recipe
        )
        recipe_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
