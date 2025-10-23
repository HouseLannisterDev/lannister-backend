from django.http import JsonResponse, HttpRequest
from django.views import View
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from chatbot.services.chatbot_factory import ChatbotFactory

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name="dispatch")
class ChatbotView(View):
    """API View para interactuar con el Chatbot."""

    def post(self, request: HttpRequest):
      
            # 1. Parsear body (esperamos JSON con { "question": "..." })
            body = json.loads(request.body.decode("utf-8"))
            question = body.get("question")

            if not question:
                return JsonResponse(
                    {"error": "El campo 'question' es obligatorio."},
                    status=400,
                    json_dumps_params={"ensure_ascii": False, "indent": 2},
                )

            # 2. Crear servicio desde el Factory
            service = ChatbotFactory.create()

            # 3. Obtener respuesta (ahora retorna un dict)
            result = service.get_answer(question)

            # 4. Retornar en JSON con metadata adicional
            return JsonResponse(
                {
                    "question": question,
                    "answer": result["answer"],
                    "confidence": round(result["confidence"], 3),
                    "type": result["type"],  # "faq" o "news_search"
                    "category": result.get("category"),  # Solo si es news_search
                    "news_count": result.get("count")  # Solo si es news_search
                },
                safe=False,
                json_dumps_params={"ensure_ascii": False, "indent": 2},
            )

      
