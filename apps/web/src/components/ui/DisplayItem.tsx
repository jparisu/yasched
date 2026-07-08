import { ItemStyle, CardShape, DisplayStyle } from '../../types';
import { getItemStyle } from '../../data/mockData';
import { Clock, AlertCircle, RefreshCw, CheckCircle2 } from 'lucide-react';

interface DisplayItemProps {
  title: string;
  description?: string;
  displayStyle: DisplayStyle;
  itemStyle?: ItemStyle;
  topicId?: string;
  startTime?: string;
  endTime?: string;
  priority?: 'low' | 'medium' | 'high';
  status?: 'todo' | 'doing' | 'done';
  recurring?: boolean;
  deadline?: Date;
  onClick?: () => void;
}

const getShapeClass = (shape: CardShape): string => {
  switch (shape) {
    case 'rectangle': return 'rounded-none';
    case 'rounded': return 'rounded-xl';
    case 'curvy': return 'rounded-2xl';
    case 'cloudy': return 'cloudy-shape';
    case 'sticky': return 'sticky-shape';
    default: return 'rounded-xl';
  }
};

export function DisplayItem({
  title,
  description,
  displayStyle,
  itemStyle: providedStyle,
  topicId,
  startTime,
  endTime,
  priority,
  status,
  recurring,
  deadline,
  onClick,
}: DisplayItemProps) {
  const style = providedStyle || (topicId ? getItemStyle({ topicId }) : null)
    || { backgroundColor: '#f1f5f9', leftColor: '#94a3b8', shape: 'rounded' as CardShape };

  const deadlineText = deadline
    ? Math.ceil((new Date(deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
    : null;

  if (displayStyle === 'collapsed') {
    return (
      <button
        onClick={onClick}
        className={`flex items-center gap-1.5 px-2 py-1 ${getShapeClass(style.shape)} transition-all hover:scale-105`}
        style={{
          backgroundColor: style.backgroundColor,
          borderLeft: `3px solid ${style.leftColor}`,
        }}
      >
        <span
          className="w-2 h-2 rounded-full flex-shrink-0"
          style={{ backgroundColor: style.leftColor }}
        />
        <span className="text-sm text-slate-700 dark:text-slate-200 truncate">{title}</span>
        {status === 'done' && (
          <CheckCircle2 size={12} className="text-success-500 ml-auto" />
        )}
      </button>
    );
  }

  if (displayStyle === 'line') {
    return (
      <button
        onClick={onClick}
        className={`w-full flex items-center gap-2 px-3 py-2 ${getShapeClass(style.shape)} transition-all hover:shadow-md`}
        style={{
          backgroundColor: style.backgroundColor,
          borderLeft: `4px solid ${style.leftColor}`,
        }}
      >
        <span
          className="w-2.5 h-2.5 rounded-full flex-shrink-0"
          style={{ backgroundColor: style.leftColor }}
        />
        <div className="flex-1 min-w-0 text-left">
          <p className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">{title}</p>
          {startTime && (
            <p className="text-xs text-slate-500">{startTime}{endTime && ` - ${endTime}`}</p>
          )}
        </div>
        {priority && (
          <span
            className={`text-xs px-1.5 py-0.5 rounded ${
              priority === 'high' ? 'bg-danger-100 text-danger-600' :
              priority === 'medium' ? 'bg-warning-100 text-warning-600' :
              'bg-success-100 text-success-600'
            }`}
          >
            {priority}
          </span>
        )}
        {status === 'done' && (
          <CheckCircle2 size={14} className="text-success-500" />
        )}
        {recurring && (
          <RefreshCw size={12} className="text-slate-400" />
        )}
        {deadlineText !== null && deadlineText <= 3 && (
          <span className="text-xs text-danger-500 flex items-center gap-0.5">
            <AlertCircle size={10} />
            {deadlineText <= 0 ? '!' : `${deadlineText}d`}
          </span>
        )}
      </button>
    );
  }

  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-3 ${getShapeClass(style.shape)} transition-all hover:shadow-lg ${
        style.shape === 'sticky' ? 'sticky-note' : ''
      }`}
      style={{
        backgroundColor: style.backgroundColor,
        borderLeft: `4px solid ${style.leftColor}`,
      }}
    >
      <div className="flex items-start gap-2">
        <span
          className="w-3 h-3 rounded-full mt-0.5 flex-shrink-0"
          style={{ backgroundColor: style.leftColor }}
        />
        <div className="flex-1 min-w-0">
          <p className="font-medium text-slate-800 dark:text-slate-100">{title}</p>
          {description && (
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">{description}</p>
          )}
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            {startTime && (
              <span className="text-xs text-slate-500 flex items-center gap-1">
                <Clock size={10} />
                {startTime}{endTime && ` - ${endTime}`}
              </span>
            )}
            {priority && (
              <span
                className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  priority === 'high' ? 'bg-danger-200 text-danger-700' :
                  priority === 'medium' ? 'bg-warning-200 text-warning-700' :
                  'bg-success-200 text-success-700'
                }`}
              >
                {priority}
              </span>
            )}
            {recurring && (
              <span className="text-xs text-slate-400 flex items-center gap-0.5">
                <RefreshCw size={10} />
                repeats
              </span>
            )}
            {status === 'done' && (
              <span className="text-xs text-success-500 flex items-center gap-0.5">
                <CheckCircle2 size={12} />
                done
              </span>
            )}
          </div>
        </div>
      </div>
      {deadlineText !== null && deadlineText <= 3 && (
        <div className="mt-2 pt-2 border-t border-slate-300/30 text-xs text-danger-600 flex items-center gap-1">
          <AlertCircle size={12} />
          {deadlineText <= 0 ? 'Overdue' : `${deadlineText} day${deadlineText > 1 ? 's' : ''} left`}
        </div>
      )}
    </button>
  );
}
