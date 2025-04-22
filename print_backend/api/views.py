from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
# Create your views here.
from .utils.drive_upload import upload_file_to_drive
from .models import *
from .serializers import  *
from rest_framework.permissions import AllowAny
from user_management.authenticate import CustomAuthentication
from django.http import HttpResponse
from .utils.drive_download import download_file_from_google_drive
from django.db.models import Count
from django.utils.timezone import now, timedelta




class OrderListView(APIView):
    authentication_classes = [CustomAuthentication]
    def get(self , request):
        orders_listing = Order.objects.all()
        orders_serializer = OrderSerializer(orders_listing , many=True)
        return Response({"Orders" : orders_serializer.data} , status = status.HTTP_200_OK)
    


    def post(self, request):
        data = request.data
        files = request.FILES  # Files are in request.FILES

    # Add user and company to the order data
        data['user_id'] = request.user.id
        data['company'] = request.user.company.id

    # Pass context with request to the serializer
        order_serializer = OrderSerializer(data=data, context={'request': request})

        if order_serializer.is_valid():
        # Save the order object
            order = order_serializer.save()

            items_data = []
            for i in range(len(data.getlist("items[0][item_name]"))):
                item_data = {
                    "item_name": data.getlist(f"items[{i}][item_name]")[0],
                    "order": order.id,  # Assign the order to the item
                }

            # Check if a file is present in the current item
                file_field_name = f"items[{i}][file]"
                if file_field_name in files:
                    item_file = files[file_field_name]
                
                # Upload file to Google Drive and get the file ID
                    file_id = upload_file_to_drive(item_file)  # Assuming this function handles Google Drive upload

                # Save the Google Drive file ID in the item data
                    item_data["google_drive_file_id"] = file_id

                items_data.append(item_data)

        # Save each item related to the order
            for item_data in items_data:
                order_item_serializer = OrderItemSerializer(data=item_data)
                if order_item_serializer.is_valid():
                    order_item_serializer.save()

            return Response({"response": "Order Created"}, status=status.HTTP_201_CREATED)

        return Response({"error": order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class DownloadFileView(APIView):
    def get(self, request, file_id, *args, **kwargs):
        try:
            # Call the download function with file_id directly
            file_name, file_handle = download_file_from_google_drive(file_id)

            # Prepare response with file as attachment
            response = HttpResponse(file_handle, content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename={file_name}'
            response["file-name"] = file_name
            print(response.headers)
            return response
        
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class OrderDetailView(APIView):
    authentication_classes = [CustomAuthentication]
    def get(self , request , pk):
        order_object = get_object_or_404(Order , pk=pk)
        
        order_serializer = OrderSerializer(order_object)
        return Response({'order' : order_serializer.data} , status=status.HTTP_200_OK)
    
    def put():
        return
    
    
    def patch(self , request , pk):
        print("hitting the patch")
        order_object = get_object_or_404(Order , pk=pk)
        
        data = request.data
        
        print(data)
        
        order_serializer = OrderSerializer(instance = order_object , data = data , partial = True)
        
        if order_serializer.is_valid():
            order_serializer.save()
            return Response({"details" : "Order updated Successfuly"} , status=status.HTTP_200_OK)
        
        return Response({"details" : order_serializer.errors} , status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self , request , pk):
        print('hiiting the delete endpoint')
        order_object = get_object_or_404(Order , pk=pk)
        
        order_object.delete()
        
        return Response({'details' : 'Order Deleted'} , status=status.HTTP_200_OK)
    
    


class OrderItemListView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # Allow file uploads
    authentication_classes = [CustomAuthentication]

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

class OrderItemDetailView(APIView):
    def get(self , request , pk):
        orderItem = get_object_or_404(OrderItem , pk = pk)
        order_item_serializer = OrderItemSerializer(orderItem , many=False)
        
        return Response({'orderItem' : order_item_serializer.data} , status=status.HTTP_200_OK)
    
    
    def patch(self , request , pk):
        
        data = request.data
        
        order_item_object = get_object_or_404(OrderItem , pk = pk)
        
        order_item_serializer = OrderItemSerializer(instance = order_item_object ,data = data , partial = True)
        
        if order_item_serializer.is_valid():
            order_item_serializer.save()
            return Response({'response' : 'Item Updated'} , status=status.HTTP_200_OK)
        
        return Response({'response' : order_item_serializer.errors} , status=status.HTTP_400_BAD_REQUEST)
    
    def put():
        return
    
    def delete():
        return
    
    
    
class OrdersStatisticsView(APIView):
    authentication_classes = [CustomAuthentication]

    def get(self, request):
        # Total orders count
        total_orders = Order.objects.count()
        recent_orders = Order.objects.all().order_by('-created_at')[:5]
        
        total_clients = Company.objects.count()
        recent_orders_serializer = OrderSerializer(recent_orders , many = True)
        # Orders grouped by status
        orders_by_status = (
            Order.objects.values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )

        # New orders in the last 7 days
        seven_days_ago = now() - timedelta(days=7)
        new_orders_count = Order.objects.filter(created_at__gte=seven_days_ago).count()

        return Response({
            "total_orders": total_orders,
            "orders_by_status": orders_by_status,
            "new_orders_last_7_days": new_orders_count,
            "recent_order" : recent_orders_serializer.data,
            "total_clients" : total_clients
        })