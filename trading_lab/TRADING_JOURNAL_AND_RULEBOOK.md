# Trading journal and rulebook

This is a personal research and decision-record template for QQQ, TQQQ, and
SQQQ. It does not connect to a broker or generate order instructions.

The purpose is simple: write the rule **before** acting, record what actually
happened afterward, and revise a rule only between trades—not while defending
an open position.

## Operating rules

### Scope

- Signal instrument: `QQQ` or the Nasdaq-100 (`NDX`), not the price of TQQQ or
  SQQQ itself.
- Exposure instruments: `TQQQ` for bullish exposure and `SQQQ` for bearish
  exposure.
- Research source: a dated `trading_lab/runs/YYYY-MM-DD/packet.json` plus
  other sources explicitly listed in the journal entry.
- No broker automation, no options, and no adding to a losing position unless
  a separately precommitted rule explicitly permits it.

### Non-negotiables

1. Record the setup, invalidation, maximum loss, and maximum holding period
   before an entry or addition.
2. Do not use the entry price or break-even price as a reason to hold.
3. Do not change a rule while a position is open. Record any proposed change
   under `Rule changes` and apply it only to a later trade.
4. A missed opportunity is acceptable. Adding because of urgency, frustration,
   or a desire to recover a loss is not a valid setup.
5. TQQQ and SQQQ target daily leveraged returns; their multi-day performance
   can differ materially from a simple three-times calculation. Signals belong
   on the underlying index/ETF, while position-risk limits belong on the actual
   ETF held.

## Breakout–retest–hold rule: hypothesis to test

This is a rule specification, not a claim that it has a profitable edge. Fill
in each blank before using it. Backtesting can later decide whether the chosen
parameters are useful.

### Definitions

| Field | My definition |
| --- | --- |
| Signal series | `QQQ` daily OHLC data |
| Reference high | `[e.g., prior all-time high / 60-day swing high]` |
| Breakout | `[e.g., daily close above reference high by ___%]` |
| Retest window | `[e.g., within ___ trading sessions after breakout]` |
| Retest zone | `[e.g., reference high ± ___%]` |
| “Holds” | `[e.g., daily close remains above lower edge of zone for ___ sessions]` |
| Confirmed failure | `[e.g., daily close below lower edge of zone]` |
| No-retest outcome | `[e.g., exit inverse exposure after ___ sessions]` |

### Application to an SQQQ position

This rule is intended to prevent an inverse position from becoming an
open-ended prediction that a rally must reverse.

- If QQQ breaks out, retests the specified zone, and **holds** according to the
  definition above: the bearish thesis is invalidated; close SQQQ.
- If QQQ breaks out but later **fails** according to the definition above: the
  breakout is not confirmed. This is evidence to reassess, not automatic
  permission to increase SQQQ.
- A new or larger SQQQ position needs its own entry evidence, position limit,
  and loss limit. A lower SQQQ price alone is not evidence.

### Application to a TQQQ position

Do not mirror the SQQQ rule mechanically. A bullish entry needs its own
defined setup—for example, a trend continuation or a pullback that recovers a
specified level. The same risk, time, and add-on requirements apply.

## Pre-trade card

Copy this section for every new position or planned addition. Complete it
before placing the order.

```markdown
### Trade ID: YYYY-MM-DD-[TQQQ|SQQQ]-01

- Decision date / time zone:
- Intended execution date:
- Instrument and direction:
- Purpose: [research test / hedge / directional swing]
- Signal instrument and date:
- Research packet/report links:

#### Thesis

- One-sentence thesis:
- Evidence supporting it:
- Evidence that contradicts it:
- Catalyst assumptions, if any:

#### Rules already decided

- Entry condition:
- Maximum initial exposure ($ and % of portfolio):
- Add condition and maximum total exposure:
- Invalidation / exit condition:
- Maximum dollar loss:
- Maximum holding period:
- Overnight / event-risk policy:

#### Pre-trade check

- [ ] This is not an attempt to recover a prior loss.
- [ ] I can state exactly what would prove the thesis wrong.
- [ ] I will not add if the position is losing unless the prewritten add rule is met.
- [ ] I understand this ETF has a daily leverage objective.
```

## Post-trade review

Complete this only after the position is closed. Do not overwrite the
pre-trade card.

```markdown
#### Execution and result

- Actual entry date(s), price(s), and shares:
- Actual exit date(s), price(s), and shares:
- Gross P/L, fees, and net P/L:
- Holding period:
- Maximum adverse excursion (largest unrealized loss):
- Maximum favorable excursion (largest unrealized gain):

#### Process review

- Did I follow the entry rule? [yes/no + evidence]
- Did I follow the exit rule? [yes/no + evidence]
- Did I add, reduce, or hold for a reason not in the plan?
- What did the signal instrument do while the trade was open?
- What did I learn about the rule—not about this one outcome?
- Proposed rule change for future trades only:
```

## Rule changes

Keep a dated log. A rule change must name the evidence used and the future
trades it applies to.

| Date | Change | Why | Applies starting with |
| --- | --- | --- | --- |
| | | | |
