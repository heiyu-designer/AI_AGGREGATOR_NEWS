export interface NewsItem {
  id: string;
  title: string;
  summary?: string;
  url: string;
  source: string;
  sourceName: string;
  sourceRegion: 'CN' | 'INT';
  category?: string;
  hotScore: number;
  rawScore?: number;
  rank?: number;
  publishedAt?: string;
  fetchedAt: string;
  imageUrl?: string;
  tags?: string[];
}

export interface NewsResponse {
  items: NewsItem[];
  total: number;
  fetchedAt: string;
  sources: SourceInfo[];
}

export interface SourceInfo {
  source: string;
  name: string;
  region: 'CN' | 'INT';
  enabled: boolean;
  itemCount: number;
}

/** 分类 */
export type Category = '全部' | 'AI模型' | 'AI产品' | '学术论文' | '产业动态' | 'AI技术';

/** 平台 */
export type Platform = '全部' | 'zhihu' | 'weibo' | 'toutiao' | 'baidu' | 'pengpai' | 'kr36' | 'people' | 'xinhua' | 'banyuetan' | 'weixin' | '163news' | 'github' | 'hackernews' | 'google_trends' | 'toolify' | 'twitter';

/** 排序方式 */
export type SortMode = 'hot' | 'time';
