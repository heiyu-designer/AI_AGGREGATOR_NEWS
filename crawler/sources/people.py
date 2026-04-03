"""人民网爬虫 — people.com.cn"""

import httpx
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item


class PeopleSource(BaseSource):
    info = SourceInfo(
        source='people',
        name='人民网',
        region='CN',
        enabled=True,
        interval_seconds=1800,
    )

    def fetch(self) -> list[NewsItem]:
        items = []
        try:
            resp = httpx.get(
                'http://www.people.com.cn/',
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml',
                },
                timeout=15,
            )
            resp.raise_for_status()
            text = resp.text

            # 从首页提取新闻链接和标题
            import re
            # 匹配 <a href="...">标题</a> 模式
            links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]{5,80})</a>', text)
            seen_titles = set()
            for url, title in links:
                title = title.strip()
                if len(title) < 5 or title in seen_titles:
                    continue
                if any(kw in title for kw in ['登录', '注册', '关于', '邮箱', 'RSS', '收藏']):
                    continue
                seen_titles.add(title)
                # 补全相对路径
                if url.startswith('/'):
                    url = 'http://www.people.com.cn' + url
                items.append(normalize_item(NewsItem(
                    id=f'people_{len(items)}_{hash(title) % 100000}',
                    title=title,
                    url=url,
                    source='people',
                    source_name='人民网',
                    source_region='CN',
                    raw_score=100 - len(items),
                    rank=len(items) + 1,
                )))
        except Exception:
            pass

        return items[:30]
