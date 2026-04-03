'use client';

import { formatAbsoluteTime } from '@/lib/utils';

interface FooterProps {
  fetchedAt: string | undefined;
  serverTime: string | undefined;
  cacheAge: number | undefined;
}

export default function Footer({ fetchedAt, serverTime, cacheAge }: FooterProps) {
  return (
    <footer className="mt-8 py-4 border-t border-gray-200 bg-white">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-gray-400">
          <div className="flex items-center gap-4">
            <span>数据来源：知乎 · 微博 · 百度 · Google Trends · Hacker News</span>
          </div>
          <div className="flex items-center gap-4">
            {fetchedAt && (
              <span>更新于 {formatAbsoluteTime(fetchedAt)}</span>
            )}
            {cacheAge !== undefined && (
              <span className="font-mono">缓存 {Math.floor(cacheAge / 60)} 分钟前</span>
            )}
            {serverTime && (
              <span>服务器时间 {formatAbsoluteTime(serverTime)}</span>
            )}
          </div>
        </div>
        <div className="mt-2 text-[10px] text-gray-300 text-center">
          内容来自各平台公开数据，仅供学习参考，如有侵权请联系删除
        </div>
      </div>
    </footer>
  );
}
