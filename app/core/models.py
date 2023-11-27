import uuid
import os

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin


def event_image_file_path(instance, filename):
    "Generate file path for event image."
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'event', filename)


class UserManager(BaseUserManager):

    def create_user(self, username, password=None, **extra_fields):
        """ Create new User """
        if not username:
            raise ValueError("User must have a username")

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password, **extra_fields):
        """ Create Superuser """
        user = self.create_user(username=username, password=password,
                                **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"

    def __str__(self) -> str:
        return f"<User: {self.username}>"


class Event(models.Model):
    title = models.CharField(max_length=128, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=128, blank=False, null=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_start = models.BooleanField(default=False)
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.PROTECT,
                                  related_name="moderated_events")
    attenders = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       related_name="events")
    image = models.ImageField(null=True, upload_to=event_image_file_path)

    def __str__(self) -> str:
        return f"<Event: '{self.title}' at '{self.location}'>"


class Gift(models.Model):
    giver = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.PROTECT,
                              related_name="gifts_to_buy")
    reciver = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.PROTECT,
                                related_name="gifts_to_recive")
    event = models.ForeignKey("Event",
                              on_delete=models.CASCADE,
                              related_name="gifts")
