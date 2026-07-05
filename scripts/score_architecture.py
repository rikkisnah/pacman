#ai-assisted with OCA/OpenAI Model with human supervision

"""Local governance scorecard for pacman."""

from __future__ import annotations

import argparse
import ast
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_NAME = "pacman"
LANGUAGE = "go"
RUNTIME_TYPE = "desktop-game"
MATURITY = "standard"
DISCLOSURE = "#ai-assisted with OCA/OpenAI Model with human supervision"
DISCLOSURE_MD = "<!-- #ai-assisted with OCA/OpenAI Model with human supervision -->"
MAX_AGENTS_LINES = 199
MAX_CONTEXT_LINES = 60
MAX_PYTHON_FUNCTION_LINES = 50
MAX_GO_FUNCTION_LINES = 60
MAX_BASH_FUNCTION_LINES = 50
MAX_SOURCE_FILE_LINES = 800

IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".uv-cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "htmlcov",
}

GOVERNANCE_FILES = (
    "README.md",
    "AGENTS.md",
    "MEMORY.md",
    "CONTEXT.md",
    "Makefile",
    "scripts/score_architecture.py",
    "tests/test_score_architecture.py",
    "docs/agent/clean-code-guide.md",
    "docs/agent/review-guide.md",
    "docs/agent/subagents-guide.md",
    "docs/agent/testing-guide.md",
    "docs/agent/go-style-guide.md",
    "docs/adr/template.md",
    "scripts/visual_smoke.sh",
    ".github/workflows/validate.yml",
    ".github/workflows/release.yml",
)

INSTALLABLE_RUNTIME_TYPES = {"library", "cli", "api", "webapp", "service", "desktop-game"}
DEPLOYABLE_RUNTIME_TYPES = {"api", "webapp", "service"}

WEAK_PUBLIC_NAMES = {
    "data",
    "info",
    "temp",
    "tmp",
    "result",
    "manager",
    "helper",
    "misc",
    "stuff",
    "thing",
    "common",
    "util",
    "utils",
}


@dataclass(frozen=True)
class ScoreResult:
    """One scorecard dimension result."""

    name: str
    score: int
    detail: str
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        """Return status for the dimension."""

        if self.score == 10:
            return "PASS"
        if self.score >= 8:
            return "WARN"
        return "FAIL"


def main(argv: list[str] | None = None) -> int:
    """Run the scorecard CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--min-score", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    results = run_scorecard(args.repo_root.resolve())
    if args.json:
        print(json.dumps([result.__dict__ | {"status": result.status} for result in results], indent=2))
    else:
        print(render_scorecard(results))

    if args.min_score and any(result.score < args.min_score for result in results):
        return 1
    return 0


def run_scorecard(repo_root: Path) -> list[ScoreResult]:
    """Run all enabled scorecard dimensions."""

    return [
        score_instruction_parity(repo_root),
        score_memory_governance(repo_root),
        score_context_governance(repo_root),
        score_documentation_accuracy(repo_root),
        score_workflow_docs(repo_root),
        score_build_and_tooling(repo_root),
        score_test_quality(repo_root),
        score_type_or_contract_safety(repo_root),
        score_clean_code(repo_root),
        score_module_cohesion(repo_root),
        score_duplication(repo_root),
        score_secret_safety(repo_root),
        score_runtime_contract(repo_root),
        score_agentic_reviewability(repo_root),
        score_disclosure_headers(repo_root),
    ]


def render_scorecard(results: list[ScoreResult]) -> str:
    """Render scorecard results."""

    lines = ["Architecture Scorecard", "======================"]
    for result in results:
        lines.append(f"{result.status:4} {result.score:2}/10 {result.name}: {result.detail}")
        for violation in result.violations:
            lines.append(f"  - {violation}")
        for warning in result.warnings:
            lines.append(f"  ? {warning}")
    overall = sum(result.score for result in results) / len(results) if results else 0.0
    lines.append(f"OVERALL {overall:.1f}/10")
    return "\n".join(lines)


def score_instruction_parity(repo_root: Path) -> ScoreResult:
    """Score AGENTS.md and CLAUDE.md parity."""

    violations: list[str] = []
    agents = repo_root / "AGENTS.md"
    if not agents.exists():
        violations.append("AGENTS.md is missing")
    else:
        text = agents.read_text(encoding="utf-8")
        if len(text.splitlines()) > MAX_AGENTS_LINES:
            violations.append("AGENTS.md must stay under 200 lines")
        # Keep delegation requirements visible in AGENTS.md, including skill-driven workflows.
        for required in (
            "CLAUDE.md must be a symlink",
            "docs/agent/clean-code-guide.md",
            "docs/agent/review-guide.md",
            "docs/agent/subagents-guide.md",
            "docs/agent/testing-guide.md",
            "Documentation drift is a bug",
            "Never write secrets",
            "Use subagents where applicable",
            "can be done independently and its result can be summarized compactly",
            "needs constant shared context, sequential reasoning, or produces mostly overlapping work",
            "skill-driven work",
            "clear ownership, expected output, constraints, and validation expectations",
            "primary agent remains responsible",
        ):
            if required not in text:
                violations.append(f"AGENTS.md missing {required!r}")

    claude = repo_root / "CLAUDE.md"
    if not claude.is_symlink() or os.readlink(claude) != "AGENTS.md":
        violations.append("CLAUDE.md must be a symlink to AGENTS.md")

    return result_from_violations("instruction parity", violations, "AGENTS/CLAUDE checked")


def score_memory_governance(repo_root: Path) -> ScoreResult:
    """Score MEMORY.md governance."""

    path = repo_root / "MEMORY.md"
    violations: list[str] = []
    if not path.exists():
        violations.append("MEMORY.md is missing")
    else:
        text = path.read_text(encoding="utf-8")
        for required in (
            "Project Context",
            "Stable Facts",
            "Decisions",
            "Assumptions",
            "Constraints",
            "Proposals",
            "Do Not Store Here",
            "not the source of truth",
        ):
            if required not in text:
                violations.append(f"MEMORY.md missing {required!r}")
    return result_from_violations("memory governance", violations, "MEMORY.md checked")


def score_context_governance(repo_root: Path) -> ScoreResult:
    """Score CONTEXT.md placeholder governance."""

    path = repo_root / "CONTEXT.md"
    violations: list[str] = []
    if not path.exists():
        violations.append("CONTEXT.md is missing")
    else:
        text = path.read_text(encoding="utf-8")
        if DISCLOSURE_MD not in text:
            violations.append("CONTEXT.md missing disclosure header")
        for required in ("Temporary working context", "Do not merge real working notes", "main", "master"):
            if required not in text:
                violations.append(f"CONTEXT.md missing {required!r}")
        if len(text.splitlines()) > MAX_CONTEXT_LINES:
            violations.append(f"CONTEXT.md has more than {MAX_CONTEXT_LINES} lines")
    return result_from_violations("context placeholder governance", violations, "CONTEXT.md checked")


def score_documentation_accuracy(repo_root: Path) -> ScoreResult:
    """Score required docs and docs drift rule."""

    violations: list[str] = []
    for relative_path in GOVERNANCE_FILES:
        if not (repo_root / relative_path).exists():
            violations.append(f"Missing required governance file: {relative_path}")

    readme = repo_root / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        for required in (
            "make setup",
            "make format",
            "make test",
            "make lint",
            "make score",
            "make validate",
            "AGENTS.md",
            "MEMORY.md",
            "CONTEXT.md",
            "docs/agent/",
        ):
            if required not in text:
                violations.append(f"README.md missing {required!r}")

    develop = repo_root / "DEVELOP.md"
    if develop.exists() and "Documentation drift is a bug" not in develop.read_text(encoding="utf-8"):
        violations.append("DEVELOP.md missing documentation drift rule")

    return result_from_violations("documentation accuracy", violations, "required docs checked")


def score_workflow_docs(repo_root: Path) -> ScoreResult:
    """Score runtime workflow docs."""

    expected = ["DEVELOP.md", "CREATE-PR.md"]
    if RUNTIME_TYPE in INSTALLABLE_RUNTIME_TYPES:
        expected.append("INSTALL.md")
    if RUNTIME_TYPE in DEPLOYABLE_RUNTIME_TYPES:
        expected.append("DEPLOY.md")

    violations = [f"{path} is missing" for path in expected if not (repo_root / path).exists()]
    for path in expected:
        doc = repo_root / path
        if doc.exists() and DISCLOSURE_MD not in doc.read_text(encoding="utf-8"):
            violations.append(f"{path} missing disclosure header")

    return result_from_violations("workflow docs", violations, ", ".join(expected))


def score_build_and_tooling(repo_root: Path) -> ScoreResult:
    """Score Makefile command surface."""

    path = repo_root / "Makefile"
    violations: list[str] = []
    if not path.exists():
        violations.append("Makefile is missing")
    else:
        text = path.read_text(encoding="utf-8")
        for target in (
            "help:",
            "setup:",
            "format:",
            "test:",
            "test-%:",
            "lint:",
            "score:",
            "score-gate:",
            "check:",
            "validate:",
            "visual-smoke:",
            "release:",
            "build-linux:",
            "build-darwin:",
            "build-windows:",
            "clean:",
            "clean-env:",
        ):
            if target not in text:
                violations.append(f"Makefile missing target {target}")
        validate_body = text.partition("validate:")[2]
        if "score-gate" not in validate_body:
            violations.append("validate target must include score-gate")
        if "--min-score 10" not in text:
            violations.append("score-gate must require --min-score 10")
        for required in (".golangci-lint-version", "scripts/visual_smoke.sh", "HOST_GOOS"):
            if required not in text:
                violations.append(f"Makefile missing {required!r}")

    lint_version = repo_root / ".golangci-lint-version"
    if not lint_version.exists():
        violations.append(".golangci-lint-version is missing")
    elif lint_version.read_text(encoding="utf-8").strip() != "v2.12.2":
        violations.append("golangci-lint must be pinned to v2.12.2")

    violations.extend(ci_workflow_violations(repo_root))
    return result_from_violations("build and tooling", violations, "Makefile checked")


def ci_workflow_violations(repo_root: Path) -> list[str]:
    """Return validation and native-release workflow violations."""

    violations: list[str] = []
    validation_terms = (
        "permissions:",
        "contents: read",
        "pull_request:",
        "push:",
        "workflow_dispatch:",
        "actions/checkout@v7",
        "actions/setup-go@v6",
        "golangci/golangci-lint-action@v9",
        "make validate",
        "make visual-smoke",
    )
    require_file_terms(repo_root, ".github/workflows/validate.yml", validation_terms, violations)

    release_terms = (
        "workflow_dispatch:",
        "tags:",
        "ubuntu-24.04",
        "macos-15-intel",
        "windows-2025",
        "pacman-linux-amd64.tar.gz",
        "pacman-darwin-amd64.tar.gz",
        "pacman-windows-amd64.exe",
        "actions/upload-artifact@v7",
    )
    release_text = require_file_terms(repo_root, ".github/workflows/release.yml", release_terms, violations)
    if "gh release" in release_text or "action-gh-release" in release_text:
        violations.append("release workflow must not create a GitHub Release")
    return violations


def score_test_quality(repo_root: Path) -> ScoreResult:
    """Score test presence and behavior-test signals."""

    violations: list[str] = []
    score_test = repo_root / "tests" / "test_score_architecture.py"
    if not score_test.exists():
        violations.append("tests/test_score_architecture.py is missing")
    else:
        text = score_test.read_text(encoding="utf-8")
        for required in (
            "test_current_repo_scores_cleanly",
            "test_agents_line_limit_is_enforced",
            "test_claude_symlink_requirement_is_enforced",
            "test_secret_patterns_lower_score",
            "test_clean_code_violations_lower_score",
            "test_runtime_contract_rejects_changed_movement_constant",
            "test_runtime_contract_rejects_missing_level_completion",
            "test_ci_contract_requires_validation_gate",
        ):
            if required not in text:
                violations.append(f"scorecard tests missing {required}")

    test_files = list((repo_root / "tests").glob("test_*.py")) if (repo_root / "tests").exists() else []
    if not test_files:
        violations.append("No test_*.py files found")

    return result_from_violations("test quality", violations, f"{len(test_files)} test files")


def score_type_or_contract_safety(repo_root: Path) -> ScoreResult:
    """Score type or public contract signals."""

    violations: list[str] = []
    if LANGUAGE == "python":
        missing_returns = 0
        for path in iter_python_files(repo_root):
            if "test_" in path.name or path.name == "score_architecture.py":
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
                    if node.returns is None:
                        missing_returns += 1
        if missing_returns:
            violations.append(f"{missing_returns} public Python functions lack return annotations")
    elif LANGUAGE == "go":
        if not (repo_root / "go.mod").exists():
            violations.append("go.mod is missing for Go contract safety")
    elif LANGUAGE == "bash":
        scripts = list(iter_files(repo_root, {".sh"}))
        if not scripts:
            violations.append("No Bash scripts found for Bash profile")
    else:
        if not any((repo_root / path).exists() for path in ("README.md", "AGENTS.md", "Makefile")):
            violations.append("Generic contract files missing")
    return result_from_violations("type or contract safety", violations, f"{LANGUAGE} contract checked")


def score_clean_code(repo_root: Path) -> ScoreResult:
    """Score measurable clean-code signals."""

    violations: list[str] = []
    violations.extend(check_python_clean_code(repo_root))
    violations.extend(check_go_clean_code(repo_root))
    violations.extend(check_bash_clean_code(repo_root))
    violations.extend(check_generic_dumping_grounds(repo_root))
    return result_from_violations("clean code", violations, "clean-code heuristics checked")


def check_python_clean_code(repo_root: Path) -> list[str]:
    """Return Python clean-code violations."""

    violations: list[str] = []
    for path in iter_python_files(repo_root):
        if path.name == "score_architecture.py":
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as error:
            violations.append(f"{path}: syntax error: {error.msg}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                length = (node.end_lineno or node.lineno) - node.lineno + 1
                if length > MAX_PYTHON_FUNCTION_LINES:
                    violations.append(f"{path}:{node.lineno} {node.name} is {length} lines")
                if not node.name.startswith("_") and node.name.lower() in WEAK_PUBLIC_NAMES:
                    violations.append(f"{path}:{node.lineno} weak public function name {node.name!r}")
                if has_hidden_side_effect(path, node):
                    violations.append(f"{path}:{node.lineno} {node.name} has hidden side effects")
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    violations.append(f"{path}:{node.lineno} bare except")
                if any(isinstance(child, ast.Pass) for child in node.body):
                    violations.append(f"{path}:{node.lineno} swallowed exception")
    return violations


def has_hidden_side_effect(path: Path, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Detect suspicious side effects in pure-sounding Python functions."""

    if not node.name.startswith(("calculate", "format", "parse", "validate")):
        return False
    source = "\n".join(path.read_text(encoding="utf-8").splitlines()[node.lineno - 1 : node.end_lineno])
    side_effect_terms = (".write(", "open(", "requests.", "subprocess.", "send_", "emit_", "global ")
    return any(term in source for term in side_effect_terms)


def check_go_clean_code(repo_root: Path) -> list[str]:
    """Return Go clean-code violations."""

    violations: list[str] = []
    for path in iter_files(repo_root, {".go"}):
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) > MAX_SOURCE_FILE_LINES:
            violations.append(f"{path}: source file exceeds {MAX_SOURCE_FILE_LINES} lines")
        if re.search(r"_\s*=\s*\w+\(", "\n".join(lines)):
            violations.append(f"{path}: ignored error-looking call")
    return violations


def check_bash_clean_code(repo_root: Path) -> list[str]:
    """Return Bash clean-code violations."""

    violations: list[str] = []
    for path in iter_files(repo_root, {".sh"}):
        text = path.read_text(encoding="utf-8")
        if "set -euo pipefail" not in text:
            violations.append(f"{path}: missing set -euo pipefail")
        if len(text.splitlines()) > MAX_SOURCE_FILE_LINES:
            violations.append(f"{path}: source file exceeds {MAX_SOURCE_FILE_LINES} lines")
    return violations


def check_generic_dumping_grounds(repo_root: Path) -> list[str]:
    """Return generic utility dumping-ground violations."""

    violations: list[str] = []
    for path in iter_source_files(repo_root):
        if path.stem.lower() in {"utils", "util", "helpers", "helper", "common", "misc"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            public_markers = len(re.findall(r"(?m)^(def|func|function)\s+\w+", text))
            if public_markers > 5:
                violations.append(f"{path}: generic dumping-ground module with {public_markers} public helpers")
    return violations


def score_module_cohesion(repo_root: Path) -> ScoreResult:
    """Score module cohesion."""

    violations: list[str] = []
    for path in iter_source_files(repo_root):
        if path.name == "score_architecture.py":
            continue
        line_count = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
        if line_count > MAX_SOURCE_FILE_LINES:
            violations.append(f"{path}: {line_count} lines exceeds {MAX_SOURCE_FILE_LINES}")
    return result_from_violations("module cohesion", violations, "source sizes checked")


def score_duplication(repo_root: Path) -> ScoreResult:
    """Score duplicate public helper names."""

    names: dict[str, list[str]] = {}
    for path in iter_python_files(repo_root):
        if path.name == "score_architecture.py":
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                names.setdefault(node.name, []).append(str(path))
    violations = [
        f"Duplicate public function {name!r} in {', '.join(locations)}"
        for name, locations in names.items()
        if len(locations) > 1 and name != "main"
    ]
    return result_from_violations("duplication", violations, "public helper names checked")


def score_secret_safety(repo_root: Path) -> ScoreResult:
    """Score obvious secret safety."""

    violations: list[str] = []
    for path in iter_secret_scan_files(repo_root):
        relative_name = path.name.lower()
        if relative_name.startswith(".env") and relative_name not in {".env.example", ".env.sample", ".env.template"}:
            violations.append(f"{path}: committed env file is not allowed")
            continue
        if path.as_posix().endswith("scripts/score_architecture.py"):
            continue
        if path.as_posix().endswith("tests/test_score_architecture.py"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        violations.extend(secret_violations_for_text(path, text))
    return result_from_violations("security and secret safety", violations, "secret scan checked")


def secret_violations_for_text(path: Path, text: str) -> list[str]:
    """Return obvious secret violations from text."""

    allowed_placeholders = ("<token>", "<secret>", "REPLACE_ME", "example_password", "dummy")
    violations: list[str] = []
    if "-----BEGIN PRIVATE KEY-----" in text:
        violations.append(f"{path}: private key marker")
    patterns = (
        r"(?i)bearer\s+[a-z0-9._=-]{20,}",
        r"(?i)(api_key|secret_key|password|token)\s*[:=]\s*['\"]?[a-z0-9._/+=-]{16,}",
        r"(?i)authorization\s*[:=]\s*['\"]?bearer\s+[a-z0-9._=-]{20,}",
    )
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            matched = match.group(0)
            if any(placeholder.lower() in matched.lower() for placeholder in allowed_placeholders):
                continue
            violations.append(f"{path}: risky secret-looking pattern")
            break
    return violations


def score_runtime_contract(repo_root: Path) -> ScoreResult:
    """Score the Pac-Man desktop runtime contract."""

    violations: list[str] = []
    require_file_terms(repo_root, "AGENTS.md", ("Runtime: desktop game",), violations)
    require_file_terms(
        repo_root,
        "go.mod",
        ("module pacman", "go 1.22", "github.com/hajimehoshi/ebiten/v2"),
        violations,
    )
    require_file_terms(repo_root, "cmd/pacman/main.go", ("ebiten.RunGame(g)",), violations)
    game_text = require_file_terms(
        repo_root,
        "internal/game/game.go",
        (
            "func (g *Game) Update() error",
            "func (g *Game) Draw(screen *ebiten.Image)",
            "func (g *Game) Layout(",
            "drawNamePrompt",
            "levelComplete",
            "drawLevelComplete",
        ),
        violations,
    )
    for name, value in (
        ("tileSize", "16"),
        ("updatesPerSecond", "60"),
        ("playerSpeedPixelsPerSecond", "120.0"),
        ("ghostSpeedPixelsPerSecond", "105.0"),
        ("frightenedDurationUpdates", "120"),
        ("alignmentThreshold", "4.0"),
    ):
        if not re.search(rf"(?m)^\s*{re.escape(name)}\s*=\s*{re.escape(value)}(?:\s|$)", game_text):
            violations.append(f"internal/game/game.go missing {name} = {value}")

    require_file_terms(
        repo_root,
        "internal/game/audio.go",
        ("PACMAN_ENABLE_AUDIO", "PACMAN_DISABLE_AUDIO"),
        violations,
    )
    require_file_terms(repo_root, "internal/game/highscore.go", ("PACMAN_CONFIG_DIR",), violations)
    require_file_terms(
        repo_root,
        "internal/game/game_movement_test.go",
        ("TestMovementConfiguration", "TestVerticalTurnsRespondBeyondAlignmentThreshold", "TestVerticalTurnsRejectWalls"),
        violations,
    )
    require_file_terms(
        repo_root,
        "internal/game/game_draw_test.go",
        ("TestNamePromptBackdropProvidesContrast", "TestLevelCompletePanelIsCenteredAndOpaque"),
        violations,
    )
    require_file_terms(
        repo_root,
        "internal/tilemap/tilemap.go",
        ("func (m *TileMap) RemainingPellets() int",),
        violations,
    )
    require_file_terms(
        repo_root,
        "internal/game/game_collision.go",
        ("g.tileMap.RemainingPellets() == 0", "g.completeLevel()"),
        violations,
    )
    require_file_terms(
        repo_root,
        "internal/game/game_completion_test.go",
        (
            "TestFinalPelletCompletesLevelEndToEnd",
            "TestNonFinalPelletDoesNotCompleteLevel",
            "TestFinalPelletWinsBeforeGhostCollision",
            "TestFinalPelletPersistsWinnerBelowGlobalHighScore",
        ),
        violations,
    )
    require_file_terms(
        repo_root,
        "scripts/visual_smoke.sh",
        ("xvfb-run", "xwininfo", "PACMAN_DISABLE_AUDIO", "PACMAN_CONFIG_DIR", "import", "124"),
        violations,
    )
    return result_from_violations("runtime contract", violations, "Pac-Man desktop-game contract checked")


def require_file_terms(
    repo_root: Path,
    relative_path: str,
    required_terms: tuple[str, ...],
    violations: list[str],
) -> str:
    """Require a file and literal contract terms, returning its text."""

    path = repo_root / relative_path
    if not path.exists():
        violations.append(f"{relative_path} is missing")
        return ""
    text = path.read_text(encoding="utf-8")
    for term in required_terms:
        if term not in text:
            violations.append(f"{relative_path} missing {term!r}")
    return text


def score_agentic_reviewability(repo_root: Path) -> ScoreResult:
    """Score reviewability and handoff docs."""

    violations: list[str] = []
    create_pr = repo_root / "CREATE-PR.md"
    if create_pr.exists():
        text = create_pr.read_text(encoding="utf-8")
        for required in ("git status --short", "make validate", "Do not push", "risks"):
            if required not in text:
                violations.append(f"CREATE-PR.md missing {required!r}")
    else:
        violations.append("CREATE-PR.md is missing")
    clean_code = repo_root / "docs/agent/clean-code-guide.md"
    if clean_code.exists() and "Required Explanations" not in clean_code.read_text(encoding="utf-8"):
        violations.append("clean-code guide missing required explanations section")
    # Require the cross-tool delegation policy to stay visible to Claude and Codex.
    subagents = repo_root / "docs" / "agent" / "subagents-guide.md"
    if subagents.exists():
        text = subagents.read_text(encoding="utf-8")
        for required in (
            "Claude",
            "Task",
            "Codex",
            "spawn_agent",
            "parallelizable",
            "independent review",
            "disjoint write scopes",
        ):
            if required not in text:
                violations.append(f"subagents guide missing {required!r}")
    else:
        violations.append("subagents guide is missing")
    return result_from_violations("agentic reviewability", violations, "handoff docs checked")


def score_disclosure_headers(repo_root: Path) -> ScoreResult:
    """Score OCA/OpenAI disclosure headers in generated governance files."""

    violations: list[str] = []
    for relative_path in GOVERNANCE_FILES:
        path = repo_root / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        expected = DISCLOSURE_MD if path.suffix == ".md" else DISCLOSURE
        if expected not in "\n".join(text.splitlines()[:5]):
            violations.append(f"{relative_path} missing disclosure header")
    return result_from_violations("AI disclosure headers", violations, "generated files checked")


def result_from_violations(name: str, violations: list[str], detail: str) -> ScoreResult:
    """Build a score result from violations."""

    score = 10 if not violations else max(0, 10 - len(violations))
    return ScoreResult(name, score, detail, violations)


def iter_python_files(repo_root: Path) -> list[Path]:
    """Return Python files for scoring."""

    return list(iter_files(repo_root, {".py"}))


def iter_source_files(repo_root: Path) -> list[Path]:
    """Return source-like files for generic checks."""

    return list(iter_files(repo_root, {".py", ".go", ".sh", ".js", ".ts", ".java", ".rb", ".rs"}))


def iter_secret_scan_files(repo_root: Path) -> list[Path]:
    """Return files to scan for obvious secrets."""

    suffixes = {".md", ".py", ".sh", ".go", ".toml", ".yaml", ".yml", ".json", ".env", ".txt"}
    files = list(iter_files(repo_root, suffixes))
    for env_file in repo_root.glob(".env*"):
        if env_file.is_file():
            files.append(env_file)
    return sorted(set(files))


def iter_files(repo_root: Path, suffixes: set[str]) -> list[Path]:
    """Return files under repo_root with selected suffixes."""

    files: list[Path] = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.relative_to(repo_root).parts):
            continue
        if path.suffix in suffixes or path.name in suffixes:
            files.append(path)
    return sorted(files)


if __name__ == "__main__":
    raise SystemExit(main())
