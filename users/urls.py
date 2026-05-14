from django.urls import path
from users import views # по isort 

app_name = "users"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("change-password/", views.change_password, name="change_password"),
    path("list/", views.user_list, name="user_list"),
    path("<int:user_id>/", views.user_detail, name="user_detail"),
]
