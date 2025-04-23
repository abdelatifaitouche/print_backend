from rest_framework.serializers import ModelSerializer
from .models import *
from rest_framework import serializers
from user_management.models import Company , CustomUser
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

        


