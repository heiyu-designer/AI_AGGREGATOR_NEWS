"""Hugging Face Blog Playwright 爬虫 — huggingface.co/blog

通过 Playwright 提取博客文章标题和链接。服务器环境需能访问 huggingface.co。
"""

import logging
from playwright.sync_api import sync_playwright
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)

HF_BLOG_URL = 'https://huggingface.co/blog'

STEAK_ARGS = [
    '--no-sandbox',
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
]


class HuggingfaceSource(BaseSource):
    info = SourceInfo(
        source='huggingface',
        name='Hugging Face',
        region='INT',
        enabled=True,
        interval_seconds=3600,
    )

    def fetch(self) -> list[NewsItem]:
        items = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(args=STEAK_ARGS)
                page = browser.new_page(viewport={'width': 1440, 'height': 900})
                page.goto(HF_BLOG_URL, timeout=15000, wait_until='domcontentloaded')
                page.wait_for_timeout(5000)

                raw_results = page.evaluate('''
                    () => {
                        const seen = new Set();
                        const results = [];
                        // 找文章卡片中的链接
                        document.querySelectorAll("article a[href*='/blog/']").forEach(a => {
                            const title = a.innerText.trim();
                            const url = a.href;
                            if (title && title.length > 10 && !seen.has(url)) {
                                seen.add(url);
                                results.push({ title, url });
                            }
                        });
                        // 备用：找所有 /blog/ 链接
                        if (results.length < 5) {
                            document.querySelectorAll("a[href*='/blog/']").forEach(a => {
                                const title = a.innerText.trim();
                                const url = a.href;
                                if (title && title.length > 15 && !seen.has(url)) {
                                    seen.add(url);
                                    results.push({ title, url });
                                }
                            });
                        }
                        return results.slice(0, 20);
                    }
                ''')
                browser.close()

                if not raw_results:
                    logger.warning('[huggingface] 未提取到任何数据')
                    return []

                for i, entry in enumerate(raw_results, start=1):
                    title = entry.get('title', '').strip()
                    url = entry.get('url', '')
                    if not title or not url:
                        continue

                    item = NewsItem(
                        id=f'huggingface_{i}',
                        title=title,
                        url=url,
                        source='huggingface',
                        source_name='Hugging Face',
                        source_region='INT',
                        raw_score=max(0, (20 - i) * 1000),
                        rank=i,
                    )
                    items.append(normalize_item(item))

        except Exception as e:
            logger.warning(f'[huggingface] 抓取异常: {type(e).__name__}: {e}')

        return items[:20]
