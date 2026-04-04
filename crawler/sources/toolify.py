"""Toolify.ai Playwright 爬虫 — AI 工具排行榜

通过反检测 Playwright 提取表格数据，从 __NUXT__ 状态获取工具名称和月访问量。
"""

import logging
from playwright.sync_api import sync_playwright
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)

TOOLIFY_URL = 'https://www.toolify.ai/Best-trending-AI-Tools'

# Playwright 反检测参数
STEAK_ARGS = [
    '--no-sandbox',
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
    '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
]


def _parse_visits(text: str) -> int:
    """从访问量文本解析为整数"""
    import re
    m = re.search(r'([\d.]+)\s*([BBMK])', text)
    if not m:
        return 0
    val = float(m.group(1))
    unit = m.group(2)
    multipliers = {'B': 1_000_000_000, 'M': 1_000_000, 'K': 1_000}
    return int(val * multipliers.get(unit, 1))


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
                browser = p.chromium.launch(args=STEAK_ARGS)
                page = browser.new_page(viewport={'width': 1440, 'height': 900})
                page.goto(TOOLIFY_URL, timeout=15000, wait_until='domcontentloaded')
                page.wait_for_timeout(6000)

                # 向下滚动，加载全部数据
                for _ in range(10):
                    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    page.wait_for_timeout(500)

                # 从表格行提取数据
                raw_results = page.evaluate('''
                    () => {
                        const results = [];
                        document.querySelectorAll('tbody tr').forEach(row => {
                            const firstLink = row.querySelector('a[href*="/tool/"]');
                            if (!firstLink) return;
                            const name = firstLink.innerText.trim();
                            if (!name || name.length < 2) return;

                            // 找包含 B/M/K 的单元格作为访问量
                            let visits = '';
                            row.querySelectorAll('td').forEach(cell => {
                                const text = cell.innerText.trim();
                                if (text && /[\\d.]+[BBMK]/.test(text)) {
                                    visits = text;
                                }
                            });

                            results.push({ name, visits });
                        });
                        return results;
                    }
                ''')
                browser.close()

                if not raw_results:
                    logger.warning('[toolify] 未提取到任何数据（页面可能被阻止）')
                    return []

                for i, entry in enumerate(raw_results[:20], start=1):
                    name = entry.get('name', '')
                    visits_text = entry.get('visits', '')
                    if not name:
                        continue

                    # 用访问量作为热度分（越大越高）
                    raw_score = _parse_visits(visits_text)
                    if raw_score == 0:
                        raw_score = max(0, (20 - i) * 1000000)

                    slug = name.lower().replace(' ', '-').replace('&', '').replace('.', '-').replace('(', '').replace(')', '')
                    tool_url = f'https://www.toolify.ai/tool/{slug}'

                    item = NewsItem(
                        id=f'toolify_{hash(name) % 1000000}',
                        title=f'{name}（{visits_text}/月）',
                        url=tool_url,
                        source='toolify',
                        source_name='Toolify.ai',
                        source_region='INT',
                        raw_score=raw_score,
                        rank=i,
                    )
                    items.append(normalize_item(item))

        except Exception as e:
            logger.warning(f'[toolify] 抓取异常: {type(e).__name__}: {e}')

        return items[:20]
