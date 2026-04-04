"""百度热搜 PC 端爬虫 — 解析网页中的标题"""

import logging
import re
import httpx
from bs4 import BeautifulSoup
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)


class BaiduSource(BaseSource):
    info = SourceInfo(
        source='baidu',
        name='百度热搜',
        region='CN',
        enabled=True,
        interval_seconds=1800,
    )

    def fetch(self) -> list[NewsItem]:
        items = []
        try:
            r = httpx.get(
                'https://top.baidu.com/board?tab=realtime',
                timeout=8.0,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                }
            )
            soup = BeautifulSoup(r.text, 'html.parser')

            # 查找所有标题元素 class="title_xxx"
            title_els = soup.find_all(class_=re.compile(r'^title_[a-zA-Z0-9]+$'))
            if not title_els:
                # 备用：查找所有含 title class 的元素
                title_els = soup.find_all(class_=re.compile('title'))

            # 查找含热度的父元素
            hot_els = soup.find_all(class_=re.compile('hot.*score|hotScore', re.I))
        except Exception as e:
            logger.warning(f'[baidu] 抓取异常: {type(e).__name__}: {e}')
            return []

        # 提取标题和链接
        for i, el in enumerate(title_els[:30], start=1):
            title = el.get_text(strip=True)
            if not title or len(title) < 5:
                continue

            # 获取链接
            link = ''
            a_tag = el if el.name == 'a' else el.find_parent('a') or el.find('a')
            if a_tag:
                link = a_tag.get('href', '')
            if not link:
                link = f'https://www.baidu.com/s?wd={title}'

            # 热度
            raw_score = 0
            parent = el.find_parent('div')
            if parent:
                score_el = parent.find(class_=re.compile('hot|score', re.I))
                if score_el:
                    try:
                        raw_score = int(re.sub(r'\D', '', score_el.get_text(strip=True))) or 0
                    except Exception:
                        pass

            item = NewsItem(
                id=f'baidu_{i}',
                title=title,
                url=link,
                source='baidu',
                source_name='百度热搜',
                source_region='CN',
                raw_score=raw_score,
                rank=i,
            )
            items.append(normalize_item(item))

        return items
