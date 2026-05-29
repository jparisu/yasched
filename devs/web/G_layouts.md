# G — Layouts

## G1 · Layout Gallery — REQUIREMENT

- Displayed as a **card grid** with live visual previews.
- Each card renders the layout's actual style: background fill or gradient,
  border (type, width, color), icon (if set).
- Cards show the layout id as a label below the preview.
- Clicking a card selects it and opens the detail panel.

## G2 · Layout Detail Panel — REQUIREMENT

Shown alongside the gallery (right panel or slide-in drawer) when a layout is selected:

- **Full style breakdown:** all fields listed — background type + color(s),
  border type / width / color, icon type / value.
- **Live rendered examples:**
  - A mock post-it card (as it would appear on the Kanban board).
  - A mock event badge (as it would appear on the Calendar).
  Both use the layout's actual styles so the user sees the real result.

Not included in v1:
- List of entities using this layout (topics / events / tasks) — FUTURE.

## G3 · Visual Layout Editor — REQUIREMENT

A UI form to create and edit layouts directly, without touching the YAML file.

### Editable fields
- **Background:** type selector (solid / gradient / none) + color picker(s).
- **Border:** type selector (solid / dashed / none) + width input + color picker.
- **Icon:** type selector (emoji / text / none) + value input.

### Persistence
- Changes are **written back to the source YAML file** on save.
- The editor uses the `DatabaseSerializer` (backending) to re-serialize only
  the layouts section of the file, preserving all other content.
- After saving, the database is automatically reloaded to reflect the change.
- A "Discard changes" button reverts to the last saved state.

### Create / delete
- "New layout" button: creates a new layout entry with a user-provided id.
- "Delete layout" button: removes the layout from the YAML after a confirmation
  prompt. Warns if any topic / event / task references this layout id.

### Live preview
- The mock post-it and event badge update in real time as the user edits fields,
  before saving.

---

## Layout

```
┌──────────────────────────────┬──────────────────────────────┐
│  Layout Gallery (card grid)  │  Detail + Editor             │
│                              │  ────────────────────────    │
│  [card] [card] [card]        │  id: work                    │
│  [card] [card] [card]        │  Background: solid #3a86ff   │
│  [card] [card]               │  Border: solid 2px #1a56cc   │
│                              │  Icon: emoji 💼              │
│  [+ New layout]              │                              │
│                              │  [mock post-it] [mock badge] │
│                              │                              │
│                              │  [Save]  [Discard]  [Delete] │
└──────────────────────────────┴──────────────────────────────┘
```
