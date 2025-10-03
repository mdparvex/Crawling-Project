
from pydantic import BaseModel, AnyUrl, Field
from typing import Optional
from datetime import datetime


class Book(BaseModel):
    crawl_timestamp: datetime = Field(default_factory=lambda: datetime.now(__import__('datetime').timezone.utc))
    status: str = "ok"
    source_url: AnyUrl
    title: str
    description: Optional[str]
    category: Optional[str]
    price_including_tax: Optional[float]
    price_excluding_tax: Optional[float]
    availability: Optional[str]
    num_reviews: Optional[int]
    image_url: Optional[AnyUrl]
    rating: Optional[int]
