from rest_framework import viewsets
from rest_framework import authentication, permissions

from core.models import Event

from secretsanta.serializers import EventSerializer
# from secretsanta.permissions import IsEventAttender, IsEventModerator
from secretsanta.permissions import EventPermission


class EventViewSet(viewsets.ModelViewSet):

    serializer_class = EventSerializer
    queryset = Event.objects.all()
    authentication_classes = [authentication.TokenAuthentication, ]
    permission_classes = [permissions.IsAuthenticated, EventPermission]

    def get_queryset(self):
        """ Return events which the authenticated user is in attenders list"""
        return self.queryset.filter(attenders=self.request.user)\
                            .order_by('-date_created')

    def perform_create(self, serializer: serializer_class):
        current_user = self.request.user
        serializer.validated_data['moderator'] = current_user
        serializer.validated_data['attenders'].append(current_user)
        serializer.save()
