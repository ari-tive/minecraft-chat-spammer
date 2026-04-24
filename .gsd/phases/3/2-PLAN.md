---
phase: 3
plan: 2
wave: 1
---

# Plan 3.2: Hotkey Wiring & UI State

## Objective
Connect the global hotkeys to the spam engine and update the UI to reflect the active state of the spammer.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md
- .gsd/phases/3/1-PLAN.md
- main.py

## Tasks

<task type="auto">
  <name>Wire F6/F7 Hotkeys to Engine</name>
  <files>main.py</files>
  <action>
    Update the hotkey handlers:
    - `on_activate_start`: 
        - Check if `self.is_running` is False.
        - Set `self.is_running = True`, clear `self.stop_event`.
        - Start a new daemon thread for `self._spam_worker`.
    - `on_activate_stop`:
        - Set `self.stop_event.set()`.
        - Set `self.is_running = False`.
        - Log "[ENGINE] Stop signal sent."
  </action>
  <verify>Run the app and use F6/F7 to start/stop the countdown/spamming. Verify logs reflect the actions.</verify>
  <done>
    - Hotkeys successfully control the background thread.
    - Multiple start commands don't launch overlapping threads.
  </done>
</task>

<task type="auto">
  <name>UI Status and Safety Improvements</name>
  <files>main.py</files>
  <action>
    Refine the user feedback:
    - Update the `counter_lbl` and `log_text` from the worker thread via the queue.
    - Change the text color of the hotkey labels in the GUI when the spammer is "Active" vs "Idle".
    - Add a small sleep between 'T' and 'Paste' and 'Enter' to ensure Minecraft has time to react (e.g. 0.1s).
  </action>
  <verify>Ensure 'T' consistently opens the chat before the message is pasted.</verify>
  <done>
    - UI gives clear visual feedback when spamming is active.
    - Counter increments correctly.
  </done>
</task>

## Success Criteria
- [ ] Global hotkeys reliably start and stop the automation engine.
- [ ] UI provides real-time feedback on sent count and engine status.
