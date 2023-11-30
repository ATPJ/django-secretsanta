import tempfile
import os

from PIL import Image

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Event, Gift

from secretsanta import serializers


EVENT_URL = reverse("santa:event-list")


def make_detail_event_url(event_id):
    return reverse("santa:event-detail", args=(event_id, ))


def make_start_event_url(event_id):
    return reverse("santa:event-start", args=(event_id, ))


def make_upload_image_url(event_id):
    return reverse("santa:event-upload-image", args=[event_id])


def sample_event_for_start(moderator, attender):
    event = sample_event(moderator)
    event.attenders.add(attender)
    event.save()
    return event


def sample_event(moderator, **params) -> Event:
    default = {
        "title": "This is Title",
        "description": "This is description",
        "location": "At Cafe"
    }
    default.update(**params)
    event = Event.objects.create(moderator=moderator, **default)
    event.attenders.add(moderator)
    return event


def make_get_event_gift_for_current_user_url(evnet_id: int):
    return reverse("santa:event-gift", args=(evnet_id, ))


def start_event_help_func(moderator: get_user_model(),
                          attender: get_user_model(),
                          client: APIClient) -> Event:
    """
        It is helper function for making an event and
        start that event then return the event for testing.
    """
    event = sample_event_for_start(moderator, attender)
    url = make_start_event_url(event.id)
    client.post(url)
    return event


def make_add_attender_url(event_id):
    return reverse("santa:event-add-attender", args=(event_id, ))


class PublicTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_unauthenticated_user(self):
        res = self.client.get(EVENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTests(TestCase):

    def setUp(self) -> None:
        self.user1 = get_user_model().objects.create_user(
            username="ATPJ",
            password="atpj1234",
            name="Amirali"
        )
        self.user2 = get_user_model().objects.create_user(
            username="Foureyed",
            password="foureyed1234",
            name="Mehrad"
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_list_events(self):
        sample_event(moderator=self.user1)
        sample_event(moderator=self.user1)

        res = self.client.get(EVENT_URL)
        events = Event.objects.all().order_by('-date_created')
        serializer = serializers.EventSerializer(events, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_list_events_limited_user(self):
        sample_event(moderator=self.user1)
        sample_event(moderator=self.user1)
        sample_event(moderator=self.user2)

        res = self.client.get(EVENT_URL)

        events = Event.objects.filter(attenders=self.user1).order_by(
                                                            '-date_created')
        serializer = serializers.EventSerializer(events, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_event_detail(self):
        event = sample_event(moderator=self.user1)
        event.attenders.add(self.user2)

        url = make_detail_event_url(event.id)
        res = self.client.get(url)
        serializer = serializers.EventSerializer(event)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_event(self):
        data = {
            "title": "This is title",
            "description": "This is description",
            "location": "At Cafe"
        }

        res = self.client.post(EVENT_URL, data=data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        event = Event.objects.get(pk=res.data['id'])

        for key in data.keys():
            self.assertEqual(data[key], getattr(event, key))
        self.assertEqual(event.moderator, self.user1)
        self.assertIn(self.user1, event.attenders.all())

    def test_create_event_with_addtional_attender(self):
        data = {
            "title": "This is title",
            "description": "This is description",
            "location": "At Cafe",
            "attenders": [self.user2.id]
        }

        res = self.client.post(EVENT_URL, data=data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        event = Event.objects.get(pk=res.data.get('id'))
        attenders = event.attenders.all()

        self.assertEqual(len(attenders), 2)
        self.assertIn(self.user2, attenders)

    def test_partial_update_event(self):
        event = sample_event(moderator=self.user1)
        data = {
            "description": "This is new description about event",
            "location": "Changing the Cafe location"
        }

        url = make_detail_event_url(event.id)
        self.client.patch(url, data=data)
        event.refresh_from_db()
        self.assertEqual(event.description, data.get("description"))
        self.assertEqual(event.location, data.get("location"))

    def test_full_update_event(self):
        event = sample_event(moderator=self.user1)
        data = {
            "title": "This is new title",
            "description": "This is new description about event",
            "location": "Changing the Cafe location",
            "attenders": [self.user1.id, self.user2.id]
        }
        url = make_detail_event_url(event.id)
        self.client.put(url, data=data)
        event.refresh_from_db()
        attenders = event.attenders.all()

        data.pop("attenders")
        for key in data.keys():
            self.assertEqual(data[key], getattr(event, key))

        self.assertIn(self.user1, attenders)
        self.assertIn(self.user2, attenders)

    def test_start_event(self):
        event = sample_event_for_start(self.user1, self.user2)
        url = make_start_event_url(event.id)
        res = self.client.post(url)
        gifts = Gift.objects.filter(event=event)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(gifts), len(event.attenders.all()))

    def test_start_event_403(self):
        event = sample_event_for_start(self.user1, self.user2)
        url = make_start_event_url(event.id)
        self.client.logout()
        self.client.force_authenticate(user=self.user2)
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_start_event_which_already_started(self):
        event = sample_event_for_start(self.user1, self.user2)
        url = make_start_event_url(event.id)
        self.client.post(url)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_gift_for_started_event(self):
        event = start_event_help_func(self.user1, self.user2, self.client)
        url = make_get_event_gift_for_current_user_url(event.id)
        resp = self.client.get(url)

        info = {
            "event": event,
            "giver": self.user1,
            "reciver": self.user2
        }
        gift = Gift.objects.get(**info)
        serializer = serializers.GiftSerializer(gift, many=False)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_get_gift_when_event_is_not_started(self):
        event = sample_event(self.user1)
        url = make_get_event_gift_for_current_user_url(event.id)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_new_user_as_attender_to_event(self):
        event = sample_event(self.user1)
        url = make_add_attender_url(event.id)
        payload = {
            "username": self.user2.username
        }

        resp = self.client.post(url, data=payload)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(self.user2.id, resp.json().get('attenders'))


class ImageUploadTests(TestCase):
    """Tests for the image upload API."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="ATPJ",
            password="atpj123456",
            name="Amirali"
        )

        self.client.force_authenticate(user=self.user)
        self.event = sample_event(self.user)

    def tearDown(self) -> None:
        self.event.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a event"""
        url = make_upload_image_url(self.event.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.event.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.event.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading invalid image."""
        url = make_upload_image_url(self.event.id)
        payload = {'image': "INVALID IMAGE"}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
