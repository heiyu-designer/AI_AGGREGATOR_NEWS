# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 开发命令

### 前端（Next.js 16）

```bash
cd frontend
npm run dev      # 启动开发服务器（端口 3852）
npm run build    # 生产构建
npm start        # 生产模式运行
npm run lint     # ESLint 检查
```

环境变量 `NEXT_PUBLIC_API_URL` — 指向爬虫服务地址，当前配置为 `http://localhost:30852`

### 爬虫服务（FastAPI）

```bash
cd crawler
pip install -r requirements.txt
python -m playwright install --with-deps  # 首次安装 Playwright 浏览器依赖
uvicorn main:app --reload --port 30852   # 启动服务（必须从 crawler 目录运行）
```

API 文档访问：http://localhost:30852/docs

### 定时任务

服务内置 APScheduler，每天 **06:00 / 12:00 / 19:00**（Asia/Shanghai）自动抓取所有数据源更新缓存。

---

## 项目架构

两个独立服务，通过 REST API 通信，无数据库，数据全部缓存在爬虫服务内存中（TTL 1800 秒）。

```
前端 (Next.js, :3852)  ──fetch──►  爬虫 (FastAPI, :30852)
                                            │
                                      TTL 内存缓存
                                      21 个数据源
```

### 爬虫目录结构

| 文件 | 作用 |
|------|------|
| `main.py` | FastAPI 入口，所有路由（`/api/news`、`/api/sources` 等）、定时任务、并发抓取 |
| `sources/__init__.py` | `SOURCE_REGISTRY` 注册表，所有数据源在此注册 |
| `sources/base.py` | `BaseSource` 基类（`fetch()` 异步方法）和 `NewsItem` 数据类 |
| `core/cache.py` | TTL 内存缓存，装饰器 `@cached` 自动缓存 |
| `core/scorer.py` | `merge_and_rank()` 将各平台原始分数归一化到 0-100 |
| `core/classifier.py` | 关键词规则引擎，将新闻分为 AI模型/AI产品/学术/产业/AI技术 |
| `core/normalizer.py` | 数据标准化工具 |

### 前端目录结构

| 文件 | 作用 |
|------|------|
| `app/page.tsx` | 首页，完整 UI：Header（搜索/排序/刷新）、平台卡片网格、收藏 |
| `lib/api.ts` | API 调用封装，对接 `/api/news` |
| `types/news.ts` | TypeScript 类型：`NewsItem`、`NewsResponse`、`SortMode` |
| `components/Providers.tsx` | TanStack Query + React Query Client Provider |

前端通过 `@tanstack/react-query` 管理服务端状态，favorites 存在 localStorage。

---

## API 接口

`GET /api/news` 参数：

| 参数 | 说明 |
|------|------|
| `region` | `ALL` / `CN` / `INT` |
| `category` | 空表示全部，可选：AI模型 / AI产品 / 学术 / 产业 / AI技术 |
| `keyword` | 标题关键词搜索 |
| `sort` | `hot`（默认，按热度） / `time`（按时间） |
| `limit` | 返回条数上限（默认 200，最大 500） |
| `force_refresh` | `true` 绕过缓存强制重新抓取 |

---

## 数据源插件机制

新增数据源三步走：

1. 创建 `sources/xxx.py`，继承 `BaseSource`：
```python
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

class XxxSource(BaseSource):
    info = SourceInfo(
        source='xxx', name='显示名称',
        region='CN',   # CN=国内，INT=国际
        enabled=True,
        interval_seconds=1800,
    )

    async def fetch(self) -> list[NewsItem]:
        items = []
        # ... 抓取逻辑 ...
        for i, data in enumerate(results, start=1):
            items.append(normalize_item(NewsItem(
                id=f'xxx_{data["id"]}',
                title=data['title'],
                url=data['url'],
                source='xxx',
                source_name='显示名称',
                source_region='CN',
                raw_score=max(0, (30 - i) * 1000),
                rank=i,
            )))
        return items
```

2. 在 `sources/__init__.py` 添加导入和注册：
```python
from sources import xxx
# SOURCE_REGISTRY 中添加：
(xxx.XxxSource, True, 1800),   # (类, 是否启用, 采集间隔秒数)
```

3. 前端 `app/page.tsx` 的 `PLATFORMS` 数组添加一项：
```typescript
{ source: 'xxx', label: '显示名称', icon: '🆔', bg: 'bg-gradient-to-r from-X to-Y' },
```

---

## 当前数据源（23个，21个启用）

| 平台 | source | 地区 | 采集间隔 | 状态 |
|------|--------|------|----------|------|
| 知乎 | zhihu | CN | 30min | 启用 |
| 微博 | weibo | CN | 30min | 启用 |
| 今日头条 | toutiao | CN | 30min | 启用 |
| 百度热搜 | baidu | CN | 30min | 启用 |
| 澎湃新闻 | pengpai | CN | 30min | 启用 |
| 36氪 | kr36 | CN | 30min | 启用 |
| 人民网 | people | CN | 30min | 启用 |
| 新华社 | xinhua | CN | 30min | 启用 |
| 半月谈 | banyuetan | CN | 30min | 启用 |
| 微信热文 | weixin | CN | 30min | 启用 |
| 网易新闻 | netease | CN | 30min | 启用 |
| IT之家 | ithome | CN | 30min | 启用 |
| 量子位 | qbitai | CN | 30min | 启用 |
| 少数派 | shaoshupai | CN | 30min | 启用 |
| 简书 | jianshu | CN | 30min | 启用 |
| GitHub Trending | github | INT | 60min | 启用 |
| Hacker News | hackernews | INT | 30min | 启用 |
| Google Trends | google_trends | INT | 60min | 启用 |
| Toolify.ai | toolify | INT | 60min | 启用 |
| X/Twitter | twitter | INT | 30min | 启用 |
| YouTube | youtube | INT | 30min | 启用 |
| Hugging Face | huggingface | INT | 60min | 启用 |
| 虎嗅网 | huxiu | CN | 30min | **禁用**（海外 WAF 拦截） |
| FT中文网 | ftchinese | CN | 60min | **禁用**（Google News 重定向不可用） |

---

## 注意事项

### 知乎 URL 格式

知乎 API 返回的 `target.id` 是 19 位内部编码，正确的 URL 格式为 `https://www.zhihu.com/question/{id}`（单数 `question`，不是 `questions`）。

### Playwright 数据源

`toutiao.py`、`xinhua.py`、`toolify.py`、`jianshu.py`、`huggingface.py` 使用 Playwright 抓取 JS 渲染页面。首次安装需运行 `python -m playwright install --with-deps`。

### 特殊网络限制

- **FT中文网 / 虎嗅**：海外服务器无法直连，在 `__init__.py` 中 `enabled=False`
- **Hugging Face**：部分环境 SSL 握手超时，需 Playwright 绕过
- **Google News RSS**：`verify=False` 绕过 SSL 证书问题

### 并发抓取与缓存保护

`main.py` 中的 `fetch_all_sources()` 使用 `asyncio.gather` 并发抓取所有数据源，`scheduled_fetch()` 在抓取前保存旧缓存，失败时自动恢复，防止缓存清空后无数据可用。
