Generate a user-facing changelog from git history.

If the user provides a ref (tag, commit, or branch), use it as the starting point.
Otherwise, use the most recent git tag (`git describe --tags --abbrev=0`).
If there are no tags, use the initial commit.

Steps:
1. Run `git log <ref>..HEAD --oneline` to collect commits since the ref.
2. Group commits by type using conventional commit prefixes:
   - `feat` / `add` → **New Features**
   - `fix` → **Bug Fixes**
   - `perf` / `refactor` → **Improvements**
   - `docs` → **Documentation**
   - `chore` / `ci` / `build` → omit (internal)
3. Within each group, write one concise bullet per commit in user-facing language (no jargon, no ticket numbers).
4. Output the final changelog in this format:

```
## What's New

### New Features
- ...

### Bug Fixes
- ...

### Improvements
- ...
```

5. Ask the user if they want the output saved to `CHANGELOG.md` or copied as App Store "What's New" text (max 4000 chars, plain text only).
