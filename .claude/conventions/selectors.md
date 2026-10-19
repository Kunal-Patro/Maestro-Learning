# Selectors

## 1. Inspect before writing

- Always dump and read the hierarchy before proposing any selector.
  Never guess, never infer a selector from a screenshot alone.
- If a screen exposes no `resource-id` / `accessibilityIdentifier` on the
  elements under test, say so explicitly and recommend adding test IDs
  (`Modifier.testTag` + `testTagsAsResourceId` on Compose) rather than
  silently working around it.
- Report what the hierarchy does *not* contain when that matters — an absent
  view is a finding, not a blocker to route around.

## 2. Selector precedence

1. `resource-id` (Android) / `accessibilityIdentifier` (iOS)
2. `accessibilityText` (content-description)
3. visible `text` — last resort

Rules:

- Never use coordinates.
- Never use a bare `index:` to disambiguate an ambiguous match. `index` is
  acceptable only when it is *structural and deliberate* —
  `id: "card", index: 0` meaning "the first card in this container" is fine;
  `text: "Music", index: 1` meaning "the second thing that happened to match"
  is not.
- Prefer combining criteria over disambiguating by position:
  `id: "account_name"` + `text: "..."` matches on both.
- Scope list items with `childOf:` so they can't match identical text elsewhere.
- **Flag every text or content-description selector as locale-dependent.**
  These break when the device locale differs from the authoring machine.

## 3. Text matching is regex

- `text:` is a **full-string**, case-insensitive regex. `"Apollo"` does not
  match `"Apollo 11"`.
- For a partial match, wrap it in `.*`: `text: ".*Apollo.*"`. Use partial
  matches sparingly, because they widen the match.
- Escape or avoid literals containing `.` `(` `)` `?` `+` `*` `[` `]`;
  they are regex metacharacters.
