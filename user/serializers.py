from django.contrib.auth.models import User
from rest_framework import serializers
from wallet.models import Wallet
from django.db import transaction

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data['username'],
                password=validated_data['password']
            )
            Wallet.objects.create(user=user, balance=0)
            return user
