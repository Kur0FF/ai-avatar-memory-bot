---
name: python-quality-gate
description: Perform a strict final quality pass on a Python Telegram bot project: imports, typing, structure, environment config, resilience, and readiness for submission.
---

# Python Quality Gate

Use this skill when:
- project implementation is mostly done
- you need a strict pre-submission review
- you want to catch issues that reduce reviewer confidence

## Audit areas
- imports and module boundaries
- runnability
- settings and `.env.example`
- SQLAlchemy model correctness
- aiogram wiring
- FSM transitions
- exception handling
- type hints
- dead code / TODOs / placeholders
- repository cleanliness

## Submission mindset
Judge the project as a reviewer would.
Look for:
- shortcuts
- fragile spots
- unclear names
- hidden bugs
- weak README
- missing demo flow

## Expected output
When invoked, produce:
1. critical issues
2. medium issues
3. low-priority improvements
4. direct code fixes where possible
