from django.test import TestCase
from django.contrib.auth import get_user_model


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
