"""网易新闻 Playwright 爬虫 — news.163.com"""

import httpx
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item
from playwright.sync_api import sync_playwright


class NeteaseSource(BaseSource):
    info = SourceInfo(
        source='163news',
        name='网易新闻',
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
                page.goto('https://news.163.com/', timeout=15000, wait_until='networkidle')
                page.wait_for_timeout(3000)

                raw_results = page.evaluate('''
                    () => {
                        const results = [];
                        const seen = new Set();
                        document.querySelectorAll('a').forEach(a => {
                            const href = a.href;
                            const text = a.innerText.trim();
                            // 匹配网易文章详情页
                            if (href && (
                                href.includes('/article/') ||
                                href.includes('dy.163.com') ||
                                href.match(/news\\.163\\.com\\/\\d/)
                            ) && !seen.has(href)) {
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
                        id=f'163news_{i}_{hash(result["title"]) % 100000}',
                        title=result['title'],
                        url=result.get('url') or 'https://news.163.com/',
                        source='163news',
                        source_name='网易新闻',
                        source_region='CN',
                        raw_score=100 - i,
                        rank=i,
                    )
                    items.append(normalize_item(item))
        except Exception:
            pass

        return items[:30]
