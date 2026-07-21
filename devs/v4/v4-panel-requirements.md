
# Elements

The elements are the main entities that will be managed in the app.
These are divided in:

- Topic: logic division for elements.
- Events: time related elements.
- Tasks: task related elements.
- Schedules: element with recurrent timing to auto-generate events or tasks.

Many elements will have connections between them: parent-child connection, topic related, locked or paused until another task is completed, etc.

## Sub-elements

Some elements allow sub-elements. These will be normal elements, but the app could show them in a different way, for instance, in a tree view.

- Task: subtasks will represent simpler tasks that are part of a bigger task. The parent task will be completed when all subtasks are completed.
- Topic: subtopics will represent a more specific topic that is part of a bigger topic.
- Schedule: subschedules will represent a more specific schedule, for instance a daily schedule inside a weekly one.

Sub-elements could have its own sub-elements, and so on.

## Auto-elements

Some elements will generate other elements automatically.
For instance, a schedule will generate events or tasks automatically depending on its configuration, or a task could generate deadlines, etc.

These elements will be treated as elements or sub-elements, but always keeping the connection with their parent element.

## Element logic

Every element (topic, event, task) will have a `DirectParents` list of entities.
In order to manage the element logic and interconnections, we are going to use a priority list of elements that are "parent" of the current one.
Let's call `Parents` the real list of parents for the element, that are recursively calculated from the `DirectParents` list.
This works as follows: the first element in the list is the "Main Parent" of the current element, then, all parents of "Main Parent" will be used as parents of the current element recursively.

For instance, let's imagine the following elements with the following `DirectParents` list:
- `A`: []
- `B`: [A]
- `C`: [A]
- `D`: [B,A]
- `E`: [C,D]

Then, the list of `Parents` for `E` will be:
- `E` parents: [C,A,D,B]

We call `MainParent` the first element in the `Parents` list.
This would be use differently as the other parents in some cases, like layout.
Some elements like sub-elements and auto-elements will have their `MainParent` as the element that generated them, and this will be forced.

### Topic

Each element may be connected to several topics.
However, only 1 topic is `Topic` of the element.
This is the first topic that appears in its `Parents` list.
This will be used for sorting purposes.

## Attributes

The attributes will be a set of elements that could be configured by the user to customize their elements.
These will be a name-value pair.
In general, the user will set its own attributes giving them capabilities such as:

- limit to element type
- determine type of value (string, number, date, etc.)
- set layout to specific attribute

Let's give an example:
A user can create an attribute `difficulty` with value type `number` between 1 and 10 and limit it to `task` elements.
Then, the user can create a layout for this attribute, that will be used in all tasks that have this attribute defined such as: over 9, the task will use red border.

### Built-in attributes

There are some attributes that will be built-in in the app, so they are created by default:

- `focus` <bool>: whether an element is focused or not. This will be used to highlight the element in the interface, or select which elements will be shown in some panels.
- `location` <string>: the location of the event. It could be a string with the address or name of the place.
- For tasks:
    - `status` <enum>: the status of the task. It could be: `not started`, `in progress`, `completed`, `paused`, `cancelled`.
    - `priority` <int>: the priority of the task. It could be between 0 and 10, being 0 the lowest priority and 10 the highest.
    - `difficulty` <number>: the difficulty of the task. It could be a number between 0 and 10.

## Inheritance

Most elements share same values: name, description, topic, layout, etc. apart from specific values: attributes, dates, etc.

Any value could be not set in any element.
In this case, the value will be inherited from the first parent in `Parents` list that has such value defined.

---

# Element types

Different element types may have different values or characteristics:

## Event

- has a start and end date (if the same, second must not appear)
- duration (could be none)
- reminders (could be none) -> generates events of class `reminder` (auto-generated) with the same name and description, but with the date of the reminder.

## Task

- has a deadline date (could be none) -> generates events of class `deadline` (auto-generated) with the same name and description, but with the date of the deadline.
- reminders (could be none) -> (similar as events)

## Schedule

- Daily: generates events or tasks for at a specific time.
- Weekly: generates events or tasks for days of the week. Each element could have a daily schedule, or generic "all day" schedule.
- Monthly: generates events or tasks for days of the month. Each element could have a daily schedule, or generic "all day" schedule.

---

# Layout

The layout is the visual representation of the elements.
This is a set values that could be set in every element independently, or inherited from its parents.

## Layout

Each element would have its own layout, that by default will have every attribute to `None`.
Every attribute to `None` means that such attribute is calculated following the `Layout hierarchy` explained below.

### Layout hierarchy

In order to decide which layout to use for each element, we will use the following hierarchy:

1. Element layout: if the element has any layout defined, use it.
2. Parent layout: if the element has any layout not defined, use the `MainParent` layout for such value.
3. Topic layout: if the element has any layout not defined, use the `Topic` layout for such value.
4. Attribute layout: if the element has any layout not defined, use the first attribute layout that is defined in the element for such value.

Be aware that the layout may be partially defined, so if some attributes are not defined, we will use the next step in the hierarchy.

## Element view

When listing the elements, 3 different views will be available to the user, depending on the panel and the context:

- **Card view**: show the element in a card with the name and information: date, duration, atts, icon, etc. These cards will be resizable to the information that is being shown. The layout in use will be:
    - all

- **Line view**: show the element in a line with the name. All elements will use same size. The layout in use will be:
    - background color
    - border
    - pin
    - animations

- **Point view**: show the element as a point or small block with no info. All elements will use same size. The layout in use will be:
    - background color
    - border
    - animations

---

# Panel requirements

Panels are each of the tabs that make up the visual interface.
Each panel would have its own responsabilities and behavior, however, several panels must share common code as they could re-use the same components or logic.

Panels will be divided in categories.
The panels will be all in left side menu.
Different categories will be together and separated by a simple line divider.
Even when they do not share category, panels from different categories can share elements, logic, or even be interconnected.

- **Core**: panels to control the app, see stats, manage elements or main information.
- **Topic**: panels for topic management.
- **Event**: panels for timing related elements.
- **Schedule**: panels for recurrent tasks and events.
- **Task**: panels for task related elements.


## Element management

These are panels that allow to easily select between elements and modify them.
In the left, there will be a collapsible column with the elements sorted by topics. Remember that topics follow a hierarchical structure, so it will be like a file explorer tree view.
Add collapse all and expand all buttons.

In the central part, there will be the characteristics of the selected element, with the ability to modify them:
name, description, attributes, dates, etc.
Depending on the type of element, the characteristics will be different.
Make this collapsible as well.

Below that, there will be a collapsible block with layout information, with the ability to modify them.


## Core panels

### Main

TODO

### Stats

TODO

### Settings

TODO

### Focus

TODO

## Topic panels

### Graph

A visualization of the topics.
Select between 2 views: tree and graph.
In graph, the sub-topics are inside their parent topic.
Show in each topic number of elements (events, tasks, topics, schedules) as stats, that can be activated or deactivated.

### Time elapsed

A statistical panel to show topics in file-tree view with different stats: time elapsed, number of events, number of tasks, etc.

### Topic management

Topic management panel.

## Event panels

### Calendar

A calendar view showing the events in a visual way by layout
View selection between: day, week, month, year.
Buttons to move forward, backward, and jump to today.
2 views for elements: line and point

### Agenda

An paper-agenda-like view for a week showing in the left from monday to wednesday and in the right from thursday to sunday, being weekend in 2 columns in the right.
It shows the number of day and the events.
All views for elements.

### Timeline

Events in point format in a line view.
Allow linear or logaritmic scale.
Allow to redimension the timeline by zooming in and out. Depending on the zoom, show day information (hours, days, months, etc.)
On hover in an element, show the card below it.

### Event management

Event management panel.

## Task panels

### Taskboard

A kanban-like view for tasks, with the ability to select in columns and rows the filters: topic, attributes (status, priority, difficulty, etc.), dates (deadline sort), etc.
It must allow to move tasks from one column to another in order to change their attributes (not important info as topic or such).

### Task management

Task management panel.

## Schedule panels

### Timeboard

This is a visualization of schedules in a timeline view, showing the events and tasks generated by the schedules.
Allow month, week, day view.
Only schedules elements and their generated elements will be shown.
This is a view to organize a generic month/week/day, and not to see the details of each event or task.
However, in different moments of time there may be different schedules (1 semester vs 2 semester) so the app must allow selection of date to visualize, similar to calendar.

### Schedule management

Schedule management panel.
