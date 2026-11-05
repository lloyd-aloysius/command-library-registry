# Command library registry

Version-controlled command packs for Command Launcher. `categories.json` is the catalogue; each published category has `<category-id>/commands.json`.

## Availability

A category includes `id`, `name`, `iconName` and `available`. `available: true` means its commands file is published. `available: false` reserves an unpublished pack in the catalogue, so clients can label it without requesting a missing file. To publish a pack, add its valid commands file and set `available` to true in the same change. The current catalogue has 64 published packs (260 commands) and 71 unpublished entries.

Existing clients that ignore the optional availability field can still read published packs. Command Launcher 1.1 understands it and avoids repeated 404 requests for unpublished packs.

## Commands

Each command needs a unique `id` within its pack, a `title` and the exact `command` text. Optional fields: `description`, `tags`, `risk`, `documentationURL` (credential-free HTTPS), and `parameters`.

A parameter matches a `<name>` placeholder and has `name`, optional `label`, `required` (default true) and `secret` (default false). For example:

```json
{
  "id": "clone",
  "title": "Clone repository",
  "command": "git clone <url>",
  "description": "Clone into a new directory",
  "parameters": [{ "name": "url", "label": "Repository URL", "required": true }]
}
```

Commands are data for review and copying; importing a pack does not execute commands.

## Validation

Run from the repository root with Python 3.9+:

```sh
python3 scripts/validate_registry.py
```

This offline check rejects missing files for published categories, false unavailable flags for existing packs, duplicate/path-unsafe category IDs, duplicate command IDs, invalid required fields, oversized commands, unsafe documentation links and mismatched parameter metadata. Update this validator and the client's schema together when changing the format.
