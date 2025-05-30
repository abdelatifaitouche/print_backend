#create a custom authentication method that overrides the default auth
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.conf import settings
from .models import CustomUser


class CustomAuthentication(JWTAuthentication):
    """Custom authentication class"""
    def authenticate(self, request):

        header = self.get_header(request)
        if header is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        else:
            raw_token = self.get_raw_token(header)
            
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token) #this the one throwing an exception
        
        
        return self.get_user(validated_token), validated_token
    
    