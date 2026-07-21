import { SettingsSection, SettingsRow, ThemeToggle, StylePicker } from '../components/ui';
import { AppStyle, LevelRanges } from '../types';
import { useSettings } from '../data/SettingsContext';

const SCALE_MAX = 10;

/** Editor for the two thresholds that split a 1..10 scale into three buckets. */
function RangeEditor({
  ranges,
  labels,
  onChange,
}: {
  ranges: LevelRanges;
  labels: [string, string, string];
  onChange: (r: LevelRanges) => void;
}) {
  const num = 'w-16 px-2 py-1 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm text-slate-800 dark:text-slate-100';
  const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
      <span className="flex items-center gap-1.5">
        <span className="w-2.5 h-2.5 rounded-full bg-mint-500" />
        {labels[0]}: <b>1</b>–
        <input
          type="number"
          min={1}
          max={SCALE_MAX - 1}
          value={ranges.lowMax}
          onChange={(e) => {
            const lowMax = clamp(Number(e.target.value) || 1, 1, SCALE_MAX - 1);
            onChange({ lowMax, medMax: Math.max(lowMax, ranges.medMax) });
          }}
          className={num}
        />
      </span>
      <span className="flex items-center gap-1.5">
        <span className="w-2.5 h-2.5 rounded-full bg-peach-500" />
        {labels[1]}: <b>{ranges.lowMax + 1}</b>–
        <input
          type="number"
          min={ranges.lowMax + 1}
          max={SCALE_MAX}
          value={ranges.medMax}
          onChange={(e) => {
            const medMax = clamp(Number(e.target.value) || ranges.lowMax + 1, ranges.lowMax + 1, SCALE_MAX);
            onChange({ ...ranges, medMax });
          }}
          className={num}
        />
      </span>
      <span className="flex items-center gap-1.5">
        <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
        {labels[2]}: <b>{ranges.medMax + 1}</b>–<b>{SCALE_MAX}</b>
      </span>
    </div>
  );
}

export function SettingsPage() {
  const { settings, updateSetting, reset } = useSettings();

  return (
    <div className="max-w-3xl space-y-6">
      <SettingsSection title="Appearance" description="Customize how yasched looks">
        <SettingsRow label="Theme" description="Choose between light and dark mode">
          <ThemeToggle
            isDark={settings.theme === 'dark'}
            onToggle={() => updateSetting('theme', settings.theme === 'dark' ? 'light' : 'dark')}
          />
        </SettingsRow>

        <div>
          <p className="font-medium text-slate-700 dark:text-slate-200">Style</p>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-3">
            Overall look and feel — works in both light and dark mode
          </p>
          <StylePicker value={settings.style} onChange={(s: AppStyle) => updateSetting('style', s)} />
        </div>

        <SettingsRow label="Accent Color" description="Your preferred color accent">
          <div className="flex items-center gap-2">
            {['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4'].map((color) => (
              <button
                key={color}
                onClick={() => updateSetting('accentColor', color)}
                className={`w-8 h-8 rounded-full transition-all ${
                  settings.accentColor === color ? 'ring-2 ring-offset-2 ring-slate-400 scale-110' : ''
                }`}
                style={{ backgroundColor: color }}
              />
            ))}
          </div>
        </SettingsRow>
      </SettingsSection>

      <SettingsSection
        title="Priority & Difficulty"
        description="Priority and difficulty are numeric values on every task and sub-task. Choose the ranges that map those numbers to Low / Medium / High."
      >
        <div>
          <p className="font-medium text-slate-700 dark:text-slate-200 mb-2">Priority ranges</p>
          <RangeEditor
            ranges={settings.priorityRanges}
            labels={['Low', 'Medium', 'High']}
            onChange={(r) => updateSetting('priorityRanges', r)}
          />
        </div>
        <div>
          <p className="font-medium text-slate-700 dark:text-slate-200 mb-2">Difficulty ranges</p>
          <RangeEditor
            ranges={settings.difficultyRanges}
            labels={['Easy', 'Medium', 'Hard']}
            onChange={(r) => updateSetting('difficultyRanges', r)}
          />
        </div>
      </SettingsSection>

      <div className="rounded-2xl p-5 bg-gradient-to-r from-coral-50 to-peach-50 dark:from-coral-900/20 dark:to-peach-900/20 border border-coral-200 dark:border-coral-800">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-semibold text-slate-800 dark:text-slate-100">Reset to Defaults</p>
            <p className="text-sm text-slate-500 dark:text-slate-400">Restore all settings to their default values</p>
          </div>
          <button
            onClick={reset}
            className="px-4 py-2 text-sm font-medium text-coral-600 dark:text-coral-400 bg-white dark:bg-slate-800 rounded-xl hover:bg-coral-100 dark:hover:bg-coral-900/30 transition-colors border border-coral-200 dark:border-coral-800"
          >
            Reset
          </button>
        </div>
      </div>
    </div>
  );
}
