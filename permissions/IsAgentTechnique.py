from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser

class IsAgentTechnique(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated or isinstance(request.user, AnonymousUser):
            return False
        
        return request.user.user_authorities.filter(
            authority__name='Agent Technique',
            status=True
        ).exists()

    message = "Accès réservé aux Agents Techniques"