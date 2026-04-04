"""IT之家 RSS 爬虫 — ithome.com"""

import logging
import httpx
import feedparser
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)


class IthomeSource(BaseSource):
    info = SourceInfo(
        source='ithome',
        name='IT之家',
        region='CN',
        enabled=True,
        interval_seconds=1800,
    )

    def fetch(self) -> list[NewsItem]:
        items = []
        try:
            resp = httpx.get(
                'https://www.ithome.com/feed',
                timeout=8,
                headers={'User-Agent': 'Mozilla/5.0'},
            )
            if resp.status_code != 200:
                logger.warning(f'[ithome] HTTP {resp.status_code}')
                return []

            feed = feedparser.parse(resp.text)
            raw_entries = feed.entries or []
        except Exception as e:
            logger.warning(f'[ithome] 抓取异常: {type(e).__name__}: {e}')
            return []

        for i, entry in enumerate(raw_entries[:30], start=1):
            title = entry.get('title', '').strip()
            link = entry.get('link', '')
            if not title or not link:
                continue

            item = NewsItem(
                id=f'ithome_{hash(link) % 1000000}',
                title=title,
                url=link,
                source='ithome',
                source_name='IT之家',
                source_region='CN',
                raw_score=max(0, (30 - i) * 1000),
                rank=i,
            )
            items.append(normalize_item(item))

        return items
