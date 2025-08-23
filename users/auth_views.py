# users/auth_views.py
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(["GET"])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf(request):
    """ Devuelve una cookie csrftoken al cliente """
    return Response({"detail": "CSRF cookie set"})

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    Inicia sesión y crea la cookie de sesión (sessionid).
    Body JSON: {"username": "...", "password": "..."}
    """
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)

    if not user:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    if not user.is_active:
        return Response({"detail": "Inactive account"}, status=status.HTTP_403_FORBIDDEN)

    login(request, user)  # Django crea la sesión y devuelve la cookie
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_authenticated": True
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """ Cierra la sesión y elimina la cookie sessionid """
    logout(request)
    return Response({"detail": "Logged out"}, status=status.HTTP_200_OK)

@api_view(["GET"])
def me(request):
    """ Devuelve info del usuario autenticado """
    if request.user.is_authenticated:
        u = request.user
        return Response({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_authenticated": True
        })
    return Response({"is_authenticated": False}, status=200)
