"""Google Trends 爬虫

注意: Google Trends API 在部分地区限流，如返回空数据属正常现象。
"""

from pytrends.request import TrendReq
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item


class GoogleTrendsSource(BaseSource):
    info = SourceInfo(
        source='google_trends',
        name='Google Trends',
        region='INT',
        enabled=True,
        interval_seconds=3600,
    )

    def _fetch_with_retry(self, kw_list: list[str], retries: int = 1) -> dict:
        for attempt in range(retries):
            try:
                pytrends = TrendReq(hl='en-US', tz=480)
                pytrends.build_payload(kw_list=kw_list, timeframe='now 1-d')
                data = pytrends.related_topics()
                return data
            except Exception:
                if attempt < retries - 1:
                    import time
                    time.sleep(3)
        return {}

    def fetch(self) -> list[NewsItem]:
        ai_topics = [
            'ChatGPT', 'GPT-4', 'LLM', 'OpenAI', 'Anthropic Claude',
            'AI model', 'machine learning', 'AIGC', 'stable diffusion',
            'Sora', 'AGI', 'AI chip',
        ]

        items = []
        try:
            data = self._fetch_with_retry(ai_topics[:5])
        except Exception:
            return []

        for topic_list in data.values():
            if not isinstance(topic_list, dict):
                continue
            top_df = topic_list.get('top', {})
            if not isinstance(top_df, dict):
                continue
            df = top_df.get('value', [])
            if not isinstance(df, list):
                continue

            for i, entry in enumerate(df[:20], start=1):
                if not isinstance(entry, dict):
                    continue
                title = entry.get('topic_title', '')
                if not title:
                    continue

                item = NewsItem(
                    id=f'google_trends_{entry.get("topic_id", i)}',
                    title=title,
                    url=entry.get('link', 'https://trends.google.com'),
                    source='google_trends',
                    source_name='Google Trends',
                    source_region='INT',
                    raw_score=entry.get('value', 0),
                    rank=i,
                )
                items.append(normalize_item(item))

        # 如果 API 返回空，返回空列表（容错）
        return items[:20]
