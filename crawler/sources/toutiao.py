"""今日头条 Playwright 爬虫"""

import logging
from playwright.sync_api import sync_playwright
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)


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
            with sync_playwright() as p:
                browser = p.chromium.launch(args=['--no-sandbox'])
                page = browser.new_page()
                page.goto('https://www.toutiao.com/', timeout=10000, wait_until='domcontentloaded')
                page.wait_for_timeout(2000)

                raw_results = page.evaluate('''
                    () => {
                        const results = [];
                        const seen = new Set();
                        document.querySelectorAll('a').forEach(a => {
                            const href = a.href;
                            const text = a.innerText.trim();
                            if (href && href.includes('toutiao.com') && !seen.has(href)
                                && (href.includes('/article/') || href.match(/toutiao\\.com\\/\\w{16}/))) {
                                if (text.length > 5 && text.length < 150) {
                                    seen.add(href);
                                    results.push({ title: text, url: href });
                                }
                            }
                        });
                        return results.slice(0, 30);
                    }
                ''')
                browser.close()

                for i, result in enumerate(raw_results[:30], start=1):
                    if not result.get('title'):
                        continue
                    item = NewsItem(
                        id=f'toutiao_{i}_{hash(result["title"]) % 100000}',
                        title=result['title'],
                        url=result.get('url') or 'https://www.toutiao.com/',
                        source='toutiao',
                        source_name='今日头条',
                        source_region='CN',
                        raw_score=0,
                        rank=i,
                    )
                    items.append(normalize_item(item))
        except Exception as e:
            logger.warning(f'[toutiao] 抓取异常: {type(e).__name__}: {e}')

        return items
