from django.db import models


class Tenant(models.Model):
    db_alias = models.CharField(max_length=100, unique=True)
    company_name = models.CharField(max_length=200)
    db_name = models.CharField(max_length=100, unique=True)
    db_user = models.CharField(max_length=100, default="postgres")
    db_host = models.CharField(max_length=255, default="localhost")
    db_port = models.IntegerField(default=5432)
    db_password = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name
