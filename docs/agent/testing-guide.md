<!-- #ai-assisted with OCA/OpenAI Model with human supervision -->

# Testing Guide

Tests are executable documentation.

## Required Guidance

- Every behavior change needs tests unless purely cosmetic.
- Prefer testing public behavior over private implementation details.
- Cover happy path, edge cases, invalid input, permissions, dependency failures, and regressions.
- Avoid live cloud/backend calls in the normal offline test suite.
- Use targeted tests during development and full validation before handoff.
- Do not weaken tests just to make a change pass.
- Add regression tests for bugs.

## Commands

```bash
make test
make test-<name>
make lint
make score
make validate
make visual-smoke
```

## Test Design

Good tests describe the behavior users or callers rely on. Avoid tests that only mirror private implementation details or make refactoring expensive without protecting behavior.

Movement tests must cover approaches beyond the 4-pixel alignment threshold, vertical turns in both directions, and blocked turns. Level-completion tests must exercise the final regular pellet, final power pellet, non-final pellets, frozen post-win updates, score persistence below an existing global high score, and a same-tick ghost collision. Rendering changes require both focused draw tests and visual inspection of the Xvfb smoke screenshot.
