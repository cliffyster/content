# 08 — Claude API mechanics

> Source: [Messages API](https://docs.claude.com/en/api/messages) ·
> [Tool use](https://docs.claude.com/en/docs/build-with-claude/tool-use)

## One endpoint

Everything goes through `POST /v1/messages`. Tool use, extended thinking,
caching and structured outputs are **features of that endpoint**, not separate
APIs. Batches, Files, Token Counting and Models are supporting endpoints that
feed into it.

## Reading a response

`response.content` is a **list of blocks** — `thinking`, `text`, `tool_use`, …

```python
for block in response.content:
    if block.type == "text":
        print(block.text)
```

`response.content[0].text` is the classic first bug: with thinking on, block 0
is usually a thinking block.

## Stop reasons

| Value | Meaning |
|---|---|
| `end_turn` | finished naturally |
| `max_tokens` | hit the cap — output is truncated mid-thought |
| `stop_sequence` | hit a custom stop sequence |
| `tool_use` | execute the tool and continue the loop |
| `pause_turn` | a server-side tool paused; resend to resume |
| `refusal` | safety decline — HTTP **200**, check `stop_details` |

A refusal is not an exception. Check `stop_reason` before reading content.
`stop_details` is populated **only** for refusals — guard before reading it.

## The agentic loop

```python
while True:
    response = client.messages.create(model=MODEL, max_tokens=16000,
                                      tools=tools, messages=messages)
    if response.stop_reason == "end_turn":
        break
    messages.append({"role": "assistant", "content": response.content})
    results = [
        {"type": "tool_result", "tool_use_id": b.id, "content": run(b.name, b.input)}
        for b in response.content if b.type == "tool_use"
    ]
    messages.append({"role": "user", "content": results})   # ALL results, ONE message
```

The API is **stateless** — you resend the full history every time. That is why
caching and context management matter so much.

Parse tool inputs with `json.loads()`; never string-match the serialized input,
because JSON escaping of the same value can differ between models.

## Thinking and effort

Use **adaptive thinking** — `thinking={"type": "adaptive"}`. Claude decides how
much to think. The old fixed `budget_tokens` knob is removed on current models
and returns a **400** if sent.

Control spend with **`output_config={"effort": ...}`** — `low`, `medium`,
`high` (default), `xhigh`, `max`. Note it lives *inside* `output_config`, not
at the top level.

`display: "summarized"` returns a readable summary of the reasoning; the
default on current models is `"omitted"` (empty thinking text). Thinking is
billed the same either way.

## Structured outputs

```python
class Grade(BaseModel):
    score: int
    correct: bool

response = client.messages.parse(model=MODEL, max_tokens=16000,
                                 messages=[...], output_format=Grade)
grade = response.parsed_output          # validated instance
```

The old assistant-prefill trick — seeding the response with `{` — returns a
**400** on current models. Use structured outputs instead.

For tools, `strict: true` goes on the **tool definition** (alongside `name`,
`description`, `input_schema`), not on `tool_choice`, and the schema needs
`additionalProperties: false` plus `required`.

## Errors

Catch a chain, most specific first — one broad `except APIStatusError` loses the
retryable/non-retryable distinction:

```python
except anthropic.NotFoundError:      ...   # bad model id — do not retry
except anthropic.RateLimitError:     ...   # read the retry-after header
except anthropic.APIStatusError as e: ...  # branch on e.status_code
except anthropic.APIConnectionError: ...   # network
```

The SDK already auto-retries 408/409/429/5xx and connection errors with
exponential backoff (default 2 retries). Only hand-roll retries for behavior
beyond that.
