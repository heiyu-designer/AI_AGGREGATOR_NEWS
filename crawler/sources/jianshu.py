"""简书爬虫 — 使用 Playwright 爬取 AI 相关文章"""

from playwright.sync_api import sync_playwright
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item


class JianshuSource(BaseSource):
    info = SourceInfo(
        source='jianshu',
        name='简书',
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
                page.goto(
                    'https://www.jianshu.com/search?q=AI&page=1&per_page=30',
                    timeout=20000,
                    wait_until='networkidle',
                )
                page.wait_for_timeout(3000)

                # 从搜索结果中提取文章
                raw_results = page.evaluate('''
                    () => {
                        const results = [];
                        // 简书搜索结果在 .note-list 下的 li 中
                        const notes = document.querySelectorAll('.note-list li');
                        notes.forEach(li => {
                            // 标题在 class="title" 的 a 标签中
                            const titleEl = li.querySelector('.title');
                            // 找包含 /p/ 的链接作为文章 URL
                            const allLinks = li.querySelectorAll('a');
                            let articleUrl = '';
                            for (const a of allLinks) {
                                if (a.href && a.href.includes('/p/')) {
                                    articleUrl = a.href;
                                    break;
                                }
                            }
                            if (titleEl && articleUrl) {
                                const title = titleEl.innerText.trim();
                                if (title.length > 5 && title.length < 200) {
                                    results.push({ title, url: articleUrl });
                                }
                            }
                        });

                        // 备用方案：直接查找所有包含 /p/ 的链接
                        if (results.length === 0) {
                            const links = document.querySelectorAll('a[href*="/p/"]');
                            links.forEach(a => {
                                const title = a.innerText.trim();
                                if (title.length > 10 && title.length < 200) {
                                    results.push({ title, url: a.href });
                                }
                            });
                        }

                        // 去重
                        const seen = new Set();
                        return results.filter(r => {
                            if (seen.has(r.title)) return false;
                            seen.add(r.title);
                            return true;
                        }).slice(0, 30);
                    }
                ''')
                browser.close()

                for i, result in enumerate(raw_results[:30], start=1):
                    if not result.get('title'):
                        continue
                    item = NewsItem(
                        id=f'jianshu_{i}_{hash(result["title"]) % 100000}',
                        title=result['title'],
                        url=result.get('url') or 'https://www.jianshu.com/',
                        source='jianshu',
                        source_name='简书',
                        source_region='CN',
                        raw_score=0,
                        rank=i,
                    )
                    items.append(normalize_item(item))
        except Exception:
            pass

        return items
