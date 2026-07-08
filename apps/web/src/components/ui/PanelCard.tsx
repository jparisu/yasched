import { ReactNode } from 'react';

interface PanelCardProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  action?: ReactNode;
  className?: string;
  variant?: 'default' | 'colorful';
  colorClass?: string;
}

export function PanelCard({
  title,
  subtitle,
  children,
  action,
  className = '',
  variant = 'default',
  colorClass,
}: PanelCardProps) {
  const colorVariants: Record<string, string> = {
    coral: 'bg-coral-50 dark:bg-coral-900/20 border-coral-200 dark:border-coral-800',
    mint: 'bg-mint-50 dark:bg-mint-900/20 border-mint-200 dark:border-mint-800',
    sky: 'bg-sky-50 dark:bg-sky-900/20 border-sky-200 dark:border-sky-800',
    lavender: 'bg-lavender-50 dark:bg-lavender-900/20 border-lavender-200 dark:border-lavender-800',
    peach: 'bg-peach-50 dark:bg-peach-900/20 border-peach-200 dark:border-peach-800',
    lemon: 'bg-lemon-50 dark:bg-lemon-900/20 border-lemon-200 dark:border-lemon-800',
    rose: 'bg-rose-50 dark:bg-rose-900/20 border-rose-200 dark:border-rose-800',
    teal: 'bg-teal-50 dark:bg-teal-900/20 border-teal-200 dark:border-teal-800',
  };

  const bgClass = variant === 'colorful' && colorClass
    ? colorVariants[colorClass] || ''
    : 'bg-white dark:bg-slate-800 border-slate-200/50 dark:border-slate-700';

  return (
    <div className={`rounded-2xl shadow-sm border overflow-hidden ${bgClass} ${className}`}>
      <div className="px-4 py-3 border-b border-inherit flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-slate-800 dark:text-slate-100">
            {title}
          </h3>
          {subtitle && (
            <p className="text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>
          )}
        </div>
        {action && <div>{action}</div>}
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
}
