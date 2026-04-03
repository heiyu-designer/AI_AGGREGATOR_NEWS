"""热度归一化 — 将各平台原始热度值归一化到 0-100"""

from sources.base import NewsItem


def normalize_score(item: NewsItem, max_raw: int | None = None) -> NewsItem:
    """将原始热度值归一化到 0-100"""
    if item.raw_score is None or item.raw_score == 0:
        item.hot_score = 50  # 无原始值，默认中间值
        return item

    if max_raw is None:
        max_raw = item.raw_score

    # 对数归一化，避免头部数值过大
    import math
    item.hot_score = min(100, int(math.log1p(item.raw_score) / math.log1p(max_raw) * 100))
    return item


def normalize_scores(items: list[NewsItem]) -> list[NewsItem]:
    """批量归一化热度分数"""
    if not items:
        return items

    # 找出各平台最大值
    by_source: dict[str, list[NewsItem]] = {}
    for item in items:
        by_source.setdefault(item.source, []).append(item)

    for source, source_items in by_source.items():
        max_raw = max(
            (it.raw_score or 1) for it in source_items
        )
        for item in source_items:
            normalize_score(item, max_raw)

    return items


def merge_and_rank(all_items: list[NewsItem], top_n: int = 50) -> list[NewsItem]:
    """合并所有来源，按热度排序，取前 N 条"""
    normalized = normalize_scores(all_items)
    sorted_items = sorted(normalized, key=lambda x: x.hot_score, reverse=True)
    return sorted_items[:top_n]
