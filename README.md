# AI 热点聚合站 (AI News Aggregator)

聚焦 AI 领域的新闻聚合平台，国内外 AI 热点一屏尽览。

## 项目结构

```
ai_aggregator_news/
├── frontend/          # Next.js 前端
│   ├── app/           # App Router 页面
│   ├── components/    # UI 组件
│   ├── lib/          # API 工具
│   └── types/        # TypeScript 类型
│
├── crawler/          # Python 爬虫服务
│   ├── main.py       # FastAPI 入口
│   ├── sources/      # 各平台爬虫（可插拔）
│   ├── core/         # 核心模块（缓存、分类、归一化）
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── SPEC.md           # 项目规格说明书
```

## 快速开始

### 1. 启动爬虫服务

```bash
cd crawler

# 安装依赖
pip install -r requirements.txt

# 方式A: 直接运行（开发）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 方式B: Docker 部署（生产）
docker compose up -d
```

服务地址: http://localhost:8000
API 文档: http://localhost:8000/docs

### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build
npm start
```

前端地址: http://localhost:3852

### 3. 环境变量

复制 `.env.local.example` 为 `.env.local`，修改 `NEXT_PUBLIC_API_URL` 为爬虫服务地址。

## 已集成的数据来源

### 国内（P0-P1）
- 知乎热榜
- 微博热搜
- 百度热搜

### 国际（P0-P1）
- Google Trends (AI 相关)
- Hacker News (AI 相关)

### 扩展数据源（可在 sources/ 添加）
- 36氪、虎嗅、品玩（科技媒体）
- Product Hunt（AI 产品发布）
- arXiv cs.AI（学术论文）
- X (Twitter)、YouTube

## 添加新的数据源

1. 在 `crawler/sources/` 创建新文件，如 `36kr.py`
2. 继承 `BaseSource`，实现 `fetch()` 方法
3. 在 `crawler/sources/__init__.py` 的 `SOURCE_REGISTRY` 中注册
4. 无需修改 API 代码，自动生效

## API 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/news` | 获取新闻列表 |
| POST | `/api/refresh` | 手动触发重新抓取 |
| GET | `/api/sources` | 获取数据源列表 |
| GET | `/api/status` | 获取服务状态 |
| GET | `/health` | 健康检查 |

## 部署

### 前端部署（Vercel）

```bash
cd frontend
npx vercel --prod
```

### 爬虫服务部署（服务器）

```bash
cd crawler
docker compose up -d
```

访问 https://your-domain.com 设置 `NEXT_PUBLIC_API_URL` 环境变量。
