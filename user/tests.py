from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from wallet.models import Wallet
from unittest.mock import patch

class UserAuthTests(APITestCase):
    def setUp(self):
        self.client.raise_request_exception = False

    def test_user_registration(self):
        url = reverse('register')
        data = {'username': 'testuser', 'password': 'testpass'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username='testuser')
        self.assertTrue(Wallet.objects.filter(user=user).exists())
        wallet = Wallet.objects.get(user=user)
        self.assertEqual(wallet.balance, 0)

    def test_registration_with_existing_username(self):
        User.objects.create_user(username='testuser', password='testpass')
        url = reverse('register')
        data = {'username': 'testuser', 'password': 'newpass'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_registration_with_missing_fields(self):
        url = reverse('register')
        data = {'username': ''}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_user_registration_wallet_creation_failure(self):
        url = reverse('register')
        data = {'username': 'failuser', 'password': 'testpass'}
        with patch('wallet.models.Wallet.objects.create', side_effect=Exception('Wallet creation failed')):
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, 500)
            self.assertFalse(User.objects.filter(username='failuser').exists())       

    def test_user_login(self):
        User.objects.create_user(username='testuser', password='testpass')
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'testpass'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_login_with_wrong_password(self):
        User.objects.create_user(username='testuser', password='testpass')
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'wrongpass'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_with_nonexistent_user(self):
        url = reverse('login')
        data = {'username': 'nouser', 'password': 'nopass'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)  