import { useState } from 'react';
import { AlertTriangle, ChevronDown, ChevronUp, X } from 'lucide-react';
import { useData } from '../../data/DataContext';

export function ValidationBanner() {
  const { validation } = useData();
  const [expanded, setExpanded] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  if (!validation || dismissed) return null;
  const { issues, errorCount, warningCount } = validation;
  if (issues.length === 0) return null;

  const hasErrors = errorCount > 0;
  const tone = hasErrors
    ? 'bg-coral-50 dark:bg-coral-900/20 border-coral-300 dark:border-coral-800 text-coral-700 dark:text-coral-300'
    : 'bg-lemon-50 dark:bg-lemon-900/20 border-lemon-300 dark:border-lemon-800 text-amber-700 dark:text-amber-300';

  return (
    <div className={`mb-4 rounded-xl border ${tone}`}>
      <div className="flex items-center gap-2 px-4 py-2.5">
        <AlertTriangle size={16} className="flex-shrink-0" />
        <span className="text-sm font-medium flex-1">
          {errorCount > 0 && `${errorCount} error${errorCount > 1 ? 's' : ''}`}
          {errorCount > 0 && warningCount > 0 && ', '}
          {warningCount > 0 && `${warningCount} warning${warningCount > 1 ? 's' : ''}`} in your agenda
        </span>
        <button onClick={() => setExpanded((v) => !v)} className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5">
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
        <button onClick={() => setDismissed(true)} className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5">
          <X size={16} />
        </button>
      </div>
      {expanded && (
        <ul className="px-4 pb-3 space-y-1 max-h-56 overflow-y-auto">
          {issues.map((issue, i) => (
            <li key={i} className="text-xs flex gap-2">
              <span
                className={`font-mono px-1.5 rounded ${
                  issue.severity === 'error'
                    ? 'bg-coral-200/60 dark:bg-coral-800/40'
                    : 'bg-lemon-200/60 dark:bg-lemon-800/40'
                }`}
              >
                {issue.severity}
              </span>
              <span>
                {issue.entityKind && (
                  <strong>
                    {issue.entityKind} “{issue.entityId}”:{' '}
                  </strong>
                )}
                {issue.message} <span className="opacity-60">({issue.code})</span>
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
