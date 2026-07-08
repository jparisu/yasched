export type Priority = 'low' | 'medium' | 'high';
export type ViewMode = 'statistics' | 'agenda' | 'calendar' | 'taskboard' | 'focus' | 'graph' | 'settings';
export type DisplayStyle = 'square' | 'line' | 'collapsed';
export type CardShape = 'rectangle' | 'rounded' | 'curvy' | 'cloudy' | 'sticky';
export type CalendarView = 'daily' | 'weekly' | 'monthly' | 'yearly';
export type DayOfWeek = 'monday' | 'sunday';
export type Density = 'expanded' | 'comfortable' | 'compact';
export type ColumnMode = 'stage' | 'priority' | 'topic' | 'custom';
export type RowMode = 'time' | 'category' | 'custom';

export interface ItemStyle {
  backgroundColor: string;
  leftColor: string;
  shape: CardShape;
}

export interface Topic {
  id: string;
  name: string;
  color: string;
  style: ItemStyle;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  priority: Priority;
  status: 'todo' | 'doing' | 'done';
  topicId: string;
  deadline?: Date;
  startDate?: Date;
  style?: ItemStyle;
  createdAt: Date;
}

export interface EventItem {
  id: string;
  title: string;
  date: Date;
  startTime?: string;
  endTime?: string;
  topicId?: string;
  description?: string;
  recurring?: boolean;
  style?: ItemStyle;
}

export interface Deadline {
  id: string;
  title: string;
  date: Date;
  priority: Priority;
  topicId: string;
  style?: ItemStyle;
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'task' | 'event' | 'topic' | 'subtopic' | 'deadline' | 'style' | 'recurring';
  x: number;
  y: number;
  connections: string[];
  description: string;
}

export interface Settings {
  theme: 'light' | 'dark';
  density: Density;
  displayStyle: DisplayStyle;
  cardShape: CardShape;
  showWeekends: boolean;
  defaultCalendarView: CalendarView;
  weekStartsOn: DayOfWeek;
  defaultColumnMode: ColumnMode;
  defaultRowMode: RowMode;
  accentColor: string;
}

export interface Statistics {
  totalTasks: number;
  completedTasks: number;
  pendingTasks: number;
  totalEvents: number;
  upcomingEvents: number;
  totalTopics: number;
  tasksByTopic: { topic: string; count: number }[];
  tasksByPriority: { priority: string; count: number }[];
  completionRate: number;
  averageCompletionTime: number;
}
