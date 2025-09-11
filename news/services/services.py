# news/services/services.py
from datetime import datetime
from typing import List, Optional
from django.conf import settings
import time

from .scraping import NewsScraper
from news.services.content_extractor import fetch_maintext_and_authors
from news import repository

# --- Sentiment (VADER) ---
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from langdetect import detect, LangDetectException

_analyzer = SentimentIntensityAnalyzer()

# Ajuste mínimo para español: añadimos algunas palabras comunes
_spanish_boost = {
    "bueno": 2.0, "excelente": 3.0, "genial": 2.5, "positivo": 1.8,
    "malo": -2.0, "terrible": -3.0, "negativo": -1.8, "horrible": -3.0,
    "feliz": 2.2, "triste": -2.2, "peor": -2.5, "mejor": 2.0,
    "ganó": 1.8, "victoria": 1.8, "derrota": -1.8, "crisis": -1.8,
}
_analyzer.lexicon.update(_spanish_boost)


# -----------------------------
# Helpers
# -----------------------------
def _detect_lang(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return "en"


def _sentiment_for(text: str) -> dict:
    if not text:
        return {"label": "NEUTRAL", "score": 0.0, "compound": 0.0, "lang": None}

    lang = _detect_lang(text[:1000])
    scores = _analyzer.polarity_scores(text[:1000])

    c = scores.get("compound", 0.0)
    if c >= 0.05:
        label = "POSITIVE"
        score = c
    elif c <= -0.05:
        label = "NEGATIVE"
        score = -c
    else:
        label = "NEUTRAL"
        score = abs(c)

    return {
        "label": label,
        "score": round(float(score), 3),
        "compound": round(float(c), 3),
        "lang": lang,
    }


def enrich_articles_content(articles: List[dict], sleep_between: float = 0.5) -> List[dict]:
    """
    Completa maintext + authors para artículos que no lo tengan.
    """
    out = []
    for a in articles:
        if (a.get("maintext") and len(a["maintext"]) > 200) and a.get("authors"):
            out.append(a)
            continue

        url = a.get("url") or ""
        if url.startswith("http"):
            try:
                maintext, authors = fetch_maintext_and_authors(url)
                if maintext and len(maintext) >= 200:
                    a["maintext"] = maintext
                if authors:
                    a["authors"] = authors
            except Exception:
                pass
            time.sleep(sleep_between)  # no saturar
        out.append(a)
    return out


# -----------------------------
# Orquestación
# -----------------------------
def scrape_news(query: str, start_date: datetime, end_date: datetime,
                domains: Optional[list] = None, max_articles: int = 25):
    if domains is None:
        domains = getattr(settings, "NEWS_SOURCES", [])
    scraper = NewsScraper(domains, max_articles=max_articles)
    return scraper.scrape(query, start_date, end_date)


def add_sentiment_analysis(articles: list):
    for article in articles:
        text = article.get("maintext") or article.get("description") or article.get("title")
        article["sentiment"] = _sentiment_for(text)
    return articles


def get_news_with_sentiment(query: str, start_date: datetime, end_date: datetime,
                            domains: Optional[list] = None, max_articles: int = 25):
    # 1. Scrape
    articles = scrape_news(query, start_date, end_date, domains, max_articles)
    # 2. Enriquecer con cuerpo + autores
    articles = enrich_articles_content(articles, sleep_between=0.4)
    # 3. Analizar sentimiento
    return add_sentiment_analysis(articles)


def save_scraped_news(news_list: List[dict]):
    repository.ensure_indexes()
    try:
        return repository.insert_many_news(news_list)
    except Exception:
        # Si tienes índice único en url, duplicados se ignoran aquí
        return []


# -----------------------------
# Queries desde API
# -----------------------------
def fetch_news(category, source=None, start_date=None, end_date=None, limit=20):
    return repository.get_news(category, source, start_date, end_date, limit)


def fetch_random_news(limit=20, category: Optional[str] = None):
    return repository.get_random_news(limit=limit, category=category)


def get_all_sources():
    return repository.get_unique_sources()
