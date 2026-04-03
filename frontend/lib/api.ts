import { NewsResponse, SortMode, Category } from '@/types/news';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchNews(params: {
  category?: Category | string;
  keyword?: string;
  sort?: SortMode;
  limit?: number;
  forceRefresh?: boolean;
}): Promise<NewsResponse> {
  const sp = new URLSearchParams();

  if (params.category && params.category !== '全部') sp.set('category', params.category);
  if (params.keyword) sp.set('keyword', params.keyword);
  if (params.sort) sp.set('sort', params.sort);
  if (params.limit) sp.set('limit', String(params.limit));
  if (params.forceRefresh) sp.set('force_refresh', 'true');

  const url = `${API_BASE}/api/news?${sp.toString()}`;
  const res = await fetch(url, { cache: 'no-store' });

  if (!res.ok) {
    throw new Error(`API 请求失败: ${res.status}`);
  }

  return res.json();
}

export async function refreshNews(): Promise<{ status: string; total: number }> {
  const res = await fetch(`${API_BASE}/api/refresh`, { method: 'POST' });
  if (!res.ok) throw new Error('刷新失败');
  return res.json();
}

export async function getSources() {
  const res = await fetch(`${API_BASE}/api/sources`, { cache: 'no-store' });
  if (!res.ok) throw new Error('获取来源失败');
  return res.json();
}

export async function getStatus() {
  const res = await fetch(`${API_BASE}/api/status`, { cache: 'no-store' });
  if (!res.ok) throw new Error('获取状态失败');
  return res.json();
}
