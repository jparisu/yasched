Comments on current v4 version

[v] - completed
[x] - cancelled
[] - pending
[?] - not sure
[-] - in progress

## 0. General

[x] 0.1 I like the way that every panel has now made of "blocks" that are independent and collapsible.
However, would it be too complex to make them resizable, and even movable? So I have window setup as in vscode.

[?] 0.2 I would like those blocks also to have a slight transparency, so the background in Office and Education is a bit more visible. But just a tiny bit.

[v] 0.3 There must be a button in the right panel of an element to move the view to the "Element Panel" of such element in order to configure it.

[v] 0.4 For auto events or elements, create sub-categories so the info of them is more clear. For instance, for deadlines create category so every deadline in the top appeas as "DEADLINE" and not as "EVENT-AUTO".

[v] 0.5 Esc must close the current right panel.

[v] 0.6 As the navigation in the panels does not change the page itself, we require to make a manual "go back" button to go back to the previous panel. Make it as a pile, and add also forward button to go forward in the navigation. Add them in the top bar.

[v] 0.7 In the top bar, the buttons (refresh, theme, and now back and forward) require a tooltip to explain what they do. Add them.

[v] 0.8 Configurations such as flexible/fit in agenda, the rows and cols in task board, view type in task board, etc. must be saved in the user settings, so when the user opens the app again, it is as he left it.


### 0.1 Element panels

[v] 0.0.1 The element panels must have something to distinguish them: the name must be "Topic Configuration".

[v] 0.0.2 If panel windows closed or changed to another panel, the info must saved automatically by default. Add a settings feature so it allows to auto-save on change, or to require a manual save (with the current button) to save the changes.

[v] 0.0.3 Options to collapse all and extend all the topic tree.

---

## 1. Main

[v] 1.1. Upcoming events and Upcoming deadlines does not have a date related, so how am I supposed to know when they are happening?
I think this is because of the line format that hide that information.
We shall be more flexible in there, allowing the line format to have some fields depending on the window. In this case, obviously, we require the date and time of them.

[v] 1.2. There is a bug (still) with dark mode. In dark mode, the text that appears over a light background (for instance the "Auto" lines in main) is not readable.
Ideas on how to fix this:

## 2. Stats

[v] 2.1 Topics must be clickable from the tree, not as line or point, just links to open the right-side panel

## 3. Focus

[v] 3.1 There should be a "Unfocus all" button.

[v] 3.2 Currently, in the right panel of each element there is not an easy way to set it as focus or not. Add a checkbox in every element that set it.

[v] 3.3. I think in the requirements I set that focus is inherited by sub-tasks or sub-events. This is wrong. I do not want it to be inherited, it must be explicitly set in every element. So, remove the inheritance of focus.

[v] 3.4 Add another version of focus that is semi-focus. This is for back-log focused tasks, or future focus tasks, so they are in the radar but nor formally on focus. For this, in on-focus page add them just below the current one blocks, as 2 other blocks with semi-focused elements.

## 4. Attributes

## 5. Settings

[?] 5.1 General - Density does not work, check this.

[v] 5.2 Add the "autosave" option here

---

## 6. Graph

[v] 6.1 Tree vision must allow collapse/expand of nodes.

## 7. Topics

---

## 8. Calendar

## 9. Agenda

[v] 9.1 The agenda size must be configurable in 2 options for vertical layout, the horizontal always full content width:
[v] 9.1.a Fixed, always the same, that is the main screen
[v] 9.1.b Flexible, that is the agenda size is the same as the main screen, but it can be resized for the elements on it

[v] 9.2 I prefer Saturday and Sunday to appear one next to the other, and not one below the other. This breaks the grid, but it is how agends are, so I prefer it this way. So, weekend days has less space, but that is ok.

[v] 9.3 The flexible or fit is okey, but there is still a problem. In fit mode, the days must be vertically distributed. Right now, Wed is much wider than the others. Assure that when using this mode, the 3 rows are correctly and equally distributed.

## 10. Events

---

## 11. Timeboard

## 12. Schedule

---

## 13. Taskboard

[v] 13.1 You totally misunderstood this. What about multiple division settings in both horizontal and vertical?
I want to be able to set the divisions by "topic, status, priority, on-focus", etc. in both vertical and horizontal.

[v] 13.2 Allow to select between card, list and point visualization for all the tasks. In Point visualization, do not stacked them vertically, but also horizontally, to reduce space.

[v] 13.3 The left space for the name of the column is too high. Make the column name text vertical.

[v] 13.4 Increase row/col text size and make it bold.

[v] 13.5 I though we said that in here only tasks, no deadlines. So scheduled tasks must appear only once, not repeated, and if the info is shown (card view) show the first deadline to come.

## 14. Task

---

## 15. Missing panels

15.1 I miss the timeline. This is something similar to the calendar but everything in a single line, similar to what there is now in "Timeboard".
Allow that, or to set it in vertical with line format for each element, selectable by option.

---

## 16. Timeline

This is okey, however 2 things:

[v] 16.1 In hover, show the info (as square format) of the element we pass by

[v] 16.2 Allow to resize the horizontal timeline, as to make it bigger or smaller so not all the elements must fit. Make a scroll bar from 1h to ALL, and in the middle just a log scale to change the time that enters in the timeline.
