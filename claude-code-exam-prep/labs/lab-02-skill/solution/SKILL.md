---
name: note
description: Append a timestamped note to the study journal.
argument-hint: "[what you learned]"
disable-model-invocation: true
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/append.sh *)
---

Append the learner's note to the study journal by running exactly:

```
${CLAUDE_SKILL_DIR}/scripts/append.sh "$ARGUMENTS"
```

Then confirm in one line what was recorded. Do not editorialise, do not add
your own commentary to the journal, and do not read the journal back unless
the learner asks — this skill is write-only by design.
