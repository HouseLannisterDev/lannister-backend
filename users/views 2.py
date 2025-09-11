from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.exceptions import PermissionDenied
from .serializers import UserSerializer, FavoriteSerializer
from .models import Favorite

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]     # abierto para pruebas
    lookup_value_regex = r'\d+'                     # pk solo numérico (evita choques de rutas)

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [BasicAuthentication, SessionAuthentication]  # evita CSRF en Postman

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # (opcional) bloquear si el usuario estuviera inactivo
        if not self.request.user.is_active:
            raise PermissionDenied("Tu cuenta está desactivada.")
        serializer.save()

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("No puedes modificar favoritos de otro usuario.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("No puedes borrar favoritos de otro usuario.")
        instance.delete()
