"""Hacker News 爬虫 — 使用官方 Firebase API"""

import asyncio
import logging
import httpx
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)


# 放宽的 AI 相关关键词（覆盖更多技术讨论）
AI_KEYWORDS_HN = [
    'AI', 'machine learning', 'deep learning', 'GPT', 'language model',
    'OpenAI', 'Anthropic', 'neural', 'LLM', 'transformer', 'diffusion',
    'agent', 'prompt', 'RAG', 'hugging face', 'stable diffusion',
    'arxiv', 'paper', 'research', 'algorithm', 'model',
    'data science', 'data engineer', 'python', 'programming',
    'startup', 'YC', 'tech', 'cloud', 'kubernetes', 'docker',
    'database', 'backend', 'frontend', 'devops', 'API',
    'GitHub', 'open source', 'software',
]


class HackerNewsSource(BaseSource):
    info = SourceInfo(
        source='hackernews',
        name='Hacker News',
        region='INT',
        enabled=True,
        interval_seconds=1800,
    )

    async def _fetch_top_ids(self, client: httpx.AsyncClient) -> list[int]:
        resp = await client.get(
            'https://hacker-news.firebaseio.com/v0/topstories.json',
            timeout=5.0,
        )
        # 扩大抓取范围，从前 50 改为 100
        return resp.json()[:100]

    async def _fetch_item(self, client: httpx.AsyncClient, item_id: int) -> dict:
        resp = await client.get(
            f'https://hacker-news.firebaseio.com/v0/item/{item_id}.json',
            timeout=5.0,
        )
        return resp.json() or {}

    async def fetch(self) -> list[NewsItem]:
        items = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                top_ids = await self._fetch_top_ids(client)
                # 并发抓取更多条目
                tasks = [self._fetch_item(client, id_) for id_ in top_ids]
                results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.warning(f'[hackernews] 抓取异常: {type(e).__name__}: {e}')
            return []

        for i, result in enumerate(results, start=1):
            if isinstance(result, Exception):
                continue
            if not isinstance(result, dict):
                continue

            title = result.get('title', '')
            if not title:
                continue

            # 放宽关键词匹配
            title_lower = title.lower()
            if not any(kw.lower() in title_lower for kw in AI_KEYWORDS_HN):
                continue

            score = result.get('score', 0) or 0
            item = NewsItem(
                id=f'hackernews_{result.get("id", i)}',
                title=title,
                url=result.get('url') or f'https://news.ycombinator.com/item?id={result.get("id")}',
                source='hackernews',
                source_name='Hacker News',
                source_region='INT',
                raw_score=score,
                rank=i,
            )
            items.append(normalize_item(item))

        return items
