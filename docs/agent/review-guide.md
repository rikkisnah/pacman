<!-- #ai-assisted with OCA/OpenAI Model with human supervision -->

# Review Guide

Lead with findings. Prioritize issues in this order:

1. Correctness and behavioral regressions.
2. Security, secrets, and unsafe auth handling.
3. Runtime behavior, reliability, and failure modes.
4. Public API compatibility.
5. Missing behavior tests.
6. Documentation drift.
7. Tooling, packaging, and validation drift.
8. Clean-code maintainability issues.
9. Missed subagent use for parallelizable, specialized, or independently reviewable work.

## Clean-Code Review

For every source, script, test, or automation change, review against `docs/agent/clean-code-guide.md`.

Reject or revise changes with:

- vague names
- long functions
- hidden side effects
- duplicated business logic
- swallowed errors
- unnecessary abstractions
- generic utility dumping grounds
- unclear module boundaries
- missing behavior tests
- tests that only assert implementation details
- new dependencies without justification
- public API changes without explicit approval
- missed subagent use where independent review, test investigation, or disjoint write scopes apply

## Documentation Drift

Documentation drift is a bug. A change that alters behavior, commands, configuration, dependencies, setup, validation, deployment, or user workflows is incomplete unless affected docs are updated in the same change set.

## Subagent Review

Check `docs/agent/subagents-guide.md` for Claude and Codex delegation expectations. Reviews should flag missed subagent use when work could have been safely split for independent exploration, focused review, test investigation, or implementation with disjoint write scopes.

## Output Format

For reviews, list findings first with file and line references when possible. Then include open questions, test gaps, and a short summary only after findings.
