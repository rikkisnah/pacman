<!-- #ai-assisted with OCA/OpenAI Model with human supervision -->

# Go Style Guide

## Defaults

- Use Go modules.
- Require Go 1.22 or newer.
- Keep packages cohesive and names domain-specific.
- Prefer small interfaces at package boundaries.
- Return errors with context.
- Avoid global mutable state.

## Tooling

- Format with `gofmt`.
- Test with `go test ./...`.
- Lint with `go vet ./...`.
- Use the exact golangci-lint release in `.golangci-lint-version`; standard maturity treats it as required.

## Error Handling

- Check errors explicitly.
- Do not ignore errors with `_ =` unless the reason is documented and safe.
- Keep side effects visible in function names and package placement.
