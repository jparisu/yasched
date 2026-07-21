import { useState } from 'react';
import {
  BarChart3,
  BookOpen,
  Calendar,
  CalendarClock,
  Kanban,
  Focus,
  Share2,
  Boxes,
  Settings,
  ChevronLeft,
} from 'lucide-react';
import { ViewMode } from '../../types';

interface SidebarProps {
  currentView: ViewMode;
  onViewChange: (view: ViewMode) => void;
  isDark: boolean;
}

interface NavItem {
  id: ViewMode;
  label: string;
  icon: React.ReactNode;
  color: string;
}

const navItems: NavItem[] = [
  { id: 'statistics', label: 'Dashboard', icon: <BarChart3 size={20} />, color: '#3b82f6' },
  { id: 'agenda', label: 'Agenda', icon: <BookOpen size={20} />, color: '#f59e0b' },
  { id: 'calendar', label: 'Calendar', icon: <Calendar size={20} />, color: '#22c55e' },
  { id: 'weekly', label: 'Weekly View', icon: <CalendarClock size={20} />, color: '#14b8a6' },
  { id: 'taskboard', label: 'Task Board', icon: <Kanban size={20} />, color: '#8b5cf6' },
  { id: 'focus', label: 'Focus', icon: <Focus size={20} />, color: '#06b6d4' },
  { id: 'graph', label: 'Database Graph', icon: <Share2 size={20} />, color: '#ec4899' },
  { id: 'element', label: 'Element', icon: <Boxes size={20} />, color: '#f43f5e' },
  { id: 'settings', label: 'Settings', icon: <Settings size={20} />, color: '#64748b' },
];

export function Sidebar({ currentView, onViewChange }: SidebarProps) {
  const [expanded, setExpanded] = useState(false);
  const [hoveredItem, setHoveredItem] = useState<ViewMode | null>(null);

  return (
    <aside
      className={`fixed left-0 top-0 h-full z-40 transition-all duration-300 ${
        expanded ? 'w-56' : 'w-16'
      } bg-gradient-to-b from-white to-slate-50 dark:from-slate-900 dark:to-slate-950 border-r border-slate-200/50 dark:border-slate-800 flex flex-col`}
    >
      <div className="flex items-center justify-between p-3 border-b border-slate-200/50 dark:border-slate-800">
        {expanded ? (
          <>
            <div className="flex items-center gap-2 min-w-0">
              <img src="/brand.png" alt="yasched" className="w-8 h-8 flex-shrink-0" />
              <span className="font-bold text-lg bg-gradient-to-r from-sky-500 to-lavender-500 bg-clip-text text-transparent truncate">
                yasched
              </span>
            </div>
            <button
              onClick={() => setExpanded(false)}
              className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 transition-colors ml-auto"
            >
              <ChevronLeft size={18} />
            </button>
          </>
        ) : (
          // Collapsed: the brand icon itself expands the sidebar.
          <button
            onClick={() => setExpanded(true)}
            title="Expand"
            className="mx-auto p-1 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <img src="/brand.png" alt="yasched" className="w-8 h-8" />
          </button>
        )}
      </div>

      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = currentView === item.id;
          const isHovered = hoveredItem === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              onMouseEnter={() => setHoveredItem(item.id)}
              onMouseLeave={() => setHoveredItem(null)}
              className={`w-full flex items-center gap-3 px-2 py-3 rounded-xl transition-all duration-200 relative ${
                isActive
                  ? 'bg-gradient-to-r from-slate-100 to-slate-50 dark:from-slate-800 dark:to-slate-900 shadow-md'
                  : 'text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
              style={isActive ? { borderLeft: `3px solid ${item.color}` } : {}}
            >
              <span
                className={`transition-all duration-200 ${
                  isActive ? 'scale-110' : ''
                }`}
                style={{ color: isActive ? item.color : undefined }}
              >
                {item.icon}
              </span>
              {expanded && (
                <span className="font-medium text-sm" style={{ color: isActive ? item.color : undefined }}>
                  {item.label}
                </span>
              )}
              {!expanded && isHovered && !isActive && (
                <div className="absolute left-full ml-3 px-3 py-2 bg-gradient-to-r from-slate-800 to-slate-700 text-white text-sm rounded-lg whitespace-nowrap shadow-lg z-50">
                  {item.label}
                  <div className="absolute right-full top-1/2 -translate-y-1/2 border-8 border-transparent border-r-slate-800" />
                </div>
              )}
            </button>
          );
        })}
      </nav>

      <div className="p-3 border-t border-slate-200/50 dark:border-slate-800">
        <div className={`flex items-center ${expanded ? 'gap-3' : 'justify-center'}`}>
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-coral-400 to-lavender-500 flex items-center justify-center text-white font-bold shadow-md">
            Y
          </div>
          {expanded && (
            <div className="text-left">
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">
                Your Space
              </p>
              <p className="text-xs text-slate-400">
                Free Plan
              </p>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
