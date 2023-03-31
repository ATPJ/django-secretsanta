from django.contrib.auth import get_user_model

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from account.serializers import UserSerializers, AuthTokenSerializers
from account.permissions import IsOwnerOrReadOnly


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializers


class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializers
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UpdateAndRetrieveView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializers
    queryset = get_user_model().objects.all()
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    lookup_field = "username"
