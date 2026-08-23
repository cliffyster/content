# Lab 06 — Write a sandbox policy

**Goal:** configure the Bash sandbox so Claude can run your build and test
suite autonomously, while your SSH keys, cloud credentials and `.env` files stay
unreachable — enforced by the OS, not by the model's cooperation.

> Requires macOS, Linux or WSL2. Native Windows and WSL1 are unsupported.

## Build it

Run `/sandbox` to see the panel and whether any Linux dependencies are missing.
Then write a `sandbox` block in `.claude/settings.json`:

1. **Filesystem.** Deny reads of your home directory, then re-open only what the
   build needs. Remember the interaction rule: a narrow allow re-opens a denied
   region, and a deny holds inside a wider allow.
2. **Credentials.** Use `sandbox.credentials` to deny specific files
   (`~/.ssh`, `~/.aws/credentials`) and unset specific environment variables
   (`GITHUB_TOKEN`, `NPM_TOKEN`) before each sandboxed command runs.
3. **Network.** Allow only the hosts your package manager needs.
4. **Auto-allow.** Turn it on, then reason about what it just changed.

## Check yourself

Ask Claude to run each of these and observe which are blocked:

```bash
cat ~/.ssh/id_rsa            # should be denied by the filesystem layer
echo $GITHUB_TOKEN           # should be empty inside the sandbox
curl https://example.com     # should be denied by the network layer
npm test                     # should run
```

Then deliberately trigger the escape hatch: ask for something that needs a host
you did not allow, and watch whether Claude retries with
`dangerouslyDisableSandbox`.

## Questions

1. With auto-allow on and your permission mode set to Manual, a Bash command
   writes a file inside the working directory. Do you get a prompt? Why?
2. Your teammate adds `Bash(git push *)` as an **ask** rule. Does it still fire
   for sandboxed commands? What about a bare `Bash` ask rule?
3. You allow `github.com` in `network.allowedDomains`. What have you actually
   guaranteed — and what have you not?
4. Where does the `Read` tool fit into this? Is it sandboxed?
