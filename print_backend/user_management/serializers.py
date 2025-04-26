from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework.serializers import ModelSerializer
from .models import CustomUser
from rest_framework import serializers


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
        
        
class UserRegisterSerializer(ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta : 
        model = CustomUser
        fields = ['username' ,'role' , 'email','phone_number' , 'email' , 'password' , 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data
    
    def create(self, validated_data):
        # Remove the password2 field as it's not part of the model
        validated_data.pop('password2')
        
        # Create the user
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            role = validated_data.get('role' , ''),
            phone_number=validated_data.get('phone_number', ''),
            company=validated_data.get('company', None)
        )
        
        # Set the password (using set_password for proper hashing)
        user.set_password(validated_data['password'])
        user.save()
        
        return user