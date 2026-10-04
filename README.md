# Maestro-Learning
This repo is just for learning test automations using Maestro

## Maestro E2E — Wikipedia Android

Flows live in `.maestro/`. Smoke tests run on every PR; the full suite runs nightly.

Local: `maestro test -e WIKI_USER=... -e WIKI_PASS=... .maestro/`

The APK is committed for convenience. In a real project the flows would live in the
app repository and CI would consume the build artifact directly — keeping tests beside
the app is what makes it cheap to add test IDs in the same PR that changes the UI.