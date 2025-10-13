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

This module removes the previous "lessons" feature. It ignores hidden
and common tool-cache directories when discovering immediate child
repositories (for example: .mypy_cache, .ruff_cache, __pycache__, .pyright).
The visitor writes an a-priori and a-posteriori file index, preserves the
extended toolchain flow, and now supports caching tool outputs to speed up
incremental reruns. Any tool failures are raised as AssertionError with the
captured stdout/stderr to make failures visible.
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

        # package root (the folder containing this module). Use this for
        # storing the canonical a-priori / a-posteriori index files so they
        # live with the visitor package rather than the workspace root.
        self.package_root = Path(__file__).resolve().parent

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

    def _ensure_index_file(self, path: Path, step_label: str) -> None:
        if path.exists() and path.stat().st_size > 0:
            return
        msg = f"{step_label} failed: {path} missing or empty"
        raise AssertionError(msg)

    def _log_discovery(self, label: str, repo_count: int) -> None:
        _info(label, f"found {repo_count} repositories under {self.root}")

    def _load_index(self, path: Path, index_name: str) -> dict[str, object]:
        try:
            with path.open("r", encoding="utf-8") as fh:
                raw_loaded = cast("object", json.load(fh))
        except Exception as exc:
            msg = f"unable to read {index_name} index"
            raise RuntimeError(msg) from exc

        if not isinstance(raw_loaded, dict):
            actual = raw_loaded.__class__.__name__
            msg = f"{index_name} index must be a mapping; got {actual}"
            raise TypeError(msg)

        return cast("dict[str, object]", raw_loaded)

    def _normalize_apriori_index(self, raw: dict[str, object]) -> dict[str, list[str]]:
        normalized: dict[str, list[str]] = {}
        for key, value in raw.items():
            key_str = str(key)
            if isinstance(value, list):
                items = cast("list[object]", value)
                normalized[key_str] = [item for item in items if isinstance(item, str)]
            else:
                normalized[key_str] = []
        return normalized

    def _validate_children_match(self, apriori: Mapping[str, list[str]]) -> None:
        expected = sorted(str(p.relative_to(self.root)) for p in self._child_dirs())
        actual = sorted(apriori.keys())
        if actual == expected:
            return
        _info("a-priori index expected:", expected)
        _info("a-priori index found:", actual)
        msg = "a-priori index contents do not match children"
        raise AssertionError(msg)

    def _prepare_posterior_data(self, raw: dict[str, object]) -> dict[str, object]:
        return {str(key): value for key, value in raw.items()}

    def _merge_tool_reports(self, data: dict[str, object]) -> None:
        for repo_name, report in self._tool_reports.items():
            tool_reports_value = report.get("tool_reports", {})
            if isinstance(tool_reports_value, dict):
                tool_reports = cast("dict[str, object]", tool_reports_value)
            else:
                tool_reports = {}

            files_index_value = report.get("files", [])
            if isinstance(files_index_value, list):
                raw_file_list = cast("list[object]", files_index_value)
                files_index = [item for item in raw_file_list if isinstance(item, str)]
            else:
                files_index = []

            existing = data.get(repo_name)
            if isinstance(existing, dict):
                existing_dict = cast("dict[str, object]", existing)
                raw_files = existing_dict.get("files", [])
                if isinstance(raw_files, list):
                    raw_list = cast("list[object]", raw_files)
                    files_value = [item for item in raw_list if isinstance(item, str)]
                else:
                    files_value = []
            elif isinstance(existing, list):
                existing_list = cast("list[object]", existing)
                files_value = [item for item in existing_list if isinstance(item, str)]
            else:
                files_value = []
            entry: dict[str, object] = {
                "files": files_value,
                "tool_reports": tool_reports,
                "files_index": files_index,
            }
            if repo_name not in data:
                entry.pop("files_index", None)
            data[repo_name] = entry

    def _write_failure_report(
        self,
        *,
        failure_path: Path,
        summary_path: Path,
        apriori_path: Path,
        posterior_path: Path,
    ) -> None:
        failure_payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "root": str(self.root),
            "had_failures": bool(self._last_run_failures),
            "total_failures": len(self._failure_details),
            "failures": self._failure_details,
            "summary_report_path": str(summary_path),
            "apriori_index_path": str(apriori_path),
            "posteriori_index_path": str(posterior_path),
            "tool_versions": self._tool_versions,
            "runtime_snapshot": self._runtime_snapshot,
        }
        if self._failure_messages:
            failure_payload["failure_messages"] = self._failure_messages
        self._atomic_write_json(failure_path, failure_payload)

    def _raise_on_failures(self, failure_report_path: Path) -> None:
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

        msg = f"toolchain failures detected; see {failure_report_path}"
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

    def inspect(self, json_name: str) -> list[str]:
        """Write an index of files present in each immediate child repo.

        Returns the list of repository names (relative paths) that were indexed.
        """
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
        index: dict[str, list[str]] = {}
        repo_names: list[str] = []
        for child in children:
            rel = str(child.relative_to(self.root))
            repo_names.append(rel)
            files: list[str] = []
            for p in child.rglob("*"):
                if not p.is_file():
                    continue
                if ".git" in p.parts or "__pycache__" in p.parts:
                    continue
                if p.suffix.lower() not in {".py", ".pyi"}:
                    continue
                files.append(str(p.relative_to(child).as_posix()))
            index[rel] = sorted(files)

        # store index files inside the visitor package directory
        out_path = self.package_root / json_name
        self._atomic_write_json(out_path, index)
        return repo_names

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
        """Run the inspect flow in four steps."""

        apriori_path = self.package_root / "x_index_a_a_priori_x.json"
        posterior_path = self.package_root / "x_index_b_a_posteriori_x.json"
        summary_path = self.package_root / "x_summary_report_x.json"
        failure_report_path = self.package_root / "x_tool_failures_x.json"

        apriori_repos = self.inspect("x_index_a_a_priori_x.json")
        self._ensure_index_file(apriori_path, "step1")
        self._log_discovery("apriori discovery:", len(apriori_repos))

        apriori_raw = self._load_index(apriori_path, "a-priori")
        apriori_index = self._normalize_apriori_index(apriori_raw)
        self._validate_children_match(apriori_index)

        self.body()

        posterior_repos = self.inspect("x_index_b_a_posteriori_x.json")
        self._ensure_index_file(posterior_path, "step3")
        self._log_discovery("a-posteriori discovery:", len(posterior_repos))

        posterior_raw = self._load_index(posterior_path, "a-posteriori")
        posterior_data = self._prepare_posterior_data(posterior_raw)
        self._merge_tool_reports(posterior_data)
        self._atomic_write_json(posterior_path, posterior_data)

        summary = self.generate_summary_report()
        self._atomic_write_json(summary_path, summary)

        self._write_failure_report(
            failure_path=failure_report_path,
            summary_path=summary_path,
            apriori_path=apriori_path,
            posterior_path=posterior_path,
        )

        self.cleanup()
        self._raise_on_failures(failure_report_path)


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

    _info(
        "wrote a-priori, a-posteriori, and summary files to:",
        inst.package_root,
    )

    summary_line = (
        f"processed {summary.get('total_repos', 0)} repositories "
        f"| cache hits: {hits}/{total} ({ratio:.1f}%)"
    )
    _info(summary_line)
