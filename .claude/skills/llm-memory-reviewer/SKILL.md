---
name: llm-memory-reviewer
description: Design and review short-term and long-term memory for LLM chatbots, including fact extraction, JSON parsing, deduplication, and prompt injection.
---

# LLM Memory Reviewer

Use this skill when:
- implementing memory behavior
- reviewing prompt construction
- validating fact extraction from dialogue
- checking robustness of long-term memory storage

## Short-term memory rules
- Use recent dialogue only.
- Prefer the last 10 messages.
- Keep role ordering correct.
- Avoid duplicating the current user message.
- Make sure the selected avatar and user scope are respected.

## Long-term memory rules
- Extract facts every 4 user messages or similar cadence.
- Ask extractor to return JSON array of strings only.
- Parse via `json.loads` first.
- If parsing fails, try extracting a JSON fragment from text.
- If still invalid, return empty list safely.
- Normalize and deduplicate facts.
- Scope facts by both `user_id` and `avatar_id`.
- Inject facts at the top of the prompt in a concise block.

## Review questions
- Will this survive bot restart?
- Are facts visibly used in later replies?
- Can `/reset` clear only short-term history while keeping facts?
- Can reviewer clearly see the difference between short-term and long-term memory?

## Expected output
When invoked, produce:
1. issues in current memory design
2. exact fixes
3. stronger prompt format if needed
4. edge cases and fallback behavior
