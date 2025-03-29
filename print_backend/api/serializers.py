from rest_framework.serializers import ModelSerializer
from .models import *
from rest_framework import serializers





class OrderItemSerializer(ModelSerializer):
    file = serializers.FileField(required=False)  # Ensure this is defined

    class Meta : 
        model = OrderItem
        fields = '__all__'




class OrderSerializer(ModelSerializer):
    items = OrderItemSerializer(many=True , read_only = True)
    order_name = serializers.SerializerMethodField()

    class Meta : 
        model = Order
        fields = '__all__'
        
    def get_order_name(self , obj):
        return str(obj)
        


