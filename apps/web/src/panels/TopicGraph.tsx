import { useState } from 'react';
import { ChevronRight } from 'lucide-react';
import { useData } from '../store';
import { ElementDTO } from '../types';
import { backgroundStyle } from '../lib/layout';
import { displayName, rootTopics, subTopics } from '../lib/elements';

export function TopicGraph({ onOpen }: { onOpen: (id: string) => void }) {
  const { elements } = useData();
  const [view, setView] = useState<'tree' | 'nested'>('nested');
  const roots = rootTopics(elements);

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {(['nested', 'tree'] as const).map((v) => (
          <button
            key={v}
            onClick={() => setView(v)}
            className={`px-3 py-1.5 rounded-lg border text-sm capitalize ${
              view === v ? 'bg-sky-500 text-white border-sky-500' : 'border-slate-200 dark:border-slate-700'
            }`}
          >
            {v === 'nested' ? 'Graph' : 'Tree'}
          </button>
        ))}
      </div>

      {roots.length === 0 ? (
        <div className="card p-8 text-center text-slate-400">No topics yet.</div>
      ) : view === 'nested' ? (
        <div className="flex flex-wrap gap-4">
          {roots.map((t) => (
            <TopicBox key={t.id} elements={elements} topicId={t.id} onOpen={onOpen} />
          ))}
        </div>
      ) : (
        <div className="card p-4">
          <ul>
            {roots.map((t) => (
              <TopicTreeRow key={t.id} elements={elements} topicId={t.id} depth={0} onOpen={onOpen} />
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function topicCounts(elements: ElementDTO[], topicId: string) {
  const inTopic = elements.filter((e) => e.topic === topicId);
  return {
    tasks: inTopic.filter((e) => e.type === 'task').length,
    events: inTopic.filter((e) => e.type === 'event').length,
    schedules: inTopic.filter((e) => e.type === 'schedule').length,
    topics: subTopics(elements, topicId).length,
  };
}

function TopicBox({
  elements,
  topicId,
  onOpen,
}: {
  elements: ElementDTO[];
  topicId: string;
  onOpen: (id: string) => void;
}) {
  const topic = elements.find((e) => e.id === topicId);
  const children = subTopics(elements, topicId);
  const c = topicCounts(elements, topicId);
  return (
    <div
      className="rounded-2xl border border-slate-200/70 dark:border-slate-700 p-3 min-w-[180px]"
      style={topic ? backgroundStyle(topic.layout) : {}}
    >
      <button onClick={() => onOpen(topicId)} className="font-semibold text-left block mb-1">
        {displayName(topic)}
      </button>
      <div className="text-xs text-slate-600 dark:text-slate-300 mb-2 flex gap-2">
        <span>✓ {c.tasks}</span>
        <span>E {c.events}</span>
        <span>↻ {c.schedules}</span>
      </div>
      {children.length > 0 && (
        <div className="flex flex-wrap gap-2 pl-2 border-l-2 border-slate-300/50">
          {children.map((ch) => (
            <TopicBox key={ch.id} elements={elements} topicId={ch.id} onOpen={onOpen} />
          ))}
        </div>
      )}
    </div>
  );
}

function TopicTreeRow({
  elements,
  topicId,
  depth,
  onOpen,
}: {
  elements: ElementDTO[];
  topicId: string;
  depth: number;
  onOpen: (id: string) => void;
}) {
  const [open, setOpen] = useState(true);
  const topic = elements.find((e) => e.id === topicId);
  const children = subTopics(elements, topicId);
  const c = topicCounts(elements, topicId);
  return (
    <li>
      <div className="flex items-center gap-1 py-0.5" style={{ paddingLeft: depth * 18 }}>
        <button
          onClick={() => setOpen((o) => !o)}
          className={`p-0.5 text-slate-400 ${children.length === 0 ? 'invisible' : ''}`}
        >
          <ChevronRight size={14} className={`transition-transform ${open ? 'rotate-90' : ''}`} />
        </button>
        <button onClick={() => onOpen(topicId)} className="text-sm font-medium hover:underline">
          {displayName(topic)}
        </button>
        <span className="text-xs text-slate-400">
          ✓{c.tasks} · E{c.events} · ↻{c.schedules}
        </span>
      </div>
      {open &&
        children.map((ch) => (
          <ul key={ch.id}>
            <TopicTreeRow elements={elements} topicId={ch.id} depth={depth + 1} onOpen={onOpen} />
          </ul>
        ))}
    </li>
  );
}
