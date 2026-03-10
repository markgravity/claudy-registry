---
name: create-add-claudy-plugin-pr
description: Create a claudy-registry PR to add a new plugin. Pass a GitHub URL, any homepage URL, a local .md file, or a local directory. Creates the branch, manifest.json, copies source files, commits, pushes, and opens the PR with title "[Plugin] Add {Name} {Kind}".
---

# Create Add Claudy Plugin PR

Create a pull request in the local `claudy-registry` clone for a new plugin.

## Usage

```
/create-add-claudy-plugin-pr <github-url | homepage-url | local-.md-file | local-directory>
```

**Examples:**
```
/create-add-claudy-plugin-pr https://github.com/upstash/context7-mcp
/create-add-claudy-plugin-pr https://developer.apple.com/documentation/xcode/giving-agentic-coding-tools-access-to-xcode
/create-add-claudy-plugin-pr ~/Projects/my-skill/skill.md
/create-add-claudy-plugin-pr ./my-command.md
/create-add-claudy-plugin-pr ~/Projects/my-skill/
```

---

## Input Detection

Detect input type by inspecting the argument:

| Condition | Mode |
|-----------|------|
| `https://github.com/{owner}/{repo}` | **GitHub URL** |
| Any other `http`/`https` URL | **Homepage URL** |
| Ends with `.md` or is a path to a `.md` file | **Single .md file** |
| Is a directory path | **Local directory** |

---

## Mode A: GitHub URL

### 1. Fetch repo metadata

For `https://github.com/owner/repo`:
- `https://raw.githubusercontent.com/owner/repo/HEAD/README.md`
- `https://raw.githubusercontent.com/owner/repo/HEAD/package.json` (or `pyproject.toml`)

Use README and package metadata to fill all fields (see Field Guide).

The plugin references its source via `gitURL`/`gitBranch`/`gitPath` — it is **not** inline.

---

## Mode A2: Homepage URL

The URL points to a product page, documentation site, or any non-GitHub page describing a tool or service.

### 1. Fetch and read the page

Use WebFetch to retrieve the page content. Extract:
- Tool/service name
- What it does (for `description`)
- Kind: if the page describes an MCP server → `"mcp"`; if it describes a CLI skill or prompt → `"skill"` or `"command"`; default to `"mcp"` for developer tools/APIs
- Install method: look for npm package names, `npx`/`uvx` commands, HTTP endpoint URLs
- Any required environment variables (API keys, tokens)
- A GitHub repo URL if linked anywhere on the page — use it to populate `gitURL`/`gitBranch`/`gitPath` if it's a file-based plugin; set as `homepageURL` otherwise

### 2. Derive org and slug

**Org** — infer from the URL domain or page content, NOT the PR submitter's GitHub username:
- `developer.apple.com` → `apple`
- `anthropic.com` or `docs.anthropic.com` → `anthropic`
- `jetbrains.com` → `jetbrains`
- `github.com/owner/...` (non-repo page) → `owner`
- Generic: use the second-level domain (e.g. `upstash.com` → `upstash`)
- Normalize to lowercase, alphanumeric + hyphens only

**Slug** — infer from the tool/feature name: lowercase, hyphenated, strip `mcp-`/`-mcp` affixes for MCPs.

**`id`** = `{slug}@{org}` (e.g. `xcode@apple`, `context7@upstash`)
**`author`** = `{org}` (the tool's owning organization, not the PR submitter)

### 3. Construct the manifest

Populate all fields from the scraped content (see Field Guide). Set `homepageURL` to the input URL.
If install details or the org are unclear, ask the user before proceeding.

---

## Mode B: Single .md File

The `.md` file **is** the plugin source (a skill prompt or command prompt).

### 1. Read the file

Read the `.md` file content. Infer the plugin slug from the filename (lowercase, hyphenated, strip `.md`).

### 2. Treat as inline plugin

This is an inline plugin — the source will live in the registry alongside `manifest.json`. Set:
```json
"gitURL": "https://github.com/{REGISTRY_REPO}",
"gitBranch": "main",
"gitPath": "plugins/{author}/{slug}"
```
where `{REGISTRY_REPO}` is the `owner/repo` of the registry remote (resolved in the setup step).

Resolve `author` by running `gh api user -q '.login'`.

Determine `kind` from context:
- If the filename or content suggests a slash command → `"command"`
- Otherwise → `"skill"`

### 3. Copy the .md file

Copy the `.md` file to `plugins/{author}/{slug}/` in the registry (keep the original filename).

---

## Mode C: Local Directory

### 1. Inspect the directory

Read all files present:
- `manifest.json` → use as base, fill in any missing required fields
- `*.md` files → source files for inline plugins
- `package.json` / `pyproject.toml` / `README.md` → use for field inference

### 2. Determine if inline or external

- **Inline**: source will live in the registry. Set `gitURL: "https://github.com/{REGISTRY_REPO}"`, `gitBranch: "main"`, `gitPath: "plugins/{author}/{slug}"`. Copy all `.md` files.
- **External**: source lives elsewhere. Set `gitURL`/`gitBranch`/`gitPath` pointing to the actual repo. Do not copy source files.

Default to **inline** unless the existing `manifest.json` already has a non-registry `gitURL`.

---

## Field Guide

| Field | Required | Notes |
|-------|----------|-------|
| `id` | ✓ | `"{slug}@{author}"` — e.g. `"context7@upstash"`. The slug is lowercase, hyphenated; for MCPs strip `mcp-`/`-mcp` affixes. |
| `kind` | ✓ | `"mcp"`, `"skill"`, or `"command"` |
| `name` | ✓ | Human-readable display name. 2–60 chars. |
| `description` | ✓ | What it does. 10–200 chars. |
| `author` | ✓ | The tool's owning org/user. For GitHub URLs: repo owner. For homepage URLs: org inferred from domain (e.g. `apple`, `anthropic`). For local files: PR creator (`gh api user -q '.login'`). |
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
| `gitURL` | file-based | Full repo URL, e.g. `"https://github.com/owner/repo"` |
| `gitBranch` | if gitURL & no gitTag | Branch name, e.g. `"main"` |
| `gitTag` | if gitURL & no gitBranch | Tag, e.g. `"v1.2.0"` |
| `gitPath` | optional | Subdirectory within the repo, e.g. `"skills/docx"` |

If `gitURL` is specified, at least one of `gitBranch` or `gitTag` must be provided.

**Field ordering in manifest.json:**
`id`, `kind`, `name`, `description`, `author`, `tags`, `iconSF`, `featured`, `version`, then optional fields: `homepageURL`, `mcpTransport`, `mcpInstallCommand`, `mcpInstallArgs`, `mcpUrl`, `requiresEnvVars`, `gitURL`, `gitBranch`, `gitTag`, `gitPath`.

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
AUTHOR=$(gh api user -q '.login')
UPSTREAM_REPO="markgravity/claudy-registry"

# Check if user has push access to upstream (owner/collaborator vs. contributor)
HAS_PUSH=$(gh api "repos/$UPSTREAM_REPO" --jq '.permissions.push // false' 2>/dev/null)

# Locate existing local clone (fork or upstream)
REGISTRY=$(find ~ -maxdepth 6 -type d -name "claudy-registry" 2>/dev/null | while read dir; do
  git -C "$dir" remote get-url origin 2>/dev/null | grep -q "claudy-registry" && echo "$dir" && break
done | head -1)

if [ "$HAS_PUSH" = "true" ]; then
  # Collaborator: push directly to upstream
  PUSH_REPO="$UPSTREAM_REPO"
  if [ -z "$REGISTRY" ]; then echo "claudy-registry not found locally. Please clone it first."; exit 1; fi
  cd "$REGISTRY" && git checkout main && git pull origin main
else
  # Contributor: fork workflow
  PUSH_REPO="${AUTHOR}/claudy-registry"

  # Create fork if it doesn't exist yet
  gh repo fork "$UPSTREAM_REPO" --clone=false 2>/dev/null || true

  if [ -z "$REGISTRY" ]; then
    # No local clone — clone the fork
    REGISTRY=~/claudy-registry
    gh repo clone "$PUSH_REPO" "$REGISTRY"
  fi

  cd "$REGISTRY"

  # Ensure upstream remote exists for syncing
  git remote get-url upstream 2>/dev/null || \
    git remote add upstream "https://github.com/$UPSTREAM_REPO.git"

  # Sync fork's main with upstream
  git fetch upstream
  git checkout main && git merge upstream/main
fi

SLUG="{slug}"  # lowercase plugin name, no @org suffix
git checkout -b "plugin/${AUTHOR}/${SLUG}"
mkdir -p "plugins/${AUTHOR}/${SLUG}"
```

Write `manifest.json` to `plugins/{author}/{slug}/manifest.json` using the Write tool. For inline plugins use `gitURL: "https://github.com/$UPSTREAM_REPO"`, `gitBranch: "main"`, `gitPath: "plugins/{author}/{slug}"` (where files land after merge). Copy any `.md` source files if inline.

Validate before committing:
```bash
python scripts/validate_plugin.py "plugins/{author}/{slug}/manifest.json"
```

If validation fails, fix `manifest.json` and re-validate before proceeding.

Commit and push:
```bash
git add "plugins/{author}/{slug}/"
git commit -m "feat: add {name}"
git push origin "plugin/{author}/{slug}"
```

Open the PR targeting upstream:
```bash
gh pr create \
  --repo "$UPSTREAM_REPO" \
  --head "${AUTHOR}:plugin/${AUTHOR}/${SLUG}" \
  --base main \
  --title "[Plugin] Add {Name} {Kind label}" \
  --body "$(cat <<'EOF'
## Plugin Submission

Adds **{Name}** to the Claudy marketplace.

- **Kind:** {kind}
- **Author:** {author}
- **Source:** {github-url or local path}

## Checklist
- [ ] `manifest.json` validates against schema
- [ ] `id` is `{slug}@{author}` matching directory path
- [ ] `author` matches org directory
- [ ] `version` is `"1.0.0"`
EOF
)"
```

Return the PR URL when done.
