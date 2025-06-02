from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser

class IsResponsableOrAgent(permissions.BasePermission):
    """Permission pour Responsable Régional OU Agent Terrain"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated or isinstance(request.user, AnonymousUser):
            return False
        
        return request.user.user_authorities.filter(
            authority__name__in=['Responsable Régional', 'Agent Terrain'],
            status=True
        ).exists()
    
    message = "Accès réservé aux Responsables Régionaux et Agents Terrain"
