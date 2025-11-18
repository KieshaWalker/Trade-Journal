from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import datetime, date, timezone

from main_app.models import Trade, TradeSchema, TradeRepository, client
from main_app.user_model import UserSchema, UserRepository
from .forms import TradeForm, LoginForm, RegistrationForm


def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Login successful!')
                print("User authenticated:", user)
                return redirect('landing_page')  # Redirect to home after successful login.
            else:
                messages.error(request, 'Invalid username or password.')
                return redirect('login_page')  # Redirect back to login page so message is shown there.
    else:
        form = LoginForm()
    # GET: render the login page template
    return render(request, 'login.html', {'form': form})

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
            
            # Save trade to MongoDB
            db = client['tradingApp']  # Use your database name
            trade_repo = TradeRepository(database=db)
            
            trade_data = TradeSchema(
                tenant={"orgId": "default_org", "userId": str(request.user.id)},
                audit={"createdAt": datetime.now(timezone.utc)},
                instrument={"underlying": symbol, "optionType": "STOCK", "strike": 0.0, "expiry": date.today()},
                side=side,
                qty=qty,
                price=float(price),
                status="OPEN"
            )
            
            trade_repo.save(trade_data)
            
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
    # Fetch trades for the logged-in user from MongoDB
    db = client['tradingApp']
    trades_collection = db['trades']
    
    # Find trades where tenant.userId matches the current user
    user_trades = list(trades_collection.find({"tenant.userId": str(request.user.id)}))
    return render(request, 'landing_page.html', {'trades': user_trades})






def register_page(request): 
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            
            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return redirect('register_page')
            
            # Create Django user for authentication
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Save to MongoDB using UserSchema
            db = client['tradingApp']
            user_repo = UserRepository(database=db)
            
            user_data = UserSchema(
                orgId="default_org",  # You can adjust this
                email=email,
                username=username,
                hashed_password=user.password,  # Django's hashed password
                role="analyst"  # Default role
            )
            
            user_repo.save(user_data)

            messages.success(request, 'Registration successful! Please log in.')
            return redirect('landing_page')
    return render(request, 'login.html')