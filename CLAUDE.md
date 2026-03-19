# Project instructions for Claude Code

This repository contains a test assignment: a Telegram bot with AI avatars using Aiogram 3.x.

## Primary goal
Build a clean, review-friendly, production-like MVP that matches the test requirements exactly.

## Tech stack
- Python 3.11
- Aiogram 3.x
- SQLAlchemy 2.x
- SQLite
- Async code
- Environment variables via `.env`
- LLM adapter via OpenAI-compatible API

## Engineering rules
- Do not put business logic into Telegram handlers.
- Keep handlers thin.
- Put LLM logic in `services/llm.py`.
- Put short-term and long-term memory logic in dedicated services.
- Put DB access behind repository/service functions.
- Use type hints everywhere practical.
- Avoid huge files. Prefer small focused modules.
- Prefer explicit names over clever abstractions.
- Do not add unnecessary frameworks or overengineering.

## Required functionality
- `/start` with avatar choice via inline keyboard
- 3 avatars with distinct system prompts
- store current avatar for the user
- chat with selected avatar
- short-term memory using recent messages
- long-term memory using extracted facts
- `/history`
- `/facts`
- `/reset`
- `/change_avatar`
- robust error handling for LLM failures
- `.env.example`
- strong `README.md`

## Memory requirements
### Short-term memory
- Use recent dialogue messages for current context.
- Prefer storing messages in DB so history survives restart.
- Use the last 10 relevant messages in prompt building.

### Long-term memory
- Extract durable facts every 4 user messages.
- Facts must be scoped to both user and avatar.
- Store facts in `memory_facts`.
- Deduplicate facts.
- Inject stored facts into the prompt on each new LLM call.

## Streaming UX rules
- Never edit Telegram message on every token.
- Use buffered streaming updates.
- Send initial placeholder like `Думаю...`.
- Update message every ~0.5–1.0 sec or when enough text accumulated.
- Final message should be clean and complete.

## Reviewer mindset
This code will be judged as a test assignment.
Optimize for:
- clarity
- correctness
- architectural cleanliness
- easy demo
- good README
- visible long-term memory behavior after `/reset`

## Delivery expectations
Before finalizing, always:
1. review architecture
2. review imports and runnability
3. review aiogram handlers/FSM
4. review DB models and relationships
5. review streaming logic
6. review fact extraction robustness
7. improve README and demo scenario

## Demo priority
The project must clearly demonstrate:
1. user tells the bot a fact
2. bot continues conversation
3. user runs `/reset`
4. bot still remembers the fact via long-term memory
