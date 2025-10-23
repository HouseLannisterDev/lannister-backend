"""
Servicio para buscar noticias en MongoDB según la categoría detectada.
"""
import re
from typing import Dict, List, Optional
from news.repository import get_random_news


class NewsSearchService:
    """Maneja la búsqueda de noticias por categoría desde MongoDB."""
    
    # Mapeo de palabras clave a categorías de MongoDB
    CATEGORY_KEYWORDS = {
        "deportes": ["deporte", "deportivo", "sport", "futbol", "soccer", "basketball", "football"],
        "moda": ["moda", "fashion", "tendencia", "trend", "estilo", "style"],
        "tecnologia": ["tecnologia", "technology", "tech", "digital", "software", "hardware"],
        "animales": ["animal", "mascota", "pet", "fauna", "wildlife"],
        "judiciales": ["judicial", "court", "legal", "tribunal", "caso", "case", "justicia", "justice"]
    }
    
    def __init__(self):
        pass
    
    def extract_category(self, user_question: str, normalized_question: str) -> Optional[str]:
        """
        Extrae la categoría de noticias que el usuario está buscando.
        
        Args:
            user_question: Pregunta original del usuario
            normalized_question: Pregunta normalizada (lematizada)
            
        Returns:
            str: Nombre de la categoría o None si no se detecta
        """
        # Buscar en la pregunta original y normalizada
        text_to_search = f"{user_question.lower()} {normalized_question.lower()}"
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                # Buscar palabra completa con límites de palabra
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_to_search):
                    return category
        
        return None
    
    def search_news(self, category: str, limit: int = 5) -> List[Dict]:
        """
        Busca noticias en MongoDB por categoría.
        
        Args:
            category: Categoría de noticias (deportes, moda, tecnologia, animales, judiciales)
            limit: Número máximo de noticias a retornar
            
        Returns:
            List[Dict]: Lista de noticias encontradas
        """
        try:
            # Capitalizar primera letra para match con MongoDB (ej: "deportes" -> "Deportes")
            category_capitalized = category.capitalize()
            
            # Obtener noticias aleatorias de la categoría
            news_list = get_random_news(limit=limit, category=category_capitalized)
            return news_list
        except Exception as e:
            print(f"❌ Error buscando noticias en MongoDB: {e}")
            return []
    
    def format_news_response(self, news_list: List[Dict], category: str, lang: str = "es") -> str:
        """
        Formatea la lista de noticias en una respuesta legible para el usuario.
        
        Args:
            news_list: Lista de noticias de MongoDB
            category: Categoría de las noticias
            lang: Idioma de la respuesta (es/en)
            
        Returns:
            str: Respuesta formateada con las noticias
        """
        if not news_list:
            if lang == "es":
                return f"Lo siento, no encontré noticias recientes de {category}. Intenta de nuevo más tarde o prueba con otra categoría."
            else:
                return f"Sorry, I couldn't find recent {category} news. Try again later or try another category."
        
        # Construir respuesta
        if lang == "es":
            header = f"📰 Aquí tienes las últimas noticias de **{category.upper()}**:\n\n"
        else:
            header = f"📰 Here are the latest **{category.upper()}** news:\n\n"
        
        formatted_news = []
        for idx, news in enumerate(news_list, 1):
            title = news.get("title", "Sin título" if lang == "es" else "No title")
            url = news.get("url", "#")
            description = news.get("description", "")
            
            # Limitar descripción a 120 caracteres
            if description and len(description) > 120:
                description = description[:120] + "..."
            
            news_item = f"**{idx}. {title}**"
            if description:
                news_item += f"\n   {description}"
            news_item += f"\n   🔗 [Leer más]({url})"
            
            formatted_news.append(news_item)
        
        response = header + "\n\n".join(formatted_news)
        
        # Agregar footer
        if lang == "es":
            response += "\n\n💬 ¿Quieres ver noticias de otra categoría? (deportes, moda, tecnología, animales, judiciales)"
        else:
            response += "\n\n💬 Want to see news from another category? (sports, fashion, technology, animals, judicial)"
        
        return response
