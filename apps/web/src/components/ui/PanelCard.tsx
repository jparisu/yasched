import { ReactNode } from 'react';
import { ChevronDown } from 'lucide-react';
import { useCollapse } from '../../lib/useCollapse';

interface PanelCardProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  action?: ReactNode;
  className?: string;
  variant?: 'default' | 'colorful';
  colorClass?: string;
  /** Stable id for remembering the collapsed state (defaults to the title). */
  collapseId?: string;
  /** Fill the grid cell and let the body scroll (used for equal-height rows). */
  fill?: boolean;
}

export function PanelCard({
  title,
  subtitle,
  children,
  action,
  className = '',
  variant = 'default',
  colorClass,
  collapseId,
  fill = false,
}: PanelCardProps) {
  const { collapsed, toggle } = useCollapse(`panel-${collapseId ?? title}`);
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

  const bgClass =
    variant === 'colorful' && colorClass
      ? colorVariants[colorClass] || ''
      : 'bg-white dark:bg-slate-800 border-slate-200/50 dark:border-slate-700';

  return (
    <div
      className={`panel-card rounded-2xl shadow-sm border overflow-hidden ${bgClass} ${
        fill && !collapsed ? 'h-full flex flex-col' : ''
      } ${className}`}
    >
      <button
        type="button"
        onClick={toggle}
        className="w-full px-4 py-3 border-b border-inherit flex items-center justify-between gap-2 text-left hover:bg-black/[0.02] dark:hover:bg-white/[0.03] flex-shrink-0"
      >
        <div className="flex items-center gap-2 min-w-0">
          <ChevronDown
            size={16}
            className={`text-slate-400 flex-shrink-0 transition-transform ${collapsed ? '-rotate-90' : ''}`}
          />
          <div className="min-w-0">
            <h3 className="font-semibold text-slate-800 dark:text-slate-100 truncate">{title}</h3>
            {subtitle && <p className="text-sm text-slate-500 dark:text-slate-400 truncate">{subtitle}</p>}
          </div>
        </div>
        {action && <div onClick={(e) => e.stopPropagation()}>{action}</div>}
      </button>
      {!collapsed && (
        <div className={fill ? 'p-4 flex-1 min-h-0 overflow-y-auto' : 'p-4'}>{children}</div>
      )}
    </div>
  );
}
