# SonarCloud issue prioritization

Sorting is applied in this order:

1. **Severity** (descending)
   - `BLOCKER` > `CRITICAL` > `MAJOR` > `MINOR` > `INFO`

2. **Type** (descending)
   - `VULNERABILITY` > `BUG` > `CODE_SMELL`

3. **Estimated effort / debt** (descending, when available)

4. **Creation date** (oldest first)

Rationale:

- `BLOCKER` / `CRITICAL` issues are most likely to affect correctness, security, or build stability.
- Vulnerabilities are handled before bugs and smells.
- Older issues are typically more entrenched and should be paid down early.
