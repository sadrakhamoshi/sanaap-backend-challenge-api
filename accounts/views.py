from rest_framework import generics
from accounts.models import User
from accounts.serializers import UserCreateSerializer
from accounts.permissions import IsAdminRole


class UserRegisterView(generics.CreateAPIView):
    """Admin-only endpoint to create new users."""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [IsAdminRole]
