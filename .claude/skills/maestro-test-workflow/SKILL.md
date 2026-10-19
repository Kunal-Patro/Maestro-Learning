---
name: maestro-test-workflow
description: Step-by-step workflow for writing, changing or debugging Maestro UI test flows (inspect → plan and stop for approval → implement → stability runs → classify failures). Use before starting a new Maestro test, planning or implementing any change to a flow or subflow under .maestro/, or investigating a failing or flaky Maestro flow.
---

# Workflow for a new test

Convention files referenced below live in `.claude/conventions/`. Read each
one at the step that names it.

## Who runs each step

The main session is the **orchestrator** (run it on Opus). It owns the
thinking steps and delegates the mechanical ones to Sonnet subagents in
`.claude/agents/`:

| Step | Runs in | Model |
|---|---|---|
| 1 Inspect | `maestro-inspector` subagent | Sonnet |
| 2 Plan + approval | main session | Opus |
| 3 Implement | `maestro-implementer` subagent | Sonnet |
| 4 Stability | `maestro-stability-runner` subagent | Sonnet |
| 5 Classify / bug found | main session | Opus |

Orchestration rules:

- Before delegating, pin the device: one `device_id`, confirmed with
  `adb -s <id> emu avd name`, passed to every subagent.
- Run subagents **one at a time** on a device — they share one app, one
  screen and one on-device Maestro driver, so parallel runs interfere.
- Subagents return compact reports, never raw hierarchy dumps.
- Any failure in Step 3 or 4 comes back **unfixed** to the main session for
  Step 5. Never ask a subagent to "make it pass".
- If the main session is not on Opus, delegate Step 5's analysis to a
  `general-purpose` agent with `model: opus`, handing it the artifact paths.

**Step 1 — Inspect.** *(delegate → `maestro-inspector`: device_id, screen to
reach, optional action to diff.)* Dump the hierarchy of the screen under test:
`inspect_screen` (Maestro MCP, after `list_devices` for the `device_id`), or
on the CLI `maestro hierarchy > h.json && python3 .maestro/tools/flatten.py h.json`.
Use `take_screenshot` only alongside the hierarchy, never instead of it.
Report available selectors and their quality (id / content-desc / text-only).
To learn what an action changes (new views, removed views, changed text or
state), diff the flattened hierarchy before and after that single action —
recipe under "Hierarchy diff" in CLAUDE.md Commands.
→ Read `selectors.md`.

**Step 2 — Plan, then stop.** *(main session.)* The plan is the spec the
implementer executes without judgement, so make it complete: per file the
path, subflows reused, exact selectors, assertions in order, env values and
tags. Present before implementing:

- which existing subflows you'll reuse (list `.maestro/common/` first)
  → `structure.md`
- the selectors you'll use, with any non-id selector flagged → `selectors.md`
- the assertions and why each one is stable → `assertions.md`
- fixture/test-data strategy, if any → `test-data.md`
- any popup or conditional handling → `dialogs.md`
- which tags → `tags.md`
- **additional cases worth adding**: the obvious negative, the empty state,
  and one interrupted-mid-flow case — propose them, let me choose

Wait for approval.

**Step 3 — Implement** exactly the approved plan. *(delegate →
`maestro-implementer`: the full approved plan + device_id.)* Explore with
inline YAML via the MCP `run` tool, then save the files and run them by path.
If it reports a plan gap, fill the gap in the plan (Step 2) and re-delegate.

**Step 4 — Stability.** *(delegate → `maestro-stability-runner`: flow paths,
N, device_id.)* Run 5–10 times. Report the pass rate, not a single green run.

**Step 5 — On failure, classify before fixing:** *(main session, Opus.)*

| Class | Signature | Owner |
|---|---|---|
| App bug | consistent, app misbehaves | dev |
| Test defect | bad selector, missing wait, wrong assumption | us |
| Environment | network, locale, device, data | infra |

Read the debug artifacts — screenshot first, then hierarchy, then logs —
before forming a hypothesis. They are in `reports/artifacts/` (screenshots,
commands.json) and `reports/debug/` (maestro.log). A failure *before* the
first command is structural or environmental; a failure *after* it is
behavioural. For a behavioural failure, a before/after hierarchy diff around
the failing step separates "app didn't do it" from "app did it but didn't
render it". → Read `gotchas.md` before proposing a fix.
