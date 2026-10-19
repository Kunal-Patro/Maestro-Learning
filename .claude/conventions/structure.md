# Structure, reuse and independence

## 5. Structure

```
<repo>/
  .gitignore            # ignores reports/ and hierarchy dumps
  reports/              # generated output, git-ignored, never committed
    junit.xml           #   --format junit --output reports/junit.xml
    artifacts/          #   --test-output-dir: screenshots, video, commands.json
    debug/              #   --debug-output: maestro.log
  .maestro/
    config.yaml         # flows: globs list the feature folders only
    common/
      setup/            # owns launchApp + clearState; must be called first
      steps/            # assumes a starting screen; composable; never launches
      teardown/         # called from onFlowComplete; may stopApp/launchApp (no clearState); every command optional
    scripts/            # JS for runScript: test-data generation, API seeding; results read as ${output.*}
    tools/              # dev helpers that are not Maestro (flatten.py: one line per node, for hierarchy diffs)
    <feature>/          # the actual tests, one folder per feature (e.g. onboarding/, search/)
```

- **One behaviour per flow.** If the description needs an "and", split it.
- A `setup/` flow owns the app lifecycle. A `steps/` flow never calls
  `launchApp`. A `teardown/` flow undoes state that survives `clearState`
  (e.g. a logged-in Android account) and runs from `onFlowComplete`, so it
  runs even when the test fails.
- Keep nesting to two levels. Deep `runFlow` chains make relative paths
  fragile and hide the launch behaviour from the reader.
- Comment each `steps/` subflow with its contract:
  `# requires: on main feed. leaves: on search screen.`
- `common/`, `scripts/` and `tools/` must never appear in the `flows:` glob in
  `config.yaml`, so subflows and support files are never collected as tests.
- JS goes in `scripts/`, never inline in YAML when it's longer than a one-liner.
- All run output goes under `reports/`, locally and in CI. Never commit reports.

## 6. Reuse before creating

- Before writing a new subflow, list what already exists in `common/` and
  reuse it. Say which existing subflows you are reusing in the plan.
- If an existing subflow is *almost* right, propose parameterising it with
  `env:` rather than duplicating it.
- Parameterised steps take values via env: test files declare `env:` in the
  header (e.g. `SEARCH_TERM`) and pass it to the subflow with `runFlow: env:`.

## 7. Test independence

- Every test creates its own preconditions. Never assume another test ran
  first — order-dependent suites break under sharding, `continueOnFailure`,
  and single-flow debugging.
- Shared setup goes in a subflow both tests call; never in a sibling test.
- Use distinct test data per flow so one test can't mask another's work.
