# A — Data Loading & Database Management

## Features

### A1 · File picker + directory browser — REQUIREMENT
- Modal dialog shown on first load (app starts with no database open).
- Modal can be re-opened at any time via a top-bar button (e.g. "Open database").
- Inside the modal: text input for manual path entry + inline directory browser
  showing folders and `.yaml` / `.yml` files.
- On selection, path is filled in the text input; user confirms with a Load button.

### A2 · Load / reload button — REQUIREMENT
- Primary action inside the modal and also accessible from the top bar when a
  database is already open (reload = re-parse the same file from disk).

### A3 · Validation error display — REQUIREMENT
- After loading, show a compact status indicator in the top bar:
  ✅ Loaded | ⚠️ N error(s) | ❌ Failed.
- Clicking the indicator opens an expandable panel listing every error with its
  type and message (per-item, not just a count).
- Errors do not block the app from rendering what it can.

### A4 · Database stats badge — REQUIREMENT
- Persistent badge in the top bar (or sidebar header) showing:
  layouts · topics · events · tasks counts.
- Updates immediately on load/reload.

### A5 · Recent files history — REQUIREMENT
- Persist the last N opened file paths in local storage (browser).
- Show them in the open-database modal as a clickable "Recent" list.
- Each entry: filename + full path + last-opened timestamp.

### A6 · Multi-file support — FUTURE
- Design the state layer to hold a list of databases, not just one.
- UI switch (dropdown or tabs) in the top bar to change the active database.
- Do not implement in v1; keep the data model multi-file-ready.

### A7 · Server-side default database config — REQUIREMENT
- The server persists the last successfully loaded database path in `~/.yasched/config.yaml`.
- On startup, if the config file contains a path, the open-database modal is shown
  **pre-filled** with that path; the user still clicks Load to confirm.
- If the file at the saved path no longer exists or fails to parse, the modal opens
  empty with an error message explaining why the saved path could not be used.
- This makes the app usable as a persistent personal local server: restart the server,
  open the browser, click Load — back to your schedule immediately.
- Config file format (minimal):
  ```yaml
  default_database: /home/user/schedule/main.yaml
  ```

## UX notes
- The modal is dismissible only if a database is already loaded.
- On first startup with no saved config, the modal is mandatory (cannot dismiss).
- On subsequent startups with a saved path, modal is pre-filled; user confirms with Load.
- Reload should diff the new data and show a "N entities changed" toast.
- Recent files (A5) use browser local storage — quick access within browser sessions.
- Default database (A7) uses server-side config — survives server restarts.
