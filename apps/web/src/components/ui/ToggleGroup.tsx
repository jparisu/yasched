type ToggleOption = {
  value: string;
  label: string;
  icon?: React.ReactNode;
};

interface ToggleGroupProps {
  options: ToggleOption[];
  value: string;
  onChange: (value: string) => void;
  size?: 'sm' | 'md';
  variant?: 'default' | 'pills';
}

export function ToggleGroup({
  options,
  value,
  onChange,
  size = 'md',
  variant = 'default',
}: ToggleGroupProps) {
  const baseClass = variant === 'pills'
    ? 'flex items-center gap-1'
    : 'flex items-center p-1 bg-slate-100 dark:bg-slate-800 rounded-lg';

  const optionBaseClass = variant === 'pills'
    ? 'px-3 py-1.5 rounded-full text-sm font-medium transition-all'
    : `transition-all duration-200 rounded-md font-medium ${
        size === 'sm' ? 'px-2.5 py-1 text-xs' : 'px-3 py-1.5 text-sm'
      }`;

  const activeClass = variant === 'pills'
    ? 'bg-gradient-to-r from-sky-500 to-lavender-500 text-white shadow-md'
    : 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm';

  const inactiveClass = variant === 'pills'
    ? 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300';

  return (
    <div className={baseClass}>
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={`${optionBaseClass} ${
            value === option.value ? activeClass : inactiveClass
          }`}
        >
          {option.icon && <span className="mr-1">{option.icon}</span>}
          {option.label}
        </button>
      ))}
    </div>
  );
}
