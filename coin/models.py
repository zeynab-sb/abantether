from django.db import models

class Coin(models.Model):
    name = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=20, decimal_places=8)

    def __str__(self):
        return f"{self.name} (${self.price})"

    class Meta:
        db_table = 'coin'