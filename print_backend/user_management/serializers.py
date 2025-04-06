from rest_framework_simplejwt.serializers import TokenObtainPairSerializer




class CustomObtainPairTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token