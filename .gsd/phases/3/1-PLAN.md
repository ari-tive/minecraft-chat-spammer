---
phase: 3
plan: 1
wave: 1
---

# Plan 3.1: Core Spam Engine Logic

## Objective
Implement the background worker thread that executes the spamming sequence, including the countdown, message cycling, and random variance.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md
- main.py

## Tasks

<task type="auto">
  <name>Install Automation Dependencies</name>
  <files>main.py</files>
  <action>
    Install `pyautogui` and `pyperclip`.
  </action>
  <verify>pip show pyautogui pyperclip</verify>
  <done>
    - Dependencies are available in the environment.
  </done>
</task>

<task type="auto">
  <name>Implement Spam Worker Thread</name>
  <files>main.py</files>
  <action>
    Create a `_spam_worker` method in `MinecraftSpammerApp`.
    - Start with a 5-second countdown loop that logs each second.
    - Check `self.stop_event` frequently to allow cancellation during countdown.
    - Implement a loop that:
        1. Identifies the next non-empty message slot (cycling 1->2->3->4->1).
        2. Calculates the next interval based on `base_interval` and `±30% variance`.
        3. Executes the automation sequence: `pyautogui.press('t')`, then `pyperclip.copy(msg)` -> `pyautogui.hotkey('ctrl', 'v')`, then `pyautogui.press('enter')`.
        4. Updates the `log_queue` with the sent message and increments the counter.
        5. Sleeps for the calculated interval while checking for the stop event.
  </action>
  <verify>Add a temporary "Debug Start" button to trigger this thread and observe the log.</verify>
  <done>
    - Spam worker correctly cycles through non-empty messages.
    - Automation sequence (T, Paste, Enter) is implemented.
    - Variance is correctly applied to the interval.
  </done>
</task>

## Success Criteria
- [ ] Spamming starts with a 5-second countdown.
- [ ] Non-empty message slots are cycled sequentially.
- [ ] Random variance is applied to the intervals as per SPEC.
