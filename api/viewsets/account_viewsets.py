from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from account.models import UserModel
from account.serializers import UserProfileSerializer

class AccountViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get', 'put'])
    def profile(self, request):
        if request.method == 'GET':
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response({'error': 'Ancien mot de passe incorrect'}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Mot de passe modifié avec succès'}) 