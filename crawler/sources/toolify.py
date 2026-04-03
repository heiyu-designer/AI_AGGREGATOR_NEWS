"""Toolify.ai Playwright 爬虫 — AI 工具排行榜"""

from playwright.sync_api import sync_playwright
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item


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
                page.goto('https://www.toolify.ai/Best-trending-AI-Tools', timeout=15000, wait_until='networkidle')
                page.wait_for_timeout(3000)

                # 滚动加载更多内容
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                page.wait_for_timeout(2000)

                raw_results = page.evaluate('''
                    () => {
                        const results = [];
                        const seen = new Set();
                        document.querySelectorAll('a').forEach(a => {
                            const href = a.href;
                            const text = a.innerText.trim();
                            // 匹配 AI 工具详情页（通常是外部链接如 xxx.ai, xxx.com）
                            // 排除导航链接
                            if (href && !seen.has(href)
                                && !href.includes('/login') && !href.includes('/signup')
                                && !href.includes('toolify.ai') || href.match(/toolify\\.ai\\/\\w+\\?utm/)) {
                                if (href.includes('.ai') || href.includes('.io') || href.includes('.com')
                                    || (href.includes('toolify.ai') && !href.match(/toolify\\.ai\\/$/))) {
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
        except Exception:
            pass

        return items[:20]
