from django.db import models

from .encryption import encrypt_value, decrypt_value


class Tenant(models.Model):
    db_alias = models.CharField(max_length=100, unique=True)
    company_name = models.CharField(max_length=200)
    db_name = models.CharField(max_length=100)
    db_host = models.CharField(max_length=255, default="localhost")
    db_port = models.IntegerField(default=5432)
    db_user = models.CharField(max_length=100)
    db_password_encrypted = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name

    def set_password(self, password):
        self.db_password_encrypted = encrypt_value(password)

    def get_password(self):
        return decrypt_value(self.db_password_encrypted)
