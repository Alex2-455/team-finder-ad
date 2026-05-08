from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import User
from .forms import RegisterForm, LoginForm, EditProfileForm, ChangePasswordForm
from team_finder.constants import USERS_PER_PAGE


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/projects/list/")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect("/projects/list/")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("/projects/list/")


def user_detail(request, user_id):
    user_obj = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": user_obj})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:user_detail", user_id=request.user.pk)
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:user_detail", user_id=request.user.pk)
    else:
        form = ChangePasswordForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


def user_list(request):
    participants = User.objects.all().order_by("id")
    paginator = Paginator(participants, USERS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "users/participants.html", {"participants": page_obj})