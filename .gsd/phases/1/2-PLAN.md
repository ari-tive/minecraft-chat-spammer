---
phase: 1
plan: 2
wave: 1
---

# Plan 1.2: Logging System & GUI Updates

## Objective
Implement a real-time logging system within the GUI to provide feedback to the user on application state and sent messages.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md
- .gsd/phases/1/1-PLAN.md

## Tasks

<task type="auto">
  <name>Add ScrolledText Logging Area</name>
  <files>main.py</files>
  <action>
    Add a ScrolledText widget (from `tkinter.scrolledtext`) to the bottom section of the GUI.
    - Set it to `state='disabled'` by default to prevent user typing.
    - Apply a "terminal-like" style (e.g., black background, green/white text).
    - Add a "Messages Sent: 0" label next to it.
  </action>
  <verify>Run main.py and verify a scrollable text area is visible at the bottom.</verify>
  <done>
    - ScrolledText widget is integrated into the layout.
    - Sent counter label is visible.
  </done>
</task>

<task type="auto">
  <name>Implement GUI Logging Handler</name>
  <files>main.py</files>
  <action>
    Create a custom `logging.Handler` class that redirects logs to the ScrolledText widget.
    - The handler must use `root.after()` to ensure UI updates happen on the main thread.
    - Format log messages with timestamps: `[HH:MM:SS] level: message`.
    - Auto-scroll to the bottom whenever a new log entry is added.
    - Initialize the standard `logging` library to use this handler.
  </action>
  <verify>Add a temporary test button that triggers `logging.info("Test Log")` and check the GUI.</verify>
  <done>
    - Logs appear in the GUI with timestamps.
    - UI remains responsive when logs are added.
  </done>
</task>

## Success Criteria
- [ ] UI contains a scrollable log area.
- [ ] Python logging messages are successfully redirected and displayed in the GUI.
- [ ] Messages Sent counter is ready for incrementing.
