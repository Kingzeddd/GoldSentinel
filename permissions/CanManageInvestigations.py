from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser
class CanManageInvestigations(permissions.BasePermission):
    """Permission pour gérer investigations"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated or isinstance(request.user , AnonymousUser):
            return False
        
        # Responsables peuvent tout gérer, Agents leurs propres investigations
        return request.user.user_authorities.filter(
            authority__name__in=['Responsable Régional', 'Agent Terrain'],
            status=True
        ).exists()
    
    def has_object_permission(self, request, view, obj):
        """Permission au niveau objet pour investigations"""
        if not request.user.is_authenticated:
            return False
        
        # Responsable peut modifier toutes les investigations
        if request.user.user_authorities.filter(
            authority__name='Responsable Régional', status=True
        ).exists():
            return True
        
        # Agent peut seulement modifier ses investigations assignées
        if request.user.user_authorities.filter(
            authority__name='Agent Terrain', status=True
        ).exists():
            return obj.assigned_to == request.user
        
        return False
    
    message = "Gestion investigations réservée aux Responsables et Agents Terrain"
