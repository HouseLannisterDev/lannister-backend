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
        try:
            print(">>> [DEBUG] ChatbotView POST request received")
            body = json.loads(request.body.decode("utf-8"))
            question = body.get("question")

            if not question:
                print(">>> [DEBUG] Falta el campo 'question'")
                return JsonResponse(
                    {"error": "El campo 'question' es obligatorio."},
                    status=400,
                    json_dumps_params={"ensure_ascii": False, "indent": 2},
                )

            service = ChatbotFactory.create()
            answer = service.get_answer(question)

            return JsonResponse(
                {
                    "question": question,
                    "answer": answer
                },
                safe=False,
                json_dumps_params={"ensure_ascii": False, "indent": 2},
            )
        except Exception as e:
            import traceback
            tb_str = traceback.format_exc()
            try:
                with open("/tmp/chatbot_error.log", "a") as f:
                    f.write("\n--- Exception ---\n")
                    f.write(tb_str)
            except Exception as file_err:
                pass
            print(">>> [ERROR] Excepción en ChatbotView:")
            print(tb_str)
            return JsonResponse(
                {"error": "Error interno en el chatbot."},
                status=500,
                json_dumps_params={"ensure_ascii": False, "indent": 2},
            )

      
