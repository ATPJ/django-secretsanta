from rest_framework.permissions import BasePermission


class IsEventModerator(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user == obj.moderator:
            return True

        return False


class IsEventAttender(BasePermission):

    def has_object_permission(self, request, view, obj):
        attenders = obj.attenders.all()
        return True if request.user in attenders else False


class EventPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if view.action in ['list', 'retrieve']:
            attenders = obj.attenders.all()
            return True if request.user in attenders else False

        if view.action in ['create', 'update', 'partial_update', 'destroy',
                           'upload_image']:
            return request.user == obj.moderator

        return False
