"""36氪 RSS 爬虫 — 使用官方 RSS Feed"""

import logging
import httpx
import feedparser
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)


class Kr36Source(BaseSource):
    info = SourceInfo(
        source='36kr',
        name='36氪',
        region='CN',
        enabled=True,
        interval_seconds=1800,
    )

    def fetch(self) -> list[NewsItem]:
        items = []
        try:
            r = httpx.get(
                'https://36kr.com/feed',
                timeout=8.0,
                headers={'User-Agent': 'Mozilla/5.0'},
            )
            feed = feedparser.parse(r.text)
            raw_items = feed.entries or []
        except Exception as e:
            logger.warning(f'[36kr] 抓取异常: {type(e).__name__}: {e}')
            return []

        for i, entry in enumerate(raw_items[:30], start=1):
            title = entry.get('title', '')
            if not title:
                continue

            link = entry.get('link', '')
            item = NewsItem(
                id=f'36kr_{entry.get("id", i)}',
                title=title,
                url=link or 'https://36kr.com/',
                source='36kr',
                source_name='36氪',
                source_region='CN',
                raw_score=0,
                rank=i,
            )
            items.append(normalize_item(item))

        return items
