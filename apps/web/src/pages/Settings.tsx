import { SettingsSection, SettingsRow, ThemeToggle, ToggleGroup } from '../components/ui';
import type { Settings } from '../types';
import { Density, DisplayStyle, CalendarView, ColumnMode, RowMode, DayOfWeek, CardShape } from '../types';

interface SettingsPageProps {
  settings: Settings;
  onUpdateSetting: <K extends keyof Settings>(key: K, value: Settings[K]) => void;
}

export function SettingsPage({ settings, onUpdateSetting }: SettingsPageProps) {
  return (
    <div className="max-w-3xl space-y-6">
      <SettingsSection title="Appearance" description="Customize how yasched looks">
        <SettingsRow label="Theme" description="Choose between light and dark mode">
          <ThemeToggle
            isDark={settings.theme === 'dark'}
            onToggle={() => onUpdateSetting('theme', settings.theme === 'dark' ? 'light' : 'dark')}
          />
        </SettingsRow>

        <SettingsRow label="Accent Color" description="Your preferred color accent">
          <div className="flex items-center gap-2">
            {['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4'].map(color => (
              <button
                key={color}
                onClick={() => onUpdateSetting('accentColor', color)}
                className={`w-8 h-8 rounded-full transition-all ${
                  settings.accentColor === color ? 'ring-2 ring-offset-2 ring-slate-400 scale-110' : ''
                }`}
                style={{ backgroundColor: color }}
              />
            ))}
          </div>
        </SettingsRow>
      </SettingsSection>

      <SettingsSection title="Display Settings" description="Configure how items appear across all pages">
        <SettingsRow label="Display Style" description="Default view style for items">
          <ToggleGroup
            options={[
              { value: 'square', label: 'Square' },
              { value: 'line', label: 'Line' },
              { value: 'collapsed', label: 'Collapsed' },
            ]}
            value={settings.displayStyle}
            onChange={(v) => onUpdateSetting('displayStyle', v as DisplayStyle)}
            size="sm"
          />
        </SettingsRow>

        <SettingsRow label="Size/Density" description="How much space items take">
          <ToggleGroup
            options={[
              { value: 'expanded', label: 'Expanded' },
              { value: 'comfortable', label: 'Normal' },
              { value: 'compact', label: 'Compact' },
            ]}
            value={settings.density}
            onChange={(v) => onUpdateSetting('density', v as Density)}
            size="sm"
          />
        </SettingsRow>

        <SettingsRow label="Card Shape" description="Shape of item cards">
          <ToggleGroup
            options={[
              { value: 'rounded', label: 'Rounded' },
              { value: 'curvy', label: 'Curvy' },
              { value: 'cloudy', label: 'Cloudy' },
              { value: 'sticky', label: 'Sticky' },
            ]}
            value={settings.cardShape}
            onChange={(v) => onUpdateSetting('cardShape', v as CardShape)}
            size="sm"
          />
        </SettingsRow>
      </SettingsSection>

      <SettingsSection title="Calendar Settings" description="Configure your calendar view">
        <SettingsRow label="Default View" description="Initial calendar display mode">
          <ToggleGroup
            options={[
              { value: 'daily', label: 'Day' },
              { value: 'weekly', label: 'Week' },
              { value: 'monthly', label: 'Month' },
              { value: 'yearly', label: 'Year' },
            ]}
            value={settings.defaultCalendarView}
            onChange={(v) => onUpdateSetting('defaultCalendarView', v as CalendarView)}
            size="sm"
          />
        </SettingsRow>

        <SettingsRow label="Week Starts On" description="First day of the week">
          <ToggleGroup
            options={[
              { value: 'monday', label: 'Monday' },
              { value: 'sunday', label: 'Sunday' },
            ]}
            value={settings.weekStartsOn}
            onChange={(v) => onUpdateSetting('weekStartsOn', v as DayOfWeek)}
            size="sm"
          />
        </SettingsRow>

        <SettingsRow label="Show Weekends" description="Display Saturday and Sunday">
          <button
            onClick={() => onUpdateSetting('showWeekends', !settings.showWeekends)}
            className={`relative w-11 h-6 rounded-full transition-colors ${
              settings.showWeekends ? 'bg-gradient-to-r from-sky-400 to-lavender-500' : 'bg-slate-200 dark:bg-slate-700'
            }`}
          >
            <span
              className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ${
                settings.showWeekends ? 'translate-x-5' : ''
              }`}
            />
          </button>
        </SettingsRow>
      </SettingsSection>

      <SettingsSection title="Task Board Settings" description="Configure your task board layout">
        <SettingsRow label="Default Column Mode" description="How columns are organized">
          <ToggleGroup
            options={[
              { value: 'stage', label: 'Stage' },
              { value: 'priority', label: 'Priority' },
              { value: 'topic', label: 'Topic' },
            ]}
            value={settings.defaultColumnMode}
            onChange={(v) => onUpdateSetting('defaultColumnMode', v as ColumnMode)}
            size="sm"
          />
        </SettingsRow>

        <SettingsRow label="Default Row Mode" description="How rows are grouped">
          <ToggleGroup
            options={[
              { value: 'time', label: 'Time' },
              { value: 'category', label: 'Category' },
            ]}
            value={settings.defaultRowMode}
            onChange={(v) => onUpdateSetting('defaultRowMode', v as RowMode)}
            size="sm"
          />
        </SettingsRow>
      </SettingsSection>

      <div className="rounded-2xl p-5 bg-gradient-to-r from-coral-50 to-peach-50 dark:from-coral-900/20 dark:to-peach-900/20 border border-coral-200 dark:border-coral-800">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-semibold text-slate-800 dark:text-slate-100">Reset to Defaults</p>
            <p className="text-sm text-slate-500 dark:text-slate-400">Restore all settings to their default values</p>
          </div>
          <button className="px-4 py-2 text-sm font-medium text-coral-600 dark:text-coral-400 bg-white dark:bg-slate-800 rounded-xl hover:bg-coral-100 dark:hover:bg-coral-900/30 transition-colors border border-coral-200 dark:border-coral-800">
            Reset
          </button>
        </div>
      </div>
    </div>
  );
}
