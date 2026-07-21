import { useEffect, useRef } from 'react';
import { X, ChevronLeft, ChevronRight, BookOpen } from 'lucide-react';
import { HELP_SECTIONS, ALL_PAGES, findPageIndex } from './helpContent';

interface Props {
  activePageId: string;
  onNavigate: (id: string) => void;
  onClose: () => void;
}

export function HelpModal({ activePageId, onNavigate, onClose }: Props) {
  const idx = findPageIndex(activePageId);
  const page = ALL_PAGES[idx];
  const prev = idx > 0 ? ALL_PAGES[idx - 1] : null;
  const next = idx < ALL_PAGES.length - 1 ? ALL_PAGES[idx + 1] : null;

  const contentRef = useRef<HTMLDivElement>(null);

  // Close on Escape.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  // Reset scroll when the page changes.
  useEffect(() => {
    contentRef.current?.scrollTo({ top: 0 });
  }, [activePageId]);

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-3 sm:p-6">
      {/* Backdrop — click to close */}
      <div className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" onClick={onClose} />

      {/* Window */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Manual"
        className="relative w-full max-w-5xl h-[86vh] flex flex-col overflow-hidden rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xl"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-200 dark:border-slate-800 bg-gradient-to-r from-sky-500/10 to-lavender-500/10">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-sky-500 to-lavender-500 flex items-center justify-center text-white shadow-md">
              <BookOpen size={18} />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-800 dark:text-slate-100 leading-tight">
                Manual
              </h2>
              <p className="text-xs text-slate-400 dark:text-slate-500 leading-tight">
                yasched help &amp; guide
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close help"
            className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Body: index + content */}
        <div className="flex-1 flex min-h-0">
          {/* Index */}
          <nav className="w-52 sm:w-60 shrink-0 border-r border-slate-200 dark:border-slate-800 overflow-y-auto py-3 px-2 bg-slate-50/60 dark:bg-slate-950/40">
            {HELP_SECTIONS.map((section) => (
              <div key={section.title} className="mb-4">
                <p className="px-2.5 mb-1 text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                  {section.title}
                </p>
                {section.pages.map((p) => {
                  const active = p.id === activePageId;
                  return (
                    <button
                      key={p.id}
                      onClick={() => onNavigate(p.id)}
                      className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm text-left transition-colors ${
                        active
                          ? 'bg-white dark:bg-slate-800 text-sky-600 dark:text-sky-400 font-semibold shadow-sm'
                          : 'text-slate-600 dark:text-slate-300 hover:bg-white/70 dark:hover:bg-slate-800/60'
                      }`}
                    >
                      <span className={active ? 'text-sky-500' : 'text-slate-400 dark:text-slate-500'}>
                        {p.icon}
                      </span>
                      <span className="truncate">{p.title}</span>
                    </button>
                  );
                })}
              </div>
            ))}
          </nav>

          {/* Content */}
          <div className="flex-1 flex flex-col min-w-0">
            <div ref={contentRef} className="flex-1 overflow-y-auto px-6 sm:px-10 py-7">
              <div className="max-w-2xl mx-auto">
                <div className="flex items-center gap-2.5 mb-4">
                  <span className="text-sky-500">{page.icon}</span>
                  <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">
                    {page.title}
                  </h1>
                </div>
                <div className="space-y-4">{page.content}</div>
              </div>
            </div>

            {/* Prev / next footer */}
            <div className="flex items-center justify-between gap-3 px-6 sm:px-10 py-3 border-t border-slate-200 dark:border-slate-800">
              <NavButton
                dir="prev"
                page={prev}
                onClick={() => prev && onNavigate(prev.id)}
              />
              <span className="text-xs text-slate-400 dark:text-slate-500 shrink-0">
                {idx + 1} / {ALL_PAGES.length}
              </span>
              <NavButton
                dir="next"
                page={next}
                onClick={() => next && onNavigate(next.id)}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function NavButton({
  dir,
  page,
  onClick,
}: {
  dir: 'prev' | 'next';
  page: { title: string } | null;
  onClick: () => void;
}) {
  const isNext = dir === 'next';
  if (!page) return <span className="w-24" />;
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-sm text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors min-w-0 ${
        isNext ? 'flex-row-reverse text-right' : ''
      }`}
    >
      {isNext ? <ChevronRight size={16} className="shrink-0" /> : <ChevronLeft size={16} className="shrink-0" />}
      <span className="flex flex-col leading-tight min-w-0">
        <span className="text-[10px] uppercase tracking-wide text-slate-400">
          {isNext ? 'Next' : 'Previous'}
        </span>
        <span className="font-medium truncate">{page.title}</span>
      </span>
    </button>
  );
}
