from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from wallet.models import Wallet
from rest_framework.authtoken.models import Token

class WalletAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.wallet = Wallet.objects.create(user=self.user, balance=100)
        self.auth_header = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_get_wallet_success(self):
        url = reverse('wallet-detail')
        response = self.client.get(url, **self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['balance'], '100.00')

    def test_get_wallet_unauthenticated(self):
        url = reverse('wallet-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_deposit_success(self):
        url = reverse('wallet-deposit')
        response = self.client.post(url, {'amount': 50}, format='json', **self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.wallet.refresh_from_db()
        self.assertEqual(float(self.wallet.balance), 150.0)

    def test_deposit_unauthenticated(self):
        url = reverse('wallet-deposit')
        response = self.client.post(url, {'amount': 50}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_deposit_missing_wallet(self):
        self.wallet.delete()
        url = reverse('wallet-deposit')
        response = self.client.post(url, {'amount': 50}, format='json', **self.auth_header)
        self.assertEqual(response.status_code, 404)

    def test_withdraw_success(self):
        url = reverse('wallet-withdraw')
        response = self.client.post(url, {'amount': 30}, format='json', **self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.wallet.refresh_from_db()
        self.assertEqual(float(self.wallet.balance), 70.0)

    def test_withdraw_insufficient_balance(self):
        url = reverse('wallet-withdraw')
        response = self.client.post(url, {'amount': 200}, format='json', **self.auth_header)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_withdraw_unauthenticated(self):
        url = reverse('wallet-withdraw')
        response = self.client.post(url, {'amount': 10}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_withdraw_missing_wallet(self):
        # Remove wallet
        self.wallet.delete()
        url = reverse('wallet-withdraw')
        response = self.client.post(url, {'amount': 10}, format='json', **self.auth_header)
        self.assertEqual(response.status_code, 404)
