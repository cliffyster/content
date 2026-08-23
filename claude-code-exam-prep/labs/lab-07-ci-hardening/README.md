# Lab 07 — Harden a headless run

**Goal:** turn a naive CI invocation into one you would be willing to run on a
pull request from a stranger.

## Start here

```bash
claude -p "Review the diff and fix any lint errors" --allowedTools "Bash,Read,Edit"
```

This looks reasonable and is not. Work out what is wrong with it before reading
on — there are at least four problems.

## Fix it

Address each of these:

1. **Repository configuration executes.** Without `--bare`, this run executes
   the hooks in the repo's `.claude/settings.json` and connects the servers in
   its `.mcp.json`, in a folder nobody trusted, with no prompt. On a PR from a
   fork, those files are attacker-controlled.
2. **Credentials.** Once you add `--bare`, OAuth and the keychain are no longer
   read. What do you set instead?
3. **Permission posture.** `-p` starts in Manual mode on every plan, and
   `--allowedTools "Bash"` is a blank cheque. Pick a mode and narrow the tools.
4. **Blast radius.** What stops a runaway loop from spending your budget?
5. **Failure detection.** A plugin or MCP server that fails to load does *not*
   fail the run. How do you notice?

## Check yourself

Your final command should survive this test: *if the repository's `.claude/` and
`.mcp.json` were written by an attacker, what could they do?*

## Questions

1. Which safeguard is disabled specifically because `-p` cannot show a prompt?
2. Why does piping the diff in (`git diff main | claude -p …`) reduce the
   permissions the run needs?
3. What exit code does SIGTERM produce, and what happens to the in-flight turn?
