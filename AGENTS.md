<!-- #ai-assisted with OCA/OpenAI Model with human supervision -->

# Agent Operating Contract

Maturity: standard
Runtime: desktop game
Language profile: Go

`AGENTS.md` is the source of truth for agent instructions. CLAUDE.md must be a symlink to `AGENTS.md` so Claude Code and Codex CLI always receive identical guidance.

Detailed guidance lives in:

- `docs/agent/clean-code-guide.md`
- `docs/agent/review-guide.md`
- `docs/agent/subagents-guide.md`
- `docs/agent/testing-guide.md`
- `docs/agent/go-style-guide.md`

## Project Context

This is a Pac-Man-style desktop game built with Go and Ebitengine. Before editing, inspect nearby code and tests and read `README.md`, `Makefile`, `MEMORY.md`, and `CONTEXT.md` when relevant.

### Common Commands

```bash
make run                # Build and run the game
make build              # Build bin/pacman
make test               # Run all unit tests
make coverage           # Generate a text coverage report
make coverage-html      # Generate an HTML coverage report
make format             # Format Go code; make fmt is an alias
make lint               # Run go vet and golangci-lint
make validate           # Run the full local gate
make visual-smoke       # Launch under Xvfb and capture the initial screen
make release            # Build an artifact for the current native host
make clean              # Remove generated artifacts
```

Targeted test examples:

```bash
go test ./internal/game
go test ./internal/game -run TestFrightenedModeTimeout
go test -v ./internal/game
```

### Architecture And Runtime Invariants

- The Ebitengine loop uses `Update` for 60 UPS state changes, `Draw` for offscreen rendering, and `Layout` for screen dimensions.
- Movement is grid-based with queued turns. Tiles are 16x16 pixels and cell centers are `(x*16+8, y*16+8)`.
- Movement uses a fixed 4-pixel alignment threshold and speeds of 120 px/s for the player and 105 px/s for ghosts.
- All timing uses `tickCounter`. Frightened mode lasts exactly 120 ticks (2 seconds), and its timeout check runs before game logic.
- Frightened ghost scoring is 200, 400, 800, then 1600 points; a new power pellet resets the combo.
- Easter eggs trigger for Rekha/Roy names, R/Y keys, or roughly 1/6000 random updates and display in pink for 3 seconds.
- Audio is lazy-loaded and disabled by default. `PACMAN_DISABLE_AUDIO=1` overrides `PACMAN_ENABLE_AUDIO=1`.
- High scores use atomic JSON persistence in the user config directory. Every named player's improved score must be saved immediately, even when it is below the global high score.
- Eating the final regular or power pellet enters `levelComplete` before ghost collision handling, freezes gameplay, and preserves the winning score.
- `enteringName`, `showingLeaderboard`, `levelComplete`, and `paused` block active-play movement input.

## Operating Principles

- Prefer readability, explicit behavior, small focused changes, and existing conventions.
- Preserve unrelated user changes and keep diffs reviewable.
- Treat tests and documentation as part of the change.
- Keep boundaries clear between game logic, input, rendering, audio, persistence, and UI.
- Handle errors explicitly; never swallow failures silently.
- Avoid speculative abstractions and generic dumping-ground modules.

## Hard Requirements

- Keep `AGENTS.md` under 200 lines and `CLAUDE.md` symlinked to it.
- Run relevant tests for code changes.
- Run `make validate` before handoff when code, packaging, config, Makefile, validation, or workflow behavior changes.
- Run `make score` for docs-only governance changes.
- Keep every enabled scorecard dimension at 10/10 unless the handoff records a user-approved exception.
- Generated source, scripts, tests, automation, and substantial docs must include `#ai-assisted with OCA/OpenAI Model with human supervision` in the language-appropriate comment form.
- Use subagents when work is safely parallelizable, specialized, or benefits from independent review; keep tightly coupled or duplicate work local.

## Go And Test Standards

- Use Go 1.22+, Go modules, `gofmt`, `go vet ./...`, golangci-lint 2.12.2, and `go test ./...`.
- Keep package APIs narrow, accept interfaces near consumers, and wrap errors with useful context.
- Prefer table-driven tests when several cases share setup and assertions.
- Use `t.Setenv("PACMAN_CONFIG_DIR", t.TempDir())` for isolated high-score tests.
- Use `t.Setenv("PACMAN_DISABLE_AUDIO", "1")` to avoid audio context conflicts.
- Test movement alignment with offsets beyond the 4-pixel threshold.
- Add regression tests for bug fixes and test observable behavior rather than implementation details.
- Level-completion tests must cover both pellet types, a non-final pellet, frozen post-win updates, same-tick ghost collision precedence, and a winner below the global high score.
- Run `make visual-smoke` for rendering changes; GitHub validation mirrors the local gate and captures the initial screen.

## Modes Of Operation

- Inspect: reproduce, trace, explain root cause, and propose the smallest fix.
- Build: make focused changes, update tests and docs, and validate.
- Review: lead with bugs, risks, regressions, missing tests, stale docs, and security issues.

## Subagents

Follow `docs/agent/subagents-guide.md`. Use subagents where applicable, including during skill-driven work.

- Use a subagent when work can be done independently and its result can be summarized compactly.
- Do not delegate work that needs constant shared context, sequential reasoning, or produces mostly overlapping work.
- Give delegated tasks clear ownership, expected output, constraints, and validation expectations.

The primary agent remains responsible for integration, user-change preservation, and final validation.

## Documentation Rules

Documentation drift is a bug. Update affected docs whenever behavior, commands, configuration, dependencies, setup, validation, packaging, or user workflows change. Check `README.md`, this file, `MEMORY.md`, `CONTEXT.md`, workflow docs, `docs/agent/`, `docs/adr/`, and Makefile help text as applicable.

## Security And Secrets

Never write secrets, tokens, credentials, private keys, wallet files, bearer headers, auth files, customer data, huge logs, or raw sensitive material into repository files, examples, tests, generated artifacts, or prompts.

## Definition Of Done

- Behavior works and remains readable.
- Relevant tests pass.
- `make validate` passes or exact blockers are documented.
- Scorecard dimensions meet the required threshold.
- Documentation and workflows match the implementation.
- No secrets or local-only artifacts are included.
