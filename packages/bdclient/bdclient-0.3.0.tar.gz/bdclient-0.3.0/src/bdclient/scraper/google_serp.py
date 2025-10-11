from datetime import datetime as dt

from pydantic import BaseModel

from bdclient.scraper.base import CollectScraper

DATASET_ID = "gd_mfz5x93lmsjjjylob"


class Organic(BaseModel):
    url: str
    rank: int
    link: str
    title: str


class General(BaseModel):
    search_engine: str | None
    language: str | None
    location: str | None
    search_type: str | None
    page_title: str | None
    datetime: dt | None
    query: str | None


class Related(BaseModel):
    rank: int | None
    link: str | None
    text: str | None


class Pagination(BaseModel):
    page: str
    link: str


class Result(BaseModel):
    url: str
    keyword: str
    general: General
    related: list[Related]
    pagination: list[Pagination]
    organic: list[Organic]
    people_also_ask: list[str]
    language: str | None
    country: str | None


class CollectByURLQuery(BaseModel):
    url: str = "https://www.google.com/"
    keyword: str
    language: str = "en"
    country: str = "US"
    uule: str = ""
    start_page: int = 1
    end_page: int = 1


class CollectByURL(CollectScraper[CollectByURLQuery, Result]):
    dataset_id = DATASET_ID
    query_model = CollectByURLQuery
    result_model = Result
