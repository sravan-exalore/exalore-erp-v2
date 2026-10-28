from django.db import models


class GnUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    default_user_id = models.BigIntegerField(
        db_index=True, null=True, blank=True, help_text="ID from default.CustomUser"
    )
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "gn_user"
