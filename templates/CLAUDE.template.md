<!--
Reusable CLAUDE.md for Maestro UI testing of an Android app on an emulator.

To use in a new repo:
  1. Copy this file to <new-repo>/CLAUDE.md and delete this comment.
  2. Copy the kit it references:
       .claude/conventions/   .claude/skills/maestro-test-workflow/   .claude/agents/
       .maestro/tools/flatten.py   .gitignore (reports/, h.json, .env)
       .github/workflows/maestro.yaml (optional: swap the env/secret names)
  3. Replace every <PLACEHOLDER>. Fill "App notes" as you learn the app.
  4. In .claude/agents/maestro-implementer.md, replace `org.wikipedia:id/` with `<APP_ID>:id/`.
  5. Empty .claude/conventions/gotchas.md of app-specific lines if any were added.
-->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Maestro UI test automation for the **<APP_NAME> Android app** (`appId: <APP_ID>`). There is no app source here. The APK under test is `<APK_PATH>`. All "code" is Maestro YAML flows in `.maestro/`. Target is an Android emulator only; the only test tool is Maestro (CLI and Maestro MCP).

## Commands

Requires an Android emulator running with the APK installed (`adb install -r <APK_PATH>`). Flows assert on <LOCALE> UI text, so the device locale must be <LOCALE>.

```bash
# Pin the device first: serials follow boot order, not the AVD
adb devices && adb -s <id> emu avd name

# Full suite (uses .maestro/config.yaml)
maestro --device <id> test .maestro/

# Single flow
maestro --device <id> test .maestro/<feature>/<flow>.yaml

# By tag (same filter CI uses)
maestro --device <id> test --include-tags smoke --exclude-tags requires-network .maestro/

# Flows that need credentials: values come from the git-ignored .env, never typed inline
set -a && . ./.env && set +a && \
  maestro --device <id> test -e <USER_ENV>="$<USER_ENV>" -e <PASS_ENV>="$<PASS_ENV>" .maestro/<feature>/<flow>.yaml

# Debug artifacts / reports
maestro --device <id> test --format junit --output reports/junit.xml --test-output-dir reports/artifacts --debug-output reports/debug .maestro/

# Find element ids: dump view hierarchy, then flatten it to an indented readable tree
maestro --device <id> hierarchy > h.json && python3 .maestro/tools/flatten.py h.json

# Hierarchy diff: see exactly what one action added, removed or changed
maestro --device <id> hierarchy > reports/before.json
#   ...perform the single action (tap, type, restart)...
maestro --device <id> hierarchy > reports/after.json
diff -w <(python3 .maestro/tools/flatten.py reports/before.json) \
        <(python3 .maestro/tools/flatten.py reports/after.json)

# Which accounts does the app hold in Android's AccountManager? (0 = clean)
adb -s <id> shell dumpsys account | grep -E "Accounts:"
```

`flatten.py` prints one line per node (`class|id|acc|text|click|checked|selected`, indented by depth, system UI dropped, no bounds), so a line diff shows only real component changes: new or removed views, changed text, toggled checked/selected state. Always use `diff -w`: adding or removing one wrapper view (e.g. the keyboard opening or closing) shifts the indentation of every node below it, and without `-w` the whole tree shows as changed. If the keyboard's open/closed state differs between dumps, its ~150 `com.google.android.inputmethod.latin` lines show up too; ignore them. Use it to find controls the docs don't mention, to see what an action really did, and to isolate display bugs (e.g. data saved but the list not rendered). It reads `maestro hierarchy` CLI JSON, not the MCP `inspect_screen` output.

## Hard rules (Maestro + Android emulator)

- **Secrets leak into reports.** Every `-e` value is written in plain text to `reports/artifacts/*/commands.json` (`defineVariablesCommand`) and `maestro.log`. Never print, grep, summarise or share those files after a credentialed run; diagnose from screenshots and hierarchy JSON only. Never read `.env` or echo its variables. `reports/` and `.env` stay git-ignored.
- **Don't mix the Maestro CLI and the Maestro MCP on one device in a session.** Running `maestro hierarchy`/`maestro test` from the CLI killed the MCP's on-device driver (`DeviceServerDiedException: UNAVAILABLE`) and it did not recover. Pick one; the CLI is the reliable fallback.
- **One device, one runner at a time.** Subagents and runs share one app, one screen and one on-device driver; parallel runs interfere.
- **`clearState: true` is `pm clear`, not a fresh install.** Accounts in Android's AccountManager, install-time state and all server-side state survive. A flow that logs in must log out from `onFlowComplete` (`common/teardown/`), or the next flow starts half-logged-in.
- **`runFlow: when:` is single-shot with no retry.** It misses a dialog that renders late. Anchor on a deterministic element first, and make a dialog that always appears a required step rather than a conditional.

## Flow architecture

- **`.maestro/config.yaml`** — workspace config. `flows:` globs (`<feature>/*`, one per test folder) decide which files run as top-level tests when running the directory; anything under `common/` is only ever invoked via `runFlow`. Add new test folders to this list or they won't run. `continueOnFailure: true`.
- **Test folders** (`<feature>/`) — one test case per file, tagged with its area plus `smoke` (fast, offline, secret-free) or `regression` + `requires-network` for flows that hit the server. Optional `properties` (`testCaseId`, `priority`).
- **`common/setup/`** — flows that start from a fresh app (`launchApp: clearState: true`) and reach a known state (e.g. past onboarding, on the home screen asserting `<HOME_ANCHOR_ID>`; logged in as a user).
- **`common/steps/`** — reusable mid-flow helpers. Never launch the app. Each starts with a contract comment: `# requires: <screen>. leaves: <screen>.`
- **`common/teardown/`** — undo state that survives `clearState` (e.g. log out). Called from `onFlowComplete` so it runs even when the test fails; every command `optional: true`.
- **Logged-in tests**: `runFlow: ../common/setup/<login_setup>.yaml` plus `onFlowComplete: - runFlow: ../common/teardown/<logout>.yaml`. The login setup fails fast with an `assertTrue` guard if `<USER_ENV>` / `<PASS_ENV>` are unset.
- `runFlow` file paths are relative to the calling file (`../common/...`).

## App notes

<!-- Fill in as you learn the app. Keep app-specific facts here, not in .claude/conventions/. -->

- Home / main screen anchor: `<HOME_ANCHOR_ID>`
- Fresh-launch path (welcome, onboarding, permission prompts): <...>
- Login entry point and post-login-only anchor: <...>
- Known popups / one-time prompts and when they appear: <...>
- Existing setup chain: <...>

## CI

`.github/workflows/maestro.yaml` boots an API 34 `google_apis` x86_64 emulator (pixel_6, animations disabled), installs the APK, and runs `--include-tags smoke --exclude-tags requires-network`, so `requires-network` flows never run in CI. All output goes to `reports/` (JUnit, artifacts, debug logs), uploaded as the `maestro-debug` artifact. If CI ever runs a credentialed flow, that artifact will contain the password (see Hard rules). Credentials come from `<USER_ENV>` / `<PASS_ENV>` repo secrets.

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
