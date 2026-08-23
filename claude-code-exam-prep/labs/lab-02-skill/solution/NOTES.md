# Lab 02 — answers

**1. No `$ARGUMENTS` in the body.**
Claude Code appends `ARGUMENTS: <your input>` to the end of the skill content,
so nothing is lost — Claude still sees what you typed, just without your chosen
placement.

**2. `$0` is the first argument.**
`$N` is shorthand for `$ARGUMENTS[N]` and the indexing is **0-based**. So
`/migrate SearchBar React Vue` gives `$0`=SearchBar, `$1`=React, `$2`=Vue. Bare
`$ARGUMENTS` is the whole string as typed.

**3. Because the skill's content never leaves.**
The rendered `SKILL.md` enters the conversation as a single message and stays
for the rest of the session, and Claude Code does not re-read the file on later
turns. A one-time step written as "first, do X" reads as a standing instruction
forever after. Write standing instructions instead — that is why the solution
says "do not read the journal back unless asked" rather than "read the journal
once at the start".

**Why the narrow grant matters.**
`allowed-tools: Bash(*)` would have worked and is a much worse habit. Skill
grants are not gated by workspace trust: a project skill's `allowed-tools`
applies even in a `-p` run in a folder you never trusted. Scoping the rule to
one script is what keeps that safe.
