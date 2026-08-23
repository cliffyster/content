# 19 — Prompt and context engineering

> Source: [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

## Before you engineer the prompt

The docs are blunt about the prerequisite: you need (1) a clear definition of
success criteria, (2) a way to test against them empirically, and (3) a first
draft to improve. Without those you are guessing.

And not every failing eval is a prompting problem — latency and cost are often
fixed more easily by changing the model or the effort level.

## General principles

**Be clear and direct.** Treat Claude as a brilliant new employee who lacks
context on your norms. If you want above-and-beyond behavior, *ask for it* — do
not expect it to be inferred from a vague prompt.

> **Golden rule:** show your prompt to a colleague with minimal context and ask
> them to follow it. If they'd be confused, Claude will be too.

Give sequential steps as a numbered list when order or completeness matters.

**Add context, not just commands.** Explaining *why* generalizes; a bare rule
does not.

| Less effective | More effective |
|---|---|
| `NEVER use ellipses` | `Your response will be read aloud by a text-to-speech engine, so never use ellipses since it won't know how to pronounce them.` |
| `Create an analytics dashboard` | `Create an analytics dashboard. Include as many relevant features and interactions as possible. Go beyond the basics.` |

**Use examples well.** Few-shot is one of the most reliable ways to steer format,
tone and structure. Make them:
- **Relevant** — mirror the real use case
- **Diverse** — cover edge cases, and vary enough that Claude doesn't latch onto
  an unintended pattern
- **Structured** — wrap in `<example>` tags (several in `<examples>`)

Three to five examples is the sweet spot.

**Structure with XML tags.** When a prompt mixes instructions, context, examples
and variable input, give each its own tag (`<instructions>`, `<context>`,
`<input>`). Use consistent tag names; nest where there's a natural hierarchy.

**Give Claude a role** in the system prompt. One sentence measurably changes
behavior and tone.

## Long context (20k+ tokens)

Two rules, and the first is the one people get backwards:

1. **Put longform data at the TOP** — documents and inputs above your query,
   instructions and examples. Queries at the end improved response quality by
   **up to 30%** in testing, especially with complex multi-document inputs.
2. **Wrap each document** in `<document index="n">` with `<source>` and
   `<document_content>` subtags.

Note how neatly this composes with prompt caching (note 09): stable long
documents at the front is *also* exactly where the cacheable prefix wants them.

## What changed on current models

- **Prefill is gone.** Seeding the assistant turn returns a 400 on current
  models. Use structured outputs (`output_config.format`) or system-prompt
  instructions to control format instead.
- **Thinking replaces "think step by step".** Adaptive thinking is a first-class
  parameter; you generally don't need to prompt for chain of thought. The docs
  now warn about the opposite problem — *overthinking and excessive
  thoroughness* — which you tune with `effort` rather than with prompt text.
- **Prompts written for older models are often too prescriptive** and can
  reduce output quality. This is why a model migration includes a prompt audit,
  not just a parameter swap.

## Agentic prompting

The best-practices page has a whole section on agentic systems. The themes worth
carrying into the exam:

- **Long-horizon reasoning and state tracking** — give the full task spec up
  front for long-running work rather than drip-feeding it.
- **Balancing autonomy and safety** — say explicitly what the agent may decide
  alone and what it must bring back.
- **Overeagerness** — a recognised failure mode, tuned with prompting and
  effort.
- **Avoid focusing on passing tests / hardcoding** — an agent optimising for a
  green test suite will hardcode; say so explicitly.
- **Minimizing hallucinations in agentic coding** — ground claims in files
  actually read.
- **Subagent orchestration** and **chaining complex prompts** — decomposition is
  a prompting technique, not just an architecture.
- **Reduce file creation** — agents left unchecked will scatter scratch files.

## The technique that isn't prompting

If an instruction *must* happen at a specific point — before every commit, after
every edit — no amount of prompt engineering makes it reliable. That is a hook.
Prompts shape behavior; hooks enforce it.
