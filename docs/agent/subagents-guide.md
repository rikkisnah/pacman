<!-- #ai-assisted with OCA/OpenAI Model with human supervision -->

# Subagents Guide

Use subagents where applicable. Applicable work is parallelizable, specialized, or benefits from independent review.

Use a subagent when the task can be done independently and its result can be summarized compactly.

Do not use a subagent when the task needs constant shared context, sequential reasoning, or produces mostly overlapping work.

## Claude

Use available Claude Task, subagent, or delegation capabilities when a task can be split safely.

## Codex

Use available Codex `spawn_agent` or delegation capabilities when a task can be split safely.

## Required Uses

- Independent exploration of separate code areas.
- Focused review of security, correctness, tests, documentation drift, or clean-code risk.
- Test investigation that can run while implementation continues.
- Implementation with disjoint write scopes and clear file ownership.
- Research or tool checks that do not block the next local step.

## Local Work

Keep work local when it is tiny, urgent blocking work, tightly coupled, likely to duplicate active local effort, requires constant shared context, or depends on sequential reasoning.

## Delegation Contract

Every delegated task must include clear ownership, expected output, constraints, validation expectations, and a reminder not to revert unrelated user or agent changes.
