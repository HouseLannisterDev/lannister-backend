# users/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from datetime import date
from .models import Favorite

User = get_user_model()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'url', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        # asigna automáticamente el usuario autenticado
        request = self.context.get('request')
        return Favorite.objects.create(user=request.user, **validated_data)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)
    # ← Embebemos los favoritos completos (id, url, created_at) en el usuario
    favorites = FavoriteSerializer(many=True, read_only=True)

    # (opcional) si tu CustomUser tiene @property age, puedes exponerlo:
    # age = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'date_joined', 'date_of_birth',
            'password', 'favorites', 'is_staff', 'is_superuser',
            # 'age',  # ← descomenta si quieres exponer la edad calculada
        ]
        read_only_fields = ['id', 'date_joined', 'favorites', 'is_staff', 'is_superuser']

    # Validar 18+
    def validate_date_of_birth(self, dob):
        if dob is None:
            raise serializers.ValidationError("Este campo es obligatorio.")
        today = date.today()
        years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if years < 18:
            raise serializers.ValidationError("Debe ser mayor de 18 años.")
        return dob

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        # garantizamos que no se eleven privilegios por la API
        user.is_staff = False
        user.is_superuser = False
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        # reforzamos no elevar privilegios por la API
        instance.is_staff = False
        instance.is_superuser = False
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
