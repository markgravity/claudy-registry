Review the pull request specified by the user (or the current branch's open PR if none is given).

Steps:
1. Use `gh pr view` to fetch the PR title, description, and diff.
2. Use `gh pr diff` to read all changed files.
3. Analyze the diff for:
   - **Bugs** — logic errors, off-by-ones, unchecked nulls, race conditions
   - **Security** — injection, hardcoded secrets, unsafe deserialization
   - **Design** — unnecessary complexity, poor naming, missing abstractions
   - **Style** — inconsistency with the surrounding codebase
4. Output a structured review with sections:
   - **Summary** — one paragraph describing what the PR does
   - **Issues** — bullet list, each tagged [bug], [security], [design], or [style], with file:line references
   - **Suggestions** — optional improvements that are not blockers
   - **Verdict** — Approve / Request Changes / Comment
5. Ask the user whether to post the review as a GitHub PR comment via `gh pr review`.
