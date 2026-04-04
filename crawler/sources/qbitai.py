"""量子位 RSS 爬虫 — qbitai.com"""

import logging
import httpx
import feedparser
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)


class QbitaiSource(BaseSource):
    info = SourceInfo(
        source='qbitai',
        name='量子位',
        region='CN',
        enabled=True,
        interval_seconds=1800,
    )

    def fetch(self) -> list[NewsItem]:
        items = []
        try:
            resp = httpx.get(
                'https://www.qbitai.com/feed',
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=8,
            )
            if resp.status_code != 200:
                logger.warning(f'[qbitai] HTTP {resp.status_code}')
                return []

            feed = feedparser.parse(resp.text)
            raw_entries = feed.entries or []
        except Exception as e:
            logger.warning(f'[qbitai] 抓取异常: {type(e).__name__}: {e}')
            return []

        for i, entry in enumerate(raw_entries[:30], start=1):
            title = entry.get('title', '').strip()
            link = entry.get('link', '')
            if not title or not link:
                continue

            item = NewsItem(
                id=f'qbitai_{hash(link) % 1000000}',
                title=title,
                url=link,
                source='qbitai',
                source_name='量子位',
                source_region='CN',
                raw_score=max(0, (30 - i) * 1000),
                rank=i,
            )
            items.append(normalize_item(item))

        return items
