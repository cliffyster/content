# 21 — Model selection and platform availability

> Source: [Models](https://platform.claude.com/docs/en/about-claude/models/overview) ·
> [Pricing](https://platform.claude.com/docs/en/about-claude/pricing)

## Choosing a model

The decision has three inputs: capability needed, cost tolerance, and context
size. In rough order:

- **Opus tier** — the default for most work. Reach for it unless you have a
  measured reason not to.
- **Sonnet tier** — high-volume production workloads where Opus-tier quality is
  more than the task needs.
- **Haiku tier** — simple, speed-critical, high-volume tasks: classification,
  routing, extraction. Note it has a **smaller context window** than the Opus and
  Sonnet tiers.

Two habits the docs push hard:

1. **Don't downgrade for cost on someone else's behalf.** Model choice is a
   product decision, not an implementation detail.
2. **Lower `effort` before you lower the model.** `output_config.effort`
   (`low`/`medium`/`high`/`xhigh`/`max`, default `high`) often buys the saving
   without the capability loss. `low` suits subagents and mechanical tasks;
   `max` is for when correctness matters more than cost.

Never construct a model ID by appending a date suffix you half-remember. Use the
exact published string, or query the **Models API** (`client.models.list()` /
`.retrieve(id)`) which returns `max_input_tokens`, `max_tokens` and a
`capabilities` object. There is no `context_window` field.

## Cost levers ranked

1. **Prompt caching** on a large repeated prefix — up to ~90% off that portion.
2. **Message Batches** — roughly 50% off, asynchronous.
3. **Lower effort.**
4. **A smaller model** for the mechanical parts, ideally as a subagent so the
   main loop's cache survives.
5. **`count_tokens`** before sending, so you know the cost in advance.

Prompt caching economics: cache **writes** cost ~1.25×, **reads** ~0.1×, and the
minimum cacheable prefix is around 1024 tokens. Max 4 breakpoints per request.

## Platform availability — the shape to remember

Claude is available first-party (Claude API), on Anthropic-operated Claude
Platform on AWS, and through the partner platforms Amazon Bedrock, Google Cloud
Vertex AI and Microsoft Foundry.

**Everywhere:** messages, streaming, tool use, PDF input, structured outputs,
adaptive thinking and effort, prompt caching, token counting, citations,
client-implemented tools (bash, text editor, memory), 1M context.

**First-party (and Claude Platform on AWS) only, or nearly so:**

| Feature | Bedrock | Vertex | Foundry |
|---|---|---|---|
| Message Batches | ❌ | ❌ | ❌ |
| Automatic prompt caching | ❌ | ❌ | β |
| Web search | ❌ | ✅ (basic variant only) | β |
| Web fetch | ❌ | ❌ | β |
| Code execution | ❌ | ❌ | β |
| MCP connector | ❌ | ❌ | β |
| Managed Agents | ❌ | ❌ | ❌ |
| `inference_geo` (data residency) | ❌ | ❌ | ❌ |
| Advisor tool | ❌ | ❌ | ❌ |

The exam-relevant generalisation: **server-side tools and the agentic
orchestration surfaces are where the partner platforms diverge most.** If a
design depends on code execution, web fetch, Managed Agents or the MCP
connector, it is a first-party design.

Also note Claude Code's own tool availability follows a similar pattern —
`RemoteTrigger`, `ScheduleWakeup`, `Monitor`, `EndConversation` and
`SendUserFile` are unavailable on Bedrock, Google Cloud and Foundry (note 12).

## Provider clients

Use the platform's dedicated client class, **not** the first-party `Anthropic()`
client with a `base_url` override:

| Platform | Python client |
|---|---|
| Amazon Bedrock | `AnthropicBedrockMantle(aws_region=…)` |
| Google Vertex AI | `AnthropicVertex(project_id=…, region=…)` |
| Microsoft Foundry | `AnthropicFoundry(api_key=…, resource=…)` |

After construction they expose the same `messages.create` / `.stream` surface.
Model IDs differ: Bedrock prefixes with `anthropic.`, Vertex uses the bare ID
(with `@` for dated snapshots), and Vertex authenticates with GCP application
default credentials rather than an Anthropic API key.

## Authentication

Credential resolution order, first match wins:

1. `ANTHROPIC_API_KEY`
2. `ANTHROPIC_AUTH_TOKEN`
3. The `ANTHROPIC_PROFILE`-selected or active OAuth profile from `ant auth login`
4. Workload Identity Federation environment variables
5. The default profile on disk

**An unset `ANTHROPIC_API_KEY` does not mean there are no credentials** — a
zero-argument `Anthropic()` works after `ant auth login`. Check with
`ant auth status` before asking anyone for a key.

For raw HTTP with an OAuth token, the token goes on `Authorization: Bearer`
(not `x-api-key`) **plus** an OAuth beta header — converting a curl from an API
key is a header change, not just a key swap.
