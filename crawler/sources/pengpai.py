"""澎湃新闻 Playwright 爬虫"""

import httpx
from bs4 import BeautifulSoup
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item
from playwright.sync_api import sync_playwright


class PengpaiSource(BaseSource):
    info = SourceInfo(
        source='pengpai',
        name='澎湃新闻',
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
                page.goto('https://www.thepaper.cn/', timeout=15000, wait_until='networkidle')
                page.wait_for_timeout(3000)

                # JS 提取新闻标题和详情页链接
                raw_results = page.evaluate('''
                    () => {
                        const results = [];
                        const seen = new Set();
                        // 查找所有文章链接 (包含 /detail/ 或 /content/)
                        const links = document.querySelectorAll('a[href]');
                        links.forEach(a => {
                            const href = a.href;
                            const text = a.innerText.trim();
                            // 匹配文章详情页
                            if ((href.includes('/detail/') || href.match(/thepaper\\.cn\\/\\d/)) && !seen.has(href)) {
                                if (text.length > 5 && text.length < 200) {
                                    seen.add(href);
                                    results.push({ title: text, url: href });
                                }
                            }
                        });

                        // 备用：从新闻卡片元素提取
                        if (results.length === 0) {
                            const cards = document.querySelectorAll('[class*="news"], [class*="article"], [class*="item"]');
                            cards.forEach(card => {
                                const a = card.querySelector('a');
                                const titleEl = card.querySelector('h1, h2, h3, [class*="title"]');
                                if (a && a.href && titleEl) {
                                    const title = titleEl.innerText.trim();
                                    if (title.length > 5 && !seen.has(a.href)) {
                                        seen.add(a.href);
                                        results.push({ title, url: a.href });
                                    }
                                }
                            });
                        }

                        // 再备用：获取页面中所有文本包含"详情"的链接
                        if (results.length < 5) {
                            const allLinks = document.querySelectorAll('a');
                            allLinks.forEach(a => {
                                const href = a.href;
                                const text = a.innerText.trim();
                                if (href && href.includes('thepaper.cn') && !seen.has(href)
                                    && (href.includes('detail') || href.includes('content'))
                                    && text.length > 5 && text.length < 200) {
                                    seen.add(href);
                                    results.push({ title: text, url: href });
                                }
                            });
                        }

                        return results.slice(0, 30);
                    }
                ''')
                browser.close()

                for i, result in enumerate(raw_results[:30], start=1):
                    if not result.get('title'):
                        continue
                    item = NewsItem(
                        id=f'pengpai_{i}_{hash(result["title"]) % 100000}',
                        title=result['title'],
                        url=result.get('url') or 'https://www.thepaper.cn/',
                        source='pengpai',
                        source_name='澎湃新闻',
                        source_region='CN',
                        raw_score=0,
                        rank=i,
                    )
                    items.append(normalize_item(item))
        except Exception:
            pass

        return items
