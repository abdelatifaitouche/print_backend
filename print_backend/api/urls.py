from django.urls import path
from .views import *

urlpatterns = [
    path('orders/ordersList/' , OrderListView.as_view() , name="Order Listing"),
    path('orders/orderItems/' , OrderItemListView.as_view())
]