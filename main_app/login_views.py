from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from datetime import datetime
from bson import ObjectId

from .forms import LoginForm, RegistrationForm, TradeForm
from main_app.models import client as mongo_client
from .user_model import UserRepository, client


def login_page(request):
    registration_form = RegistrationForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user_collection = client['tradingApp']['users']
            user_data = user_collection.find_one({'username': form.cleaned_data['username']})
            if user_data and check_password(form.cleaned_data['password'], user_data['hashed_password']):
                request.session['user_id'] = str(user_data['_id'])
                request.session['username'] = user_data['username']
                messages.success(request, 'Login successful!')
                return redirect('landing_page')
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'registration_form': registration_form})


def logout_view(request):
    request.session.flush()
    messages.info(request, 'You have been logged out.')
    return redirect('about_page')


@login_required
def new_trade(request):
    if request.method == 'POST':
        form = TradeForm(request.POST)
        if form.is_valid():
            trades_collection = mongo_client['tradingApp']['trades']

            trade_doc = {
                '_id': ObjectId(),
                'userId': request.user.id,
                'username': request.user.username,
                'symbol': form.cleaned_data['symbol'],
                'side': form.cleaned_data['side'],
                'qty': form.cleaned_data['qty'],
                'price': float(form.cleaned_data['price']),
                'createdAt': datetime.utcnow(),
            }

            trades_collection.insert_one(trade_doc)
            messages.success(request, 'Trade saved.')
            return redirect('landing_page')
    else:
        form = TradeForm()

    return render(request, 'new_trade.html', {'form': form})


@login_required
def landing_page(request):
    trades_collection = mongo_client['tradingApp']['trades']
    user_trades = list(trades_collection.find({'userId': request.user.id}).sort('createdAt', -1))
    return render(request, 'landing_page.html', {'trades': user_trades})


def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        login_form = LoginForm()

        if form.is_valid():
            user = form.save_to_mongodb()
            request.session['user_id'] = str(user.id)
            request.session['username'] = user.username
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('landing_page')

        messages.error(request, 'Please correct the errors below.')
        return render(request, 'login.html', { 'registration_form': form})

    return redirect('landing_page')