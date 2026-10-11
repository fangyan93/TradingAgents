"""CLI entry point for the Codex-backed, research-only QQQ/TQQQ workflow."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from .codex_runner import run_role
from .data_packet import collect_packet
from .prompts import analyst_prompt, reviewer_prompt, risk_judge_prompt


ROOT = Path(__file__).resolve().parent
SCHEMAS = ROOT / "schemas"


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _load_or_run(*, report_path: Path, prompt: str, schema_path: Path, run_dir: Path) -> dict:
    """Resume an interrupted research session without repeating completed roles."""
    if report_path.exists():
        loaded = json.loads(report_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            return loaded
        raise ValueError(f"Existing report is not a JSON object: {report_path}")
    result = run_role(prompt=prompt, schema_path=schema_path, workdir=run_dir)
    _write_json(report_path, result.payload)
    return result.payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the research-only Codex QQQ/TQQQ review workflow.")
    parser.add_argument("--as-of", default=date.today().isoformat(), help="Point-in-time market date (YYYY-MM-DD).")
    parser.add_argument("--dry-run", action="store_true", help="Collect and save the packet, but do not invoke Codex.")
    args = parser.parse_args()

    run_dir = ROOT / "runs" / args.as_of
    run_dir.mkdir(parents=True, exist_ok=True)
    packet = collect_packet(as_of=args.as_of, cache_dir=ROOT / "data_cache")
    _write_json(run_dir / "packet.json", packet)

    if args.dry_run:
        print(f"Saved point-in-time packet to {run_dir / 'packet.json'}; Codex was not invoked.")
        return

    analyst = _load_or_run(
        report_path=run_dir / "analyst.json",
        prompt=analyst_prompt(packet),
        schema_path=SCHEMAS / "analyst.json",
        run_dir=run_dir,
    )

    reviewer = _load_or_run(
        report_path=run_dir / "bull_bear_review.json",
        prompt=reviewer_prompt(packet, analyst),
        schema_path=SCHEMAS / "reviewer.json",
        run_dir=run_dir,
    )

    _load_or_run(
        report_path=run_dir / "risk_judgment.json",
        prompt=risk_judge_prompt(packet, analyst, reviewer),
        schema_path=SCHEMAS / "risk_judge.json",
        run_dir=run_dir,
    )
    print(f"Saved three research reports to {run_dir}. No orders were created.")


if __name__ == "__main__":
    main()
