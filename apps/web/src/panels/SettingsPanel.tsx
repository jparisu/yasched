import { useData } from '../store';
import { AppStyle, Density, useSettings } from '../settings';
import { PanelCard } from '../ui/PanelCard';

const STYLES: AppStyle[] = ['simple', 'programmer', 'office', 'educational'];
const DENSITIES: Density[] = ['compact', 'comfortable', 'spacious'];

export function SettingsPanel() {
  const { settings, updateSetting, reset } = useSettings();
  const { meta } = useData();

  return (
    <div className="space-y-4 max-w-2xl">
      <PanelCard title="Database" collapseId="set-db">
        <p className="text-sm text-slate-500 mb-1">Current file</p>
        <p className="font-mono text-sm break-all text-slate-700 dark:text-slate-200">
          {meta?.agenda ?? '—'}
        </p>
        {meta?.multiFile && (
          <p className="text-xs text-amber-600 mt-2">
            This database uses file includes; the first save from the app will flatten it into a
            single file.
          </p>
        )}
      </PanelCard>

      <PanelCard title="Appearance" collapseId="set-appearance">
        <div className="space-y-4">
          <Row label="Theme">
            <button
              onClick={() => updateSetting('theme', settings.theme === 'dark' ? 'light' : 'dark')}
              className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-sm"
            >
              {settings.theme === 'dark' ? '🌙 Dark' : '☀️ Light'}
            </button>
          </Row>
          <Row label="Style">
            <div className="flex flex-wrap gap-2">
              {STYLES.map((s) => (
                <button
                  key={s}
                  onClick={() => updateSetting('style', s)}
                  className={`px-3 py-1.5 rounded-lg border text-sm capitalize ${
                    settings.style === s
                      ? 'bg-sky-500 text-white border-sky-500'
                      : 'border-slate-200 dark:border-slate-700'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </Row>
        </div>
      </PanelCard>

      <PanelCard title="General" collapseId="set-general">
        <div className="space-y-4">
          <Row label="Density">
            <div className="flex gap-2">
              {DENSITIES.map((d) => (
                <button
                  key={d}
                  onClick={() => updateSetting('density', d)}
                  className={`px-3 py-1.5 rounded-lg border text-sm capitalize ${
                    settings.density === d
                      ? 'bg-sky-500 text-white border-sky-500'
                      : 'border-slate-200 dark:border-slate-700'
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </Row>
          <Row label="Week starts on">
            <button
              onClick={() => updateSetting('weekStartsOnMonday', !settings.weekStartsOnMonday)}
              className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-sm"
            >
              {settings.weekStartsOnMonday ? 'Monday' : 'Sunday'}
            </button>
          </Row>
          <Row label="Auto-save edits">
            <button
              onClick={() => updateSetting('autoSave', !settings.autoSave)}
              className={`px-3 py-1.5 rounded-lg border text-sm ${
                settings.autoSave
                  ? 'bg-sky-500 text-white border-sky-500'
                  : 'border-slate-200 dark:border-slate-700'
              }`}
            >
              {settings.autoSave ? 'On (save on change)' : 'Off (manual save)'}
            </button>
          </Row>
          <button onClick={reset} className="text-sm text-rose-500 hover:underline">
            Reset settings
          </button>
        </div>
      </PanelCard>
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-sm text-slate-600 dark:text-slate-300">{label}</span>
      {children}
    </div>
  );
}
