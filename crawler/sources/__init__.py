"""数据源注册表 — 所有可用数据源在此注册"""

from sources.base import BaseSource

# 注册爬虫模块（新增来源时在此添加）
from sources import zhihu
from sources import weibo
from sources import kr36
from sources import baidu
from sources import github_trending
from sources import hacker_news
from sources import pengpai
from sources import toutiao
from sources import google_trends
from sources import people
from sources import xinhua
from sources import netease
from sources import banyuetan
from sources import weixin
from sources import toolify
from sources import twitter
from sources import youtube
from sources import shaoshupai
from sources import jianshu

# 来源列表 — 按优先级和重要性排序
# 格式：(SourceClass, 是否启用, 采集间隔秒数)
SOURCE_REGISTRY: list[tuple[type[BaseSource], bool, int]] = [
    (zhihu.ZhihuSource, True, 1800),              # 知乎热榜
    (weibo.WeiboSource, True, 1800),              # 微博热搜
    (toutiao.ToutiaoSource, True, 1800),          # 今日头条
    (baidu.BaiduSource, True, 1800),               # 百度热搜
    (pengpai.PengpaiSource, True, 1800),           # 澎湃新闻
    (kr36.Kr36Source, True, 1800),                 # 36氪
    (people.PeopleSource, True, 1800),             # 人民网
    (xinhua.XinhuaSource, True, 1800),             # 新华社
    (banyuetan.BanyuetanSource, True, 1800),       # 半月谈
    (weixin.WeixinSource, True, 1800),             # 微信热文
    (netease.NeteaseSource, True, 1800),       # 网易新闻
    (github_trending.GitHubTrendingSource, True, 3600),  # GitHub Trending
    (hacker_news.HackerNewsSource, True, 1800),    # Hacker News
    (google_trends.GoogleTrendsSource, True, 3600), # Google Trends
    (toolify.ToolifySource, True, 3600),          # Toolify.ai
    (twitter.TwitterSource, True, 1800),           # X/Twitter
    (youtube.YouTubeSource, True, 1800),            # YouTube
    (shaoshupai.ShaoshupaiSource, True, 1800),     # 少数派
    (jianshu.JianshuSource, True, 1800),           # 简书
]


def get_all_sources() -> list[BaseSource]:
    """返回所有已注册的数据源实例"""
    sources = []
    for cls, enabled, interval in SOURCE_REGISTRY:
        instance = cls()
        instance.info.enabled = enabled
        instance.info.interval_seconds = interval
        sources.append(instance)
    return sources


def get_enabled_sources() -> list[BaseSource]:
    """返回所有已启用的数据源"""
    return [s for s in get_all_sources() if s.info.enabled]
