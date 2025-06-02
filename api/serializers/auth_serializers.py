from rest_framework import serializers
from account.models.user_model import UserModel
from account.models.user_authority_model import UserAuthorityModel

class LoginSerializer(serializers.Serializer):
    """Serializer pour login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour profil utilisateur avec autorités"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    authorities = serializers.SerializerMethodField()
    primary_authority = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'job_title', 'institution', 'authorized_region',
            'authorities', 'primary_authority', 'is_active'
        ]
        read_only_fields = ['id', 'email']

    def get_authorities(self, obj):
        """Retourne toutes les autorités de l'utilisateur"""
        return list(
            obj.user_authorities.filter(status=True)
            .values_list('authority__name', flat=True)
        )

    def get_primary_authority(self, obj):
        """Retourne l'autorité principale"""
        primary = obj.user_authorities.filter(is_primary=True, status=True).first()
        return primary.authority.name if primary else None

class TokenResponseSerializer(serializers.Serializer):
    """Serializer pour réponse tokens"""
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = UserProfileSerializer()
    authorities = serializers.ListField(child=serializers.CharField())
    expires_in = serializers.IntegerField()
