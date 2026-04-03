"""知乎热榜爬虫 — 使用非官方 API

知乎是科技类问答平台，热榜内容大多与科技/互联网/AI相关，
不做严格AI关键词过滤，取全部热搜。
"""

import httpx
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item


class ZhihuSource(BaseSource):
    info = SourceInfo(
        source='zhihu',
        name='知乎',
        region='CN',
        enabled=True,
        interval_seconds=1800,
    )

    async def fetch(self) -> list[NewsItem]:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    'https://api.zhihu.com/topstory/hot-lists/total',
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'Accept': 'application/json',
                    }
                )
                data = resp.json()
        except Exception:
            return []

        items = []
        raw_items = data.get('data', []) or []

        # 取全部热搜（知乎热榜内容偏科技/互联网，不做关键词过滤）
        for i, entry in enumerate(raw_items[:30], start=1):
            target = entry.get('target', {})
            title = target.get('title', '')
            if not title:
                continue

            raw_id = target.get('id', entry.get('id', i))
            # 知乎热榜 API 返回的 target.id 即为问题 URL 的 ID
            # 格式: https://www.zhihu.com/question/{id}（与 tophub.today 一致）
            item = NewsItem(
                id=f'zhihu_{raw_id}',
                title=title,
                url=f'https://www.zhihu.com/question/{raw_id}',
                source='zhihu',
                source_name='知乎',
                source_region='CN',
                raw_score=max(0, (30 - i) * 1000),
                rank=i,
            )
            items.append(normalize_item(item))

        return items
