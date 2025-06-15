from django.urls import path
from .views import WalletDetailView, WalletDepositView, WalletWithdrawView

urlpatterns = [
    path('', WalletDetailView.as_view(), name='wallet-detail'),
    path('deposit/', WalletDepositView.as_view(), name='wallet-deposit'),
    path('withdraw/', WalletWithdrawView.as_view(), name='wallet-withdraw'),
]
