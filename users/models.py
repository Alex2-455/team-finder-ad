from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from .utils import generate_avatar
from team_finder.constants import (
    USER_NAME_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    USER_ABOUT_MAX_LENGTH,
    AVATAR_UPLOAD_DIR,
)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH, verbose_name="Имя")
    surname = models.CharField(max_length=USER_SURNAME_MAX_LENGTH, verbose_name="Фамилия")
    avatar = models.ImageField(upload_to=AVATAR_UPLOAD_DIR, blank=True, verbose_name="Аватар")
    phone = models.CharField(max_length=USER_PHONE_MAX_LENGTH, verbose_name="Телефон")
    github_url = models.URLField(blank=True, verbose_name="GitHub")
    about = models.TextField(max_length=USER_ABOUT_MAX_LENGTH, blank=True, verbose_name="О себе")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            first_letter = self.name[0].upper() if self.name else "U"
            self.avatar = generate_avatar(first_letter)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.surname} ({self.email})"