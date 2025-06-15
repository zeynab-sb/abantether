from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from .redis_client import redis_client
from wallet.models import Wallet
from coin.models import Coin
from django.shortcuts import get_object_or_404
from .constants import (
    ORDER_MIN_USD_VALUE,
    REDIS_LOCK_TIMEOUT,
    ORDER_STATUS_PENDING,
    ORDER_STATUS_COMPLETED,
)

def buy_from_exchange(coin_name, amount):
    pass

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data['amount']
        coin_name = serializer.validated_data['currency']
        user = request.user

        coin = get_object_or_404(Coin, name=coin_name)
        price = coin.price
        usd_value = amount * price

        wallet = get_object_or_404(Wallet, user=request.user)
        if not wallet.has_balance(usd_value):
            return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

        wallet.deduct(usd_value)

        order = serializer.save(user=user, coin=coin, price_at_purchase=price, status=ORDER_STATUS_PENDING)

        total_amount_to_buy = 0

        if usd_value < ORDER_MIN_USD_VALUE:
            lock_key = f"order:{coin.name}"
            with redis_client.lock(lock_key, timeout=REDIS_LOCK_TIMEOUT):
                pending_orders = Order.objects.filter(coin=coin, status=ORDER_STATUS_PENDING)
                total = sum(o.amount * price for o in pending_orders)
                if total + usd_value >= ORDER_MIN_USD_VALUE:
                    pending_orders.update(status=ORDER_STATUS_COMPLETED)
                    total_amount_to_buy = total + usd_value
        else:
            total_amount_to_buy = order.amount

        if total_amount_to_buy >= ORDER_MIN_USD_VALUE:
            order.status = ORDER_STATUS_COMPLETED
            order.save()
            buy_from_exchange(coin.name, total_amount_to_buy)
    
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
