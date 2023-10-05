from django.contrib.auth import get_user_model

from rest_framework import generics, permissions

from rest_framework_simplejwt.authentication import JWTAuthentication

from account.serializers import UserSerializers
from account.permissions import IsOwnerOrReadOnly


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializers


class UpdateAndRetrieveView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializers
    queryset = get_user_model().objects.all()
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    lookup_field = "username"
