import { ReactNode } from 'react';
import {
  Sparkles,
  Layers,
  FolderTree,
  ListTodo,
  CalendarPlus,
  SquarePen,
  BarChart3,
  BookOpen,
  Calendar,
  CalendarClock,
  Kanban,
  Focus,
  Share2,
  Settings,
  Plus,
  ShieldCheck,
  Repeat,
  Tags,
  FileCode,
} from 'lucide-react';
import { ViewMode } from '../types';
import { EntityKind } from '../api/client';
import { HelpLead, HelpP, HelpH, HelpList, HelpTip, HelpImage, Ui, Code } from './helpUI';

export interface HelpPage {
  id: string;
  title: string;
  icon: ReactNode;
  content: ReactNode;
}

export interface HelpSection {
  title: string;
  pages: HelpPage[];
}

/* -------------------------------------------------------------------------- */
/* Manual content                                                             */
/* -------------------------------------------------------------------------- */

export const HELP_SECTIONS: HelpSection[] = [
  {
    title: 'Getting started',
    pages: [
      {
        id: 'welcome',
        title: 'Welcome to yasched',
        icon: <Sparkles size={16} />,
        content: (
          <>
            <HelpLead>
              <strong>yasched</strong> is a local-first scheduler for your topics, tasks and
              events. One YAML agenda is the single source of truth; every panel in this app is
              just a different lens on it.
            </HelpLead>
            <HelpImage src="/help/statistics.png" label="The yasched app — sidebar, top bar and a panel" />
            <HelpH>Find your way around</HelpH>
            <HelpList
              items={[
                <>
                  The <strong>sidebar</strong> on the left switches between panels (Statistics,
                  Agenda, Calendar, Weekly View, Task Board, Focus, Database Graph, Settings).
                </>,
                <>
                  The <strong>top bar</strong> shows the current panel and holds the{' '}
                  <Ui>+ New</Ui> and <Ui>? Help</Ui> buttons and the theme toggle.
                </>,
                <>
                  This <strong>Help</strong> window is context-aware: open it from any panel and
                  it jumps straight to that panel's page; open it while editing an item and it
                  shows that element's page.
                </>,
              ]}
            />
            <HelpTip>
              Everything runs on your machine. yasched makes no network calls, so your agenda
              never leaves your computer.
            </HelpTip>
          </>
        ),
      },
      {
        id: 'concepts',
        title: 'Core concepts',
        icon: <Layers size={16} />,
        content: (
          <>
            <HelpLead>
              yasched has three things you create — <strong>Topics</strong>,{' '}
              <strong>Tasks</strong> and <strong>Events</strong> — plus two supporting ideas that
              make them powerful: <strong>Traits</strong> and <strong>Schedules</strong>.
            </HelpLead>
            <HelpImage src="/help/graph.png" label="Topics containing tasks and events, with inheritance flowing down" />
            <HelpH>The three elements</HelpH>
            <HelpList
              items={[
                <>
                  <strong>Topic</strong> — an organizational category (e.g. <Code>work</Code>).
                  Topics can nest, and their styling and data flow down to whatever belongs to
                  them.
                </>,
                <>
                  <strong>Task</strong> — a unit of work. It can have a deadline, recur on a
                  schedule, depend on other tasks, or be a subtask of another.
                </>,
                <>
                  <strong>Event</strong> — a time-bound occurrence, usually recurring (a lecture,
                  a stand-up).
                </>,
              ]}
            />
            <HelpH>Two open bags</HelpH>
            <HelpP>
              Every element carries two open maps: <strong>attributes</strong> (semantic data like{' '}
              <Code>priority</Code>, <Code>deadline</Code>, <Code>status</Code>) and{' '}
              <strong>layout</strong> (visual style like colour and shape). Any key is allowed —
              the model stays open.
            </HelpP>
            <HelpH>Inheritance</HelpH>
            <HelpP>
              Attributes, tags and layout are merged in layers, lowest to highest priority:
            </HelpP>
            <HelpTip tone="note">
              <Code>default</Code> &lt; <Code>topic(s)</Code> &lt; <Code>traits</Code> &lt;{' '}
              <Code>parent</Code> &lt; <Code>own</Code>
              <br />
              Higher layers win per attribute key; tags accumulate; backgrounds compose. This is
              why setting a colour on a topic quietly styles everything inside it.
            </HelpTip>
          </>
        ),
      },
    ],
  },
  {
    title: 'Elements',
    pages: [
      {
        id: 'element-topics',
        title: 'Topics',
        icon: <FolderTree size={16} />,
        content: (
          <>
            <HelpLead>
              A <strong>Topic</strong> is a category that groups your tasks and events and passes
              its styling and data down to them.
            </HelpLead>
            <HelpImage src="/help/editor-topic.png" label="Topic editor — parent topics, tags and colour" />
            <HelpList
              items={[
                <>
                  Topics form a <strong>DAG</strong>: a topic can have several parent topics via{' '}
                  <Ui>Parent topics</Ui>. Tags, attributes and layout flow down from parents.
                </>,
                <>
                  Give a topic a <Ui>Color</Ui> and every task/event referencing it inherits that
                  colour unless it overrides it.
                </>,
                <>
                  Tasks and events join a topic through their own <Ui>Topics</Ui> selector — a
                  task may belong to several topics.
                </>,
              ]}
            />
            <HelpTip>
              Start by sketching a few broad topics (Work, Study, Home). Colour them once and the
              whole app becomes readable at a glance.
            </HelpTip>
          </>
        ),
      },
      {
        id: 'element-tasks',
        title: 'Tasks',
        icon: <ListTodo size={16} />,
        content: (
          <>
            <HelpLead>
              A <strong>Task</strong> is a unit of work — one-off with a deadline, recurring on a
              schedule, or a subtask that builds toward a larger one.
            </HelpLead>
            <HelpImage src="/help/editor-task.png" label="Task editor — status, priority, deadline, relations" />
            <HelpH>What a task can carry</HelpH>
            <HelpList
              items={[
                <>
                  <Ui>Status</Ui> (<Code>todo</Code> / <Code>doing</Code> / <Code>done</Code>),{' '}
                  <Ui>Priority</Ui> and a <Ui>Deadline</Ui>.
                </>,
                <>
                  <Ui>Schedules</Ui> to make it recurring, or a{' '}
                  <Ui>Parent task</Ui> to make it a subtask (it inherits the parent's topics,
                  tags, attributes and layout).
                </>,
                <>
                  <Ui>Relations</Ui> to other tasks: <Code>requires</Code>, <Code>needs</Code>,{' '}
                  <Code>connected</Code>, <Code>similar</Code>.
                </>,
                <>
                  Event links, so a task can, for example, use an event as its deadline or as
                  context.
                </>,
              ]}
            />
            <HelpTip tone="note">
              A task belongs to zero or more topics. Priority, deadline and any other{' '}
              <em>attribute</em> can also be inherited from a topic or a trait instead of being
              set directly.
            </HelpTip>
          </>
        ),
      },
      {
        id: 'element-events',
        title: 'Events',
        icon: <CalendarPlus size={16} />,
        content: (
          <>
            <HelpLead>
              An <strong>Event</strong> is a time-bound occurrence. Give it one or more{' '}
              <Ui>Schedules</Ui> and yasched expands them into concrete dated occurrences.
            </HelpLead>
            <HelpImage src="/help/editor-event.png" label="Event editor — schedules and location" />
            <HelpList
              items={[
                <>
                  Events are usually <strong>recurring</strong> (a weekly lecture, a daily
                  stand-up) — see the <strong>Schedules</strong> page for the five schedule kinds.
                </>,
                <>
                  A <strong>sub-event</strong> sets a <Ui>Parent event</Ui> and overrides a single
                  occurrence (e.g. move a room for one week).
                </>,
                <>
                  If a sub-event's effective status is <Code>cancelled</Code>, that one occurrence
                  is removed entirely.
                </>,
                <>
                  Events carry a <Ui>Location</Ui> and, like everything, topics, tags and layout.
                </>,
              ]}
            />
          </>
        ),
      },
      {
        id: 'element-editor',
        title: 'The element editor',
        icon: <SquarePen size={16} />,
        content: (
          <>
            <HelpLead>
              Creating or editing anything opens the <strong>element editor</strong> — the panel
              that slides in from the right. It has the same shape for topics, tasks and events,
              showing only the fields that apply.
            </HelpLead>
            <HelpImage src="/help/editor-task.png" label="The element editor drawer, open on the right" />
            <HelpH>Fields you'll see</HelpH>
            <HelpList
              items={[
                <>
                  <Ui>Id</Ui> — a unique identifier (fixed once created) and a display{' '}
                  <Ui>Name</Ui>.
                </>,
                <>
                  <Ui>Topics</Ui> / <Ui>Parent topics</Ui>, <Ui>Traits</Ui>, <Ui>Tags</Ui> and a{' '}
                  <Ui>Color</Ui>.
                </>,
                <>
                  For tasks: <Ui>Status</Ui>, <Ui>Priority</Ui>, <Ui>Deadline</Ui> and{' '}
                  <Ui>Relations</Ui>. For events: <Ui>Location</Ui>.
                </>,
                <>
                  <Ui>Schedules</Ui> (tasks &amp; events) and an <Ui>Other attributes</Ui> section
                  where you can add any custom key/value.
                </>,
              ]}
            />
            <HelpTip>
              With the editor open, press <Ui>? Help</Ui> in the top bar and this manual jumps
              straight to the page for the element you're editing.
            </HelpTip>
            <HelpP>
              Save writes changes back to your agenda; <Ui>Delete</Ui> (when editing) removes the
              element after a confirmation. Close with <Ui>Cancel</Ui>, the <Ui>✕</Ui>, or by
              clicking outside.
            </HelpP>
          </>
        ),
      },
    ],
  },
  {
    title: 'Panels',
    pages: [
      {
        id: 'panel-statistics',
        title: 'Statistics',
        icon: <BarChart3 size={16} />,
        content: (
          <>
            <HelpLead>
              An at-a-glance overview of your agenda: totals, completion rate and breakdowns by
              topic and priority.
            </HelpLead>
            <HelpImage src="/help/statistics.png" label="Statistics panel — summary cards and charts" />
            <HelpList
              items={[
                <>Counts of tasks, events and topics, plus how many tasks are done vs pending.</>,
                <>Distribution of tasks across topics and priorities.</>,
                <>Use it as a health check before diving into the working panels.</>,
              ]}
            />
          </>
        ),
      },
      {
        id: 'panel-agenda',
        title: 'Agenda',
        icon: <BookOpen size={16} />,
        content: (
          <>
            <HelpLead>
              A week-at-a-time list view of what's happening: events and tasks grouped by day.
            </HelpLead>
            <HelpImage src="/help/agenda.png" label="Agenda panel — a week of tasks and events by day" />
            <HelpList
              items={[
                <>Move between weeks with the arrows, or jump back with <Ui>Today</Ui>.</>,
                <>Each day shows its events and any tasks whose deadline or start falls that day.</>,
                <>
                  Adjust card look (style, density, shape) from <strong>Settings</strong> or the
                  panel's display controls.
                </>,
              ]}
            />
          </>
        ),
      },
      {
        id: 'panel-calendar',
        title: 'Calendar',
        icon: <Calendar size={16} />,
        content: (
          <>
            <HelpLead>
              A traditional calendar grid — daily, weekly, monthly or yearly — showing events and
              dated tasks in place.
            </HelpLead>
            <HelpImage src="/help/calendar.png" label="Calendar panel — month grid with events" />
            <HelpList
              items={[
                <>Switch the calendar range and navigate between periods with the controls.</>,
                <>Recurring events appear on every date their schedule produces.</>,
                <>Colours come from each item's topic, so months stay readable at a glance.</>,
              ]}
            />
          </>
        ),
      },
      {
        id: 'panel-weekly',
        title: 'Weekly View',
        icon: <CalendarClock size={16} />,
        content: (
          <>
            <HelpLead>
              A class-timetable grid of your <strong>recurring weekly</strong> events — days
              across, time down.
            </HelpLead>
            <HelpImage src="/help/weekly.png" label="Weekly View — timetable grid of weekly events" />
            <HelpList
              items={[
                <>Only events with a <Code>weekly</Code> schedule appear here.</>,
                <>Each block is placed by its start time and sized by its duration.</>,
                <>Click a block to open the element editor for that event.</>,
              ]}
            />
            <HelpTip tone="note">
              If an event isn't showing up, check that it has a <Code>weekly</Code> schedule with
              week days and a start time — see the <strong>Schedules</strong> page.
            </HelpTip>
          </>
        ),
      },
      {
        id: 'panel-taskboard',
        title: 'Task Board',
        icon: <Kanban size={16} />,
        content: (
          <>
            <HelpLead>
              A kanban board of your tasks. Group the columns by stage, priority or topic.
            </HelpLead>
            <HelpImage src="/help/taskboard.png" label="Task Board — kanban columns of task cards" />
            <HelpList
              items={[
                <>
                  Choose how columns are grouped (by <Code>status</Code>, priority or topic) from
                  the board's controls.
                </>,
                <>Click any card to open the element editor and change its status, priority, etc.</>,
                <>Cards are coloured by topic so related work clusters visually.</>,
              ]}
            />
          </>
        ),
      },
      {
        id: 'panel-focus',
        title: 'Focus',
        icon: <Focus size={16} />,
        content: (
          <>
            <HelpLead>
              A stripped-down view that surfaces what deserves your attention right now — the
              most pressing tasks without the surrounding noise.
            </HelpLead>
            <HelpImage src="/help/focus.png" label="Focus panel — prioritized short list" />
            <HelpList
              items={[
                <>Great for a daily start: pick the next thing and go.</>,
                <>Priority and deadlines drive what rises to the top.</>,
              ]}
            />
          </>
        ),
      },
      {
        id: 'panel-graph',
        title: 'Database Graph',
        icon: <Share2 size={16} />,
        content: (
          <>
            <HelpLead>
              A visual map of your whole agenda: topics as areas, with tasks and events inside
              them, connected by their relationships.
            </HelpLead>
            <HelpImage src="/help/graph.png" label="Database Graph — topics as areas, tasks (▭) and events (◆)" />
            <HelpList
              items={[
                <>Tasks are drawn as rounded rectangles (▭) and events as diamonds (◆).</>,
                <>
                  Arrows use UML-style heads for the kind of link: dependency, composition,
                  aggregation and generalization. A legend explains each.
                </>,
                <>Click a node to open its element editor.</>,
              ]}
            />
            <HelpTip>
              The graph is the fastest way to spot orphaned items or a tangle of dependencies you
              didn't realize you had.
            </HelpTip>
          </>
        ),
      },
      {
        id: 'panel-settings',
        title: 'Settings',
        icon: <Settings size={16} />,
        content: (
          <>
            <HelpLead>
              Control how the app looks and behaves: theme, card style, density, week start,
              default calendar view and board grouping.
            </HelpLead>
            <HelpImage src="/help/settings.png" label="Settings panel — appearance and defaults" />
            <HelpList
              items={[
                <>
                  <strong>Appearance:</strong> light/dark theme, card shape, display style and
                  density.
                </>,
                <>
                  <strong>Defaults:</strong> which day the week starts on, the default calendar
                  view, and how the Task Board groups columns.
                </>,
                <>Settings are saved in your browser, separate from the agenda file itself.</>,
              ]}
            />
          </>
        ),
      },
    ],
  },
  {
    title: 'Features',
    pages: [
      {
        id: 'feature-new',
        title: 'Creating & editing',
        icon: <Plus size={16} />,
        content: (
          <>
            <HelpLead>
              Build your agenda right from the app — no YAML editing required.
            </HelpLead>
            <HelpImage src="/help/new-menu.png" label="The + New menu open in the top bar" />
            <HelpList
              items={[
                <>
                  <Ui>+ New</Ui> in the top bar opens a menu to create a <strong>Topic</strong>,{' '}
                  <strong>Task</strong> or <strong>Event</strong>.
                </>,
                <>
                  Click an item almost anywhere — a Task Board card, a Database Graph node, a
                  Weekly View block — to open its editor.
                </>,
                <>Changes are written straight back to your agenda YAML when you save.</>,
              ]}
            />
            <HelpTip tone="warn">
              Agendas split across files with include directives (<Code>__file__</Code> /{' '}
              <Code>__ext__</Code>) are <strong>browse-only</strong> — saving would flatten their
              structure. The bundled demo is one such example. Edit those files as YAML directly.
            </HelpTip>
          </>
        ),
      },
      {
        id: 'feature-schedules',
        title: 'Schedules & recurrence',
        icon: <Repeat size={16} />,
        content: (
          <>
            <HelpLead>
              A <strong>Schedule</strong> describes <em>when</em> something happens. Events and
              recurring tasks can have one or more. yasched expands them into concrete dated
              occurrences.
            </HelpLead>
            <HelpImage src="/help/editor-schedule.png" label="Schedule editor — choosing a schedule type" />
            <HelpH>The five kinds</HelpH>
            <HelpList
              items={[
                <>
                  <Code>weekly</Code> — pick week days + a start time and end time or duration.
                </>,
                <>
                  <Code>monthly</Code> — a day of the month (1–31, clamped to the month's end).
                </>,
                <>
                  <Code>yearly</Code> — a month and day.
                </>,
                <>
                  <Code>single_day</Code> — one specific date.
                </>,
                <>
                  <Code>multi_day</Code> — a start date and an end date.
                </>,
              ]}
            />
            <HelpTip tone="note">
              Times are 24-hour (<Code>09:00</Code>). Durations look like <Code>30m</Code>,{' '}
              <Code>1h</Code>, <Code>1h30m</Code>. Dates are ISO (<Code>2026-10-20</Code>).
            </HelpTip>
          </>
        ),
      },
      {
        id: 'feature-traits',
        title: 'Traits & inheritance',
        icon: <Tags size={16} />,
        content: (
          <>
            <HelpLead>
              A <strong>Trait</strong> is a named, reusable bundle of attributes and/or layout you
              can attach to any element — define "urgent" once, apply it everywhere.
            </HelpLead>
            <HelpImage src="/help/editor-task.png" label="Traits selector in the element editor" />
            <HelpList
              items={[
                <>
                  Attach traits from the <Ui>Traits</Ui> selector in the editor; they merge as a
                  layer between topics and the element's own values.
                </>,
                <>A trait with only layout is effectively a "named style" you can reuse.</>,
                <>
                  Combined with topic inheritance, traits keep your agenda DRY: change the trait,
                  and everything using it updates.
                </>,
              ]}
            />
            <HelpTip tone="note">
              Remember the precedence: <Code>default</Code> &lt; <Code>topics</Code> &lt;{' '}
              <Code>traits</Code> &lt; <Code>parent</Code> &lt; <Code>own</Code>. An element's own
              value always wins.
            </HelpTip>
          </>
        ),
      },
      {
        id: 'feature-validation',
        title: 'Validation',
        icon: <ShieldCheck size={16} />,
        content: (
          <>
            <HelpLead>
              yasched continuously checks your agenda and shows a banner summarizing any problems
              it finds.
            </HelpLead>
            <HelpImage label="Validation banner with expandable issue list" />
            <HelpList
              items={[
                <>
                  <strong>Errors</strong> — unknown references, dependency cycles, impossible
                  schedules.
                </>,
                <>
                  <strong>Warnings</strong> — duplicate ids, redundant times, and other smells.
                </>,
                <>Expand the banner to see each issue, its element, and a short code.</>,
              ]}
            />
            <HelpTip>
              From the command line, <Code>yasched check --agenda FILE</Code> runs the same checks
              without the app.
            </HelpTip>
          </>
        ),
      },
      {
        id: 'feature-agenda-file',
        title: 'The agenda file',
        icon: <FileCode size={16} />,
        content: (
          <>
            <HelpLead>
              Your entire agenda lives in one YAML file (by default{' '}
              <Code>~/.yasched/agenda.yaml</Code>). The app reads and writes it; you can also edit
              it by hand.
            </HelpLead>
            <HelpImage label="An agenda.yaml opened in an editor" />
            <HelpList
              items={[
                <>
                  Up to five top-level keys, all optional: <Code>default</Code>, <Code>traits</Code>
                  , <Code>topics</Code>, <Code>events</Code>, <Code>tasks</Code>.
                </>,
                <>
                  Large agendas can be split with <Code>__file__</Code> (splice a file in place)
                  and <Code>__ext__</Code> (extend a base file with overrides).
                </>,
                <>
                  <Code>yasched init</Code> creates a starter file; <Code>yasched check</Code>{' '}
                  validates it; <Code>yasched serve</Code> runs this app.
                </>,
              ]}
            />
            <HelpTip tone="warn">
              Files that use <Code>__file__</Code> / <Code>__ext__</Code> includes open in
              browse-only mode in the app. Edit them directly in YAML to preserve their structure.
            </HelpTip>
          </>
        ),
      },
    ],
  },
];

/* -------------------------------------------------------------------------- */
/* Lookups                                                                     */
/* -------------------------------------------------------------------------- */

export const ALL_PAGES: HelpPage[] = HELP_SECTIONS.flatMap((s) => s.pages);
export const DEFAULT_PAGE_ID = 'welcome';

/** Which manual page a panel/view maps to. */
export const VIEW_TO_PAGE: Record<ViewMode, string> = {
  statistics: 'panel-statistics',
  agenda: 'panel-agenda',
  calendar: 'panel-calendar',
  weekly: 'panel-weekly',
  taskboard: 'panel-taskboard',
  focus: 'panel-focus',
  graph: 'panel-graph',
  element: 'panel-graph',
  settings: 'panel-settings',
};

/** Which manual page the element editor maps to, per element kind. */
export const KIND_TO_PAGE: Record<EntityKind, string> = {
  topics: 'element-topics',
  tasks: 'element-tasks',
  events: 'element-events',
};

export function findPageIndex(id: string): number {
  const i = ALL_PAGES.findIndex((p) => p.id === id);
  return i === -1 ? 0 : i;
}
