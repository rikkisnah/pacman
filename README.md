<!-- #ai-assisted with OCA/OpenAI Model with human supervision -->

# Pac-Man (Go + Ebitengine)

A cross-platform Pac-Man-style desktop game written in Go with Ebitengine. It includes smooth grid movement, four ghosts, power-pellet combos, terminal level completion, persistent multi-player high scores, optional audio, and a scalable classic maze.

## Quick Start

Prerequisites:

- Go 1.22 or newer
- Make
- Platform libraries required by Ebitengine
- golangci-lint 2.12.2 for `make lint` and `make validate`

```bash
make setup
make validate
make run
```

Audio is disabled by default. Enable it for one run with:

```bash
PACMAN_ENABLE_AUDIO=1 make run
```

`PACMAN_DISABLE_AUDIO=1` always takes precedence.

## Controls

| Key | Action |
| --- | --- |
| Arrow keys | Move Pac-Man |
| Space | Pause or resume |
| F | Toggle fullscreen |
| S | Show or hide the leaderboard |
| Q | Show the leaderboard, then quit; exit immediately after level completion |
| R | Show the Rekha easter egg |
| Y | Show the Roy easter egg |

## Gameplay

- Regular pellets score 10 points and power pellets score 50.
- Power pellets activate frightened mode for exactly 120 ticks (2 seconds at 60 UPS).
- Consecutive frightened ghosts score 200, 400, 800, and 1600 points.
- Eating the final regular or power pellet immediately ends gameplay and shows the level-complete screen. A final-pellet win takes precedence over a ghost collision on the same update.
- The checked-in constants currently move the player at 120 px/s and ghosts at 105 px/s.
- High scores are stored as JSON in the operating system's user config directory.
- Set `PACMAN_CONFIG_DIR` to override high-score storage, especially in tests.

The game accepts a player name at startup and immediately persists each player's improved score, even when it does not beat the global leader. The leaderboard shows the top ten players and supports legacy high-score import.

## Audio And Assets

Place optional WAV files under `assets/sounds/`:

- `pellet.wav`
- `power.wav`
- `ghost.wav`
- `death.wav`

When a file is absent, the audio manager can synthesize a fallback beep. Art and sound contributions must be original or carry a compatible license.

## Development

```bash
make format          # Format Go source
make lint            # Run go vet and golangci-lint
make test            # Run all tests
make test-NAME       # Run tests matching NAME
make coverage        # Print coverage details
make coverage-html   # Write coverage.html
make score           # Print the architecture scorecard
make validate        # Run the complete local gate
make visual-smoke    # Launch under Xvfb and capture tmp/pacman-smoke.png
```

Target one package or test directly when iterating:

```bash
go test ./internal/game
go test ./internal/game -run TestFrightenedModeTimeout
go test -v ./internal/game
```

`make release` builds only for the current native amd64 host. Platform-specific local targets fail early when invoked from the wrong operating system:

```bash
make release
make build-linux
make build-darwin
make build-windows
```

The native release workflow builds Linux, Intel macOS, and Windows artifacts on their corresponding GitHub runners for `v*` tags or manual dispatch. It uploads workflow artifacts without creating a GitHub Release.

## Project Structure

```text
cmd/pacman/                 Application entry point
internal/entities/          Player and ghost definitions
internal/game/              Game loop, movement, audio, collisions, state, scores
internal/tilemap/           Maze data and rendering
internal/ui/                HUD utilities
assets/images/              Image assets
assets/sounds/              Optional sound assets
docs/agent/                 Agent engineering and review guides
docs/adr/                   Architecture decision records
scripts/score_architecture.py  Local governance scorecard
scripts/visual_smoke.sh        Xvfb launch and screenshot validation
tests/test_score_architecture.py Scorecard regression tests
.github/workflows/            Validation and native release automation
```

## Technical Invariants

- Ebitengine calls `Update` at 60 UPS, while `Draw` renders to an offscreen buffer and `Layout` controls dimensions.
- The maze uses 16x16-pixel cells whose centers are `(x*16+8, y*16+8)`.
- Queued turns currently use a fixed 4-pixel alignment threshold.
- A blocked player snaps to the cell center to prevent jitter.
- Timing is tick-based. Frightened timeout processing occurs before the rest of the update logic.
- Level completion is terminal: player and ghost simulation stop once no regular or power pellets remain.
- High-score writes are atomic and happen immediately when a new score is achieved.

Detailed current and planned game requirements live in `requirements.md`.

## Agentic Repository Governance

This repository uses local-first governance and validation:

- `AGENTS.md` is the authoritative operating contract.
- `CLAUDE.md` is a symlink to `AGENTS.md` for cross-tool parity.
- `MEMORY.md` stores durable, non-secret context.
- `CONTEXT.md` is a temporary branch handoff placeholder.
- `INSTALL.md`, `DEVELOP.md`, and `CREATE-PR.md` define repeatable workflows.
- `make score-gate` requires every enabled architecture dimension to score 10/10.
- GitHub validation runs `make validate` under Xvfb and then runs `make visual-smoke`; release builds run natively on each target OS.

Treat documentation drift as incomplete work. Never store credentials, tokens, private keys, bearer headers, customer data, or other sensitive material in repository docs or examples.

## Known Follow-Ups

- Add multi-level progression that resets the maze and increases difficulty after the existing terminal level-complete state.

- Add chase/scatter ghost AI and pathfinding.
- Add fruits.
- Add licensed or original sound assets.

## License

See `LICENSE`.
