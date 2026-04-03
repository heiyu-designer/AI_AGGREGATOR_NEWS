"""YouTube 爬虫 — 混合方案：RSS + 直接 HTML 解析"""

import httpx
import re
import feedparser
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item


# 在中国大陆可用的 AI 相关 YouTube 频道
AI_CHANNELS = [
    ('3Blue1Brown', 'UCWN3xxRkmTPmbKwht9FuE5A'),
    ('DeepMind', 'UCMiJRAwDNSNzuYeN2uWa0pA'),
    ('Siraj Raval', 'UCWN3xxRkmTPmbKwht9FuE5A'),
    ('StatQuest', 'UCtYLUTtgS3kCtFgFY7-vhlQ'),
    ('Yannic Kilcher', 'UCXUPKJOwMGNxqk4LSdLLYqA'),
    ('MIT OpenCourseWare', 'UCDapq3k2VDKaV9wU1X_LPmg'),
]


class YouTubeSource(BaseSource):
    info = SourceInfo(
        source='youtube',
        name='YouTube',
        region='INT',
        enabled=True,
        interval_seconds=1800,
    )

    def fetch(self) -> list[NewsItem]:
        items = []
        seen_titles = set()

        # 方案1：RSS feeds（对大陆访问较稳定的频道）
        for name, channel_id in AI_CHANNELS:
            try:
                resp = httpx.get(
                    f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}',
                    headers={'User-Agent': 'Mozilla/5.0'},
                    timeout=8,
                )
                if resp.status_code != 200:
                    continue
                feed = feedparser.parse(resp.text)
                for entry in feed.entries[:10]:
                    title = entry.get('title', '')
                    if title and title not in seen_titles and len(title) > 3:
                        seen_titles.add(title)
                        vid = ''
                        for link in entry.get('links', []):
                            if link.get('href', '').endswith('youtube.com/watch?v=' + entry.get('yt_videoid', '')):
                                vid = entry.get('yt_videoid', '')
                                break
                        if not vid:
                            vid = entry.get('yt_videoid', str(hash(title))[:11])
                        items.append(normalize_item(NewsItem(
                            id=f'youtube_{vid}_{hash(title) % 100000}',
                            title=title,
                            url=f'https://www.youtube.com/watch?v={vid}',
                            source='youtube',
                            source_name='YouTube',
                            source_region='INT',
                            raw_score=100 - len(items),
                            rank=len(items) + 1,
                        )))
            except Exception:
                continue

        # 方案2：从 YouTube 搜索页面直接提取（绕过 JS 渲染）
        if len(items) < 10:
            try:
                resp = httpx.get(
                    'https://www.youtube.com/results?search_query=AI+chatbot+LLM&sp=CAMSAhAC',
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml',
                    },
                    timeout=10,
                )
                text = resp.text

                # 从 ytInitialData 中提取视频
                m = re.search(r'ytInitialData\s*=\s*\{', text)
                if m:
                    start = m.start()
                    depth = 0
                    for i, c in enumerate(text[start:]):
                        if c == '{':
                            depth += 1
                        elif c == '}':
                            depth -= 1
                            if depth == 0:
                                end = start + i + 1
                                break
                    import json
                    raw = text[start + len('ytInitialData = '):end]
                    data = json.loads(raw)
                    contents = data.get('contents', [])
                    for c in contents:
                        if isinstance(c, dict):
                            for key in c:
                                sub = c[key]
                                if isinstance(sub, dict):
                                    tabs = sub.get('tabs', [])
                                    for tab in tabs:
                                        tab_r = tab.get('tabRenderer', {})
                                        grid = tab_r.get('content', {}).get('richGridRenderer', {}).get('contents', [])
                                        for item in grid:
                                            vid_r = item.get('richItemRenderer', {}).get('content', {}).get('videoRenderer', {})
                                            if vid_r:
                                                title_runs = vid_r.get('title', {}).get('runs', [])
                                                if title_runs:
                                                    title = title_runs[0].get('text', '')
                                                    vid_id = vid_r.get('videoId', '')
                                                    if title and vid_id and title not in seen_titles:
                                                        seen_titles.add(title)
                                                        items.append(normalize_item(NewsItem(
                                                            id=f'youtube_{vid_id}_{hash(title) % 100000}',
                                                            title=title,
                                                            url=f'https://www.youtube.com/watch?v={vid_id}',
                                                            source='youtube',
                                                            source_name='YouTube',
                                                            source_region='INT',
                                                            raw_score=100 - len(items),
                                                            rank=len(items) + 1,
                                                        )))
            except Exception:
                pass

        return items[:30]
