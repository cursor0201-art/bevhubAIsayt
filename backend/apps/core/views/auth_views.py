from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from core.serializers.auth_serializers import UserRegistrationSerializer

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Record user journey telemetry event
        from core.domain.models import UserJourneyEvent
        UserJourneyEvent.objects.create(
            user=user,
            step='registration',
            status='success'
        )
        
        # Automatically generate JWT tokens for immediate login after signup
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": {
                "username": user.username,
                "email": user.email,
                "role": user.role
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


from rest_framework_simplejwt.views import TokenObtainPairView as SimpleJWTTokenObtainPairView
from core.serializers.auth_serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(SimpleJWTTokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "theme": user.theme,
            "language": user.language,
            "tenant_id": str(user.tenant.id) if user.tenant else None
        })

    def patch(self, request):
        user = request.user
        username = request.data.get('username')
        email = request.data.get('email')
        theme = request.data.get('theme')
        language = request.data.get('language')

        if username:
            user.username = username
        if email:
            user.email = email
        if theme:
            user.theme = theme
        if language:
            user.language = language

        user.save()
        return Response({
            "message": "Profile updated successfully",
            "username": user.username,
            "email": user.email,
            "theme": user.theme,
            "language": user.language
        })


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({"error": "old_password and new_password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({"error": "Invalid current password"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password updated successfully"})


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        password = request.data.get('password')

        if not password:
            return Response({"error": "Password confirmation is required to delete account"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({"error": "Invalid password confirmation"}, status=status.HTTP_400_BAD_REQUEST)

        # Soft delete user
        user.delete()
        return Response({"message": "Account successfully deleted"})

