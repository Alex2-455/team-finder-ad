from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User

admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "surname", "is_active", "is_staff")
    search_fields = ("email", "name", "surname")
    list_filter = ("is_active", "is_staff")
    ordering = ("email",)