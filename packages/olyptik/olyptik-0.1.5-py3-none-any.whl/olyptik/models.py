from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar


class CrawlStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    TIMED_OUT = "timed_out"
    FAILED = "failed"
    ABORTED = "aborted"
    ERROR = "error"


class EngineType(str, Enum):
    PLAYWRIGHT = "playwright"
    CHEERIO = "cheerio"
    AUTO = "auto"


@dataclass
class StartCrawlPayload:
    startUrl: str
    maxResults: Optional[int] = None
    maxDepth: Optional[int] = None
    includeLinks: Optional[bool] = None
    useSitemap: Optional[bool] = None
    entireWebsite: Optional[bool] = None
    excludeNonMainTags: Optional[bool] = None
    deduplicateContent: Optional[bool] = None
    extraction: Optional[str] = None
    timeout: Optional[int] = None
    engineType: Optional[EngineType] = None
    useStaticIps: Optional[bool] = None


@dataclass
class QueryCrawlsPayload:
    page: int = 0
    status: Optional[List[CrawlStatus]] = None
    startUrls: Optional[List[str]] = None


@dataclass
class CrawlResult:
    crawlId: str
    url: str
    title: str
    markdown: str
    teamId: Optional[str] = None
    depthOfUrl: Optional[int] = None
    createdAt: Optional[str] = None
    anonymousUserId: Optional[str] = None
    isSuccess: Optional[bool] = None
    error: Optional[str] = None
    isDeleted: Optional[bool] = None


@dataclass
class Crawl:
    id: str
    status: CrawlStatus
    startUrls: List[str]
    includeLinks: bool
    maxDepth: int
    maxResults: int
    teamId: str
    createdAt: str
    durationInSeconds: int
    numberOfResults: int
    useSitemap: bool
    entireWebsite: bool
    excludeNonMainTags: bool
    timeout: int
    useStaticIps: bool
    engineType: EngineType
    completedAt: Optional[str] = None
    projectId: Optional[str] = None
    deduplicateContent: Optional[bool] = None
    extraction: Optional[str] = None


T = TypeVar("T")


@dataclass
class PaginationResult(Generic[T]):
    results: List[T]
    page: int
    limit: int
    totalPages: int
    totalResults: int


def _from_dict(model_cls, data: Dict[str, Any]):
    return model_cls(**data)


