from django.contrib.auth import get_user_model

from rest_framework import serializers

from core.models import Event, Gift


class EventSerializer(serializers.ModelSerializer):

    attenders = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=get_user_model().objects.all(),
    )

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description',
            'location', 'moderator', 'attenders',
            'date_created', 'date_updated', 'image'
        )
        read_only_fields = ('id', 'moderator', 'image')


class GiftSerializer(serializers.ModelSerializer):

    class Meta:
        model = Gift
        fields = "__all__"


class AddAttenderSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, allow_blank=False)


class EventImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Event
        fields = ['id', 'image']
        read_only_fiedls = ['id']
        extra_kwargs = {'image': {'required': True}}
