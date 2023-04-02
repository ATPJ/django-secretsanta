from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Event


def sample_user(**params):
    return get_user_model().objects.create_user(**params)


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
            "location": "At Cafe"
        }

        event = Event.objects.create(**data)
        event.save()
        event.attenders.add(user1, user2)

        attenders = event.attenders.all()

        self.assertEqual(event.title, data.get("title"))
        self.assertEqual(event.description, data.get("description"))
        self.assertEqual(event.location, data.get("location"))
        self.assertIn(user1, attenders)
        self.assertIn(user2, attenders)
