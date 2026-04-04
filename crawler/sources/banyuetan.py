"""半月谈爬虫 — banyuetan.cn"""

import logging
import httpx
import re
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)


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
                'http://www.banyuetan.org.cn/',
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml',
                },
                timeout=8,
            )
            resp.raise_for_status()
            text = resp.text

            links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]{5,100})</a>', text)
            seen_titles = set()
            for url, title in links:
                title = title.strip()
                if len(title) < 5 or title in seen_titles:
                    continue
                if any(kw in title for kw in ['登录', '注册', 'RSS', '关于', '邮箱', 'APP']):
                    continue
                seen_titles.add(title)
                if url.startswith('/'):
                    url = 'http://www.banyuetan.org.cn' + url
                items.append(normalize_item(NewsItem(
                    id=f'banyuetan_{len(items)}_{hash(title) % 100000}',
                    title=title,
                    url=url,
                    source='banyuetan',
                    source_name='半月谈',
                    source_region='CN',
                    raw_score=100 - len(items),
                    rank=len(items) + 1,
                )))
        except Exception as e:
            logger.warning(f'[banyuetan] 抓取异常: {type(e).__name__}: {e}')

        return items[:30]
