---
phase: 1
plan: 1
wave: 1
---

# Plan 1.1: Core UI Layout & Controls

## Objective
Establish the foundational GUI structure using Tkinter, providing the user with input fields for messages and configuration settings.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md
- .gsd/RESEARCH.md

## Tasks

<task type="auto">
  <name>Scaffold Main Window and Layout</name>
  <files>main.py</files>
  <action>
    Create the main application class `MinecraftSpammerApp`.
    - Set up the Tkinter root window with a professional title and fixed/responsive geometry.
    - Implement a grid-based layout split into three sections: Message Slots (Top), Configuration (Middle), and Logo/Status (Bottom).
    - Use a clean, modern aesthetic (e.g., consistent padding, themed colors).
  </action>
  <verify>python main.py (Ensure window opens without error and shows basic structure)</verify>
  <done>
    - main.py exists.
    - Window displays with correct title.
  </done>
</task>

<task type="auto">
  <name>Implement Message Slots and Config Form</name>
  <files>main.py</files>
  <action>
    Populate the UI with input widgets:
    - Create 4 labeled Entry widgets for message slots.
    - Create a "Configuration" frame with:
        - Interval (Spinbox or Entry, default 2.0s).
        - Variance toggle (Checkbutton, default ON).
        - Hotkey labels (Placeholders for now: "Start: F6", "Stop: F7").
    - Ensure all widgets are stored as instance variables for easy access.
  </action>
  <verify>Run the script and visually confirm 4 message boxes and config controls exist.</verify>
  <done>
    - 4 Entry boxes are visible and usable.
    - Interval and Variance controls are functional.
  </done>
</task>

## Success Criteria
- [ ] Application window launches with a 4-slot message input area.
- [ ] Base interval and variance settings are configurable via the GUI.
