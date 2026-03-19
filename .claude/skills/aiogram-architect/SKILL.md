---
name: aiogram-architect
description: Design clean Aiogram 3.x architecture, FSM flow, handlers, services, database layout, and project structure for review-friendly Telegram bots.
---

# Aiogram Architect

Use this skill when:
- designing the initial project structure
- planning FSM states and transitions
- deciding where handlers, services, repositories, and keyboards should live
- reviewing whether the codebase is clean enough for a test assignment

## Objectives
- Keep handlers thin.
- Separate bot transport layer from business logic.
- Use idiomatic Aiogram 3.x routers and FSM.
- Build a structure that looks senior and easy to maintain.

## Checklist
- Define project folders before coding.
- Ensure routers are split by responsibility.
- Define FSM states clearly.
- Avoid putting database access directly into handlers unless trivial.
- Avoid giant `main.py` or single-file bots.
- Keep keyboards separate.
- Keep avatar logic separate from chat logic.

## Expected output
When invoked, produce:
1. proposed folder tree
2. FSM states and transitions
3. major modules and responsibilities
4. implementation order
5. risks and mitigation
