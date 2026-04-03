"""数据标准化工具"""

import re
from datetime import datetime, timezone
from sources.base import NewsItem
from core.classifier import classify_news, extract_tags


def now_iso() -> str:
    """返回当前 UTC 时间 ISO 格式"""
    return datetime.now(timezone.utc).isoformat()


def clean_title(title: str) -> str:
    """清理标题中的 HTML 标签和多余空白"""
    title = re.sub(r'<[^>]+>', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip()


def normalize_item(item: NewsItem) -> NewsItem:
    """对单条新闻进行标准化处理"""
    item.title = clean_title(item.title)
    item.fetched_at = now_iso()

    # 自动分类
    if not item.category:
        item.category = classify_news(item.title) or '产业动态'

    # 自动提取标签
    if not item.tags:
        item.tags = extract_tags(item.title)

    return item


def normalize_items(items: list[NewsItem]) -> list[NewsItem]:
    """批量标准化"""
    return [normalize_item(item) for item in items]
