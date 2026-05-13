import re

from django import forms
from django.contrib.auth import authenticate

from team_finder.constants import (
    GITHUB_URL_PATTERN,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_ALT_REGEX,
    USER_PHONE_PREFIX,
    USER_PHONE_REGEX,
    USER_SURNAME_MAX_LENGTH,
)
from users.models import User


class GithubURLValidatorMixin:
    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url and GITHUB_URL_PATTERN not in url:
            raise forms.ValidationError("Ссылка должна вести на github.com")
        return url


class NameSurnameValidatorMixin:
    def _validate_name_length(self, value, max_length, field_name):
        if len(value) > max_length:
            raise forms.ValidationError(
                f"{field_name} не может быть длиннее {max_length} символов"
            )
        return value

    def clean_name(self):
        name = self.cleaned_data.get("name")
        return self._validate_name_length(name, USER_NAME_MAX_LENGTH, "Имя")

    def clean_surname(self):
        surname = self.cleaned_data.get("surname")
        return self._validate_name_length(surname, USER_SURNAME_MAX_LENGTH, "Фамилия")


class RegisterForm(NameSurnameValidatorMixin, forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            self.user = authenticate(email=email, password=password)
            if self.user is None:
                raise forms.ValidationError("Неверный email или пароль")
        return cleaned_data


class EditProfileForm(
    GithubURLValidatorMixin,
    NameSurnameValidatorMixin,
    forms.ModelForm,
):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            return phone
        phone = phone.strip()
        if re.match(USER_PHONE_ALT_REGEX, phone):
            phone = USER_PHONE_PREFIX + phone[1:]
        if not re.match(USER_PHONE_REGEX, phone):
            raise forms.ValidationError(
                "Телефон должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX"
            )
        qs = User.objects.filter(phone=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Пользователь с таким номером телефона уже существует")
        return phone


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label="Текущий пароль")
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="Новый пароль")
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Подтвердите новый пароль")

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old = self.cleaned_data.get("old_password")
        if not self.user.check_password(old):
            raise forms.ValidationError("Неверный текущий пароль")
        return old

    def clean(self):
        cleaned = super().clean()
        new_password1 = cleaned.get("new_password1")
        new_password2 = cleaned.get("new_password2")
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("Новые пароли не совпадают")
        return cleaned

    def save(self):
        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save()
