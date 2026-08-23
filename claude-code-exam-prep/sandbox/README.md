# Sandbox

Runnable experiments against the Claude API. Unlike the rest of the repo these
need credentials and network access.

```bash
pip install anthropic pydantic
export ANTHROPIC_API_KEY=sk-ant-...      # or run: ant auth login
```

| Script | What it shows |
|---|---|
| [`01_first_call.py`](01_first_call.py) | The shape of a Messages call: content blocks, adaptive thinking, `output_config.effort`, refusal handling, a real error chain |
| [`02_prompt_caching.py`](02_prompt_caching.py) | Caching hit, then deliberately broken — run it and watch `cache_read_input_tokens` drop to zero |
| [`03_tool_runner_agent.py`](03_tool_runner_agent.py) | An agent over the question bank using `client.beta.messages.tool_runner` |
| [`04_grade_free_response.py`](04_grade_free_response.py) | LLM-as-judge with structured outputs — grades a free-text answer against the bank |

## Start with 02

It is the most useful five minutes in this directory. It sends the same large
system prompt three times — cold, warm, and with a timestamp prepended — and
prints the cache counters for each. Seeing `read=0` on the third run because of
one `datetime.now()` is the lesson that sticks.

## These cost money

`02` and `04` each make multiple calls with a large context. They are cheap, not
free. `02` in particular is designed to *waste* a cache write, which is the
point.

## A warning about the code

The scripts are written against the current SDK surface: adaptive thinking,
`effort` inside `output_config`, `messages.parse()` for structured outputs.
Several of these changed during 2025–2026 — `budget_tokens` is now rejected,
assistant prefill returns a 400. If something here fails with a 400, check the
[API docs](https://docs.claude.com/en/api/messages) before assuming the script
is wrong; it may simply be older than the API.
