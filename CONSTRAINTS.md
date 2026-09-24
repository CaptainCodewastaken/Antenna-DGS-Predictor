# Constraints

Last reviewed: 2026-09-24

## Floor (always enforced, no setup required)

- **ACTION: BLOCK**
- No new suppression comments: `@ts-ignore`, `eslint-disable`, `# noqa`, `# type: ignore`
- No unimplemented stubs: `throw new Error("Not implemented")`, empty `catch {}`
- No skipped or deleted tests without a reason in the commit message
- No secrets in source
- This file does not get weakened to make a change pass

## Enforced with numbers

| Dimension | Rule | Checked by | Runs at | Action |
|-----------|------|-----------|---------|--------|
| Coverage (Python) | Changed lines ≥ 80% covered | `pytest --cov` | task end, CI | WARN |
| Coverage (JS) | Changed lines ≥ 80% covered | `vitest run --coverage` | task end, CI | WARN |

*Note: Enforced checks currently WARN on failure to avoid blocking progress mid-task. They will be upgraded to BLOCK after the first two weeks of development.*

## Measured, not yet enforced

| Metric | Today | Direction |
|--------|-------|-----------|
| Project coverage (Python) | 0% | must not fall |
| Project coverage (JS) | 0% | must not fall |

## Exceptions

| ID | Rule | Path | Reason | Owner | Expires |
|----|------|------|--------|-------|---------|
