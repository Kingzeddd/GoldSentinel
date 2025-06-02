from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser
class CanLaunchAnalysis(permissions.BasePermission):
    """Permission pour lancer des analyses (Responsables )"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated or isinstance(request.user, AnonymousUser):
            return False
        
        return request.user.user_authorities.filter(
            authority__name__in=['Responsable Régional', 'Agent Technique'],
            status=True
        ).exists()
    
    message = "Lancement d'analyse réservé aux Responsables et Agents Techniques"
