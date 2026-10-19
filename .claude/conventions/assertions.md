# Assertions

## 4. Assertions

- Assert stable anchors, never marketing copy or body text.
- Assert the **precondition** before acting on it, so failures point at the
  real cause instead of cascading three steps later.
- Prefer assertions that can *only* be true in the claimed state:
  a post-auth-only control beats a username that might be cached;
  a counter reading "2 selected" beats "1 selected".
- Prefer structural / count assertions over content assertions when the
  content is server-supplied or dynamic.
- Do not assert on transient UI (snackbars, toasts) as the primary signal.
  Assert the durable state change; use `extendedWaitUntil` if the transient
  message must also be checked.
- Use `extendedWaitUntil` with an explicit timeout for network-dependent
  results.
- Avoid AI assertions by default. Deterministic assertions only, unless the
  property is genuinely semantic and the flake cost is acceptable.
