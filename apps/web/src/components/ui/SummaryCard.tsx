import { ReactNode } from 'react';

interface SummaryCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  colorClass?: string;
  onClick?: () => void;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
}

const gradientClasses = {
  coral: 'from-coral-400 to-coral-600',
  mint: 'from-mint-400 to-mint-600',
  sky: 'from-sky-400 to-sky-600',
  lavender: 'from-lavender-400 to-lavender-600',
  peach: 'from-peach-400 to-peach-600',
  lemon: 'from-lemon-400 to-lemon-600',
  rose: 'from-rose-400 to-rose-600',
  teal: 'from-teal-400 to-teal-600',
};

const bgClasses = {
  coral: 'bg-coral-100 dark:bg-coral-900/30',
  mint: 'bg-mint-100 dark:bg-mint-900/30',
  sky: 'bg-sky-100 dark:bg-sky-900/30',
  lavender: 'bg-lavender-100 dark:bg-lavender-900/30',
  peach: 'bg-peach-100 dark:bg-peach-900/30',
  lemon: 'bg-lemon-100 dark:bg-lemon-900/30',
  rose: 'bg-rose-100 dark:bg-rose-900/30',
  teal: 'bg-teal-100 dark:bg-teal-900/30',
};

const textClasses = {
  coral: 'text-coral-600 dark:text-coral-400',
  mint: 'text-mint-600 dark:text-mint-400',
  sky: 'text-sky-600 dark:text-sky-400',
  lavender: 'text-lavender-600 dark:text-lavender-400',
  peach: 'text-peach-600 dark:text-peach-400',
  lemon: 'text-lemon-600 dark:text-lemon-400',
  rose: 'text-rose-600 dark:text-rose-400',
  teal: 'text-teal-600 dark:text-teal-400',
};

export function SummaryCard({
  title,
  value,
  subtitle,
  icon,
  colorClass = 'sky',
  onClick,
  trend,
  trendValue,
}: SummaryCardProps) {
  const gradient = gradientClasses[colorClass as keyof typeof gradientClasses] || gradientClasses.sky;
  const bg = bgClasses[colorClass as keyof typeof bgClasses] || bgClasses.sky;
  const text = textClasses[colorClass as keyof typeof textClasses] || textClasses.sky;

  return (
    <button
      onClick={onClick}
      disabled={!onClick}
      className={`w-full p-4 rounded-2xl text-left transition-all duration-300 ${
        onClick ? 'hover:shadow-lg hover:scale-[1.02] cursor-pointer' : ''
      } ${bg}`}
    >
      <div className="flex items-center gap-3">
        {icon && (
          <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center text-white shadow-md`}>
            {icon}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">{title}</p>
          <div className="flex items-baseline gap-2">
            <p className={`text-2xl font-bold ${text}`}>{value}</p>
            {trend && trendValue && (
              <span className={`text-xs font-medium ${
                trend === 'up' ? 'text-success-500' :
                trend === 'down' ? 'text-danger-500' :
                'text-slate-400'
              }`}>
                {trend === 'up' ? '+' : trend === 'down' ? '-' : ''}{trendValue}
              </span>
            )}
          </div>
          {subtitle && (
            <p className="text-xs text-slate-400 dark:text-slate-500">{subtitle}</p>
          )}
        </div>
      </div>
    </button>
  );
}
