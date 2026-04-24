# SPEC.md — Project Specification

> **Status**: `FINALIZED`

## Vision
A specialized Python desktop application designed to evaluate Minecraft server antispam plugins by simulating realistic, customizable player chat patterns through keyboard and clipboard automation.

## Goals
1. **Configurable Spam Engine**: Support 4 message slots with sequential cycling, custom intervals (seconds), and a ±30% random variance toggle.
2. **Robust Automation**: Use `pyautogui` and `pyperclip` to simulate chat triggers (T), message insertion, and submission (Enter) after a 5-second window-switching grace period.
3. **User-Centric GUI**: Provide a Tkinter interface with real-time logging, message counters, customizable hotkeys (Start/Stop), and system tray integration.
4. **Standalone Portability**: Package the final application as a single Windows-compatible `.exe` file using PyInstaller.

## Non-Goals (Out of Scope)
- Cross-platform support (Windows is the primary target).
- Support for multiple Minecraft instances simultaneously.
- Complex bot actions (movement, combat, or block interaction).
- Direct RCON or protocol-level communication (simulation only).

## Users
Minecraft server administrators and plugin developers who need a reliable tool to stress-test and calibrate antispam sensitivity and detection thresholds.

## Constraints
- **Environment**: Must run on Windows 10/11.
- **Dependencies**: Python 3.x, `pyautogui`, `pyperclip`, `pynput` (for global hotkeys), `pystray` (for system tray), and `Tkinter`.
- **Interference**: Users must ensure the Minecraft window is focused before the 5-second countdown expires.

## Success Criteria
- [ ] Application cycles through filled message boxes sequentially.
- [ ] Variance ±30% is applied to the base interval for each message.
- [ ] Global hotkeys (Start/Stop) work regardless of which window is focused.
- [ ] Message log displays timestamps and a running count of sent messages.
- [ ] PyInstaller builds a functional, standalone `.exe`.
