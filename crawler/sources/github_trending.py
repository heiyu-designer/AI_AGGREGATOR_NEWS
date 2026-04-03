"""GitHub Trending AI 项目爬虫 — 使用 GitHub Search API"""

import httpx
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item


class GitHubTrendingSource(BaseSource):
    info = SourceInfo(
        source='github',
        name='GitHub Trending',
        region='INT',
        enabled=True,
        interval_seconds=3600,
    )

    async def fetch(self) -> list[NewsItem]:
        items = []

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    'https://api.github.com/search/repositories',
                    params={
                        'q': 'AI language:python',
                        'sort': 'stars',
                        'order': 'desc',
                        'per_page': 15,
                    },
                    headers={
                        'User-Agent': 'Mozilla/5.0',
                        'Accept': 'application/vnd.github.v3+json',
                    }
                )
                data = resp.json()
                raw_items = data.get('items', []) or []
        except Exception:
            return []

        for i, entry in enumerate(raw_items[:15], start=1):
            stars = entry.get('stargazers_count', 0) or 0
            item = NewsItem(
                id=f'github_{entry.get("id", i)}',
                title=f"{entry.get('full_name', '')} — {entry.get('description', '') or '无描述'}",
                url=entry.get('html_url', 'https://github.com'),
                source='github',
                source_name='GitHub Trending',
                source_region='INT',
                raw_score=stars,
                rank=i,
            )
            items.append(normalize_item(item))

        return items
