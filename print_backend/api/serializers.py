from rest_framework.serializers import ModelSerializer
from .models import *
from rest_framework import serializers
from user_management.models import Company , CustomUser
from django.contrib.auth.password_validation import validate_password

class CompanySerializer(ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'  # or exclude specific fields if needed

class UserPublicSerializer(ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = CustomUser
        exclude = ['password', 'last_login', 'is_superuser', 'user_permissions', 'groups']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'item_name', 'google_drive_file_id' , 'status']
        




class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserPublicSerializer(read_only=True)
    company = CompanySerializer(read_only=True)
    order_name = serializers.SerializerMethodField() 

    class Meta:
        model = Order
        fields = '__all__'
        
    def get_order_name(self, obj):
        # Return the string representation of the order, which includes the order number
        return str(obj)


    def create(self, validated_data):
        # Get the request object from the context
        request = self.context.get('request')

        # Ensure the user and company are added when saving the Order
        user = request.user if request else None  # Fallback if no request context is available
        company = user.company if user else None  # Assuming the user has a company

        # Add user and company to validated_data before creating the order
        validated_data['user'] = user
        validated_data['company'] = company

        # Now create the order
        order = Order.objects.create(**validated_data)
        return order

        


class RegisterSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'password2', 'company' , 'role']

    def validate(self, attrs):
        # Ensure passwords match first
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields do not match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')  # Remove password2 since it's not in the model

        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])  # Hash password
        user.save()

        #send an email confirmation
        #response = email_verification(validated_data['email'])
        #print(response)

        return user
        