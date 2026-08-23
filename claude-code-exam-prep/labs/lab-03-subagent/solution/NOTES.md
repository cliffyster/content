# Lab 03 — answers

**1. It cannot ask.**
`AskUserQuestion` is removed from every subagent, along with `EndConversation`,
`EnterPlanMode`/`ExitPlanMode`, `ScheduleWakeup`, `Workflow`, and `Agent` at the
depth limit. So the design rule is: a subagent's prompt must resolve its own
ambiguity, or it must report both readings and let the main session decide. The
solution above does the latter — "which is right, and why" instead of stopping
to ask.

**2. It starts from a fresh context window.**
A non-fork subagent receives its own system prompt, the task message Claude
writes for it, `CLAUDE.md` (except Explore and Plan), a git status snapshot,
skills named in its `skills:` field, and the sibling roster. It does **not**
receive the main conversation history, output style, auto memory, or skills
invoked earlier in the main session.

What would give it that context: a **fork**, which inherits the full history,
system prompt, tools and model, and shares the parent's prompt cache. The
trade is that a fork is not context-isolated — which was the reason to use a
subagent in the first place.

**3. `model: haiku` trades capability for speed and cost.**
Right when the work is mechanical and voluminous — grepping, collating,
reformatting — and the judgement lives in your prompt rather than in the model.
Wrong here: deciding whether two differently-worded claims actually contradict
each other is exactly the judgement you would be economising on. `inherit` is
the default for a reason.
