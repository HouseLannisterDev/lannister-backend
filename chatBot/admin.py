# chatBot/admin.py
from django.contrib import admin
from .models import ChatSession, ChatMessage, ChatFeedback

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['session_id', 'user__username']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'intent', 'confidence', 'response_time', 'created_at']
    list_filter = ['intent', 'created_at']
    search_fields = ['message', 'response', 'intent']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session')

@admin.register(ChatFeedback)
class ChatFeedbackAdmin(admin.ModelAdmin):
    list_display = ['message', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['feedback_text', 'message__message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
