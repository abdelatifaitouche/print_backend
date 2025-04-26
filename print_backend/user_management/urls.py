from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import CustomObtainViewPair , VerifyToken,LogoutView , GetUserRole , UserRegisterView


urlpatterns = [
    path('login/' , CustomObtainViewPair.as_view() , name="auth login"),
    path('verify/' , VerifyToken.as_view() , name="verify token"),
    path('logout/' , LogoutView.as_view() , name="logout view"),
    path('role/' , GetUserRole.as_view() , name="user role"),
    path('createUser/' ,UserRegisterView.as_view() , name='register user' )
    
]