import { useState } from 'react';
import { DisplayItem, GlobalControls } from '../components/ui';
import { mockTasks, mockTopics } from '../data/mockData';
import { ColumnMode, RowMode, DisplayStyle, Density, CardShape } from '../types';

interface TaskBoardProps {
  displayStyle: DisplayStyle;
  density: Density;
  cardShape: CardShape;
  onUpdateSettings: (key: string, value: string) => void;
}

export function TaskBoard({ displayStyle, density, cardShape, onUpdateSettings }: TaskBoardProps) {
  const [columnMode, setColumnMode] = useState<ColumnMode>('stage');
  const [rowMode, setRowMode] = useState<RowMode>('time');

  const getColumnDefs = () => {
    switch (columnMode) {
      case 'stage':
        return [
          { id: 'todo', label: 'To Do', color: '#3b82f6', bgClass: 'from-sky-100 to-sky-50 dark:from-sky-900/30 dark:to-sky-900/10' },
          { id: 'doing', label: 'Doing', color: '#f59e0b', bgClass: 'from-peach-100 to-peach-50 dark:from-peach-900/30 dark:to-peach-900/10' },
          { id: 'done', label: 'Done', color: '#22c55e', bgClass: 'from-mint-100 to-mint-50 dark:from-mint-900/30 dark:to-mint-900/10' },
        ];
      case 'priority':
        return [
          { id: 'low', label: 'Low', color: '#22c55e', bgClass: 'from-mint-100 to-mint-50 dark:from-mint-900/30 dark:to-mint-900/10' },
          { id: 'medium', label: 'Medium', color: '#f59e0b', bgClass: 'from-lemon-100 to-lemon-50 dark:from-lemon-900/30 dark:to-lemon-900/10' },
          { id: 'high', label: 'High', color: '#ef4444', bgClass: 'from-coral-100 to-coral-50 dark:from-coral-900/30 dark:to-coral-900/10' },
        ];
      case 'topic':
        return mockTopics.map(t => ({
          id: t.id,
          label: t.name,
          color: t.color,
          bgClass: '',
          style: t.style,
        }));
      default:
        return [];
    }
  };

  const getRowDefs = () => {
    switch (rowMode) {
      case 'time':
        return [
          { id: 'this_week', label: 'This Week' },
          { id: 'later', label: 'Later' },
          { id: 'waiting', label: 'No Deadline' },
        ];
      case 'category':
        return mockTopics.slice(0, 4).map(t => ({ id: t.id, label: t.name }));
      default:
        return [{ id: 'all', label: 'All Tasks' }];
    }
  };

  const getTasksForCell = (columnId: string, rowId: string) => {
    let filtered = [...mockTasks];

    if (columnMode === 'stage') filtered = filtered.filter(t => t.status === columnId);
    else if (columnMode === 'priority') filtered = filtered.filter(t => t.priority === columnId);
    else if (columnMode === 'topic') filtered = filtered.filter(t => t.topicId === columnId);

    if (rowMode === 'time') {
      filtered = filtered.filter(t => {
        const deadline = t.deadline;
        if (!deadline) return rowId === 'waiting' || rowId === 'No Deadline';
        const deadlineDate = new Date(deadline);
        const weekFromNow = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
        if (rowId === 'this_week') return deadlineDate <= weekFromNow;
        if (rowId === 'later') return deadlineDate > weekFromNow;
        return false;
      });
    }

    return filtered;
  };

  const columnDefs = getColumnDefs();
  const rowDefs = getRowDefs();

  const densityClass = density === 'expanded' ? 'p-4' : density === 'comfortable' ? 'p-3' : 'p-2';

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-4">
          <div>
            <span className="text-xs text-slate-500 mr-2">Columns:</span>
            <div className="flex items-center gap-1 p-0.5 bg-slate-100 dark:bg-slate-800 rounded-lg">
              {[
                { value: 'stage', label: 'Stage' },
                { value: 'priority', label: 'Priority' },
                { value: 'topic', label: 'Topic' },
              ].map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setColumnMode(opt.value as ColumnMode)}
                  className={`px-3 py-1 text-xs rounded-md transition-all ${
                    columnMode === opt.value
                      ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
                      : 'text-slate-500'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
          <div>
            <span className="text-xs text-slate-500 mr-2">Rows:</span>
            <div className="flex items-center gap-1 p-0.5 bg-slate-100 dark:bg-slate-800 rounded-lg">
              {[
                { value: 'time', label: 'Time' },
                { value: 'category', label: 'Category' },
              ].map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setRowMode(opt.value as RowMode)}
                  className={`px-3 py-1 text-xs rounded-md transition-all ${
                    rowMode === opt.value
                      ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
                      : 'text-slate-500'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
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

      <div className="overflow-x-auto rounded-2xl shadow-lg border border-slate-200/50 dark:border-slate-700 bg-white dark:bg-slate-800">
        <table className="w-full border-collapse min-w-[600px]">
          <thead>
            <tr>
              <th className="w-36 p-3 bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-900 border-b border-r border-slate-200/50 dark:border-slate-700 text-left">
                <span className="text-xs font-medium text-slate-400">
                  {columnMode === 'stage' ? 'Stage' : columnMode === 'priority' ? 'Priority' : 'Topic'} / {rowMode === 'time' ? 'Time' : 'Category'}
                </span>
              </th>
              {columnDefs.map((col) => (
                <th
                  key={col.id}
                  className={`p-3 border-b border-r border-slate-200/50 dark:border-slate-700 bg-gradient-to-r ${col.bgClass}`}
                >
                  <div className="flex items-center gap-2">
                    <span
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: col.color }}
                    />
                    <span className="font-semibold" style={{ color: col.color }}>
                      {col.label}
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rowDefs.map((row) => (
              <tr key={row.id}>
                <td className="p-3 bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-900 border-r border-b border-slate-200/50 dark:border-slate-700">
                  <span className="font-medium text-slate-700 dark:text-slate-200 text-sm">{row.label}</span>
                </td>
                {columnDefs.map((col) => {
                  const tasks = getTasksForCell(col.id, row.id);
                  return (
                    <td
                      key={col.id}
                      className={`${densityClass} border-r border-b border-slate-200/50 dark:border-slate-700 align-top bg-gradient-to-br ${col.bgClass}`}
                    >
                      <div className={`space-y-2 ${density === 'compact' ? 'space-y-1' : ''}`}>
                        {tasks.map((task) => (
                          <DisplayItem
                            key={task.id}
                            title={task.title}
                            description={task.description}
                            displayStyle={displayStyle}
                            itemStyle={task.style}
                            topicId={task.topicId}
                            priority={task.priority}
                            status={task.status}
                            deadline={task.deadline}
                          />
                        ))}
                        {tasks.length === 0 && (
                          <div className="text-xs text-slate-400 text-center py-3">
                            No tasks
                          </div>
                        )}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
