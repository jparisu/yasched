import { useState } from 'react';
import { ChevronLeft } from 'lucide-react';
import { PanelId } from '../types';
import { CATEGORY_ORDER, NAV } from './nav';

interface Props {
  current: PanelId;
  onChange: (id: PanelId) => void;
}

export function Sidebar({ current, onChange }: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <aside
      className={`fixed left-0 top-0 h-full z-40 transition-all duration-300 ${
        expanded ? 'w-56' : 'w-16'
      } bg-gradient-to-b from-white to-slate-50 dark:from-slate-900 dark:to-slate-950 border-r border-slate-200/50 dark:border-slate-800 flex flex-col`}
    >
      <div className="flex items-center justify-between p-3 border-b border-slate-200/50 dark:border-slate-800">
        {expanded ? (
          <>
            <span className="font-bold text-lg bg-gradient-to-r from-sky-500 to-lavender-500 bg-clip-text text-transparent">
              yasched
            </span>
            <button
              onClick={() => setExpanded(false)}
              className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500"
            >
              <ChevronLeft size={18} />
            </button>
          </>
        ) : (
          <button
            onClick={() => setExpanded(true)}
            title="Expand"
            className="mx-auto w-8 h-8 rounded-lg bg-gradient-to-br from-sky-400 to-lavender-500 text-white font-bold flex items-center justify-center"
          >
            Y
          </button>
        )}
      </div>

      <nav className="flex-1 py-3 px-2 overflow-y-auto">
        {CATEGORY_ORDER.map((category, ci) => (
          <div key={category}>
            {ci > 0 && <div className="my-2 border-t border-slate-200/60 dark:border-slate-800" />}
            {NAV.filter((n) => n.category === category).map((item) => {
              const Icon = item.icon;
              const active = current === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onChange(item.id)}
                  title={item.label}
                  className={`w-full flex items-center gap-3 px-2 py-2.5 rounded-xl transition-colors relative ${
                    active
                      ? 'bg-slate-100 dark:bg-slate-800 shadow-sm'
                      : 'text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                  style={active ? { borderLeft: `3px solid ${item.color}` } : {}}
                >
                  <Icon size={20} style={{ color: active ? item.color : undefined }} />
                  {expanded && (
                    <span className="text-sm font-medium" style={{ color: active ? item.color : undefined }}>
                      {item.label}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </nav>
    </aside>
  );
}
