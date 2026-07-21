/* eslint-disable react-refresh/only-export-components -- provider + hook colocated by design */
import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { Settings } from '../types';
import { defaultSettings } from './mockData';

interface SettingsApi {
  settings: Settings;
  updateSetting: <K extends keyof Settings>(key: K, value: Settings[K]) => void;
  reset: () => void;
}

const SettingsContext = createContext<SettingsApi>({
  settings: defaultSettings,
  updateSetting: () => {},
  reset: () => {},
});

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<Settings>(() => {
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

  // Theme + style are global document attributes.
  useEffect(() => {
    document.documentElement.classList.toggle('dark', settings.theme === 'dark');
    localStorage.setItem('theme', settings.theme);
  }, [settings.theme]);

  useEffect(() => {
    document.documentElement.setAttribute('data-style', settings.style);
  }, [settings.style]);

  const updateSetting = <K extends keyof Settings>(key: K, value: Settings[K]) =>
    setSettings((prev) => ({ ...prev, [key]: value }));

  return (
    <SettingsContext.Provider value={{ settings, updateSetting, reset: () => setSettings(defaultSettings) }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings(): SettingsApi {
  return useContext(SettingsContext);
}
