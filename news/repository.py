# news/repository.py
from datetime import datetime
from typing import List, Optional
from pymongo import ASCENDING
from pymongo.errors import BulkWriteError
from mongo_client import get_mongo_client  # usa el helper de la raíz

# Conexión
db = get_mongo_client()
collection = db["news"]
metadata_collection = db["scraping_metadata"]

def ensure_indexes():
    """
    Crea índices útiles para consultas rápidas.
    url es única para evitar duplicados de la misma noticia.
    """
    collection.create_index([("date_publish", ASCENDING)])
    collection.create_index([("source_domain", ASCENDING)])
    collection.create_index([("category", ASCENDING)])
    collection.create_index("url", unique=True)   # <- deduplicación
    metadata_collection.create_index("key", unique=True)

def insert_many_news(news_list: List[dict]):
    """
    Inserta varias noticias en Mongo.
    - Normaliza date_publish (str ISO → datetime).
    - Se asegura que scraped_at exista.
    - Ignora duplicados por url (BulkWriteError con code 11000).
    """
    for item in news_list:
        # Normalizar date_publish
        iso = item.get("date_publish")
        if isinstance(iso, str):
            try:
                item["date_publish"] = datetime.fromisoformat(
                    iso.replace("Z", "+00:00")
                )
            except Exception:
                # Si ya es válido o None, lo dejamos
                pass

        # Asegurar scraped_at
        if not item.get("scraped_at"):
            item["scraped_at"] = datetime.utcnow()

    if not news_list:
        return []

    try:
        # ordered=False → inserta todo lo que pueda, ignora duplicados
        return collection.insert_many(news_list, ordered=False).inserted_ids
    except BulkWriteError as e:
        # Ignorar duplicados (error code 11000)
        inserted = e.details.get("nInserted", 0)
        return [None] * inserted

def get_news(
    category: Optional[str] = None,
    source: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 20,
):
    """
    Devuelve noticias filtradas por categoría, fuente y rango de fechas.
    Ordenadas por fecha descendente.
    """
    q = {}
    if category:
        q["category"] = category
    if source:
        q["source_domain"] = source
    if start_date and end_date:
        q["date_publish"] = {"$gte": start_date, "$lte": end_date}
    return list(collection.find(q).sort("date_publish", -1).limit(int(limit)))

def get_random_news(limit: int = 20, category: Optional[str] = None):
    """
    Devuelve noticias aleatorias, opcionalmente filtradas por categoría.
    """
    pipeline = []
    if category:
        pipeline.append({"$match": {"category": category}})
    pipeline.append({"$sample": {"size": int(limit)}})
    return list(collection.aggregate(pipeline))

def get_unique_sources():
    """
    Devuelve lista de dominios únicos de origen.
    """
    return collection.distinct("source_domain")

def get_metadata(key: str):
    """
    Devuelve el valor de una metadata por key.
    """
    rec = metadata_collection.find_one({"key": key})
    return rec["value"] if rec else None

def set_metadata(key: str, value):
    """
    Actualiza o inserta metadata con clave/valor.
    """
    metadata_collection.update_one(
        {"key": key},
        {"$set": {"value": value, "updated_at": datetime.utcnow()}},
        upsert=True
    )
