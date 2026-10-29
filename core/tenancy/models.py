from django.db import models
from core.security import decrypt_secret, encrypt_secret


class Tenant(models.Model):
    db_alias = models.CharField(max_length=100, unique=True, db_index=True)
    company_name = models.CharField(max_length=200)
    db_name = models.CharField(max_length=100, unique=True)
    db_user = models.CharField(max_length=100, default="postgres")
    db_host = models.CharField(max_length=255, default="localhost")
    db_port = models.IntegerField(default=5432)
    db_password = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company_name} ({self.db_alias})"

    def get_decrypted_password(self) -> str:
        """
        Returns the plaintext database password. Decrypts if encrypted.
        """
        return decrypt_secret(self.db_password)

    def set_encrypted_password(self, raw_password: str) -> None:
        """
        Encrypts and assigns database password.
        """
        self.db_password = encrypt_secret(raw_password)

    def save(self, *args, **kwargs):
        # Auto-encrypt if raw password does not appear encrypted and an encryption key is active
        if self.db_password and not self.db_password.startswith("gAAAAA"):
            encrypted = encrypt_secret(self.db_password)
            if encrypted != self.db_password:
                self.db_password = encrypted
        super().save(*args, **kwargs)
