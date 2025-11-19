"""Django REST Framework serializers for trading app models."""

from rest_framework import serializers
from django.contrib.auth.models import User as DjangoUser


class UserSerializer(serializers.ModelSerializer):
    """Serializer for Django's built-in User model."""
    
    class Meta:
        model = DjangoUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class TradeListSerializer(serializers.Serializer):
    """Simple serializer for trade data (example)."""
    
    tradeId = serializers.CharField()
    side = serializers.CharField()
    qty = serializers.IntegerField()
    price = serializers.FloatField()
    status = serializers.CharField()


class JournalEntrySerializer(serializers.Serializer):
    """Simple serializer for journal entry data (example)."""
    
    entryId = serializers.CharField()
    title = serializers.CharField(required=False)
    setup = serializers.CharField(required=False)
    thesis = serializers.CharField(required=False)
    emotions = serializers.CharField(required=False)
