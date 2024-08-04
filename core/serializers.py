from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer

from rest_framework import serializers
0
class UserCreateSerializer(BaseUserCreateSerializer):
    birth_date = serializers.DateField()
    
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password', 'email','first_name', 'last_name', 'birth_date']


class UserSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'email','first_name', 'last_name']