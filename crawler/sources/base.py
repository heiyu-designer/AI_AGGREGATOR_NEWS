"""数据源基类，所有爬虫模块必须继承此基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class SourceInfo:
    source: str
    name: str
    region: str  # 'CN' | 'INT'
    enabled: bool = True
    interval_seconds: int = 1800  # 默认 30 分钟


@dataclass
class NewsItem:
    id: str
    title: str
    url: str
    source: str
    source_name: str
    source_region: str
    hot_score: int = 0
    raw_score: Optional[int] = None
    rank: Optional[int] = None
    published_at: Optional[str] = None
    image_url: Optional[str] = None
    tags: list[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class BaseSource(ABC):
    """爬虫数据源基类"""

    info: SourceInfo

    @abstractmethod
    async def fetch(self) -> list[NewsItem]:
        """抓取数据，返回新闻列表"""
        pass

    def normalize(self, item: NewsItem) -> NewsItem:
        """数据标准化钩子，可被子类重写"""
        return item
