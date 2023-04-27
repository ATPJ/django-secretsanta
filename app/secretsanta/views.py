from rest_framework import viewsets
from rest_framework import authentication, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import server_error, bad_request, \
                                      ValidationError

from core.models import Event

from secretsanta.serializers import EventSerializer
from secretsanta.permissions import EventPermission, IsEventModerator

from secretsanta.utils import match_and_create_gift_for_attenders


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

    @action(detail=True, methods=['POST'], url_path="start",
            url_name="start",
            permission_classes=[permissions.IsAuthenticated, IsEventModerator])
    def event_start(self, request, pk=None):
        event = self.get_object()
        if event.is_start:
            return bad_request(request, ValidationError)
        state = match_and_create_gift_for_attenders(event)
        if not state:
            raise server_error(request)
        event.is_start = True
        event.save()
        return Response({"Message": "ok"}, 200)
