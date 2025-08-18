from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FavoriteViewSet

# acepta URLs con o sin slash final
router = DefaultRouter(trailing_slash=True)

# MUY IMPORTANTE: registrar 'favorites' PRIMERO
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'', UserViewSet, basename='user')

urlpatterns = router.urls
