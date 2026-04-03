import { formatDistanceToNow } from 'date-fns';
import { zhCN, enUS } from 'date-fns/locale';
import { Category } from '@/types/news';

export function formatTimeAgo(isoString: string | undefined): string {
  if (!isoString) return '';
  try {
    const date = new Date(isoString);
    return formatDistanceToNow(date, { addSuffix: true, locale: zhCN });
  } catch {
    return '';
  }
}

export function formatAbsoluteTime(isoString: string | undefined): string {
  if (!isoString) return '';
  try {
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return '';
  }
}

const CATEGORY_COLORS: Record<string, string> = {
  'AI模型': 'bg-purple-100 text-purple-700',
  'AI产品': 'bg-green-100 text-green-700',
  '学术论文': 'bg-blue-100 text-blue-700',
  '产业动态': 'bg-orange-100 text-orange-700',
  'AI技术': 'bg-teal-100 text-teal-700',
};

const SOURCE_COLORS: Record<string, string> = {
  CN: 'bg-red-100 text-red-700',
  INT: 'bg-blue-100 text-blue-700',
};

export function getCategoryColor(category: string | undefined): string {
  if (!category) return 'bg-gray-100 text-gray-600';
  return CATEGORY_COLORS[category] || 'bg-gray-100 text-gray-600';
}

export function getRegionColor(region: string): string {
  return SOURCE_COLORS[region] || 'bg-gray-100 text-gray-600';
}

export function cn(...classes: (string | undefined | false)[]): string {
  return classes.filter(Boolean).join(' ');
}
