---
phase: 4
plan: 2
wave: 1
---

# Plan 4.2: PyInstaller Distribution

## Objective
Bundle the Python application into a standalone Windows `.exe` file for easy distribution.

## Context
- .gsd/SPEC.md
- .gsd/RESEARCH.md
- main.py

## Tasks

<task type="auto">
  <name>Implement Resource Path Helper</name>
  <files>main.py</files>
  <action>
    Add the `resource_path` function to `main.py` to handle bundled icons correctly.
    - Reference the tray icon via this helper.
    - Ensure the script still works in development mode (finding the icon locally).
  </action>
  <verify>Run the script locally and check if the tray icon still loads correctly.</verify>
  <done>
    - Resource paths are resolved dynamically for both dev and bundled modes.
  </done>
</task>

<task type="auto">
  <name>Build Standalone Executable</name>
  <files>build_exe.ps1</files>
  <action>
    Create a `build_exe.ps1` script to automate the PyInstaller build:
    - Include flags: `--onefile`, `--windowed`, `--noconfirm`.
    - Correctly handle `--add-data "assets/icon.png;."` (creating an `assets` folder if needed).
    - Execute the build and verify the `dist/` folder contains the `.exe`.
  </action>
  <verify>Run the build script and check the output in the `dist` directory.</verify>
  <done>
    - Functional `.exe` is generated in the `dist` folder.
  </done>
</task>

## Success Criteria
- [ ] Application successfully bundles into a single `.exe`.
- [ ] The bundled `.exe` correctly displays the system tray icon on start.
