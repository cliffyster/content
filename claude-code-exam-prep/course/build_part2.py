"""Course content, module 3: extending Claude Code."""
import json, pathlib

M = [{
"id": "m3", "title": "Extending Claude Code", "blurb":
"Four mechanisms — skills, hooks, subagents, MCP. Each solves a different problem, "
"and choosing the wrong one is the most common mistake.",
"lessons": [
{
 "id": "l10", "title": "Choosing a mechanism",
 "objective": "Given a requirement, name which of the four extension points it belongs to.",
 "teach": """
<p>Before the details, the decision. Four mechanisms, four different jobs:</p>

<table class="tbl">
<tr><th>You want…</th><th>Use</th><th>Because</th></tr>
<tr><td>Claude to know a fact, always</td><td><b>CLAUDE.md</b></td><td>loaded every session</td></tr>
<tr><td>A repeatable procedure, on demand</td><td><b>Skill</b></td><td>loads only when invoked — costs nothing until used</td></tr>
<tr><td>Something to happen <em>every time</em>, guaranteed</td><td><b>Hook</b></td><td>the harness runs it as code; Claude cannot forget</td></tr>
<tr><td>Work done without polluting your context</td><td><b>Subagent</b></td><td>separate context window; returns a conclusion</td></tr>
<tr><td>Access to an external system</td><td><b>MCP</b></td><td>connects real tools and data</td></tr>
</table>

<p>The two failure modes are worth naming now, because both are common:</p>

<p><b>Putting a procedure in CLAUDE.md.</b> It works, but you pay its tokens on
every turn of every session forever, and adherence drops as the file grows. If a
section of your CLAUDE.md has become a numbered procedure rather than a fact,
that is the signal to make it a skill.</p>

<p><b>Putting a guarantee in a prompt.</b> “Always run the linter” in CLAUDE.md,
in your prompt, or in a skill is a request. Only a hook is a guarantee. If the
answer to “what if Claude doesn't?” is “that's a problem”, you need a hook.</p>
""",
 "example": {"label": "The same requirement, three ways", "lang": "text", "code":
"""\"We use pnpm, not npm\"
  -> CLAUDE.md. A fact, always relevant, one line.

\"Here is our 12-step release procedure\"
  -> Skill. Long, only relevant when releasing, loads on demand.

\"Never let a commit through without the linter passing\"
  -> Hook. A guarantee. PostToolUse on Edit|Write, or PreToolUse on
     Bash(git commit *)."""},
 "takeaway": "Facts → CLAUDE.md. Procedures → skills. Guarantees → hooks. Context isolation → subagents. External systems → MCP.",
 "checks": [{
   "q": "A section of your CLAUDE.md has grown into a numbered 12-step deployment procedure. What should you do?",
   "choices": [
     "Leave it — CLAUDE.md is the right home for instructions",
     "Move it to a skill, so it loads only when you invoke it",
     "Move it to a hook",
     "Split it across several CLAUDE.md files"],
   "answer": [1],
   "why": "A skill's body loads only when used, so long reference material costs almost nothing until you need it. A CLAUDE.md section costs its tokens on every turn of every session. 'A section that has become a procedure rather than a fact' is the documented signal to convert it."}]
},
{
 "id": "l11", "title": "Skills",
 "objective": "Write a skill, and explain the two different lifetimes inside it.",
 "teach": """
<p>A skill is a markdown file with YAML frontmatter that becomes a slash command.
<code>.claude/skills/deploy/SKILL.md</code> gives you <code>/deploy</code>.</p>

<p>(Custom commands were merged into skills. A file at
<code>.claude/commands/deploy.md</code> does the same thing and still works; the
skill form adds a directory for supporting files and richer frontmatter.)</p>

<p>Claude can invoke a skill itself when it seems relevant — which you often do
<em>not</em> want for anything with side effects. Hence:</p>

<pre class="mini">disable-model-invocation: true   # only you can trigger it</pre>

<p>Now the part that gets tested. A skill has <b>two different lifetimes</b>:</p>

<table class="tbl">
<tr><th></th><th>Lifetime</th></tr>
<tr><td>The skill's <b>content</b></td><td>Enters the conversation once and <b>stays for the whole session</b>. Claude Code never re-reads the file.</td></tr>
<tr><td>Its <code>allowed-tools</code> <b>grant</b></td><td>Applies to <b>the invoking turn only</b>. Clears when you send your next message.</td></tr>
</table>

<p>The practical consequence: <b>write standing instructions, not one-time
steps.</b> “First, read the changelog” reads fine on turn one and badly on turn
nine, because the text is still sitting there. Write “Always prefer X over Y”
instead.</p>

<p><b>Arguments</b> use <code>$ARGUMENTS</code> for the whole string, or
<code>$ARGUMENTS[N]</code> / <code>$N</code> for one by index — <b>0-based</b>, so
<code>$0</code> is the <em>first</em> argument. If you pass arguments and the body
has no placeholder, Claude Code appends <code>ARGUMENTS: your text</code> so
nothing is lost.</p>

<p class="callout"><b>Security note.</b> Workspace trust does <em>not</em> gate
<code>allowed-tools</code>. A skill committed to a repository applies its grant
whenever it is invoked — including in a <code>-p</code> run in a folder you have
never trusted. Read the <code>allowed-tools</code> of repository skills before
running Claude Code there.</p>
""",
 "example": {"label": "A skill with a scoped, prompt-free grant", "lang": "markdown", "code":
"""---
name: commit
description: Stage and commit the current changes with a conventional message.
argument-hint: "[scope]"
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
---

Review the staged changes and commit them.

- Write a conventional-commit subject line, scoped to $ARGUMENTS if given.
- Never commit files the user did not stage.
- If nothing is staged, say so and stop — do not stage anything yourself."""},
 "takeaway": "Skill content persists all session; its allowed-tools grant lasts one turn. $0 is the first argument.",
 "checks": [{
   "q": "How long does a skill's allowed-tools grant last?",
   "choices": [
     "The whole session",
     "Only the turn that invoked the skill — it clears at your next message",
     "Until the skill is invoked again",
     "Permanently, once written to settings"],
   "answer": [1],
   "why": "The grant covers the invoking turn and clears when you send your next message, even though the skill's CONTENT stays in context for the whole session. To pre-approve for a whole session, use permission settings instead."},
  {
   "q": "Your skill body says 'First, read the changelog.' On turn nine Claude reads it again unprompted. Why?",
   "choices": [
     "A bug in skill handling",
     "The rendered skill content stays in the conversation for the session, so a one-time step reads as a standing instruction forever",
     "The skill was invoked twice",
     "Because allowed-tools was still active"],
   "answer": [1],
   "why": "The rendered SKILL.md enters the conversation as one message and persists; Claude Code does not re-read the file on later turns. Write guidance as standing instructions rather than sequenced steps."},
  {
   "q": "In a skill body, what does $1 expand to?",
   "choices": ["The first argument", "The second argument — indexing is 0-based", "The literal text '$1'", "The full argument string"],
   "answer": [1],
   "why": "$N is shorthand for $ARGUMENTS[N] and indexing is 0-based, so $0 is first and $1 is second. Bare $ARGUMENTS is the whole string as typed."}]
},
{
 "id": "l12", "title": "Hooks — the guarantee mechanism",
 "objective": "Write a hook that blocks a tool call, and read its exit codes correctly.",
 "teach": """
<p>A hook is code the <b>harness</b> runs at a fixed lifecycle point. That is the
entire reason it exists: “please always run the linter” is a request Claude can
forget; a <code>PostToolUse</code> hook cannot.</p>

<p>Configuration nests three levels: <b>event</b> → <b>matcher group</b> →
<b>handler</b>.</p>

<p>The events you will actually use:</p>
<ul>
<li><code>PreToolUse</code> — before a call. <b>Can block.</b></li>
<li><code>PostToolUse</code> — after success. (Failures fire <code>PostToolUseFailure</code>.)</li>
<li><code>UserPromptSubmit</code> — before Claude sees your prompt. Can block or rewrite it.</li>
<li><code>SessionStart</code> / <code>SessionEnd</code>, <code>PreCompact</code> / <code>PostCompact</code>, <code>SubagentStart</code> / <code>SubagentStop</code></li>
</ul>

<p>Your hook receives the event as JSON on <b>stdin</b> and communicates back two
ways.</p>

<p><b>Exit codes</b> — three outcomes, and the third is the trap:</p>
<table class="tbl">
<tr><th>Exit</th><th>Meaning</th></tr>
<tr><td><code>0</code></td><td>Success. stdout is parsed as JSON for structured control.</td></tr>
<tr><td><code>2</code></td><td><b>Blocking error.</b> The call is stopped.</td></tr>
<tr><td>anything else</td><td><b>Non-blocking</b> error — reported, and the action <b>proceeds</b>.</td></tr>
</table>

<p class="callout">A hook with a typo that exits 1 does not fail loudly. It
silently stops protecting you.</p>

<p><b>Structured JSON</b> is the richer path — it lets you deny <em>with a
reason Claude can act on</em>, or even rewrite the tool's input.</p>

<p>Matchers are worth one line of care: a matcher of only letters, digits,
<code>_</code>, <code>-</code>, spaces, commas or pipes is an exact string or
list (<code>Edit|Write</code>). Anything else is compiled as an <b>unanchored
JavaScript regex</b> (<code>^Notebook.*</code>).</p>
""",
 "example": {"label": "A PreToolUse hook that denies with a reason", "lang": "bash", "code":
"""#!/usr/bin/env bash
# .claude/hooks/block-force-push.sh
set -uo pipefail

command=$(jq -r '.tool_input.command // ""')

if printf '%s' "$command" | grep -q -- '--force'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Force push blocked. Use --force-with-lease."
    }
  }'
fi
exit 0   # no output = no decision; the normal permission flow applies"""},
 "takeaway": "Exit 0 = success (JSON read), 2 = block, anything else = the action proceeds anyway.",
 "checks": [{
   "q": "Your hook script has a typo and exits with status 1. Does the tool call still run?",
   "choices": [
     "No — any non-zero exit blocks",
     "Yes — only 2 is a blocking error; every other non-zero code is non-blocking and the action proceeds",
     "It retries the hook",
     "The session ends"],
   "answer": [1],
   "why": "Only 0 (success) and 2 (blocking error) are special. Every other exit code is a non-blocking error: it is reported, and the action proceeds. A broken hook silently stops protecting you — which is why you test hooks by piping JSON into them."},
  {
   "q": "Which JSON does a PreToolUse hook emit to deny a call with a reason?",
   "choices": [
     "{\"decision\": \"deny\", \"reason\": \"...\"}",
     "{\"hookSpecificOutput\": {\"hookEventName\": \"PreToolUse\", \"permissionDecision\": \"deny\", \"permissionDecisionReason\": \"...\"}}",
     "{\"block\": true}",
     "{\"continue\": false}"],
   "answer": [1],
   "why": "PreToolUse uses hookSpecificOutput with permissionDecision and permissionDecisionReason, and can also supply updatedInput to rewrite the call. The bare {decision, reason} shape belongs to the PermissionRequest event."}]
},
{
 "id": "l13", "title": "Hooks vs. rules — the precedence you must know",
 "objective": "Predict the outcome when a hook and a permission rule disagree, in both directions.",
 "teach": """
<p>Hooks and permission rules both gate tool calls, so what happens when they
disagree? The answer is asymmetric, and both halves are tested.</p>

<p><b>Direction 1 — a hook says allow, a deny rule matches.</b></p>
<p class="rule-flow">Deny rule wins. The call is blocked.</p>
<p>Hook decisions do not bypass permission rules. Claude Code evaluates deny and
ask rules regardless of what a <code>PreToolUse</code> hook returned. Deny-first
precedence is preserved, including for deny rules from managed settings.</p>

<p><b>Direction 2 — a hook exits 2, an allow rule matches.</b></p>
<p class="rule-flow">Hook wins. The call is blocked.</p>
<p>An exit-2 hook stops the call <em>before</em> permission rules are evaluated
at all.</p>

<p>Read those together and the principle is clean: <b>restrictions win in both
directions.</b> Nothing you configure can make a call run that something else
wanted blocked.</p>

<p>And that asymmetry is what solves the problem from Lesson 5 — “allow all of X
except Y”, which deny rules alone cannot express:</p>

<p class="callout"><b>The pattern:</b> put <code>"Bash"</code> in your
<code>allow</code> list, then register a <code>PreToolUse</code> hook that
rejects the specific cases. The allow rule handles the common path with no
prompts; the hook, running first, catches the exceptions with the full
expressive power of code rather than a glob.</p>
""",
 "example": {"label": "Allow-with-exceptions", "lang": "json", "code":
"""{
  "permissions": { "allow": ["Bash"] },

  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/gate.sh",
        "args": []
      }]
    }]
  }
}

// gate.sh inspects the whole command and exits 2 for the cases you
// refuse — something a prefix glob could never express safely."""},
 "takeaway": "Hook 'allow' loses to a deny rule; hook exit 2 beats an allow rule. Restrictions win in both directions.",
 "checks": [{
   "q": "A PreToolUse hook returns permissionDecision 'allow', but a project deny rule also matches. What happens?",
   "choices": [
     "The hook wins and the call runs",
     "The deny rule wins and the call is blocked",
     "You are prompted",
     "Claude Code errors"],
   "answer": [1],
   "why": "Hook decisions do not bypass permission rules. Deny and ask rules are evaluated regardless of what a PreToolUse hook returns, preserving deny-first precedence."},
  {
   "q": "You want every Bash command to run without prompting EXCEPT a handful you consider dangerous. What is the documented approach?",
   "choices": [
     "Add 'Bash' to allow, and a PreToolUse hook that exits 2 for the dangerous cases",
     "Add 'Bash' to allow plus narrower deny rules — allow wins for everything else",
     "Use bypassPermissions with a PostToolUse hook",
     "Not possible — allow and deny cannot combine on one tool"],
   "answer": [0],
   "why": "A hook exiting 2 stops the call before permission rules are evaluated, so it overrides the allow rule. Deny rules cannot do this, because a deny rule cannot carry allowlist exceptions — a broad deny blocks everything it matches."}]
},
{
 "id": "l14", "title": "Subagents",
 "objective": "Say what a subagent does and does not receive, and when the handoff is worth it.",
 "teach": """
<p>A subagent is a specialized assistant with <b>its own context window</b>. You
reach for one for two reasons: a task produces output you do not want in your
main conversation, or you want to hard-limit what a piece of work can touch.</p>

<p>Defined as markdown with frontmatter in <code>.claude/agents/</code>. Only
<code>name</code> and <code>description</code> are required.</p>

<p><b>The constraint is structural, not persuasive.</b> Setting
<code>tools: Read, Grep, Glob</code> removes the write tools from the agent's
pool entirely. A confused agent, a bad prompt, or injected text in a file it
reads cannot make it write. That is a different kind of guarantee from asking it
nicely.</p>

<p>What crosses the boundary matters:</p>
<table class="tbl">
<tr><th>Receives</th><th>Does not receive</th></tr>
<tr><td>Its own system prompt</td><td><b>The main conversation history</b></td></tr>
<tr><td>The task message Claude writes for it</td><td>Output style preferences</td></tr>
<tr><td><code>CLAUDE.md</code> (except Explore/Plan)</td><td>Auto memory from the main session</td></tr>
<tr><td>A git status snapshot</td><td>Skills invoked earlier in the main session</td></tr>
</table>

<p class="callout">A subagent <b>cannot call <code>AskUserQuestion</code></b> — it
is removed, along with <code>EndConversation</code>, plan-mode tools and
<code>Workflow</code>. So design its prompt to resolve its own ambiguity, or to
report both readings and let the main session decide. It cannot stop and ask.</p>

<p><b>@-mention guarantees</b> a specific subagent runs; relying on the
description means Claude decides. <code>model</code> defaults to
<code>inherit</code> — routing verbose mechanical work to a faster model is a
real cost lever.</p>

<p>And when <em>not</em> to: a subagent starting from a blank context has to
rediscover what you already know. For a small edit in a file you are looking at,
the handoff costs more than it saves.</p>
""",
 "example": {"label": "An agent that cannot write, by construction", "lang": "markdown", "code":
"""---
name: notes-auditor
description: Audit the notes in docs/ against the code and report drift.
             Use when asked whether documentation is still accurate.
tools: Read, Grep, Glob
model: inherit
---

You audit documentation against the code it describes.

Report only — you have no write tools and must not ask for them.
Proposing an edit is the main session's job, not yours.

For each finding give file:line for both sides, then your judgement of
which is correct. If you find nothing, say so in one sentence."""},
 "takeaway": "Own context window, no conversation history, cannot ask questions. Tool limits are structural, not advisory.",
 "checks": [{
   "q": "Your subagent needs to ask the user which of two readings they meant. How does it do that?",
   "choices": [
     "With AskUserQuestion",
     "It cannot — that tool is removed from every subagent; design the prompt to resolve or report both readings",
     "By returning a special exit code",
     "By spawning a sub-subagent"],
   "answer": [1],
   "why": "AskUserQuestion is removed from every subagent, along with EndConversation, the plan-mode tools, ScheduleWakeup and Workflow. A subagent's prompt must resolve its own ambiguity or report both options for the main session to decide."},
  {
   "q": "What does a non-fork subagent NOT receive?",
   "choices": [
     "The main conversation history",
     "CLAUDE.md files",
     "A git status snapshot",
     "Skills previously invoked in the main session"],
   "answer": [0, 3],
   "why": "It gets a fresh context: its own system prompt, the task message, CLAUDE.md (except Explore and Plan), a git status snapshot, and any preloaded skills. It does not get the main conversation history, output style, auto memory, or skills invoked earlier. A fork is the variant that DOES inherit the full history."}]
},
{
 "id": "l15", "title": "MCP",
 "objective": "Add a server, name its tools in a rule, and explain the approval asymmetry.",
 "teach": """
<p>MCP — the Model Context Protocol — is an open standard for connecting Claude
to external systems. Connect a server when you find yourself copying data into
chat from somewhere else.</p>

<p>Four transports, added four ways:</p>
<pre class="mini">claude mcp add --transport http  notion https://mcp.notion.com/mcp
claude mcp add --transport sse    asana https://mcp.asana.com/sse
claude mcp add --transport stdio  local -- npx -y my-server
claude mcp add-json events '{"type":"ws","url":"wss://…"}'</pre>

<p>For stdio servers the bare <code>--</code> separates Claude's own flags from
the server's command line; everything after it is passed through untouched.
(<code>--transport</code> does not accept <code>ws</code> — WebSocket servers must
go through <code>add-json</code> or <code>.mcp.json</code>.)</p>

<p><b>Tools are named <code>mcp__&lt;server&gt;__&lt;tool&gt;</code></b> —
<code>mcp__github__get_issue</code>. That naming is what permission rules and hook
matchers must use. And allow globs need a <b>literal, glob-free server
segment</b>: <code>mcp__github__get_*</code> works, <code>mcp__*</code> is skipped
with a warning and approves nothing.</p>

<p><b>Three scopes:</b> <code>local</code> (default, private to you),
<code>project</code> (writes <code>.mcp.json</code> at the repo root, meant to be
committed), and <code>user</code> (all your projects).</p>

<p class="callout"><b>The asymmetry that matters.</b> Project-scoped servers from
<code>.mcp.json</code> prompt for approval in <b>interactive</b> sessions.
<code>claude -p</code>, Agent SDK sessions and cloud sessions <b>cannot show that
prompt, so they load them without asking.</b></p>

<p>Read that twice. A <code>.mcp.json</code> in a repo you cloned is a request to
run someone else's code, and CI is exactly the place where nobody sees the
prompt. To exclude a server regardless of mode, use
<code>disabledMcpjsonServers</code>.</p>
""",
 "example": {"label": "Project config and a matching allow rule", "lang": "json", "code":
"""// .mcp.json — committed, shared with the team
{
  "mcpServers": {
    "github": { "type": "http", "url": "https://api.githubcopilot.com/mcp/" }
  }
}

// .claude/settings.json — approve only the read-only tools
{
  "permissions": {
    "allow": ["mcp__github__get_*", "mcp__github__list_*"]
  }
}"""},
 "takeaway": "mcp__server__tool naming. Project servers prompt interactively but load silently under -p, the SDK and cloud.",
 "checks": [{
   "q": "A repo contains .mcp.json. In which contexts do those servers load WITHOUT an approval prompt?",
   "choices": ["An interactive terminal session", "A `claude -p` run", "An Agent SDK session", "A cloud session"],
   "answer": [1, 2, 3],
   "why": "Interactive sessions prompt before using project-scoped servers. Non-interactive contexts cannot show that prompt, so they load them without asking — which is why a .mcp.json from an untrusted repo is a real supply-chain concern in CI."},
  {
   "q": "Which MCP allow rule actually auto-approves tools?",
   "choices": ["mcp__*", "mcp__github__get_*", "\"*\"", "mcp__*__get_issue"],
   "answer": [1],
   "why": "Allow rules accept tool-name globs only after a literal mcp__<server>__ prefix, and the server segment must be glob-free. Unanchored globs are skipped with a warning and approve nothing."}]
}]}]

pathlib.Path("part2.json").write_text(json.dumps(M, indent=1))
print(f"modules: {len(M)}  lessons: {sum(len(m['lessons']) for m in M)}  "
      f"checks: {sum(len(l['checks']) for m in M for l in m['lessons'])}")
