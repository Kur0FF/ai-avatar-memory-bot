# Claude Code workflow pack for the AI-avatar Telegram bot test task

Use the prompts below **in order**.

---

## 1) Analyze the test task first

```text
Read the full test task below and do NOT write code yet.

I need architecture and implementation planning first.

Do:
1. brief requirement analysis
2. project architecture proposal
3. folder/file tree
4. FSM states and transitions
5. database schema proposal
6. plan for:
   - avatar selection
   - short-term memory
   - long-term memory
   - streaming responses in Telegram
   - /history
   - /facts
   - /reset
   - /change_avatar
7. risks and mitigation
8. implementation plan by stages

Constraints:
- Python 3.11
- Aiogram 3.x
- SQLAlchemy 2.x
- SQLite
- async code
- .env
- type hints

Do not create files yet.
```

---

## 2) Install project instructions and skills in this repo

```text
Create and populate the following files in this repository:
- CLAUDE.md
- .claude/skills/aiogram-architect/SKILL.md
- .claude/skills/llm-memory-reviewer/SKILL.md
- .claude/skills/telegram-streaming-ux/SKILL.md
- .claude/skills/python-quality-gate/SKILL.md
- .claude/skills/readme-demo-packager/SKILL.md

Use them to guide all further work on this project.

Rules:
- keep CLAUDE.md compact but specific
- skills should be practical, not generic
- optimize the repo for this exact test assignment
```

---

## 3) Implement the project

```text
Now implement the project strictly according to the approved architecture.

Build a complete working MVP with no TODO placeholders.

Requirements:
- Python 3.11
- Aiogram 3.x
- SQLAlchemy 2.x
- SQLite
- async code
- .env config
- modular structure
- type hints

Required features:
- /start with inline avatar selection
- 3 avatars with distinct prompts
- selected avatar saved for the user
- normal chat with selected avatar
- short-term memory: last 10 messages
- long-term memory: extract facts every 4 user messages
- inject facts into next LLM prompts
- /history
- /facts
- /reset
- /change_avatar
- LLM API error handling
- buffered streaming response UX
- .env.example
- README.md

Important implementation rules:
- do not mix business logic into handlers
- create users, avatars, messages, memory_facts tables
- facts must be scoped by both user and avatar
- deduplicate facts
- if fact extraction JSON is broken:
  - try json.loads
  - try extracting JSON fragment
  - otherwise return [] safely
- for streaming:
  - send placeholder first
  - buffer updates
  - do not edit on every token

After coding, list created files and explain their roles briefly.
```

---

## 4) Strict self-review and fixes

```text
Now act as a strict senior reviewer.

Check and fix everything that could reduce the score of this test assignment.

Audit:
- imports
- runnability
- aiogram 3.x correctness
- routers and handlers
- FSM transitions
- DB initialization
- SQLAlchemy models
- message history logic
- long-term fact extraction robustness
- fact deduplication
- prompt construction
- streaming UX and update cadence
- error handling
- .env.example
- README

If you find issues, fix them directly in code.
Do not just list problems.

Then provide:
- final run commands
- .env.example preview
- smoke test scenario
```

---

## 5) Prepare the repository for submission

```text
Now prepare this repository for employer review.

Improve:
1. README.md
2. setup instructions
3. architecture explanation
4. FSM explanation
5. short-term memory explanation
6. long-term memory explanation
7. demo scenario
8. scenario proving memory survives /reset
9. limitations and future improvements

README should feel practical and reviewer-friendly.

Also provide:
- suggested repository name
- GitHub description
- 5 commit messages
- a short employer-facing message to send with the repo link
```

---

## 6) Harsh reviewer audit

```text
Act as a strict reviewer who is tired of weak test assignments.

Do not praise the project.
Find everything that looks rushed, fragile, fake, or underdesigned.

Judge:
- architecture
- aiogram 3.x usage
- FSM
- short-term memory
- long-term memory
- streaming
- commands
- DB
- resilience
- UX
- README
- demo readiness

For each issue say:
- what is wrong
- why it hurts the score
- how to fix it
- severity

Then give:
- verdict: strong / average / weak
- score out of 10
- probability employer likes it
- must-fix items before submission
- optional 1-2 hour improvements
```

---

## 7) Fix audit findings

```text
Fix all critical and medium issues from the audit.
Do not argue with the audit.
Update code, README, and structure where needed.
Then summarize exactly what changed.
```

---

## 8) Demo script for recording video

```text
Prepare a clear 2-3 minute demo scenario for video or screenshots.

Show:
- /start
- avatar selection
- ordinary dialogue
- user tells an important fact
- continued dialogue
- /facts
- /reset
- new question after reset
- bot recalls the fact through long-term memory

Give concrete sample user messages and expected bot behavior.
```
