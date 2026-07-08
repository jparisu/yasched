import { Target, Clock, AlertCircle, CheckCircle2, ArrowRight, Zap, PenLine } from 'lucide-react';
import { DisplayItem, GlobalControls, PanelCard } from '../components/ui';
import { mockTasks, mockEvents, mockDeadlines } from '../data/mockData';
import { DisplayStyle, Density, CardShape } from '../types';

interface FocusProps {
  displayStyle: DisplayStyle;
  density: Density;
  cardShape: CardShape;
  onUpdateSettings: (key: string, value: string) => void;
}

export function Focus({ displayStyle, density, cardShape, onUpdateSettings }: FocusProps) {
  const highPriorityTasks = mockTasks
    .filter(t => t.priority === 'high' && t.status !== 'done')
    .slice(0, 3);

  const urgentDeadlines = mockDeadlines
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .slice(0, 3);

  const upcomingEvents = mockEvents
    .filter(e => {
      const eventDate = new Date(e.date).toDateString();
      const today = new Date().toDateString();
      return eventDate === today || new Date(e.date) > new Date();
    })
    .slice(0, 3);

  const currentFocus = highPriorityTasks[0];

  return (
    <div className="max-w-5xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-center flex-1 mb-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-lavender-100 to-sky-100 dark:from-lavender-900/30 dark:to-sky-900/30 text-lavender-600 dark:text-lavender-400 text-sm font-semibold mb-2">
            <Zap size={16} />
            Focus Mode
          </div>
          <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100">
            What should you work on now?
          </h2>
        </div>
        <GlobalControls
          displayStyle={displayStyle}
          density={density}
          cardShape={cardShape}
          onDisplayStyleChange={(v) => onUpdateSettings('displayStyle', v)}
          onDensityChange={(v) => onUpdateSettings('density', v)}
          onCardShapeChange={(v) => onUpdateSettings('cardShape', v)}
        />
      </div>

      {currentFocus && (
        <div className="rounded-2xl p-6 bg-gradient-to-br from-sky-100 via-lavender-50 to-mint-50 dark:from-sky-900/30 dark:via-lavender-900/20 dark:to-mint-900/10 border-2 border-sky-200 dark:border-sky-800 shadow-lg">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-sky-400 to-lavender-500 flex items-center justify-center text-white flex-shrink-0 shadow-lg">
              <Target size={28} />
            </div>
            <div className="flex-1">
              <p className="text-xs font-bold text-sky-600 dark:text-sky-400 uppercase tracking-wide mb-1">
                Current Focus
              </p>
              <h3 className="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-2">
                {currentFocus.title}
              </h3>
              {currentFocus.description && (
                <p className="text-slate-600 dark:text-slate-300 mb-3">
                  {currentFocus.description}
                </p>
              )}
              <div className="flex items-center gap-3 flex-wrap">
                <span className="inline-flex items-center gap-1.5 text-sm bg-coral-100 dark:bg-coral-900/30 px-3 py-1.5 rounded-full text-coral-600 dark:text-coral-400 font-medium">
                  <AlertCircle size={14} />
                  High Priority
                </span>
                {currentFocus.deadline && (
                  <span className="inline-flex items-center gap-1.5 text-sm bg-white dark:bg-slate-800 px-3 py-1.5 rounded-full text-slate-600 dark:text-slate-300">
                    <Clock size={14} />
                    Due {new Date(currentFocus.deadline).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </span>
                )}
              </div>
            </div>
            <button className="px-5 py-2.5 bg-gradient-to-r from-sky-400 to-lavender-500 hover:from-sky-500 hover:to-lavender-600 text-white rounded-xl font-semibold transition-all shadow-md hover:shadow-lg flex items-center gap-2">
              Start <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <PanelCard title="Priority Tasks" subtitle="High priority items" colorClass="sky" variant="colorful">
          <div className={`space-y-2 ${density === 'compact' ? 'space-y-1' : ''}`}>
            {highPriorityTasks.length > 0 ? (
              highPriorityTasks.map((task) => (
                <DisplayItem
                  key={task.id}
                  title={task.title}
                  description={task.description}
                  displayStyle={displayStyle}
                  itemStyle={task.style}
                  topicId={task.topicId}
                  priority={task.priority}
                  deadline={task.deadline}
                />
              ))
            ) : (
              <div className="py-8 text-center">
                <CheckCircle2 className="w-12 h-12 mx-auto text-mint-500 mb-2" />
                <p className="text-slate-500 dark:text-slate-400 text-sm">
                  All high priority tasks completed
                </p>
              </div>
            )}
          </div>
        </PanelCard>

        <PanelCard title="Close Deadlines" subtitle="Approaching due dates" colorClass="coral" variant="colorful">
          <div className={`space-y-2 ${density === 'compact' ? 'space-y-1' : ''}`}>
            {urgentDeadlines.map((deadline) => (
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

        <PanelCard title="Today's Events" subtitle="Upcoming schedule" colorClass="lavender" variant="colorful">
          <div className={`space-y-2 ${density === 'compact' ? 'space-y-1' : ''}`}>
            {upcomingEvents.map((event) => (
              <DisplayItem
                key={event.id}
                title={event.title}
                displayStyle={displayStyle}
                itemStyle={event.style}
                topicId={event.topicId}
                startTime={event.startTime}
                endTime={event.endTime}
                recurring={event.recurring}
              />
            ))}
          </div>
        </PanelCard>
      </div>

      <div className="rounded-2xl p-4 bg-gradient-to-br from-peach-50 to-lemon-50 dark:from-peach-900/20 dark:to-lemon-900/20 border border-peach-200 dark:border-peach-800">
        <div className="flex items-center gap-2 mb-3">
          <PenLine size={16} className="text-peach-600" />
          <h4 className="font-semibold text-slate-800 dark:text-slate-100">
            Notes
          </h4>
        </div>
        <textarea
          className={`w-full ${density === 'expanded' ? 'h-32' : density === 'comfortable' ? 'h-24' : 'h-16'} p-3 rounded-xl bg-white/80 dark:bg-slate-800/80 border border-peach-200 dark:border-peach-800 text-slate-800 dark:text-slate-100 resize-none focus:outline-none focus:ring-2 focus:ring-peach-400 font-sans`}
          placeholder="Add notes for your focus session..."
        />
      </div>
    </div>
  );
}
