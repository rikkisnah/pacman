<!-- #ai-assisted with OCA/OpenAI Model with human supervision -->

# Clean Code Guide

## Core Principle

Agentic code should be easy for both humans and future agents to understand, modify, test, and verify.

Simple rule: agentic clean code should be easy to read, easy to test, easy to change, and hard to misuse.

## Meaningful Names

Use names that reveal intent and domain meaning. Avoid public names such as `data`, `info`, `temp`, `tmp`, `result`, `manager`, `helper`, `misc`, `stuff`, `thing`, `common`, `util`, or `utils` unless the scope is tiny and conventional.

## Small Focused Functions

Keep functions focused on one responsibility. Split code when a function mixes policy, parsing, validation, I/O, transformation, and presentation.

## Intent Vs Implementation

High-level code should read like the workflow it implements. Hide mechanical details behind clearly named functions only when doing so improves readability.

## Avoid Clever Code

Prefer straightforward code over clever expressions, implicit behavior, or dense abstractions.

## Useful Comments Only

Use comments to explain why, constraints, invariants, or surprising trade-offs. Do not narrate what the next line already says.

## Explicit Side Effects

Names and structure should make writes, network calls, database updates, global mutation, and event emission obvious.

## Pure Functions

Prefer pure functions for business rules and transformations. Keep I/O at boundaries.

## Clear Boundaries

Keep business logic, I/O, APIs, persistence, validation, logging, presentation, and orchestration separated.

## Tests As Executable Documentation

Tests should explain behavior, edge cases, invalid input, dependency failures, permissions, and regressions.

## Refactor Continuously

When code becomes hard to name, hard to test, or hard to explain, refactor before adding more behavior.

## Avoid Duplication

Remove duplicated business rules by extracting named concepts. Do not extract accidental duplication into vague helpers.

## Clear Error Handling

Handle errors explicitly. Do not swallow exceptions or ignore errors silently.

## Visible Dependencies

Pass dependencies in where practical. Avoid hidden global mutable clients, configuration, and singletons.

## Consistent Formatting

Use the project formatter, linter, import sorter, and file organization conventions.

## Simple Data Structures

Prefer simple structures until a richer abstraction removes real complexity.

## Protected Invariants

Use validation, types, tests, assertions, schemas, constraints, or constructors to protect important invariants.

## Cohesive Modules

Keep modules about one concept. Avoid dumping unrelated public helpers into `utils`, `helpers`, `common`, or `misc`.

## Design For Change

Design for likely change. Do not invent speculative architecture for hypothetical needs.

## Types, Schemas, And Contracts

Use types, interfaces, schemas, or contracts where the language supports them.

## Agent-Friendly Code Instructions

Agents should preserve nearby project conventions, keep changes scoped, explain assumptions, and avoid unrelated rewrites.

## Small Diffs

Keep diffs small enough to review. Split unrelated changes.

## Required Explanations

For non-trivial changes, explain what changed, why, impact, tests, risks, and files touched.

## Clean Agentic Coding Loop

Understand -> Plan -> Implement -> Test -> Refactor -> Review.

## Do Not Let Agents Invent Architecture

New abstractions need evidence: repeated patterns, real complexity, stable boundaries, or a known project convention.

## Clean-Code Smells

- Long functions.
- Vague names.
- Hidden side effects.
- Duplicated business rules.
- Too many parameters.
- Large classes.
- Generic utility dumping grounds.
- Commented-out code.
- Swallowed errors.
- Dead code.
- Unnecessary abstractions.
- Tests that only verify implementation details.

## Clean-Code Checklist

- [ ] Names reveal intent.
- [ ] Functions are small and focused.
- [ ] Code reads top-down like a story.
- [ ] No hidden side effects.
- [ ] Business rules are explicit.
- [ ] Error handling is clear.
- [ ] Duplication is removed.
- [ ] Tests cover behavior and edge cases.
- [ ] Types or contracts are clear.
- [ ] Formatting and linting pass.
- [ ] No unnecessary abstractions.
- [ ] No unexplained dependencies.
- [ ] The change is small enough to review.
- [ ] The agent explained assumptions and risks.
- [ ] The code follows nearby project conventions.

## Standard Prompt For Coding Agents

```text
Apply Clean Code principles to this change.

Constraints:
- Keep the diff small.
- Follow existing project conventions.
- Use clear, intention-revealing names.
- Keep functions small and single-purpose.
- Do not introduce new dependencies unless necessary.
- Avoid clever code.
- Make side effects explicit.
- Add or update tests for behavior changes.
- Preserve existing public APIs unless explicitly approved.
- Explain assumptions, tradeoffs, and risks before finalizing.

Before finalizing, review your own diff for naming, function size, duplication, hidden side effects, error handling, tests, unnecessary abstractions, and project convention drift.
```
