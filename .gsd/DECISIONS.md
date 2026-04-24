# DECISIONS.md (ADR)

## ADR-001: Threading Pattern
- **Decision**: Use Tkinter + Queue + Background Daemon Threads.
- **Rationale**: Prevents GUI lockup during blocking pystray/pyautogui/pynput calls.
