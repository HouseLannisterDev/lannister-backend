from django.conf import settings
from django.db import models

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
            models.UniqueConstraint(
                fields=['user', 'url'],
                name='unique_favorite_per_user'
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} → {self.url}'