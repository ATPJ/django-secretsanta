from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Event

from secretsanta import serializers


EVENT_URL = reverse("santa:event-list")


def make_detail_event_url(event_id):
    return reverse("santa:event-detail", args=(event_id, ))


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
