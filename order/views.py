from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from .redis_client import redis_client
from wallet.models import Wallet
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .constants import (
    ORDER_MIN_USD_VALUE,
    REDIS_LOCK_TIMEOUT,
    ORDER_STATUS_PENDING,
    ORDER_STATUS_COMPLETED,
)

COIN_PRICES = {
    "ABAN": Decimal("4.0"),
    "BTC": Decimal("65000.0"),
    "ETH": Decimal("3500.0"),
    "USDT": Decimal("1.0"),
    "DOGE": Decimal("0.15"),
}

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
        currency = serializer.validated_data['currency']
        price = COIN_PRICES.get(currency)
        if price is None:
            return Response({"error": "Unknown currency"}, status=status.HTTP_400_BAD_REQUEST)

        usd_value = amount * price
        wallet = get_object_or_404(Wallet, user=request.user)
        if not wallet.has_balance(usd_value):
            return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

        wallet.deduct(usd_value)
        order = serializer.save(user=request.user, price_at_purchase=price, status=ORDER_STATUS_PENDING)
        total_amount_to_buy = 0

        if usd_value < ORDER_MIN_USD_VALUE:
            lock_key = f"order:{currency}"
            with redis_client.lock(lock_key, timeout=REDIS_LOCK_TIMEOUT):
                pending_orders = Order.objects.filter(currency=currency, status=ORDER_STATUS_PENDING)
                total = sum(o.amount * price for o in pending_orders)
                if total >= ORDER_MIN_USD_VALUE:
                    pending_orders.update(status=ORDER_STATUS_COMPLETED)
                    total_amount_to_buy = sum(o.amount for o in pending_orders)
        else:
            order.status = ORDER_STATUS_COMPLETED
            order.save()
            total_amount_to_buy = order.amount

        if total_amount_to_buy > ORDER_MIN_USD_VALUE:
            order.status = ORDER_STATUS_COMPLETED
            order.save()
            buy_from_exchange(currency, total_amount_to_buy)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
