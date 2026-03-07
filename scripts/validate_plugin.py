#!/usr/bin/env python3
"""
validate_plugin.py — Validate a Claudy plugin.json file.

Usage:
    python scripts/validate_plugin.py plugins/author/plugin-id/plugin.json [...]

Exits 0 if all files are valid, 1 if any fail.
"""

import json
import os
import sys
from pathlib import Path

import jsonschema

STATS_FIELDS = {"installCount", "averageRating", "ratingCount", "ratingSum"}
SCHEMA_PATH = Path(__file__).parent.parent / "schema" / "plugin.schema.json"


def load_schema() -> dict:
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def validate(plugin_path: str, schema: dict) -> list[str]:
    """Return a list of error strings (empty = valid)."""
    errors = []
    path = Path(plugin_path)

    # 1. Valid JSON
    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]
    except FileNotFoundError:
        return [f"File not found: {plugin_path}"]

    # 2. No stats fields
    found_stats = STATS_FIELDS & set(data.keys())
    if found_stats:
        errors.append(f"Stats fields must not appear in plugin.json: {sorted(found_stats)}")

    # 3. JSON Schema compliance
    validator = jsonschema.Draft7Validator(schema)
    schema_errors = list(validator.iter_errors(data))
    for e in schema_errors:
        field = " -> ".join(str(p) for p in e.absolute_path) or "(root)"
        errors.append(f"Schema error at {field}: {e.message}")

    if errors:
        # Stop early — structural errors make further checks unreliable
        return errors

    # Derive expected author and id from path: plugins/{author}/{id}/plugin.json
    parts = path.parts
    try:
        plugins_idx = next(i for i, p in enumerate(parts) if p == "plugins")
        expected_author = parts[plugins_idx + 1]
        expected_id = parts[plugins_idx + 2]
    except (StopIteration, IndexError):
        errors.append("plugin.json must be located at plugins/{author}/{id}/plugin.json")
        return errors

    # 4. id matches directory name
    if data.get("id") != expected_id:
        errors.append(f"'id' must match directory name '{expected_id}', got '{data.get('id')}'")

    # 5. author matches parent directory
    if data.get("author") != expected_author:
        errors.append(
            f"'author' must match parent directory '{expected_author}', got '{data.get('author')}'"
        )

    kind = data.get("kind")
    transport = data.get("mcpTransport")

    # 6. MCP stdio requires mcpInstallCommand
    if kind == "mcp" and transport == "stdio" and not data.get("mcpInstallCommand"):
        errors.append("MCP stdio plugins require 'mcpInstallCommand'")

    # 7. MCP http requires mcpUrl
    if kind == "mcp" and transport == "http" and not data.get("mcpUrl"):
        errors.append("MCP http plugins require 'mcpUrl'")

    # 8. MCP requires mcpTransport (already covered by schema, but explicit here)
    if kind == "mcp" and not transport:
        errors.append("MCP plugins require 'mcpTransport'")

    github_repo = data.get("githubRepo")
    github_path = data.get("githubPath")

    # 9. Inline githubPath must equal plugins/{author}/{id}
    is_inline = github_repo == "markgravity/claudy-registry"
    expected_github_path = f"plugins/{expected_author}/{expected_id}"
    if is_inline and github_path != expected_github_path:
        errors.append(
            f"Inline plugin 'githubPath' must be '{expected_github_path}', got '{github_path}'"
        )

    plugin_dir = path.parent

    # 10. Inline skill/command must have source files
    if is_inline and kind in ("skill", "command"):
        source_files = list(plugin_dir.glob("*.md"))
        if not source_files:
            errors.append(
                f"Inline {kind} plugin must include at least one .md source file in {plugin_dir}"
            )

    # 11. Inline command must have a .md file (already covered by 10, but explicit)
    # (No additional check needed beyond #10)

    # 12. githubPath required when githubRepo set
    if github_repo and not github_path:
        errors.append("'githubPath' is required when 'githubRepo' is set")

    # 13. id format: lowercase alphanumeric + hyphens
    import re
    if data.get("id") and not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$", data["id"]):
        errors.append(
            f"'id' must be lowercase alphanumeric with hyphens only, got '{data['id']}'"
        )

    # 14. name length: 2–60 chars (also covered by schema)
    name = data.get("name", "")
    if not (2 <= len(name) <= 60):
        errors.append(f"'name' must be 2–60 characters, got {len(name)}")

    # 15. description length: 10–200 chars (also covered by schema)
    desc = data.get("description", "")
    if not (10 <= len(desc) <= 200):
        errors.append(f"'description' must be 10–200 characters, got {len(desc)}")

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_plugin.py <plugin.json> [...]", file=sys.stderr)
        sys.exit(1)

    schema = load_schema()
    all_valid = True

    for plugin_path in sys.argv[1:]:
        errors = validate(plugin_path, schema)
        if errors:
            all_valid = False
            print(f"FAIL: {plugin_path}", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
        else:
            print(f"OK:   {plugin_path}")

    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
