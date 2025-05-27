from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
# Create your views here.
from .models import *
from .serializers import  *
from rest_framework.permissions import AllowAny
from user_management.authenticate import CustomAuthentication
from django.http import HttpResponse
from django.db.models import Count
from django.utils.timezone import now, timedelta
from user_management.models import Company
from rest_framework import generics 
from rest_framework.exceptions import NotFound, ValidationError
from api.utils.invoice_generator import create_invoice
from api.utils.factories import GoogleDriveClientFactory

class TestingView(APIView):
    authentication_classes =[CustomAuthentication]
    def get(self , request):
        print(request.data)
        return Response({"current user : " : "testing"})


    def post(self , request):
        data = request.data
        data["user"] = request.user.id
        data["company"] = request.user.company.id
        return Response({'data' : data})




class OrderListView(APIView):
    authentication_classes = [CustomAuthentication]
    def get(self , request):
        print("request user" , request.user)
        if request.user.role == "admin" or request.user.role == "operator" :
            orders_listing = Order.objects.all().order_by('-created_at')
            orders_serializer = OrderSerializer(orders_listing , many=True)
            return Response({"Orders" : orders_serializer.data} , status = status.HTTP_200_OK)
        else : 
            orders_listing = Order.objects.filter(company_id = request.user.company).order_by('-created_at')
            orders_serializer = OrderSerializer(orders_listing , many = True)
            return Response({"Orders" : orders_serializer.data} , status = status.HTTP_200_OK)
    


    def post(self, request):
        """
        REFACTOR THIS FUNCTION  : 
            - Change what the payload is to : {order , user , company , items : [item_data , item_data]}
            - item_data = {item_name , file , google_drive_id , order }
            - separate this function into two : extract the items from the request , create the items objects
            - once this done and tested, think about offloading this into celery and redis (async work)
        """
        data = request.data
        # Add user and company to the order data
        data['user_id'] = request.user.id
        data['company'] = request.user.company.id
        # Pass context with request to the serializer
        
        order_serializer = OrderSerializer(data=data, context={'request': request})
        client = GoogleDriveClientFactory.from_env()
        if not order_serializer.is_valid():
        # Save the order object            
            return Response({"error": order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        order = order_serializer.save()
        
        
        files = request.FILES  # Files are in request.FILES   

        items_data = []
        for item in range(len(data['items'])):
            item_data = {
                    "item_name": data['items'][item]['item_name'],
                    "order": order.id,  # Assign the order to the item
                }

            # Check if a file is present in the current item
            file_field_name = f"items[{i}][file]"
            if file_field_name in files:
                item_file = files[file_field_name]
                
                # Upload file to Google Drive and get the file ID
                file_id = client.upload_file_to_drive(item_file , "SOLIC")  # Assuming this function handles Google Drive upload

                # Save the Google Drive file ID in the item data
                item_data["google_drive_file_id"] = file_id

                items_data.append(item_data)
            print("check if the items data contains everything" , items_data)
        # Save each item related to the order
            for item_data in items_data:
                order_item_serializer = OrderItemSerializer(data=item_data)
                if order_item_serializer.is_valid():
                    order_item_serializer.save()

            return Response({"response": "Order Created"}, status=status.HTTP_201_CREATED)
    
class DownloadFileView(APIView):
    def get(self, request, file_id, *args, **kwargs):
        try:
            # Call the download function with file_id directly
            client = GoogleDriveClientFactory.from_env()
            file_name, file_handle = client.download_file_from_google_drive(file_id)

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
        print(order_serializer.data)
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
        print(order_item_serializer.data)
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
        
        
class CompaniesListView(APIView):
    authentication_classes = [CustomAuthentication]

    def get(self , request):
        companie_objects = Company.objects.all()
        companies_serializer = CompanySerializer(companie_objects , many=True)
        
        return Response({"response" : companies_serializer.data} , status=status.HTTP_200_OK)
    
    
    
    def post(self , request):
        data = request.data 
        
        company_serializer = CompanySerializer(data = data)
        
        if company_serializer.is_valid():
            company_serializer.save()
            return Response({'response' : "Company Created"} , status=status.HTTP_200_OK)
        else : 
            return Response({'response' : company_serializer.errors} , status=status.HTTP_400_BAD_REQUEST)
        



class CompanyDetailView(APIView):
    """
    Handles retrieval, partial update, and deletion of a single company.
    """
    authentication_classes = [CustomAuthentication]

    def get_object(self, pk):
        return get_object_or_404(Company, pk=pk)

    def get(self, request, pk):
        """
        Retrieve company details by ID.
        """
        company = self.get_object(pk)
        serializer = CompanySerializer(company)
        return Response({"response": serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """
        Partially update a company's information.
        """
        company = self.get_object(pk)
        serializer = CompanySerializer(company, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"response": "Company updated"}, status=status.HTTP_200_OK)

        return Response({"response": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a company by ID.
        """
        company = self.get_object(pk)
        company.delete()
        return Response({"response": "Company deleted"}, status=status.HTTP_200_OK)

class CompanyUserListView(APIView):
    authentication_classes = [CustomAuthentication]
    
    def get(self , request , pk):
        
        company_users = CustomUser.objects.filter(company_id = pk)
        
        company_user_serializer = UserPublicSerializer(company_users , many=True)
        
        return Response({'reponse' : company_user_serializer.data} , status=status.HTTP_200_OK)
    

        
class UsersListView(APIView):
    authentication_classes = [CustomAuthentication]
    def get(self , request):
        users = CustomUser.objects.all()
        
        users_serializer = UserPublicSerializer(users , many = True)
        
        return Response({'users' : users_serializer.data} , status=status.HTTP_200_OK)



class UserDetailView(APIView):
    
    def get(self, request, pk):
        try:
            user_model = get_object_or_404(CustomUser, pk=pk)
            user_serializer = UserPublicSerializer(user_model)
            return Response({'response': user_serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, pk):
        try:
            user = get_object_or_404(CustomUser, pk=pk)
            data = request.data
            user_serializer = UserUpdateSerializer(instance=user, data=data, partial=True)
            
            if user_serializer.is_valid():
                user_serializer.save()
                return Response(user_serializer.data, status=status.HTTP_200_OK)
            
            raise ValidationError(user_serializer.errors)

        except ValidationError as ve:
            return Response({"errors": ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        except NotFound:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            user = get_object_or_404(CustomUser, pk=pk)
            user.delete()
            return Response({'response': "User deleted"}, status=status.HTTP_200_OK)
        except NotFound:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BlockUserView(APIView):
    authentication_classes = [CustomAuthentication]
    def post(self, request, pk):
        # Only admins can block users
        if request.user.role != 'admin':
            return Response({"detail": "Only admins can block users."},
                            status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(CustomUser, pk=pk)

        if not user.is_active:
            return Response({"detail": "User is already blocked."},
                            status=status.HTTP_400_BAD_REQUEST)

        user.is_active = False
        user.save()

        return Response({"detail": f"User '{user.username}' has been blocked."},
                        status=status.HTTP_200_OK)



class UnblockUserView(APIView):
    authentication_classes = [CustomAuthentication]
    def post(self, request, pk):
        if request.user.role != 'admin':
            return Response({"detail": "Only admins can unblock users."},
                            status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(CustomUser, pk=pk)

        if user.is_active:
            return Response({"detail": "User is already active."},
                            status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()

        return Response({"detail": f"User '{user.username}' has been unblocked."},
                        status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    authentication_classes = [CustomAuthentication]
    def post(self, request, pk=None):
        user = request.user

        # Admin wants to change another user's password
        if pk:
            if not user.is_staff:
                return Response({'error': 'Only admins can change other users\' passwords.'},
                                status=status.HTTP_403_FORBIDDEN)
            user = get_object_or_404(CustomUser, pk=pk)

        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        new_password2 = request.data.get('new_password2')

        if not new_password or not new_password2:
            return Response({'error': 'Both new password fields are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if new_password != new_password2:
            return Response({'error': 'New passwords do not match.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Regular users must provide current password
        if not request.user.is_staff or (pk and request.user.pk == int(pk)):
            if not current_password:
                return Response({'error': 'Current password is required.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if not user.check_password(current_password):
                return Response({'error': 'Current password is incorrect.'},
                                status=status.HTTP_403_FORBIDDEN)

        user.set_password(new_password)
        user.save()

        return Response({'response': 'Password changed successfully.'},
                        status=status.HTTP_200_OK)

class StatusViewList(APIView):
    def get(self , request) :
        return
    
    def post(self , request):
        return
    
    
class GenerateInvoice(APIView):
    
    def post(self , request):
        
        invoice_items = [
        {"description": "Website Design", "quantity": 1, "unit_price": 2000.00},
        {"description": "Hosting (1 year)", "quantity": 1, "unit_price": 300.00},
        {"description": "SEO Services", "quantity": 5, "unit_price": 150.00},
        ]


        invoice = create_invoice(invoice_items)
        invoice.seek(0)
        response = HttpResponse(invoice, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_testing.pdf"'
        return response
