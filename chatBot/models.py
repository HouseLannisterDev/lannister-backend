# chatBot/models.py
from django.db import models
from django.conf import settings

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'chat_sessions'

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    response = models.TextField()
    confidence = models.FloatField(default=0.0)
    intent = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    response_time = models.FloatField(default=0.0)  # tiempo de respuesta en segundos
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['-created_at']

class ChatFeedback(models.Model):
    message = models.OneToOneField(ChatMessage, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, 'Muy malo'), (2, 'Malo'), (3, 'Regular'), (4, 'Bueno'), (5, 'Excelente')])
    feedback_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_feedback'
