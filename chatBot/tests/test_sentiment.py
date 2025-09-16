#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lannister_news_api.settings')
django.setup()

from mongo_client import get_mongo_client

def test_sentiment_query():
    print("Probando consultas de sentimiento...")
    
    try:
        client = get_mongo_client()
        news_collection = client["news"]
        
        # Ver estructura de una noticia con sentimiento
        sample = news_collection.find_one({"sentiment": {"$exists": True}})
        if sample:
            print("\n=== ESTRUCTURA DE DATOS ===")
            print(f"Título: {sample.get('title', 'N/A')}")
            print(f"Sentimiento: {sample.get('sentiment', 'N/A')}")
            print(f"Categoría: {sample.get('category', 'N/A')}")
        
        # Contar noticias por sentimiento
        print("\n=== CONTEO POR SENTIMIENTO ===")
        for sentiment in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
            count = news_collection.count_documents({"sentiment.label": sentiment})
            print(f"Noticias {sentiment}: {count}")
        
        # Buscar noticias negativas específicamente
        print("\n=== MUESTRA DE NOTICIAS NEGATIVAS ===")
        negative_news = list(news_collection.find(
            {"sentiment.label": "NEGATIVE"}, 
            {"title": 1, "sentiment": 1}
        ).limit(3))
        
        for i, news in enumerate(negative_news, 1):
            print(f"{i}. {news.get('title', 'Sin título')} - Sentimiento: {news.get('sentiment', {})}")
        
        # Buscar noticias positivas específicamente
        print("\n=== MUESTRA DE NOTICIAS POSITIVAS ===")
        positive_news = list(news_collection.find(
            {"sentiment.label": "POSITIVE"}, 
            {"title": 1, "sentiment": 1}
        ).limit(3))
        
        for i, news in enumerate(positive_news, 1):
            print(f"{i}. {news.get('title', 'Sin título')} - Sentimiento: {news.get('sentiment', {})}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_sentiment_query()
