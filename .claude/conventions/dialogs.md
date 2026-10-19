# Interrupting dialogs

## 9. Interrupting dialogs

1. Suppress at source if possible (feature flag, seeded preference, debug
   build). Removing the condition beats branching around it.
2. If not: anchor on a deterministic element *first*, then evaluate the
   conditional. `when:` is single-shot with no retry — it will miss a dialog
   that renders 300ms late.
3. Every conditional needs a **canary test** elsewhere asserting the thing
   actually appears. A conditional that silently stops firing is invisible
   decay.
4. Assert inside the branch (`assertNotVisible` after dismissing) so a
   half-working condition fails loudly.
