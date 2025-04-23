from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework.serializers import ModelSerializer
from .models import CustomUser


class CustomObtainPairTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token
    
    
    
class UserPublicSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        exclude = ['password', 'last_login', 'is_superuser', 'user_permissions', 'groups']
        depth = 1 