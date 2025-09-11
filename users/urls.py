from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FavoriteViewSet
from .auth_views import csrf, login_view, logout_view, me

# acepta URLs con o sin slash final
router = DefaultRouter(trailing_slash=True)

# MUY IMPORTANTE: registrar 'favorites' PRIMERO
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'', UserViewSet, basename='user')

urlpatterns =[
    path('auth/csrf/', csrf, name='csrf'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/me/', me, name='me'),
] + router.urls
