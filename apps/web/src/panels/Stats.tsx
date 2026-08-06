import { useState } from 'react';
import { ChevronRight } from 'lucide-react';
import { useData } from '../store';
import { PanelCard } from '../ui/PanelCard';
import { ElementDTO } from '../types';
import { attrString, displayName, rootTopics, subTopics } from '../lib/elements';

export function Stats({ onOpen }: { onOpen: (id: string) => void }) {
  const { elements, meta } = useData();
  const counts = meta?.counts ?? { topics: 0, events: 0, tasks: 0, schedules: 0 };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatTile label="Topics" value={counts.topics} color="text-sky-500" />
        <StatTile label="Events" value={counts.events} color="text-mint-500" />
        <StatTile label="Tasks" value={counts.tasks} color="text-lavender-500" />
        <StatTile label="Schedules" value={counts.schedules} color="text-peach-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <PanelCard title="Elements by topic" collapseId="stats-by-topic">
          <TopicStatTree elements={elements} kind="counts" onOpen={onOpen} />
        </PanelCard>
        <PanelCard title="Completion progress by topic" collapseId="stats-progress">
          <TopicStatTree elements={elements} kind="progress" onOpen={onOpen} />
        </PanelCard>
      </div>
    </div>
  );
}

function StatTile({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="card p-4">
      <p className={`text-3xl font-bold ${color}`}>{value}</p>
      <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
    </div>
  );
}

function TopicStatTree({
  elements,
  kind,
  onOpen,
}: {
  elements: ElementDTO[];
  kind: 'counts' | 'progress';
  onOpen: (id: string) => void;
}) {
  const roots = rootTopics(elements);
  if (roots.length === 0) return <p className="text-sm text-slate-400">No topics yet.</p>;
  return (
    <ul className="space-y-1">
      {roots.map((t) => (
        <TopicStatRow key={t.id} elements={elements} topicId={t.id} depth={0} kind={kind} onOpen={onOpen} />
      ))}
    </ul>
  );
}

function TopicStatRow({
  elements,
  topicId,
  depth,
  kind,
  onOpen,
}: {
  elements: ElementDTO[];
  topicId: string;
  depth: number;
  kind: 'counts' | 'progress';
  onOpen: (id: string) => void;
}) {
  const [open, setOpen] = useState(true);
  const topic = elements.find((e) => e.id === topicId);
  const children = subTopics(elements, topicId);
  const inTopic = elements.filter((e) => e.topic === topicId);
  const tasks = inTopic.filter((e) => e.type === 'task');
  const events = inTopic.filter((e) => e.type === 'event');
  const schedules = inTopic.filter((e) => e.type === 'schedule');
  const done = tasks.filter((t) => attrString(t, 'status') === 'completed').length;
  const pct = tasks.length ? Math.round((done / tasks.length) * 100) : 0;

  return (
    <li>
      <div className="flex items-center gap-2" style={{ paddingLeft: depth * 14 }}>
        <button onClick={() => setOpen((o) => !o)} className="text-slate-400 p-0.5">
          <ChevronRight size={14} className={`transition-transform ${open ? 'rotate-90' : ''}`} />
        </button>
        <button
          onClick={() => onOpen(topicId)}
          className="text-sm font-medium text-slate-700 dark:text-slate-200 flex-1 truncate text-left hover:text-sky-600 dark:hover:text-sky-400 hover:underline"
        >
          {displayName(topic)}
        </button>
        {kind === 'counts' ? (
          <span className="text-xs text-slate-500 flex gap-2">
            <span title="tasks">✓ {tasks.length}</span>
            <span title="events">E {events.length}</span>
            <span title="schedules">↻ {schedules.length}</span>
          </span>
        ) : (
          <div className="flex items-center gap-2 w-40">
            <div className="flex-1 h-2 rounded-full bg-slate-100 dark:bg-slate-700 overflow-hidden">
              <div className="h-full bg-mint-500" style={{ width: `${pct}%` }} />
            </div>
            <span className="text-xs text-slate-500 w-8 text-right">{pct}%</span>
          </div>
        )}
      </div>
      {open && children.length > 0 && (
        <ul className="space-y-1 mt-1">
          {children.map((c) => (
            <TopicStatRow
              key={c.id}
              elements={elements}
              topicId={c.id}
              depth={depth + 1}
              kind={kind}
              onOpen={onOpen}
            />
          ))}
        </ul>
      )}
    </li>
  );
}
