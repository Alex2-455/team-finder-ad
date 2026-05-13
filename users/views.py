from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from team_finder.constants import USERS_PER_PAGE
from users.forms import ChangePasswordForm, EditProfileForm, LoginForm, RegisterForm
from users.models import User
from users.utils import paginate


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("projects:project_list")
    return render(request, "users/register.html", {"form": form})


def user_login(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        login(request, form.user)
        return redirect("projects:project_list")
    return render(request, "users/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("projects:project_list")


def user_detail(request, user_id):
    user_obj = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": user_obj})


@login_required
def edit_profile(request):
    form = EditProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )
    if form.is_valid():
        form.save()
        return redirect("users:user_detail", user_id=request.user.pk)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = ChangePasswordForm(request.user, request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("users:user_detail", user_id=request.user.pk)
    return render(request, "users/change_password.html", {"form": form})


def user_list(request):
    participants = User.objects.all().order_by("id")
    page_obj = paginate(request, participants, USERS_PER_PAGE)
    return render(request, "users/participants.html", {"participants": page_obj})
