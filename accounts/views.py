from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import UserCreateSerializer, UserRoleUpdateSerializer
from .permissions import IsAdminRole

User = get_user_model()

class UserRegisterView(generics.CreateAPIView):
    """Admin-only endpoint to create new users."""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [IsAdminRole]
