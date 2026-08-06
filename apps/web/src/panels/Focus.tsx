import { useState } from 'react';
import { StarOff } from 'lucide-react';
import { useData } from '../store';
import { PanelCard } from '../ui/PanelCard';
import { ElementView } from '../ui/ElementView';
import { ElementDTO } from '../types';
import { attrBool, byWhenAsc, isCancelled } from '../lib/elements';

interface Props {
  onOpen: (id: string) => void;
}

export function Focus({ onOpen }: Props) {
  const { elements, patchAttributes } = useData();
  const [clearing, setClearing] = useState(false);

  const alive = elements.filter((e) => !isCancelled(e));
  const focused = alive.filter((e) => attrBool(e, 'focus'));
  const semi = alive.filter((e) => attrBool(e, 'semiFocus') && !attrBool(e, 'focus'));

  const unfocusAll = async () => {
    setClearing(true);
    try {
      for (const e of [...focused, ...semi]) {
        await patchAttributes(e.id, { focus: false, semiFocus: false });
      }
    } finally {
      setClearing(false);
    }
  };

  if (focused.length === 0 && semi.length === 0) {
    return (
      <div className="card p-8 text-center text-slate-400">
        Nothing is focused. Use the ★ / ◑ buttons in an element's drawer to focus (or semi-focus, for
        backlog / future items) it.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">
          {focused.length} focused · {semi.length} semi-focused
        </p>
        <button
          onClick={unfocusAll}
          disabled={clearing}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-sm text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-50"
        >
          <StarOff size={15} /> Unfocus all
        </button>
      </div>

      <FocusBlocks group={focused} keyPrefix="focus" onOpen={onOpen} />

      {semi.length > 0 && (
        <>
          <div className="flex items-center gap-3 pt-1">
            <span className="text-xs uppercase tracking-wide text-slate-400">Semi-focused · on the radar</span>
            <div className="flex-1 border-t border-slate-200/60 dark:border-slate-700" />
          </div>
          <FocusBlocks group={semi} keyPrefix="semi" onOpen={onOpen} muted />
        </>
      )}
    </div>
  );
}

function FocusBlocks({
  group,
  keyPrefix,
  onOpen,
  muted,
}: {
  group: ElementDTO[];
  keyPrefix: string;
  onOpen: (id: string) => void;
  muted?: boolean;
}) {
  const tasks = group.filter((e) => e.type === 'task').sort(byWhenAsc);
  const events = group.filter((e) => e.type === 'event').sort(byWhenAsc);
  const other = group.filter((e) => e.type === 'topic' || e.type === 'schedule');
  const opacity = muted ? 'opacity-90' : '';

  return (
    <div className={`grid grid-cols-1 lg:grid-cols-2 gap-4 ${opacity}`}>
      <PanelCard title={muted ? 'Semi-focused tasks' : 'Focused tasks'} collapseId={`${keyPrefix}-tasks`}>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {tasks.map((e) => (
            <ElementView key={e.id} element={e} mode="card" onClick={onOpen} />
          ))}
          {tasks.length === 0 && <p className="text-sm text-slate-400">None</p>}
        </div>
      </PanelCard>
      <PanelCard title={muted ? 'Semi-focused events' : 'Focused events'} collapseId={`${keyPrefix}-events`}>
        <div className="space-y-1.5">
          {events.map((e) => (
            <ElementView key={e.id} element={e} mode="line" onClick={onOpen} when="datetime" />
          ))}
          {events.length === 0 && <p className="text-sm text-slate-400">None</p>}
        </div>
      </PanelCard>
      {other.length > 0 && (
        <PanelCard
          title={muted ? 'Semi-focused topics & schedules' : 'Focused topics & schedules'}
          collapseId={`${keyPrefix}-other`}
          className="lg:col-span-2"
        >
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {other.map((e) => (
              <ElementView key={e.id} element={e} mode="card" onClick={onOpen} />
            ))}
          </div>
        </PanelCard>
      )}
    </div>
  );
}
