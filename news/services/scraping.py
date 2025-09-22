# news/services/scraping.py
from typing import List, Dict, Optional, Tuple
from urllib.parse import quote, urlparse, parse_qs, quote_plus
from math import ceil
from datetime import datetime, timedelta, timezone

import random
import time
import requests
import feedparser
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from django.conf import settings

from news.serializers import NewsDoc
from news.services.content_extractor import fetch_maintext_and_authors


def _env_list(name: str) -> list:
    raw = getattr(settings, name, [])
    if isinstance(raw, str):
        return [s.strip() for s in raw.split(",") if s.strip()]
    return list(raw)


class NewsScraper:
    BASE_URL = "https://www.google.com/search"

    DEFAULT_UAS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    ]

    SELECTORS = {
        "title": "div.n0jPhd",
        "url": "a.WlydOe",
        "description": "div.GI74Re",
        "date": "div.rbYSKb",
        "source": "div.NUnG9d",
    }

    def __init__(self, domains: Optional[list] = None, max_articles: int = 50, max_retries: int = None):
        self.domains = domains or getattr(settings, "NEWS_SOURCES", [])
        self.article_per_pages = 100
        self.max_pages = ceil(max_articles / self.article_per_pages)
        self.max_articles = max_articles

        # .env / settings
        self.user_agents = _env_list("NEWS_USER_AGENTS") or self.DEFAULT_UAS
        self.proxies_pool = _env_list("NEWS_PROXIES")  # puede ser []
        self.delay_min = float(getattr(settings, "NEWS_REQ_DELAY_MIN", 3))
        self.delay_max = float(getattr(settings, "NEWS_REQ_DELAY_MAX", 8))
        self.max_retries = int(max_retries or getattr(settings, "NEWS_MAX_RETRIES", 3))

    # -----------------------
    # Utilidades generales
    # -----------------------
    def _headers(self):
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        }

    def _pick_proxy(self) -> Optional[dict]:
        if not self.proxies_pool:
            return None
        p = random.choice(self.proxies_pool)
        return {"http": p, "https": p}

    def _sleep(self, base: float = 0.0):
        time.sleep(base + random.uniform(self.delay_min, self.delay_max))

    def _clean_url(self, url: Optional[str]) -> Optional[str]:
        if url and url.startswith("/url?"):
            qs = parse_qs(urlparse(url).query)
            return qs.get("q", [url])[0]
        return url

    def _txt(self, el):
        return el.get_text().strip() if el else None

    def _to_iso_utc(self, ymd: Optional[str]) -> Optional[str]:
        if not ymd:
            return None
        try:
            dt = datetime.strptime(ymd, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except Exception:
            return ymd

    def parse_date(self, s: Optional[str]) -> Optional[str]:
        if not s:
            return None
        s = s.lower().strip()
        today = datetime.today()
        try:
            if any(k in s for k in ("hour", "minute", "second")):
                return today.strftime("%Y-%m-%d")
            if "day" in s:
                return (today - timedelta(days=int(s.split()[0]))).strftime("%Y-%m-%d")
            if "week" in s:
                return (today - timedelta(weeks=int(s.split()[0]))).strftime("%Y-%m-%d")
            if "month" in s:
                return (today - relativedelta(months=int(s.split()[0]))).strftime("%Y-%m-%d")
            if "year" in s:
                return (today - relativedelta(years=int(s.split()[0]))).strftime("%Y-%m-%d")
            for fmt in ("%Y-%m-%d", "%d %b %Y", "%d %B %Y"):
                try:
                    return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    pass
        except Exception:
            pass
        return None

    # -----------------------
    # Google News (HTML)
    # -----------------------
    def construct_url(self, query: str, start_date: datetime, end_date: datetime, page: int = 0) -> str:
        date_filter = f"cdr:1,cd_min:{start_date.strftime('%m/%d/%Y')},cd_max:{end_date.strftime('%m/%d/%Y')}"
        domain_q = " OR ".join([f"site:{d}" for d in self.domains]) if self.domains else ""
        full_q = f"{query} {domain_q}".strip()
        params = {
            "q": quote(full_q),
            "tbm": "nws",
            "tbs": date_filter,
            "start": page * self.article_per_pages,
            "hl": "es",
            "lr": "lang_es",
            "num": str(self.article_per_pages),
        }
        return f"{self.BASE_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

    def extract(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        out = []
        for box in soup.find_all("div", class_="SoaBEf"):
            title = self._txt(box.select_one(self.SELECTORS["title"]))
            url = self._clean_url((box.select_one(self.SELECTORS["url"]) or {}).get("href"))
            desc = self._txt(box.select_one(self.SELECTORS["description"]))
            date_day = self.parse_date(self._txt(box.select_one(self.SELECTORS["date"])))
            source = self._txt(box.select_one(self.SELECTORS["source"]))
            if url:
                out.append(
                    {
                        "title": title or "",
                        "url": url,
                        "description": desc or "",
                        "date_publish": self._to_iso_utc(date_day),
                        "source_domain": source or "",
                    }
                )
        return out

    # -----------------------
    # Google News (RSS) - Fallback
    # -----------------------
    def _rss_url(self, query: str, hl: str = "es-419", gl: str = "CO", ceid: str = "CO:es") -> str:
        q = query
        if self.domains:
            sites = " OR ".join([f"site:{d}" for d in self.domains])
            q = f"{query} {sites}"
        return f"https://news.google.com/rss/search?q={quote_plus(q)}&hl={hl}&gl={gl}&ceid={ceid}"

    def _within_range(self, dt: Optional[datetime], start_date: datetime, end_date: datetime) -> bool:
        if not dt:
            return True
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return start_date.replace(tzinfo=timezone.utc) <= dt <= end_date.replace(tzinfo=timezone.utc)

    def scrape_rss(self, query: str, start_date: datetime, end_date: datetime, max_items: int = 100) -> List[Dict]:
        url = self._rss_url(query)
        feed = feedparser.parse(url)
        out: List[Dict] = []

        for e in feed.entries[: max_items * 3]:  # leemos más por el filtrado
            title = e.get("title") or ""
            description_html = e.get("summary") or ""
            description = _clean_rss_description(description_html)

            original_url = _pick_original_url(e) or ""
            source = (e.get("source") or {}).get("title") if isinstance(e.get("source"), dict) else None

            # fecha
            dt = None
            if getattr(e, "published_parsed", None):
                dt = datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
            elif getattr(e, "updated_parsed", None):
                dt = datetime(*e.updated_parsed[:6], tzinfo=timezone.utc)

            if not self._within_range(dt, start_date, end_date):
                continue
            date_iso = dt.isoformat() if dt else None

            # Saltar páginas índice/tag/categoría
            if _is_probably_index(original_url, title):
                continue

            # ---- EXTRAER maintext + authors del artículo original ----
            maintext, authors = ("", [])
            if original_url.startswith("http"):
                try:
                    maintext, authors = fetch_maintext_and_authors(original_url, title=title)
                except Exception:
                    pass  # tolerante

            try:
                n = NewsDoc(
                    title=title,
                    url=original_url or (e.get("link") or ""),
                    source_domain=source or "",
                    date_publish=date_iso,
                    description=description,
                    maintext=maintext,
                    authors=authors,
                    category=query,
                    sentiment=None,
                )
                out.append(n.model_dump())
            except Exception:
                out.append({
                    "title": title,
                    "url": original_url or (e.get("link") or ""),
                    "source_domain": source or "",
                    "date_publish": date_iso,
                    "description": description,
                    "maintext": maintext,
                    "authors": authors,
                    "category": query,
                    "sentiment": None,
                })

            if len(out) >= max_items:
                break

        return out[:max_items]

    # -----------------------
    # Orquestación principal
    # -----------------------
    def scrape(self, query: str, start_date: datetime, end_date: datetime):
        items: List[Dict] = []

        # 1) Intento HTML (tbm=nws)
        for page in range(self.max_pages):
            if len(items) >= self.max_articles:
                break

            url = self.construct_url(query, start_date, end_date, page)
            retries = 0
            while retries < self.max_retries:
                try:
                    resp = requests.get(
                        url,
                        headers=self._headers(),
                        proxies=self._pick_proxy(),
                        timeout=30,
                    )
                    status = resp.status_code
                    if status in (429, 500, 502, 503, 504):
                        retries += 1
                        self._sleep(base=2 ** retries * 0.5)
                        continue

                    resp.raise_for_status()

                    txt = resp.text
                    if "Our systems have detected unusual traffic" in txt or "To continue, please verify" in txt:
                        retries += 1
                        self._sleep(base=2 ** retries * 0.5)
                        continue

                    raw = self.extract(txt)
                    if not raw:
                        self._sleep()
                        break

                    for rdoc in raw:
                        doc = NewsDoc(
                            title=rdoc["title"],
                            url=rdoc["url"],
                            source_domain=rdoc["source_domain"],
                            date_publish=rdoc["date_publish"],
                            description=rdoc["description"],
                            maintext="",
                            authors=[],
                            category=query,
                            sentiment=None,
                        )
                        items.append(doc.model_dump())

                    self._sleep()
                    break

                except requests.RequestException:
                    retries += 1
                    self._sleep(base=2 ** retries * 0.5)

        # 2) Fallback RSS si HTML no devolvió nada
        if not items:
            items = self.scrape_rss(query, start_date, end_date, max_items=self.max_articles)

        return items[: self.max_articles]


# -----------------------
# Helpers RSS/Google News
# -----------------------
def _clean_rss_description(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")  # evita lxml
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    # quita anchors, deja texto
    for a in soup.find_all("a"):
        a.unwrap()
    text = soup.get_text(" ", strip=True)
    return text


def _resolve_original_from_link(link: str) -> Optional[str]:
    try:
        parsed = urlparse(link or "")
        # si ya es medio original
        if "news.google.com" not in (parsed.netloc or ""):
            return link
        qs = parse_qs(parsed.query or "")
        if "url" in qs and qs["url"]:
            return qs["url"][0]
    except Exception:
        pass
    return None


def _resolve_original_from_summary(summary_html: str) -> Optional[str]:
    if not summary_html:
        return None
    soup = BeautifulSoup(summary_html, "html.parser")  # evita lxml
    anchors = soup.find_all("a", href=True)
    if anchors:
        return anchors[-1]["href"]
    return None


def _pick_original_url(entry) -> Optional[str]:
    link = entry.get("link") or ""
    return _resolve_original_from_link(link) or _resolve_original_from_summary(entry.get("summary") or "") or link


# detector de páginas índice (mismo criterio que el extractor)
import re
_INDEX_HINTS = re.compile(r"/(tag|tags|etiqueta|categoria|category|seccion|section)(/|$)", re.I)

def _is_probably_index(url: str, title: str = "") -> bool:
    if not url:
        return True
    p = urlparse(url)
    path = (p.path or "").lower()
    if _INDEX_HINTS.search(path):
        return True
    if title.lower().startswith(("etiqueta:", "tag:", "categoría:", "categoria:")):
        return True
    return False
