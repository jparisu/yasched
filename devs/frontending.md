# Frontend Development Plan

## Context

**Backend**: Pure Python library (`yasched`) — YAML-driven data model with `DatabaseInterface` providing query methods. No HTTP layer exists yet.

**Template**: React 18 + Vite + TypeScript + Tailwind CSS 4 + shadcn/ui (46 components) + Recharts + react-dnd. Located at `tmp/frontend-template/`.

**Streamlit POC** (existing, in `apps/streamlit/`): Kanban tasks board + monthly calendar + overview tab. Good reference for what worked.

---

## Compatibility Analysis

| Concern | Status | Notes |
|---|---|---|
| React template tech stack | Ready | React + Vite + TS + Tailwind — modern, solid |
| shadcn/ui components | Ready | Calendar, Kanban, Tables, Charts all present |
| Backend HTTP API | **MISSING** | No FastAPI/Flask REST layer exists yet — must build first |
| Data models → JSON | Ready | All models are Python dataclasses — easy to serialize |
| Authentication | N/A | Single-user local tool, skip auth |
| YAML DB → read-only API | Design choice | Decide if frontend can only read or also write |

**Critical prerequisite**: A FastAPI app exposing `DatabaseInterface` as REST endpoints must be built before any real frontend data integration.

---

## Phase 1 — MVP: Running Web App (Empty Shell)

Goal: a working app that launches in the browser with sidebar navigation but no real data yet.

### 1.1 — FastAPI Backend

- [ ] Create `apps/api/` package
- [ ] `main.py` — FastAPI app, CORS config, database loading on startup
- [ ] `routers/tasks.py` — endpoints from `DatabaseInterface` task methods
- [ ] `routers/events.py` — endpoints from `DatabaseInterface` event methods
- [ ] `routers/topics.py` — endpoints from `DatabaseInterface` topic methods
- [ ] `routers/schedule.py` — daily/weekly/range schedule endpoints
- [ ] `schemas.py` — Pydantic models (JSON serialization of `Task`, `Event`, `Topic`, `Schedule`)
- [ ] Add `uvicorn` + `fastapi` to dev dependencies
- [ ] `GET /tasks`, `GET /tasks/{id}`, `GET /tasks/status/{status}`
- [ ] `GET /events`, `GET /events/{id}`, `GET /schedule/daily`, `GET /schedule/weekly`, `GET /schedule/range`
- [ ] `GET /topics`, `GET /topics/{id}`, `GET /topics/tree`
- [ ] `GET /health` — validate DB and return summary
- [ ] Test all endpoints manually with `curl` or Swagger UI

### 1.2 — Frontend Project Setup

- [ ] Create `apps/web/` directory
- [ ] Copy template structure from `tmp/frontend-template/` as starting point
  - Keep: `vite.config.ts`, `tailwind.css`, `globals.css`, `default_theme.css`, `fonts.css`, `ui/` components, `Sidebar.tsx`, `Layout.tsx`
  - Remove/gut: energy-domain components (ConsumptionChart, DemandChart, EnergyParameters, etc.)
  - Keep skeletons of: Dashboard, Calendar, TaskBoard, Topics, Agenda (empty state)
- [ ] Set `VITE_API_URL=http://localhost:8000` in `.env`
- [ ] Create `src/api/client.ts` — thin fetch wrapper pointing at FastAPI
- [ ] Replace Figma asset references with local assets or remove them
- [ ] Rename sidebar nav items to yasched pages (TBD in Phase 2)
- [ ] Confirm `pnpm dev` runs without errors and sidebar renders

### 1.3 — Smoke Test

- [ ] `uvicorn` starts, `/health` returns valid response
- [ ] `pnpm dev` starts, browser shows sidebar with empty pages
- [ ] No TypeScript errors, no console errors

---

## Phase 2 — Layout & Tab Design (Interactive with User)

**This phase is a conversation, not a coding sprint.**

Before coding any real page, answer these questions with the user:

### Questions to resolve

1. **Which pages do we need?**
   Candidates from template + backend:
   - `Dashboard` — DB health, entity counts, task status summary
   - `Calendar` — Daily / Weekly / Monthly view of scheduled tasks + events
   - `Tasks` — Kanban board by status (TODO / IN_PROGRESS / DONE / CANCELLED / BLOCKED)
   - `Topics` — Hierarchy/tree or network graph of topics
   - `Agenda` — Weekly planner (upcoming tasks + events side by side)
   - _(possible)_ `Search` — Search/filter tasks by tag, deadline, topic

2. **Read-only or editable?**
   Does the UI only display data from YAML, or can users create/edit tasks and events through the web interface? (This drastically changes backend scope.)

3. **Calendar default view?**
   Template has daily / weekly / monthly / yearly. Which should be the landing view?

4. **Task board layout?**
   Template uses Eisenhower quadrant (urgent/important matrix). Backend has `status`-based columns (TODO / IN_PROGRESS / …). Which layout?

5. **Topic visualization?**
   Template has a network graph (force-directed). Backend supports topic trees (DAG with parent_ids). Graph or tree?

6. **Theme / color?**
   Template defaults to green sidebar (#2c5f4e). Keep or change?

### Deliverable

A confirmed page list, tab order, and layout decisions — written as a comment on this file or a new `devs/frontending-pages.md`.

---

## Phase 3 — Tab-by-Tab Implementation

Each tab is a sub-phase. User validates before moving to the next.

### Template for each tab

- [ ] Define data needs (which API endpoints)
- [ ] Create React component in `apps/web/src/pages/<TabName>.tsx`
- [ ] Wire API calls with React Query or plain `useEffect`
- [ ] Build layout using shadcn/ui + Tailwind (reuse template components where possible)
- [ ] Handle loading state and error state
- [ ] Manual smoke test
- [ ] User validation ✓

### Likely tab order (to be confirmed in Phase 2)

1. **Dashboard** — simplest; just counts and status summary; validates API connectivity
2. **Tasks (Kanban)** — core feature; Streamlit POC reference available
3. **Calendar** — schedule view; most complex date logic
4. **Topics** — tree or graph visualization
5. **Agenda** — weekly view combining tasks + events

---

## Open Decisions

| Decision | Default assumption | Needs confirmation |
|---|---|---|
| API framework | FastAPI | No — FastAPI is the obvious choice |
| Read-only vs editable | Read-only first | **Yes** |
| Pages to build | Dashboard, Tasks, Calendar, Topics, Agenda | **Yes — Phase 2** |
| Monorepo tooling | `pnpm` (already in template) | No |
| Deployment | Local dev only | **Yes** |
| Auth | None (single-user local tool) | No |
