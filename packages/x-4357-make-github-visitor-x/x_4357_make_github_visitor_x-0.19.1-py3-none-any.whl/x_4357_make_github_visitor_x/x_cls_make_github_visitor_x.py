from __future__ import annotations

import hashlib
import json
import logging as _logging
import os
import platform
import shutil
import subprocess
import sys
import time
from collections.abc import Mapping, MutableMapping, Sequence
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

_LOGGER = _logging.getLogger("x_make")


def _info(*args: object) -> None:
    msg = " ".join(str(a) for a in args)
    with suppress(Exception):
        _LOGGER.info("%s", msg)
    printed = False
    with suppress(Exception):
        print(msg)
        printed = True
    if not printed:
        with suppress(Exception):
            sys.stdout.write(msg + "\n")


"""Visitor to run ruff/black/mypy/pyright on immediate child git clones.

Hidden and cache directories (for example: .mypy_cache, .ruff_cache,
__pycache__, .pyright) are ignored when discovering child repositories.
The visitor caches tool outputs for unchanged repositories and now emits a
timestamped Markdown TODO report summarising any failures instead of the
legacy JSON index files. Failures still raise AssertionError with captured
stdout/stderr for visibility.
"""


COMMON_CACHE_NAMES = {
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    ".pyright",
    ".tool_cache",
}

GENERATED_BUILD_DIR_PREFIXES: tuple[str, ...] = ("_build_temp",)

TOOL_MODULE_MAP = {
    "ruff_fix": "ruff",
    "ruff_check": "ruff",
    "black": "black",
    "mypy": "mypy",
    "pyright": "pyright",
}

ToolResult = dict[str, object]
RepoReport = dict[str, object]
FAILURE_PREVIEW_LIMIT = 5
OUTPUT_PREVIEW_LIMIT = 5
VISIBLE_DIR_PREVIEW_LIMIT = 10
DEFAULT_TIMEOUT_SECONDS = 300
REQUIRED_PACKAGES: tuple[str, ...] = (
    "ruff",
    "black",
    "mypy",
    "pyright",
)
MARKDOWN_MESSAGE_LIMIT = 240
REPORTS_DIR_NAME = "reports"


@dataclass(frozen=True)
class ToolConfig:
    name: str
    command: list[str]
    skip_if_no_python: bool


@dataclass
class ToolOutcome:
    result: ToolResult
    failure_message: str | None = None
    failure_detail: dict[str, object] | None = None


@dataclass
class RepoProcessingResult:
    relative_name: str
    report: RepoReport
    failure_messages: list[str]
    failure_details: list[dict[str, object]]


@dataclass(frozen=True)
class RepoContext:
    path: Path
    rel_path: str
    repo_hash: str
    has_python: bool


def _coerce_exit_code(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _increment_counter(
    mapping: MutableMapping[str, object],
    key: str,
    delta: int = 1,
) -> None:
    current = mapping.get(key, 0)
    if isinstance(current, int):
        mapping[key] = current + delta
    else:
        mapping[key] = delta


def _preview_lines(lines: Sequence[str], limit: int) -> str:
    preview = "\n".join(lines[:limit])
    if len(lines) > limit:
        preview += "\n…"
    return preview


def _is_generated_build_dir(name: str) -> bool:
    return any(name.startswith(prefix) for prefix in GENERATED_BUILD_DIR_PREFIXES)


class x_cls_make_github_visitor_x:  # noqa: N801 - legacy naming retained for compatibility
    def __init__(
        self,
        root_dir: str | Path,
        *,
        output_filename: str = "repos_index.json",
        ctx: object | None = None,
        enable_cache: bool = True,
    ) -> None:
        """Initialize visitor.

        root_dir: path to a workspace that contains immediate child git clones.
        output_filename: unused for package-local index storage but kept for
        backwards compatibility.
        enable_cache: whether to reuse cached tool outputs when repositories are
        unchanged between runs.
        """
        self.root = Path(root_dir)
        if not self.root.exists() or not self.root.is_dir():
            msg = f"root path must exist and be a directory: {self.root}"
            raise AssertionError(msg)

        # The workspace root must not itself be a git repository (we operate
        # on immediate child clones).

        if (self.root / ".git").exists():
            msg = f"root path must not be a git repository: {self.root}"
            raise AssertionError(msg)

        self.output_filename = output_filename
        self._tool_reports: dict[str, RepoReport] = {}
        self._ctx = ctx
        self.enable_cache = enable_cache
        self._last_run_failures: bool = False
        self._failure_messages: list[str] = []
        self._failure_details: list[dict[str, object]] = []
        self._tool_versions: dict[str, str] = {}
        self._runtime_snapshot: dict[str, object] = {}
        self._last_report_path: Path | None = None

        # package root (the folder containing this module). Reports live here so
        # they remain alongside the visitor package rather than the workspace
        # root.
        self.package_root = Path(__file__).resolve().parent
        self._reports_dir = self.package_root / REPORTS_DIR_NAME

        self.cache_dir = self.package_root / ".tool_cache"
        if self.enable_cache:
            self.cache_dir.mkdir(exist_ok=True)

    def _child_dirs(self) -> list[Path]:
        """Return immediate child directories excluding hidden and cache dirs.

        Exclude names starting with '.' or '__' and common cache names to avoid
        treating tool caches as repositories.
        """
        out: list[Path] = []
        for p in self.root.iterdir():
            if not p.is_dir():
                continue
            name = p.name
            if name.startswith((".", "__")):
                # hidden or dunder directories (including caches)
                continue
            if name in COMMON_CACHE_NAMES:
                continue
            # Only include directories that look like git clones (contain .git)
            if not (p / ".git").exists():
                # skip non-repo helper folders
                continue
            out.append(p)
        return sorted(out)

    def _atomic_write_json(self, path: Path, data: object) -> None:
        tmp = path.with_name(path.name + ".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=4, sort_keys=True)
            fh.flush()
            with suppress(OSError):
                os.fsync(fh.fileno())
        tmp.replace(path)

    @staticmethod
    def _ensure_text(value: object) -> str:
        def decode_bytes(raw: bytes) -> str:
            try:
                return raw.decode("utf-8")
            except UnicodeDecodeError:  # pragma: no cover - diagnostic fallback
                return raw.decode("utf-8", "replace")

        if isinstance(value, str):
            return value

        if isinstance(value, (bytes, bytearray)):
            return decode_bytes(bytes(value))

        if isinstance(value, memoryview):
            return decode_bytes(value.tobytes())

        if value is None:
            return ""
        return str(value)

    def _cleanup_generated_build_dirs(self, repo_path: Path) -> None:
        with suppress(OSError):
            for child in repo_path.iterdir():
                if not child.is_dir():
                    continue
                if not _is_generated_build_dir(child.name):
                    continue
                _info("Removing generated build directory:", str(child))
                shutil.rmtree(child, ignore_errors=True)

    def _repo_content_hash(self, repo_path: Path) -> str:
        """Return a deterministic hash of repository contents for caching."""
        hasher = hashlib.sha256()
        for p in sorted(repo_path.rglob("*")):
            if not p.is_file():

                continue
            if ".git" in p.parts or "__pycache__" in p.parts:
                continue
            if any(_is_generated_build_dir(part) for part in p.parts):
                continue
            if p.suffix in {".pyc", ".pyo"}:
                continue
            rel = p.relative_to(repo_path).as_posix().encode("utf-8")
            hasher.update(rel)
            try:
                hasher.update(p.read_bytes())
            except OSError:
                # Skip unreadable files without failing the whole hash
                continue
        return hasher.hexdigest()

    def _cache_path(self, repo_name: str, tool_name: str, repo_hash: str) -> Path:
        key = f"{repo_name}_{tool_name}_{repo_hash[:16]}"
        return self.cache_dir / f"{key}.json"

    def _prepare_environment(self, python: str, packages: Sequence[str]) -> None:
        proc = subprocess.run(  # noqa: S603
            [python, "-m", "pip", "install", "--upgrade", *packages],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            msg = f"failed to install required packages: {proc.stdout}\n{proc.stderr}"
            raise AssertionError(msg)

        self._tool_versions = self._collect_tool_versions(python)
        self._runtime_snapshot = {
            "python_executable": python,
            "python_version": sys.version.replace("\n", " "),
            "platform": platform.platform(),
            "run_started_at": datetime.now(UTC).isoformat(),
            "workspace_root": str(self.root),
        }

        env_snapshot = {
            key: os.environ.get(key)
            for key in ("PATH", "PYTHONPATH", "VIRTUAL_ENV")
            if os.environ.get(key)
        }
        if env_snapshot:
            self._runtime_snapshot["environment"] = env_snapshot

        self._prune_cache()

    def _tool_configurations(self, python: str) -> list[ToolConfig]:
        return [
            ToolConfig(
                name="ruff_fix",
                command=[
                    python,
                    "-m",
                    "ruff",
                    "check",
                    ".",
                    "--fix",
                    "--select",
                    "ALL",
                    "--ignore",
                    "D,COM812,ISC001,T20",
                    "--line-length",
                    "88",
                    "--target-version",
                    "py311",
                ],
                skip_if_no_python=False,
            ),
            ToolConfig(
                name="black",
                command=[
                    python,
                    "-m",
                    "black",
                    ".",
                    "--line-length",
                    "88",
                    "--target-version",
                    "py311",
                    "--check",
                    "--diff",
                ],
                skip_if_no_python=True,
            ),
            ToolConfig(
                name="ruff_check",
                command=[
                    python,
                    "-m",
                    "ruff",
                    "check",
                    ".",
                    "--select",
                    "ALL",
                    "--ignore",
                    "D,COM812,ISC001,T20",
                    "--line-length",
                    "88",
                    "--target-version",
                    "py311",
                ],
                skip_if_no_python=False,
            ),
            ToolConfig(
                name="mypy",
                command=[
                    python,
                    "-m",
                    "mypy",
                    ".",
                    "--strict",
                    "--no-warn-unused-configs",
                    "--show-error-codes",
                    "--warn-return-any",
                    "--warn-unreachable",
                    "--disallow-any-unimported",
                    "--disallow-any-expr",
                    "--disallow-any-decorated",
                    "--disallow-any-explicit",
                ],
                skip_if_no_python=True,
            ),
            ToolConfig(
                name="pyright",
                command=[
                    python,
                    "-m",
                    "pyright",
                    ".",
                    "--level",
                    "error",
                ],
                skip_if_no_python=True,
            ),
        ]

    def _collect_repo_files(self, repo_path: Path) -> list[str]:
        files: list[str] = []
        for pth in repo_path.rglob("*"):
            if not pth.is_file():
                continue
            if ".git" in pth.parts or "__pycache__" in pth.parts:
                continue
            if any(_is_generated_build_dir(part) for part in pth.parts):
                continue
            if pth.suffix.lower() not in {".py", ".pyi"}:
                continue
            files.append(str(pth.relative_to(repo_path).as_posix()))
        return sorted(files)

    def _process_repository(
        self,
        repo_path: Path,
        python: str,
        timeout: int,
    ) -> RepoProcessingResult:
        self._cleanup_generated_build_dirs(repo_path)
        rel = str(repo_path.relative_to(self.root))
        repo_hash = self._repo_content_hash(repo_path)
        repo_files = self._collect_repo_files(repo_path)
        repo_context = RepoContext(
            path=repo_path,
            rel_path=rel,
            repo_hash=repo_hash,
            has_python=bool(repo_files),
        )

        tool_reports: dict[str, ToolResult] = {}
        failure_messages: list[str] = []
        failure_details: list[dict[str, object]] = []

        configs = self._tool_configurations(python)
        for config in configs:
            outcome = self._run_tool_for_repo(
                repo=repo_context,
                config=config,
                timeout=timeout,
            )
            tool_reports[config.name] = outcome.result
            if outcome.failure_message:
                failure_messages.append(outcome.failure_message)
            if outcome.failure_detail:
                failure_details.append(outcome.failure_detail)

        repo_report: RepoReport = {
            "timestamp": datetime.now(UTC).isoformat(),
            "repo_hash": repo_context.repo_hash,
            "tool_reports": tool_reports,
            "files": repo_files,
        }

        return RepoProcessingResult(
            relative_name=repo_context.rel_path,
            report=repo_report,
            failure_messages=failure_messages,
            failure_details=failure_details,
        )

    def _build_skip_outcome(
        self,
        *,
        repo: RepoContext,
        config: ToolConfig,
        tool_version: str,
        module_name: str,
    ) -> ToolOutcome:
        now_iso = datetime.now(UTC).isoformat()
        skip_result: ToolResult = {
            "exit": 0,
            "stdout": "",
            "stderr": "skipped - no Python source (.py/.pyi) found",
            "cached": False,
            "skipped": True,
            "skip_reason": "no_python_files",
            "cmd": list(config.command),
            "cmd_display": " ".join(str(part) for part in config.command),
            "cwd": str(repo.path),
            "started_at": now_iso,
            "ended_at": now_iso,
            "duration_seconds": 0.0,
            "repo_hash": repo.repo_hash,
            "tool_version": tool_version,
            "tool_module": module_name,
        }
        return ToolOutcome(skip_result)

    def _load_cached_outcome(
        self,
        *,
        repo: RepoContext,
        config: ToolConfig,
        tool_version: str,
        module_name: str,
    ) -> ToolOutcome | None:
        cached = self._load_cache(repo.rel_path, config.name, repo.repo_hash)
        if cached is None:
            return None
        cached_result: ToolResult = dict(cached)
        cached_result["cached"] = True
        cached_result.setdefault("cmd", list(config.command))
        cached_result.setdefault(
            "cmd_display",
            " ".join(str(part) for part in config.command),
        )
        cached_result.setdefault("cwd", str(repo.path))
        cached_result.setdefault("repo_hash", repo.repo_hash)
        cached_result.setdefault("tool_version", tool_version)
        cached_result.setdefault("tool_module", module_name)
        cached_result.setdefault("started_at", "")
        cached_result.setdefault("ended_at", "")
        cached_result.setdefault("duration_seconds", 0.0)
        _info(f"{config.name}: cache hit for {repo.rel_path}")
        return ToolOutcome(cached_result)

    def _run_tool_for_repo(
        self,
        *,
        repo: RepoContext,
        config: ToolConfig,
        timeout: int,
    ) -> ToolOutcome:
        module_name = TOOL_MODULE_MAP.get(config.name, config.name)
        tool_version = self._tool_versions.get(module_name, "<unknown>")

        if config.skip_if_no_python and not repo.has_python:
            _info(f"{config.name}: skipped (no Python files) in {repo.rel_path}")
            return self._build_skip_outcome(
                repo=repo,
                config=config,
                tool_version=tool_version,
                module_name=module_name,
            )

        cached_outcome = self._load_cached_outcome(
            repo=repo,
            config=config,
            tool_version=tool_version,
            module_name=module_name,
        )
        if cached_outcome is not None:
            return cached_outcome

        start_wall = datetime.now(UTC)
        start_perf = time.perf_counter()
        timed_out = False
        exit_code: int | None
        stdout_obj: object
        stderr_obj: object

        try:
            completed = subprocess.run(  # noqa: S603
                config.command,
                check=False,
                cwd=str(repo.path),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            exit_code = completed.returncode
            stdout_obj = completed.stdout
            stderr_obj = completed.stderr
        except subprocess.TimeoutExpired as exc:  # pragma: no cover - diag path
            timed_out = True
            exit_code = None
            stdout_output = cast("object | None", exc.output)
            stderr_output = cast("object | None", exc.stderr)
            stdout_obj = stdout_output if stdout_output is not None else ""
            stderr_obj = stderr_output if stderr_output is not None else ""

        end_wall = datetime.now(UTC)
        duration = max(time.perf_counter() - start_perf, 0.0)

        proc_stdout = self._ensure_text(stdout_obj)
        proc_stderr = self._ensure_text(stderr_obj)

        result: ToolResult = {
            "exit": exit_code,
            "stdout": proc_stdout,
            "stderr": proc_stderr,
            "cached": False,
            "cmd": list(config.command),
            "cmd_display": " ".join(str(part) for part in config.command),
            "cwd": str(repo.path),
            "started_at": start_wall.isoformat(),
            "ended_at": end_wall.isoformat(),
            "duration_seconds": duration,
            "repo_hash": repo.repo_hash,
            "tool_version": tool_version,
            "tool_module": module_name,
        }
        if timed_out:
            result["timed_out"] = True
            result["timeout_seconds"] = timeout

        failure_condition = timed_out or exit_code is None or exit_code != 0
        if failure_condition:
            self._delete_cache(repo.rel_path, config.name, repo.repo_hash)
            message, detail = self._build_failure_payload(
                repo=repo,
                config=config,
                timed_out=timed_out,
                result=result,
            )
            _info(
                f"{config.name}: failure in {repo.rel_path};",
                "details captured",
            )
            return ToolOutcome(result, message, detail)

        self._store_cache(repo.rel_path, config.name, repo.repo_hash, result)
        return ToolOutcome(result)

    def _build_failure_payload(
        self,
        *,
        repo: RepoContext,
        config: ToolConfig,
        timed_out: bool,
        result: ToolResult,
    ) -> tuple[str, dict[str, object]]:
        stdout_text = self._ensure_text(result.get("stdout", ""))
        stderr_text = self._ensure_text(result.get("stderr", ""))
        truncated_stdout = stdout_text.strip().splitlines()
        truncated_stderr = stderr_text.strip().splitlines()
        preview_stdout = _preview_lines(truncated_stdout, OUTPUT_PREVIEW_LIMIT)
        preview_stderr = _preview_lines(truncated_stderr, OUTPUT_PREVIEW_LIMIT)
        exit_code = _coerce_exit_code(result.get("exit"))
        exit_display = "timeout" if timed_out else f"exit {exit_code}"
        duration_value = result.get("duration_seconds", 0.0)
        if isinstance(duration_value, (int, float)):
            duration = float(duration_value)
        else:
            duration = 0.0
        tool_version = self._ensure_text(result.get("tool_version", "<unknown>"))
        cmd_display = self._ensure_text(result.get("cmd_display", ""))
        started_at = self._ensure_text(result.get("started_at", ""))
        failure_message_lines = [
            f"{config.name} failed for {repo.rel_path} ({exit_display})",
            f"cwd: {repo.path}",
            f"command: {cmd_display}",
            f"started_at: {started_at}",
            f"duration: {duration:.3f}s",
            f"tool_version: {tool_version}",
            f"stdout:\n{preview_stdout or '<empty>'}",
            f"stderr:\n{preview_stderr or '<empty>'}",
        ]
        failure_message = "\n".join(failure_message_lines)
        failure_detail: dict[str, object] = {
            "repo": repo.rel_path,
            "repo_path": str(repo.path),
            "tool": config.name,
            "tool_module": self._ensure_text(result.get("tool_module", config.name)),
        }
        failure_detail.update(result)
        return failure_message, failure_detail

    def _ensure_reports_dir(self) -> Path:
        reports_dir = self._reports_dir
        reports_dir.mkdir(parents=True, exist_ok=True)
        return reports_dir

    def _remove_legacy_json_reports(self) -> None:
        legacy_names = (
            "x_index_a_a_priori_x.json",
            "x_index_b_a_posteriori_x.json",
            "x_summary_report_x.json",
            "x_tool_failures_x.json",
        )
        for name in legacy_names:
            stale_path = self.package_root / name
            with suppress(OSError):
                if stale_path.exists():
                    stale_path.unlink()

    def _summarize_failure_message(self, message: str) -> str:
        collapsed = " ".join(message.strip().split())
        if not collapsed:
            return "Tool failure recorded"
        if len(collapsed) <= MARKDOWN_MESSAGE_LIMIT:
            return collapsed
        return collapsed[: MARKDOWN_MESSAGE_LIMIT - 1] + "…"

    def _command_display(self, detail: Mapping[str, object]) -> str:
        cmd_display = detail.get("cmd_display")
        if isinstance(cmd_display, str) and cmd_display.strip():
            return cmd_display.strip()
        raw_cmd = detail.get("cmd")
        if isinstance(raw_cmd, Sequence) and not isinstance(
            raw_cmd,
            (str, bytes, bytearray),
        ):
            parts_seq = cast("Sequence[object]", raw_cmd)
            parts = [str(part) for part in parts_seq]
            if parts:
                return " ".join(parts)
        return "<command unavailable>"

    def _ensure_detail_text(self, detail: Mapping[str, object], key: str) -> str:
        value = detail.get(key)
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        return str(value)

    def _detail_value(
        self,
        detail: Mapping[str, object],
        *keys: str,
        default: str = "",
    ) -> str:
        for key in keys:
            value = self._ensure_detail_text(detail, key)
            if value:
                return value
        return default

    def _stat_value(self, mapping: Mapping[str, object], key: str) -> int:
        value = mapping.get(key)
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            with suppress(ValueError):
                return int(value)
        return 0

    def _write_markdown_failure_report(self) -> Path:
        reports_dir = self._ensure_reports_dir()
        now = datetime.now(UTC)
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"visitor_failures_{timestamp}.md"
        report_path = reports_dir / filename

        summary = self.generate_summary_report()
        overall = summary.get("overall_stats", {})
        typed_overall: Mapping[str, object]
        if isinstance(overall, Mapping):
            typed_overall = cast("Mapping[str, object]", overall)
        else:
            typed_overall = cast("Mapping[str, object]", {})

        detail_pairs = list(
            zip(self._failure_details, self._failure_messages, strict=False)
        )

        lines = self._report_header_lines(now, summary, typed_overall)
        lines.extend(self._failure_section_lines(detail_pairs))
        lines.extend(self._report_footer_lines())

        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self._last_report_path = report_path
        return report_path

    def _report_header_lines(
        self,
        now: datetime,
        summary: Mapping[str, object],
        overall: Mapping[str, object],
    ) -> list[str]:
        lines = [f"# Visitor Failure Report — {now.isoformat()}", ""]
        lines.append(f"- Workspace root: `{self.root}`")
        run_started = self._runtime_snapshot.get("run_started_at", "")
        if run_started:
            lines.append(f"- Run started at: {run_started}")
        run_finished = self._runtime_snapshot.get("run_completed_at", "")
        if run_finished:
            lines.append(f"- Run completed at: {run_finished}")
        lines.append(f"- Total repositories examined: {summary.get('total_repos', 0)}")
        total_tools = self._stat_value(overall, "total_tools_run")
        lines.append(f"- Total tool executions: {total_tools}")
        failed_tools = self._stat_value(overall, "failed_tools")
        lines.append(f"- Failing tool executions: {failed_tools}")
        cache_hits = self._stat_value(overall, "cache_hits")
        lines.append(f"- Cache hits: {cache_hits}")
        lines.extend(["", "## Failures", ""])
        return lines

    def _failure_section_lines(
        self,
        detail_pairs: Sequence[tuple[Mapping[str, object], str]],
    ) -> list[str]:
        if not detail_pairs:
            return ["- [x] No failures detected — all tools passed", ""]

        lines: list[str] = []
        for detail, message in detail_pairs:
            lines.extend(self._render_failure(detail, message))
        return lines

    def _render_failure(
        self,
        detail: Mapping[str, object],
        message: str,
    ) -> list[str]:
        repo = self._detail_value(detail, "repo", "repo_path", default="<unknown repo>")
        tool = self._detail_value(
            detail,
            "tool",
            "tool_module",
            default="<unknown tool>",
        )
        preview = self._summarize_failure_message(message)
        lines = [f"- [ ] `{repo}` · `{tool}` — {preview}"]

        command_display = self._command_display(detail)
        exit_display = self._exit_display(detail)
        repo_path = self._detail_value(detail, "repo_path", "cwd")
        suggestion = self._detail_value(
            detail,
            "next_action",
            default="Investigate",
        )
        captured_at = self._detail_value(detail, "ended_at", "started_at")
        tool_version = self._detail_value(detail, "tool_version")
        stdout_preview = self._preview_output(detail, "stdout")
        stderr_preview = self._preview_output(detail, "stderr")

        lines.extend(
            [
                f"  - Command: `{command_display}`",
                f"  - Exit: {exit_display}",
            ]
        )
        if repo_path:
            lines.append(f"  - Repo path: `{repo_path}`")
        if tool_version:
            lines.append(f"  - Tool version: {tool_version}")
        if captured_at:
            lines.append(f"  - Captured at: {captured_at}")
        lines.append(f"  - Suggested action: {suggestion}")
        if stdout_preview:
            lines.extend(self._render_output_preview("Stdout", stdout_preview))
        if stderr_preview:
            lines.extend(self._render_output_preview("Stderr", stderr_preview))
        lines.append("")
        return lines

    def _exit_display(self, detail: Mapping[str, object]) -> str:
        if detail.get("timed_out"):
            timeout = self._detail_value(detail, "timeout_seconds")
            return f"timeout after {timeout}s" if timeout else "timeout"

        exit_code = _coerce_exit_code(detail.get("exit"))
        if exit_code is None:
            return "exit <unknown>"
        return f"exit {exit_code}"

    def _preview_output(self, detail: Mapping[str, object], key: str) -> str:
        text = self._ensure_text(detail.get(key, ""))
        return _preview_lines(text.splitlines(), OUTPUT_PREVIEW_LIMIT)

    def _render_output_preview(self, label: str, preview: str) -> list[str]:
        header = f"  - {label} preview:"
        lines = [header]
        lines.extend(f"    > {line}" for line in preview.splitlines())
        return lines

    def _report_footer_lines(self) -> list[str]:
        return [
            "---",
            "",
            (
                "_Generated by x_make_github_visitor_x_; actionable items are "
                "tracked as unchecked tasks._"
            ),
        ]

    def _raise_on_failures(self, report_path: Path | None) -> None:
        if not self._last_run_failures:
            return
        msgs = self._failure_messages[:]
        if not msgs:
            msgs = ["tool failures occurred but no messages were captured"]

        preview_chunks = msgs[:FAILURE_PREVIEW_LIMIT]
        preview = "\n\n".join(preview_chunks)
        _info("toolchain failure preview:")
        if preview:
            for block in preview.split("\n\n"):
                _info(block)
        if len(msgs) > FAILURE_PREVIEW_LIMIT:
            _info("…additional failures omitted…")

        if report_path is not None:
            msg = f"toolchain failures detected; see {report_path}"
        else:
            msg = "toolchain failures detected; markdown report path unavailable"
        raise AssertionError(msg)

    def _load_cache(
        self,
        repo_name: str,
        tool_name: str,
        repo_hash: str,
    ) -> ToolResult | None:
        if not self.enable_cache:
            return None
        cache_file = self._cache_path(repo_name, tool_name, repo_hash)
        if not cache_file.exists():
            return None
        try:
            with cache_file.open("r", encoding="utf-8") as fh:
                cached = cast("ToolResult", json.load(fh))
        except (OSError, json.JSONDecodeError):
            with suppress(OSError):
                cache_file.unlink()
            return None
        exit_value = cached.get("exit", 0)
        exit_code: int | None
        if isinstance(exit_value, int):
            exit_code = exit_value
        elif isinstance(exit_value, str):
            try:
                exit_code = int(exit_value)
            except ValueError:
                exit_code = None
        else:
            exit_code = None
        if exit_code not in (None, 0):
            self._delete_cache(repo_name, tool_name, repo_hash)
            return None
        return cached

    def _store_cache(
        self,
        repo_name: str,
        tool_name: str,
        repo_hash: str,
        payload: ToolResult,
    ) -> None:
        if not self.enable_cache:
            return
        cache_file = self._cache_path(repo_name, tool_name, repo_hash)
        with suppress(OSError):
            self._atomic_write_json(cache_file, payload)

    def _delete_cache(
        self,
        repo_name: str,
        tool_name: str,
        repo_hash: str,
    ) -> None:
        if not self.enable_cache:
            return
        cache_file = self._cache_path(repo_name, tool_name, repo_hash)
        with suppress(OSError):
            cache_file.unlink()

    def _prune_cache(self, keep: int = 500) -> None:
        if not self.enable_cache or not self.cache_dir.exists():
            return
        try:
            candidate_files = list(self.cache_dir.glob("*.json"))
        except OSError:
            return

        def _file_mtime(path: Path) -> float:
            try:
                return path.stat().st_mtime
            except OSError:
                return 0.0

        cache_files = sorted(candidate_files, key=_file_mtime)
        overflow = len(cache_files) - keep
        if overflow <= 0:
            return
        for stale in cache_files[:overflow]:
            with suppress(OSError):
                stale.unlink()

    def _collect_tool_versions(self, python: str) -> dict[str, str]:
        versions: dict[str, str] = {}
        for module in sorted({*TOOL_MODULE_MAP.values()}):
            try:
                proc = subprocess.run(  # noqa: S603
                    [python, "-m", module, "--version"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            except (
                OSError,
                subprocess.TimeoutExpired,
                subprocess.SubprocessError,
            ) as exc:  # pragma: no cover - diagnostics only
                versions[module] = f"<error invoking --version: {exc}>"
                continue
            output = (proc.stdout or proc.stderr).strip()
            if proc.returncode != 0:
                versions[module] = f"<exit {proc.returncode}> {output}"
            else:
                versions[module] = output or "<no output>"
        return versions

    def body(self) -> None:
        """Run ruff/black/mypy/pyright against each child repository."""

        python = sys.executable
        self._prepare_environment(python, REQUIRED_PACKAGES)

        reports: dict[str, RepoReport] = {}
        failure_messages: list[str] = []
        failure_details: list[dict[str, object]] = []

        for child in self._child_dirs():
            result = self._process_repository(
                child,
                python,
                DEFAULT_TIMEOUT_SECONDS,
            )
            reports[result.relative_name] = result.report
            failure_messages.extend(result.failure_messages)
            failure_details.extend(result.failure_details)

        self._tool_reports = reports
        self._last_run_failures = bool(failure_messages)
        self._failure_messages = failure_messages
        self._failure_details = failure_details
        self._runtime_snapshot["run_completed_at"] = datetime.now(UTC).isoformat()

    def cleanup(self) -> None:
        """Placeholder for cleanup. Override if needed."""
        return

    def generate_summary_report(self) -> dict[str, object]:
        """Produce an aggregate summary of the most recent tool run."""
        overall_stats: dict[str, object] = {
            "cache_hits": 0,
            "cache_misses": 0,
            "failed_tools": 0,
            "total_tools_run": 0,
            "had_failures": bool(self._last_run_failures),
        }
        repos_section: dict[str, dict[str, object]] = {}
        summary: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "total_repos": len(self._tool_reports),
            "overall_stats": overall_stats,
            "repos": repos_section,
        }
        for repo_name, report in self._tool_reports.items():
            tools_summary: dict[str, dict[str, object]] = {}
            repo_summary: dict[str, object] = {
                "repo_hash": report.get("repo_hash"),
                "tools": tools_summary,
                "cached": 0,
                "failed": 0,
            }
            raw_tools = report.get("tool_reports")
            tool_map: dict[str, ToolResult]
            if isinstance(raw_tools, dict):
                tool_map = cast("dict[str, ToolResult]", raw_tools)
            else:
                tool_map = {}
            for tool_name, tool_report in tool_map.items():
                exit_code = _coerce_exit_code(tool_report.get("exit"))
                cached_flag = bool(tool_report.get("cached", False))
                timed_out_flag = bool(tool_report.get("timed_out", False))
                tools_summary[tool_name] = {
                    "exit": exit_code,
                    "cached": cached_flag,
                    "timed_out": timed_out_flag,
                }
                _increment_counter(overall_stats, "total_tools_run")
                if cached_flag:
                    _increment_counter(repo_summary, "cached")
                    _increment_counter(overall_stats, "cache_hits")
                else:
                    _increment_counter(overall_stats, "cache_misses")
                if timed_out_flag or exit_code not in (None, 0):
                    _increment_counter(repo_summary, "failed")
                    _increment_counter(overall_stats, "failed_tools")
            repos_section[repo_name] = repo_summary
        return summary

    def run_inspect_flow(self) -> None:
        """Run discovery, execute tools, and emit a markdown TODO report."""

        children = self._child_dirs()
        if not children:
            try:
                entries = sorted(p.name for p in self.root.iterdir() if p.is_dir())
            except OSError:
                entries = []
            preview = ", ".join(entries[:VISIBLE_DIR_PREVIEW_LIMIT])
            suffix = "" if len(entries) <= VISIBLE_DIR_PREVIEW_LIMIT else " …"
            msg = (
                "no child git repositories found"
                f" under {self.root} (visible dirs: {preview}{suffix})"
            )
            raise AssertionError(msg)

        repo_names = [str(child.relative_to(self.root)) for child in children]
        self._runtime_snapshot["discovered_repositories"] = repo_names
        _info(
            "visitor discovery:",
            f"found {len(repo_names)} repositories under {self.root}",
        )

        self._remove_legacy_json_reports()
        self.body()
        report_path = self._write_markdown_failure_report()
        self.cleanup()
        self._raise_on_failures(report_path)

    @property
    def last_report_path(self) -> Path | None:
        return self._last_report_path


def _workspace_root() -> str:
    here = Path(__file__).resolve()
    for anc in here.parents:
        if (anc / ".git").exists():  # repo root
            return str(anc.parent)
    # Fallback: two levels up
    return str(here.parent.parent)


def init_name(
    root_dir: str | Path,
    *,
    output_filename: str | None = None,
    ctx: object | None = None,
    enable_cache: bool = True,
) -> x_cls_make_github_visitor_x:
    if output_filename is None:
        return x_cls_make_github_visitor_x(
            root_dir,
            ctx=ctx,
            enable_cache=enable_cache,
        )
    return x_cls_make_github_visitor_x(
        root_dir,
        output_filename=output_filename,
        ctx=ctx,
        enable_cache=enable_cache,
    )


def init_main(
    ctx: object | None = None,
    *,
    enable_cache: bool = True,
) -> x_cls_make_github_visitor_x:
    """Initialize the visitor using dynamic workspace root (parent of this repo)."""
    return init_name(_workspace_root(), ctx=ctx, enable_cache=enable_cache)


if __name__ == "__main__":
    inst = init_main()
    inst.run_inspect_flow()
    summary = inst.generate_summary_report()
    overall_raw = summary.get("overall_stats", {})
    overall: Mapping[str, object]
    if isinstance(overall_raw, Mapping):
        overall = cast("Mapping[str, object]", overall_raw)
    else:
        overall = {}

    hits = _coerce_exit_code(overall.get("cache_hits", 0)) or 0
    total = _coerce_exit_code(overall.get("total_tools_run", 0)) or 0
    ratio = (hits / total * 100.0) if total else 0.0

    report_path = inst.last_report_path
    if report_path is not None:
        _info("visitor markdown report saved to:", report_path)
    else:
        _info("visitor markdown report path unavailable")

    summary_line = (
        f"processed {summary.get('total_repos', 0)} repositories "
        f"| cache hits: {hits}/{total} ({ratio:.1f}%)"
    )
    _info(summary_line)
