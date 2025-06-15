from django.db import models
from django.contrib.auth.models import User
from coin.models import Coin

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    price_at_purchase = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.coin.name} - {self.amount}"

    class Meta:
        db_table = 'order'