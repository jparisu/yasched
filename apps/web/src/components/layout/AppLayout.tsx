import { ViewMode, Settings } from '../../types';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';

interface AppLayoutProps {
  children: React.ReactNode;
  currentView: ViewMode;
  onViewChange: (view: ViewMode) => void;
  settings: Settings;
  onThemeToggle: () => void;
}

export function AppLayout({
  children,
  currentView,
  onViewChange,
  settings,
  onThemeToggle,
}: AppLayoutProps) {
  return (
    <div className={`min-h-screen ${settings.theme === 'dark' ? 'dark' : ''}`}>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
        <Sidebar
          currentView={currentView}
          onViewChange={onViewChange}
          isDark={settings.theme === 'dark'}
        />
        <div className="ml-16 min-h-screen">
          <TopBar
            currentView={currentView}
            settings={settings}
            onThemeToggle={onThemeToggle}
          />
          <main className="p-4 md:p-6">{children}</main>
        </div>
      </div>
    </div>
  );
}
