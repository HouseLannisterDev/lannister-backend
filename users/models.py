# users/models.py
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date


class CustomUser(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def __str__(self):
        return self.username


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'url'], name='unique_favorite_per_user')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} → {self.url}'
