
from typing import Optional
from django import forms
from django.contrib.auth.hashers import make_password
from bson import ObjectId

from .user_model import UserSchema, UserRepository, client
from .models import TenantScoped, AuditMeta, Instrument, TradeRepository, TradeSchema, strategy_choices, market_sentiment_choices
from pydantic import Field
from typing import List
from pydantic_mongo import PydanticObjectId
from datetime import datetime, date, timezone

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if not username or not password:
            raise forms.ValidationError("Both fields are required.")
        return cleaned_data


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save_to_mongodb(self):
        """Persist the validated user to MongoDB using the Pydantic UserSchema."""
        if not self.is_valid():
            raise ValueError("Form must be valid before saving")

        user_repo = UserRepository(database=client['tradingApp'])

        user_data = UserSchema(
            _id=ObjectId(),
            orgId=ObjectId(),
            email=self.cleaned_data['email'],
            username=self.cleaned_data['username'],
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            hashed_password=make_password(self.cleaned_data['password']),
            role="analyst"
        )

        user_repo.save(user_data)
        return user_data




class TradeForm(forms.Form):
    # Instrument fields
    underlying = forms.CharField(max_length=10, required=True, label="Underlying Symbol")
    optionType = forms.ChoiceField(choices=[('CALL', 'Call'), ('PUT', 'Put')], required=True, label="Option Type")
    strike = forms.FloatField(required=True, label="Strike Price")
    expiry = forms.DateField(required=True, label="Expiry Date")
    
    # Trade fields
    side = forms.ChoiceField(choices=[('BUY', 'Buy'), ('SELL', 'Sell'), ('SHORT', 'Short'), ('COVER', 'Cover')], required=True)
    qty = forms.IntegerField(min_value=1, required=True, label="Quantity")
    price = forms.FloatField(min_value=0, required=True, label="Price")
    fees = forms.FloatField(min_value=0, required=False, initial=0.0, label="Fees")
    status = forms.ChoiceField(choices=[('OPEN', 'Open'), ('CLOSED', 'Closed'), ('CANCELLED', 'Cancelled')], required=True, initial='OPEN')
    strategyTag = forms.MultipleChoiceField(required=True, widget=forms.CheckboxSelectMultiple, choices=[(choice, choice) for choice in strategy_choices], label="Strategy Tags")
    marketSentimentTag = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, choices=[(choice, choice) for choice in market_sentiment_choices], label="Market Sentiment Tags")
    
    def save_to_mongodb(self, user_id):
        """Persist the validated trade to MongoDB using the Pydantic TradeSchema."""
        if not self.is_valid():
            raise ValueError("Form must be valid before saving")
        
        trade_repo = TradeRepository(database=client['tradingApp'])
        
        # Create instrument
        instrument = Instrument(
            underlying=self.cleaned_data['underlying'],
            optionType=self.cleaned_data['optionType'],
            strike=self.cleaned_data['strike'],
            expiry=self.cleaned_data['expiry']
        )
        
        # Create tenant
        tenant = TenantScoped(
            orgId=ObjectId(),  # You might want to set this properly
            userId=ObjectId(user_id)
        )
        
        # Create audit
        audit = AuditMeta()
        
        trade_data = TradeSchema(
            _id=ObjectId(),
            tenant=tenant,
            audit=audit,
            instrument=instrument,
            side=self.cleaned_data['side'],
            qty=self.cleaned_data['qty'],
            price=self.cleaned_data['price'],
            fees=self.cleaned_data['fees'],
            status=self.cleaned_data['status'],
            strategyTag=self.cleaned_data['strategyTag'],
            marketSentimentTag=self.cleaned_data.get('marketSentimentTag', []),
            regimeTagIds=[],
            journalEntryIds=[],
            screenshotIds=[],
            realizedPnL=None,
            unrealizedPnL=None
        )
        
        trade_repo.save(trade_data)
        return trade_data

