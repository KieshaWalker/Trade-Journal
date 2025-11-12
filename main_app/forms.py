
try:
    from pymongo import MongoClient  # optional, used at runtime where needed
except Exception:
    MongoClient = None
from django import forms
from django.forms import ModelForm
from .models import Trade

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

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
    

class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=True)
    bio = forms.CharField(widget=forms.Textarea, required=False)



class TradeForm(forms.Form):
    symbol = forms.CharField(max_length=16, label="Underlying")
    side = forms.ChoiceField(choices=[("BUY","Buy"), ("SELL","Sell")])
    qty = forms.IntegerField(min_value=1, label="Quantity")
    price = forms.DecimalField(max_digits=12, decimal_places=2)