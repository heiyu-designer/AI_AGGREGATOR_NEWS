"""Twitter/X 爬虫 — 使用 Nitter RSS 获取 AI 相关推文"""

import httpx
import feedparser
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item


# Nitter 实例（按可用性排序，nitter.privacydev.net 是备选）
NITTER_INSTANCES = [
    'https://nitter.net',
    'https://nitter.privacydev.net',
    'https://nitter.poast.org',
]

# AI/科技相关的 Twitter 账号
AI_ACCOUNTS = [
    'sama',                  # Sam Altman
    'ylecun',                # Yann LeCun
    'AndrewYNg',             # Andrew Ng
    'Jim_Fan',               # Jim Fan (NVIDIA AI)
    'emollick',              # Ethan Mollick
]


class TwitterSource(BaseSource):
    info = SourceInfo(
        source='twitter',
        name='X/Twitter',
        region='INT',
        enabled=True,
        interval_seconds=1800,
    )

    def fetch(self) -> list[NewsItem]:
        items = []
        seen_ids = set()

        for instance in NITTER_INSTANCES:
            for username in AI_ACCOUNTS:
                try:
                    resp = httpx.get(
                        f'{instance}/{username}/rss',
                        headers={'User-Agent': 'Mozilla/5.0'},
                        timeout=2,          # 快速失败，不阻塞
                        follow_redirects=True,
                    )
                    if resp.status_code != 200 or len(resp.text) < 500:
                        continue

                    feed = feedparser.parse(resp.text)
                    for entry in feed.entries[:10]:
                        tweet_id = entry.get('id', entry.get('link', ''))
                        if tweet_id in seen_ids:
                            continue
                        seen_ids.add(tweet_id)

                        title = entry.get('title', '').strip()
                        link = entry.get('link', '')
                        if not title or len(title) < 5:
                            continue

                        # 清理标题（去除 "username: " 前缀）
                        title = title.split(':', 1)[-1].strip()
                        if not title:
                            continue

                        items.append(normalize_item(NewsItem(
                            id=f'twitter_{hash(tweet_id) % 1000000}',
                            title=title,
                            url=link or f'https://twitter.com/{username}',
                            source='twitter',
                            source_name='X/Twitter',
                            source_region='INT',
                            raw_score=100 - len(items),
                            rank=len(items) + 1,
                        )))
                except Exception:
                    continue

            # 获取到足够数据就停止
            if len(items) >= 20:
                break

        return items[:30]
