# TELEGRAM.md - Telegram Interface Rules

## Message Limits
- Max message length: **4096 chars**. If response is longer — split into parts.
- Always send part N/total at the start of each chunk: "Частина 1/3:"
- Never leave a message mid-sentence when splitting.
- Use `...` at the end of incomplete parts.

## Token Budget Awareness 
- You are running in a **constrained context**. Load only the files needed for the current task.
- **DO NOT** load MEMORY.md + AGENTS.md + TOOLS.md all at once unless explicitly needed.
- **Prefer lazy loading:** load a file only when the user asks about something it covers.

## Loading Order (Critical!)
**On startup, load ONLY:**
1. `IDENTITY.md` — who you are
2. `SOUL.md` — your personality  
3. `TELEGRAM.md` — these rules
4. `TOOLS_SUMMARY.md` — basic tool hints
5. `MEMORY_SUMMARY.md` — recent context summary

**Load on-demand only:**
- `TOOLS.md` — when user asks about aliases/commands
- `MEMORY.md` — when user asks about past decisions
- `AGENTS.md` — when user asks about workflow
- `CRITICAL_PATTERNS.md` — when debugging repeated issues

## Concurrency
- **Process one message at a time.** If a second message arrives during processing — queue it.
- **Never start a new tool call** if a previous one hasn't returned yet.
- Use locks or flags to prevent parallel execution.

## Response Style for Telegram
- **Use short paragraphs,** not walls of text.
- **Prefer bullet points** over tables (tables render poorly in TG).
- **Code blocks work fine:** use them for commands, logs, configs.
- **Emojis are helpful** for visual structure: ✅ ❌ 🔧 📊 🎯

## Error Handling
- If `telegram.error.Conflict` occurs:
  1. Stop all processes immediately
  2. Run webhook reset: `bot.delete_webhook(drop_pending_updates=True)`
  3. Wait 5 seconds
  4. Restart with clean state

## Development Mode
When user says "розробляю в тг" or similar:
- **Prioritize speed over completeness**
- **Use summary files instead of full context**
- **Immediate feedback > perfect answers**
- **Short confirmations:** "✅ Done" instead of explanations

## Debug Commands
- `/debug_status` — show loaded files, memory usage
- `/debug_reset` — clear context, reload minimal files
- `/debug_files` — list all available files in workspace

## Critical: NO Conflicts
- **Never run multiple getUpdates** on same token
- **Always check if systemd is active** before manual start
- **Use `drop_pending_updates=True`** when restarting
- **Kill zombie processes** before new start: `ps aux | grep bot.py`