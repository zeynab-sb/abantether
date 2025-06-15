from rest_framework import serializers
from .models import Order
from coin.models import Coin

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')    
    currency = serializers.CharField(write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'amount', 'price_at_purchase', 'status', 'coin', 'currency']
        read_only_fields = ['id', 'user', 'price_at_purchase', 'status', 'coin']

    def validate_currency(self, value):
        if not Coin.objects.filter(name=value).exists():
            raise serializers.ValidationError("Invalid currency symbol.")
        return value

    def create(self, validated_data):
        validated_data.pop('currency')
        return super().create(validated_data)
