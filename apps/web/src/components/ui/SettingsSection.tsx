import { ReactNode } from 'react';
import { ChevronDown } from 'lucide-react';
import { useCollapse } from '../../lib/useCollapse';

interface SettingsSectionProps {
  title: string;
  description?: string;
  children: ReactNode;
}

export function SettingsSection({
  title,
  description,
  children,
}: SettingsSectionProps) {
  const { collapsed, toggle } = useCollapse(`settings-${title}`);
  return (
    <div className="card p-5">
      <button type="button" onClick={toggle} className="w-full mb-4 flex items-start gap-2 text-left">
        <ChevronDown
          size={18}
          className={`text-slate-400 mt-0.5 flex-shrink-0 transition-transform ${collapsed ? '-rotate-90' : ''}`}
        />
        <div>
          <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100">{title}</h3>
          {description && (
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{description}</p>
          )}
        </div>
      </button>
      {!collapsed && <div className="space-y-4">{children}</div>}
    </div>
  );
}

interface SettingsRowProps {
  label: string;
  description?: string;
  children: ReactNode;
}

export function SettingsRow({ label, description, children }: SettingsRowProps) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div className="flex-1">
        <p className="font-medium text-slate-700 dark:text-slate-200">{label}</p>
        {description && (
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {description}
          </p>
        )}
      </div>
      <div className="flex-shrink-0">{children}</div>
    </div>
  );
}
