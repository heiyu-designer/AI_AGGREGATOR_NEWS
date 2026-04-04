"""今日头条 API 爬虫 — news_tech 热榜"""

import logging
import httpx
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)

# 使用科技分类热榜 API，服务器环境可正常访问
TOUTIAO_API = 'https://www.toutiao.com/api/article/feed/?category=news_tech'


class ToutiaoSource(BaseSource):
    info = SourceInfo(
        source='toutiao',
        name='今日头条',
        region='CN',
        enabled=True,
        interval_seconds=1800,
    )

    def fetch(self) -> list[NewsItem]:
        items = []
        try:
            resp = httpx.get(
                TOUTIAO_API,
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=8,
            )
            if resp.status_code != 200:
                logger.warning(f'[toutiao] HTTP {resp.status_code}')
                return []

            data = resp.json()
            articles = data.get('data') or []
        except Exception as e:
            logger.warning(f'[toutiao] 抓取异常: {type(e).__name__}: {e}')
            return []

        for i, article in enumerate(articles[:30], start=1):
            title = article.get('title', '').strip()
            item_id = article.get('item_id', '')
            if not title:
                continue

            # 构造文章 URL：相对路径转绝对路径
            relative = article.get('share_url') or article.get('source_url') or ''
            if relative.startswith('/'):
                url = f'https://www.toutiao.com{relative}'
            elif relative:
                url = relative
            elif item_id:
                url = f'https://www.toutiao.com/group/{item_id}/'
            else:
                url = 'https://www.toutiao.com/'

            item = NewsItem(
                id=f'toutiao_{item_id or i}',
                title=title,
                url=url,
                source='toutiao',
                source_name='今日头条',
                source_region='CN',
                raw_score=max(0, (30 - i) * 1000),
                rank=i,
            )
            items.append(normalize_item(item))

        return items
