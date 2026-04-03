'use client';

import { RefreshCw, Zap } from 'lucide-react';

interface HeaderProps {
  keyword: string;
  onKeywordChange: (kw: string) => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export default function Header({
  keyword,
  onKeywordChange,
  onRefresh,
  isRefreshing,
}: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-4">
        {/* Logo */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
            <Zap size={15} className="text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-gray-900 leading-tight tracking-wide">AI 热点聚合</h1>
            <p className="text-[10px] text-gray-400 leading-tight">AI News</p>
          </div>
        </div>

        {/* 搜索框 */}
        <div className="flex-1 max-w-xs">
          <input
            type="text"
            placeholder="搜索 AI 热点..."
            value={keyword}
            onChange={(e) => onKeywordChange(e.target.value)}
            className="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-lg
                       focus:outline-none focus:ring-2 focus:ring-red-400 focus:border-transparent
                       placeholder:text-gray-400 transition-all bg-gray-50"
          />
        </div>

        {/* 刷新按钮 */}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium
                     text-gray-500 hover:text-gray-800 hover:bg-gray-100
                     rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed
                     flex-shrink-0 border border-gray-200"
        >
          <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
          <span className="hidden sm:inline text-xs">{isRefreshing ? '刷新中' : '刷新'}</span>
        </button>
      </div>
    </header>
  );
}
