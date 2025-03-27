from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
from .models import *
from .serializers import  *

class OrderListView(APIView):

    def get(self , request):
        orders_listing = Order.objects.all()
        orders_serializer = OrderSerializer(orders_listing , many=True)
        return Response({"Orders" : orders_serializer.data} , status = status.HTTP_200_OK)
    

    def post(self , request):

        data = request.data
        order_serializer = OrderSerializer(data = data)
        if order_serializer.is_valid():
            order_serializer.save()

            items_data = request.data.get('items' , [])
            print(items_data)

            return Response({'response' : 'Order Created'} , status=status.HTTP_201_CREATED)
        return Response({'response' :order_serializer.errors} , status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):
    pass



