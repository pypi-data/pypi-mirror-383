from datetime import datetime

from pydantic import BaseModel

from bdclient.scraper.base import CollectScraper

DATASET_ID = "gd_lnsxoxzi1omrwnka5r"


class Result(BaseModel):
    url: str
    title: str | None
    publisher: str
    date: datetime
    category: str | None
    keyword: str
    country: str | None
    image: str | None


class CollectByURLQuery(BaseModel):
    url: str = "https://news.google.com/"
    keyword: str
    country: str = "US"
    language: str = "en"


class CollectByURL(CollectScraper[CollectByURLQuery, Result]):
    dataset_id = DATASET_ID
    query_model = CollectByURLQuery
    result_model = Result
