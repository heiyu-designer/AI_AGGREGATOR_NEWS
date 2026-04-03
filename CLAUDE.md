# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 开发命令

### 前端（Next.js）

```bash
cd frontend
npm run dev      # 启动开发服务器（端口 3852）
npm run build    # 生产构建
npm run lint     # ESLint 检查
```

环境变量：`NEXT_PUBLIC_API_URL` — 指向爬虫服务地址，当前配置为 `http://localhost:30852`

### 爬虫服务（FastAPI）

```bash
cd crawler
pip install -r requirements.txt
python -m playwright install --with-deps  # 首次安装 Playwright 浏览器
uvicorn main:app --reload --port 30852  # 启动服务
```

API 文档访问：http://localhost:30852/docs

### 定时任务

服务内置 APScheduler，每天 **06:00 / 12:00 / 19:00** 自动抓取所有数据源更新缓存。
- `GET /api/scheduler` — 查看定时任务状态（下次执行时间）
- `POST /api/refresh` — 手动触发一次抓取

---

## 项目架构

项目分为两个独立服务：

- **frontend/** — Next.js 14 前端，纯展示，通过 fetch 调用爬虫服务 API，无数据库
- **crawler/** — Python FastAPI 爬虫服务，无状态，TTL 内存缓存 + APScheduler 定时任务，19 个可插拔数据源

### 前端

- [frontend/app/page.tsx](frontend/app/page.tsx) — 首页（唯一页面），包含完整 UI：Header 搜索框、平台卡片网格、排序切换、收藏功能
- [frontend/lib/api.ts](frontend/lib/api.ts) — API 请求封装，调用 `/api/news`
- [frontend/types/news.ts](frontend/types/news.ts) — `NewsItem`、`NewsResponse`、`SortMode` 等类型

卡片网格布局：`grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4`，一行最多 4 个平台卡片，每卡片内部可滚动展示最多 10 条新闻。通过 `@tanstack/react-query` 管理服务端状态，favorites 存储在 localStorage。

### 爬虫

- [crawler/main.py](crawler/main.py) — FastAPI 入口，路由 `/api/news`、`/api/sources`、`/api/status`、`/api/scheduler`、`/api/refresh`
- [crawler/sources/__init__.py](crawler/sources/__init__.py) — 数据源注册表 `SOURCE_REGISTRY`
- [crawler/sources/base.py](crawler/sources/base.py) — `BaseSource` 基类，所有爬虫继承它
- [crawler/core/scorer.py](crawler/core/scorer.py) — 热度归一化，`merge_and_rank()` 跨平台归一化到 0-100
- [crawler/core/cache.py](crawler/core/cache.py) — TTL 内存缓存（TTL=1800秒）
- [crawler/core/classifier.py](crawler/core/classifier.py) — 内容分类，按关键词分为 AI模型/AI产品/学术/产业/AI技术

---

## API 接口

`GET /api/news` 参数：

| 参数 | 说明 |
|------|------|
| `region` | `ALL` \| `CN` \| `INT` |
| `category` | AI模型/AI产品/学术/产业/AI技术（空表示全部） |
| `keyword` | 标题关键词搜索 |
| `sort` | `hot`（默认）\| `time` |
| `limit` | 返回条数上限（默认 200，最大 500） |
| `force_refresh` | `true` 绕过缓存强制重新抓取 |

---

## 数据源插件机制

每个数据源是 `sources/` 下独立 Python 文件，实现 `BaseSource`。启用/禁用和采集间隔在 [sources/__init__.py](crawler/sources/__init__.py) 的 `SOURCE_REGISTRY` 中配置：

```python
SOURCE_REGISTRY: list[tuple[type[BaseSource], bool, int]] = [
    (zhihu.ZhihuSource, True, 1800),   # (类, 是否启用, 间隔秒数)
    ...
]
```

新增数据源：创建 `sources/xxx.py` → 在 `__init__.py` 导入 → 加入 `SOURCE_REGISTRY`。

---

## 技术选型要点

- **无数据库**：数据缓存在爬虫服务内存中（TTL），不持久化，每天 06:00 / 12:00 / 19:00 自动更新
- **可插拔架构**：19 个数据源独立实现，通过注册表开关，无需改动核心代码
- **热度归一化**：`scorer.merge_and_rank()` 将各平台原始热度值归一化到统一的 0-100 分
- **内容分类**：规则引擎在 `classifier.py`，按关键词将新闻分类

---

## 注意事项

### 知乎数据源

知乎热榜 API（`api.zhihu.com/topstory/hot-lists/total`）返回的 `target.id` 是 19 位内部编码，不是真实问题 ID。正确的 URL 格式为 `https://www.zhihu.com/question/{id}`（注意是单数 `question`，不是复数 `questions`）。知乎有强反爬限制，部分环境可能无法直接访问 `/question/{id}` 页面。

### Playwright 数据源

`toutiao.py`、`xinhua.py`、`toolify.py`、`jianshu.py` 等使用 Playwright 无头浏览器抓取 JS 渲染页面，首次安装需运行 `python -m playwright install --with-deps`。这些爬虫在容器/服务器环境可能需要额外配置浏览器依赖。
