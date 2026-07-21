import { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { ToggleGroup, DisplayItem, GlobalControls } from '../components/ui';
import { useData } from '../data/DataContext';
import { useEditor } from '../data/EditorContext';
import { useElement } from '../data/ElementContext';
import { usePanelConfig } from '../data/usePanelConfig';
import { itemListClass } from '../lib/itemList';
import { orderTasks } from '../lib/tasks';
import { baseId } from '../api/client';
import { CalendarView, Density } from '../types';

export function Calendar() {
  const { events: mockEvents, tasks: mockTasks } = useData();
  const { openEdit } = useEditor();
  const { openElement } = useElement();
  const { view: displayStyle, setView: setDisplayStyle } = usePanelConfig('calendar');
  const density = 'comfortable' as Density;
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<CalendarView>('monthly');

  const getItemsForDay = (date: Date) => {
    const events = mockEvents.filter(
      (e) => new Date(e.date).toDateString() === date.toDateString()
    );
    const tasks = mockTasks.filter((t) => {
      if (!t.deadline) return false;
      return new Date(t.deadline).toDateString() === date.toDateString();
    });
    return { events, tasks };
  };

  const goToPrevious = () => {
    const newDate = new Date(currentDate);
    switch (view) {
      case 'daily': newDate.setDate(newDate.getDate() - 1); break;
      case 'weekly': newDate.setDate(newDate.getDate() - 7); break;
      case 'monthly': newDate.setMonth(newDate.getMonth() - 1); break;
      case 'yearly': newDate.setFullYear(newDate.getFullYear() - 1); break;
    }
    setCurrentDate(newDate);
  };

  const goToNext = () => {
    const newDate = new Date(currentDate);
    switch (view) {
      case 'daily': newDate.setDate(newDate.getDate() + 1); break;
      case 'weekly': newDate.setDate(newDate.getDate() + 7); break;
      case 'monthly': newDate.setMonth(newDate.getMonth() + 1); break;
      case 'yearly': newDate.setFullYear(newDate.getFullYear() + 1); break;
    }
    setCurrentDate(newDate);
  };

  const goToToday = () => setCurrentDate(new Date());

  const getTitle = () => {
    switch (view) {
      case 'daily':
        return currentDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
      case 'weekly': {
        const startOfWeek = new Date(currentDate);
        startOfWeek.setDate(startOfWeek.getDate() - currentDate.getDay() + 1);
        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setDate(endOfWeek.getDate() + 6);
        return `${startOfWeek.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${endOfWeek.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
      }
      case 'monthly':
        return currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
      case 'yearly':
        return currentDate.getFullYear().toString();
    }
  };

  const getMonthDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const days: (Date | null)[] = [];
    const startOffset = (firstDay.getDay() + 6) % 7;
    for (let i = 0; i < startOffset; i++) days.push(null);
    for (let i = 1; i <= lastDay.getDate(); i++) days.push(new Date(year, month, i));
    return days;
  };

  const isToday = (date: Date) => date.toDateString() === new Date().toDateString();

  const densityStyles = {
    expanded: { minH: 'min-h-36', p: 'p-3' },
    comfortable: { minH: 'min-h-28', p: 'p-2' },
    compact: { minH: 'min-h-20', p: 'p-1' },
  };

  const renderMonthlyView = () => {
    const days = getMonthDays();
    const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

    return (
      <div className="calendar-surface rounded-2xl overflow-hidden shadow-lg border border-slate-200/50 dark:border-slate-700 bg-white dark:bg-slate-800">
        <div className="grid grid-cols-7 bg-gradient-to-r from-sky-100 to-lavender-100 dark:from-sky-900/30 dark:to-lavender-900/30">
          {dayNames.map((day) => (
            <div key={day} className="py-2.5 text-center text-sm font-semibold text-slate-600 dark:text-slate-300">
              {day}
            </div>
          ))}
        </div>
        <div className="grid grid-cols-7">
          {days.map((day, index) => {
            if (!day) {
              return (
                <div key={index} className={`${densityStyles[density].minH} ${densityStyles[density].p} bg-slate-50/50 dark:bg-slate-900/30 border-r border-b border-slate-100 dark:border-slate-800`} />
              );
            }
            const { events, tasks } = getItemsForDay(day);
            const today = isToday(day);
            const weekend = day.getDay() === 0 || day.getDay() === 6;

            return (
              <div
                key={index}
                className={`${densityStyles[density].minH} ${densityStyles[density].p} border-r border-b border-slate-100 dark:border-slate-800 ${
                  weekend ? 'bg-lemon-50/30 dark:bg-lemon-900/10' : ''
                } ${today ? 'ring-2 ring-sky-400 ring-inset bg-sky-50/50 dark:bg-sky-900/20' : ''}`}
              >
                <div className={`text-center mb-1.5 ${today ? '' : ''}`}>
                  <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-sm font-semibold ${
                    today
                      ? 'bg-gradient-to-br from-sky-400 to-lavender-500 text-white'
                      : 'text-slate-700 dark:text-slate-200'
                  }`}>
                    {day.getDate()}
                  </span>
                </div>
                <div className="space-y-1">
                  {events.slice(0, density === 'compact' ? 2 : displayStyle === 'collapsed' ? 3 : 2).map((event) => (
                    <DisplayItem
                      key={event.id}
                      title={event.title}
                      displayStyle={displayStyle === 'square' ? 'line' : displayStyle}
                      itemStyle={event.style}
                      topicId={event.topicId}
                      startTime={event.startTime}
                      onClick={() => openEdit('events', baseId(event.id))}
                      onDoubleClick={() => openElement('events', baseId(event.id))}
                    />
                  ))}
                  {tasks.length > 0 && displayStyle !== 'collapsed' && (
                    <div className="flex flex-wrap gap-1">
                      {tasks.slice(0, 3).map((task) => (
                        <span
                          key={task.id}
                          onClick={() => openEdit('tasks', baseId(task.id))}
                          className="w-1.5 h-1.5 rounded-full cursor-pointer"
                          style={{ backgroundColor: task.style?.leftColor || mockTasks.find(t => t.topicId === task.topicId)?.style?.leftColor }}
                          title={task.title}
                        />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const dayItems = (date: Date) => {
    const { events, tasks } = getItemsForDay(date);
    const sortedEvents = [...events].sort((a, b) => (a.startTime || '').localeCompare(b.startTime || ''));
    return (
      <div className={itemListClass(displayStyle)}>
        {sortedEvents.map((event) => (
          <DisplayItem
            key={event.id}
            title={event.title}
            displayStyle={displayStyle}
            itemStyle={event.style}
            startTime={event.startTime}
            endTime={event.endTime}
            recurring={event.recurring}
            onClick={() => openEdit('events', baseId(event.id))}
            onDoubleClick={() => openElement('events', baseId(event.id))}
          />
        ))}
        {orderTasks(tasks).map(({ task, depth }) => (
          <DisplayItem
            key={task.id}
            title={task.title}
            displayStyle={displayStyle}
            itemStyle={task.style}
            priority={task.priority}
            deadline={task.deadline}
            depth={depth}
            onClick={() => openEdit('tasks', baseId(task.id))}
            onDoubleClick={() => openElement('tasks', baseId(task.id))}
          />
        ))}
        {events.length + tasks.length === 0 && (
          <p className="text-sm text-slate-400 text-center py-4">Nothing scheduled</p>
        )}
      </div>
    );
  };

  const renderDailyView = () => (
    <div className="max-w-2xl mx-auto rounded-2xl shadow-lg border border-slate-200/50 dark:border-slate-700 bg-white dark:bg-slate-800 p-4">
      {dayItems(currentDate)}
    </div>
  );

  const renderWeeklyView = () => {
    const monday = new Date(currentDate);
    const dow = monday.getDay();
    monday.setDate(monday.getDate() - dow + (dow === 0 ? -6 : 1));
    const days = Array.from({ length: 7 }, (_, i) => {
      const d = new Date(monday);
      d.setDate(d.getDate() + i);
      return d;
    });
    const names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    return (
      <div className="rounded-2xl overflow-hidden shadow-lg border border-slate-200/50 dark:border-slate-700 bg-white dark:bg-slate-800 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7">
        {days.map((d, i) => {
          const today = isToday(d);
          return (
            <div key={i} className="border-r border-b border-slate-100 dark:border-slate-800 p-2 min-h-[12rem]">
              <div className="text-center mb-2">
                <p className={`text-xs font-medium ${today ? 'text-sky-600 dark:text-sky-400' : 'text-slate-400'}`}>{names[i]}</p>
                <span className={
                  today
                    ? 'inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold bg-gradient-to-br from-sky-400 to-lavender-500 text-white'
                    : 'text-sm font-bold text-slate-700 dark:text-slate-200'
                }>
                  {d.getDate()}
                </span>
              </div>
              {dayItems(d)}
            </div>
          );
        })}
      </div>
    );
  };

  const renderYearlyView = () => {
    const year = currentDate.getFullYear();
    const countFor = (m: number) => {
      const evs = mockEvents.filter((e) => {
        const d = new Date(e.date);
        return d.getFullYear() === year && d.getMonth() === m;
      }).length;
      const tks = mockTasks.filter(
        (t) => t.deadline && new Date(t.deadline).getFullYear() === year && new Date(t.deadline).getMonth() === m
      ).length;
      return { evs, tks };
    };
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {Array.from({ length: 12 }, (_, m) => {
          const { evs, tks } = countFor(m);
          const monthDate = new Date(year, m, 1);
          const current = m === new Date().getMonth() && year === new Date().getFullYear();
          return (
            <button
              key={m}
              onClick={() => {
                setCurrentDate(new Date(year, m, 1));
                setView('monthly');
              }}
              className={`rounded-xl border p-4 text-left transition-all hover:shadow-md bg-white dark:bg-slate-800 ${
                current ? 'border-sky-400 ring-1 ring-sky-300' : 'border-slate-200/50 dark:border-slate-700'
              }`}
            >
              <p className="font-semibold text-slate-800 dark:text-slate-100">
                {monthDate.toLocaleDateString('en-US', { month: 'long' })}
              </p>
              <div className="flex gap-3 mt-2 text-xs text-slate-500 dark:text-slate-400">
                <span>{evs} event{evs !== 1 ? 's' : ''}</span>
                <span>{tks} deadline{tks !== 1 ? 's' : ''}</span>
              </div>
            </button>
          );
        })}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2">
          <button
            onClick={goToPrevious}
            className="p-2 rounded-lg bg-peach-100 dark:bg-peach-900/30 text-peach-600 hover:bg-peach-200 transition-colors"
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
            onClick={goToNext}
            className="p-2 rounded-lg bg-peach-100 dark:bg-peach-900/30 text-peach-600 hover:bg-peach-200 transition-colors"
          >
            <ChevronRight size={18} />
          </button>
          <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100 ml-2">{getTitle()}</h2>
        </div>
        <div className="flex items-center gap-3">
          <ToggleGroup
            options={[
              { value: 'daily', label: 'Day' },
              { value: 'weekly', label: 'Week' },
              { value: 'monthly', label: 'Month' },
              { value: 'yearly', label: 'Year' },
            ]}
            value={view}
            onChange={(v) => setView(v as CalendarView)}
            size="sm"
          />
          <GlobalControls
            displayStyle={displayStyle}
            onDisplayStyleChange={setDisplayStyle}
          />
        </div>
      </div>

      {view === 'daily' && renderDailyView()}
      {view === 'weekly' && renderWeeklyView()}
      {view === 'monthly' && renderMonthlyView()}
      {view === 'yearly' && renderYearlyView()}
    </div>
  );
}
