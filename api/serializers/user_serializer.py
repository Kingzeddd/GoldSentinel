from rest_framework import serializers
from account.models.user_model import UserModel


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = UserModel
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name',
                  'job_title', 'institution', 'authorized_region']
        read_only_fields = ['id']