# chatBot/data_preprocessor.py
import json
import re
import nltk
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from mongo_client import get_mongo_client
from textblob import TextBlob
import pandas as pd

logger = logging.getLogger(__name__)

class NewsDataPreprocessor:
    """
    Procesa los datos de noticias de MongoDB para crear intents para el chatbot
    """
    
    def __init__(self):
        self.db = get_mongo_client()
        self.collection = self.db["news"]
        
    def clean_text(self, text: str) -> str:
        """Limpia y normaliza texto"""
        if not text:
            return ""
        
        # Remover caracteres especiales y normalizar
        text = re.sub(r'[^\w\s\áéíóúüñ]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """Extrae palabras clave del texto"""
        try:
            blob = TextBlob(text)
            # Obtener sustantivos y adjetivos
            keywords = [word for word, pos in blob.tags if pos in ['NN', 'NNP', 'JJ']]
            # Filtrar palabras muy cortas
            keywords = [k for k in keywords if len(k) > 3]
            return keywords[:max_keywords]
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def categorize_news(self, title: str, description: str, category: str) -> str:
        """Categoriza la noticia basada en contenido"""
        content = f"{title} {description}".lower()
        
        # Categorías específicas
        if any(word in content for word in ['política', 'gobierno', 'presidente', 'congreso', 'elecciones']):
            return 'politica'
        elif any(word in content for word in ['economía', 'finanzas', 'banco', 'inflación', 'dólar']):
            return 'economia'
        elif any(word in content for word in ['deporte', 'fútbol', 'gol', 'partido', 'jugador']):
            return 'deportes'
        elif any(word in content for word in ['tecnología', 'tech', 'inteligencia artificial', 'software']):
            return 'tecnologia'
        elif any(word in content for word in ['salud', 'médico', 'hospital', 'enfermedad', 'vacuna']):
            return 'salud'
        else:
            return category or 'general'
    
    def generate_intents_from_news(self, limit: int = 10000) -> Dict[str, Any]:
        """
        Genera intents para el chatbot basado en los datos de noticias
        """
        logger.info(f"Generando intents desde {limit} noticias...")
        
        # Obtener noticias de MongoDB
        news_cursor = self.collection.find({}).limit(limit)
        news_data = list(news_cursor)
        
        if not news_data:
            logger.error("No se encontraron noticias en la base de datos")
            return {"intents": []}
        
        logger.info(f"Procesando {len(news_data)} noticias...")
        
        # Agrupar por categorías
        categories = {}
        for news in news_data:
            title = news.get('title', '')
            description = news.get('description', '')
            category = self.categorize_news(title, description, news.get('category', ''))
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append({
                'title': title,
                'description': description,
                'url': news.get('url', ''),
                'source': news.get('source_domain', ''),
                'date': news.get('date_publish', ''),
                'keywords': self.extract_keywords(f"{title} {description}")
            })
        
        # Generar intents
        intents = []
        
        # Intent de saludo
        intents.append({
            "tag": "saludo",
            "patterns": [
                "hola",
                "buenos días",
                "buenas tardes",
                "buenas noches",
                "saludos",
                "qué tal",
                "cómo estás",
                "hey"
            ],
            "responses": [
                "¡Hola! Soy tu asistente de noticias. ¿En qué puedo ayudarte?",
                "¡Buenos días! ¿Qué noticias te interesan hoy?",
                "¡Hola! Estoy aquí para ayudarte con las últimas noticias.",
                "¡Saludos! ¿Sobre qué tema quieres conocer las noticias?"
            ]
        })
        
        # Intent de despedida
        intents.append({
            "tag": "despedida",
            "patterns": [
                "adiós",
                "nos vemos",
                "hasta luego",
                "chao",
                "gracias",
                "bye",
                "hasta pronto"
            ],
            "responses": [
                "¡Hasta luego! Que tengas un buen día.",
                "¡Nos vemos! Vuelve cuando quieras más noticias.",
                "¡Adiós! Estaré aquí cuando necesites información.",
                "¡Hasta pronto! Cuídate mucho."
            ]
        })
        
        # Intents por categoría
        for category, news_list in categories.items():
            if len(news_list) < 5:  # Solo crear intent si hay suficientes noticias
                continue
                
            # Patrones para esta categoría
            patterns = [
                f"noticias de {category}",
                f"qué pasa en {category}",
                f"últimas noticias de {category}",
                f"información sobre {category}",
                f"cuéntame de {category}",
                f"novedades en {category}"
            ]
            
            # Añadir patrones específicos basados en keywords
            keywords = set()
            for news in news_list[:20]:  # Solo primeras 20 para no saturar
                keywords.update(news['keywords'])
            
            for keyword in list(keywords)[:10]:  # Máximo 10 keywords por categoría
                patterns.extend([
                    f"noticias sobre {keyword}",
                    f"qué hay de {keyword}",
                    f"información de {keyword}"
                ])
            
            # Respuestas con noticias reales
            responses = []
            for news in news_list[:5]:  # Top 5 noticias por categoría
                response = f"📰 {news['title']}"
                if news['description']:
                    response += f"\n{news['description'][:150]}..."
                if news['source']:
                    response += f"\n📍 Fuente: {news['source']}"
                responses.append(response)
            
            # Respuestas genéricas para la categoría
            responses.extend([
                f"Aquí tienes las últimas noticias de {category}. ¿Te interesa alguna en particular?",
                f"Estas son las noticias más relevantes de {category} que tengo.",
                f"Te muestro lo más destacado en {category}."
            ])
            
            intents.append({
                "tag": category,
                "patterns": patterns,
                "responses": responses[:10]  # Máximo 10 respuestas por intent
            })
        
        # Intent de búsqueda general
        intents.append({
            "tag": "busqueda_general",
            "patterns": [
                "buscar noticias",
                "qué noticias hay",
                "últimas noticias",
                "noticias de hoy",
                "qué está pasando",
                "noticias recientes",
                "novedades",
                "actualidad"
            ],
            "responses": [
                "¿Sobre qué tema específico te gustaría conocer noticias?",
                "Tengo noticias de varios temas: política, economía, deportes, tecnología, salud. ¿Cuál te interesa?",
                "Puedo ayudarte con noticias de diferentes categorías. ¿Qué tema prefieres?",
                "¿Hay algún tema en particular que te interese?"
            ]
        })
        
        # Intent para cuando no entiende
        intents.append({
            "tag": "no_entiendo",
            "patterns": [],
            "responses": [
                "No estoy seguro de entender. ¿Podrías ser más específico sobre qué noticias buscas?",
                "Disculpa, no entendí bien. Puedo ayudarte con noticias de política, economía, deportes, tecnología y más.",
                "No comprendí tu solicitud. ¿Puedes decirme sobre qué tema quieres noticias?",
                "Lo siento, no entendí. Intenta preguntarme sobre noticias de un tema específico."
            ]
        })
        
        logger.info(f"Generados {len(intents)} intents con {len(news_data)} noticias")
        
        return {
            "intents": intents
        }
    
    def save_intents_to_file(self, intents_data: Dict[str, Any], filename: str = "intents_spanish.json"):
        """Guarda los intents en un archivo JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(intents_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Intents guardados en {filename}")
            return True
        except Exception as e:
            logger.error(f"Error guardando intents: {e}")
            return False
    
    def get_news_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de las noticias en la BD"""
        pipeline = [
            {
                "$group": {
                    "_id": "$category",
                    "count": {"$sum": 1},
                    "sources": {"$addToSet": "$source_domain"}
                }
            },
            {
                "$project": {
                    "category": "$_id",
                    "count": 1,
                    "unique_sources": {"$size": "$sources"}
                }
            }
        ]
        
        stats = list(self.collection.aggregate(pipeline))
        total_news = self.collection.count_documents({})
        
        return {
            "total_news": total_news,
            "categories": stats,
            "total_categories": len(stats)
        }
