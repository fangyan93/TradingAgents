# Codex research lab

This is a research-only layer that reuses TradingAgents' Yahoo Finance and
indicator data utilities while using the local Codex CLI for three separate
roles:

1. market research analyst;
2. adversarial bull/bear reviewer; and
3. research risk judge.

The original TradingAgents graph is not changed. This layer intentionally does
not connect to a broker, set position sizes, or create orders.

## Run

First create a point-in-time packet without using Codex:

```bash
.venv/bin/python -m trading_lab.run_research --as-of 2026-09-11 --dry-run
```

Run all three Codex roles only when you want to use Codex subscription usage:

```bash
.venv/bin/python -m trading_lab.run_research --as-of 2026-09-11
```

Each role runs `codex exec` with `--ephemeral` and `--sandbox read-only`.
`OPENAI_API_KEY` and `CODEX_API_KEY` are removed from the subprocess environment
so this workflow uses the saved ChatGPT/Codex login instead of API-key billing.

Results and cached data remain local in `trading_lab/runs/` and
`trading_lab/data_cache/`; both are ignored by Git.

For the architecture, report files, resuming an interrupted run, credential
choices, and the difference from the native API-key TradingAgents graph, see
[USING_THE_CODEX_LAYER.md](USING_THE_CODEX_LAYER.md).

Use [TRADING_JOURNAL_AND_RULEBOOK.md](TRADING_JOURNAL_AND_RULEBOOK.md) to
record rules before a position is opened and review it only after the position
is closed.
