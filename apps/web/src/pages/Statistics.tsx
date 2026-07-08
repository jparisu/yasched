import { CheckCircle2, Clock, Layers, Calendar, Tag, AlertCircle } from 'lucide-react';
import { SummaryCard, PanelCard, DisplayItem } from '../components/ui';
import { mockTasks, mockEvents, mockTopics, mockDeadlines } from '../data/mockData';
import { DisplayStyle, Density, CardShape } from '../types';

interface StatisticsProps {
  displayStyle: DisplayStyle;
  density: Density;
  cardShape: CardShape;
}

export function Statistics({ displayStyle, density }: StatisticsProps) {
  const totalTasks = mockTasks.length;
  const completedTasks = mockTasks.filter(t => t.status === 'done').length;
  const pendingTasks = mockTasks.filter(t => t.status !== 'done').length;
  const doingTasks = mockTasks.filter(t => t.status === 'doing').length;

  const totalEvents = mockEvents.length;
  const upcomingEvents = mockEvents.filter(e => new Date(e.date) >= new Date()).length;

  const tasksByTopic = mockTopics.map(topic => ({
    topic: topic.name,
    count: mockTasks.filter(t => t.topicId === topic.id).length,
    color: topic.color,
    style: topic.style,
  })).filter(t => t.count > 0);

  const tasksByPriority = [
    { priority: 'high', count: mockTasks.filter(t => t.priority === 'high').length, color: '#ef4444' },
    { priority: 'medium', count: mockTasks.filter(t => t.priority === 'medium').length, color: '#f59e0b' },
    { priority: 'low', count: mockTasks.filter(t => t.priority === 'low').length, color: '#22c55e' },
  ];

  const closeDeadlines = mockDeadlines
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .slice(0, 5);

  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  return (
    <div className="space-y-6">
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
          <div className="space-y-3">
            {tasksByTopic.map(({ topic, count, color }) => (
              <div key={topic} className="flex items-center gap-3">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm font-bold"
                  style={{ backgroundColor: color }}
                >
                  {count}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-200">{topic}</span>
                    <span className="text-xs text-slate-400">{Math.round((count / totalTasks) * 100)}%</span>
                  </div>
                  <div className="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${(count / totalTasks) * 100}%`,
                        backgroundColor: color,
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </PanelCard>

        <PanelCard
          title="Tasks by Priority"
          subtitle="Current priority distribution"
          className="overflow-hidden"
        >
          <div className="flex items-center gap-4 mb-4">
            {tasksByPriority.map(({ priority, count, color }) => (
              <div
                key={priority}
                className="flex-1 text-center p-3 rounded-xl"
                style={{ backgroundColor: `${color}15` }}
              >
                <div className="text-3xl font-bold mb-0.5" style={{ color }}>{count}</div>
                <div className="text-xs font-medium text-slate-500 capitalize">{priority}</div>
              </div>
            ))}
          </div>

          <div className="h-8 rounded-xl overflow-hidden flex">
            {tasksByPriority.map(({ priority, count, color }) => (
              <div
                key={priority}
                className="h-full transition-all duration-500"
                style={{
                  width: `${(count / totalTasks) * 100}%`,
                  backgroundColor: color,
                }}
                title={`${priority}: ${count}`}
              />
            ))}
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
                <span className="w-3 h-3 rounded-full bg-success-500" />
                <span className="text-sm text-slate-600">Done ({completedTasks})</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-warning-500" />
                <span className="text-sm text-slate-600">In Progress ({doingTasks})</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-slate-300" />
                <span className="text-sm text-slate-600">Todo ({pendingTasks - doingTasks})</span>
              </div>
            </div>
          </div>
        </PanelCard>

        <PanelCard
          title="Upcoming Deadlines"
          subtitle="Next 5 deadlines"
          colorClass="coral"
          variant="colorful"
          className="lg:col-span-2"
        >
          <div className={`space-y-2 ${density === 'compact' ? 'space-y-1' : ''}`}>
            {closeDeadlines.map((deadline) => (
              <DisplayItem
                key={deadline.id}
                title={deadline.title}
                displayStyle={displayStyle}
                itemStyle={deadline.style}
                topicId={deadline.topicId}
                priority={deadline.priority}
                deadline={deadline.date}
              />
            ))}
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
