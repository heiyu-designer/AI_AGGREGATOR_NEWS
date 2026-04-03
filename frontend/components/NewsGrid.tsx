'use client';

import { ExternalLink, Bookmark, BookmarkCheck, TrendingUp } from 'lucide-react';
import { NewsItem } from '@/types/news';
import { formatTimeAgo } from '@/lib/utils';

interface NewsGridProps {
  items: NewsItem[];
  onToggleFavorite: (item: NewsItem) => void;
  favorites: Set<string>;
}

const CATEGORY_COLORS: Record<string, string> = {
  'AI模型': 'bg-purple-100 text-purple-700 border-purple-200',
  'AI产品': 'bg-green-100 text-green-700 border-green-200',
  '学术论文': 'bg-blue-100 text-blue-700 border-blue-200',
  '产业动态': 'bg-orange-100 text-orange-700 border-orange-200',
  'AI技术': 'bg-teal-100 text-teal-700 border-teal-200',
};

function HotBar({ score }: { score: number }) {
  return (
    <div className="w-full h-0.5 bg-gray-100 rounded-full overflow-hidden mt-2">
      <div
        className="h-full rounded-full transition-all duration-500"
        style={{
          width: `${Math.min(score, 100)}%`,
          background: score > 80
            ? 'linear-gradient(to right, #f97316, #ef4444)'
            : score > 50
            ? 'linear-gradient(to right, #f97316, #f59e0b)'
            : 'linear-gradient(to right, #94a3b8, #64748b)',
        }}
      />
    </div>
  );
}

export default function NewsGrid({ items, onToggleFavorite, favorites }: NewsGridProps) {
  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center">
          <TrendingUp size={24} className="text-gray-300" />
        </div>
        <p className="text-sm text-gray-400">暂无数据</p>
        <p className="text-xs text-gray-300">该平台暂无 AI 相关热点</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
      {items.map((item, index) => {
        const isFavorite = favorites.has(item.id);
        const catColor = item.category ? CATEGORY_COLORS[item.category] : 'bg-gray-100 text-gray-500 border-gray-200';

        return (
          <article
            key={item.id}
            className="bg-white rounded-xl border border-gray-100 p-4 hover:border-gray-200 hover:shadow-sm transition-all cursor-pointer group relative animate-fade-in-up"
            style={{ animationDelay: `${index * 20}ms` }}
          >
            {/* 顶部行：排名 + 分类 + 来源 */}
            <div className="flex items-center gap-2 mb-2">
              {/* 排名 */}
              <span className="flex-shrink-0 w-6 h-6 rounded bg-gray-100 flex items-center justify-center">
                <span className="text-[10px] font-mono font-bold text-gray-400">{index + 1}</span>
              </span>

              {/* 分类标签 */}
              {item.category && (
                <span className={`inline-block text-[10px] px-1.5 py-0.5 rounded font-medium border ${catColor}`}>
                  {item.category}
                </span>
              )}

              {/* 热度分 */}
              {item.hotScore > 0 && (
                <span className="flex-shrink-0 flex items-center gap-0.5 text-[10px] text-orange-500 font-medium">
                  <TrendingUp size={9} />
                  {item.hotScore}
                </span>
              )}

              {/* 来源 */}
              <span className="ml-auto text-[10px] text-gray-400">{item.sourceName}</span>
            </div>

            {/* 标题 */}
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block mb-2"
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-sm font-medium text-gray-900 leading-snug line-clamp-2 group-hover:text-red-600 transition-colors">
                {item.title}
              </h2>
            </a>

            {/* 底部行：时间 + 操作 */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-[11px] text-gray-400">
                {item.publishedAt && (
                  <span>{formatTimeAgo(item.publishedAt)}</span>
                )}
                {item.rawScore && item.rawScore > 0 && (
                  <span className="font-mono hidden sm:inline">热度 {item.hotScore}</span>
                )}
              </div>

              <div className="flex items-center gap-1">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleFavorite(item);
                  }}
                  className="p-1 rounded hover:bg-gray-100 transition-colors"
                  title={isFavorite ? '取消收藏' : '收藏'}
                >
                  {isFavorite ? (
                    <BookmarkCheck size={13} className="text-red-500" />
                  ) : (
                    <Bookmark size={13} className="text-gray-300 group-hover:text-gray-400" />
                  )}
                </button>
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="p-1 rounded hover:bg-gray-100 transition-colors"
                  title="打开原文"
                >
                  <ExternalLink size={13} className="text-gray-300 group-hover:text-gray-500" />
                </a>
              </div>
            </div>

            {/* 热度条 */}
            <HotBar score={item.hotScore} />
          </article>
        );
      })}
    </div>
  );
}
