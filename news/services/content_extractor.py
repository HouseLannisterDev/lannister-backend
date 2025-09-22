# news/services/content_extractor.py
from __future__ import annotations
import re
from typing import List, Tuple, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from django.conf import settings

__all__ = ["fetch_maintext_and_authors", "is_probably_index_page"]

# UA básicos (puedes sobreescribir vía settings.NEWS_USER_AGENTS)
_FALLBACK_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

_INDEX_HINTS = re.compile(r"/(tag|tags|etiqueta|categoria|category|seccion|section)(/|$)", re.I)

def _headers() -> dict:
    uas = getattr(settings, "NEWS_USER_AGENTS", None)
    if isinstance(uas, str):
        uas = [u.strip() for u in uas.split(",") if u.strip()]
    ua = (uas or _FALLBACK_UAS)[0]
    return {"User-Agent": ua, "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"}

def is_probably_index_page(url: str, title: str = "") -> bool:
    if not url:
        return True
    p = urlparse(url)
    path = (p.path or "").lower()
    if _INDEX_HINTS.search(path):
        return True
    if title.lower().startswith(("etiqueta:", "tag:", "categoría:", "categoria:")):
        return True
    return False

def _meta(soup: BeautifulSoup, *names) -> Optional[str]:
    for n in names:
        tag = soup.find("meta", attrs={"name": n}) or soup.find("meta", attrs={"property": n})
        if tag and tag.get("content"):
            return tag["content"].strip()
    return None

def _collect_authors(soup: BeautifulSoup) -> List[str]:
    # 1) metas típicas
    candidates = [
        "author", "article:author", "article:author_name",
        "parsely-author", "og:article:author", "dcterms.creator",
        "byl", "byline",
    ]
    got = _meta(soup, *candidates)
    if got:
        parts = re.split(r",| y | and ", got)
        return [p.strip() for p in parts if p.strip()]
    # 2) selectores frecuentes
    sel = [
        '[itemprop="author"]',
        ".author, .byline, .Byline-bylineName, .c-article-author__name",
        "a[rel=author]",
    ]
    for s in sel:
        found = soup.select(s)
        names = [f.get_text(" ", strip=True) for f in found if f.get_text(strip=True)]
        if names:
            return names
    return []

def _collect_main(soup: BeautifulSoup) -> str:
    # 1) dentro de <article>
    art = soup.find("article")
    if art:
        ps = art.find_all(["p", "h2", "li"])
        text = "\n".join(p.get_text(" ", strip=True) for p in ps if p.get_text(strip=True))
        if len(text) > 300:
            return text
    # 2) bloques comunes
    blocks = soup.select(
        ".article__body, .entry-content, .post-content, .c-article-body, .content-body, .story-body, .gnt_ar_b"
    )
    for b in blocks:
        ps = b.find_all(["p", "h2", "li"])
        text = "\n".join(p.get_text(" ", strip=True) for p in ps if p.get_text(strip=True))
        if len(text) > 300:
            return text
    # 3) fallback: todos los <p> (quitando navegación)
    for bad in soup.select("nav, header, footer, script, style, noscript, aside"):
        bad.extract()
    ps = soup.find_all("p")
    text = "\n".join(p.get_text(" ", strip=True) for p in ps if p.get_text(strip=True))
    return text

def fetch_maintext_and_authors(url: str, title: Optional[str] = None) -> Tuple[str, List[str]]:
    """
    Devuelve (maintext, authors). Sin dependencias pesadas (no lxml/readability).
    """
    if is_probably_index_page(url, title or ""):
        return "", []
    try:
        resp = requests.get(url, headers=_headers(), timeout=25)
        resp.raise_for_status()
    except requests.RequestException:
        return "", []
    soup = BeautifulSoup(resp.text, "html.parser")
    # si la URL final parece índice/sección, descartamos
    if is_probably_index_page(resp.url, (soup.title.string if soup.title else "") or ""):
        return "", []
    authors = _collect_authors(soup)
    maintext = _collect_main(soup)
    # limpieza básica
    maintext = re.sub(r"\n{3,}", "\n\n", maintext).strip()
    return maintext, authors
