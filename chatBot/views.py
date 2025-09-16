# chatBot/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import time
import uuid
from datetime import datetime
from .models import ChatSession, ChatMessage, ChatFeedback
from .neural_network import NewsletterChatbot
import logging

logger = logging.getLogger(__name__)

# Instancia global del chatbot (se carga una vez)
chatbot_instance = None

def get_chatbot():
    """Obtiene la instancia del chatbot, la carga si es necesario"""
    global chatbot_instance
    if chatbot_instance is None:
        chatbot_instance = NewsletterChatbot()
        if not chatbot_instance.load_model():
            logger.error("No se pudo cargar el modelo del chatbot")
            return None
        if not chatbot_instance.load_intents():
            logger.error("No se pudieron cargar los intents del chatbot")
            return None
    return chatbot_instance

@method_decorator(csrf_exempt, name='dispatch')
class ChatView(View):
    """Vista principal para el chat"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id')
            
            if not message:
                return JsonResponse({
                    'error': 'Mensaje vacío'
                }, status=400)
            
            # Obtener o crear sesión
            if session_id:
                try:
                    session = ChatSession.objects.get(session_id=session_id, is_active=True)
                except ChatSession.DoesNotExist:
                    session = self._create_session(request)
            else:
                session = self._create_session(request)
            
            # Obtener respuesta del chatbot
            start_time = time.time()
            chatbot = get_chatbot()
            
            if not chatbot:
                return JsonResponse({
                    'error': 'Chatbot no disponible'
                }, status=503)
            
            response, intent, confidence = chatbot.get_response(message)
            response_time = time.time() - start_time
            
            # Guardar mensaje en la BD
            chat_message = ChatMessage.objects.create(
                session=session,
                message=message,
                response=response,
                confidence=confidence,
                intent=intent,
                response_time=response_time
            )
            
            return JsonResponse({
                'response': response,
                'session_id': session.session_id,
                'message_id': chat_message.id,
                'intent': intent,
                'confidence': round(confidence, 3),
                'response_time': round(response_time, 3)
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            logger.exception("Error en ChatView")
            return JsonResponse({
                'error': 'Error interno del servidor'
            }, status=500)
    
    def _create_session(self, request):
        """Crea una nueva sesión de chat"""
        session_id = str(uuid.uuid4())
        user = request.user if request.user.is_authenticated else None
        
        return ChatSession.objects.create(
            session_id=session_id,
            user=user
        )

@method_decorator(csrf_exempt, name='dispatch')
class ChatFeedbackView(View):
    """Vista para feedback de mensajes"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            message_id = data.get('message_id')
            rating = data.get('rating')
            feedback_text = data.get('feedback_text', '')
            
            if not message_id or rating is None:
                return JsonResponse({
                    'error': 'message_id y rating son requeridos'
                }, status=400)
            
            if rating not in [1, 2, 3, 4, 5]:
                return JsonResponse({
                    'error': 'rating debe ser entre 1 y 5'
                }, status=400)
            
            try:
                message = ChatMessage.objects.get(id=message_id)
            except ChatMessage.DoesNotExist:
                return JsonResponse({
                    'error': 'Mensaje no encontrado'
                }, status=404)
            
            # Crear o actualizar feedback
            feedback, created = ChatFeedback.objects.get_or_create(
                message=message,
                defaults={
                    'rating': rating,
                    'feedback_text': feedback_text
                }
            )
            
            if not created:
                feedback.rating = rating
                feedback.feedback_text = feedback_text
                feedback.save()
            
            return JsonResponse({
                'success': True,
                'feedback_id': feedback.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            logger.exception("Error en ChatFeedbackView")
            return JsonResponse({
                'error': 'Error interno del servidor'
            }, status=500)

class ChatHistoryView(View):
    """Vista para obtener historial de chat"""
    
    def get(self, request):
        session_id = request.GET.get('session_id')
        limit = int(request.GET.get('limit', 20))
        
        if not session_id:
            return JsonResponse({
                'error': 'session_id es requerido'
            }, status=400)
        
        try:
            session = ChatSession.objects.get(session_id=session_id)
            messages = ChatMessage.objects.filter(session=session).order_by('-created_at')[:limit]
            
            history = []
            for msg in reversed(messages):
                history.append({
                    'id': msg.id,
                    'message': msg.message,
                    'response': msg.response,
                    'intent': msg.intent,
                    'confidence': msg.confidence,
                    'created_at': msg.created_at.isoformat(),
                    'response_time': msg.response_time
                })
            
            return JsonResponse({
                'history': history,
                'session_id': session_id
            })
            
        except ChatSession.DoesNotExist:
            return JsonResponse({
                'error': 'Sesión no encontrada'
            }, status=404)
        except Exception as e:
            logger.exception("Error en ChatHistoryView")
            return JsonResponse({
                'error': 'Error interno del servidor'
            }, status=500)

class ChatStatsView(View):
    """Vista para estadísticas del chat"""
    
    def get(self, request):
        try:
            # Estadísticas generales
            total_sessions = ChatSession.objects.count()
            total_messages = ChatMessage.objects.count()
            active_sessions = ChatSession.objects.filter(is_active=True).count()
            
            # Estadísticas de intents
            from django.db.models import Count, Avg
            intent_stats = ChatMessage.objects.values('intent').annotate(
                count=Count('id'),
                avg_confidence=Avg('confidence')
            ).order_by('-count')
            
            # Estadísticas de feedback
            feedback_stats = ChatFeedback.objects.values('rating').annotate(
                count=Count('id')
            ).order_by('rating')
            
            # Promedio de tiempo de respuesta
            avg_response_time = ChatMessage.objects.aggregate(
                avg_time=Avg('response_time')
            )['avg_time'] or 0
            
            return JsonResponse({
                'total_sessions': total_sessions,
                'total_messages': total_messages,
                'active_sessions': active_sessions,
                'intent_distribution': list(intent_stats),
                'feedback_distribution': list(feedback_stats),
                'avg_response_time': round(avg_response_time, 3)
            })
            
        except Exception as e:
            logger.exception("Error en ChatStatsView")
            return JsonResponse({
                'error': 'Error interno del servidor'
            }, status=500)

@require_http_methods(["GET"])
def health_check(request):
    """Verifica el estado del chatbot"""
    try:
        chatbot = get_chatbot()
        if chatbot:
            # Probar con un mensaje simple
            response, intent, confidence = chatbot.get_response("hola")
            return JsonResponse({
                'status': 'healthy',
                'model_loaded': True,
                'test_response': response[:50] + '...' if len(response) > 50 else response
            })
        else:
            return JsonResponse({
                'status': 'unhealthy',
                'model_loaded': False,
                'error': 'No se pudo cargar el modelo'
            }, status=503)
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'model_loaded': False,
            'error': str(e)
        }, status=503)
