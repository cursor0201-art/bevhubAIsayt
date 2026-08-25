from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ai.models import UserMemory


class AIPreferencesView(APIView):
    """
    Manages personal styling and copywriting options stored in the UserMemory model,
    allowing customization of the AI generation's persona, language, and styling.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        memory, _ = UserMemory.objects.get_or_create(
            user=user,
            defaults={
                'writing_style': 'Professional',
                'favorite_colors': ['#8b5cf6', '#ec4899'],
                'preferred_language': 'English'
            }
        )

        return Response({
            "writing_style": memory.writing_style,
            "favorite_colors": memory.favorite_colors,
            "preferred_language": memory.preferred_language
        })

    def post(self, request):
        user = request.user
        memory, _ = UserMemory.objects.get_or_create(user=user)

        # Parse request body inputs
        writing_style = request.data.get("writing_style")
        favorite_colors = request.data.get("favorite_colors")
        preferred_language = request.data.get("preferred_language")

        if writing_style:
            memory.writing_style = writing_style
        if isinstance(favorite_colors, list):
            memory.favorite_colors = favorite_colors
        if preferred_language:
            memory.preferred_language = preferred_language

        memory.save()

        return Response({
            "message": "AI generation preferences updated successfully!",
            "writing_style": memory.writing_style,
            "favorite_colors": memory.favorite_colors,
            "preferred_language": memory.preferred_language
        })
