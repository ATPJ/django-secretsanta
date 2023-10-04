from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("account:create-user")
ACCESS_TOKEN_URL = reverse("account:access-token")
REFRESH_TOKEN_URL = reverse("account:refresh-token")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def make_detail_username_url(username: str):
    return reverse("account:detail", args=(username, ))


class PublicTest(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_successful_user(self):
        data = {
            "username": "atpj",
            "password": "atpj1234",
            "name": "Amirali"
        }

        res = self.client.post(CREATE_USER_URL, data=data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(data.get('password')))
        self.assertTrue(user.username, data.get("username"))

    def test_create_without_username_credentials(self):
        data = {
            "username": "",
            "password": "aptj21412"
        }

        res = self.client.post(CREATE_USER_URL, data=data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_if_user_already_exists(self):
        data = {
            "username": "atpj",
            "password": "atpj1234",
            "name": "Amirali"
        }
        create_user(**data)
        res = self.client.post(CREATE_USER_URL, data=data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_too_short_password_for_user(self):
        data = {
            "username": "atpj",
            "password": "at",
            "name": "Amirali"
        }

        res = self.client.post(CREATE_USER_URL, data=data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_access_token_for_user(self):
        data = {
            "username": "atpj",
            "password": "atpjpass124124",
        }
        create_user(**data)
        res = self.client.post(ACCESS_TOKEN_URL, data=data)

        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_access_token_with_invalid_credentials(self):
        data = {
            "username": "atpj",
            "password": "atpjpass124124",
        }
        create_user(**data)
        wrong_data = {
            "username": "atpj",
            "password": "wrongpass"
        }
        res = self.client.post(ACCESS_TOKEN_URL, data=wrong_data)
        self.assertNotIn('access', res.data)
        self.assertNotIn('refresh', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_access_token_with_not_existed_user(self):
        data = {
            "username": "atpj",
            "password": "atpjpass124124",
        }

        res = self.client.post(ACCESS_TOKEN_URL, data=data)
        self.assertNotIn("access", res.data)
        self.assertNotIn("refresh", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_with_valid_refresh_token(self):
        data = {
            "username": "atpj",
            "password": "atpjpass124124",
        }
        create_user(**data)

        refresh = self.client.post(ACCESS_TOKEN_URL, data=data
                                   ).json().get('refresh')
        payload = {
            'refresh': refresh
        }

        res = self.client.post(REFRESH_TOKEN_URL, data=payload)
        self.assertIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_refresh_with_invalid_refresh_token(self):
        data = {
            "username": "atpj",
            "password": "atpjpass124124",
        }
        create_user(**data)
        self.client.post(ACCESS_TOKEN_URL, data=data)
        payload = {
            'refresh': "AAAAAAAAAA.AAAAAAAAAA.AAAAA"
        }

        res = self.client.post(REFRESH_TOKEN_URL, data=payload)
        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_without_refresh_token(self):
        data = {
            "username": "atpj",
            "password": "atpjpass124124",
        }
        create_user(**data)
        self.client.post(ACCESS_TOKEN_URL, data=data)

        res = self.client.post(REFRESH_TOKEN_URL, data={})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_info_without_authentication(self):
        data = {
            "username": "atpj",
            "password": "atpjpass124124",
        }
        create_user(**data)
        url = make_detail_username_url(data.get('username'))
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTest(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user1 = create_user(username="ATPJ", password="atpj1234",
                                 name="Amirali")
        self.user2 = create_user(username="Foureyed", password="foureyed1234")

        self.client.force_authenticate(user=self.user1)

    def test_retreive_successful(self):
        url = make_detail_username_url("ATPJ")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            "username": self.user1.username,
            "name": self.user1.name
        })

    def test_post_not_allowed(self):
        url = make_detail_username_url("ATPJ")
        res = self.client.post(url, data={})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_retreive_profile(self):
        data = {
            "password": "newatpjpass",
            "name": "New Amirali"
        }
        url = make_detail_username_url("ATPJ")
        res = self.client.patch(url, data=data)
        self.user1.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user1.name, data.get('name'))
        self.assertTrue(self.user1.check_password(data.get('password')))

    def test_update_someone_else_info(self):
        data = {
            "password": "newatpjpass",
            "name": "New Amirali"
        }
        url = make_detail_username_url("Foureyed")
        res = self.client.patch(url, data=data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
