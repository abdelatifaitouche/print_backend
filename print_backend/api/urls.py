from django.urls import path
from .views import *

urlpatterns = [
    
    path("testingView/" , TestingView.as_view() , name="testing") , 
    
    
    path('orders/ordersList/' , OrderListView.as_view() , name="Order Listing"),
    path('orders/orderDetails/<str:pk>' , OrderDetailView.as_view() , name='Order Details'),
    path('orders/orderItems/' , OrderItemListView.as_view()),
    path('orders/download/<str:file_id>/', DownloadFileView.as_view(), name='download_file'),
    path('orders/ordersStats/' , OrdersStatisticsView.as_view() , name="as view"),
    
    path('orders/orderItem/orderItemDetails/<str:pk>' , OrderItemDetailView.as_view() , name="order Item details"),
    
    
    
    
    path('users/usersList/' , UsersListView.as_view() , name="users"),
    path('users/userDetails/<str:pk>' , UserDetailView.as_view() , name="user Details"),
    path("users/blockuser/<str:pk>" , BlockUserView.as_view() , name="block user"),
    path("users/unblockUser/<str:pk>" , UnblockUserView.as_view() , name="unblock user"),
    path('users/change-password/', ChangePasswordView.as_view(), name='change_own_password'),
    path('users/change-password/<int:pk>/', ChangePasswordView.as_view(), name='admin_change_password'),
    
    
    
    
    
    path("orders/generateInvoice/" , GenerateInvoice.as_view() , name="invoice gen"),
    
    path('companies/companyDetails/<str:pk>' , CompanyDetailView.as_view() , name='company details'),
    path('companies/companyDetails/<str:pk>/users' , CompanyUserListView.as_view() , name='company details'),#redondent work, you can simply filter them on the list view 
    #a better thing to do in the company page details, is listigin all theirs orders 

    path('companies/companiesList/' , CompaniesListView.as_view() , name="Company listing"),

    
    
    
    
    path('users/status/' , StatusViewList.as_view() , name="create user")


]