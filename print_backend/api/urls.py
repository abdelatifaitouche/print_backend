from django.urls import path
from .views import *

urlpatterns = [
    path('orders/ordersList/' , OrderListView.as_view() , name="Order Listing"),
    path('orders/orderDetails/<str:pk>' , OrderDetailView.as_view() , name='Order Details'),
    path('orders/orderItems/' , OrderItemListView.as_view()),
    path('orders/download/<str:file_id>/', DownloadFileView.as_view(), name='download_file'),
    path('orders/ordersStats/' , OrdersStatisticsView.as_view() , name="as view"),
    
    path('orders/orderItem/orderItemDetails/<str:pk>' , OrderItemDetailView.as_view() , name="order Item details"),
    
    
    path('companies/companiesList/' , CompaniesListView.as_view() , name="Company listing"),
    
    
    path('users/usersList/' , UsersListView.as_view() , name="users")


]