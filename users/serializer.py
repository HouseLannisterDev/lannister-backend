from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Favorite

User = get_user_model()

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'url', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        return Favorite.objects.create(user=user, **validated_data)

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)
    favorites = serializers.SlugRelatedField(many=True, read_only=True, slug_field='url')

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'date_joined',
            'password', 'favorites', 'is_staff', 'is_superuser'
        ]
        read_only_fields = ['id', 'date_joined', 'favorites', 'is_staff', 'is_superuser']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
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
        # reforzamos que no se eleven privilegios por API
        instance.is_staff = False
        instance.is_superuser = False
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
