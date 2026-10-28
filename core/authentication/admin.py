from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    model = CustomUser

    list_display = [
        "username",
        "email",
        "is_staff",
        "is_active",
        "is_core_admin",
    ]

    fieldsets = UserAdmin.fieldsets + (
        ("EXALORE permissions", {"fields": ("is_core_admin",)}),
    )
