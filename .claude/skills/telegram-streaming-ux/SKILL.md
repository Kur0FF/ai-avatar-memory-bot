---
name: telegram-streaming-ux
description: Implement and review streaming LLM responses in Telegram with buffered edits, stable UX, and safe edit cadence.
---

# Telegram Streaming UX

Use this skill when:
- implementing token streaming
- editing messages progressively in Telegram
- improving perceived responsiveness of the bot

## Rules
- Never edit on every token.
- Start with a placeholder message like `Думаю...`.
- Buffer chunks.
- Update on time interval and/or size threshold.
- Keep edits resilient to Telegram API errors.
- Ensure the final message is the complete answer.
- If streaming fails mid-way, recover gracefully.

## UX guidance
- First visible feedback should be quick.
- Avoid flickering and noisy edits.
- Make the user feel the answer is being generated live.
- Keep the final message readable and polished.

## Review questions
- Is the update cadence reasonable?
- Could this hit Telegram edit limits?
- Is the experience better than sending one delayed message?
- Is the implementation simple and reliable?

## Expected output
When invoked, produce:
1. streaming design or review
2. recommended buffering strategy
3. edge case handling
4. concrete fixes in code if needed
