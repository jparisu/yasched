import {
  BarChart3,
  Boxes,
  BookOpen,
  Calendar,
  CalendarClock,
  Focus,
  Kanban,
  LayoutGrid,
  ListTree,
  Ruler,
  Settings,
  Share2,
  Sliders,
  Table,
  Timer,
  LucideIcon,
} from 'lucide-react';
import { PanelCategory, PanelId } from '../types';

export interface NavItem {
  id: PanelId;
  label: string;
  category: PanelCategory;
  icon: LucideIcon;
  color: string;
}

export const NAV: NavItem[] = [
  { id: 'main', label: 'Main', category: 'core', icon: LayoutGrid, color: '#0ea5e9' },
  { id: 'stats', label: 'Stats', category: 'core', icon: BarChart3, color: '#3b82f6' },
  { id: 'focus', label: 'Focus', category: 'core', icon: Focus, color: '#06b6d4' },
  { id: 'attributes', label: 'Attributes', category: 'core', icon: Sliders, color: '#64748b' },
  { id: 'settings', label: 'Settings', category: 'core', icon: Settings, color: '#64748b' },

  { id: 'topic-graph', label: 'Graph', category: 'topic', icon: Share2, color: '#ec4899' },
  // Time elapsed / effort is a *topic* view (time used per topic), not a
  // schedule one — it answers "where did my time go", which is a topic question.
  { id: 'effort', label: 'Time elapsed', category: 'topic', icon: Timer, color: '#ec4899' },
  { id: 'topic-manage', label: 'Topics', category: 'topic', icon: ListTree, color: '#ec4899' },

  { id: 'calendar', label: 'Calendar', category: 'event', icon: Calendar, color: '#22c55e' },
  { id: 'agenda', label: 'Agenda', category: 'event', icon: BookOpen, color: '#f59e0b' },
  { id: 'timeline', label: 'Timeline', category: 'event', icon: Ruler, color: '#22c55e' },
  { id: 'event-manage', label: 'Events', category: 'event', icon: Boxes, color: '#22c55e' },

  { id: 'timeboard', label: 'Timeboard', category: 'schedule', icon: CalendarClock, color: '#14b8a6' },
  { id: 'schedule-manage', label: 'Schedules', category: 'schedule', icon: Table, color: '#14b8a6' },

  { id: 'taskboard', label: 'Task board', category: 'task', icon: Kanban, color: '#8b5cf6' },
  { id: 'task-manage', label: 'Tasks', category: 'task', icon: Boxes, color: '#8b5cf6' },
];

export const CATEGORY_ORDER: PanelCategory[] = ['core', 'topic', 'event', 'schedule', 'task'];
