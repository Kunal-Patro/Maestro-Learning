# Test data and fixtures

## 8. Test data and fixtures

- Never depend on data you don't control. Seed it via API where an API exists.
- Unique identifiers per run (timestamp + random) so parallel shards collide.
- Fixtures **throw** on failure — a broken fixture invalidates the test.
- Cleanup only **logs** on failure — a failed cleanup doesn't invalidate a
  result. Prefer a pattern-based sweeper over per-test teardown, because
  teardown written at the end of a flow never runs when the flow fails.
- Environment and credentials come from `-e` at runtime. Never hardcode a
  URL, never commit a credential.
