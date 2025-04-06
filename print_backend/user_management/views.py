from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView,TokenVerifyView
# Create your views here.
from django.conf import settings
from rest_framework.views import APIView
from .authenticate import CustomAuthentication
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from .serializers import CustomObtainPairTokenSerializer

#the logic for authentication 
    # we have a custom user Model
        # we need to authenticate the user using jwt auth (access and refresh token)
        
        
        
class CustomObtainViewPair(TokenObtainPairView):
    serializer_class = CustomObtainPairTokenSerializer
    def post(self , request , *args , **kwargs):
        response = super().post(request , *args , **kwargs)
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        
        #we need a way to return these inside an http only cookie instead of the simple response bodu
        response.set_cookie(
            key = settings.SIMPLE_JWT['AUTH_COOKIE'] ,
            value=access_token , 
            domain=settings.SIMPLE_JWT["AUTH_COOKIE_DOMAIN"],
            path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )

        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='Strict',
            path='/'
        )
        
        response.data = {}
        
        return response
    
    
class VerifyToken(TokenVerifyView):
    authentication_classes = [CustomAuthentication]
    def post(self , request , *args ,**kwargs):
        access_token = request.COOKIES.get("access_token")
        
        if not access_token : 
            return Response({"details" : 'No access provided'} , status=status.HTTP_400_BAD_REQUEST)
        
        data = {"token" : access_token}
        
        serializer = self.get_serializer(data = data)
        
        if serializer.is_valid():
            return Response({"details" : "Valid token"} , status=status.HTTP_200_OK)
        return Response(serializer.errors , status=status.HTTP_401_UNAUTHORIZED)
    
    
class LogoutView(APIView):
    authentication_classes = [CustomAuthentication]

    def post(self , request , *args , **kwargs):
        response = Response({'detail': 'Logged out successfully'})

        token = RefreshToken(request.COOKIES.get("refresh_token"))
        token.blacklist()
        response.delete_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            domain=settings.SIMPLE_JWT["AUTH_COOKIE_DOMAIN"]
        )   

        response.delete_cookie(
            key='refresh_token',
            path='/',  # Ensure it's the same path as when it was set
            samesite='Strict',
        )   

        response.set_cookie(
            key='access_token',
            value='',
            expires='Thu, 01 Jan 1970 00:00:00 GMT',  # Expire immediately
            path='/',
            httponly=True,
            secure=True,
            samesite='None',
            )

        response.set_cookie(
            key='refresh_token',
            value='',
            expires='Thu, 01 Jan 1970 00:00:00 GMT',
            path='/',
            httponly=True,
            secure=True,
            samesite='None',
            )
        return response
    
    
class GetUserRole(APIView):
    def get(self , request):
        access_token = request.COOKIES.get("access_token")
        
        if not access_token : 
            return Response({'details' : "invalid token"} , status=status.HTTP_401_UNAUTHORIZED)
        
        try : 
            token = AccessToken(access_token)
            user_role = token['role']
            return Response({'user_role' : user_role} , status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"details" : "Invalid or expired token"} , status=status.HTTP_400_BAD_REQUEST) 
        
        