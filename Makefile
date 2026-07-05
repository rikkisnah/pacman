#ai-assisted with OCA/OpenAI Model with human supervision

SHELL := /bin/bash

.DEFAULT_GOAL := help

GO             ?= go
GO_CMD         ?= env -u GOROOT $(GO)
GOLANGCI_LINT  ?= golangci-lint
GOLANGCI_LINT_VERSION_FILE ?= .golangci-lint-version
GOLANGCI_LINT_VERSION := $(shell sed -e 's/^v//' $(GOLANGCI_LINT_VERSION_FILE) 2>/dev/null)
BINARY         ?= pacman
PKG            ?= ./cmd/pacman
BUILD_DIR      ?= bin
VISUAL_SMOKE_OUTPUT ?= tmp/pacman-smoke.png
HOST_GOOS      := $(shell $(GO_CMD) env GOOS)
HOST_GOARCH    := $(shell $(GO_CMD) env GOARCH)

.PHONY: help setup deps format fmt test test-% lint vet score score-gate check validate \
	build run visual-smoke coverage coverage-html release build-linux build-darwin build-windows \
	clean clean-env

help:
	@printf '%s\n' \
		'Targets:' \
		'  setup          Download Go modules' \
		'  deps           Tidy Go module metadata' \
		'  format/fmt     Format Go source' \
		'  test           Run all unit tests' \
		'  test-NAME      Run tests matching NAME' \
		'  lint/vet       Run static checks' \
		'  score          Print the architecture scorecard' \
		'  score-gate     Require every scorecard dimension to score 10/10' \
		'  check          Run lint and tests' \
		'  validate       Run the full local validation gate' \
		'  build/run      Build or run the game' \
		'  visual-smoke   Launch under Xvfb and capture the initial screen' \
		'  coverage       Print test coverage' \
		'  coverage-html  Write coverage.html' \
		'  release        Build an artifact for this native host' \
		'  clean          Remove generated artifacts'

setup:
	$(GO_CMD) mod download

deps:
	$(GO_CMD) mod tidy

format:
	@if command -v gofmt >/dev/null 2>&1; then \
		gofmt -w $$(find . -type f -name '*.go' -not -path './.git/*'); \
	else \
		echo 'gofmt missing.'; \
		exit 1; \
	fi

fmt: format

test:
	$(GO_CMD) test ./...

test-%:
	$(GO_CMD) test ./... -run "$*"

lint:
	$(GO_CMD) vet ./...
	@if ! command -v $(GOLANGCI_LINT) >/dev/null 2>&1; then \
		echo 'golangci-lint $(GOLANGCI_LINT_VERSION) is required; see INSTALL.md.'; \
		exit 1; \
	fi
	@actual="$$(env -u GOROOT $(GOLANGCI_LINT) version 2>/dev/null)"; \
	if ! printf '%s\n' "$$actual" | grep -F 'version $(GOLANGCI_LINT_VERSION) ' >/dev/null; then \
		echo "golangci-lint $(GOLANGCI_LINT_VERSION) is required; found: $$actual"; \
		exit 1; \
	fi
	env -u GOROOT $(GOLANGCI_LINT) run

vet:
	$(GO_CMD) vet ./...

score:
	python3 scripts/score_architecture.py

score-gate:
	python3 scripts/score_architecture.py --min-score 10

check: lint test

validate: check score-gate

build: setup
	@mkdir -p $(BUILD_DIR)
	$(GO_CMD) build -o $(BUILD_DIR)/$(BINARY) $(PKG)

run: build
	./$(BUILD_DIR)/$(BINARY)

visual-smoke: build
	VISUAL_SMOKE_BINARY="$(abspath $(BUILD_DIR)/$(BINARY))" \
	VISUAL_SMOKE_OUTPUT="$(abspath $(VISUAL_SMOKE_OUTPUT))" \
	./scripts/visual_smoke.sh

coverage:
	$(GO_CMD) test ./... -coverprofile=coverage.out
	$(GO_CMD) tool cover -func=coverage.out

coverage-html: coverage
	$(GO_CMD) tool cover -html=coverage.out -o coverage.html
	@echo 'HTML report written to coverage.html'

release: build-$(HOST_GOOS)

build-linux:
	@if [ "$(HOST_GOOS)" != 'linux' ] || [ "$(HOST_GOARCH)" != 'amd64' ]; then \
		echo 'build-linux requires a native linux/amd64 host; use the GitHub release workflow.'; \
		exit 2; \
	fi
	@mkdir -p $(BUILD_DIR)
	$(GO_CMD) build -o $(BUILD_DIR)/$(BINARY)-linux-amd64 $(PKG)

build-darwin:
	@if [ "$(HOST_GOOS)" != 'darwin' ] || [ "$(HOST_GOARCH)" != 'amd64' ]; then \
		echo 'build-darwin requires a native darwin/amd64 host; use the GitHub release workflow.'; \
		exit 2; \
	fi
	@mkdir -p $(BUILD_DIR)
	$(GO_CMD) build -o $(BUILD_DIR)/$(BINARY)-darwin-amd64 $(PKG)

build-windows:
	@if [ "$(HOST_GOOS)" != 'windows' ] || [ "$(HOST_GOARCH)" != 'amd64' ]; then \
		echo 'build-windows requires a native windows/amd64 host; use the GitHub release workflow.'; \
		exit 2; \
	fi
	@mkdir -p $(BUILD_DIR)
	$(GO_CMD) build -o $(BUILD_DIR)/$(BINARY)-windows-amd64.exe $(PKG)

clean:
	rm -rf $(BUILD_DIR) coverage.out coverage.html dist build tmp .cache

clean-env:
	$(GO_CMD) clean -cache -testcache
