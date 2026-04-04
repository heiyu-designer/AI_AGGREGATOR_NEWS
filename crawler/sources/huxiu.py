"""虎嗅网 Playwright 爬虫 — m.huxiu.com（移动版）

通过 Playwright + iPhone UA 绕过 WAF 验证，从移动版首页提取文章标题和链接。
"""

import logging
from playwright.sync_api import sync_playwright
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)

HUXIU_URL = 'https://m.huxiu.com/'

STEAK_ARGS = [
    '--no-sandbox',
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
]



class HuxiuSource(BaseSource):
    info = SourceInfo(
        source='huxiu',
        name='虎嗅网',
        region='CN',
        enabled=True,
        interval_seconds=1800,
    )

    def fetch(self) -> list[NewsItem]:
        items = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(args=STEAK_ARGS)
                page = browser.new_page(
                    viewport={'width': 390, 'height': 844},
                    device_scale_factor=2,
                )
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                })
                page.goto(HUXIU_URL, timeout=15000, wait_until='domcontentloaded')
                page.wait_for_timeout(5000)

                raw_results = page.evaluate('''
                    () => {
                        const seen = new Set();
                        const results = [];
                        // 找 h2 标签（包含干净标题），再找其父级 a 链接
                        document.querySelectorAll("h2").forEach(el => {
                            const t = el.innerText.trim();
                            const parentA = el.closest ? el.closest("a") : null;
                            const url = parentA ? parentA.href : null;
                            if (t && t.length > 5 && url && url.includes("/article/") && !seen.has(t)) {
                                seen.add(t);
                                results.push({ title: t, url: url });
                            }
                        });
                        return results.slice(0, 30);
                    }
                ''')
                browser.close()

                if not raw_results:
                    logger.warning('[huxiu] 未提取到任何数据（可能被 WAF 拦截）')
                    return []

                for i, entry in enumerate(raw_results, start=1):
                    title = entry.get('title', '').strip()
                    url = entry.get('url', '')
                    if not title or not url:
                        continue

                    item = NewsItem(
                        id=f'huxiu_{i}',
                        title=title,
                        url=url,
                        source='huxiu',
                        source_name='虎嗅网',
                        source_region='CN',
                        raw_score=max(0, (30 - i) * 1000),
                        rank=i,
                    )
                    items.append(normalize_item(item))

        except Exception as e:
            logger.warning(f'[huxiu] 抓取异常: {type(e).__name__}: {e}')

        return items[:30]
