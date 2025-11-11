
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from . import api_views
from . import login_views

# REST API Router
router = DefaultRouter()
router.register(r'users', api_views.UserViewSet, basename='user')

urlpatterns = [
    # Web pages
    path('', views.about_page, name='about_page'),

    # API endpoints
    path('api/', api_views.api_root, name='api-root'),
    path('api/', include(router.urls)),

    # login endpoints
    path('login/', login_views.login_page, name='login_page'),
    path('landing/', views.landing_page, name='landing_page'),
    path('navbar/', views.navbar, name='navbar'),
    path('logout/', login_views.logout_view, name='logout_view'),
    
    # add a trade
    path('landing/new/', login_views.new_trade, name='new_trade'),

    ]

# Web URLs: localhost:8000/
# API URLs: localhost:8000/api/
