"""Course content, modules 4-5: automation, then the API and security."""
import json, pathlib

M = []

M.append({
"id": "m4", "title": "Running it without you", "blurb":
"Headless runs, CI, and the security posture that changes the moment no human is "
"watching a prompt.",
"lessons": [
{
 "id": "l16", "title": "Headless mode",
 "objective": "Run Claude Code from a script and consume its structured output.",
 "teach": """
<p>Add <code>-p</code> (or <code>--print</code>) and Claude Code runs
non-interactively: prompt in, result out, exit.</p>

<pre class="mini">claude -p "Find and fix the bug in auth.py" --allowedTools "Read,Edit"</pre>

<p>It behaves like a Unix tool. stdin is read (capped at <b>10MB</b>), exit code
0 on success and non-zero on failure, so scripts can branch on it.</p>

<p><b>Output formats:</b></p>
<table class="tbl">
<tr><th><code>--output-format</code></th><th>Gives you</th></tr>
<tr><td><code>text</code> (default)</td><td>plain text</td></tr>
<tr><td><code>json</code></td><td><code>result</code>, <code>session_id</code>, usage, <code>total_cost_usd</code></td></tr>
<tr><td><code>stream-json</code></td><td>newline-delimited events; the last line is the <code>result</code></td></tr>
</table>

<p>Add <code>--json-schema</code> to constrain the answer; it arrives in
<code>structured_output</code>.</p>

<p><b>Sessions persist across invocations</b>, so a script can hold a
conversation:</p>
<pre class="mini">id=$(claude -p "Start a review" --output-format json | jq -r '.session_id')
claude -p "Now check the database queries" --resume "$id"</pre>

<p>One quiet failure mode to know now: <b>a plugin or MCP server that fails to
load does not fail the run.</b> The <code>system/init</code> event carries
<code>plugin_errors</code> and <code>mcp_server_errors</code>; a CI gate has to
check them itself.</p>
""",
 "example": {"label": "Claude as a linter in package.json", "lang": "json", "code":
"""{
  "scripts": {
    "lint:claude": "git diff main | claude -p --bare \\"you are a typo linter. for each typo in this diff, report filename:line on one line and the issue on the next. return nothing else.\\""
  }
}"""},
 "takeaway": "-p makes Claude Code a Unix tool. json/stream-json give you structured output; load errors do not fail the run.",
 "checks": [{
   "q": "Your CI run passes --mcp-config and one server fails validation. What happens?",
   "choices": [
     "The run aborts with a non-zero exit",
     "The server is skipped, the run continues and exits cleanly — check mcp_server_errors yourself",
     "Claude Code prompts for confirmation",
     "The server is retried until it connects"],
   "answer": [1],
   "why": "Invalid entries are skipped and the run continues and exits cleanly. The system/init event carries mcp_servers/mcp_server_errors and plugins/plugin_errors, and a CI gate must fail on a non-empty errors array itself. When a CI runner captures stderr, no warning is printed at all."}]
},
{
 "id": "l17", "title": "Why CI needs --bare",
 "objective": "Explain the specific risk of a non-bare -p run and write a hardened command.",
 "teach": """
<p>This lesson is one fact, and it is the most security-relevant thing in the
course.</p>

<p class="callout"><b>Without <code>--bare</code>, a <code>claude -p</code> run
executes the hooks in a project's <code>.claude/settings.json</code> and connects
the servers in its <code>.mcp.json</code> — in a folder you have never trusted,
with no workspace-trust dialog and no per-server approval prompt.</b></p>

<p>Now recall Lesson 9: <code>deny</code> and <code>ask</code> bind immediately,
but <code>allow</code> waits for trust. That protection depends on a human being
able to grant trust. Under <code>-p</code>, <b>trust verification is
disabled</b> — because there is no way to show the dialog.</p>

<p>Put those together and think about CI running against a pull request from a
fork. The attacker controls <code>.claude/settings.json</code> and
<code>.mcp.json</code> in that branch.</p>

<p><b><code>--bare</code> is the answer.</b> It skips auto-discovery of hooks,
skills, commands, subagents, plugins, MCP servers, auto memory and CLAUDE.md.
It is the recommended mode for scripted and SDK calls, and is slated to become
the default for <code>-p</code>.</p>

<p>One consequence: in bare mode Claude Code <b>never reads OAuth credentials or
the system keychain</b>. Set <code>ANTHROPIC_API_KEY</code>. (Bedrock, Google
Cloud and Foundry still read their own provider credentials.)</p>

<p>The rest of a hardened run:</p>
<ul>
<li><code>-p</code> starts in <b>Manual mode on every plan</b> — so pin the mode.
<code>--permission-mode dontAsk</code> denies rather than prompting.</li>
<li>Narrow the tools. Better still, <b>pipe the input in</b> so the run needs no
Bash permission at all to see it.</li>
<li>Cap the blast radius: <code>--max-turns</code>, <code>--max-budget-usd</code>.</li>
</ul>
""",
 "example": {"label": "A run you could point at an untrusted PR", "lang": "bash", "code":
"""git diff main | claude \\
  --bare \\
  -p "Review this diff for correctness bugs. Report file:line and one line each." \\
  --permission-mode dontAsk \\
  --allowedTools "Read" \\
  --max-turns 12 \\
  --max-budget-usd 2 \\
  --output-format json

# --bare      repo config does not execute
# dontAsk     anything unlisted is denied, not queued for a prompt nobody sees
# piped diff  no Bash permission needed to read the change
# caps        a runaway loop cannot spend your afternoon"""},
 "takeaway": "Without --bare, a -p run executes untrusted repo hooks and MCP servers, and trust verification is off under -p.",
 "checks": [{
   "q": "Which safeguard is explicitly DISABLED when running with -p?",
   "choices": ["The permission system", "Trust verification for first-time codebases and new MCP servers", "Deny rules", "Credential storage"],
   "answer": [1],
   "why": "Trust verification is disabled non-interactively because the dialog cannot be shown. Combined with a non-bare run executing the repo's hooks and .mcp.json servers, that is exactly why --bare is the correct default for CI."},
  {
   "q": "You add --bare and authentication now fails, though you are logged in interactively. Why?",
   "choices": [
     "--bare requires --model",
     "In bare mode Claude Code never reads OAuth credentials or the keychain — set ANTHROPIC_API_KEY",
     "-p does not support authentication",
     "Bare mode only works on Bedrock"],
   "answer": [1],
   "why": "Bare mode does not use your subscription login. Set ANTHROPIC_API_KEY or supply an apiKeyHelper in --settings JSON. Bedrock, Google Cloud and Foundry continue reading their own provider credentials."}]
},
{
 "id": "l18", "title": "Context at scale",
 "objective": "Predict what survives compaction and choose the right tool to keep a long session healthy.",
 "teach": """
<p>Long sessions fill the window, and Claude Code compacts: it summarizes the
conversation history to fit. What happens to your carefully placed instructions
depends entirely on <em>how they were loaded</em>.</p>

<table class="tbl">
<tr><th>Mechanism</th><th>After compaction</th></tr>
<tr><td>System prompt and output style</td><td>Unchanged — never part of message history</td></tr>
<tr><td>Project-root CLAUDE.md, unscoped rules</td><td><b>Re-injected from disk</b></td></tr>
<tr><td>Auto memory</td><td><b>Re-injected from disk</b></td></tr>
<tr><td>Rules with <code>paths:</code> frontmatter</td><td><b>Lost</b> until a matching file is read again</td></tr>
<tr><td>Nested CLAUDE.md in subdirectories</td><td><b>Lost</b> until a file there is read again</td></tr>
<tr><td>Invoked skill bodies</td><td>Re-injected — capped at 5,000 tokens per skill, 25,000 total, oldest dropped first</td></tr>
<tr><td>Hooks</td><td>N/A — hooks are code, not context</td></tr>
</table>

<p>Two things follow that you can act on:</p>

<p><b>If a rule must survive compaction, drop its <code>paths:</code>
frontmatter</b> or move it to the project-root CLAUDE.md. Path-scoped rules enter
message history when their trigger file is read, so compaction summarizes them
away like anything else.</p>

<p><b>Skill truncation keeps the START of the file.</b> Put the load-bearing
instructions near the top of <code>SKILL.md</code>, never in a closing section.</p>

<p>The levers, roughly in order of how much they buy you:</p>
<ul>
<li><b>Subagents</b> — the structural fix. Reading happens in another window.</li>
<li><b>Skills</b> — bodies load on demand, so reference material is free until used.</li>
<li><b>Tool search</b> — MCP schemas stay deferred; only names load at startup.</li>
<li><code>/context</code> to diagnose, <code>/compact</code> to continue,
<code>/clear</code> when the task changed.</li>
</ul>
""",
 "example": {"label": "A rule that survives, and one that does not", "lang": "markdown", "code":
"""<!-- .claude/rules/api.md — LOST after compaction until a match is read -->
---
paths:
  - "src/api/**/*.ts"
---
All API endpoints must validate input.

<!-- .claude/rules/always.md — no paths: field, so re-injected from disk -->
Never write to the balances table directly; go through src/ledger/."""},
 "takeaway": "Path-scoped rules and nested CLAUDE.md are lost to compaction; project-root CLAUDE.md and auto memory are re-injected.",
 "checks": [{
   "q": "After a /compact, which of these is LOST until its trigger fires again?",
   "choices": ["Project-root CLAUDE.md", "Auto memory", "A rule with paths: frontmatter", "The system prompt"],
   "answer": [2],
   "why": "Project-root CLAUDE.md, unscoped rules and auto memory are re-injected from disk. The system prompt is never in message history. Path-scoped rules and nested CLAUDE.md entered message history when their trigger file was read, so compaction summarizes them away."},
  {
   "q": "Where should the most important instructions go in a long SKILL.md, and why?",
   "choices": [
     "At the end, so they are read last",
     "Near the top — compaction truncates skill bodies from the start, keeping the beginning",
     "In the frontmatter",
     "It does not matter"],
   "answer": [1],
   "why": "Skill bodies are re-injected after compaction but truncated to a 5,000-token per-skill cap, and truncation keeps the START of the file. Anything in a closing section is what gets dropped."}]
}]})

M.append({
"id": "m5", "title": "The API and the SDKs", "blurb":
"Claude Code is one way to use Claude. The exam also covers calling the API "
"directly and building agents on it.",
"lessons": [
{
 "id": "l19", "title": "The Messages API",
 "objective": "Read a response correctly and handle the stop reasons that matter.",
 "teach": """
<p>Everything goes through one endpoint: <code>POST /v1/messages</code>. Tool
use, extended thinking, caching and structured outputs are all <b>features of
that endpoint</b>, not separate APIs.</p>

<p>The API is <b>stateless</b> — you resend the full conversation every time.
That single fact is why caching and context management matter as much as they
do.</p>

<p><b>The first bug everyone writes</b> is <code>response.content[0].text</code>.
<code>content</code> is a <em>list of blocks</em> — thinking, text, tool_use —
and with thinking on, block 0 is usually a thinking block. Iterate and check
<code>block.type</code>.</p>

<p><b>Stop reasons</b> you must handle:</p>
<table class="tbl">
<tr><td><code>end_turn</code></td><td>finished naturally</td></tr>
<tr><td><code>tool_use</code></td><td>execute the tool and continue the loop</td></tr>
<tr><td><code>max_tokens</code></td><td>truncated mid-thought — you pay for the retry too</td></tr>
<tr><td><code>pause_turn</code></td><td>a server-side tool paused; resend to resume. <b>Looks like an ending and is not.</b></td></tr>
<tr><td><code>refusal</code></td><td>a safety decline. <b>Arrives as HTTP 200</b>, not an exception.</td></tr>
</table>

<p>Two current-generation details that catch people out: <b>prefill is removed</b>
(seeding the assistant turn returns a 400 — use structured outputs instead), and
<b><code>effort</code> lives inside <code>output_config</code></b>, not at the
top level.</p>
""",
 "example": {"label": "A correct first call", "lang": "python", "code":
"""import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    system="You are a concise technical writer.",
    thinking={"type": "adaptive"},        # not budget_tokens — that is a 400 now
    output_config={"effort": "medium"},   # inside output_config, not top level
    messages=[{"role": "user", "content": "Explain MCP transports briefly."}],
)

if response.stop_reason == "refusal":     # HTTP 200, not an exception
    raise SystemExit(response.stop_details.category)

for block in response.content:            # a LIST of blocks
    if block.type == "text":
        print(block.text)"""},
 "takeaway": "One endpoint, stateless, content is a list of blocks. refusal is a 200; pause_turn is not an ending.",
 "checks": [{
   "q": "Why is response.content[0].text a common bug?",
   "choices": [
     "content is a string, not a list",
     "content is a LIST of blocks — with thinking on, block 0 is usually a thinking block",
     "The field is called message, not text",
     "content is only populated when streaming"],
   "answer": [1],
   "why": "response.content is a list of content block objects: thinking, text, tool_use. Iterate and check block.type before reading .text."},
  {
   "q": "Which stop_reason looks like an ending but is not?",
   "choices": ["end_turn", "pause_turn", "max_tokens", "stop_sequence"],
   "answer": [1],
   "why": "pause_turn means a server-side tool hit an iteration limit and the turn can be resumed by sending the paused assistant content back. Treating it as terminal gives you a silently truncated answer with no error and no warning."}]
},
{
 "id": "l20", "title": "Tool use and the agent loop",
 "objective": "Write the agentic loop correctly, including the mistake that degrades it silently.",
 "teach": """
<p>You define tools; Claude asks to call them; you execute and send results
back; repeat until it stops asking. That loop <em>is</em> an agent.</p>

<p>A tool is a name, a description and a JSON Schema. <b>The description is the
highest-leverage field</b> — and the trick is to be prescriptive about
<em>when</em> to call it, not just what it does. Recent models reach for tools
conservatively, so “Call this when the user asks about current prices” measurably
raises the should-call rate over “Gets prices”.</p>

<p class="callout"><b>The silent degradation.</b> When Claude returns three
<code>tool_use</code> blocks in one message, all three <code>tool_result</code>
blocks go back in a <b>single user message</b>. Splitting them across several
messages does not error — it quietly trains Claude to stop making parallel
calls, and your agent gets slower over the conversation for no visible reason.</p>

<p>A failed tool still gets a <code>tool_result</code>, with
<code>is_error: true</code>. Dropping it leaves an unanswered
<code>tool_use</code> and the next request is rejected.</p>

<p>More generally: <b>return errors as tool results, not as exceptions.</b> An
uncaught exception aborts the run and the model never learns the tool failed.
Returning <code>"error: no records found, ask the user to widen the date range"</code>
turns a crash into a conversation.</p>
""",
 "example": {"label": "The loop, and the one-message rule", "lang": "python", "code":
"""messages = [{"role": "user", "content": user_input}]

while True:
    response = client.messages.create(
        model="claude-opus-5", max_tokens=16000,
        tools=tools, messages=messages,
    )
    if response.stop_reason == "end_turn":
        break

    messages.append({"role": "assistant", "content": response.content})

    results = [
        {"type": "tool_result", "tool_use_id": b.id, "content": run(b.name, b.input)}
        for b in response.content if b.type == "tool_use"
    ]
    messages.append({"role": "user", "content": results})   # ALL of them, ONE message"""},
 "takeaway": "All parallel tool_results go back in one user message. Return tool errors as results, never as exceptions.",
 "checks": [{
   "q": "Claude returns three tool_use blocks in one message. How do you return the results?",
   "choices": [
     "One user message per result, in order",
     "All three tool_result blocks in a single user message",
     "As a system message",
     "Under the assistant role"],
   "answer": [1],
   "why": "Splitting them across several messages silently trains Claude to stop making parallel calls — no error, just a gradually more sequential agent. A failed tool still gets a tool_result with is_error: true."}]
},
{
 "id": "l21", "title": "Prompt caching",
 "objective": "Lay out a request so the cache hits, and diagnose it when it does not.",
 "teach": """
<p>Caching can cut the cost of a large repeated prefix by up to about 90%. It is
also the feature most often silently broken.</p>

<p class="rule-flow">Caching is a <b>prefix match</b>.</p>

<p>Render order is <b>tools → system → messages</b>. Any byte change anywhere in
the cached prefix invalidates <em>everything after it</em>. So: stable content
first, volatile content after the last breakpoint.</p>

<p><b>Verify, never assume.</b> If <code>usage.cache_read_input_tokens</code> is
zero across repeated identical-prefix requests, something is invalidating it:</p>

<table class="tbl">
<tr><th>Invalidator</th><th>Fix</th></tr>
<tr><td><code>datetime.now()</code> or a UUID in the system prompt</td><td>move it after the breakpoint</td></tr>
<tr><td><code>json.dumps()</code> on an unsorted dict</td><td><code>sort_keys=True</code></td></tr>
<tr><td>A tool list built from a set</td><td>sort it</td></tr>
<tr><td>A prefix under ~1024 tokens</td><td>too short to cache at all</td></tr>
</table>

<p>Economics: writes cost about <b>1.25×</b>, reads about <b>0.1×</b>. Max 4
breakpoints. That asymmetry is why a prefix that gets rewritten every turn is
<em>worse</em> than not caching at all.</p>

<p>Three agent-specific workarounds worth memorizing, because each looks
harmless and is not:</p>
<ul>
<li>Editing the system prompt mid-session invalidates the cache → append a
<code>{"role": "system"}</code> message to <code>messages[]</code> instead.</li>
<li>Switching models mid-session invalidates it → spawn a <b>subagent</b> on the
cheaper model and keep the main loop on one model.</li>
<li>Adding or removing tools invalidates it → use <b>tool search</b>, which
<em>appends</em> schemas rather than swapping them.</li>
</ul>
""",
 "example": {"label": "Stable first, volatile last", "lang": "python", "code":
"""response = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    system=[{
        "type": "text",
        "text": BIG_STABLE_CONTEXT,               # never changes between calls
        "cache_control": {"type": "ephemeral"},   # <- the breakpoint
    }],
    messages=[{"role": "user", "content": todays_question}],  # volatile, after it
)

print(response.usage.cache_read_input_tokens)   # 0 means something broke it"""},
 "takeaway": "Prefix match, tools→system→messages. Stable first. Verify with cache_read_input_tokens.",
 "checks": [{
   "q": "Where should volatile content — a timestamp, the user's question — go?",
   "choices": [
     "At the very start so the model sees it first",
     "After the last cache_control breakpoint",
     "Anywhere — the cache keys on content, not position",
     "In the tools array"],
   "answer": [1],
   "why": "Render order is tools, then system, then messages, and any byte change in the cached prefix invalidates everything after it. Stable content goes first; volatile content goes after the last breakpoint."},
  {
   "q": "cache_read_input_tokens is zero across repeated requests with what should be an identical prefix. Which are plausible causes?",
   "choices": [
     "A datetime.now() or UUID in the system prompt",
     "json.dumps() on an unsorted dict",
     "A tool list built from a set, so its order varies",
     "Using the same model on every request"],
   "answer": [0, 1, 2],
   "why": "Those are the classic silent invalidators, plus a prefix under ~1024 tokens which never caches at all. Keeping the model constant HELPS — switching models mid-session is itself an invalidator."}]
},
{
 "id": "l22", "title": "Four ways to build an agent",
 "objective": "Distinguish the Tool Runner, the Claude Agent SDK, and Managed Agents.",
 "teach": """
<p>Two independent questions separate the options: <b>who supplies the
harness</b> (the loop and context management), and <b>who supplies the
deployment</b> (the infrastructure it runs on).</p>

<table class="tbl">
<tr><th>Approach</th><th>You write</th><th>Harness / deployment</th></tr>
<tr><td>Manual loop</td><td>the <code>while</code> loop yourself</td><td>you build it, you host it</td></tr>
<tr><td><b>Tool Runner</b><br><code>client.beta.messages.tool_runner</code></td><td>just the tool functions</td><td>SDK harness, <b>you host</b></td></tr>
<tr><td><b>Claude Agent SDK</b><br><code>claude-agent-sdk</code></td><td>a prompt + options</td><td>Claude Code harness, <b>you host</b></td></tr>
<tr><td><b>Managed Agents</b></td><td>an agent config</td><td>Anthropic harness <b>and</b> hosted sandbox</td></tr>
</table>

<p class="callout"><b>Tool Runner ≠ Claude Agent SDK.</b> They sound alike and
are different packages. Tool Runner lives in the regular Anthropic API SDK and is
a thin helper over <code>POST /v1/messages</code> that loops over tools
<em>you</em> define — no built-in tools, no filesystem, no sandbox. The Claude
Agent SDK is Claude Code packaged as a library: built-in Read/Write/Edit/Bash,
subagents, hooks, permissions, sessions.</p>

<p><b>Both are harness-only — you host and deploy them.</b> Only Managed Agents
adds managed deployment.</p>

<p>Before choosing the agent tier at all, the docs give four criteria:
<b>complexity</b> (multi-step and hard to specify up front?), <b>value</b> (does
it justify the cost and latency?), <b>viability</b> (is Claude good at this?),
and <b>cost of error</b> (can mistakes be caught?). Any “no” means drop to a
scripted workflow or a single call. Most production LLM work is a single call.</p>
""",
 "example": {"label": "Tool Runner: you write tools, not loops", "lang": "python", "code":
"""from anthropic import Anthropic, beta_tool

@beta_tool
def get_weather(location: str, unit: str = "celsius") -> str:
    \"\"\"Get current weather for a location.

    Call this when the user asks about weather, temperature or conditions.

    Args:
        location: City and state, e.g. San Francisco, CA.
        unit: Either "celsius" or "fahrenheit".
    \"\"\"
    return f"18C and raining in {location}"

runner = Anthropic().beta.messages.tool_runner(
    model="claude-opus-5", max_tokens=16000,
    tools=[get_weather],
    messages=[{"role": "user", "content": "Weather in Paris?"}],
)
for message in runner:      # the SDK drives the loop
    print(message)

# The docstring IS the tool description. The Args: block IS the schema."""},
 "takeaway": "Tool Runner = API SDK helper, your tools only. Agent SDK = Claude Code as a library. Only Managed Agents hosts it too.",
 "checks": [{
   "q": "What is the difference between the SDK's Tool Runner and the Claude Agent SDK?",
   "choices": [
     "Two names for the same package",
     "Tool Runner is a helper in the Anthropic API SDK that loops over tools YOU define; the Claude Agent SDK is a separate package shipping the Claude Code harness with built-in file and bash tools",
     "Tool Runner is hosted by Anthropic; the Agent SDK runs locally",
     "Tool Runner is Python-only; the Agent SDK is TypeScript-only"],
   "answer": [1],
   "why": "Tool Runner is a thin helper over POST /v1/messages with no built-in tools and no sandbox. The Claude Agent SDK is Claude Code as a library. Both are harness-only — you host and deploy them; only Managed Agents adds managed deployment."},
  {
   "q": "Which approach gives you BOTH a managed agent loop and Anthropic-hosted infrastructure?",
   "choices": ["A manual loop", "The Tool Runner", "Managed Agents", "The Claude Agent SDK"],
   "answer": [2],
   "why": "The manual loop supplies neither; Tool Runner and the Claude Agent SDK supply a harness but you still host it. Only Managed Agents supplies both — Anthropic runs the loop and hosts a per-session sandbox."}]
},
{
 "id": "l23", "title": "The Agent SDK's permission flow",
 "objective": "Order the six steps and avoid the two traps that silently disable your checks.",
 "teach": """
<p>The Agent SDK's evaluation order is <b>richer than the CLI's</b>
deny→ask→allow, and the extra steps are where the traps live.</p>

<ol class="steps">
<li><b>Hooks</b> — run first. Can deny outright. A hook returning <code>allow</code> does <b>not</b> skip steps 2 and 3.</li>
<li><b>Deny rules</b> — block even in <code>bypassPermissions</code>.</li>
<li><b>Ask rules</b> — fall through to your callback, even in <code>bypassPermissions</code>.</li>
<li><b>Permission mode</b> — <code>bypassPermissions</code> approves; <code>plan</code> routes edits to the callback regardless of allow rules.</li>
<li><b>Allow rules</b> — approve if matched.</li>
<li><b><code>can_use_tool</code> callback</b> — only if nothing above resolved it. <b>Skipped entirely in <code>dontAsk</code></b>, which denies instead.</li>
</ol>

<p class="callout"><b>Trap 1: auto-approved tools never reach
<code>can_use_tool</code>.</b> A security check in your callback is silently
bypassed for anything an allow rule, <code>acceptEdits</code> or
<code>bypassPermissions</code> already approved. A bare entry like
<code>allowed_tools=["Read"]</code> auto-approves <em>every</em> Read. For a check
that must run on every call, use a <code>PreToolUse</code> hook — hooks run
before every other step.</p>

<p class="callout"><b>Trap 2: <code>allowed_tools</code> does not constrain
<code>bypassPermissions</code>.</b> Unlisted tools are simply unmatched by an
allow rule, so they fall through to the mode — which approves them.
<code>allowed_tools=["Read"]</code> with <code>bypassPermissions</code> still
permits Bash, Write and Edit. To block specific tools under bypass, use
<code>disallowed_tools</code>.</p>

<p>For a genuinely locked-down agent, pair them the other way:
<code>allowed_tools=[…]</code> with <code>permission_mode="dontAsk"</code>.</p>
""",
 "example": {"label": "Locked down, and the trap beside it", "lang": "python", "code":
"""# CORRECT: explicit surface, everything else denied outright
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep"],
    permission_mode="dontAsk",
)

# TRAP: this approves EVERY tool, including Bash, Write and Edit.
options = ClaudeAgentOptions(
    allowed_tools=["Read"],
    permission_mode="bypassPermissions",   # unlisted tools fall through to the mode
)"""},
 "takeaway": "Hooks → deny → ask → mode → allow → callback. Auto-approved tools skip the callback; allowed_tools does not constrain bypass.",
 "checks": [{
   "q": "Put the Agent SDK's permission evaluation steps in order.",
   "choices": [
     "Deny, ask, allow, hooks, mode, canUseTool",
     "Hooks, deny rules, ask rules, permission mode, allow rules, canUseTool",
     "canUseTool, hooks, deny, ask, allow, mode",
     "Permission mode, hooks, deny, ask, allow, canUseTool"],
   "answer": [1],
   "why": "Hooks run first and can deny outright, but a hook returning allow does not skip the deny and ask rules below it. The callback is last, and is skipped entirely in dontAsk mode."},
  {
   "q": "You put a security check in can_use_tool and set allowed_tools=['Read']. Why might the check never run for Read?",
   "choices": [
     "can_use_tool only fires for Bash",
     "Auto-approved tools never reach the callback — a bare allow entry approves every call to that tool first",
     "Read is read-only and exempt from checks",
     "The callback must be registered before allowed_tools"],
   "answer": [1],
   "why": "Anything approved at an earlier step skips the callback. A bare name like 'Read' auto-approves every Read; a scoped rule like Bash(ls *) only auto-approves matching calls. Use a PreToolUse hook for a check that must run on every call."}]
},
{
 "id": "l24", "title": "Untrusted content and the sandbox",
 "objective": "Name the injection surfaces and say what the Bash sandbox does that permissions cannot.",
 "teach": """
<p>The last idea, and the one that ties the course together.</p>

<p class="callout"><b>Everything the model reads is untrusted.</b> Issue bodies,
PR review comments, CI logs, web pages, MCP tool output, files in a repo you
cloned. All of it is attacker-influenceable, and all of it must be treated as
<b>data, never as instructions</b>.</p>

<p>Claude Code's own defences are worth knowing by name: the permission system;
context-aware analysis; <b>network commands like <code>curl</code> and
<code>wget</code> are not auto-approved</b>; WebFetch runs in an <b>isolated
context window</b> specifically so fetched content cannot inject into your
conversation; trust verification; command-injection detection even for
previously allowlisted commands; and fail-closed matching.</p>

<p>But permissions have a structural limit. They are evaluated <em>before</em> a
command runs, <em>from the command string</em>. They cannot know what a command
will actually do.</p>

<p><b>That is what the sandbox adds.</b></p>

<table class="tbl">
<tr><th></th><th>Controls</th><th>Enforced</th></tr>
<tr><td>Permission rules</td><td>whether a call runs</td><td>before it, from the command string</td></tr>
<tr><td><b>Sandbox</b></td><td>what a Bash command can <em>access</em></td><td><b>by the OS, on the running process</b></td></tr>
</table>

<p>So the sandbox holds <b>regardless of what the model chose to run, and even if
an allowed command does more than its name suggests</b>. macOS uses Seatbelt,
Linux and WSL2 use bubblewrap. It covers Bash and its children only — Read, Edit
and Write go through the permission system instead.</p>

<p>One rule to carry: in sandbox filesystem policy, <b>a deny holds inside a
wider allow</b>, and a narrow allow re-opens a denied region. So
<code>allowRead: ["~/"]</code> with <code>denyRead: ["~/.env"]</code> gives you
the home directory <em>without</em> the secret — a broad allow cannot silently
re-expose it.</p>

<p>And the honest caveat: by default the network proxy does not inspect TLS, so
allowing a broad domain like <code>github.com</code> still creates an
exfiltration path.</p>
""",
 "example": {"label": "A policy your credentials survive", "lang": "json", "code":
"""{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "denyRead":  ["~/"],
      "allowRead": ["~/code", "~/.cache"]
    },
    "credentials": {
      "files": [{ "path": "~/.ssh", "mode": "deny" }],
      "env":   [{ "name": "GITHUB_TOKEN", "mode": "deny" }]
    },
    "network": { "allowedDomains": ["registry.npmjs.org"] }
  }
}"""},
 "takeaway": "Permissions gate whether a call runs, from its text. The sandbox gates what it can touch, enforced by the OS.",
 "checks": [{
   "q": "What is the essential difference between a permission rule and the Bash sandbox?",
   "choices": [
     "None — the sandbox is a permission mode",
     "Permission rules decide whether a call runs, evaluated beforehand from the command string; the sandbox restricts what a running command can access, enforced by the OS on the process",
     "Permission rules are OS-enforced; the sandbox is advisory",
     "The sandbox covers every tool; permission rules cover only Bash"],
   "answer": [1],
   "why": "Permission rules are evaluated before a tool runs and apply to every tool. The sandbox is OS-level enforcement on the running process and applies only to Bash and its children — so it holds regardless of what the model chose to run."},
  {
   "q": "Sandbox filesystem policy has allowRead: ['~/'] and denyRead: ['~/.env']. What is readable?",
   "choices": [
     "Everything under home, including ~/.env — the broader allow wins",
     "Nothing — the rules conflict",
     "Everything under home except ~/.env — a deny holds inside a wider allow",
     "Only ~/.env"],
   "answer": [2],
   "why": "A deny holds inside a wider allow, so a broad allow cannot silently re-expose a secret. The reverse also works: denyRead ~/ with allowRead ~/projects re-opens that narrower region."},
  {
   "q": "Why does WebFetch use a separate context window?",
   "choices": [
     "To reduce latency",
     "To avoid injecting potentially malicious fetched content into the main conversation",
     "Because HTML is large",
     "To enable caching"],
   "answer": [1],
   "why": "Isolated context windows for web fetch are a named prompt-injection safeguard: fetched content is analyzed separately rather than dropped into the main conversation where it could act as instructions."}]
}]})

pathlib.Path("part3.json").write_text(json.dumps(M, indent=1))
print(f"modules: {len(M)}  lessons: {sum(len(m['lessons']) for m in M)}  "
      f"checks: {sum(len(l['checks']) for m in M for l in m['lessons'])}")
