
from pydantic import BaseModel, AnyUrl, Field
from typing import Optional
from datetime import datetime

class Book(BaseModel):
    url: AnyUrl
    title: str
    description: Optional[str]
    category: Optional[str]
    price_including_tax: Optional[float]
    price_excluding_tax: Optional[float]
    availability: Optional[str]
    num_reviews: Optional[int]
    image_url: Optional[AnyUrl]
    rating: Optional[int]
    crawl_timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_url: AnyUrl
    status: str = "ok"
    raw_html: Optional[str]
    fingerprint: Optional[str]
