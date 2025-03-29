from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
# Create your views here.
from .utils.drive_upload import upload_file_to_drive
from .models import *
from .serializers import  *

class OrderListView(APIView):

    def get(self , request):
        orders_listing = Order.objects.all()
        orders_serializer = OrderSerializer(orders_listing , many=True)
        return Response({"Orders" : orders_serializer.data} , status = status.HTTP_200_OK)
    


    def post(self, request):
        # Parsing data from request.data
        data = request.data
        files = request.FILES  # Files are in request.FILES
        
        order_serializer = OrderSerializer(data=data)
        if order_serializer.is_valid():
            # Save the order object
            order = order_serializer.save()

            # Extract items data from the request
            items_data = []
            for i in range(len(data.getlist("items[0][item_name]"))):
                item_data = {
                    "item_name": data.getlist(f"items[{i}][item_name]")[0],  # Fetch the item name
                    "order": order.id,  # Assign the order to the item
                }

                # Check if a file is present in the current item
                file_field_name = f"items[{i}][file]"
                if file_field_name in files:
                    item_data["file"] = files[file_field_name]
                    
                    file_id = upload_file_to_drive(item_data["file"])

                    # Save the file ID for later use (if you want to store it)
                    item_data["google_drive_file_id"] = file_id

                items_data.append(item_data)

            # Now, save each item related to the order
            for item_data in items_data:
                order_item_serializer = OrderItemSerializer(data=item_data)
                if order_item_serializer.is_valid():
                    order_item_serializer.save()

            return Response({"response": "Order Created"}, status=status.HTTP_201_CREATED)

        return Response({"error": order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):
    pass


class OrderItemListView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # Allow file uploads

    def get(self , request):
        order_items = OrderItem.objects.all()
        orderitems_serializer = OrderItemSerializer(order_items , many = True)
        
        return Response({'order_items' : orderitems_serializer.data} , status=status.HTTP_200_OK)
    
    
    def post(self , request):
        data = request.data
        order_item_serializer = OrderItemSerializer(data = data)
        
        if order_item_serializer.is_valid():
            order_item = order_item_serializer.save()
            
            #file_id = upload_to_drive(order_item.file.path, order_item.file.name)
            
            return Response({'response' : order_item_serializer.data} , status=status.HTTP_201_CREATED)
        return Response({'response' : order_item_serializer.errors} , status=status.HTTP_400_BAD_REQUEST)
