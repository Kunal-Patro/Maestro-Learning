# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Learning repo for Maestro UI test automation against the **Wikipedia Android app** (`appId: org.wikipedia`). There is no app source here — the APK under test is committed as `app.apk`. All "code" is Maestro YAML flows in `.maestro/`.

## Commands

Requires an Android emulator/device running with `app.apk` installed (`adb install -r app.apk`). Flows assert on English UI text, so the device locale must be English.

```bash
# Full suite (uses .maestro/config.yaml)
maestro test .maestro/

# Single flow
maestro test .maestro/search/search_term_added_to_history.yaml

# By tag (same filter CI uses)
maestro test --include-tags smoke --exclude-tags requires-network .maestro/

# Debug artifacts / reports
maestro test --format junit --output reports/junit.xml --test-output-dir reports/artifacts --debug-output reports/debug .maestro/

# Find element ids: dump view hierarchy, then flatten it to an indented readable tree
maestro hierarchy > h.json && python3 .maestro/tools/flatten.py h.json

# Hierarchy diff: see exactly what one action added, removed or changed
maestro --device <id> hierarchy > reports/before.json
#   ...perform the single action (tap, type, restart)...
maestro --device <id> hierarchy > reports/after.json
diff -w <(python3 .maestro/tools/flatten.py reports/before.json) \
        <(python3 .maestro/tools/flatten.py reports/after.json)
```

`flatten.py` prints one line per node (`class|id|acc|text|click|checked|selected`, indented by depth, system UI dropped, no bounds), so a line diff shows only real component changes: new or removed views, changed text, toggled checked/selected state. Always use `diff -w`: adding or removing one wrapper view (e.g. the keyboard opening or closing) shifts the indentation of every node below it, and without `-w` the whole tree shows as changed. If the keyboard's open/closed state differs between dumps, its ~150 `com.google.android.inputmethod.latin` lines show up too; ignore them. Use it to find controls the docs don't mention, to see what an action really did, and to isolate display bugs (e.g. data saved but the list not rendered). It reads `maestro hierarchy` CLI JSON, not the MCP `inspect_screen` output.

## Flow architecture

- **`.maestro/config.yaml`** — workspace config. `flows:` globs (`onboarding/*`, `auth/*`, `search/*`) decide which files run as top-level tests when running the directory; anything under `common/` is only ever invoked via `runFlow`. Add new test folders to this list or they won't run. `continueOnFailure: true`.
- **Test folders** (`onboarding/`, `auth/`, `search/`) — one test case per file, tagged with its area plus `smoke`, or `regression` + `requires-network` for flows that hit the server (`auth/login_success.yaml`). Some carry `properties` (`testCaseId`, `priority`).
- **`common/setup/`** — flows that start from a fresh app (`launchApp: clearState: true`) and reach a known state. Chain: `move_from_welcome_screen` → `skip_onboarding` / `complete_onboarding` (both end asserting `main_view_pager`, i.e. home feed). `login_as_user` = credential guard → `skip_onboarding` → `steps/open_login_screen` → `steps/login`; ends on home feed, logged in.
- **`common/steps/`** — reusable mid-flow helpers (open search, type a search term, open the login form, log in, dismiss prompts).
- **`common/teardown/`** — `logout.yaml`, run from `onFlowComplete` by every flow that logs in. Needed because the Wikipedia account lives in Android's AccountManager and **survives `clearState`**: a leftover account makes the next flow's welcome screen show a late "Turn on collection sync?" dialog that the single-shot `dismiss_sync_promt` misses, failing on `tapOn: "Forward"`. Check with `adb shell dumpsys account | grep Accounts:` (0 = clean).
- **Logged-in tests**: `runFlow: ../common/setup/login_as_user.yaml` plus `onFlowComplete: - runFlow: ../common/teardown/logout.yaml`, run with `-e WIKI_USER=... -e WIKI_PASS=...` (locally from the git-ignored `.env`). The password is written in plain text to `reports/artifacts/*/commands.json` (`defineVariablesCommand`) and `maestro.log` — never print or share those.
- `runFlow` file paths are relative to the calling file (`../common/...`).

## CI

`.github/workflows/maestro.yaml` runs on PRs, nightly cron, and manual dispatch: boots an API 34 `google_apis` x86_64 emulator (pixel_6, animations disabled), installs `app.apk`, and runs `--include-tags smoke --exclude-tags requires-network`. So flows tagged `requires-network` never run in CI. Note the nightly run currently uses the same smoke filter — the README's "full suite nightly" is not implemented. All output goes to `reports/` (JUnit, artifacts, debug logs), which is uploaded as the `maestro-debug` artifact. Credentials come from `WIKI_USER` / `WIKI_PASS` repo secrets.

## Maestro flow authoring conventions

The step-by-step process (inspect → plan and stop → implement → stability →
classify failures) is the **`maestro-test-workflow` skill**
(`.claude/skills/maestro-test-workflow/`). Invoke it before starting a new
test, changing any flow, or debugging a failing one.

Rules for writing Maestro flows live in `.claude/conventions/`. They are **not**
loaded at startup. When a trigger below applies, Read the listed file(s)
before acting, and follow them unless told otherwise in a specific request.

| Trigger: before you… | Read |
|---|---|
| inspect a screen or choose or write any selector (`id`, `text`, `childOf`, `index`) | `.claude/conventions/selectors.md` |
| write or change an assertion (`assertVisible`, `assertNotVisible`, `extendedWaitUntil`) | `.claude/conventions/assertions.md` |
| create or move a flow, subflow, script or folder, or edit `config.yaml` or report paths | `.claude/conventions/structure.md` |
| handle a popup, dialog, tooltip, or any `runFlow: when:` conditional | `.claude/conventions/dialogs.md` |
| use test data, `env:` values, credentials, or fixtures | `.claude/conventions/test-data.md` |
| add or change tags, or CI include/exclude filters | `.claude/conventions/tags.md` |
| debug a failing or flaky flow | `.claude/conventions/gotchas.md` (after invoking the skill) |

If several triggers apply, read every file that matches. Don't read files whose triggers don't apply.
