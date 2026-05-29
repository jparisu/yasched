# H — Analytics

Dedicated page (Page 7). All charts respond to a shared date-range filter at the top of the page.

## H1 · Task Count by Topic — REQUIREMENT

- Horizontal bar chart: one bar per topic, sorted by count descending.
- Bars color-coded by topic's `effective_layout` or topic palette color.
- Toggle: include subtopic counts rolled up into parent, or show each topic independently.
- Clicking a bar navigates to the Topics page with that topic selected.

## H2 · Priority Distribution — REQUIREMENT

- Histogram: x-axis = priority level (numeric), y-axis = task count.
- Stacked by status (TODO / IN_PROGRESS / BLOCKED / DONE / CANCELLED) using status colors.
- Tasks with no priority shown in a separate "unset" bucket on the right.

## H3 · Deadline Density — REQUIREMENT

- Bar chart or heatmap calendar showing how many task deadlines fall per week or per month.
- Toggle between weekly bars and monthly heatmap view.
- Overdue deadlines (past dates) shown in red; future deadlines in neutral color.
- Helps identify crunch periods at a glance.

## H4 · Effort Estimate Totals — FUTURE

- Sum of min and max effort (Duration) per topic or per status group.
- Shown as a range bar chart (min–max band per group).

---

## Shared controls
- **Date range filter** at the top: restricts all charts to tasks/deadlines within the range.
- **Status filter**: toggle which statuses are included in the counts.
- Charts update reactively as filters change.
