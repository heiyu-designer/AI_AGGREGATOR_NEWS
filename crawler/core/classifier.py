"""内容分类器 — 基于关键词规则对新闻进行分类"""

CATEGORY_KEYWORDS = {
    'AI模型': [
        '大模型', 'GPT', 'LLM', 'ChatGPT', 'Gemini', 'Claude',
        'Sora', '文心', '通义', 'Kimi', '智谱', 'Mistral',
        'Llama', 'Grok', 'Qwen', '豆包', '盘古', '混元',
        'MoE', 'Transformer', '参数', '训练', '微调',
    ],
    'AI产品': [
        '发布', '上线', '推出', '产品', '工具', '应用',
        'App', '网站', '功能', '更新', '版本', '开放',
        '内测', '公测', 'Beta', '正式版',
    ],
    '学术论文': [
        '论文', '研究', 'arXiv', 'benchmark', '基准',
        'ACL', 'NeurIPS', 'ICML', 'ICLR', 'AAAI',
        'EMNLP', 'CVPR', '证明', '实验', 'arxiv',
    ],
    '产业动态': [
        '融资', '收购', '合作', '裁员', '财报', '上市',
        '政策', '监管', '投资', '估值', '独角兽', ' IPO',
        '禁止', '限制', '欧盟', '美国', '中国',
    ],
    'AI技术': [
        '训练', 'RLHF', 'Prompt', 'RAG', 'Agent', '幻觉',
        '推理', '部署', '蒸馏', '量化', '优化', '检索',
        '向量', 'embedding', 'token', '涌现', '安全',
    ],
}


def classify_news(title: str) -> str | None:
    """根据标题关键词判断新闻分类，返回分类名或 None"""
    title_lower = title.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in title_lower:
                return category

    return None


def extract_tags(title: str) -> list[str]:
    """从标题中提取 AI 相关关键词作为标签"""
    title_lower = title.lower()
    tags = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in title_lower:
                if kw not in tags:
                    tags.append(kw)

    return tags[:5]  # 最多 5 个标签
