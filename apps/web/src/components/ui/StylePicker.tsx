import { AppStyle } from '../../types';

interface StyleOption {
  value: AppStyle;
  label: string;
  description: string;
  swatch: string;
  font: string;
}

// Each preview swatch uses the style's own accent + display font so the
// picker reads as a real preview rather than a plain list.
const STYLE_OPTIONS: StyleOption[] = [
  {
    value: 'simple',
    label: 'Simple',
    description: 'Clean & colorful',
    swatch: 'linear-gradient(135deg, #0ea5e9, #a855f7)',
    font: "'Nunito', sans-serif",
  },
  {
    value: 'programmer',
    label: 'Programmer',
    description: 'Plain & monospaced',
    swatch: '#2563eb',
    font: "'JetBrains Mono', monospace",
  },
  {
    value: 'office',
    label: 'Office',
    description: 'Warm desk & coffee',
    swatch: 'linear-gradient(135deg, #0f766e, #8a5a2b)',
    font: "'Inter', sans-serif",
  },
  {
    value: 'educational',
    label: 'Educational',
    description: 'Playful classroom',
    swatch: 'linear-gradient(135deg, #ff6b6b, #4ade80, #38bdf8)',
    font: "'Fredoka', 'Nunito', sans-serif",
  },
];

interface StylePickerProps {
  value: AppStyle;
  onChange: (style: AppStyle) => void;
}

export function StylePicker({ value, onChange }: StylePickerProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full">
      {STYLE_OPTIONS.map((option) => {
        const active = value === option.value;
        return (
          <button
            key={option.value}
            onClick={() => onChange(option.value)}
            className={`text-left rounded-xl border p-3 transition-all ${
              active
                ? 'ring-2 ring-offset-2 ring-sky-400 dark:ring-offset-slate-900 border-transparent'
                : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
            }`}
          >
            <div
              className="h-10 rounded-lg mb-2 flex items-center justify-center text-white text-lg font-bold shadow-inner"
              style={{ background: option.swatch, fontFamily: option.font }}
            >
              Aa
            </div>
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">
              {option.label}
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-tight mt-0.5">
              {option.description}
            </p>
          </button>
        );
      })}
    </div>
  );
}
