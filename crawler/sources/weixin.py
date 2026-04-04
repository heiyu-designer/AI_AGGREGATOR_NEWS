"""微信热文爬虫 — 搜狗微信搜索 (weixin.sogou.com)"""

import logging
import httpx
from bs4 import BeautifulSoup
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)


class WeixinSource(BaseSource):
    info = SourceInfo(
        source='weixin',
        name='微信热文',
        region='CN',
        enabled=True,
        interval_seconds=1800,
    )

    def fetch(self) -> list[NewsItem]:
        items = []
        try:
            resp = httpx.get(
                'https://weixin.sogou.com/weixin?type=2&s_from=input&query=AI+OR+人工智能&ie=utf8&_sug_=n&_sug_type_=',
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Referer': 'https://weixin.sogou.com/',
                },
                timeout=8,
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            # 搜狗微信文章结构
            for entry in soup.find_all('div', class_='txt-box') or soup.find_all('li'):
                title_el = entry.find('h3') or entry.find('a')
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                if len(title) < 5:
                    continue
                url_el = entry.find('a')
                url = url_el['href'] if url_el and url_el.get('href') else ''
                if url.startswith('/'):
                    url = 'https://weixin.sogou.com' + url
                items.append(normalize_item(NewsItem(
                    id=f'weixin_{len(items)}_{hash(title) % 100000}',
                    title=title,
                    url=url,
                    source='weixin',
                    source_name='微信热文',
                    source_region='CN',
                    raw_score=100 - len(items),
                    rank=len(items) + 1,
                )))

            # 如果没找到结构化数据，尝试通用方式
            if not items:
                for a in soup.find_all('a', href=True):
                    title = a.get_text(strip=True)
                    href = a['href']
                    if len(title) < 5 or title in [i.title for i in items]:
                        continue
                    if href.startswith('/'):
                        href = 'https://weixin.sogou.com' + href
                    items.append(normalize_item(NewsItem(
                        id=f'weixin_{len(items)}_{hash(title) % 100000}',
                        title=title,
                        url=href,
                        source='weixin',
                        source_name='微信热文',
                        source_region='CN',
                        raw_score=100 - len(items),
                        rank=len(items) + 1,
                    )))
        except Exception as e:
            logger.warning(f'[weixin] 抓取异常: {type(e).__name__}: {e}')

        return items[:30]
