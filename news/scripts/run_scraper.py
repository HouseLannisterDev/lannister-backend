# news/scripts/run_scraper.py
import os, sys, time
from datetime import datetime, timedelta   # <--- necesario

from pathlib import Path

# --- Asegurar que el proyecto esté en sys.path ---
# /lannister-backend/news/scripts/run_scraper.py
# Project root = two levels arriba
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# --- Nombre exacto del paquete settings del proyecto ---
# Si tu carpeta del proyecto se llama diferente, cámbialo aquí:
DJANGO_SETTINGS = "lannister_news_api.settings"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS)

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa
from mongo_client import get_mongo_client  # noqa
from news import repository  # noqa
from news.services.services import get_news_with_sentiment, save_scraped_news  # noqa

# ========================
# Config
# ========================
CATEGORIES = ["Deportes", "Judiciales", "Moda", "Tecnología", "Animales"]

CAP_DOCS = 10_000                     # tope duro de la colección
MAX_ARTICLES_PER_CATEGORY = 200       # pedido por ejecución/categoría (se recorta por CAP)
MAX_RETRIES = 2                       # reintentos si no llegan artículos
SLEEP_BETWEEN_CATEGORIES_SEC = 2      # pausa pequeña entre categorías

# Ventana: ÚLTIMO AÑO
WINDOW_DAYS = 365                     # <-- clave: 1 año


# ========================
# Helpers
# ========================
def _coll():
    return get_mongo_client()["news"]

def current_count() -> int:
    return _coll().count_documents({})

def cap_remaining() -> int:
    return max(CAP_DOCS - current_count(), 0)

def log(msg: str):
    ts = datetime.utcnow().isoformat(timespec="seconds")
    print(f"[{ts}] {msg}")


# ========================
# Main
# ========================
def main():
    repository.ensure_indexes()

    remaining = cap_remaining()
    if remaining <= 0:
        log(f"CAP {CAP_DOCS} alcanzado. Nada que hacer.")
        return

    now = datetime.utcnow()
    start = now - timedelta(days=WINDOW_DAYS)
    end = now

    log(f"Ventana de scraping: {start.date()} -> {end.date()} (último año)")
    log(f"Restantes hacia CAP: {remaining}")

    total_inserted = 0
    domains = getattr(settings, "NEWS_SOURCES", [])

    for category in CATEGORIES:
        if cap_remaining() <= 0:
            log("CAP alcanzado durante la ejecución. Deteniendo…")
            break

        log(f"==> Categoría: {category}")
        retries = 0
        batch = []

        while retries <= MAX_RETRIES and not batch:
            batch_target = min(MAX_ARTICLES_PER_CATEGORY, cap_remaining())
            if batch_target <= 0:
                break

            batch = get_news_with_sentiment(
                query=category,
                start_date=start,
                end_date=end,
                domains=domains,
                max_articles=batch_target
            )

            if not batch:
                retries += 1
                if retries <= MAX_RETRIES:
                    log(f"Sin artículos. Reintento {retries}/{MAX_RETRIES}")
                    time.sleep(5)

        if not batch:
            log(f"Categoría {category}: sin artículos tras {MAX_RETRIES} reintentos.")
            continue

        # Recortar si nos pasamos del CAP restante
        remaining = cap_remaining()
        if len(batch) > remaining:
            batch = batch[:remaining]

        inserted_ids = save_scraped_news(batch)
        inserted = len(inserted_ids)
        total_inserted += inserted

        log(f"Guardados {inserted} artículos de {category} | Restante hacia CAP: {cap_remaining()}")
        time.sleep(SLEEP_BETWEEN_CATEGORIES_SEC)

    log(f"Total insertados en esta corrida: {total_inserted}")
    log("Done.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Interrumpido por el usuario.")
        sys.exit(1)
