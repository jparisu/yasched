import { useData } from '../store';
import { PanelCard } from '../ui/PanelCard';
import { ElementView } from '../ui/ElementView';
import {
  attrNumber,
  byType,
  byWhenAsc,
  isCancelled,
  isVisibleTask,
  whenOf,
} from '../lib/elements';
import { ElementDTO } from '../types';
import { today } from '../lib/format';

interface MainProps {
  onOpen: (id: string) => void;
}

export function Main({ onOpen }: MainProps) {
  const { elements, byId, meta } = useData();
  const now = today();

  const upcomingEvents = byType(elements, 'event')
    .filter((e) => !isCancelled(e))
    .filter((e) => {
      const w = whenOf(e);
      return w != null && w >= now;
    })
    .sort(byWhenAsc)
    .slice(0, 12);

  const tasks = byType(elements, 'task').filter((t) => isVisibleTask(t, byId));

  const upcomingDeadlines = tasks
    .filter((t) => whenOf(t) != null)
    .sort(byWhenAsc)
    .slice(0, 8);

  const priorityTasks = tasks
    .filter((t) => whenOf(t) == null)
    .sort((a, b) => (attrNumber(b, 'priority') ?? 0) - (attrNumber(a, 'priority') ?? 0))
    .slice(0, 8);

  return (
    <div className="space-y-4">
      <div className="card px-4 py-3 flex items-center justify-between">
        <div className="min-w-0">
          <p className="text-xs text-slate-400 uppercase tracking-wide">Database</p>
          <p className="font-mono text-sm truncate text-slate-700 dark:text-slate-200">
            {meta?.agenda ?? '—'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <PanelCard title="Upcoming events" collapseId="main-events">
          <EventLines items={upcomingEvents} onOpen={onOpen} empty="No upcoming events" />
        </PanelCard>

        <div className="space-y-4">
          <PanelCard title="Upcoming deadlines" collapseId="main-deadlines">
            <EventLines items={upcomingDeadlines} onOpen={onOpen} empty="No deadlines ahead" />
          </PanelCard>
          <PanelCard title="Priority tasks" collapseId="main-priority">
            <EventLines items={priorityTasks} onOpen={onOpen} empty="No open priority tasks" />
          </PanelCard>
        </div>
      </div>
    </div>
  );
}

function EventLines({
  items,
  onOpen,
  empty,
}: {
  items: ElementDTO[];
  onOpen: (id: string) => void;
  empty: string;
}) {
  if (items.length === 0) return <p className="text-sm text-slate-400">{empty}</p>;
  return (
    <div className="space-y-1.5">
      {items.map((e) => (
        <ElementView key={e.id} element={e} mode="line" onClick={onOpen} when="datetime" />
      ))}
    </div>
  );
}
