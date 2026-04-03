"""微博热搜爬虫 — 使用移动端接口

微博热搜实时变化，内容涵盖各领域。
同样不做AI关键词过滤，取全部热搜，保证数据量。
"""

import httpx
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item


class WeiboSource(BaseSource):
    info = SourceInfo(
        source='weibo',
        name='微博热搜',
        region='CN',
        enabled=True,
        interval_seconds=1800,
    )

    async def fetch(self) -> list[NewsItem]:
        items = []

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    'https://weibo.com/ajax/side/hotSearch',
                    headers={
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)',
                        'Referer': 'https://weibo.com/',
                        'Accept': 'application/json',
                    }
                )
                data = resp.json()
                # 取实时热搜（realtime 字段）+ band_list
                realtime = data.get('data', {}).get('realtime', []) or []
                band_list = data.get('data', {}).get('band_list', []) or []
                all_bands = realtime + band_list
        except Exception:
            return []

        # 取全部热搜，不做AI关键词过滤
        for i, entry in enumerate(all_bands[:30], start=1):
            word = entry.get('word', '')
            if not word:
                continue

            raw_score = entry.get('num', 0) or max(0, (30 - i) * 5000)
            item = NewsItem(
                id=f'weibo_{entry.get("realpos", i)}_{hash(word) % 100000}',
                title=word,
                url=f'https://s.weibo.com/weibo?q={word}',
                source='weibo',
                source_name='微博热搜',
                source_region='CN',
                raw_score=raw_score,
                rank=entry.get('realpos', i),
            )
            items.append(normalize_item(item))

        return items
