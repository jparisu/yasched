import { Task, EventItem, Deadline, Topic, GraphNode, Settings, ItemStyle, CardShape } from '../types';

const createStyle = (bg: string, left: string, shape: CardShape = 'rounded'): ItemStyle => ({
  backgroundColor: bg,
  leftColor: left,
  shape,
});

export const mockTopics: Topic[] = [
  {
    id: 'work',
    name: 'Work',
    color: '#3b82f6',
    style: createStyle('#dbeafe', '#3b82f6', 'rounded'),
  },
  {
    id: 'personal',
    name: 'Personal',
    color: '#10b981',
    style: createStyle('#d1fae5', '#10b981', 'curvy'),
  },
  {
    id: 'study',
    name: 'Study',
    color: '#f59e0b',
    style: createStyle('#fef3c7', '#f59e0b', 'sticky'),
  },
  {
    id: 'health',
    name: 'Health',
    color: '#f43f5e',
    style: createStyle('#ffe4e6', '#f43f5e', 'rounded'),
  },
  {
    id: 'projects',
    name: 'Projects',
    color: '#8b5cf6',
    style: createStyle('#ede9fe', '#8b5cf6', 'cloudy'),
  },
  {
    id: 'creative',
    name: 'Creative',
    color: '#ec4899',
    style: createStyle('#fce7f3', '#ec4899', 'curvy'),
  },
  {
    id: 'home',
    name: 'Home',
    color: '#06b6d4',
    style: createStyle('#cffafe', '#06b6d4', 'rounded'),
  },
];

export const mockTasks: Task[] = [
  {
    id: 'task1',
    title: 'Prepare weekly planning',
    description: 'Review goals and plan upcoming week activities',
    priority: 8,
    status: 'todo',
    topicId: 'work',
    deadline: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
    style: createStyle('#dbeafe', '#3b82f6', 'rounded'),
    createdAt: new Date(),
  },
  {
    id: 'task2',
    title: 'Submit quarterly report',
    description: 'Finalize and submit the quarterly report',
    priority: 8,
    status: 'doing',
    topicId: 'work',
    deadline: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000),
    style: createStyle('#dbeafe', '#3b82f6', 'sticky'),
    createdAt: new Date(),
  },
  {
    id: 'task3',
    title: 'Review study notes',
    description: 'Go through lecture notes from this week',
    priority: 5,
    status: 'todo',
    topicId: 'study',
    style: createStyle('#fef3c7', '#f59e0b', 'sticky'),
    createdAt: new Date(),
  },
  {
    id: 'task4',
    title: 'Team meeting prep',
    description: 'Prepare presentation for team sync',
    priority: 5,
    status: 'doing',
    topicId: 'projects',
    deadline: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
    style: createStyle('#ede9fe', '#8b5cf6', 'cloudy'),
    createdAt: new Date(),
  },
  {
    id: 'task5',
    title: 'Documentation update',
    description: 'Update project documentation files',
    priority: 2,
    status: 'done',
    topicId: 'work',
    style: createStyle('#dbeafe', '#3b82f6', 'curvy'),
    createdAt: new Date(),
  },
  {
    id: 'task6',
    title: 'Plan focus sessions',
    description: 'Schedule deep work blocks for next week',
    priority: 5,
    status: 'todo',
    topicId: 'personal',
    style: createStyle('#d1fae5', '#10b981', 'curvy'),
    createdAt: new Date(),
  },
  {
    id: 'task7',
    title: 'Morning exercise',
    description: '30 min yoga and stretching',
    priority: 2,
    status: 'todo',
    topicId: 'health',
    style: createStyle('#ffe4e6', '#f43f5e', 'rounded'),
    createdAt: new Date(),
  },
  {
    id: 'task8',
    title: 'Read new articles',
    description: 'Catch up on saved reading list',
    priority: 2,
    status: 'todo',
    topicId: 'study',
    style: createStyle('#fef3c7', '#f59e0b', 'rounded'),
    createdAt: new Date(),
  },
  {
    id: 'task9',
    title: 'Sketch new ideas',
    description: 'Creative brainstorming session',
    priority: 5,
    status: 'todo',
    topicId: 'creative',
    style: createStyle('#fce7f3', '#ec4899', 'cloudy'),
    createdAt: new Date(),
  },
  {
    id: 'task10',
    title: 'Clean workspace',
    description: 'Organize desk and digital files',
    priority: 2,
    status: 'done',
    topicId: 'home',
    style: createStyle('#cffafe', '#06b6d4', 'curvy'),
    createdAt: new Date(),
  },
  {
    id: 'task11',
    title: 'Prepare lunch for week',
    description: 'Meal prep for healthy eating',
    priority: 5,
    status: 'todo',
    topicId: 'health',
    deadline: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000),
    style: createStyle('#ffe4e6', '#f43f5e', 'sticky'),
    createdAt: new Date(),
  },
];

export const mockEvents: EventItem[] = [
  {
    id: 'evt1',
    title: 'Morning Standup',
    date: new Date(),
    startTime: '09:00',
    endTime: '09:30',
    topicId: 'work',
    recurring: true,
    style: createStyle('#dbeafe', '#3b82f6', 'rounded'),
  },
  {
    id: 'evt2',
    title: 'Project Review',
    date: new Date(),
    startTime: '14:00',
    endTime: '15:30',
    topicId: 'projects',
    description: 'Quarterly project review with stakeholders',
    style: createStyle('#ede9fe', '#8b5cf6', 'cloudy'),
  },
  {
    id: 'evt3',
    title: 'Focus Time',
    date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000),
    startTime: '10:00',
    endTime: '12:00',
    topicId: 'personal',
    style: createStyle('#d1fae5', '#10b981', 'curvy'),
  },
  {
    id: 'evt4',
    title: 'Client Presentation',
    date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
    startTime: '16:00',
    endTime: '17:00',
    topicId: 'work',
    style: createStyle('#dbeafe', '#3b82f6', 'rounded'),
  },
  {
    id: 'evt5',
    title: 'Weekly Planning',
    date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    startTime: '08:00',
    endTime: '09:00',
    topicId: 'personal',
    recurring: true,
    style: createStyle('#d1fae5', '#10b981', 'sticky'),
  },
  {
    id: 'evt6',
    title: 'Yoga Class',
    date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000),
    startTime: '18:00',
    endTime: '19:00',
    topicId: 'health',
    recurring: true,
    style: createStyle('#ffe4e6', '#f43f5e', 'rounded'),
  },
  {
    id: 'evt7',
    title: 'Study Group',
    date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
    startTime: '19:00',
    endTime: '21:00',
    topicId: 'study',
    style: createStyle('#fef3c7', '#f59e0b', 'sticky'),
  },
];

export const mockDeadlines: Deadline[] = [
  {
    id: 'dl1',
    title: 'Report Submission',
    date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000),
    priority: 8,
    topicId: 'work',
    style: createStyle('#fee2e2', '#ef4444', 'rounded'),
  },
  {
    id: 'dl2',
    title: 'Documentation Due',
    date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
    priority: 5,
    topicId: 'projects',
    style: createStyle('#ede9fe', '#8b5cf6', 'cloudy'),
  },
  {
    id: 'dl3',
    title: 'Assignment Deadline',
    date: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000),
    priority: 8,
    topicId: 'study',
    style: createStyle('#fef3c7', '#f59e0b', 'sticky'),
  },
  {
    id: 'dl4',
    title: 'Sprint Review',
    date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    priority: 5,
    topicId: 'work',
    style: createStyle('#dbeafe', '#3b82f6', 'rounded'),
  },
];

export const mockGraphNodes: GraphNode[] = [
  { id: 'gn1', label: 'Tasks', type: 'task', x: 200, y: 150, connections: ['gn2', 'gn3', 'gn5'], description: 'Individual task entries' },
  { id: 'gn2', label: 'Subtasks', type: 'task', x: 350, y: 100, connections: ['gn1'], description: 'Smaller task components' },
  { id: 'gn3', label: 'Events', type: 'event', x: 350, y: 200, connections: ['gn1', 'gn6'], description: 'Calendar events' },
  { id: 'gn4', label: 'Deadlines', type: 'deadline', x: 500, y: 150, connections: ['gn1', 'gn3'], description: 'Important dates' },
  { id: 'gn5', label: 'Topics', type: 'topic', x: 200, y: 300, connections: ['gn6', 'gn1'], description: 'Organization categories' },
  { id: 'gn6', label: 'Subtopics', type: 'subtopic', x: 350, y: 300, connections: ['gn5'], description: 'Nested categories' },
  { id: 'gn7', label: 'Styles', type: 'style', x: 500, y: 300, connections: ['gn1', 'gn3'], description: 'Visual customization' },
  { id: 'gn8', label: 'Recurring', type: 'recurring', x: 650, y: 200, connections: ['gn3', 'gn1'], description: 'Repeating items' },
];

export const defaultSettings: Settings = {
  theme: 'light',
  style: 'simple',
  density: 'comfortable',
  displayStyle: 'square',
  showWeekends: true,
  defaultCalendarView: 'monthly',
  weekStartsOn: 'monday',
  defaultColumnMode: 'stage',
  defaultRowMode: 'time',
  accentColor: '#3b82f6',
  priorityRanges: { lowMax: 3, medMax: 6 },
  difficultyRanges: { lowMax: 3, medMax: 6 },
};

export const getTopicStyle = (topicId: string): ItemStyle => {
  const topic = mockTopics.find(t => t.id === topicId);
  return topic?.style || { backgroundColor: '#f1f5f9', leftColor: '#94a3b8', shape: 'rounded' };
};

export const getItemStyle = (item: { style?: ItemStyle; topicId?: string }): ItemStyle => {
  if (item.style) return item.style;
  if (item.topicId) return getTopicStyle(item.topicId);
  return { backgroundColor: '#f1f5f9', leftColor: '#94a3b8', shape: 'rounded' };
};
