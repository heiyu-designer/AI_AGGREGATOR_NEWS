"""少数派 RSS 爬虫 — 使用官方 RSS Feed"""

import logging
import httpx
import feedparser
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)


class ShaoshupaiSource(BaseSource):
    info = SourceInfo(
        source='sspai',
        name='少数派',
        region='CN',
        enabled=True,
        interval_seconds=1800,
    )

    def fetch(self) -> list[NewsItem]:
        items = []
        try:
            r = httpx.get(
                'https://sspai.com/feed',
                timeout=8.0,
                headers={'User-Agent': 'Mozilla/5.0'},
            )
            feed = feedparser.parse(r.text)
            raw_items = feed.entries or []
        except Exception as e:
            logger.warning(f'[sspai] 抓取异常: {type(e).__name__}: {e}')
            return []

        for i, entry in enumerate(raw_items[:30], start=1):
            title = entry.get('title', '')
            if not title:
                continue

            link = entry.get('link', '')
            item = NewsItem(
                id=f'sspai_{entry.get("id", i)}',
                title=title,
                url=link or 'https://sspai.com',
                source='sspai',
                source_name='少数派',
                source_region='CN',
                raw_score=0,
                rank=i,
            )
            items.append(normalize_item(item))

        return items
