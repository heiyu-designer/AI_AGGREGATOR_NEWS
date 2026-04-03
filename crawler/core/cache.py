"""TTL 内存缓存 — 避免频繁请求数据源"""

from cachetools import TTLCache
from typing import Optional
from sources.base import NewsItem

# 全局缓存实例
_news_cache: Optional[list[NewsItem]] = None
_cache_timestamp: Optional[float] = None

# TTL: 30 分钟（秒）
CACHE_TTL = 1800


def get_cached_news() -> Optional[list[NewsItem]]:
    """获取缓存的新闻数据"""
    return _news_cache


def set_cached_news(items: list[NewsItem]) -> None:
    """设置缓存"""
    global _news_cache, _cache_timestamp
    import time
    _news_cache = items
    _cache_timestamp = time.time()


def is_cache_valid() -> bool:
    """判断缓存是否有效"""
    if _news_cache is None or _cache_timestamp is None:
        return False
    import time
    return (time.time() - _cache_timestamp) < CACHE_TTL


def get_cache_age() -> Optional[int]:
    """获取缓存已存在时间（秒）"""
    if _cache_timestamp is None:
        return None
    import time
    return int(time.time() - _cache_timestamp)


def clear_cache() -> None:
    """清空缓存"""
    global _news_cache, _cache_timestamp
    _news_cache = None
    _cache_timestamp = None
