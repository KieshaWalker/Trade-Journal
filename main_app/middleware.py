from django.contrib.auth.models import AnonymousUser
from .user_model import client


class MongoAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_id = request.session.get('user_id')
        if user_id:
            user_collection = client['tradingApp']['users']
            user_data = user_collection.find_one({'_id': user_id})
            if user_data:
                class SimpleUser:
                    def __init__(self, data):
                        self.id = str(data['_id'])
                        self.username = data['username']
                        self.is_authenticated = True
                        self.is_active = True
                request.user = SimpleUser(user_data)
            else:
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()

        response = self.get_response(request)
        return response