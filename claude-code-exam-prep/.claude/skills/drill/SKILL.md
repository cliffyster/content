---
name: drill
description: Run a spaced-repetition drill session from the exam question bank. Use when the learner asks to be quizzed, tested, or drilled on a topic.
argument-hint: "[domain]"
disable-model-invocation: true
allowed-tools: Bash(python3 -m quiz *)
---

Run a drill session for the learner.

1. If `$ARGUMENTS` names a domain, run:
   `python3 -m quiz drill --domain $ARGUMENTS --limit 10`
   Otherwise run `python3 -m quiz drill --limit 10` to review whatever is due.
2. The tool is interactive and will handle the questions itself. Do not
   paraphrase the questions or reveal answers ahead of it.
3. When the session ends, run `python3 -m quiz stats` and give the learner
   **one** concrete next step based on their weakest domain — name the note
   file to read, not a generic "review the material".

If nothing is due, say so and offer `--all` rather than silently drilling
everything: the schedule is the point of the tool.
