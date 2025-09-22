# news/serializers.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class NewsDoc(BaseModel):
    title: str
    description: Optional[str] = ""          #  string vacío
    maintext: Optional[str] = ""             # idem
    authors: List[str] = []                  # lista vacía por defecto

    category: str

    # ISO 8601 con timezone
    date_publish: Optional[str] = None

    source_domain: Optional[str] = ""
    url: str

    # {"positive": 0.xx, "neutral": 0.xx, "negative": 0.xx}
    sentiment: Optional[Dict[str, float]] = None

    scraped_at: datetime = Field(default_factory=datetime.now)

    class Config:
        str_strip_whitespace = True
        validate_default = True
        populate_by_name = True
