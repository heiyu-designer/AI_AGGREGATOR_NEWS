"""数据源配置文件 — 管理所有可用的爬虫来源

新增数据源：
1. 在 sources/ 目录创建新的 *.py 文件，继承 BaseSource
2. 在 SOURCES 列表中注册即可自动生效
"""

from sources.base import BaseSource, SourceInfo

# 全局 AI + 科技关键词过滤列表（用于国内泛平台热搜过滤）
AI_KEYWORDS = [
    # 核心 AI 词
    'AI', '人工智能', '大模型', 'LLM', 'ChatGPT', 'AIGC', 'AGI',
    '机器学习', '深度学习', 'NLP', '大语言模型', 'Transformer',
    'Sora', 'Gemini', 'Claude', '文心', '通义', 'Kimi',
    '智谱', 'Midjourney', 'Stable Diffusion', '自动驾驶',
    '人形机器人', 'AI芯片', '算力', '英伟达', 'NVIDIA', 'AMD',
    'OpenAI', 'Anthropic', 'xAI', 'Meta AI', 'Hugging Face',
    'LangChain', 'RAG', 'RLHF', 'Copilot', '多模态', 'AI安全',
    # 科技公司/产品
    '字节跳动', '百度', '腾讯', '阿里', '华为', '微软', '谷歌',
    'Google', '苹果', 'Apple', 'iPhone', '特斯拉', 'TikTok',
    '字节', '小红书', 'DeepSeek', '豆包', '昆仑万维', '商汤',
    # 技术热词
    '算法', '模型', '智能', 'GPU', '芯片', '科技', '互联网',
    '数字', '数据', '网络', 'Token', 'Scaling', '涌现',
]


def is_ai_related(title: str) -> bool:
    """判断标题是否与 AI 相关"""
    title_lower = title.lower()
    return any(kw.lower() in title_lower for kw in AI_KEYWORDS)


# 数据源列表 — 按优先级排序
# 新增数据源：先创建 sources/xxx.py，然后在下面注册
SOURCES: list[type[BaseSource]] = []

# 来源注册表（动态导入）
IMPORTED_SOURCES: list[BaseSource] = []


def register_sources() -> None:
    """从 sources 包动态注册所有数据源"""
    from sources import zhihu, google_trends, hacker_news, baidu, weibo

    IMPORTED_SOURCES.clear()
    for src_cls in SOURCES:
        instance = src_cls()
        IMPORTED_SOURCES.append(instance)


def get_enabled_sources() -> list[BaseSource]:
    """获取所有已启用的数据源"""
    return [s for s in IMPORTED_SOURCES if s.info.enabled]


# 数据源元信息（用于 API 展示）
def get_sources_info() -> list[SourceInfo]:
    """获取所有数据源的基本信息"""
    return [s.info for s in IMPORTED_SOURCES]
