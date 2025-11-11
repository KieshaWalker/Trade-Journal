from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import loader
# Create your views here.


def about_page(request):
    return render(request, 'login.html')

def navbar(request):
    return render(request, 'nav.html')

def register_page(request):
    return HttpResponse("Registration Page Under Construction")

@login_required
def landing_page(request):
    return render(request, 'landing.html')