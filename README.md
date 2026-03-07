# claudy-registry

Community plugin registry for the [Claudy](https://github.com/markgravity/Claudy) macOS app.

Plugins appear in the Claudy marketplace. Contributors open PRs — on merge, plugins are automatically synced to Firestore.

## Plugin Types

| Kind | Description |
|------|-------------|
| `mcp` | MCP server (stdio or HTTP transport) |
| `skill` | Claude Code skill (`.md` file) |
| `command` | Claude Code slash command (`.md` file) |

## Quickstart

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/claudy-registry
cd claudy-registry

# 2. Create your plugin directory
mkdir -p plugins/YOUR_USERNAME/your-plugin-id

# 3. Create plugin.json (see CONTRIBUTING.md for all fields)
cat > plugins/YOUR_USERNAME/your-plugin-id/plugin.json << 'EOF'
{
  "id": "your-plugin-id",
  "marketplaceId": "YOUR_USERNAME/your-plugin-id",
  "kind": "mcp",
  "name": "Your Plugin Name",
  "description": "What your plugin does in one sentence.",
  "author": "YOUR_USERNAME",
  "tags": ["your", "tags"],
  "iconSF": "gear",
  "featured": false,
  "mcpTransport": "stdio",
  "mcpInstallCommand": "npx",
  "mcpInstallArgs": ["-y", "@scope/your-package@latest"]
}
EOF

# 4. Validate locally
pip install -r scripts/requirements.txt
python scripts/validate_plugin.py plugins/YOUR_USERNAME/your-plugin-id/plugin.json

# 5. Open a PR
```

## Repository Structure

```
plugins/
└── {author}/
    └── {plugin-id}/
        ├── plugin.json    ← required
        └── *.md           ← required for inline skill/command plugins
schema/
└── plugin.schema.json     ← JSON Schema (source of truth)
scripts/
├── validate_plugin.py     ← run locally or used by CI
├── sync_to_firestore.py   ← full sync on every merge to main
└── requirements.txt
```

## CI

- **PR opened** → validates all changed `plugin.json` files
- **Merged to main** → syncs all plugins to Firestore (`claudy-129fe`, collection `plugins`)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full field reference, examples, and review process.
