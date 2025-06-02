from rest_framework import serializers
from .models import UserModel

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = [
            'id', 'username', 'email', 'full_name', 'job_title',
            'institution', 'authorized_region', 'primary_authority',
            'created_at', 'last_login'
        ]
        read_only_fields = ['id', 'username', 'email', 'created_at', 'last_login'] 