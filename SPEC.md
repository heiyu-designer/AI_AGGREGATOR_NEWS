# AI 新闻聚合站 — MVP 手册

> 本文档是项目的需求分析 + 技术规格说明书，开发前请先通读确认。

---

## 一、项目目标

**一句话定位**：聚焦 AI 领域的热点新闻聚合平台，国内外 AI 热点一屏尽览。

**核心价值**：解决目前市面上新闻聚合站缺乏国际视野、AI 内容分散的问题，为 AI 从业者、投资人、爱好者提供一站式热点获取渠道。

---

## 二、数据来源（完整版）

### 2.1 国内 AI 新闻（11个来源）

| # | 平台 | 数据类型 | 采集方式 | 优先级 |
|---|---|---|---|---|
| 1 | 知乎 | AI 相关问题/文章热榜 | 非官方 API / RSS | P0 |
| 2 | 微博 | AI 热搜词（关键词过滤） | 第三方 API | P0 |
| 3 | 百度 | AI 热搜榜 | 网页爬取 | P0 |
| 4 | 今日头条 | AI 频道热文 | 移动端 API 抓包 | P1 |
| 5 | 澎湃新闻 | 科技/AI 分类 | RSS | P1 |
| 6 | 36氪 | AI 频道文章 | 网页爬取 | P1 |
| 7 | 虎嗅 | AI/科技文章 | 网页爬取 | P1 |
| 8 | 品玩 PingWest | AI 频道文章 | 网页爬取 | P1 |
| 9 | 网易新闻 | AI/科技热文 | RSS / 网页 | P2 |
| 10 | 人民网 | 科技分类 | RSS | P2 |
| 11 | 微信公众号 | AI 相关文章 | 第三方聚合 API | P2 |

### 2.2 国际 AI 新闻（6个来源）

| # | 平台 | 数据类型 | 采集方式 | 优先级 |
|---|---|---|---|---|
| 1 | Google Trends | AI 相关趋势 | pytrends 库 | P0 |
| 2 | X (Twitter) | AI 相关热搜/博主 | 第三方 API | P1 |
| 3 | YouTube | AI 相关热门视频 | YouTube Data API | P1 |
| 4 | Product Hunt | AI 产品发布 | 网页爬取 | P1 |
| 5 | Hacker News | AI 相关帖子 | 官方 API | P1 |
| 6 | arXiv (cs.AI) | AI 热门论文 | RSS Feed | P2 |

### 2.3 AI 内容关键词过滤

用于从泛内容平台（微博、知乎、百度等）精准过滤 AI 相关内容：

```
AI, 人工智能, 大模型, LLM, ChatGPT, GPT, AIGC, AGI,
机器学习, 深度学习, NLP, 大语言模型, Transformer,
Sora, Gemini, Claude, 文心一言, 通义千问, Kimi,
智谱AI, Midjourney, Stable Diffusion, 自动驾驶,
人形机器人, AI芯片, 算力, 英伟达, NVIDIA, AMD,
OpenAI, Google DeepMind, Anthropic, xAI, Meta AI,
Stable Diffusion, Hugging Face, LangChain, RAG,
向量数据库, 微调, RLHF, Prompt工程, AI Agent,
Copilot, AI PC, AI手机, 端侧AI, 多模态, AI安全
```

---

## 三、数据标准格式

```typescript
interface NewsItem {
  id: string;           // 格式: {source}_{原始ID}，如 weibo_123456
  title: string;        // 新闻标题（纯文本，不含HTML）
  summary?: string;     // 摘要（可为空，暂不做AI摘要）
  url: string;          // 原文链接
  source: string;       // 平台标识 weibo/zhihu/bing/hn/ph/arxiv...
  sourceName: string;    // 展示用名称 "微博" "知乎" "Hacker News"
  sourceRegion: 'CN' | 'INT';  // 'CN'=国内 'INT'=国际
  category?: string;    // 内容分类：AI模型/AI产品/学术/产业/融资
  hotScore: number;     // 热度分 0-100（归一化后）
  rawScore?: number;    // 平台原始热度值（如 5000000）
  rank?: number;        // 平台原始排名（如热搜第3名）
  publishedAt: string;  // 发布时间 ISO8601（可为空）
  fetchedAt: string;    // 抓取时间 ISO8601
  imageUrl?: string;    // 配图 URL（可选）
  tags?: string[];      // 自动提取的关键词标签
}
```

**内容分类规则（规则引擎）**：

| 分类 | 命中关键词 |
|---|---|
| AI模型 | 大模型, GPT, LLM, ChatGPT, Gemini, Claude, Sora, 文心, 通义, Kimi, 智谱 |
| AI产品 | 发布, 上线, 推出, 产品, 工具, 应用, App, 网站 |
| 学术论文 | arXiv, 论文, 研究, 基准, benchmark |
| 产业动态 | 融资, 收购, 合作, 裁员, 财报, 政策, 监管 |
| AI技术 | 训练, 微调, RLHF, Prompt, RAG, Agent, 幻觉 |

---

## 四、系统架构

```
┌──────────────────────┐
│  Next.js (Vercel)    │  纯展示，无数据库依赖
└──────────┬───────────┘
           │ fetch /api/news
┌──────────▼───────────┐
│  Python 爬虫服务      │  Docker 部署，自有服务器
│  (无状态，按需抓取)   │  无数据库，TTL 内存缓存
│  FastAPI             │  可插拔数据源架构
└──────────────────────┘
```

**关键设计**：
- **无数据库**：爬虫实时抓取，按需返回，服务端 TTL 内存缓存（避免重复请求打到数据源）
- **可插拔数据源**：每个来源独立 Python 模块，配置文件中注册/开关，新增来源零改动
- **Docker 部署**：爬虫服务打包成 Docker，一键部署到服务器

**部署说明**：
- 前端 → Vercel（免费 CDN 加速）
- 爬虫服务 → Docker 部署，自有服务器
- 无数据库，零运维负担

---

## 五、页面与功能

### 5.1 首页（核心页面）

```
┌─────────────────────────────────────────────────┐
│ Header: Logo | 搜索框 | 导航 | 刷新按钮 | 来源管理 │
├─────────────────────────────────────────────────┤
│ 🔥 今日热点 Banner（热度最高的5条）               │
├──────────────────┬──────────────────────────────┤
│  国内 AI 新闻      │  国际 AI 新闻                │
│  (60% 宽度)       │  (40% 宽度)                  │
│  [全部] [模型]     │  [全部] [产品] [学术]         │
│  [产品] [产业]     │                              │
│  [学术] [技术]     │  Hacker News                │
│                  │  Google Trends               │
│  微博 | 知乎      │  Product Hunt               │
│  百度 | 头条      │  X / YouTube                │
│  36氪 | 虎嗅      │                              │
│  品玩 | 网易      │                              │
├──────────────────┴──────────────────────────────┤
│ Footer: 数据来源声明 | 更新: 30分钟前 | 服务器时间 │
└─────────────────────────────────────────────────┘
```

### 5.2 功能清单

| 功能 | 描述 | MVP 阶段 |
|---|---|---|
| 热搜展示 | 各平台 AI 热搜列表 | MVP |
| 分栏展示 | 国内/国际双栏，PC 端并行，移动端 Tab | MVP |
| 内容分类 | 按AI模型/产品/学术/产业/技术分类筛选 | MVP |
| 热度排序 | 默认按热度降序 | MVP |
| 时间排序 | 切换为按发布时间排序 | MVP |
| 关键词搜索 | 输入关键词过滤，支持搜索历史 | MVP |
| 跳转原文 | 点击卡片跳转原文（新窗口打开） | MVP |
| 手动刷新 | 一键触发重新抓取 | MVP |
| 收藏功能 | localStorage 存储收藏列表 | MVP |
| 定时刷新 | 后台每 30 分钟自动增量更新 | MVP |
| 移动端适配 | 响应式布局 | MVP |
| 数据来源管理 | 可开关各平台数据源 | 后置 |

### 5.3 响应式断点

- **Desktop (>1024px)**：左右分栏并行
- **Tablet (768-1024px)**：国内/国际 Tab 切换
- **Mobile (<768px)**：单列，卡片堆叠，顶部 Tab 筛选

---

## 六、技术栈

### 6.1 前端

| 技术 | 选型 | 说明 |
|---|---|---|
| 框架 | Next.js 14 (App Router) | SSR/SSG 支持，API Routes 内置 |
| 语言 | TypeScript | 类型安全 |
| 样式 | Tailwind CSS | 快速构建响应式 UI |
| 状态管理 | TanStack Query (React Query) | 服务端状态缓存/同步 |
| 图表/数字 | date-fns | 日期格式化 |
| 图标 | Lucide React | 开源图标库 |
| 部署 | Vercel | 免费，CDN 加速 |

### 6.2 后端（爬虫服务）

| 技术 | 选型 | 说明 |
|---|---|---|
| 语言 | Python 3.11+ | 数据处理生态丰富 |
| Web 框架 | FastAPI | 高性能 API，自动文档，无状态服务 |
| 动态爬虫 | Playwright | 渲染 JS 页面的首选 |
| 静态爬虫 | httpx + BeautifulSoup | 轻量快速 |
| RSS 解析 | feedparser | 标准 RSS/Atom 解析 |
| 缓存 | cachetools (TTL) | 内存 TTL 缓存，避免重复请求 |
| 调度器 | APScheduler | 定时预热缓存 |
| 数据校验 | Pydantic | 类型校验 |
| 趋势数据 | pytrends | Google Trends 官方库 |
| Docker | Docker + Docker Compose | 一键部署 |

---

## 七、爬虫优先级与更新频率

| 优先级 | 来源 | 更新频率 | 方式 |
|---|---|---|---|
| P0 | 知乎、微博、百度 | 30 分钟 | API / 爬虫 |
| P0 | Google Trends | 60 分钟 | pytrends |
| P1 | 36氪、虎嗅、品玩、今日头条 | 60 分钟 | Playwright / httpx |
| P1 | Hacker News、Product Hunt | 60 分钟 | API / httpx |
| P1 | X、YouTube | 120 分钟 | API |
| P2 | arXiv、网易、人民网、微信 | 120 分钟 | RSS / 爬虫 |

---

## 八、MVP 开发计划

### Week 1：项目搭建 & 核心数据
- [ ] 初始化 Next.js 项目 + Tailwind CSS + TypeScript
- [ ] 搭建 Python 爬虫脚手架（FastAPI + Playwright + httpx）
- [ ] 实现 P0 级爬虫（知乎、Google Trends、Hacker News）
- [ ] FastAPI 基础接口（/api/news、/api/sources）
- [ ] TTL 缓存层（cachetools）
- [ ] 基础 UI 框架（Header、左右分栏布局、新闻卡片）
- [ ] Docker + Docker Compose 配置文件

### Week 2：全量数据 & 核心功能
- [ ] 实现 P1/P2 级爬虫（全部 17 个来源）
- [ ] 热度归一化算法（跨平台归一化到 0-100）
- [ ] 内容分类引擎（规则 + 关键词）
- [ ] 分类筛选 + 排序切换
- [ ] 搜索功能
- [ ] 手动刷新按钮 + 定时任务预热缓存

### Week 3：体验打磨 & 适配
- [ ] 收藏功能（localStorage）
- [ ] 移动端响应式适配
- [ ] 骨架屏 / 加载状态
- [ ] 错误处理 + 空状态展示
- [ ] Footer 声明 + 更新频率展示
- [ ] 部署到 Vercel（前端）+ Docker（爬虫服务）

---

## 九、已知挑战与应对

| 挑战 | 应对 |
|---|---|
| 微博/微信强反爬 | 优先用第三方 API，User-Agent 轮换，降级方案：减少抓取频率 |
| Google Trends 限流 | pytrends 退避策略（retry_after）+ 本地缓存 2 小时 |
| X (Twitter) 国内访问 | 使用第三方聚合 API 或代理池 |
| 今日头条 JS 渲染 | Playwright headless 模式 |
| 爬虫服务稳定性 | APScheduler 重试机制 + 失败日志 + 告警 |
| 数据合法性 | 仅展示标题+链接，注明来源，不存储全文 |

---

## 十、文件结构

```
ai_aggregator_news/
├── frontend/                   # Next.js 前端
│   ├── app/
│   │   ├── layout.tsx         # 根布局
│   │   ├── page.tsx           # 首页
│   │   └── api/               # API Routes
│   │       └── news/
│   │           └── route.ts
│   ├── components/             # UI 组件
│   │   ├── Header.tsx
│   │   ├── NewsCard.tsx
│   │   ├── NewsColumn.tsx
│   │   ├── FilterBar.tsx
│   │   └── Footer.tsx
│   ├── lib/
│   │   ├── api.ts             # API 请求封装
│   │   └── utils.ts           # 工具函数
│   ├── types/
│   │   └── news.ts            # 类型定义
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── crawler/                   # Python 爬虫服务
│   ├── main.py                # FastAPI 入口
│   ├── config.py              # 数据源配置（可插拔）
│   ├── sources/               # 各平台爬虫（可插拔模块）
│   │   ├── __init__.py        # 数据源注册表
│   │   ├── base.py            # 基类（统一接口）
│   │   ├── zhihu.py           # 知乎
│   │   ├── weibo.py           # 微博
│   │   ├── baidu.py           # 百度
│   │   ├── google_trends.py   # Google Trends
│   │   ├── hacker_news.py     # Hacker News
│   │   ├── product_hunt.py    # Product Hunt
│   │   ├── arxiv.py           # arXiv
│   │   └── tech_portals.py    # 36氪/虎嗅/品玩
│   ├── core/
│   │   ├── classifier.py       # 内容分类器
│   │   ├── scorer.py          # 热度归一化
│   │   ├── cache.py           # TTL 缓存
│   │   └── normalizer.py      # 数据标准化
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── SPEC.md                    # 本文档
└── README.md                  # 项目说明
```

---

## 十一、MVP 确认清单

在开始开发前，请确认以下要点：

- [x] **项目定位**：AI 新闻聚合站（不泛化到所有新闻）
- [x] **数据来源**：17 个来源（国内11 + 国际6）
- [x] **展示方式**：国内/国际分栏 + 内容分类筛选
- [x] **技术栈**：Next.js + Python FastAPI（无数据库）
- [x] **数据策略**：实时抓取 + TTL 内存缓存，无持久化
- [x] **可插拔**：数据源配置化管理，新增来源通过配置文件注册
- [x] **部署方式**：Vercel（前端）+ Docker（爬虫服务）
- [x] **AI 摘要**：MVP 阶段不接入
- [x] **用户系统**：不做，收藏用 localStorage
- [x] **数据合规**：只展示标题+链接，注明来源
