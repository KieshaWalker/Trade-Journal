
from django import forms
from django.contrib.auth.hashers import make_password
from bson import ObjectId

from .user_model import UserSchema, UserRepository, client


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

        return user_repo.save(user_data)



class TradeForm(forms.Form):
    symbol = forms.CharField(max_length=16, required=True)
    side = forms.ChoiceField(choices=[("BUY", "Buy"), ("SELL", "Sell")], required=True)
    qty = forms.IntegerField(min_value=1, required=True)
    price = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0, required=True)



