import { Moon, Sun } from 'lucide-react';

interface ThemeToggleProps {
  isDark: boolean;
  onToggle: () => void;
}

export function ThemeToggle({ isDark, onToggle }: ThemeToggleProps) {
  return (
    <button
      onClick={onToggle}
      className="relative w-14 h-7 rounded-full bg-slate-200 dark:bg-slate-700 transition-colors p-0.5"
      aria-label="Toggle theme"
    >
      <div
        className={`absolute w-6 h-6 rounded-full bg-white shadow-md transition-transform duration-200 flex items-center justify-center ${
          isDark ? 'translate-x-7' : 'translate-x-0'
        }`}
      >
        {isDark ? (
          <Moon size={14} className="text-slate-600" />
        ) : (
          <Sun size={14} className="text-warning-500" />
        )}
      </div>
    </button>
  );
}
