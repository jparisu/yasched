import { ReactNode } from 'react';
import { Image as ImageIcon, Info, Lightbulb, AlertTriangle } from 'lucide-react';

/**
 * Small presentational primitives used to author the manual pages in
 * `helpContent.tsx`. Keeping them here lets each page read like prose while
 * staying consistent (spacing, colours, light/dark) with the rest of the app.
 */

export function HelpLead({ children }: { children: ReactNode }) {
  return (
    <p className="text-base leading-relaxed text-slate-600 dark:text-slate-300 mb-2">
      {children}
    </p>
  );
}

export function HelpP({ children }: { children: ReactNode }) {
  return (
    <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-300">{children}</p>
  );
}

export function HelpH({ children }: { children: ReactNode }) {
  return (
    <h3 className="text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400 mt-7 mb-2">
      {children}
    </h3>
  );
}

export function HelpList({ items }: { items: ReactNode[] }) {
  return (
    <ul className="space-y-1.5 text-sm leading-relaxed text-slate-600 dark:text-slate-300 list-disc pl-5 marker:text-slate-400">
      {items.map((item, i) => (
        <li key={i}>{item}</li>
      ))}
    </ul>
  );
}

/** Inline highlight for a UI label the reader will look for on screen. */
export function Ui({ children }: { children: ReactNode }) {
  return (
    <span className="px-1.5 py-0.5 rounded-md text-[0.8em] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 whitespace-nowrap">
      {children}
    </span>
  );
}

/** Inline monospace token for ids, keys, and literal values. */
export function Code({ children }: { children: ReactNode }) {
  return (
    <code className="px-1 py-0.5 rounded bg-sky-50 dark:bg-sky-950/40 text-sky-700 dark:text-sky-300 font-mono text-[0.82em]">
      {children}
    </code>
  );
}

const TIP_STYLES = {
  tip: {
    box: 'bg-mint-50/70 dark:bg-mint-900/15 border-mint-300 dark:border-mint-800 text-teal-800 dark:text-mint-200',
    icon: <Lightbulb size={16} className="flex-shrink-0 mt-0.5" />,
  },
  note: {
    box: 'bg-sky-50/70 dark:bg-sky-900/15 border-sky-300 dark:border-sky-800 text-sky-800 dark:text-sky-200',
    icon: <Info size={16} className="flex-shrink-0 mt-0.5" />,
  },
  warn: {
    box: 'bg-lemon-50/70 dark:bg-lemon-900/15 border-lemon-300 dark:border-lemon-800 text-amber-800 dark:text-amber-200',
    icon: <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" />,
  },
} as const;

export function HelpTip({
  tone = 'tip',
  children,
}: {
  tone?: keyof typeof TIP_STYLES;
  children: ReactNode;
}) {
  const s = TIP_STYLES[tone];
  return (
    <div className={`flex gap-2.5 rounded-xl border px-3.5 py-2.5 text-sm leading-relaxed ${s.box}`}>
      {s.icon}
      <div>{children}</div>
    </div>
  );
}

/**
 * Placeholder slot for a screenshot. Renders a labelled, dashed frame that can
 * be replaced with a real image later by passing `src`.
 */
export function HelpImage({
  label,
  caption,
  src,
}: {
  label: string;
  caption?: string;
  src?: string;
}) {
  return (
    <figure className="my-1">
      {src ? (
        <img
          src={src}
          alt={label}
          className="w-full rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm"
        />
      ) : (
        <div className="relative w-full aspect-[16/9] rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-700 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/40 dark:to-slate-900/40 flex flex-col items-center justify-center gap-2 text-slate-400 dark:text-slate-500">
          <ImageIcon size={28} strokeWidth={1.5} />
          <span className="text-sm font-semibold text-slate-500 dark:text-slate-400 px-4 text-center">
            {label}
          </span>
          <span className="text-[11px] uppercase tracking-wider text-slate-400/80 dark:text-slate-600">
            screenshot
          </span>
        </div>
      )}
      {caption && (
        <figcaption className="mt-2 text-xs text-slate-400 dark:text-slate-500 text-center italic">
          {caption}
        </figcaption>
      )}
    </figure>
  );
}
