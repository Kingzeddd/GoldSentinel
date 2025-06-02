from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser
class CanViewLogs(permissions.BasePermission):
    """Permission pour voir les logs système"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated or isinstance(request.user, AnonymousUser):
            return False
        
        # Seuls Responsables et Administrateurs
        return request.user.user_authorities.filter(
            authority__name__in=['Responsable Régional', 'Administrateur'],
            status=True
        ).exists()
    
    message = "Accès logs réservé aux Responsables Régionaux et Administrateurs"
