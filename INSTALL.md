<!-- #ai-assisted with OCA/OpenAI Model with human supervision -->

# Install

Use this runbook to set up `pacman` locally.

## Required Inputs

```text
LOCAL_REPO="<absolute repo path>"
RUN_VALIDATION="<yes|no>"
```

Recommended defaults:

```text
LOCAL_REPO="$(pwd)"
RUN_VALIDATION="yes"
```

## Prerequisites

Confirm the standard command surface:

```bash
git --version
make --version
go version
golangci-lint version
```

Required versions are Go 1.22 or newer and the exact golangci-lint release named in `.golangci-lint-version` (currently 2.12.2). Install the official golangci-lint binary for the local operating system; `make lint` rejects missing or mismatched versions.

For Debian or Ubuntu, install Ebitengine and visual-smoke dependencies:

```bash
sudo apt-get update
sudo apt-get install --yes \
  libc6-dev libgl1-mesa-dev libxcursor-dev libxi-dev libxinerama-dev \
  libxrandr-dev libxxf86vm-dev libasound2-dev pkg-config xvfb x11-utils imagemagick
```

The dependency manager is Go modules.

## Setup

```bash
cd "$LOCAL_REPO"
git status --short
make setup
make lint
```

Use Makefile targets for normal setup and validation.

## Validation

```bash
make validate
make visual-smoke
```

`make visual-smoke` writes `tmp/pacman-smoke.png`. It requires Xvfb, `xwininfo`, ImageMagick, and GNU `timeout` and uses a temporary high-score directory with audio disabled.

## Release Builds

```bash
make release
```

Local release targets build only on a matching native amd64 host. GitHub's native release workflow builds all three supported platforms on `v*` tags or manual dispatch.

If validation is skipped, report why and list the exact command that should be run later.

## Expected Handoff

Report repo path, language/runtime version when known, dependency tool version when known, validation result, and skipped steps.
