# Contributing to claudy-registry

Thank you for contributing to the Claudy plugin marketplace!

## How to Submit a Plugin

1. **Fork** this repository
2. **Create** your plugin directory: `plugins/{your-github-username}/{plugin-id}/`
3. **Add** a `plugin.json` (see field reference below)
4. **For inline plugins** — add source files (`.md`) alongside `plugin.json`
5. **Open a PR** — CI will validate your plugin automatically

---

## Plugin Directory Structure

```
plugins/
└── {author}/           ← your GitHub username
    └── {plugin-id}/    ← lowercase alphanumeric + hyphens
        ├── plugin.json
        └── skill.md    ← inline only (skill/command)
```

---

## Field Reference

### Required (all kinds)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Must match directory name. Lowercase alphanumeric + hyphens. |
| `marketplaceId` | string | Must be `{author}/{id}`. |
| `kind` | string | `"mcp"`, `"skill"`, or `"command"` |
| `name` | string | Display name. 2–60 characters. |
| `description` | string | What it does. 10–200 characters. |
| `author` | string | Must match parent directory (your GitHub username). |
| `tags` | array of strings | At least one tag. Used for search. |
| `iconSF` | string | SF Symbols name (e.g. `"gear"`, `"network"`). |
| `featured` | boolean | Set to `false` for community submissions. |

### MCP plugins (`kind: "mcp"`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mcpTransport` | string | Yes | `"stdio"` or `"http"` |
| `mcpInstallCommand` | string | stdio | Command to install/run (e.g. `"npx"`, `"uvx"`) |
| `mcpInstallArgs` | array | stdio | Args for install command |
| `mcpUrl` | string (URI) | http | URL for the HTTP MCP server |

### File-based plugins (skill/command)

| Field | Type | Description |
|-------|------|-------------|
| `githubRepo` | string | `"owner/repo"` format |
| `githubPath` | string | Path to plugin files within the repo |

**External reference** — source lives in another repo:
```json
{
  "githubRepo": "someuser/their-repo",
  "githubPath": "path/to/skill"
}
```

**Inline** — source files live in this registry:
```json
{
  "githubRepo": "markgravity/claudy-registry",
  "githubPath": "plugins/{author}/{id}"
}
```

> Include the `.md` source file alongside `plugin.json` for inline plugins.

---

## Forbidden Fields

Never include these in `plugin.json` — they are managed by Firestore:

- `installCount`
- `averageRating`
- `ratingCount`
- `ratingSum`

CI will reject any plugin containing these fields.

---

## Example: External MCP Plugin

```json
{
  "id": "my-mcp-server",
  "marketplaceId": "myusername/my-mcp-server",
  "kind": "mcp",
  "name": "My MCP Server",
  "description": "Does something useful via the Model Context Protocol.",
  "author": "myusername",
  "tags": ["mcp", "utility"],
  "iconSF": "network",
  "featured": false,
  "mcpTransport": "stdio",
  "mcpInstallCommand": "npx",
  "mcpInstallArgs": ["-y", "@myusername/my-mcp-server@latest"]
}
```

## Example: Inline Skill

`plugins/myusername/my-skill/plugin.json`:
```json
{
  "id": "my-skill",
  "marketplaceId": "myusername/my-skill",
  "kind": "skill",
  "name": "My Skill",
  "description": "A helpful skill that does something great.",
  "author": "myusername",
  "tags": ["productivity"],
  "iconSF": "wand.and.stars",
  "featured": false,
  "githubRepo": "markgravity/claudy-registry",
  "githubPath": "plugins/myusername/my-skill"
}
```

`plugins/myusername/my-skill/skill.md`:
```markdown
Your skill prompt content here...
```

---

## Validation

Run the validator locally before opening a PR:

```bash
pip install -r scripts/requirements.txt
python scripts/validate_plugin.py plugins/myusername/my-skill/plugin.json
```

---

## SF Symbols Reference

Pick an icon name from [SF Symbols](https://developer.apple.com/sf-symbols/). Common ones:
- `gear` — settings/config
- `network` — networking/MCP
- `wand.and.stars` — AI/generation
- `terminal` — CLI tools
- `doc.text` — documentation
- `magnifyingglass` — search

---

## Review Process

1. CI validates your `plugin.json` automatically
2. A maintainer reviews the PR
3. On merge, the plugin is automatically synced to Firestore and appears in the Claudy app
