# Using the Codex research layer

## Purpose

`trading_lab` is a small, local, research-only workflow added beside the
upstream TradingAgents project. It was designed for studying QQQ and TQQQ
without connecting a broker, placing orders, choosing position sizes, or
generating a trade instruction.

It reuses the project's public-market-data and indicator utilities, but it
does **not** run the upstream `TradingAgentsGraph`. Instead, it gives a compact
point-in-time data packet to three independent Codex roles:

1. **Analyst** — describes technical context and uncertainty.
2. **Bull/bear reviewer** — challenges the analyst case and states what would
   distinguish the competing interpretations.
3. **Risk judge** — checks whether there is enough evidence for the research
   stance and highlights missing information.

The result is intentionally an auditable set of separate reports, not an
automated recommendation.

## How it works

```text
Yahoo Finance data
       |
TradingAgents data/indicator utilities
       |
packet.json (QQQ and TQQQ, as-of one market date)
       |
       +--> Codex analyst --------> analyst.json
       |
       +--> Codex bull/bear review -> bull_bear_review.json
       |
       +--> Codex risk judge ------> risk_judgment.json
```

Each later role receives the prior report as context. The roles are separate
`codex exec` runs, each constrained to a read-only sandbox and a JSON output
schema. That schema makes the output stable enough to read, compare, or later
turn into a journal/dashboard.

## Files to know

| Path | Role |
| --- | --- |
| `trading_lab/run_research.py` | The command-line entry point and sequence of the three roles. |
| `trading_lab/data_packet.py` | Fetches point-in-time QQQ/TQQQ OHLCV data and computes indicators. |
| `trading_lab/prompts.py` | The research-only instructions given to each role. |
| `trading_lab/schemas/` | Required JSON structure for each report. |
| `trading_lab/codex_runner.py` | Runs Codex safely and saves/parses each final response. |
| `trading_lab/runs/YYYY-MM-DD/` | Your local, dated research packet and reports. Git ignores this directory. |
| `trading_lab/data_cache/` | Local market-data cache. Git ignores this directory. |

The small malformed-cache cleanup in `data_packet.py` is intentional: a failed
Yahoo download can leave an unusable cache CSV. The cleanup removes only that
invalid file in `trading_lab/data_cache/`, then allows a later download retry.

## Run it in a future session

From the repository root:

```bash
.venv/bin/python -m trading_lab.run_research --as-of 2026-09-11 --dry-run
```

Use `--dry-run` first when you want to validate market-data collection. It
creates only `packet.json`; it does not call Codex or consume Codex usage.

When that works, run the full research sequence:

```bash
.venv/bin/python -m trading_lab.run_research --as-of 2026-09-11
```

Use the date you want to study in `YYYY-MM-DD` form. The date is the latest
data boundary: on a weekend or market holiday, the packet uses the most recent
available trading day on or before it.

At the end, open these files:

```text
trading_lab/runs/2026-09-11/packet.json
trading_lab/runs/2026-09-11/analyst.json
trading_lab/runs/2026-09-11/bull_bear_review.json
trading_lab/runs/2026-09-11/risk_judgment.json
```

The command is resume-safe. If it stops after completing one or two roles,
rerun the identical command. Existing valid report JSON is reused; only the
unfinished role(s) run again.

## Authentication and cost: current configuration

The current layer is explicitly configured to use your saved ChatGPT/Codex
sign-in, rather than API credits. In `codex_runner.py`, the child Codex process
removes `OPENAI_API_KEY` and `CODEX_API_KEY` from its environment before it is
started. Your `.env` is therefore not used by these three Codex roles.

This does **not** mean the `.env` file is pointless. It remains available for
the upstream TradingAgents API-key workflow. Keep it private and out of Git.
Never paste a key into a prompt, report, issue, or chat.

The official Codex documentation confirms that `codex exec` normally reuses
saved CLI authentication and can write schema-constrained final output to a
file. It also supports API-key authentication through `CODEX_API_KEY` for a
single invocation. See [Authentication](https://learn.chatgpt.com/docs/auth)
and [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode).

## If you later want to spend API credits

There are two distinct choices:

### A. Keep this research layer, switch only the Codex credential

This preserves the same command, three roles, report files, JSON format,
resume behavior, and research safeguards. Only the authentication/billing
source changes from saved ChatGPT/Codex login to API usage.

It is **not enabled today**, on purpose: the runner strips API-key variables.
If you choose this route later, add an explicit opt-in authentication mode
rather than silently changing behavior. The Codex documentation uses
`CODEX_API_KEY` for this non-interactive Codex path; do not expose it broadly
to repository-controlled code or put it in output files.

### B. Run the upstream TradingAgents graph with `OPENAI_API_KEY`

This is a different product flow. It uses LangGraph and direct provider API
calls, with more specialized analysts, tool calls, debate rounds, a portfolio
manager, and an upstream final trade decision. Its interactive CLI displays
progress as it runs and it saves its own full state log under the configured
`results_dir` (by default, `~/.tradingagents/logs`). It does not produce the
three files above unless we build an adapter for it.

| Question | Codex research layer | Native TradingAgents API workflow |
| --- | --- | --- |
| Input | Compact QQQ/TQQQ technical packet | Broader multi-agent, tool-using graph |
| Output | Three local JSON research reports | Interactive progress plus graph/state reports and final decision |
| Credential today | Saved ChatGPT/Codex sign-in | `.env` API key / provider credential |
| API credits today | Not used | Used |
| Broker/order access | None | None by default, but its language is more decision-oriented |

So: **API credits do not automatically make the experience change.** If we
switch the *extra layer* to `CODEX_API_KEY`, you would see the same reports in
the same place. If you run *native TradingAgents* through `OPENAI_API_KEY`,
you would see a different, larger multi-agent workflow.

## Practical research discipline

Treat every dated run as a journal entry. Before reading the reports, write a
one-sentence research question and the evidence that would prove it wrong.
Afterward, record what happened over a fixed horizon. Avoid changing the
question after seeing the result; that is the simplest defense against turning
the tool into confirmation seeking.

This layer is an analysis aid, not investment, tax, or legal advice. Leveraged
ETFs such as TQQQ can diverge materially from a simple multiple of index
returns over time, particularly in volatile markets.
