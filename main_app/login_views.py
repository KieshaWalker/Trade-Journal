from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from main_app.models import Trade
from .forms import TradeForm


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('landing_page')  # Redirect to home after successful login.
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login_page')  # Redirect back to login page so message is shown there.
    # GET: render the login page template
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('about_page')  # Redirect to a success page.

@login_required 
def new_trade(request):
    if request.method == 'POST':
        form = TradeForm(request.POST)
        if form.is_valid():
            # Access validated data
            symbol = form.cleaned_data['symbol']
            side = form.cleaned_data['side']
            qty = form.cleaned_data['qty']
            price = form.cleaned_data['price']
            
            # TODO: Save trade to database
            # Trade.objects.create(
            #     user=request.user,
            #     symbol=symbol,
            #     side=side,
            #     qty=qty,
            #     price=price
            # )
            
            messages.success(request, 'Trade saved.')
            return redirect('landing_page')  # PRG pattern
        # If invalid, fall through and re-render form with errors
    else:
        # GET request: instantiate empty form
        form = TradeForm()
    
    # Render for both GET and POST (invalid)
    return render(request, 'new_trade.html', {"form": form})

# show the trades on the landing page
@login_required
def landing_page(request):
    # Fetch trades for the logged-in user
    trades = Trade.objects.filter(user=request.user)
    return render(request, 'landing_page.html', {'trades': trades})