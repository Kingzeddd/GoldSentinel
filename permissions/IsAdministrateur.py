from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser


class IsAdministrateur(permissions.BasePermission):
    """Permission pour Administrateur uniquement"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated or isinstance(request.user, AnonymousUser):
            return False
        
        return (request.user.is_superuser or 
                request.user.user_authorities.filter(
                    authority__name='Administrateur',
                    status=True
                ).exists())
    
    message = "Accès réservé aux Administrateurs"