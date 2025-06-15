from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from wallet.models import Wallet
from order.models import Order
from rest_framework.authtoken.models import Token

class OrderAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.wallet1 = Wallet.objects.create(user=self.user1, balance=100)
        self.wallet2 = Wallet.objects.create(user=self.user2, balance=100)
        self.order1 = Order.objects.create(user=self.user1, currency='ABAN', amount=5)
        self.order2 = Order.objects.create(user=self.user2, currency='BTC', amount=2)
        self.auth_header1 = {'HTTP_AUTHORIZATION': f'Token {self.token1.key}'}
        self.auth_header2 = {'HTTP_AUTHORIZATION': f'Token {self.token2.key}'}

    def test_get_orders_for_user(self):
        url = reverse('order-list')
        response = self.client.get(url, **self.auth_header1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order1.id)

    def test_get_order_by_id_success(self):
        url = reverse('order-detail', args=[self.order1.id])
        response = self.client.get(url, **self.auth_header1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.order1.id)

    def test_get_order_by_id_not_found(self):
        url = reverse('order-detail', args=[self.order2.id])
        response = self.client.get(url, **self.auth_header1)
        self.assertEqual(response.status_code, 404)

    def test_post_order_success(self):
        url = reverse('order-list')
        data = {'currency': 'ABAN', 'amount': 10}
        response = self.client.post(url, data, format='json', **self.auth_header1)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['currency'], 'ABAN')
        self.assertEqual(float(response.data['amount']), 10.0)

    def test_post_order_insufficient_balance(self):
        url = reverse('order-list')
        self.wallet1.balance = 1
        self.wallet1.save()
        data = {'currency': 'ABAN', 'amount': 10}
        response = self.client.post(url, data, format='json', **self.auth_header1)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_post_order_unauthenticated(self):
        url = reverse('order-list')
        data = {'currency': 'ABAN', 'amount': 10}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_get_orders_unauthenticated(self):
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
