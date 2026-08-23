# 09 — Cost, context and security

> Source: [Prompt caching](https://docs.claude.com/en/docs/build-with-claude/prompt-caching) ·
> [Permissions](https://code.claude.com/docs/en/permissions)

## Prompt caching is a prefix match

Render order is **tools → system → messages**. Any byte change anywhere in the
prefix invalidates everything after it.

So: stable content first (frozen system prompt, deterministically ordered tool
list), volatile content after the last `cache_control` breakpoint.

```python
client.messages.create(
    model="claude-opus-5", max_tokens=16000,
    system=[{"type": "text", "text": BIG_STABLE_CONTEXT,
             "cache_control": {"type": "ephemeral"}}],
    messages=[{"role": "user", "content": todays_question}],
)
```

**Verify, do not assume.** If `usage.cache_read_input_tokens` is zero across
repeated identical-prefix requests, something is silently invalidating it:

| Invalidator | Fix |
|---|---|
| `datetime.now()` / a UUID in the system prompt | move it after the breakpoint |
| `json.dumps(d)` on an unsorted dict | `sort_keys=True` |
| A tool list built from a set | sort it |
| A prefix under ~1024 tokens | too short to cache at all |

Max 4 breakpoints per request. Cache writes cost ~1.25×, reads ~0.1×.
[`sandbox/02_prompt_caching.py`](../sandbox/02_prompt_caching.py) reproduces
both the hit and the break.

## Cost levers, in order of payoff

1. **Caching** a large repeated prefix — up to ~90% off that portion.
2. **The Batches API** — ~50% off, if latency does not matter. Results come back
   in **any order**; key them by `custom_id`, never by position.
3. **Lower `effort`** before you reach for a smaller model. Disabling thinking
   on current models is usually the wrong trade.
4. **Model choice** — a smaller model for mechanical, high-volume work.
5. **`count_tokens`** before sending, to know what a request will cost.
   Never `tiktoken` — that is a different tokenizer and its numbers are wrong.

Do not lowball `max_tokens` to save money: hitting the cap truncates mid-thought
and you pay for the retry too.

## Context management

Three distinct mechanisms, often confused:

| Mechanism | What it does |
|---|---|
| **Context editing** | *Clears* old tool results or thinking blocks |
| **Compaction** | *Summarizes* earlier context server-side |
| **Memory** | Persists facts across sessions |

With compaction, append `response.content` — not just the extracted text — back
into your messages. The compaction blocks are how the API replaces the
compacted history on the next request, and extracting only the text silently
loses that state.

## Security

**The context window is not a vault.** Anything in it can be echoed back,
quoted, or extracted by prompt injection. Keep credentials out of it: hold them
host-side in the tool implementation, or use a vault credential substituted at
egress so it never enters the sandbox.

**Everything the model reads is untrusted.** Issue bodies, PR review comments,
CI logs, web pages, MCP tool output — all of it is attacker-influenceable. Treat
it as **data, never as instructions**. The mitigations are structural:

- Deny rules on secret paths: `Read(./.env)`, `Read(./secrets/**)`.
- Tool allowlists on subagents — `tools: Read, Grep, Glob` cannot write.
- Approval gates on consequential actions.
- Block network Bash tools (`curl`, `wget`) and allow specific fetches with
  `WebFetch(domain:github.com)` instead — a Bash rule that tries to constrain a
  URL argument is trivially bypassed by a variation in the command.

**Review what a repository ships.** `.claude/settings.json`, `.mcp.json`, and
skills with `allowed-tools` all execute or grant on your machine. Skill
`allowed-tools` is not gated by workspace trust, and `.mcp.json` servers load
without a prompt in `-p`, SDK and cloud sessions — which is precisely where
nobody is watching.
