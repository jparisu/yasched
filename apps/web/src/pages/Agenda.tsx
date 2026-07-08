import { useState } from 'react';
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react';
import { DisplayItem, GlobalControls } from '../components/ui';
import { mockTasks, mockEvents, mockTopics } from '../data/mockData';
import { DisplayStyle, Density, CardShape } from '../types';

interface AgendaProps {
  displayStyle: DisplayStyle;
  density: Density;
  cardShape: CardShape;
  onUpdateSettings: (key: string, value: string) => void;
}

export function Agenda({ displayStyle, density, cardShape, onUpdateSettings }: AgendaProps) {
  const [currentWeekStart, setCurrentWeekStart] = useState(() => {
    const today = new Date();
    const dayOfWeek = today.getDay();
    const diff = today.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
    return new Date(today.setDate(diff));
  });

  const getWeekDays = () => {
    const days = [];
    for (let i = 0; i < 7; i++) {
      const day = new Date(currentWeekStart);
      day.setDate(day.getDate() + i);
      days.push(day);
    }
    return days;
  };

  const weekDays = getWeekDays();
  const shortDayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  const goToPreviousWeek = () => {
    const newDate = new Date(currentWeekStart);
    newDate.setDate(newDate.getDate() - 7);
    setCurrentWeekStart(newDate);
  };

  const goToNextWeek = () => {
    const newDate = new Date(currentWeekStart);
    newDate.setDate(newDate.getDate() + 7);
    setCurrentWeekStart(newDate);
  };

  const goToToday = () => {
    const today = new Date();
    const dayOfWeek = today.getDay();
    const diff = today.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
    setCurrentWeekStart(new Date(today.setDate(diff)));
  };

  const getItemsForDay = (date: Date) => {
    const events = mockEvents.filter(
      (e) => new Date(e.date).toDateString() === date.toDateString()
    );
    const tasks = mockTasks.filter((t) => {
      if (!t.deadline && !t.startDate) return false;
      const checkDate = t.startDate || t.deadline;
      return checkDate && new Date(checkDate).toDateString() === date.toDateString();
    });
    return { events, tasks: tasks.filter(t => t.status !== 'done') };
  };

  const isToday = (date: Date) => date.toDateString() === new Date().toDateString();
  const isWeekend = (date: Date) => date.getDay() === 0 || date.getDay() === 6;

  const densityClasses = {
    expanded: 'min-h-48 p-4',
    comfortable: 'min-h-32 p-3',
    compact: 'min-h-20 p-2',
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2">
          <button
            onClick={goToPreviousWeek}
            className="p-2 rounded-lg bg-peach-100 dark:bg-peach-900/30 text-peach-600 hover:bg-peach-200 dark:hover:bg-peach-900/50 transition-colors"
          >
            <ChevronLeft size={18} />
          </button>
          <button
            onClick={goToToday}
            className="px-4 py-2 text-sm font-semibold rounded-lg bg-gradient-to-r from-sky-400 to-lavender-500 text-white shadow-md hover:shadow-lg transition-shadow"
          >
            Today
          </button>
          <button
            onClick={goToNextWeek}
            className="p-2 rounded-lg bg-peach-100 dark:bg-peach-900/30 text-peach-600 hover:bg-peach-200 dark:hover:bg-peach-900/50 transition-colors"
          >
            <ChevronRight size={18} />
          </button>
          <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 ml-2">
            {weekDays[0].toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
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

      <div className="agenda-page rounded-3xl overflow-hidden shadow-xl">
        <div className="agenda-fold flex">
          <div className="flex-1">
            <div className="flex divide-x divide-amber-200/30 dark:divide-slate-700/50">
              {weekDays.slice(0, 4).map((date, index) => {
                const { events, tasks } = getItemsForDay(date);
                const today = isToday(date);
                const weekend = isWeekend(date);

                return (
                  <div
                    key={index}
                    className={`flex-1 min-w-0 ${densityClasses[density]} ${
                      weekend ? 'bg-lemon-50/30 dark:bg-lemon-900/10' : ''
                    } ${today ? 'ring-2 ring-sky-400 ring-inset' : ''}`}
                  >
                    <div className={`text-center mb-3 ${today ? 'py-1' : ''}`}>
                      <p className={`text-xs font-medium ${
                        today ? 'text-sky-600 font-bold' : 'text-slate-400'
                      }`}>
                        {shortDayNames[index]}
                      </p>
                      <div className={`text-xl font-bold ${
                        today
                          ? 'w-8 h-8 bg-gradient-to-br from-sky-400 to-lavender-500 text-white rounded-full mx-auto flex items-center justify-center text-sm'
                          : 'text-slate-700 dark:text-slate-200'
                      }`}>
                        {date.getDate()}
                      </div>
                    </div>
                    <div className="space-y-1.5">
                      {events.slice(0, displayStyle === 'collapsed' ? 4 : 2).map((event) => (
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
                      {tasks.slice(0, displayStyle === 'collapsed' ? 2 : 1).map((task) => (
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
                      ))}
                      {events.length + tasks.length === 0 && (
                        <button className="w-full flex items-center justify-center gap-1 text-xs text-slate-400 hover:text-slate-500 py-2 rounded-lg hover:bg-amber-100/50 dark:hover:bg-slate-700/50 transition-colors">
                          <Plus size={12} />
                          Add
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="flex-1">
            <div className="flex divide-x divide-amber-200/30 dark:divide-slate-700/50">
              {weekDays.slice(4).map((date, index) => {
                const { events, tasks } = getItemsForDay(date);
                const today = isToday(date);
                const weekend = isWeekend(date);

                return (
                  <div
                    key={index + 4}
                    className={`flex-1 min-w-0 ${densityClasses[density]} ${
                      weekend ? 'bg-lemon-50/30 dark:bg-lemon-900/10' : ''
                    } ${today ? 'ring-2 ring-sky-400 ring-inset' : ''}`}
                  >
                    <div className={`text-center mb-3 ${today ? 'py-1' : ''}`}>
                      <p className={`text-xs font-medium ${
                        today ? 'text-sky-600 font-bold' : 'text-slate-400'
                      }`}>
                        {shortDayNames[index + 4]}
                      </p>
                      <div className={`text-xl font-bold ${
                        today
                          ? 'w-8 h-8 bg-gradient-to-br from-sky-400 to-lavender-500 text-white rounded-full mx-auto flex items-center justify-center text-sm'
                          : 'text-slate-700 dark:text-slate-200'
                      }`}>
                        {date.getDate()}
                      </div>
                    </div>
                    <div className="space-y-1.5">
                      {events.slice(0, displayStyle === 'collapsed' ? 4 : 2).map((event) => (
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
                      {tasks.slice(0, displayStyle === 'collapsed' ? 2 : 1).map((task) => (
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
                      ))}
                      {events.length + tasks.length === 0 && (
                        <button className="w-full flex items-center justify-center gap-1 text-xs text-slate-400 hover:text-slate-500 py-2 rounded-lg hover:bg-amber-100/50 dark:hover:bg-slate-700/50 transition-colors">
                          <Plus size={12} />
                          Add
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="flex justify-center gap-4 py-3 px-4 border-t border-amber-200/30 dark:border-slate-700/50 bg-amber-50/30 dark:bg-slate-800/30">
          {mockTopics.slice(0, 5).map((topic) => (
            <div key={topic.id} className="flex items-center gap-1.5">
              <span
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: topic.color }}
              />
              <span className="text-xs text-slate-500">{topic.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
