"""FT中文网爬虫 — 通过 Google News RSS 提取 FTChinese.com 内容

注意：Google News RSS 有一定延迟，且包含部分非新闻内容（如应用程序页面）。
如需更实时准确的数据，建议从中国内地网络访问 FT 官网。
"""

import logging
import httpx
import feedparser
from sources.base import BaseSource, SourceInfo, NewsItem
from core.normalizer import normalize_item

logger = logging.getLogger(__name__)

# Google News RSS — 搜索 ftchinese.com
FT_RSS_URL = (
    'https://news.google.com/rss/search?'
    'q=site:ftchinese.com&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'
)

# 排除噪音关键词（应用程序、工具类页面、汇总页）
NOISE_KEYWORDS = [
    '应用程序', 'iPad', 'iPhone', 'Android', 'App', '应用',
    '大全', 'RSS', '订阅', 'newsletter', '移动应用',
    '电子书', '版权', '关于我们', '档案', '文集', '编辑',
    '作者', '文章档案', '专题', ' podcast',
    'FT中文网 - ai.ftchinese.com',  # 子站非主文
]

# 必需关键词（提高新闻文章命中率）
NEWS_KEYWORDS = [
    '中国', '美国', '经济', '市场', '政策', 'AI', '贸易',
    '金融', '投资', '公司', '分析', '观点', '评论', '报告', '数据',
    '战争', '外交', '政治', '社会', '环境', '能源', '气候', '疫苗',
    '疫情', '增长', '衰退', '通胀', '央行', '美联储', '欧盟', '英国',
    '日本', '俄罗斯', '普京', '习近平', '拜登', '特朗普', '峰会',
    '制裁', '选举', '协议', '谈判', '军事', '科技', '芯片', '半导体',
    '企业', '产业', '监管', '债务', '人民币', '美元', '股市', '房价',
]


def _is_noise_title(title: str) -> bool:
    t = title.lower()
    for kw in NOISE_KEYWORDS:
        if kw.lower() in t:
            return True
    return False


def _is_news_title(title: str) -> bool:
    t = title.lower()
    count = sum(1 for kw in NEWS_KEYWORDS if kw.lower() in t)
    return count >= 1


class FtchineseSource(BaseSource):
    info = SourceInfo(
        source='ftchinese',
        name='FT中文网',
        region='CN',
        enabled=True,
        interval_seconds=3600,
    )

    def fetch(self) -> list[NewsItem]:
        items = []
        try:
            resp = httpx.get(
                FT_RSS_URL,
                timeout=8,
                verify=False,
                headers={'User-Agent': 'Mozilla/5.0'},
            )
            if resp.status_code != 200:
                logger.warning(f'[ftchinese] HTTP {resp.status_code}')
                return []

            feed = feedparser.parse(resp.text)
            raw_entries = feed.entries or []

        except Exception as e:
            logger.warning(f'[ftchinese] 抓取异常: {type(e).__name__}: {e}')
            return []

        for i, entry in enumerate(raw_entries[:50], start=1):
            title = entry.get('title', '').strip()
            link = entry.get('link', '')
            if not title or not link:
                continue

            # 过滤噪音页面，必须包含新闻关键词
            if _is_noise_title(title) or not _is_news_title(title):
                continue

            item = NewsItem(
                id=f'ftchinese_{hash(link) % 1000000}',
                title=title,
                url=link,
                source='ftchinese',
                source_name='FT中文网',
                source_region='CN',
                raw_score=max(0, (50 - i) * 1000),
                rank=i,
            )
            items.append(normalize_item(item))

            if len(items) >= 20:
                break

        return items
