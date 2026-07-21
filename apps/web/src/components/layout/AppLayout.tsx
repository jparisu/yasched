import { ViewMode, Settings } from '../../types';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { ValidationBanner } from '../ui/ValidationBanner';

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
      <div className="app-bg min-h-screen">
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
          <main className="p-4 md:p-6" data-view={currentView}>
            <ValidationBanner />
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
