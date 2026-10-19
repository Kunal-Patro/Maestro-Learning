# Things that have actually bitten us

- Content-descriptions are localised. An unset device locale broke every flow
  in CI while the same flows passed locally.
- `clearState: true` is `pm clear`, not a fresh install. Local data is wiped;
  the APK, install-time state, and all server-side state survive.
- `run-as` only works on debuggable builds. Release and Play Store images
  can't be rooted, so no preference seeding.
- Maestro has no global interrupt handler. There is no way to catch an
  unexpected dialog that appears at an arbitrary point.
- Emulator serials follow boot order, not the AVD. With two emulators,
  `emulator-5554` was `maestro_34` one day and `play_36` the next, and flows
  failed against the wrong one. Confirm with `adb -s <id> emu avd name`.
- Hierarchy diffing (before/after one action, flattened to one line per node)
  finds undocumented controls and isolates display bugs. Use it.
