from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(**params) -> get_user_model():
    return get_user_model().objects.create_user(**params)


def sample_event(**params) -> models.Event:
    default = {
        "title": "This is title",
        "description": "This is description",
        "location": "At Cafe"
    }
    default.update(**params)
    return models.Event.objects.create(**default)


class TestModels(TestCase):

    def test_create_user(self):
        info = {
            "username": "atpj",
            "password": "atpj3523236",
            "name": "Amirali"
        }
        user = get_user_model().objects.create_user(**info)
        self.assertEqual(user.username, info.get("username"))
        self.assertTrue(user.check_password(info.get("password")))
        self.assertEqual(user.name, info.get("name"))

    def test_create_with_blank_username(self):
        info = {
            "username": None,
            "password": "pafgjgdkds",
            "name": "Amirali"
        }
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(**info)

    def test_create_super_user(self):
        info = {
            "username": "atpj",
            "password": "pass1234",
            "name": "Amirali"
        }
        user = get_user_model().objects.create_superuser(**info)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_event(self):
        user1 = sample_user(username="atpj", password="atpj1234")
        user2 = sample_user(username="majid", password="majid1234")
        data = {
            "title": "This is title",
            "description": "This is description",
            "location": "At Cafe",
            "moderator": user1
        }

        event = models.Event.objects.create(**data)
        event.save()
        event.attenders.add(user1, user2)

        attenders = event.attenders.all()

        for key in data:
            self.assertEqual(getattr(event, key), data[key])

        self.assertFalse(event.is_start)
        self.assertEqual(event.moderator, user1)
        self.assertIn(user1, attenders)
        self.assertIn(user2, attenders)

    def test_create_gift(self):
        user1 = sample_user(username="atpj", password="atpj1234")
        user2 = sample_user(username="majid", password="majid1234")
        event = sample_event(moderator=user1)
        data = {
            "giver": user1,
            "reciver": user2,
            "event": event
        }

        models.Gift.objects.create(**data)
        gift = models.Gift.objects.get()

        self.assertEqual(gift.giver, user1)
        self.assertEqual(gift.reciver, user2)
        self.assertEqual(gift.event, event)

    @patch('core.models.uuid.uuid4')
    def test_event_image_file_name(self, mock_uuid):
        """Test generating image path name."""
        uuid = 'this-test'
        mock_uuid.return_value = uuid
        file_path = models.event_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
