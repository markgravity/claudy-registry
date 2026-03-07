---
name: create-add-claudy-plugin-pr
description: Create a claudy-registry PR to add a new plugin. Pass a GitHub URL, a local .md file, or a local directory. Creates the branch, plugin.json, copies source files, commits, pushes, and opens the PR with title "[Plugin] Add {Name} {Kind}".
---

# Create Add Claudy Plugin PR

Create a pull request in the local `claudy-registry` clone for a new plugin.

## Usage

```
/create-add-claudy-plugin-pr <github-url | local-.md-file | local-directory>
```

**Examples:**
```
/create-add-claudy-plugin-pr https://github.com/upstash/context7-mcp
/create-add-claudy-plugin-pr ~/Projects/my-skill/skill.md
/create-add-claudy-plugin-pr ./my-command.md
/create-add-claudy-plugin-pr ~/Projects/my-skill/
```

---

## Input Detection

Detect input type by inspecting the argument:

| Condition | Mode |
|-----------|------|
| Starts with `http` | **GitHub URL** |
| Ends with `.md` or is a path to a `.md` file | **Single .md file** |
| Is a directory path | **Local directory** |

---

## Mode A: GitHub URL

### 1. Fetch repo metadata

For `https://github.com/owner/repo`:
- `https://raw.githubusercontent.com/owner/repo/HEAD/README.md`
- `https://raw.githubusercontent.com/owner/repo/HEAD/package.json` (or `pyproject.toml`)

Use README and package metadata to fill all fields (see Field Guide).

The plugin references its source via `githubRepo`/`githubPath` — it is **not** inline.

---

## Mode B: Single .md File

The `.md` file **is** the plugin source (a skill prompt or command prompt).

### 1. Read the file

Read the `.md` file content. Infer `id` from the filename (lowercase, hyphenated, strip `.md`).

### 2. Treat as inline plugin

This is an inline plugin — the source will live in the registry alongside `plugin.json`. Set:
```json
"githubRepo": "{REGISTRY_REPO}",
"githubPath": "plugins/{author}/{id}"
```
where `{REGISTRY_REPO}` is the `owner/repo` of the registry remote (resolved in the setup step).

Resolve `author` by running `gh api user -q '.login'`.

Determine `kind` from context:
- If the filename or content suggests a slash command → `"command"`
- Otherwise → `"skill"`

### 3. Copy the .md file

Copy the `.md` file to `plugins/{author}/{id}/` in the registry (keep the original filename).

---

## Mode C: Local Directory

### 1. Inspect the directory

Read all files present:
- `plugin.json` → use as base, fill in any missing required fields
- `*.md` files → source files for inline plugins
- `package.json` / `pyproject.toml` / `README.md` → use for field inference

### 2. Determine if inline or external

- **Inline**: source will live in the registry. Set `githubRepo: "{REGISTRY_REPO}"`, `githubPath: "plugins/{author}/{id}"`. Copy all `.md` files.
- **External**: source lives elsewhere. Set `githubRepo`/`githubPath` pointing to the actual repo. Do not copy source files.

Default to **inline** unless the existing `plugin.json` already has a non-registry `githubRepo`.

---

## Field Guide

| Field | Required | Notes |
|-------|----------|-------|
| `id` | ✓ | Lowercase, hyphenated. For MCPs strip `mcp-`/`-mcp` affixes. Must match the registry directory name. |
| `marketplaceId` | ✓ | `"{author}"` for inline; `"{github-username}"` for external |
| `kind` | ✓ | `"mcp"`, `"skill"`, or `"command"` |
| `name` | ✓ | Human-readable display name. 2–60 chars. |
| `description` | ✓ | What it does. 10–200 chars. |
| `author` | ✓ | GitHub username of the PR creator. Resolve by running `gh api user -q '.login'`. |
| `tags` | ✓ | 3–6 lowercase topic strings |
| `iconSF` | ✓ | SF Symbol name — see Icon Guide below |
| `featured` | ✓ | Always `false` for new submissions |
| `version` | ✓ | Always `"1.0.0"` for new plugins |
| `homepageURL` | optional | GitHub repo URL |
| `mcpTransport` | MCP only | `"stdio"` or `"http"` |
| `mcpInstallCommand` | stdio MCPs | `"npx"` for npm, `"uvx"` for Python |
| `mcpInstallArgs` | stdio MCPs | e.g. `["-y", "@scope/package@latest"]` for npx, `["package-name"]` for uvx |
| `mcpUrl` | http MCPs | The HTTP endpoint URL |
| `requiresEnvVars` | optional | Array of required env var names, e.g. `["GITHUB_TOKEN"]` |
| `githubRepo` | file-based | `"owner/repo"` format |
| `githubPath` | file-based | Path to skill/command files within the repo |

**Field ordering in plugin.json:**
`id`, `marketplaceId`, `kind`, `name`, `description`, `author`, `tags`, `iconSF`, `featured`, `version`, then optional fields: `homepageURL`, `mcpTransport`, `mcpInstallCommand`, `mcpInstallArgs`, `mcpUrl`, `requiresEnvVars`, `githubRepo`, `githubPath`.

**Icon Guide:**

| Context | Symbol |
|---------|--------|
| Browser/web | `"safari"` |
| Debugging | `"ladybug"` |
| Database | `"cylinder"` |
| File/document | `"doc"` |
| Git | `"arrow.triangle.branch"` |
| Terminal/shell | `"terminal"` |
| Search | `"magnifyingglass"` |
| Cloud/API | `"cloud"` |
| Security/auth | `"lock.shield"` |
| Code | `"chevron.left.forwardslash.chevron.right"` |
| Data/analytics | `"chart.bar"` |
| Communication | `"message"` |
| Networking/MCP | `"network"` |
| AI/ML | `"cpu"` |

---

## PR Title Kind Label

- `kind: "mcp"` → `"MCP server"` (e.g. `[Plugin] Add Context7 MCP server`)
- `kind: "skill"` → `"skill"` (e.g. `[Plugin] Add Commit Message skill`)
- `kind: "command"` → `"command"` (e.g. `[Plugin] Add Explain Code command`)

---

## Create Branch, Validate, Commit, and Open PR

```bash
# Locate the local claudy-registry clone
REGISTRY=$(find ~ -maxdepth 6 -type d -name "claudy-registry" 2>/dev/null | while read dir; do
  git -C "$dir" remote get-url origin 2>/dev/null | grep -q "claudy-registry" && echo "$dir" && break
done | head -1)
if [ -z "$REGISTRY" ]; then echo "claudy-registry not found locally. Please clone it first."; exit 1; fi

# Derive registry repo (e.g. "markgravity/claudy-registry") from git remote
REGISTRY_REPO=$(git -C "$REGISTRY" remote get-url origin | sed 's|.*github.com[:/]||' | sed 's|\.git$||')

AUTHOR=$(gh api user -q '.login')
cd "$REGISTRY"
git checkout main && git pull origin main
git checkout -b "plugin/${AUTHOR}/{id}"
mkdir -p "plugins/${AUTHOR}/{id}"
```

Write `plugin.json` using the Write tool. Copy any `.md` source files if inline.

Validate before committing:
```bash
python scripts/validate_plugin.py "plugins/{author}/{id}/plugin.json"
```

If validation fails, fix `plugin.json` and re-validate before proceeding.

Commit and push:
```bash
git add "plugins/{author}/{id}/"
git commit -m "feat(plugin): add {name}"
git push origin "plugin/{author}/{id}"
```

Open the PR:
```bash
gh pr create \
  --repo "$REGISTRY_REPO" \
  --title "[Plugin] Add {Name} {Kind label}" \
  --body "$(cat <<'EOF'
## Plugin Submission

Adds **{Name}** to the Claudy marketplace.

- **Kind:** {kind}
- **Author:** {author}
- **Source:** {github-url or local path}

## Checklist
- [ ] `plugin.json` validates against schema
- [ ] `id` matches directory name
- [ ] `author` matches parent directory
- [ ] `version` is `"1.0.0"`
EOF
)"
```

Return the PR URL when done.
