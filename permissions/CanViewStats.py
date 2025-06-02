from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser
class CanViewStats(permissions.BasePermission):
    """Permission pour voir les statistiques"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated or isinstance(request.user, AnonymousUser):
            return False
        
        # Tous sauf Agent Terrain basique peuvent voir stats
        return request.user.user_authorities.filter(
            authority__name__in=['Responsable Régional', 'Agent Analyste', 'Agent Technique', 'Administrateur'],
            status=True
        ).exists()
    
    message = "Accès statistiques réservé aux Responsables, Analystes et Techniques"
