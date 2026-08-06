/* eslint-disable react-refresh/only-export-components -- provider + hook colocated by design */
import { createContext, ReactNode, useContext, useEffect, useState } from 'react';

export type Theme = 'light' | 'dark';
export type AppStyle = 'simple' | 'programmer' | 'office' | 'educational';
export type Density = 'compact' | 'comfortable' | 'spacious';
export type ElementViewMode = 'card' | 'line' | 'point';

export interface Settings {
  theme: Theme;
  style: AppStyle;
  density: Density;
  weekStartsOnMonday: boolean;
  /** Save element edits automatically on change / when leaving the editor. */
  autoSave: boolean;
}

export const defaultSettings: Settings = {
  theme: 'light',
  style: 'simple',
  density: 'comfortable',
  weekStartsOnMonday: true,
  autoSave: true,
};

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
        return { ...defaultSettings, ...(JSON.parse(saved) as Partial<Settings>) };
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
    document.documentElement.classList.toggle('dark', settings.theme === 'dark');
  }, [settings.theme]);

  useEffect(() => {
    document.documentElement.setAttribute('data-style', settings.style);
  }, [settings.style]);

  // Density scales the root font size, so all rem-based spacing/text follows.
  useEffect(() => {
    document.documentElement.setAttribute('data-density', settings.density);
  }, [settings.density]);

  const updateSetting = <K extends keyof Settings>(key: K, value: Settings[K]) =>
    setSettings((prev) => ({ ...prev, [key]: value }));

  return (
    <SettingsContext.Provider
      value={{ settings, updateSetting, reset: () => setSettings(defaultSettings) }}
    >
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings(): SettingsApi {
  return useContext(SettingsContext);
}
