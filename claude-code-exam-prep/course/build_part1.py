"""Course content, modules 1-2. Authored as Python for readable multi-line prose."""
import json, pathlib

M = []

M.append({
"id": "m1", "title": "How Claude Code works", "blurb":
"Before any configuration makes sense, you need the mental model: what a session "
"is, what Claude can see, and who decides what runs.",
"lessons": [
{
 "id": "l1", "title": "What Claude Code actually is",
 "objective": "Describe the agent loop and say what makes Claude Code different from a chat window.",
 "teach": """
<p>Claude Code is <b>an agent that runs on your machine</b>. You describe a goal in
plain English; it reads files, runs commands, and edits code to get there, then
reports back. That loop — think, act, observe, repeat — is the whole product.</p>

<p>The difference from a chat window is that it <b>acts on real state</b>. A chat
assistant returns text you then apply yourself. Claude Code applies it. That is
why almost everything else you will learn is about <b>constraining what it may
do</b>, rather than about getting better answers.</p>

<p>One turn looks like this:</p>
<ol>
<li>You send a prompt.</li>
<li>Claude decides on a <b>tool call</b> — read this file, run this command, edit
that function.</li>
<li>The <b>harness</b> — the Claude Code program itself, not the model — decides
whether that call is allowed. It may run it, block it, or ask you.</li>
<li>The result goes back to Claude, which decides on the next call, or stops and
answers.</li>
</ol>

<p>Hold on to step 3. The model <em>proposes</em>; the harness <em>disposes</em>.
Every permission rule, hook and sandbox setting in this course is you
programming step 3.</p>
""",
 "example": {"label": "The surfaces it runs on", "lang": "text", "code":
"""claude                    # interactive terminal session
claude -p "fix the test"   # one-shot, non-interactive (scripts, CI)

# also: VS Code and JetBrains extensions, a desktop app,
# claude.ai/code on the web, GitHub Actions, and a Slack integration."""},
 "takeaway": "Claude proposes tool calls; the harness decides whether they run. Configuration is how you program that decision.",
 "checks": [{
   "q": "You add a rule that blocks a command. Claude still tries to run it. Is that a failure?",
   "choices": [
     "Yes — the rule should stop Claude from trying",
     "No — Claude proposes tool calls and the harness blocks them; a blocked attempt is the system working",
     "Yes — it means the rule syntax is wrong",
     "Only if it happens more than once"],
   "answer": [1],
   "why": "Rules act on the harness, not on Claude's intentions. Claude may well propose a blocked call; the block is what makes the rule real. This is why enforcement lives in rules and hooks rather than in instructions you write in prose."}]
},
{
 "id": "l2", "title": "The context window",
 "objective": "Say what is loaded before you type, and why context is the scarce resource.",
 "teach": """
<p>Claude has no memory between sessions. Everything it knows about your project
arrives in the <b>context window</b> — a finite budget of tokens holding the
system prompt, your instructions, the conversation, and every file it has read.</p>

<p>Before you type a single character, a session has already loaded:</p>
<ul>
<li>the <b>system prompt</b> (~4k tokens) — core instructions you never see</li>
<li><b>auto memory</b> — notes Claude wrote itself in past sessions</li>
<li><b>environment info</b> — working directory, platform, shell, plus git branch
and status as a separate block</li>
<li><b>your CLAUDE.md files</b> and any unscoped rules</li>
<li><b>tool definitions</b>, and the <em>names</em> of MCP tools</li>
</ul>

<p>Two consequences follow, and they drive a lot of later design:</p>

<p><b>Context is spent, not free.</b> A 400-line CLAUDE.md costs its tokens on
every single turn, forever. That is the argument for moving long procedures into
skills, which load only when used.</p>

<p><b>Reading files is the main cost.</b> A search that opens forty files can
consume more window than the entire rest of your session. That is the argument
for subagents, which do the reading in a <em>separate</em> window and hand back
only the conclusion.</p>
""",
 "example": {"label": "Inspect your own session", "lang": "bash", "code":
"""/context     # visualize what is in the window right now
/compact     # summarize the history, keep working
/clear       # throw the history away and start fresh"""},
 "takeaway": "Everything Claude knows is in one finite window. Context is the budget you are always spending.",
 "checks": [{
   "q": "You finish one task and start a completely unrelated one in the same session. /clear or /compact?",
   "choices": [
     "/compact — it preserves useful history",
     "/clear — the task changed, so the old history is pure cost",
     "Neither; open a new terminal",
     "/context"],
   "answer": [1],
   "why": "/compact summarizes and continues, which is right when the same task got long. When the task itself changed, that history has no future value — it is just tokens you keep paying for. /clear is correct."},
  {
   "q": "Why does reading many files hurt more than a long prompt?",
   "choices": [
     "File contents are billed at a higher rate",
     "File contents stay in the window for the rest of the session, so their cost repeats every turn",
     "Files are never compacted",
     "It does not — they cost the same"],
   "answer": [1],
   "why": "Once read, a file's contents sit in the conversation and are re-sent with every subsequent turn. A one-off long prompt is paid once; forty files are paid over and over. This is precisely the problem subagents solve."}]
},
{
 "id": "l3", "title": "Permission prompts",
 "objective": "Predict which actions prompt you, and know what 'don't ask again' actually writes.",
 "teach": """
<p>In the default mode — called <b>Manual</b> — Claude Code starts read-only and
asks before it changes anything. The rough shape:</p>

<ul>
<li><b>Never prompts:</b> reading files, <code>Grep</code>, <code>Glob</code>,
and a built-in set of read-only shell commands like <code>ls</code>,
<code>cat</code> and <code>git status</code>.</li>
<li><b>Prompts:</b> editing or writing files, and any other shell command.</li>
</ul>

<p>There is also a <b>working directory boundary</b>. Claude Code writes only
inside the folder you started it in and below. In Manual mode it even asks
before <em>reading</em> outside that boundary.</p>

<p>When you answer a prompt with <b>“Yes, and don't ask again”</b>, that is not a
vague preference. Claude Code writes a concrete <b>allow rule</b> into
<code>.claude/settings.local.json</code> — a real file, in your project, that you
can open and edit. Understanding that file is the bridge to the next module.</p>

<p>One detail that surprises people: that file is read from the <b>repository
root</b>, even if you started Claude Code in a subdirectory. So an approval you
give in <code>src/api/</code> applies across the whole repo.</p>
""",
 "example": {"label": "What 'don't ask again' writes", "lang": "json", "code":
"""// .claude/settings.local.json  — created for you, yours alone, gitignored
{
  "permissions": {
    "allow": [
      "Bash(npm test:*)"
    ]
  }
}"""},
 "takeaway": "Manual mode is read-only by default. 'Don't ask again' writes a real allow rule to .claude/settings.local.json.",
 "checks": [{
   "q": "Which of these run WITHOUT a prompt in Manual mode?",
   "choices": ["Editing a file", "git status", "npm install", "curl https://example.com"],
   "answer": [1],
   "why": "A built-in read-only command set — ls, cat, git status, git diff, grep, find — runs without asking. Edits prompt, arbitrary commands prompt, and network commands like curl and wget are specifically NOT auto-approved."}]
},
{
 "id": "l4", "title": "CLAUDE.md — telling Claude about your project",
 "objective": "Know what belongs in CLAUDE.md, where it lives, and why it is not enforcement.",
 "teach": """
<p><code>CLAUDE.md</code> is a plain markdown file of standing instructions,
loaded into context at the start of every session. It is where you write down
what you would otherwise re-explain: build commands, conventions, project
layout, “always do X” rules.</p>

<p>It can live in several places, loaded broadest-first:</p>
<ul>
<li><b>Managed policy</b> — deployed by your organization, cannot be excluded</li>
<li><b>User</b> — <code>~/.claude/CLAUDE.md</code>, all your projects</li>
<li><b>Project</b> — <code>./CLAUDE.md</code> or <code>./.claude/CLAUDE.md</code>, committed for the team</li>
<li><b>Local</b> — <code>./CLAUDE.local.md</code>, yours, gitignored</li>
</ul>

<p>Files are <b>concatenated, not overridden</b>, ordered from the filesystem
root down to your working directory — so the instructions closest to where you
launched are read <em>last</em>.</p>

<p>Now the most important sentence in this lesson:</p>

<p class="callout"><b>CLAUDE.md is context, not enforced configuration.</b> Claude
reads it and tries to follow it. There is no guarantee, especially for vague or
conflicting instructions.</p>

<p>So “always run the linter before committing” in CLAUDE.md is a <em>hope</em>.
If it truly must happen every time, it belongs in a hook — which you will meet
in Module 3. Keep CLAUDE.md for facts, under about 200 lines, and specific:
“Use 2-space indentation” beats “format code properly”.</p>
""",
 "example": {"label": "A CLAUDE.md that earns its tokens", "lang": "markdown", "code":
"""# payments-api

## Commands
- `make test` — full suite (needs a local Redis)
- `make lint` — ruff + mypy, run before committing

## Layout
- API handlers live in `src/api/handlers/`
- Anything touching money goes through `src/ledger/` — never write to
  the balances table directly

## Conventions
- 2-space indentation, no tabs
- New endpoints need a test in `tests/api/` before review"""},
 "takeaway": "CLAUDE.md is loaded every session and is guidance, not enforcement. Facts here; procedures in skills; guarantees in hooks.",
 "checks": [{
   "q": "You put 'always run make lint before committing' in CLAUDE.md and Claude sometimes forgets. What is the structural fix?",
   "choices": [
     "Write it in capital letters",
     "Repeat it in three places",
     "Move it to a hook — CLAUDE.md is context, not enforcement",
     "Move it to settings.json"],
   "answer": [2],
   "why": "No amount of emphasis makes context into enforcement. An instruction tied to a specific moment — before every commit, after each edit — belongs in a hook, which the harness executes as code regardless of what Claude decides."},
  {
   "q": "You have CLAUDE.md at the repo root and another in src/api/. You launch Claude Code in src/api/. What happens?",
   "choices": [
     "Only src/api/CLAUDE.md loads — the nearest wins",
     "Both load, concatenated, with the root file first and src/api/ last",
     "Only the root file loads",
     "They conflict and Claude Code errors"],
   "answer": [1],
   "why": "All discovered files are concatenated rather than overriding each other, ordered from the filesystem root down to your working directory. Instructions closest to where you launched are read last."}]
}]})

M.append({
"id": "m2", "title": "Controlling what Claude can do", "blurb":
"The permission system is the densest examinable area and the one where intuition "
"is most often wrong. Take it slowly.",
"lessons": [
{
 "id": "l5", "title": "deny → ask → allow",
 "objective": "State the evaluation order and predict the outcome when rules overlap.",
 "teach": """
<p>You write permission rules in a settings file under three lists:
<code>deny</code>, <code>ask</code> and <code>allow</code>. When Claude proposes a
tool call, the harness checks them in a fixed order:</p>

<p class="rule-flow"><b>deny</b> &rarr; <b>ask</b> &rarr; <b>allow</b></p>

<p><b>The first match in that order wins, and specificity is irrelevant.</b> This
is the single most tested fact in the whole syllabus, and it is the opposite of
how CSS, firewall rules, and most things programmers know actually work.</p>

<p>Concretely: you have <code>Bash(aws *)</code> in deny and
<code>Bash(aws s3 ls)</code> in allow. Claude proposes <code>aws s3 ls</code>.
The deny list is checked first, it matches, and the call is blocked — even
though your allow rule is far more specific.</p>

<p class="callout">A deny rule <b>cannot carry allowlist exceptions</b>. If you
need “block all of X except Y”, deny rules alone cannot express it. You will
learn the technique that can in Module 3.</p>

<p>The same asymmetry holds between ask and allow: a matching ask rule prompts
you even when a more specific allow rule also matches.</p>

<p>One more distinction. A <b>bare tool name</b> in deny behaves differently from
a scoped rule:</p>
<ul>
<li><code>deny: Bash</code> — removes the tool from Claude's context entirely. It
never sees that the tool exists.</li>
<li><code>deny: Bash(rm *)</code> — the tool stays available; matching calls are
blocked when attempted.</li>
</ul>
""",
 "example": {"label": "Reading a config the way the harness does", "lang": "json", "code":
"""{
  "permissions": {
    "deny":  ["Read(./.env)", "Bash(aws *)"],
    "ask":   ["Bash(git push *)"],
    "allow": ["Bash(npm test:*)", "Bash(aws s3 ls)"]
  }
}

// aws s3 ls    -> BLOCKED. deny matched first; the allow never gets a look.
// git push     -> PROMPTS. ask matched before allow could apply.
// npm test -v  -> RUNS.    no deny, no ask, allow matched."""},
 "takeaway": "deny → ask → allow, first match wins, specificity never breaks the tie.",
 "checks": [{
   "q": "deny has Bash(aws *). allow has Bash(aws s3 ls). Claude proposes `aws s3 ls`. What happens?",
   "choices": [
     "It runs — the allow rule is more specific",
     "It is blocked — deny is evaluated first and specificity does not matter",
     "You are prompted to break the tie",
     "Claude Code reports a configuration conflict"],
   "answer": [1],
   "why": "Rules are evaluated deny, then ask, then allow, and the first match in that order determines the outcome. A broad deny blocks everything it matches, so a deny rule can never carry an allowlist exception."},
  {
   "q": "What does `deny: Bash` do that `deny: Bash(rm *)` does not?",
   "choices": [
     "Nothing — they are equivalent",
     "It removes the tool from Claude's context entirely, so Claude never sees it",
     "It applies only in bypassPermissions mode",
     "It blocks the tool for subagents only"],
   "answer": [1],
   "why": "A bare tool name in deny removes the tool from Claude's context. A scoped rule leaves the tool available and blocks only matching calls. (One exception: EndConversation cannot be removed while any other tool remains.)"}]
},
{
 "id": "l6", "title": "Bash rule syntax",
 "objective": "Write a Bash allow rule that matches what you intend and nothing more.",
 "teach": """
<p>Bash rule wildcards look like shell globs and are not. Three mechanics decide
everything.</p>

<p><b>1. A space before the trailing <code>*</code> creates a word boundary.</b></p>
<table class="tbl">
<tr><th>Rule</th><th>Matches</th><th>Does not match</th></tr>
<tr><td><code>Bash(ls *)</code></td><td><code>ls -la</code></td><td><code>lsof</code></td></tr>
<tr><td><code>Bash(ls*)</code></td><td><code>ls -la</code> and <code>lsof</code></td><td>—</td></tr>
</table>
<p>Miss that space and you have silently widened your allowlist to every command
starting with those letters. <code>Bash(ls:*)</code> is an equivalent way to write
the word-boundary form.</p>

<p><b>2. Shell operators split the command, and every part must match
independently.</b> The recognised separators are
<code>&amp;&amp;</code>, <code>||</code>, <code>;</code>, <code>|</code>,
<code>|&amp;</code>, <code>&amp;</code> and newlines. So
<code>Bash(safe-cmd *)</code> does <em>not</em> approve
<code>safe-cmd &amp;&amp; rm -rf /</code>. This is a deliberate defence, and it is
why you cannot smuggle a command past a prefix rule.</p>

<p><b>3. A fixed list of wrappers is stripped before matching.</b>
<code>timeout</code>, <code>time</code>, <code>nice</code>, <code>nohup</code>,
<code>stdbuf</code>, the builtins <code>command</code> and <code>builtin</code>,
zsh's <code>noglob</code>, and bare <code>xargs</code>. So
<code>Bash(npm test *)</code> also covers <code>timeout 30 npm test</code>.</p>

<p class="callout"><b>And here is the trap.</b> Environment runners are
<em>not</em> stripped — <code>npx</code>, <code>docker exec</code>,
<code>devbox run</code>, <code>direnv exec</code>, <code>mise exec</code>. Which
means <code>Bash(devbox run *)</code> matches <code>devbox run rm -rf .</code>.
Write one rule per inner command instead: <code>Bash(devbox run npm test)</code>.</p>

<p>Finally, some things can never be prefix-approved: the exec wrappers
<code>watch</code>, <code>setsid</code>, <code>ionice</code>, <code>flock</code>,
and <code>find</code> with <code>-exec</code> or <code>-delete</code>. They always
prompt in Manual mode.</p>
""",
 "example": {"label": "Narrow rules that hold", "lang": "json", "code":
"""{
  "permissions": {
    "allow": [
      "Bash(npm run test:*)",     // npm run test, npm run test:watch...
      "Bash(git diff *)",          // any git diff invocation
      "Bash(git log *)",
      "Bash(devbox run npm test)"  // NOT Bash(devbox run *)
    ],
    "deny": ["Bash(curl *)", "Bash(wget *)"]
  }
}"""},
 "takeaway": "The space before * is a word boundary; shell operators split the command; environment runners are not stripped.",
 "checks": [{
   "q": "Your allow rule is Bash(ls *). Which commands does it match?",
   "choices": [
     "Both `ls -la` and `lsof`",
     "`ls -la` but not `lsof`",
     "`lsof` but not `ls -la`",
     "Neither — a trailing wildcard is invalid in allow"],
   "answer": [1],
   "why": "A '*' at the end preceded by a space enforces a word boundary: the prefix must be followed by a space or end-of-string. Written without the space, Bash(ls*) matches both."},
  {
   "q": "You allow Bash(devbox run *). Why is that dangerous?",
   "choices": [
     "devbox is not a real command",
     "Environment runners are not stripped before matching, so the rule matches `devbox run rm -rf .`",
     "It only works on Linux",
     "It is not dangerous — the runner sandboxes what it runs"],
   "answer": [1],
   "why": "The wrapper-stripping list is fixed and does not include environment runners like devbox, npx, docker exec, direnv exec or mise exec. Because these execute their arguments as a command, a prefix rule covering the runner covers anything you can pass it. Write one rule per inner command."},
  {
   "q": "With Bash(safe-cmd *) allowed, Claude proposes `safe-cmd && rm -rf /tmp/x`. What happens?",
   "choices": [
     "It runs — the rule matched the start",
     "It is not auto-approved; each subcommand must match a rule independently",
     "Only the first half runs",
     "Claude Code rejects the rule at startup"],
   "answer": [1],
   "why": "Claude Code is aware of shell operators. It splits on &&, ||, ;, |, |&, & and newlines, and requires every subcommand to match independently."}]
},
{
 "id": "l7", "title": "File rules — the silent no-op",
 "objective": "Write a file permission rule that is actually consulted.",
 "teach": """
<p>You want to stop Claude reading your <code>.env</code>. The obvious rule is
wrong in a way that produces no error at the moment you need it.</p>

<p class="callout"><b>File permission checks consult only
<code>Read(path)</code> and <code>Edit(path)</code> rules.</b> A path rule
written for <code>Write</code>, <code>NotebookEdit</code>, <code>Glob</code> or
the legacy <code>MultiEdit</code> is accepted, stored, and <b>never
consulted</b>.</p>

<p>Claude Code warns at startup — but the file was still readable the whole time
you thought it was protected.</p>

<table class="tbl">
<tr><th>Intent</th><th>Wrong</th><th>Right</th></tr>
<tr><td>Block reads</td><td><code>Glob(./secrets/**)</code></td><td><code>Read(./secrets/**)</code></td></tr>
<tr><td>Block writes</td><td><code>Write(./secrets/**)</code></td><td><code>Edit(./secrets/**)</code></td></tr>
</table>

<p><code>Edit(path)</code> governs <em>all</em> the built-in tools that write
files, <code>Write</code> and <code>NotebookEdit</code> included. There is one
rule form for reading and one for writing; that is the whole vocabulary.</p>

<p><b>Path anchors matter too.</b> <code>./x</code> is relative to the settings
file. <code>//x</code> is absolute from the filesystem root — so
<code>Read(//Users/alice/secrets/**)</code> means the real
<code>/Users/alice/secrets</code>. A single leading slash anchors at the rule's
source instead, which is rarely what you meant.</p>

<p>One more: <b>output redirection is checked as a file write</b>. A rule
allowing <code>git commit</code> allows the command, not the target of a
<code>&gt;</code> in it. <code>/dev/null</code> is exempt; a target containing
<code>~</code> or a glob always prompts.</p>
""",
 "example": {"label": "Excluding secrets, correctly", "lang": "json", "code":
"""{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Edit(./secrets/**)",
      "Read(//Users/me/.ssh/**)"
    ]
  }
}"""},
 "takeaway": "Only Read(path) and Edit(path) are consulted. Write/Glob/NotebookEdit path rules are accepted and ignored.",
 "checks": [{
   "q": "You want to stop Claude reading .env files. Which rule works?",
   "choices": ["deny: Read(./.env)", "deny: Write(./.env)", "deny: Glob(./.env)", "deny: NotebookEdit(./.env)"],
   "answer": [0],
   "why": "File permission checks consult only Edit(path) and Read(path). The other three are accepted, warned about at startup, and never consulted — a rule that looks like protection and is not."}]
},
{
 "id": "l8", "title": "Permission modes",
 "objective": "Pick the right mode for a task and know what each stops auto-approving.",
 "teach": """
<p>A mode sets the baseline for everything your rules do not explicitly cover.
Switch with <b>Shift+Tab</b> in the CLI.</p>

<table class="tbl">
<tr><th>Mode</th><th>What runs without asking</th></tr>
<tr><td><code>default</code> (Manual)</td><td>Read-only commands only. Everything else prompts.</td></tr>
<tr><td><code>plan</code></td><td>Reads and read-only commands. Claude explores and proposes, never edits your source.</td></tr>
<tr><td><code>acceptEdits</code></td><td>File edits, plus <code>mkdir</code>, <code>touch</code>, <code>mv</code>, <code>cp</code>, <code>sed</code> in the working directory.</td></tr>
<tr><td><code>auto</code></td><td>A classifier model reviews actions instead of you.</td></tr>
<tr><td><code>dontAsk</code></td><td>Nothing new — anything not pre-approved is <b>denied</b>, not prompted.</td></tr>
<tr><td><code>bypassPermissions</code></td><td>Almost everything, including writes to <code>.git</code> and <code>.claude</code>.</td></tr>
</table>

<p>Two are worth extra attention.</p>

<p><b><code>dontAsk</code> is the CI mode.</b> It converts every prompt into a
denial. That makes your tool surface fixed and explicit, which is exactly what
you want when no human is watching.</p>

<p><b><code>plan</code> is stronger than it looks.</b> File edits are never
auto-approved in plan mode, <em>even when an allow rule matches</em>. That is a
deliberate exception to normal rule evaluation.</p>

<p>Regardless of mode, a short list is <b>never</b> auto-approved: anything
matched by an explicit ask rule, tools that require user interaction like
<code>AskUserQuestion</code>, and <code>rm</code>/<code>rmdir</code> targeting a
critical path. There are also <b>protected paths</b> — <code>.git</code>,
<code>.vscode</code>, <code>.idea</code>, <code>.husky</code> and friends — whose
writes no allow rule can pre-approve; only <code>bypassPermissions</code> lets
them through.</p>
""",
 "example": {"label": "Locking the modes down org-wide", "lang": "json", "code":
"""// managed-settings.json — deployed by an administrator
{
  "permissions": {
    "disableBypassPermissionsMode": "disable",
    "disableAutoMode": "disable",
    "defaultMode": "default"
  }
}"""},
 "takeaway": "dontAsk denies instead of prompting. plan never auto-approves edits, even with a matching allow rule.",
 "checks": [{
   "q": "Which mode auto-DENIES anything not already pre-approved?",
   "choices": ["plan", "acceptEdits", "dontAsk", "bypassPermissions"],
   "answer": [2],
   "why": "dontAsk converts any permission prompt into a denial. Tools pre-approved by allow rules still run. It is the right posture for a headless agent where nobody can answer a prompt."},
  {
   "q": "In plan mode, an allow rule matches a file edit Claude wants to make. Does it run?",
   "choices": [
     "Yes — allow rules always win",
     "No — plan mode never auto-approves file edits, even with a matching allow rule",
     "Only if you are also in acceptEdits",
     "Only for files inside the working directory"],
   "answer": [1],
   "why": "Plan mode routes file edits and shell writes to a prompt regardless of allow rules, so write operations cannot be auto-approved while planning. It is a deliberate exception to normal evaluation."}]
},
{
 "id": "l9", "title": "Settings files, precedence and trust",
 "objective": "Predict which file wins, and explain why a cloned repo cannot silently widen your access.",
 "teach": """
<p>Five sources hold settings. Highest precedence first:</p>
<ol>
<li><b>Managed</b> — your organization. Nothing overrides it, not even a CLI flag.</li>
<li><b>Command line</b> — <code>claude --settings</code></li>
<li><b>Project local</b> — <code>.claude/settings.local.json</code> (yours, gitignored)</li>
<li><b>Shared project</b> — <code>.claude/settings.json</code> (committed)</li>
<li><b>User</b> — <code>~/.claude/settings.json</code></li>
</ol>

<p><b>Scalars override; lists merge.</b> Set <code>permissions.allow</code> in
three files and you get the union of all three. This is why “I removed that
allow rule and it still applies” almost always means another scope still
declares it.</p>

<p>Now the security question. A repository can ship a
<code>.claude/settings.json</code>. Cloning it must not silently grant the author
access to your machine. So Claude Code splits the file by direction:</p>

<table class="tbl">
<tr><th>Rules</th><th>When they apply</th></tr>
<tr><td><code>deny</code> and <code>ask</code></td><td><b>Immediately</b></td></tr>
<tr><td><code>allow</code>, <code>additionalDirectories</code>, most <code>env</code></td><td><b>Only after you trust the folder</b></td></tr>
</table>

<p class="callout"><b>Restrictions bind at once; grants wait for a human.</b>
Learn this asymmetry — it answers a whole family of questions, and it is the
principle behind several later lessons.</p>

<p>Last thing: settings files are <b>strict JSON</b>. A <code>//</code> comment
or a trailing comma is a syntax error that surfaces as a Settings Error at your
next start.</p>
""",
 "example": {"label": "Which file for which job", "lang": "text", "code":
"""~/.claude/settings.json          your preferences, every project
.claude/settings.json            the team's rules — commit this
.claude/settings.local.json      your approvals here — gitignored
managed-settings.json            org policy — you cannot override it"""},
 "takeaway": "Managed > CLI > local > project > user. Lists merge. deny/ask apply at once; allow waits for trust.",
 "checks": [{
   "q": "A teammate clones your repo with a committed .claude/settings.json. Which rules take effect BEFORE they trust the folder?",
   "choices": ["deny rules", "ask rules", "allow rules", "additionalDirectories"],
   "answer": [0, 1],
   "why": "Restrictions bind immediately; grants wait. deny and ask apply at once, while permissions.allow, additionalDirectories, extraKnownMarketplaces and most env values wait for the trust step. Otherwise cloning a repo would silently widen your access."},
  {
   "q": "You set permissions.allow in both your user settings and the project's settings.json. What happens?",
   "choices": [
     "The higher-precedence file's list replaces the other",
     "The lists merge — entries from both apply",
     "Claude Code reports a conflict",
     "Only the user file is read"],
   "answer": [1],
   "why": "List keys such as permissions.allow merge across scopes rather than overriding, so each file can contribute entries. Scalar keys follow normal precedence."}]
}]})

pathlib.Path("part1.json").write_text(json.dumps(M, indent=1))
print(f"modules: {len(M)}  lessons: {sum(len(m['lessons']) for m in M)}  "
      f"checks: {sum(len(l['checks']) for m in M for l in m['lessons'])}")
