"""FastAPI 爬虫服务入口"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from sources import get_enabled_sources
from sources.base import NewsItem
from core.cache import (
    get_cached_news, set_cached_news, is_cache_valid,
    get_cache_age, clear_cache,
)
from core.scorer import merge_and_rank

logger = logging.getLogger(__name__)

# 定时任务调度器
_scheduler: Optional[AsyncIOScheduler] = None


async def scheduled_fetch():
    """定时抓取所有数据源"""
    from datetime import datetime
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f'[定时任务] 开始抓取数据 {now}')
    try:
        clear_cache()
        all_items, source_counts = await fetch_all_sources()
        ranked = merge_and_rank(all_items, top_n=1000)
        set_cached_news(ranked)
        logger.info(f'[定时任务] 完成，共抓取 {len(all_items)} 条，来自 {[k for k,v in source_counts.items() if v > 0]}')
    except Exception as e:
        logger.error(f'[定时任务] 抓取失败: {e}')


def start_scheduler():
    """启动定时任务调度器：每天 6:00 / 12:00 / 19:00 自动更新"""
    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = AsyncIOScheduler()
    # 每天早上 6:00
    _scheduler.add_job(scheduled_fetch, CronTrigger(hour=6, minute=0),
                       id='fetch_0600', name='早间更新 06:00', misfire_grace_time=3600)
    # 每天中午 12:00
    _scheduler.add_job(scheduled_fetch, CronTrigger(hour=12, minute=0),
                       id='fetch_1200', name='午间更新 12:00', misfire_grace_time=3600)
    # 每天晚上 19:00
    _scheduler.add_job(scheduled_fetch, CronTrigger(hour=19, minute=0),
                       id='fetch_1900', name='晚间更新 19:00', misfire_grace_time=3600)
    _scheduler.start()
    logger.info('定时任务已启动：06:00 / 12:00 / 19:00')


def stop_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None


app = FastAPI(
    title='AI News Aggregator API',
    description='AI 新闻聚合后端服务 — 实时抓取国内外 AI 热点',
    version='1.0.0',
)


@app.on_event('startup')
async def startup():
    start_scheduler()


@app.on_event('shutdown')
async def shutdown():
    stop_scheduler()


# CORS 允许前端跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# ---- 响应模型 ----

class SourceInfoResponse(BaseModel):
    source: str
    name: str
    region: str
    enabled: bool
    item_count: int


class NewsItemResponse(BaseModel):
    id: str
    title: str
    summary: Optional[str] = None
    url: str
    source: str
    sourceName: str
    sourceRegion: str
    category: Optional[str] = None
    hotScore: int
    rawScore: Optional[int] = None
    rank: Optional[int] = None
    publishedAt: Optional[str] = None
    fetchedAt: str
    imageUrl: Optional[str] = None
    tags: list[str] = []


class NewsResponse(BaseModel):
    items: list[NewsItemResponse]
    total: int
    fetchedAt: str
    sources: list[SourceInfoResponse]


def to_response(item: NewsItem) -> NewsItemResponse:
    return NewsItemResponse(
        id=item.id,
        title=item.title,
        summary=item.summary,
        url=item.url,
        source=item.source,
        sourceName=item.source_name,
        sourceRegion=item.source_region,
        category=item.category,
        hotScore=item.hot_score,
        rawScore=item.raw_score,
        rank=item.rank,
        publishedAt=item.published_at,
        fetchedAt=item.fetched_at,
        imageUrl=item.image_url,
        tags=item.tags or [],
    )


# ---- 全局锁，防止重复抓取 ----
_fetch_lock = asyncio.Lock()


async def fetch_all_sources() -> tuple[list[NewsItem], dict]:
    """并发抓取所有已启用数据源"""
    sources = get_enabled_sources()
    source_counts = {}

    async def fetch_one(source) -> list[NewsItem]:
        try:
            # 兼容同步/异步爬虫
            if asyncio.iscoroutinefunction(source.fetch):
                items = await source.fetch()
            else:
                items = await asyncio.to_thread(source.fetch)
            source_counts[source.info.source] = len(items)
            return items
        except Exception:
            source_counts[source.info.source] = 0
            return []

    tasks = [fetch_one(s) for s in sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_items = []
    for result in results:
        if isinstance(result, Exception):
            continue
        if isinstance(result, list):
            all_items.extend(result)

    return all_items, source_counts


async def ensure_cache() -> None:
    """确保缓存有效，如无效则重新抓取"""
    if is_cache_valid():
        return

    async with _fetch_lock:
        if is_cache_valid():  # 双重检查
            return

        all_items, _ = await fetch_all_sources()
        ranked = merge_and_rank(all_items, top_n=1000)
        set_cached_news(ranked)


# ---- API 路由 ----

@app.get('/api/news', response_model=NewsResponse)
async def get_news(
    region: str = Query('ALL', description="筛选区域: ALL | CN | INT"),
    category: str = Query('', description="内容分类筛选"),
    keyword: str = Query('', description="关键词搜索"),
    sort: str = Query('hot', description="排序: hot | time"),
    limit: int = Query(200, ge=1, le=500),
    force_refresh: bool = Query(False, description="是否强制刷新"),
):
    """
    获取新闻列表

    - **region**: 区域筛选 (ALL=全部, CN=国内, INT=国际)
    - **category**: 内容分类 (AI模型/AI产品/学术论文/产业动态/AI技术)
    - **keyword**: 关键词搜索（标题匹配）
    - **sort**: 排序方式 (hot=热度, time=时间)
    - **limit**: 返回条数上限
    - **force_refresh**: 强制重新抓取（绕过缓存）
    """
    if force_refresh:
        clear_cache()

    await ensure_cache()
    items = get_cached_news() or []

    # 区域筛选
    if region == 'CN':
        items = [i for i in items if i.source_region == 'CN']
    elif region == 'INT':
        items = [i for i in items if i.source_region == 'INT']

    # 分类筛选
    if category:
        items = [i for i in items if i.category == category]

    # 关键词搜索
    if keyword:
        kw_lower = keyword.lower()
        items = [i for i in items if kw_lower in i.title.lower()]

    # 排序
    if sort == 'time':
        items = sorted(
            items,
            key=lambda x: x.published_at or '',
            reverse=True,
        )
    else:
        items = sorted(items, key=lambda x: x.hot_score, reverse=True)

    # 限制条数
    items = items[:limit]

    # 来源统计
    sources = get_enabled_sources()
    source_counts = {}
    for s in sources:
        count = sum(1 for i in items if i.source == s.info.source)
        source_counts[s.info.source] = count

    source_infos = [
        SourceInfoResponse(
            source=s.info.source,
            name=s.info.name,
            region=s.info.region,
            enabled=s.info.enabled,
            item_count=source_counts.get(s.info.source, 0),
        )
        for s in sources
    ]

    return NewsResponse(
        items=[to_response(i) for i in items],
        total=len(items),
        fetchedAt=datetime.now(timezone.utc).isoformat(),
        sources=source_infos,
    )


@app.post('/api/refresh')
async def refresh_cache():
    """手动触发重新抓取"""
    clear_cache()
    await ensure_cache()
    items = get_cached_news() or []
    return {'status': 'ok', 'total': len(items)}


@app.get('/api/sources')
async def get_sources():
    """获取所有数据源列表"""
    sources = get_enabled_sources()
    return [
        {
            'source': s.info.source,
            'name': s.info.name,
            'region': s.info.region,
            'enabled': s.info.enabled,
            'intervalSeconds': s.info.interval_seconds,
        }
        for s in sources
    ]


@app.get('/api/status')
async def get_status():
    """获取服务状态"""
    cache_age = get_cache_age()
    items = get_cached_news() or []
    return {
        'status': 'ok',
        'cache_valid': is_cache_valid(),
        'cache_age_seconds': cache_age,
        'cached_items': len(items),
        'sources_count': len(get_enabled_sources()),
        'server_time': datetime.now(timezone.utc).isoformat(),
    }


@app.get('/health')
async def health():
    return {'status': 'ok'}


@app.get('/api/scheduler')
async def get_scheduler_status():
    """查看定时任务状态"""
    if _scheduler is None:
        return {'status': 'not_running'}
    jobs = _scheduler.get_jobs()
    return {
        'status': 'running',
        'jobs': [
            {
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
            }
            for job in jobs
        ]
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
