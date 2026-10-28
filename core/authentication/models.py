from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    tenant = models.ForeignKey("tenancy.Tenant", on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "core_users"
