"""半月谈爬虫 — 通过 Google News RSS 提取 banyuetan.org 内容

banyuetan.org.cn 官网在海外服务器上返回 502，改用 Google News RSS 代理。
只保留来自 banyuetan.org 的真实文章，过滤第三方引用。
"""

import logging
import httpx
import feedparser
import urllib.parse
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)

BANYUETAN_GOOGLE_RSS = (
    'https://news.google.com/rss/search?'
    'q=%E5%8D%8A%E6%9C%88%E8%B0%88&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'
)


class BanyuetanSource(BaseSource):
    info = SourceInfo(
        source='banyuetan',
        name='半月谈',
        region='CN',
        enabled=True,
        interval_seconds=1800,
    )

    def fetch(self) -> list[NewsItem]:
        items = []
        try:
            resp = httpx.get(
                BANYUETAN_GOOGLE_RSS,
                timeout=8,
                verify=False,
                headers={'User-Agent': 'Mozilla/5.0'},
            )
            if resp.status_code != 200:
                logger.warning(f'[banyuetan] HTTP {resp.status_code}')
                return []

            feed = feedparser.parse(resp.text)
            raw_entries = feed.entries or []
        except Exception as e:
            logger.warning(f'[banyuetan] 抓取异常: {type(e).__name__}: {e}')
            return []

        for i, entry in enumerate(raw_entries[:50], start=1):
            title = entry.get('title', '').strip()
            link = entry.get('link', '')
            if not title or not link:
                continue

            # Google News RSS 格式：标题末尾含 " - 来源域名"
            # 只保留来自 banyuetan.org 的真实文章
            if title.endswith(' - banyuetan.org'):
                title = title[:-len(' - banyuetan.org')].strip()
            elif ' - banyuetan.org' not in title:
                # 不是来自 banyuetan.org 的文章，跳过
                continue

            item = NewsItem(
                id=f'banyuetan_{hash(link) % 1000000}',
                title=title,
                url=link,
                source='banyuetan',
                source_name='半月谈',
                source_region='CN',
                raw_score=max(0, (50 - i) * 1000),
                rank=i,
            )
            items.append(normalize_item(item))

        return items[:30]
