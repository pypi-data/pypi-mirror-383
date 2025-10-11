from datetime import datetime

from pydantic import BaseModel

from bdclient.scraper.base import DiscoveryScraper

DATASET_ID = "gd_lk56epmy2i5g7lzu0k"


class DiscoverByKeywordQuery(BaseModel):
    keyword: str
    num_of_posts: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    country: str | None = None


class Result(BaseModel):
    url: str
    title: str
    youtuber: str
    youtuber_md5: str
    video_url: str
    video_length: float
    likes: int
    views: int
    date_posted: datetime
    description: str


class DiscoverByKeyword(DiscoveryScraper[DiscoverByKeywordQuery, Result]):
    dataset_id = DATASET_ID
    discover_by = "keyword"
    query_model = DiscoverByKeywordQuery
    result_model = Result
