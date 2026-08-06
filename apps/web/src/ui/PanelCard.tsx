import { ReactNode, useState } from 'react';
import { ChevronDown } from 'lucide-react';

interface PanelCardProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  collapsible?: boolean;
  defaultCollapsed?: boolean;
  collapseId?: string;
}

export function PanelCard({
  title,
  subtitle,
  action,
  children,
  className = '',
  collapsible = true,
  defaultCollapsed = false,
  collapseId,
}: PanelCardProps) {
  const key = collapseId ? `panel-collapsed-${collapseId}` : undefined;
  const [collapsed, setCollapsed] = useState<boolean>(() => {
    if (key) {
      const saved = localStorage.getItem(key);
      if (saved != null) return saved === '1';
    }
    return defaultCollapsed;
  });

  const toggle = () => {
    setCollapsed((prev) => {
      const next = !prev;
      if (key) localStorage.setItem(key, next ? '1' : '0');
      return next;
    });
  };

  return (
    <div
      className={`panel-card rounded-2xl shadow-sm border overflow-hidden bg-white/85 dark:bg-slate-800/80 backdrop-blur-sm border-slate-200/60 dark:border-slate-700 ${className}`}
    >
      <div className="w-full px-4 py-3 border-b border-slate-200/60 dark:border-slate-700 flex items-center justify-between gap-2">
        <button
          type="button"
          onClick={collapsible ? toggle : undefined}
          className="flex items-center gap-2 min-w-0 text-left flex-1"
        >
          {collapsible && (
            <ChevronDown
              size={16}
              className={`text-slate-400 flex-shrink-0 transition-transform ${
                collapsed ? '-rotate-90' : ''
              }`}
            />
          )}
          <div className="min-w-0">
            <h3 className="font-semibold text-slate-800 dark:text-slate-100 truncate">{title}</h3>
            {subtitle && (
              <p className="text-sm text-slate-500 dark:text-slate-400 truncate">{subtitle}</p>
            )}
          </div>
        </button>
        {action && <div className="flex-shrink-0">{action}</div>}
      </div>
      {!collapsed && <div className="p-4">{children}</div>}
    </div>
  );
}
