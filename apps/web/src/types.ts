// API types — mirror the shapes served by src/yasched/serving.

export type ElementType = 'topic' | 'event' | 'task' | 'schedule';

export interface LayoutDTO {
  background?: { color: string; gradient_color?: string };
  border?: { color: string; width: string; style: string };
  icon?: { type: string; value: string };
  pin?: { color: string };
  shape?: string;
  animation?: string;
  hover_animation?: string;
  format?: { font?: string; font_size?: string; font_color?: string; text_align?: string };
}

export interface ConnectionDTO {
  to: string;
  relation: string;
}

export interface IncomingDTO {
  from: string;
  relation: string;
}

/** A resolved element as returned by GET /api/elements. */
export interface ElementDTO {
  id: string;
  type: ElementType;
  virtual: boolean;
  attributes: Record<string, unknown>;
  layout: LayoutDTO;
  parents: string[];
  mainParent: string | null;
  topic: string | null;
  connections: ConnectionDTO[];
  incoming: IncomingDTO[];
}

export interface AttributeDefinitionDTO {
  name: string;
  valueType: string;
  appliesTo: ElementType[];
  builtin: boolean;
  inherits: boolean;
  enumValues?: string[];
  min?: number;
  max?: number;
  layout?: LayoutDTO;
}

export interface PayloadDTO {
  window: { start: string; end: string };
  definitions: AttributeDefinitionDTO[];
  elements: ElementDTO[];
}

export interface MetaDTO {
  agenda: string;
  multiFile: boolean;
  counts: { topics: number; events: number; tasks: number; schedules: number };
}

export interface ValidationIssueDTO {
  severity: 'error' | 'warning';
  code: string;
  message: string;
  entityKind: string;
  entityId: string;
}

export interface ValidationDTO {
  issues: ValidationIssueDTO[];
  errorCount: number;
  warningCount: number;
}

/** Per-topic time used (minutes), own and rolled up through subtopics. */
export interface TopicEffort {
  ownEvents: number;
  ownTasks: number;
  rolledEvents: number;
  rolledTasks: number;
}

export interface EffortDTO {
  window: { start: string; end: string };
  topics: Record<string, TopicEffort>;
}

/** The write shape accepted by POST/PUT /api/elements. */
export interface ElementSpec {
  id: string;
  type: ElementType;
  directParents?: string[];
  attributes?: Record<string, unknown>;
  layout?: LayoutDTO;
}

// ---- UI navigation --------------------------------------------------------

export type PanelId =
  | 'main'
  | 'stats'
  | 'focus'
  | 'attributes'
  | 'settings'
  | 'topic-graph'
  | 'topic-manage'
  | 'calendar'
  | 'agenda'
  | 'timeline'
  | 'event-manage'
  | 'timeboard'
  | 'effort'
  | 'schedule-manage'
  | 'taskboard'
  | 'task-manage';

export type PanelCategory = 'core' | 'topic' | 'event' | 'schedule' | 'task';
