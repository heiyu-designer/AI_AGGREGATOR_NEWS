'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Loader2, AlertCircle, Search, RefreshCw, TrendingUp, Flame, Clock, Heart, Link2, CalendarDays } from 'lucide-react';
import { fetchNews } from '@/lib/api';
import { NewsItem, SortMode } from '@/types/news';

const WEEKDAY = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'] as const;

const FAVORITES_KEY = 'ai-news-favorites';

const PLATFORMS = [
  { source: 'zhihu', label: '知乎', icon: '💬', bg: 'bg-gradient-to-r from-blue-500 to-blue-600' },
  { source: 'toutiao', label: '今日头条', icon: '📰', bg: 'bg-gradient-to-r from-orange-500 to-orange-600' },
  { source: 'pengpai', label: '澎湃新闻', icon: '🌊', bg: 'bg-gradient-to-r from-cyan-500 to-cyan-600' },
  { source: '163news', label: '网易新闻', icon: '🎯', bg: 'bg-gradient-to-r from-blue-600 to-blue-700' },
  
  { source: 'github', icon: '⭐', label: 'GitHub', bg: 'bg-gradient-to-r from-gray-700 to-gray-800' },
  { source: 'toolify', label: 'Toolify.ai', icon: '🛠️', bg: 'bg-gradient-to-r from-pink-500 to-pink-600' },
  { source: 'twitter', label: 'X/Twitter', icon: '🐦', bg: 'bg-gradient-to-r from-gray-800 to-gray-900' },
  { source: 'youtube', label: 'YouTube', icon: '▶️', bg: 'bg-gradient-to-r from-red-600 to-red-700' },
  
  { source: 'weixin', label: '微信热文', icon: '💚', bg: 'bg-gradient-to-r from-green-500 to-green-600' },
  { source: 'hackernews', label: 'Hacker News', icon: '💻', bg: 'bg-gradient-to-r from-orange-500 to-orange-600' },
  { source: 'xinhua', label: '新华社', icon: '📡', bg: 'bg-gradient-to-r from-red-800 to-red-900' },
  { source: 'weibo', label: '微博热搜', icon: '🔥', bg: 'bg-gradient-to-r from-red-500 to-red-600' },
  
  { source: 'people', label: '人民网', icon: '🏛️', bg: 'bg-gradient-to-r from-red-700 to-red-800' },
  { source: 'baidu', label: '百度热搜', icon: '🔍', bg: 'bg-gradient-to-r from-blue-400 to-blue-500' },
  { source: 'kr36', label: '36氪', icon: '🚀', bg: 'bg-gradient-to-r from-purple-500 to-purple-600' },
  { source: 'ithome', label: 'IT之家', icon: '💻', bg: 'bg-gradient-to-r from-orange-400 to-red-500' },
  { source: 'qbitai', label: '量子位', icon: '⚛️', bg: 'bg-gradient-to-r from-cyan-500 to-blue-600' },
  { source: 'banyuetan', label: '半月谈', icon: '📚', bg: 'bg-gradient-to-r from-indigo-500 to-indigo-600' },
  { source: 'google_trends', label: 'Google Trends', icon: '🌐', bg: 'bg-gradient-to-r from-teal-500 to-teal-600' },
  { source: 'huggingface', label: 'Hugging Face', icon: '🤗', bg: 'bg-gradient-to-r from-yellow-400 to-orange-500' },
  { source: 'sspai', label: '少数派', icon: '✒️', bg: 'bg-gradient-to-r from-yellow-500 to-orange-500' },
  { source: 'jianshu', label: '简书', icon: '📝', bg: 'bg-gradient-to-r from-gray-500 to-gray-600' },
];

function loadFavorites(): Set<string> {
  if (typeof window === 'undefined') return new Set();
  try {
    const raw = localStorage.getItem(FAVORITES_KEY);
    return new Set(raw ? JSON.parse(raw) : []);
  } catch { return new Set(); }
}

function saveFavorites(favs: Set<string>) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(FAVORITES_KEY, JSON.stringify([...favs]));
}

export default function HomePage() {
  const [sort, setSort] = useState<SortMode>('hot');
  const [keyword, setKeyword] = useState('');
  const [favorites, setFavorites] = useState<Set<string>>(new Set());

  const today = useMemo(() => {
    const d = new Date();
    const month = d.getMonth() + 1;
    const day = d.getDate();
    const weekday = WEEKDAY[d.getDay()];
    return { month, day, weekday, label: `${month}月${day}日 ${weekday}` };
  }, []);

  useEffect(() => { setFavorites(loadFavorites()); }, []);

  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['news', sort],
    queryFn: () => fetchNews({ sort, limit: 500 }),
    staleTime: 30 * 1000,
    refetchInterval: 30 * 60 * 1000,
  });

  const handleRefresh = useCallback(() => refetch(), [refetch]);

  function toggleFavorite(item: NewsItem) {
    setFavorites((prev) => {
      const next = new Set(prev);
      if (next.has(item.id)) next.delete(item.id);
      else next.add(item.id);
      saveFavorites(next);
      return next;
    });
  }

  function getPlatformItems(source: string): NewsItem[] {
    const items = (data?.items || []).filter((i) => i.source === source);
    if (!keyword.trim()) return items;
    const kw = keyword.toLowerCase();
    return items.filter((i) => i.title.toLowerCase().includes(kw));
  }

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 overflow-hidden">
      {/* 顶部栏 */}
      <header className="flex-none bg-white/80 backdrop-blur-lg border-b border-white/20 shadow-lg shadow-black/5 z-50">
        <div className="h-14 px-4 flex items-center gap-4">
          {/* Logo */}
          <div className="flex items-center gap-2.5 flex-none">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-red-500 via-orange-500 to-yellow-500 flex items-center justify-center shadow-lg shadow-red-500/30">
              <TrendingUp size={16} className="text-white" />
            </div>
            <span className="text-base font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">AI 热点聚合</span>
          </div>

          {/* 搜索框 */}
          <div className="flex-1 flex items-center gap-2 bg-gray-100/80 rounded-xl px-4 py-2 max-w-md backdrop-blur-sm border border-gray-200/50">
            <Search size={14} className="text-gray-400 flex-shrink-0" />
            <input
              type="text"
              placeholder="搜索热点新闻..."
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              className="flex-1 text-sm bg-transparent outline-none placeholder:text-gray-400 text-gray-700"
            />
            {keyword && (
              <button
                onClick={() => setKeyword('')}
                className="text-gray-400 hover:text-gray-600 text-xs"
              >
                ✕
              </button>
            )}
          </div>

          {/* 右侧操作区 */}
          <div className="flex items-center gap-3 flex-none">
            {/* 日期标签 */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 shadow-sm">
              <CalendarDays size={13} className="text-indigo-500 flex-shrink-0" />
              <span className="text-xs font-semibold text-indigo-600 whitespace-nowrap">{today.label}</span>
            </div>

            {/* 排序切换 */}
            <div className="flex bg-gray-100 rounded-xl p-1 border border-gray-200/50 shadow-sm">
              <button
                onClick={() => setSort('hot')}
                className={`px-4 py-1.5 text-sm font-medium rounded-lg transition-all duration-200 flex items-center gap-1.5 ${
                  sort === 'hot'
                    ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg shadow-orange-500/30'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <Flame size={12} />
                热度
              </button>
              <button
                onClick={() => setSort('time')}
                className={`px-4 py-1.5 text-sm font-medium rounded-lg transition-all duration-200 flex items-center gap-1.5 ${
                  sort === 'time'
                    ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg shadow-blue-500/30'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <Clock size={12} />
                最新
              </button>
            </div>

            {/* 刷新按钮 */}
            <button
              onClick={handleRefresh}
              disabled={isFetching}
              className="p-2.5 rounded-xl bg-gray-100/80 hover:bg-gray-200/80 transition-all border border-gray-200/50 backdrop-blur-sm disabled:opacity-50 group shadow-sm"
              title="刷新"
            >
              <RefreshCw size={14} className={`text-gray-600 group-hover:text-gray-800 ${isFetching ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </header>

      {/* 内容区 */}
      <main className="flex-1 overflow-auto p-4">
        {/* 加载状态 */}
        {isLoading && (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <div className="relative">
              <Loader2 size={40} className="text-gray-300 animate-spin" />
              <div className="absolute inset-0 blur-xl bg-gradient-to-r from-blue-400 to-purple-400 opacity-30 animate-pulse rounded-full"></div>
            </div>
            <p className="text-sm text-gray-500 font-medium">正在聚合全网热点...</p>
          </div>
        )}

        {/* 错误状态 */}
        {isError && (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center">
              <AlertCircle size={28} className="text-red-500" />
            </div>
            <p className="text-sm text-red-500 font-medium">数据获取失败</p>
            <button 
              onClick={handleRefresh} 
              className="px-6 py-2.5 text-sm font-medium bg-gradient-to-r from-red-500 to-orange-500 text-white rounded-xl shadow-lg shadow-red-500/30 hover:shadow-xl hover:scale-105 transition-all"
            >
              重新加载
            </button>
          </div>
        )}

        {/* 平台卡片网格 */}
        {!isLoading && !isError && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {PLATFORMS.map((platform) => {
              const items = getPlatformItems(platform.source);
              if (items.length === 0) return null;

              return (
                <div 
                  key={platform.source} 
                  className="bg-white rounded-2xl border border-gray-100/50 flex flex-col overflow-hidden shadow-lg shadow-black/5 hover:shadow-xl hover:shadow-black/10 transition-all duration-300 hover:-translate-y-1"
                >
                  {/* 平台标题 */}
                  <div className={`px-4 py-2.5 ${platform.bg} flex items-center gap-2 flex-none`}>
                    <span className="text-sm">{platform.icon}</span>
                    <span className="text-sm font-semibold text-white truncate">{platform.label}</span>
                    <span className="ml-auto text-xs text-white/80 flex-none bg-white/20 px-2 py-0.5 rounded-full font-medium">
                      {items.length}
                    </span>
                  </div>

                  {/* 新闻列表 */}
                  <div className="h-[350px] overflow-y-auto divide-y divide-gray-50/80">
                    {items.slice(0, 10).map((item, index) => {
                      const isFav = favorites.has(item.id);
                      return (
                        <div
                          key={item.id}
                          className="flex items-center gap-2 px-3 py-2.5 hover:bg-gradient-to-r hover:from-gray-50 to-transparent transition-all group cursor-pointer"
                        >
                          {/* 序号 */}
                          <span className={`flex-none text-xs font-bold w-5 h-5 rounded-md flex items-center justify-center ${
                            index < 3 
                              ? 'bg-gradient-to-br from-orange-400 to-red-500 text-white shadow-sm' 
                              : 'bg-gray-100 text-gray-400'
                          }`}>
                            {index + 1}
                          </span>
                          
                          {/* 标题 */}
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex-1 text-sm text-gray-700 hover:text-transparent hover:bg-clip-text hover:bg-gradient-to-r hover:from-red-500 hover:to-orange-500 transition-all leading-relaxed line-clamp-2"
                          >
                            {item.title}
                          </a>

                          {/* 热度 */}
                          <span className="flex-none text-xs text-orange-500 font-semibold whitespace-nowrap bg-orange-50 px-1.5 py-0.5 rounded">
                            {item.hotScore}
                          </span>

                          {/* 操作按钮 */}
                          <div className="flex-shrink-0 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={(e) => { e.preventDefault(); toggleFavorite(item); }}
                              className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
                              title={isFav ? "取消收藏" : "收藏"}
                            >
                              {isFav ? (
                                <Heart size={12} className="text-red-500 fill-red-500" />
                              ) : (
                                <Heart size={12} className="text-gray-400" />
                              )}
                            </button>
                            <a
                              href={item.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              onClick={(e) => e.stopPropagation()}
                              className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
                              title="在新窗口打开"
                            >
                              <Link2 size={12} className="text-gray-400" />
                            </a>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* 空状态 */}
        {!isLoading && !isError && PLATFORMS.every((p) => getPlatformItems(p.source).length === 0) && (
          <div className="flex flex-col items-center justify-center h-full gap-3">
            <div className="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center">
              <Search size={32} className="text-gray-300" />
            </div>
            <p className="text-base text-gray-500 font-medium">未找到相关新闻</p>
            <p className="text-sm text-gray-400">试试调整搜索条件</p>
          </div>
        )}
      </main>

      {/* 底部状态栏 */}
      {!isLoading && !isError && (
        <div className="flex-none h-10 px-6 flex items-center justify-between text-xs text-gray-400 bg-white/60 backdrop-blur-lg border-t border-white/20">
          <div className="flex items-center gap-2">
            <span className="font-medium text-gray-500">共</span>
            <span className="font-bold text-orange-500">{data?.items?.length || 0}</span>
            <span className="font-medium text-gray-500">条热点</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-gray-300">|</span>
            <span className="hover:text-gray-500 transition-colors cursor-default">知乎</span>
            <span className="text-gray-300">·</span>
            <span className="hover:text-gray-500 transition-colors cursor-default">微博</span>
            <span className="text-gray-300">·</span>
            <span className="hover:text-gray-500 transition-colors cursor-default">头条</span>
            <span className="text-gray-300">·</span>
            <span className="hover:text-gray-500 transition-colors cursor-default">百度</span>
            <span className="text-gray-300">·</span>
            <span className="hover:text-gray-500 transition-colors cursor-default">36氪</span>
            <span className="text-gray-300">·</span>
            <span className="hover:text-gray-500 transition-colors cursor-default">GitHub</span>
          </div>
        </div>
      )}
    </div>
  );
}