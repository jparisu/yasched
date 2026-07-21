export type Priority = 'low' | 'medium' | 'high';
/** Bucket a numeric priority/difficulty falls into. */
export type Level = 'low' | 'medium' | 'high';
/** Two thresholds splitting a 1..10 scale into low / medium / high. */
export interface LevelRanges {
  lowMax: number;
  medMax: number;
}
export type ViewMode = 'statistics' | 'agenda' | 'calendar' | 'weekly' | 'taskboard' | 'focus' | 'graph' | 'element' | 'settings';
export type AppStyle = 'simple' | 'programmer' | 'office' | 'educational';
export type DisplayStyle = 'square' | 'line' | 'collapsed';
export type CardShape = 'rectangle' | 'rounded' | 'curvy' | 'cloudy' | 'sticky';
export type CalendarView = 'daily' | 'weekly' | 'monthly' | 'yearly';
export type DayOfWeek = 'monday' | 'sunday';
export type Density = 'expanded' | 'comfortable' | 'compact';
export type ColumnMode = 'stage' | 'priority' | 'topic' | 'custom';
export type RowMode = 'time' | 'category' | 'custom';

export interface ItemStyle {
  backgroundColor: string;
  /** Left accent line — reflects the MAIN (root) topic. */
  leftColor: string;
  /** Dot color — reflects the specific sub-topic. Falls back to leftColor. */
  dotColor?: string;
  shape: CardShape;
}

export interface Topic {
  id: string;
  name: string;
  color: string;
  parentIds?: string[];
  style: ItemStyle;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  /** Numeric priority (1..10-ish); bucketed via Settings.priorityRanges. */
  priority?: number;
  /** Numeric difficulty (1..10-ish); bucketed via Settings.difficultyRanges. */
  difficulty?: number;
  status: 'todo' | 'doing' | 'done';
  topicId: string;
  deadline?: Date;
  startDate?: Date;
  /** Parent task id when this task is a subtask (decomposition). */
  parentId?: string | null;
  /** Effective `on-focus`: when true this subtask surfaces in the panels. */
  onFocus?: boolean;
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
  onFocus?: boolean;
  style?: ItemStyle;
}

export interface Deadline {
  id: string;
  title: string;
  date: Date;
  priority?: number;
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
  style: AppStyle;
  density: Density;
  displayStyle: DisplayStyle;
  showWeekends: boolean;
  defaultCalendarView: CalendarView;
  weekStartsOn: DayOfWeek;
  defaultColumnMode: ColumnMode;
  defaultRowMode: RowMode;
  accentColor: string;
  /** Numeric-value buckets for task priority and difficulty. */
  priorityRanges: LevelRanges;
  difficultyRanges: LevelRanges;
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
