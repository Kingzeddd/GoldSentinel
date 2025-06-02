from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser

class IsResponsableRegional(permissions.BasePermission):
    """Permission pour Responsable Régional uniquement"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated or isinstance(request.user, AnonymousUser):
            return False
        
        return request.user.user_authorities.filter(
            authority__name='Responsable Régional',
            status=True
        ).exists()
    
    message = "Accès réservé aux Responsables Régionaux"