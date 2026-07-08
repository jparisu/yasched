import { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { ToggleGroup, DisplayItem, GlobalControls } from '../components/ui';
import { mockEvents, mockTasks } from '../data/mockData';
import { CalendarView, DisplayStyle, Density, CardShape } from '../types';

interface CalendarProps {
  displayStyle: DisplayStyle;
  density: Density;
  cardShape: CardShape;
  onUpdateSettings: (key: string, value: string) => void;
}

export function Calendar({ displayStyle, density, cardShape, onUpdateSettings }: CalendarProps) {
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
      <div className="rounded-2xl overflow-hidden shadow-lg border border-slate-200/50 dark:border-slate-700 bg-white dark:bg-slate-800">
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
                    />
                  ))}
                  {tasks.length > 0 && displayStyle !== 'collapsed' && (
                    <div className="flex flex-wrap gap-1">
                      {tasks.slice(0, 3).map((task) => (
                        <span
                          key={task.id}
                          className="w-1.5 h-1.5 rounded-full"
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
            density={density}
            cardShape={cardShape}
            onDisplayStyleChange={(v) => onUpdateSettings('displayStyle', v)}
            onDensityChange={(v) => onUpdateSettings('density', v)}
            onCardShapeChange={(v) => onUpdateSettings('cardShape', v)}
          />
        </div>
      </div>

      {view === 'monthly' && renderMonthlyView()}
    </div>
  );
}
