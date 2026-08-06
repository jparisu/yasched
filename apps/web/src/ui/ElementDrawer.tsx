import { Settings2, Star, StarHalf, X } from 'lucide-react';
import { useData } from '../store';
import { categoryLabel, displayName } from '../lib/elements';
import { ElementView } from './ElementView';

interface Props {
  elementId: string;
  onClose: () => void;
  onOpen: (id: string) => void;
  onConfigure: (id: string) => void;
}

const HIDDEN_ATTRS = new Set(['name', 'description', 'connections', 'focus', 'semiFocus']);

export function ElementDrawer({ elementId, onClose, onOpen, onConfigure }: Props) {
  const { byId, patchAttributes } = useData();
  const el = byId[elementId];
  if (!el) return null;

  const attrs = Object.entries(el.attributes).filter(([k]) => !HIDDEN_ATTRS.has(k));
  const description = typeof el.attributes['description'] === 'string' ? el.attributes['description'] : null;
  const focused = el.attributes['focus'] === true;
  const semiFocused = el.attributes['semiFocus'] === true;

  return (
    <div className="fixed inset-0 z-50 flex justify-end" onClick={onClose}>
      <div className="absolute inset-0 bg-black/30" />
      <aside
        className="relative w-full max-w-md h-full bg-white dark:bg-slate-900 shadow-2xl overflow-y-auto p-5 space-y-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-2">
          <div>
            <span className="text-xs uppercase tracking-wide text-slate-400">
              {categoryLabel(el)}
              {el.virtual ? ' · auto' : ''}
            </span>
            <h2 className="text-xl font-bold">{displayName(el)}</h2>
            <p className="font-mono text-xs text-slate-400 break-all">{el.id}</p>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800">
            <X size={18} />
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onConfigure(el.id)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-500 text-white text-sm hover:bg-sky-600"
          >
            <Settings2 size={15} /> Configure
          </button>
          <button
            onClick={() => void patchAttributes(el.id, { focus: !focused, semiFocus: false })}
            title="Formally on focus"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-sm ${
              focused
                ? 'border-amber-400 text-amber-600 bg-amber-50 dark:bg-amber-900/20'
                : 'border-slate-200 dark:border-slate-700 text-slate-500'
            }`}
          >
            <Star size={15} fill={focused ? 'currentColor' : 'none'} /> {focused ? 'Focused' : 'Focus'}
          </button>
          <button
            onClick={() => void patchAttributes(el.id, { semiFocus: !semiFocused, focus: false })}
            title="On the radar (backlog / future), not formally focused"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-sm ${
              semiFocused
                ? 'border-sky-400 text-sky-600 bg-sky-50 dark:bg-sky-900/20'
                : 'border-slate-200 dark:border-slate-700 text-slate-500'
            }`}
          >
            <StarHalf size={15} fill={semiFocused ? 'currentColor' : 'none'} /> Semi
          </button>
        </div>

        <div className="w-40">
          <ElementView element={el} mode="card" />
        </div>

        {description && <p className="text-sm text-slate-600 dark:text-slate-300">{description}</p>}

        {el.topic && (
          <Info label="Topic">
            <LinkChip id={el.topic} onOpen={onOpen} name={displayName(byId[el.topic])} />
          </Info>
        )}
        {el.mainParent && (
          <Info label="Main parent">
            <LinkChip id={el.mainParent} onOpen={onOpen} name={displayName(byId[el.mainParent])} />
          </Info>
        )}

        {attrs.length > 0 && (
          <Info label="Attributes">
            <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-sm">
              {attrs.map(([k, v]) => (
                <div key={k} className="contents">
                  <dt className="text-slate-400 font-mono">{k}</dt>
                  <dd className="text-slate-700 dark:text-slate-200 truncate">{formatValue(v)}</dd>
                </div>
              ))}
            </dl>
          </Info>
        )}

        {(el.connections.length > 0 || el.incoming.length > 0) && (
          <Info label="Connections">
            <ul className="text-sm space-y-1">
              {el.connections.map((c, i) => (
                <li key={`o${i}`}>
                  → <span className="font-medium">{c.relation}</span>{' '}
                  <LinkChip id={c.to} onOpen={onOpen} name={displayName(byId[c.to])} />
                </li>
              ))}
              {el.incoming.map((c, i) => (
                <li key={`i${i}`} className="text-slate-500">
                  ← <LinkChip id={c.from} onOpen={onOpen} name={displayName(byId[c.from])} />{' '}
                  <span className="font-medium">{c.relation}</span>
                </li>
              ))}
            </ul>
          </Info>
        )}
      </aside>
    </div>
  );
}

function Info({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-wide text-slate-400 mb-1">{label}</p>
      {children}
    </div>
  );
}

function LinkChip({ id, name, onOpen }: { id: string; name: string; onOpen: (id: string) => void }) {
  return (
    <button onClick={() => onOpen(id)} className="text-sky-600 dark:text-sky-400 hover:underline">
      {name}
    </button>
  );
}

function formatValue(v: unknown): string {
  if (Array.isArray(v)) return v.map((x) => (typeof x === 'object' ? JSON.stringify(x) : String(x))).join(', ');
  if (typeof v === 'object' && v !== null) return JSON.stringify(v);
  return String(v);
}
