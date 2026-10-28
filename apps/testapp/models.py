from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        app_label = "testapp"
        db_table = "products"

    def __str__(self):
        return self.name
