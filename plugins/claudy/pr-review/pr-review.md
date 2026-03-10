Review the pull request for the current branch and provide structured, actionable feedback.

**Steps:**
1. Run `gh pr view` to get the PR title, description, and linked issues
2. Run `gh pr diff` to see all changed files and lines
3. For each changed file, evaluate:
   - **Correctness** — does the logic do what it claims? Are there edge cases or off-by-ones?
   - **Security** — injection, auth bypass, sensitive data exposure, insecure defaults
   - **Performance** — unnecessary loops, missing indexes, expensive operations in hot paths
   - **Clarity** — are names meaningful? Is the code easy to follow?
   - **Tests** — are new behaviours covered? Are existing tests still valid?

**Output format:**

### Summary
One or two sentences on the overall quality and purpose of the PR.

### What's good
Specific praise for well-written or clever parts.

### Must fix (blocking)
List each issue with `file.ts:line` references. Explain *why* it's a problem and suggest a fix.

### Suggestions (non-blocking)
Improvements that would be nice but aren't required for approval.

### Verdict
`✅ Approve` | `🔄 Request changes` | `💬 Comment`
