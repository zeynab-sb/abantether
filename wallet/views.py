from django.db import transaction
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Wallet
from .serializers import WalletSerializer, WalletUpdateSerializer

class WalletDetailView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Wallet, user=self.request.user)

class WalletDepositView(generics.GenericAPIView):
    serializer_class = WalletUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet = get_object_or_404(Wallet, user=request.user)
        wallet.balance += serializer.validated_data['amount']
        wallet.save()
        return Response({'balance': wallet.balance})

class WalletWithdrawView(generics.GenericAPIView):
    serializer_class = WalletUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet = get_object_or_404(Wallet, user=request.user)
        amount = serializer.validated_data['amount']
        if wallet.balance < amount:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
        wallet.balance -= amount
        wallet.save()
        return Response({'balance': wallet.balance})
