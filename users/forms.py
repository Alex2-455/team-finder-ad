import re
from django import forms
from django.contrib.auth import authenticate
from .models import User
from team_finder.constants import (
    USER_PHONE_REGEX,
    USER_PHONE_ALT_REGEX,
    USER_PHONE_PREFIX,
    GITHUB_URL_PATTERN,
)


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if len(name) > 30:
            raise forms.ValidationError("Имя не может быть длиннее 30 символов")
        return name

    def clean_surname(self):
        surname = self.cleaned_data.get("surname")
        if len(surname) > 30:
            raise forms.ValidationError("Фамилия не может быть длиннее 30 символов")
        return surname

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


class EditProfileForm(forms.ModelForm):
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

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if len(name) > 30:
            raise forms.ValidationError("Имя не может быть длиннее 30 символов")
        return name

    def clean_surname(self):
        surname = self.cleaned_data.get("surname")
        if len(surname) > 30:
            raise forms.ValidationError("Фамилия не может быть длиннее 30 символов")
        return surname

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

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url and GITHUB_URL_PATTERN not in url:
            raise forms.ValidationError("Ссылка должна вести на github.com")
        return url


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
        p1 = cleaned.get("new_password1")
        p2 = cleaned.get("new_password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Новые пароли не совпадают")
        return cleaned

    def save(self):
        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save()