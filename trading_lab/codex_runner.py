"""Run a bounded Codex research role using the local ChatGPT/Codex login."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class CodexRunError(RuntimeError):
    """Raised when Codex cannot produce the required final response."""


@dataclass(frozen=True)
class CodexResult:
    """A role response, preserved both as parsed JSON and raw text."""

    payload: dict[str, Any]
    raw_text: str


def _parse_json(text: str) -> dict[str, Any]:
    """Parse a Codex response while tolerating an accidental Markdown fence."""
    candidate = text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if len(lines) >= 3 and lines[-1].strip().startswith("```"):
            candidate = "\n".join(lines[1:-1]).strip()
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise CodexRunError("Codex returned non-JSON output despite the output schema.") from exc
    if not isinstance(parsed, dict):
        raise CodexRunError("Codex returned JSON that was not an object.")
    return parsed


def run_role(
    *,
    prompt: str,
    schema_path: Path,
    workdir: Path,
    timeout_seconds: int = 300,
) -> CodexResult:
    """Run one read-only, ephemeral Codex role.

    The API-key environment variables are deliberately removed so this path
    uses the user's cached ChatGPT/Codex login rather than API billing.
    """
    output_path = workdir / f"{schema_path.stem}.response.json"
    environment = os.environ.copy()
    environment.pop("OPENAI_API_KEY", None)
    environment.pop("CODEX_API_KEY", None)

    command = [
        "codex",
        "exec",
        "--ephemeral",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "-C",
        str(workdir),
        "--output-schema",
        str(schema_path),
        "--output-last-message",
        str(output_path),
        prompt,
    ]
    completed = subprocess.run(
        command,
        cwd=workdir,
        env=environment,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise CodexRunError(f"Codex role failed (exit {completed.returncode}): {detail}")
    if not output_path.exists():
        raise CodexRunError("Codex completed without writing its final response.")

    raw_text = output_path.read_text(encoding="utf-8")
    return CodexResult(payload=_parse_json(raw_text), raw_text=raw_text)
