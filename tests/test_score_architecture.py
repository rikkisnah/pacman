#ai-assisted with OCA/OpenAI Model with human supervision

"""Regression tests for scripts/score_architecture.py."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "score_architecture.py"
SPEC = importlib.util.spec_from_file_location("score_architecture", SCRIPT_PATH)
assert SPEC is not None
score_architecture = importlib.util.module_from_spec(SPEC)
sys.modules["score_architecture"] = score_architecture
assert SPEC.loader is not None
SPEC.loader.exec_module(score_architecture)


DISCLOSURE = "#ai-assisted with OCA/OpenAI Model with human supervision"
DISCLOSURE_MD = "<!-- #ai-assisted with OCA/OpenAI Model with human supervision -->"


class ScoreArchitectureTests(unittest.TestCase):
    """Scorecard policy regression tests."""

    def test_current_repo_scores_cleanly(self) -> None:
        repo = Path(__file__).resolve().parents[1]

        results = score_architecture.run_scorecard(repo)

        self.assertTrue(results)
        self.assertTrue(all(result.score == 10 for result in results), results)

    def test_agents_line_limit_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "AGENTS.md").write_text("\n".join(["line"] * 210), encoding="utf-8")

            result = score_architecture.score_instruction_parity(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("under 200" in violation for violation in result.violations))

    def test_claude_symlink_requirement_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp), symlink=False)

            result = score_architecture.score_instruction_parity(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("CLAUDE.md" in violation for violation in result.violations))

    def test_validate_must_include_score_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "Makefile").write_text(
                f"{DISCLOSURE}\nscore-gate:\n\tpython3 scripts/score_architecture.py --min-score 10\nvalidate: check\n",
                encoding="utf-8",
            )

            result = score_architecture.score_build_and_tooling(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("validate target" in violation for violation in result.violations))

    def test_score_gate_requires_ten(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            makefile = (repo / "Makefile").read_text(encoding="utf-8").replace("--min-score 10", "--min-score 8")
            (repo / "Makefile").write_text(makefile, encoding="utf-8")

            result = score_architecture.score_build_and_tooling(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("--min-score 10" in violation for violation in result.violations))

    def test_missing_required_docs_lower_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "README.md").unlink()

            result = score_architecture.score_documentation_accuracy(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("README.md" in violation for violation in result.violations))

    def test_missing_clean_code_guide_lowers_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "docs/agent/clean-code-guide.md").unlink()

            result = score_architecture.score_documentation_accuracy(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("clean-code-guide" in violation for violation in result.violations))

    def test_missing_subagents_guide_lowers_scores(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "docs/agent/subagents-guide.md").unlink()

            docs_result = score_architecture.score_documentation_accuracy(repo)
            review_result = score_architecture.score_agentic_reviewability(repo)

        self.assertLess(docs_result.score, 10)
        self.assertLess(review_result.score, 10)
        self.assertTrue(any("subagents-guide" in violation for violation in docs_result.violations))
        self.assertTrue(any("subagents guide" in violation for violation in review_result.violations))

    def test_agents_must_link_to_clean_code_guide(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            agents = (repo / "AGENTS.md").read_text(encoding="utf-8").replace(
                "docs/agent/clean-code-guide.md",
                "docs/agent/missing.md",
            )
            (repo / "AGENTS.md").write_text(agents, encoding="utf-8")

            result = score_architecture.score_instruction_parity(repo)

        self.assertLess(result.score, 10)

    def test_agents_must_link_to_subagents_guide(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            agents = (repo / "AGENTS.md").read_text(encoding="utf-8").replace(
                "docs/agent/subagents-guide.md",
                "docs/agent/missing-subagents.md",
            )
            (repo / "AGENTS.md").write_text(agents, encoding="utf-8")

            result = score_architecture.score_instruction_parity(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("subagents-guide" in violation for violation in result.violations))

    def test_agents_must_include_skill_aware_subagent_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            # The top-level agent contract must mention skill-driven delegation directly.
            agents = (repo / "AGENTS.md").read_text(encoding="utf-8").replace(
                "Apply this rule during skill-driven work as well as ordinary repo work.",
                "",
            )
            (repo / "AGENTS.md").write_text(agents, encoding="utf-8")

            result = score_architecture.score_instruction_parity(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("skill-driven work" in violation for violation in result.violations))

    def test_agents_must_include_subagent_decision_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            agents = (repo / "AGENTS.md").read_text(encoding="utf-8").replace(
                "Use a subagent when the task can be done independently and its result can be summarized compactly.",
                "",
            )
            (repo / "AGENTS.md").write_text(agents, encoding="utf-8")

            result = score_architecture.score_instruction_parity(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("summarized compactly" in violation for violation in result.violations))

    def test_missing_scorecard_tests_lower_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "tests/test_score_architecture.py").unlink()

            result = score_architecture.score_test_quality(repo)

        self.assertLess(result.score, 10)

    def test_runtime_contract_accepts_clean_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))

            result = score_architecture.score_runtime_contract(repo)

        self.assertEqual(result.score, 10, result.violations)

    def test_runtime_contract_rejects_changed_movement_constant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            game = repo / "internal/game/game.go"
            game.write_text(game.read_text(encoding="utf-8").replace("120.0", "720.0"), encoding="utf-8")

            result = score_architecture.score_runtime_contract(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("playerSpeedPixelsPerSecond" in violation for violation in result.violations))

    def test_runtime_contract_rejects_missing_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "cmd/pacman/main.go").write_text("package main\n", encoding="utf-8")

            result = score_architecture.score_runtime_contract(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("RunGame" in violation for violation in result.violations))

    def test_runtime_contract_rejects_missing_environment_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "internal/game/audio.go").write_text("package game\n", encoding="utf-8")

            result = score_architecture.score_runtime_contract(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("PACMAN_ENABLE_AUDIO" in violation for violation in result.violations))

    def test_runtime_contract_rejects_missing_level_completion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "internal/game/game_collision.go").write_text("package game\n", encoding="utf-8")

            result = score_architecture.score_runtime_contract(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("completeLevel" in violation for violation in result.violations))

    def test_ci_contract_requires_validation_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            workflow = repo / ".github/workflows/validate.yml"
            workflow.write_text(workflow.read_text(encoding="utf-8").replace("make validate", "make test"), encoding="utf-8")

            result = score_architecture.score_build_and_tooling(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("make validate" in violation for violation in result.violations))

    def test_ci_contract_requires_native_release_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            workflow = repo / ".github/workflows/release.yml"
            workflow.write_text(workflow.read_text(encoding="utf-8").replace("macos-15-intel", "ubuntu-24.04"), encoding="utf-8")

            result = score_architecture.score_build_and_tooling(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("macos-15-intel" in violation for violation in result.violations))

    def test_lint_version_pin_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / ".golangci-lint-version").write_text("v1.64.8\n", encoding="utf-8")

            result = score_architecture.score_build_and_tooling(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("v2.12.2" in violation for violation in result.violations))

    def test_missing_type_or_public_contract_signals_lower_score_where_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            source = repo / "src/example.py"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(f"{DISCLOSURE}\n\ndef public_function():\n    return 1\n", encoding="utf-8")

            result = score_architecture.score_type_or_contract_safety(repo)

        if score_architecture.LANGUAGE == "python":
            self.assertLess(result.score, 10)
        else:
            self.assertTrue(result.score <= 10)

    def test_generic_public_helper_names_lower_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            source = repo / "src/bad_names.py"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(f"{DISCLOSURE}\n\ndef helper() -> None:\n    return None\n", encoding="utf-8")

            result = score_architecture.score_clean_code(repo)

        self.assertLess(result.score, 10)

    def test_long_functions_lower_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            body = "\n".join("    value = 1" for _ in range(55))
            (repo / "src/long_func.py").write_text(
                f"{DISCLOSURE}\n\ndef long_function() -> None:\n{body}\n",
                encoding="utf-8",
            )

            result = score_architecture.score_clean_code(repo)

        self.assertLess(result.score, 10)

    def test_bare_except_lowers_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "src/bare_except.py").write_text(
                f"{DISCLOSURE}\n\ndef run() -> None:\n    try:\n        risky()\n    except:\n        raise\n",
                encoding="utf-8",
            )

            result = score_architecture.score_clean_code(repo)

        self.assertLess(result.score, 10)

    def test_swallowed_errors_lower_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "src/swallowed.py").write_text(
                f"{DISCLOSURE}\n\ndef run() -> None:\n    try:\n        risky()\n    except Exception:\n        pass\n",
                encoding="utf-8",
            )

            result = score_architecture.score_clean_code(repo)

        self.assertLess(result.score, 10)

    def test_hidden_side_effects_lower_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "src/hidden.py").write_text(
                f"{DISCLOSURE}\n\ndef calculate_total() -> None:\n    open('out.txt', 'w').write('x')\n",
                encoding="utf-8",
            )

            result = score_architecture.score_clean_code(repo)

        self.assertLess(result.score, 10)

    def test_utils_dumping_ground_lowers_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            helpers = "\n".join(f"def public_{index}() -> None:\n    return None\n" for index in range(6))
            (repo / "src/utils.py").write_text(f"{DISCLOSURE}\n\n{helpers}", encoding="utf-8")

            result = score_architecture.score_clean_code(repo)

        self.assertLess(result.score, 10)

    def test_missing_behavior_tests_lowers_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "tests").rename(repo / "tests-moved")

            result = score_architecture.score_test_quality(repo)

        self.assertLess(result.score, 10)

    def test_duplicate_public_helpers_lower_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "src/a.py").write_text(f"{DISCLOSURE}\n\ndef duplicate() -> None:\n    return None\n", encoding="utf-8")
            (repo / "src/b.py").write_text(f"{DISCLOSURE}\n\ndef duplicate() -> None:\n    return None\n", encoding="utf-8")

            result = score_architecture.score_duplication(repo)

        self.assertLess(result.score, 10)

    def test_secret_patterns_lower_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "README.md").write_text(
                f"{DISCLOSURE_MD}\n\napi_key = 'abcdef1234567890abcdef'\n",
                encoding="utf-8",
            )

            result = score_architecture.score_secret_safety(repo)

        self.assertLess(result.score, 10)

    def test_committed_env_lowers_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / ".env").write_text("TOKEN=<token>\n", encoding="utf-8")

            result = score_architecture.score_secret_safety(repo)

        self.assertLess(result.score, 10)

    def test_context_too_large_lowers_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "CONTEXT.md").write_text(DISCLOSURE_MD + "\n" + "\n".join("line" for _ in range(70)), encoding="utf-8")

            result = score_architecture.score_context_governance(repo)

        self.assertLess(result.score, 10)

    def test_oca_openai_disclosure_header_rule_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "README.md").write_text("# Missing header\n", encoding="utf-8")

            result = score_architecture.score_disclosure_headers(repo)

        self.assertLess(result.score, 10)

    def test_all_generated_markdown_requires_disclosure_header(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "docs/agent/review-guide.md").write_text("# Missing header\n", encoding="utf-8")

            result = score_architecture.score_disclosure_headers(repo)

        self.assertLess(result.score, 10)

    def test_incomplete_subagents_guide_lowers_reviewability(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._clean_repo(Path(tmp))
            (repo / "docs/agent/subagents-guide.md").write_text(
                f"{DISCLOSURE_MD}\n# Subagents Guide\n\nUse subagents.\n",
                encoding="utf-8",
            )

            result = score_architecture.score_agentic_reviewability(repo)

        self.assertLess(result.score, 10)
        self.assertTrue(any("Codex" in violation for violation in result.violations))

    def _clean_repo(self, repo: Path, *, symlink: bool = True) -> Path:
        for path in (
            ".github/workflows",
            "cmd/pacman",
            "docs/agent",
            "docs/adr",
            "internal/game",
            "scripts",
            "tests",
            "src",
        ):
            (repo / path).mkdir(parents=True, exist_ok=True)

        files = self._fixture_files()
        files.update(self._runtime_fixture_files())
        if score_architecture.RUNTIME_TYPE in score_architecture.INSTALLABLE_RUNTIME_TYPES:
            files["INSTALL.md"] = f"{DISCLOSURE_MD}\n# Install\n"
        if score_architecture.RUNTIME_TYPE in score_architecture.DEPLOYABLE_RUNTIME_TYPES:
            files["DEPLOY.md"] = f"{DISCLOSURE_MD}\n# Deploy\n"

        for relative_path, content in files.items():
            path = repo / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

        if symlink:
            os.symlink("AGENTS.md", repo / "CLAUDE.md")
        else:
            (repo / "CLAUDE.md").write_text("not a symlink\n", encoding="utf-8")
        return repo

    def _fixture_files(self) -> dict[str, str]:
        return {
            "README.md": self._readme(),
            "AGENTS.md": self._agents(),
            "MEMORY.md": self._memory(),
            "CONTEXT.md": self._context(),
            "Makefile": self._makefile(),
            ".golangci-lint-version": "v2.12.2\n",
            ".github/workflows/validate.yml": self._validation_workflow(),
            ".github/workflows/release.yml": self._release_workflow(),
            "scripts/score_architecture.py": f"{DISCLOSURE}\n",
            "scripts/visual_smoke.sh": self._visual_smoke_script(),
            "tests/test_score_architecture.py": self._score_tests_text(),
            "docs/agent/clean-code-guide.md": self._clean_code(),
            "docs/agent/review-guide.md": self._review(),
            "docs/agent/subagents-guide.md": self._subagents(),
            "docs/agent/testing-guide.md": f"{DISCLOSURE_MD}\n# Testing Guide\n",
            f"docs/agent/{score_architecture.LANGUAGE}-style-guide.md": f"{DISCLOSURE_MD}\n# Style Guide\n",
            "docs/adr/template.md": f"{DISCLOSURE_MD}\n# ADR-NNNN: Title\n",
            "CREATE-PR.md": self._create_pr(),
            "DEVELOP.md": f"{DISCLOSURE_MD}\n# Develop\n\nDocumentation drift is a bug.\n",
        }

    def _runtime_fixture_files(self) -> dict[str, str]:
        return {
            "go.mod": "module pacman\n\ngo 1.22\n\nrequire github.com/hajimehoshi/ebiten/v2 v2.7.7\n",
            "cmd/pacman/main.go": "package main\n\n// ebiten.RunGame(g)\n",
            "internal/game/game.go": self._game_source(),
            "internal/game/audio.go": "package game\n\n// PACMAN_ENABLE_AUDIO PACMAN_DISABLE_AUDIO\n",
            "internal/game/highscore.go": "package game\n\n// PACMAN_CONFIG_DIR\n",
            "internal/game/game_movement_test.go": (
                "package game\n\n"
                "// TestMovementConfiguration TestVerticalTurnsRespondBeyondAlignmentThreshold "
                "TestVerticalTurnsRejectWalls\n"
            ),
            "internal/game/game_draw_test.go": (
                "package game\n\n"
                "// TestNamePromptBackdropProvidesContrast TestLevelCompletePanelIsCenteredAndOpaque\n"
            ),
            "internal/game/game_completion_test.go": (
                "package game\n\n"
                "// TestFinalPelletCompletesLevelEndToEnd TestNonFinalPelletDoesNotCompleteLevel "
                "TestFinalPelletWinsBeforeGhostCollision "
                "TestFinalPelletPersistsWinnerBelowGlobalHighScore\n"
            ),
            "internal/game/game_collision.go": (
                "package game\n\n"
                "// g.tileMap.RemainingPellets() == 0\n"
                "// g.completeLevel()\n"
            ),
            "internal/tilemap/tilemap.go": (
                "package tilemap\n\n"
                "func (m *TileMap) RemainingPellets() int { return 0 }\n"
            ),
        }

    def _readme(self) -> str:
        return (
            f"{DISCLOSURE_MD}\n# Repo\n\n"
            "make setup\nmake format\nmake test\nmake lint\nmake score\nmake validate\n"
            "AGENTS.md\nMEMORY.md\nCONTEXT.md\ndocs/agent/\n"
        )

    def _agents(self) -> str:
        return (
            f"{DISCLOSURE_MD}\n# Agents\n\n"
            "Runtime: desktop game\n"
            "CLAUDE.md must be a symlink\n"
            "docs/agent/clean-code-guide.md\n"
            "docs/agent/review-guide.md\n"
            "docs/agent/subagents-guide.md\n"
            "docs/agent/testing-guide.md\n"
            "Documentation drift is a bug\n"
            "Never write secrets\n"
            "Use subagents where applicable\n"
            "Apply this rule during skill-driven work as well as ordinary repo work.\n"
            "Use a subagent when the task can be done independently and its result can be summarized compactly.\n"
            "Do not use a subagent when the task needs constant shared context, sequential reasoning, or produces mostly overlapping work.\n"
            "clear ownership, expected output, constraints, and validation expectations\n"
            "primary agent remains responsible\n"
        )

    def _memory(self) -> str:
        return (
            f"{DISCLOSURE_MD}\n# Memory\n\n"
            "## Project Context\n## Stable Facts\n## Decisions\n## Assumptions\n"
            "## Constraints\n## Proposals\n## Do Not Store Here\n"
            "not the source of truth\n"
        )

    def _context(self) -> str:
        return (
            f"{DISCLOSURE_MD}\n# CONTEXT.md\n\n"
            "Temporary working context.\n"
            "Do not merge real working notes into main or master.\n"
        )

    def _makefile(self) -> str:
        return (
            f"{DISCLOSURE}\n"
            "HOST_GOOS := linux\n"
            "GOLANGCI_LINT_VERSION_FILE := .golangci-lint-version\n"
            "help:\n\t@echo help\n"
            "setup:\n\t@echo setup\n"
            "format:\n\t@echo format\n"
            "test:\n\t@echo test\n"
            "test-%:\n\t@echo test\n"
            "lint:\n\t@echo lint\n"
            "score:\n\tpython3 scripts/score_architecture.py\n"
            "score-gate:\n\tpython3 scripts/score_architecture.py --min-score 10\n"
            "check: lint test\n"
            "validate: check score-gate\n"
            "visual-smoke: scripts/visual_smoke.sh\n\t@echo smoke\n"
            "release: build-$(HOST_GOOS)\n"
            "build-linux:\n\t@echo linux\n"
            "build-darwin:\n\t@echo darwin\n"
            "build-windows:\n\t@echo windows\n"
            "clean:\n\t@echo clean\n"
            "clean-env:\n\t@echo clean-env\n"
        )

    def _score_tests_text(self) -> str:
        return (
            f"{DISCLOSURE}\n"
            "def test_current_repo_scores_cleanly(): pass\n"
            "def test_agents_line_limit_is_enforced(): pass\n"
            "def test_claude_symlink_requirement_is_enforced(): pass\n"
            "def test_secret_patterns_lower_score(): pass\n"
            "def test_clean_code_violations_lower_score(): pass\n"
            "def test_runtime_contract_rejects_changed_movement_constant(): pass\n"
            "def test_runtime_contract_rejects_missing_level_completion(): pass\n"
            "def test_ci_contract_requires_validation_gate(): pass\n"
        )

    def _game_source(self) -> str:
        return (
            "package game\n\n"
            "const (\n"
            "    tileSize = 16\n"
            "    updatesPerSecond = 60\n"
            "    playerSpeedPixelsPerSecond = 120.0\n"
            "    ghostSpeedPixelsPerSecond = 105.0\n"
            "    frightenedDurationUpdates = 120\n"
            "    alignmentThreshold = 4.0\n"
            ")\n"
            "type Game struct { levelComplete bool }\n"
            "func (g *Game) Update() error { return nil }\n"
            "func (g *Game) Draw(screen *ebiten.Image) {}\n"
            "func (g *Game) Layout(width, height int) (int, int) { return width, height }\n"
            "func drawNamePrompt() {}\n"
            "func drawLevelComplete() {}\n"
        )

    def _validation_workflow(self) -> str:
        return (
            f"{DISCLOSURE}\n"
            "permissions:\n  contents: read\n"
            "on:\n  pull_request:\n  push:\n  workflow_dispatch:\n"
            "# actions/checkout@v7 actions/setup-go@v6 golangci/golangci-lint-action@v9\n"
            "# make validate\n# make visual-smoke\n"
        )

    def _release_workflow(self) -> str:
        return (
            f"{DISCLOSURE}\n"
            "on:\n  push:\n    tags: ['v*']\n  workflow_dispatch:\n"
            "# ubuntu-24.04 macos-15-intel windows-2025\n"
            "# pacman-linux-amd64.tar.gz pacman-darwin-amd64.tar.gz pacman-windows-amd64.exe\n"
            "# actions/upload-artifact@v7\n"
        )

    def _visual_smoke_script(self) -> str:
        return (
            f"{DISCLOSURE}\n"
            "set -euo pipefail\n"
            "# xvfb-run xwininfo PACMAN_DISABLE_AUDIO PACMAN_CONFIG_DIR import 124\n"
        )

    def _clean_code(self) -> str:
        return f"{DISCLOSURE_MD}\n# Clean Code Guide\n\n## Required Explanations\n"

    def _review(self) -> str:
        return f"{DISCLOSURE_MD}\n# Review Guide\n\nDocumentation drift is a bug.\n"

    def _subagents(self) -> str:
        return (
            f"{DISCLOSURE_MD}\n# Subagents Guide\n\n"
            "Claude Task delegation.\n"
            "Codex spawn_agent delegation.\n"
            "parallelizable work.\n"
            "independent review.\n"
            "disjoint write scopes.\n"
        )

    def _create_pr(self) -> str:
        return (
            f"{DISCLOSURE_MD}\n# Create PR\n\n"
            "git status --short\nmake validate\nDo not push\nrisks\n"
        )


if __name__ == "__main__":
    unittest.main()
