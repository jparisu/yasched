import { useState, useEffect } from 'react';
import { AppLayout } from './components/layout';
import {
  Statistics,
  Agenda,
  Calendar,
  WeekTimetable,
  TaskBoard,
  Focus,
  DatabaseGraph,
  ElementPage,
  SettingsPage,
} from './pages';
import { ViewMode } from './types';
import { useData } from './data/DataContext';
import { useElement } from './data/ElementContext';
import { useSettings } from './data/SettingsContext';

function App() {
  const { loading, error, reload } = useData();
  const { navSeq } = useElement();
  const { settings, updateSetting } = useSettings();
  const [currentView, setCurrentView] = useState<ViewMode>(() => {
    const saved = localStorage.getItem('yasched-view');
    const views: ViewMode[] = [
      'statistics', 'agenda', 'calendar', 'weekly',
      'taskboard', 'focus', 'graph', 'element', 'settings',
    ];
    return views.includes(saved as ViewMode) ? (saved as ViewMode) : 'statistics';
  });

  // Opening an element (double-click anywhere) navigates to the Element page.
  useEffect(() => {
    if (navSeq > 0) setCurrentView('element');
  }, [navSeq]);

  useEffect(() => {
    localStorage.setItem('yasched-view', currentView);
  }, [currentView]);

  const handleThemeToggle = () => {
    updateSetting('theme', settings.theme === 'dark' ? 'light' : 'dark');
  };

  // Each panel manages its own View/zoom via usePanelConfig (persisted per panel),
  // so panels no longer share a global display setting.
  const renderPage = () => {
    switch (currentView) {
      case 'statistics':
        return <Statistics />;
      case 'agenda':
        return <Agenda />;
      case 'calendar':
        return <Calendar />;
      case 'weekly':
        return <WeekTimetable />;
      case 'taskboard':
        return <TaskBoard />;
      case 'focus':
        return <Focus />;
      case 'graph':
        return <DatabaseGraph />;
      case 'element':
        return <ElementPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <Statistics />;
    }
  };

  return (
    <AppLayout
      currentView={currentView}
      onViewChange={setCurrentView}
      settings={settings}
      onThemeToggle={handleThemeToggle}
    >
      {error ? (
        <div className="flex flex-col items-center justify-center h-full gap-4 text-center p-8">
          <p className="text-lg font-semibold text-coral-600 dark:text-coral-400">
            Could not load your agenda
          </p>
          <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md">{error}</p>
          <button
            onClick={reload}
            className="px-4 py-2 rounded-lg bg-sky-500 text-white text-sm font-medium hover:bg-sky-600"
          >
            Retry
          </button>
        </div>
      ) : loading ? (
        <div className="flex items-center justify-center h-full text-slate-400">Loading…</div>
      ) : (
        renderPage()
      )}
    </AppLayout>
  );
}

export default App;
