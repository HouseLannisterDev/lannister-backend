# chatBot/urls.py
from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # API endpoints
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('feedback/', views.ChatFeedbackView.as_view(), name='feedback'),
    path('history/', views.ChatHistoryView.as_view(), name='history'),
    path('stats/', views.ChatStatsView.as_view(), name='stats'),
    path('health/', views.health_check, name='health'),
]
