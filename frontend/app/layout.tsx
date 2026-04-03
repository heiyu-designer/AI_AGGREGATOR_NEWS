import type { Metadata } from 'next';
import './globals.css';
import Providers from '@/components/Providers';

export const metadata: Metadata = {
  title: 'AI 热点聚合 — 国内外 AI 新闻一屏尽览',
  description: '聚合知乎、微博、GitHub、Hacker News 等平台的 AI 热点新闻',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
