"""Django REST Framework views for the trading app API."""

from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User as DjangoUser

from .serializers import UserSerializer


@api_view(['GET'])
def api_root(request):
    """Root API endpoint listing available endpoints."""
    return Response({
        'message': 'Welcome to Trading App API',
        'endpoints': {
            'users': '/api/users/',
            'trades': '/api/trades/',
            'journal': '/api/journal/',
            'login': '/api/login/',
            'logout': '/api/logout/',
        }
    })


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User management."""
    
    queryset = DjangoUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = []  # Allow unauthenticated access for now
    
    def get_queryset(self):
        # Optionally filter to current user
        if self.request.user.is_authenticated:
            return DjangoUser.objects.filter(id=self.request.user.id)
        return DjangoUser.objects.none()
