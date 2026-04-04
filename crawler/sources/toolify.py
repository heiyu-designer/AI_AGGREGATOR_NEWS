"""Toolify.ai Playwright 爬虫 — AI 工具排行榜"""

import logging
from playwright.sync_api import sync_playwright
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)


class ToolifySource(BaseSource):
    info = SourceInfo(
        source='toolify',
        name='Toolify.ai',
        region='INT',
        enabled=True,
        interval_seconds=3600,
    )

    def fetch(self) -> list[NewsItem]:
        items = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(args=['--no-sandbox'])
                page = browser.new_page()
                page.goto('https://www.toolify.ai/Best-trending-AI-Tools', timeout=10000, wait_until='domcontentloaded')
                page.wait_for_timeout(2000)

                # 滚动加载更多内容
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                page.wait_for_timeout(1500)

                raw_results = page.evaluate('''
                    () => {
                        const results = [];
                        const seen = new Set();
                        document.querySelectorAll('a').forEach(a => {
                            const href = a.href || '';
                            const text = (a.innerText || '').trim();
                            if (!href || seen.has(href)) return;
                            if (href.includes('/login') || href.includes('/signup')) return;
                            const isUtm = href.includes('toolify.ai') && href.includes('utm');
                            const isAi = href.includes('.ai') || href.includes('.io') || href.includes('.com');
                            const isToolify = href.includes('toolify.ai') && !href.endsWith('toolify.ai/');
                            if ((!href.includes('toolify.ai') || isUtm) && (isAi || isToolify)) {
                                if (text.length >= 2 && text.length <= 60) {
                                    seen.add(href);
                                    results.push({ title: text, url: href });
                                }
                            }
                        });
                        return results.slice(0, 30);
                    }
                ''')
                browser.close()

                for i, result in enumerate(raw_results[:20], start=1):
                    if not result.get('title'):
                        continue
                    item = NewsItem(
                        id=f'toolify_{i}_{hash(result["title"]) % 100000}',
                        title=result['title'],
                        url=result.get('url') or 'https://www.toolify.ai/',
                        source='toolify',
                        source_name='Toolify.ai',
                        source_region='INT',
                        raw_score=100 - i,
                        rank=i,
                    )
                    items.append(normalize_item(item))
        except Exception as e:
            logger.warning(f'[toolify] 抓取异常: {type(e).__name__}: {e}')

        return items[:20]
