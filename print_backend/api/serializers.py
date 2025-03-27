from rest_framework.serializers import ModelSerializer
from .models import *





class OrderItemSerializer(ModelSerializer):
    class Meta : 
        model = OrderItem
        fields = '__all__'




class OrderSerializer(ModelSerializer):
    items = OrderItemSerializer(many=True , read_only = True)
    class Meta : 
        model = Order
        fields = '__all__'


