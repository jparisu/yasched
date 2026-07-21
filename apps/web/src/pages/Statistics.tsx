import { useState } from 'react';
import { CheckCircle2, Clock, Layers, Calendar, Tag, AlertCircle, ChevronDown } from 'lucide-react';
import { SummaryCard, PanelCard, DisplayItem, GlobalControls } from '../components/ui';
import { useData } from '../data/DataContext';
import { useEditor } from '../data/EditorContext';
import { useElement } from '../data/ElementContext';
import { baseId } from '../api/client';
import { contrastText } from '../lib/colors';
import { itemListClass } from '../lib/itemList';
import { visibleDeadlines } from '../lib/tasks';
import { usePanelConfig } from '../data/usePanelConfig';

export function Statistics() {
  const { tasks: mockTasks, events: mockEvents, topics: mockTopics, deadlines: mockDeadlines } = useData();
  const { openEdit } = useEditor();
  const { openElement } = useElement();
  const { view: displayStyle, setView } = usePanelConfig('statistics');
  const [collapsedTopics, setCollapsedTopics] = useState<Set<string>>(new Set());
  const toggleTopic = (id: string) =>
    setCollapsedTopics((prev) => {
      const s = new Set(prev);
      if (s.has(id)) s.delete(id);
      else s.add(id);
      return s;
    });
  const totalTasks = mockTasks.length;
  const completedTasks = mockTasks.filter(t => t.status === 'done').length;
  const pendingTasks = mockTasks.filter(t => t.status !== 'done').length;
  const doingTasks = mockTasks.filter(t => t.status === 'doing').length;

  const totalEvents = mockEvents.length;
  const upcomingEvents = mockEvents.filter(e => new Date(e.date) >= new Date()).length;

  // Tasks by topic, organized as a hierarchy: root topics, then sub-topics,
  // then sub-sub-topics… Each row shows its own tasks and its sub-tree total.
  const topicById = new Map(mockTopics.map((t) => [t.id, t]));
  const directCount = (id: string) => mockTasks.filter((t) => t.topicId === id).length;
  const childrenOf = new Map<string, typeof mockTopics>();
  for (const t of mockTopics) {
    const p = t.parentIds?.[0];
    if (p && topicById.has(p)) {
      const l = childrenOf.get(p) ?? [];
      l.push(t);
      childrenOf.set(p, l);
    }
  }
  const subtreeCount = (id: string): number =>
    directCount(id) + (childrenOf.get(id) ?? []).reduce((s, c) => s + subtreeCount(c.id), 0);
  const topicRows: {
    id: string; name: string; color: string; depth: number; direct: number; total: number; hasChildren: boolean;
  }[] = [];
  const seenT = new Set<string>();
  const walkTopic = (t: (typeof mockTopics)[number], depth: number) => {
    if (seenT.has(t.id)) return;
    seenT.add(t.id);
    const kids = childrenOf.get(t.id) ?? [];
    topicRows.push({
      id: t.id, name: t.name, color: t.color, depth,
      direct: directCount(t.id), total: subtreeCount(t.id), hasChildren: kids.length > 0,
    });
    // A collapsed topic hides the rows of its descendants.
    if (!collapsedTopics.has(t.id)) for (const c of kids) walkTopic(c, depth + 1);
  };
  mockTopics
    .filter((t) => !t.parentIds?.length || !topicById.has(t.parentIds[0]))
    .forEach((r) => walkTopic(r, 0));
  const visibleTopicRows = topicRows.filter((r) => r.total > 0);
  const maxTopicTotal = Math.max(1, ...visibleTopicRows.map((r) => r.total));

  // Tasks ordered by priority (desc), then due date (asc), then name.
  const priorityTasks = [...mockTasks].sort((a, b) => {
    const pa = a.priority ?? -Infinity;
    const pb = b.priority ?? -Infinity;
    if (pb !== pa) return pb - pa;
    const da = a.deadline ? new Date(a.deadline).getTime() : Infinity;
    const db = b.deadline ? new Date(b.deadline).getTime() : Infinity;
    if (da !== db) return da - db;
    return a.title.localeCompare(b.title);
  });

  const closeDeadlines = visibleDeadlines(mockDeadlines, mockTasks)
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .slice(0, 5);

  const todayStart = new Date();
  todayStart.setHours(0, 0, 0, 0);
  const closeEvents = mockEvents
    .filter((e) => new Date(e.date) >= todayStart)
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .slice(0, 5);

  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <GlobalControls displayStyle={displayStyle} onDisplayStyleChange={setView} />
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SummaryCard
          title="Total Tasks"
          value={totalTasks}
          subtitle={`${pendingTasks} pending`}
          icon={<Layers size={20} />}
          colorClass="sky"
        />
        <SummaryCard
          title="Completed"
          value={completedTasks}
          subtitle={`${completionRate}% rate`}
          icon={<CheckCircle2 size={20} />}
          colorClass="mint"
          trend={completionRate > 50 ? 'up' : 'neutral'}
          trendValue={`${completionRate}%`}
        />
        <SummaryCard
          title="Upcoming Events"
          value={upcomingEvents}
          subtitle={`of ${totalEvents} total`}
          icon={<Calendar size={20} />}
          colorClass="lavender"
        />
        <SummaryCard
          title="Close Deadlines"
          value={closeDeadlines.length}
          subtitle="Within 7 days"
          icon={<AlertCircle size={20} />}
          colorClass="coral"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PanelCard
          title="Tasks by Topic"
          subtitle="Distribution across categories"
          className="overflow-hidden"
        >
          <div className="space-y-2.5">
            {visibleTopicRows.map((row) => (
              <div key={row.id} className="flex items-center gap-2" style={{ marginLeft: row.depth * 18 }}>
                {row.hasChildren ? (
                  <button
                    onClick={() => toggleTopic(row.id)}
                    className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 flex-shrink-0"
                    title={collapsedTopics.has(row.id) ? 'Expand sub-topics' : 'Collapse sub-topics'}
                  >
                    <ChevronDown size={16} className={`transition-transform ${collapsedTopics.has(row.id) ? '-rotate-90' : ''}`} />
                  </button>
                ) : (
                  <span className="w-4 flex-shrink-0" />
                )}
                <button
                  onClick={() => openEdit('topics', row.id)}
                  onDoubleClick={() => openElement('topics', row.id)}
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold flex-shrink-0"
                  style={{ backgroundColor: row.color, color: contrastText(row.color) }}
                  title={`${row.total} in sub-tree`}
                >
                  {row.total}
                </button>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">
                      {row.name}
                      {row.direct > 0 && row.direct !== row.total && (
                        <span className="text-xs text-slate-400 ml-1">({row.direct} direct)</span>
                      )}
                    </span>
                  </div>
                  <div className="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${(row.total / maxTopicTotal) * 100}%`, backgroundColor: row.color }}
                    />
                  </div>
                </div>
              </div>
            ))}
            {visibleTopicRows.length === 0 && (
              <p className="text-sm text-slate-400 text-center py-4">No tasks assigned to topics</p>
            )}
          </div>
        </PanelCard>

        <PanelCard title="Tasks by Priority" subtitle="Highest priority first" fill>
          <div className={itemListClass(displayStyle)}>
            {priorityTasks.length > 0 ? (
              priorityTasks.map((task) => (
                <DisplayItem
                  key={task.id}
                  title={task.title}
                  displayStyle={displayStyle}
                  itemStyle={task.style}
                  topicId={task.topicId}
                  priority={task.priority}
                  status={task.status}
                  deadline={task.deadline}
                  onClick={() => openEdit('tasks', task.id)}
                  onDoubleClick={() => openElement('tasks', task.id)}
                />
              ))
            ) : (
              <p className="text-sm text-slate-400 text-center py-4">No tasks</p>
            )}
          </div>
        </PanelCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <PanelCard
          title="Completion Progress"
          subtitle="Task status breakdown"
          colorClass="mint"
          variant="colorful"
        >
          <div className="relative pt-4">
            <div className="w-32 h-32 mx-auto relative">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke="#e2e8f0"
                  strokeWidth="12"
                  className="dark:stroke-slate-700"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke="#22c55e"
                  strokeWidth="12"
                  strokeLinecap="round"
                  strokeDasharray={`${completionRate * 2.51} 251`}
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-3xl font-bold text-slate-800 dark:text-slate-100">
                  {completionRate}%
                </span>
              </div>
            </div>
            <div className="flex justify-center gap-4 mt-4">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-mint-500" />
                <span className="text-sm text-slate-600 dark:text-slate-300">Done ({completedTasks})</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-peach-500" />
                <span className="text-sm text-slate-600 dark:text-slate-300">In Progress ({doingTasks})</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-slate-400 dark:bg-slate-500" />
                <span className="text-sm text-slate-600 dark:text-slate-300">Todo ({pendingTasks - doingTasks})</span>
              </div>
            </div>
          </div>
        </PanelCard>

        <PanelCard
          title="Upcoming Deadlines"
          subtitle="Next 5 deadlines"
          colorClass="coral"
          variant="colorful"
        >
          <div className={itemListClass(displayStyle)}>
            {closeDeadlines.length > 0 ? (
              closeDeadlines.map((deadline) => (
                <DisplayItem
                  key={deadline.id}
                  title={deadline.title}
                  displayStyle={displayStyle}
                  itemStyle={deadline.style}
                  topicId={deadline.topicId}
                  priority={deadline.priority}
                  deadline={deadline.date}
                  onClick={() => openEdit('tasks', baseId(deadline.id))}
                  onDoubleClick={() => openElement('tasks', baseId(deadline.id))}
                />
              ))
            ) : (
              <p className="text-sm text-slate-400 text-center py-6">No upcoming deadlines</p>
            )}
          </div>
        </PanelCard>

        <PanelCard
          title="Upcoming Events"
          subtitle="Next 5 events"
          colorClass="lavender"
          variant="colorful"
        >
          <div className={itemListClass(displayStyle)}>
            {closeEvents.length > 0 ? (
              closeEvents.map((event) => (
                <DisplayItem
                  key={event.id}
                  title={event.title}
                  displayStyle={displayStyle}
                  itemStyle={event.style}
                  topicId={event.topicId}
                  startTime={event.startTime}
                  endTime={event.endTime}
                  recurring={event.recurring}
                  onClick={() => openEdit('events', baseId(event.id))}
                  onDoubleClick={() => openElement('events', baseId(event.id))}
                />
              ))
            ) : (
              <p className="text-sm text-slate-400 text-center py-6">No upcoming events</p>
            )}
          </div>
        </PanelCard>
      </div>

      <PanelCard
        title="Database Overview"
        subtitle="Summary of all database entities"
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 rounded-xl bg-gradient-to-br from-sky-50 to-sky-100 dark:from-sky-900/20 dark:to-sky-900/10">
            <Layers className="w-8 h-8 mx-auto text-sky-500 mb-2" />
            <div className="text-2xl font-bold text-slate-800 dark:text-slate-100">{mockTasks.length}</div>
            <div className="text-sm text-slate-500">Tasks</div>
          </div>
          <div className="text-center p-4 rounded-xl bg-gradient-to-br from-lavender-50 to-lavender-100 dark:from-lavender-900/20 dark:to-lavender-900/10">
            <Calendar className="w-8 h-8 mx-auto text-lavender-500 mb-2" />
            <div className="text-2xl font-bold text-slate-800 dark:text-slate-100">{mockEvents.length}</div>
            <div className="text-sm text-slate-500">Events</div>
          </div>
          <div className="text-center p-4 rounded-xl bg-gradient-to-br from-mint-50 to-mint-100 dark:from-mint-900/20 dark:to-mint-900/10">
            <Tag className="w-8 h-8 mx-auto text-mint-500 mb-2" />
            <div className="text-2xl font-bold text-slate-800 dark:text-slate-100">{mockTopics.length}</div>
            <div className="text-sm text-slate-500">Topics</div>
          </div>
          <div className="text-center p-4 rounded-xl bg-gradient-to-br from-coral-50 to-coral-100 dark:from-coral-900/20 dark:to-coral-900/10">
            <Clock className="w-8 h-8 mx-auto text-coral-500 mb-2" />
            <div className="text-2xl font-bold text-slate-800 dark:text-slate-100">{mockDeadlines.length}</div>
            <div className="text-sm text-slate-500">Deadlines</div>
          </div>
        </div>
      </PanelCard>
    </div>
  );
}
