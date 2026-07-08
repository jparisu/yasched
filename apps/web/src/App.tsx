import { useState, useEffect } from 'react';
import { AppLayout } from './components/layout';
import {
  Statistics,
  Agenda,
  Calendar,
  TaskBoard,
  Focus,
  DatabaseGraph,
  SettingsPage,
} from './pages';
import { ViewMode, Settings as SettingsType } from './types';
import { defaultSettings } from './data/mockData';

function App() {
  const [currentView, setCurrentView] = useState<ViewMode>('statistics');
  const [settings, setSettings] = useState<SettingsType>(() => {
    const saved = localStorage.getItem('yasched-settings');
    if (saved) {
      try {
        return { ...defaultSettings, ...JSON.parse(saved) };
      } catch {
        return defaultSettings;
      }
    }
    return defaultSettings;
  });

  useEffect(() => {
    localStorage.setItem('yasched-settings', JSON.stringify(settings));
  }, [settings]);

  useEffect(() => {
    if (settings.theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', settings.theme);
  }, [settings.theme]);

  const handleUpdateSetting = <K extends keyof SettingsType>(
    key: K,
    value: SettingsType[K]
  ) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const handleThemeToggle = () => {
    handleUpdateSetting('theme', settings.theme === 'dark' ? 'light' : 'dark');
  };

  const handleUpdateSettings = (key: string, value: string) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const renderPage = () => {
    switch (currentView) {
      case 'statistics':
        return (
          <Statistics
            displayStyle={settings.displayStyle}
            density={settings.density}
            cardShape={settings.cardShape}
          />
        );
      case 'agenda':
        return (
          <Agenda
            displayStyle={settings.displayStyle}
            density={settings.density}
            cardShape={settings.cardShape}
            onUpdateSettings={handleUpdateSettings}
          />
        );
      case 'calendar':
        return (
          <Calendar
            displayStyle={settings.displayStyle}
            density={settings.density}
            cardShape={settings.cardShape}
            onUpdateSettings={handleUpdateSettings}
          />
        );
      case 'taskboard':
        return (
          <TaskBoard
            displayStyle={settings.displayStyle}
            density={settings.density}
            cardShape={settings.cardShape}
            onUpdateSettings={handleUpdateSettings}
          />
        );
      case 'focus':
        return (
          <Focus
            displayStyle={settings.displayStyle}
            density={settings.density}
            cardShape={settings.cardShape}
            onUpdateSettings={handleUpdateSettings}
          />
        );
      case 'graph':
        return (
          <DatabaseGraph
            displayStyle={settings.displayStyle}
            density={settings.density}
            cardShape={settings.cardShape}
            onUpdateSettings={handleUpdateSettings}
          />
        );
      case 'settings':
        return <SettingsPage settings={settings} onUpdateSetting={handleUpdateSetting} />;
      default:
        return <Statistics displayStyle={settings.displayStyle} density={settings.density} cardShape={settings.cardShape} />;
    }
  };

  return (
    <AppLayout
      currentView={currentView}
      onViewChange={setCurrentView}
      settings={settings}
      onThemeToggle={handleThemeToggle}
    >
      {renderPage()}
    </AppLayout>
  );
}

export default App;
