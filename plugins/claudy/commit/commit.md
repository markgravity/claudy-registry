Review all staged and unstaged changes and create a Conventional Commit.

**Steps:**
1. Run `git status` and `git diff HEAD` to understand what changed
2. Choose the commit type: `feat` | `fix` | `refactor` | `docs` | `test` | `chore` | `style` | `ci` | `perf`
3. Optionally add a scope in parentheses, e.g. `feat(auth):`
4. Write a subject line ≤72 chars in imperative mood ("add X" not "adds X" or "added X")
5. If needed, add a blank line and a short body explaining *why* — not what the diff already shows
6. Stage all relevant files and run the commit

**Rules:**
- Do NOT commit files containing secrets (`.env`, API keys, credentials)
- Do NOT use `--no-verify` or skip pre-commit hooks
- Do NOT amend a previous commit unless the user explicitly asks
- Breaking changes must include `BREAKING CHANGE:` in the footer
