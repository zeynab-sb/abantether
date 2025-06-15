from rest_framework import serializers
from .models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['user', 'balance']
        read_only_fields = ['user', 'balance']

class WalletUpdateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
