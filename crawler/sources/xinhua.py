"""新华社 Playwright 爬虫 — xinhuanet.com"""

import logging
from playwright.sync_api import sync_playwright
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)


class XinhuaSource(BaseSource):
    info = SourceInfo(
        source='xinhua',
        name='新华社',
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
                page.goto('https://www.xinhuanet.com/', timeout=10000, wait_until='domcontentloaded')
                page.wait_for_timeout(2000)

                raw_results = page.evaluate('''
                    () => {
                        const results = [];
                        const seen = new Set();
                        document.querySelectorAll('a').forEach(a => {
                            const href = a.href;
                            const text = a.innerText.trim();
                            // 匹配新华社文章详情页
                            if (href && href.includes('xinhuanet.com') && !seen.has(href)
                                && !href.includes('/finance/') && !href.includes('/energy/')
                                && (href.includes('/news') || href.match(/xinhuanet\\.com\\/\\d{8}/) || href.match(/xinhuanet\\.com\\/.{2,}\\/\\d/))) {
                                if (text.length > 5 && text.length < 100) {
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
                        id=f'xinhua_{i}_{hash(result["title"]) % 100000}',
                        title=result['title'],
                        url=result.get('url') or 'https://www.xinhuanet.com/',
                        source='xinhua',
                        source_name='新华社',
                        source_region='CN',
                        raw_score=100 - i,
                        rank=i,
                    )
                    items.append(normalize_item(item))
        except Exception as e:
            logger.warning(f'[xinhua] 抓取异常: {type(e).__name__}: {e}')

        return items[:30]
