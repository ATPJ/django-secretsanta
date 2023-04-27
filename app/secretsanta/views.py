from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework import authentication, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import (server_error, bad_request,
                                       ValidationError)

from core.models import Event, Gift

from secretsanta.serializers import EventSerializer, GiftSerializer
from secretsanta.permissions import (EventPermission, IsEventModerator,
                                     IsEventAttender)

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
            return server_error(request)
        event.is_start = True
        event.save()
        return Response({"Message": "ok"}, 200)

    @action(detail=True, methods=['GET'], url_path="gift",
            url_name="gift", serializer_class=GiftSerializer,
            permission_classes=[permissions.IsAuthenticated, IsEventAttender])
    def get_gift(self, request, pk=None):
        event = self.get_object()
        if not event.is_start:
            return bad_request(request, ValidationError())
        gift = Gift.objects.get(event=event, giver=request.user)
        serialized_data = self.get_serializer(gift).data

        return Response(serialized_data)

    @action(detail=True, methods=['POST'], url_path='add-attender',
            url_name='add-attender',
            permission_classes=[permissions.IsAuthenticated, IsEventModerator])
    def add_attender(self, request, pk=None):
        event = self.get_object()
        if event.is_start:
            return bad_request(request, ValidationError)

        username = request.data.get('username')
        new_attender = get_object_or_404(get_user_model(), username=username)
        event.attenders.add(new_attender)
        event.save()
        serialize = self.get_serializer(event)
        return Response(serialize.data)
