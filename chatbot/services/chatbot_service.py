
import torch
from transformers import pipeline
from langdetect import detect

from chatbot.services.logging_manager import LoggingManager
from chatbot.services.news_search_service import NewsSearchService




class ChatbotService:
    

    def __init__(self, faqs_manager, normalizer, failover, model_provider):
        # Gestores auxiliares
        self._faqs_manager = faqs_manager
        self._normalizer = normalizer
        self._failover = failover
        
        # Servicio de búsqueda de noticias
        self._news_search = NewsSearchService()

        # Modelo y tokenizer desde el ModelProvider
        self._model = model_provider.get_model()
        self._tokenizer = model_provider.get_tokenizer()

        # Crear pipeline
        self._clf = pipeline(
            "text-classification",
            model=self._model,
            tokenizer=self._tokenizer,
            device=0 if torch.cuda.is_available() else -1,
        )


    def get_answer(self, user_question: str) -> dict:
        """
        Retorna la respuesta a la pregunta del usuario,
        aplicando normalización, modelo y failover.
        Detecta si es una FAQ normal o una búsqueda de noticias.
        
        Returns:
            dict: {
                "answer": str,
                "confidence": float,
                "type": str ("faq" o "news_search")
            }
        """
        # 1. Detectar idioma automáticamente (es/en)
        try:
            lang = detect(user_question)
            if lang not in ["es", "en"]:
                lang = "es"  # fallback por defecto
        except:
            lang = "es"

        # 2. Normalizar
        clean_q = self._normalizer.normalize(user_question, lang=lang)

        # 3. Predicción del modelo
        pred = self._clf(clean_q, truncation=True, max_length=128)[0]  # Aumentado a 128 tokens
        
        label_idx = int(pred["label"].replace("LABEL_", ""))
        confidence = pred["score"]
        
        # 4. Recuperar FAQ asociada
        faq = self._faqs_manager.get_faq_by_label(label_idx)
        
        if faq:
            predicted_answer = faq.get("answer", {}).get(lang)
            if not predicted_answer:  # si no hay en ese idioma, fallback a español
                predicted_answer = faq.get("answer", {}).get("es", self._failover.get_message())
        else:
            predicted_answer = self._failover.get_message()
        
        # 5. Verificar si es búsqueda de noticias
        if predicted_answer == "SEARCH_NEWS":
            # Extraer categoría de la pregunta
            category = self._news_search.extract_category(user_question, clean_q)
            
            if category:
                # Buscar noticias en MongoDB
                news_list = self._news_search.search_news(category, limit=5)
                final_answer = self._news_search.format_news_response(news_list, category, lang)
                
                # Logging de búsqueda de noticias
                LoggingManager.log_interaction(
                    user_question, 
                    f"[NEWS_SEARCH:{category}] {len(news_list)} noticias encontradas", 
                    confidence
                )
                
                return {
                    "answer": final_answer,
                    "confidence": confidence,
                    "type": "news_search",
                    "category": category,
                    "count": len(news_list)
                }
            else:
                # No se detectó categoría específica
                if lang == "es":
                    fallback_msg = "Entiendo que quieres ver noticias, pero ¿de qué categoría? Puedo mostrarte: deportes, moda, tecnología, animales o judiciales."
                else:
                    fallback_msg = "I understand you want to see news, but which category? I can show you: sports, fashion, technology, animals, or judicial."
                
                LoggingManager.log_interaction(user_question, fallback_msg, confidence)
                
                return {
                    "answer": fallback_msg,
                    "confidence": confidence,
                    "type": "faq"
                }
        
        # 6. Logging de FAQ normal
        LoggingManager.log_interaction(user_question, predicted_answer, confidence)

        # 7. Failover por baja confianza
        final_answer = self._failover.check(confidence, predicted_answer)
        
        return {
            "answer": final_answer,
            "confidence": confidence,
            "type": "faq"
        }