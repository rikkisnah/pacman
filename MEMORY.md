<!-- #ai-assisted with OCA/OpenAI Model with human supervision -->

# Project Memory

Durable, non-secret project context for future agents and maintainers.

`MEMORY.md` is durable context, not the source of truth. `AGENTS.md`, `README.md`, Makefile targets, workflow docs, and code remain authoritative.

## Project Context

- Project: `pacman`
- Runtime type: `desktop-game`
- Language profile: `go`
- Maturity: `standard`

## Stable Facts

- This repository uses `AGENTS.md` as the authoritative agent contract.
- `CLAUDE.md` must remain a symlink to `AGENTS.md`.
- `make validate` is the full local validation gate.
- `scripts/score_architecture.py` is the local governance scorecard.
- The application entry point is `cmd/pacman`; game code is under `internal/`.
- Ebitengine drives the game at 60 updates per second, and gameplay timers use ticks.
- Frightened mode lasts 120 ticks and resets the ghost-eating combo when it expires.
- Audio is disabled by default and high scores are persisted as JSON in the user config directory.
- Go 1.22 is the minimum supported toolchain.
- Movement uses 120/105 px/s player/ghost speeds and a fixed 4-pixel alignment threshold.
- Eating the final regular or power pellet enters a terminal level-complete state before ghost collision handling.
- `make visual-smoke` launches the game under Xvfb and captures `tmp/pacman-smoke.png`.
- GitHub runs validation under Xvfb on Linux and produces release artifacts on native Linux, Intel macOS, and Windows runners.

## Decisions

- Use local-first validation through Makefile targets.
- Treat documentation drift as incomplete work.
- Require OCA/OpenAI AI-assistance disclosure headers for generated artifacts.
- Persist a newly achieved high score immediately rather than waiting for process exit.
- Persist every named player's improved score, not only scores that beat the global leader.
- Keep level completion terminal until explicit multi-level progression is implemented; freeze simulation and let Q exit from the win screen.
- Isolate high-score tests with `PACMAN_CONFIG_DIR` and disable audio in tests that create audio contexts.
- Pin golangci-lint to 2.12.2 and keep local validation aligned with GitHub validation.
- Build local release artifacts only on the matching native host; use GitHub for the three-platform matrix.

## Assumptions

- Project-specific runtime behavior should be documented in `README.md` and workflow docs.
- Runtime-contract scorecard checks are deterministic static checks; the Xvfb smoke target provides executable launch evidence.

## Constraints

- Do not commit secrets or local-only environment files.
- Keep generated governance files consistent with `AGENTS.md`.

## Known Issues Or Follow-Ups

- Implement chase/scatter ghost AI, fruits, and level progression.

## Proposals

Use this section for non-authoritative proposed updates. Move accepted rules into `AGENTS.md`, docs, Makefile, or code.

## Do Not Store Here

Do not store credentials, tokens, wallet files, private keys, customer data, bearer headers, auth files, private URLs with credentials, huge logs, or temporary scratch notes in `MEMORY.md`.
