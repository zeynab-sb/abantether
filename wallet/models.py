from django.db import models, transaction
from django.contrib.auth.models import User

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} - Balance: {self.balance}"

    def has_balance(self, amount):
        return self.balance >= amount

    @transaction.atomic
    def deduct(self, amount):
        if self.balance < amount:
            return False
        self.balance -= amount
        self.save()

    class Meta:
        db_table = 'wallet'        