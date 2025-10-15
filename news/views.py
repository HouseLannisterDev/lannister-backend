# news/views.py
from __future__ import annotations
from django.http import JsonResponse
from datetime import datetime, timedelta
from typing import Optional, Tuple
from bson import ObjectId

from .services.services import (
    fetch_news,
    fetch_random_news,
    get_all_sources,
)

# ---------------------------
# Helpers
# ---------------------------

def _stringify_ids(docs: list[dict]) -> list[dict]:
    for d in docs:
        _id = d.get("_id")
        if isinstance(_id, ObjectId):
            d["_id"] = str(_id)
        # Normaliza datetime → ISO string legible (opcional)
        dp = d.get("date_publish")
        if isinstance(dp, datetime):
            d["date_publish"] = dp.isoformat()
        sa = d.get("scraped_at")
        if isinstance(sa, datetime):
            d["scraped_at"] = sa.isoformat()
    return docs

def _parse_date(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    # Acepta YYYY-MM-DD o ISO-8601
    try:
        if len(s) == 10:
            return datetime.strptime(s, "%Y-%m-%d")
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None

def _default_range_if_missing(start_dt: Optional[datetime], end_dt: Optional[datetime]) -> Tuple[datetime, datetime]:
    """
    Si no mandan rango, por defecto mostramos noticias del ÚLTIMO AÑO,
    para alinearnos al mismo rango que usa tu scraper.
    """
    if start_dt and end_dt:
        return start_dt, end_dt
    now = datetime.utcnow()
    return now - timedelta(days=365), now

# ---------------------------
# Views
# ---------------------------

def get_news_view(request):
    """
    GET /news/?q=<categoria>&source=<dominio>&limit=50&start=YYYY-MM-DD&end=YYYY-MM-DD
    - q: categoría (Deportes, Judiciales, Moda, Tecnología, Animales)
    - source: filtra por dominio de origen
    - start/end: rango de fechas (si no envías, NO se aplica filtro de fecha)
    - limit: cantidad a devolver (default 50)
    """
    category = request.GET.get("q")
    source = request.GET.get("source")
    limit = int(request.GET.get("limit", 50))

    start = _parse_date(request.GET.get("start"))
    end = _parse_date(request.GET.get("end"))
    
    # Solo aplicar filtro de fecha si ambos parámetros están presentes
    start_dt = start
    end_dt = end
    if start and not end:
        # Si solo hay start, usar start hasta ahora
        end_dt = datetime.utcnow()
    elif end and not start:
        # Si solo hay end, usar desde hace un año hasta end
        start_dt = end - timedelta(days=365)

    docs = fetch_news(category, source, start_dt, end_dt, limit)
    return JsonResponse(
        _stringify_ids(docs),
        safe=False,
        json_dumps_params={"ensure_ascii": False, "indent": 2},
    )

def get_sources_view(request):
    """
    GET /news/sources/
    Devuelve lista de dominios únicos presentes en la colección.
    """
    sources = get_all_sources()
    return JsonResponse(
        {"sources": sources},
        json_dumps_params={"ensure_ascii": False, "indent": 2},
    )

def get_random_view(request):
    """
    GET /news/random/?limit=20&category=<categoria>
    Entrega noticias aleatorias (útil para sesiones no persistentes).
    """
    category = request.GET.get("category")
    limit = int(request.GET.get("limit", 20))
    docs = fetch_random_news(limit, category)
    return JsonResponse(
        _stringify_ids(docs),
        safe=False,
        json_dumps_params={"ensure_ascii": False, "indent": 2},
    )

def get_section_view(request, section: str):
    """
    GET /news/section/<slug>/?limit=40
    Slugs soportados: deportes|judiciales|moda|tecnologia|animales
    Mapea a tus categorías normalizadas.
    """
    mapping = {
        "deportes": "Deportes",
        "judiciales": "Judiciales",
        "moda": "Moda",
        "tecnologia": "Tecnología",
        "animales": "Animales",
    }
    category = mapping.get(section.lower(), section)
    limit = int(request.GET.get("limit", 40))

    start_dt, end_dt = _default_range_if_missing(None, None)
    docs = fetch_news(category, None, start_dt, end_dt, limit)
    return JsonResponse(
        _stringify_ids(docs),
        safe=False,
        json_dumps_params={"ensure_ascii": False, "indent": 2},
    )

# ---------------------------
# Bonus: stats para probar rápido
# ---------------------------
def stats_view(request):
    """
    GET /news/stats/
    Métricas simples para verificar funcionamiento.
    """
    from mongo_client import get_mongo_client
    db = get_mongo_client()
    coll = db["news"]

    total = coll.count_documents({})
    sources = coll.distinct("source_domain")
    unique_sources = len([s for s in sources if s])

    # Cap duro que usa tu script
    CAP_DOCS = 10_000
    remaining = max(CAP_DOCS - total, 0)

    # Últimas 24h (útil para ver refresco)
    now = datetime.utcnow()
    last24 = coll.count_documents({
        "scraped_at": {"$gte": now - timedelta(hours=24)}
    })

    data = {
        "total_docs": total,
        "unique_sources": unique_sources,
        "cap_docs": CAP_DOCS,
        "remaining_until_cap": remaining,
        "inserted_last_24h": last24,
    }
    return JsonResponse(data, json_dumps_params={"ensure_ascii": False, "indent": 2})
