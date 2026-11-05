#!/usr/bin/env python3
"""Validate registry references and command schemas without network access."""
import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse


def validate(root):
    errors, seen, published, unpublished, count = [], set(), 0, 0, 0
    try:
        categories = json.loads((root / "categories.json").read_text())
        if not isinstance(categories, list) or not categories:
            return ["categories.json must be a non-empty array"], {}
        for category in categories:
            category_id = category.get("id", "")
            if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", category_id) or category_id in seen:
                errors.append(f"Invalid or duplicate category ID: {category_id}")
                continue
            seen.add(category_id)
            if not all(isinstance(category.get(key), str) and category[key].strip() for key in ("name", "iconName")):
                errors.append(f"{category_id}: name and iconName are required")
            source = root / category_id / "commands.json"
            if category.get("available") is False:
                unpublished += 1
                if source.is_file():
                    errors.append(f"{category_id}: has a commands file but is marked unavailable")
                continue
            published += 1
            if not source.is_file():
                errors.append(f"{category_id}: missing commands.json; publish the pack or set available=false")
                continue
            commands = json.loads(source.read_text())
            if not isinstance(commands, list) or len(commands) > 10000:
                errors.append(f"{category_id}: commands must be an array with at most 10,000 entries")
                continue
            ids = set()
            for command in commands:
                if not isinstance(command, dict) or any(not isinstance(command.get(key), str) or not command[key].strip() for key in ("id", "title", "command")):
                    errors.append(f"{category_id}: command missing required string fields")
                    continue
                if command["id"] in ids:
                    errors.append(f'{category_id}: duplicate command ID {command["id"]}')
                ids.add(command["id"])
                if len(command["id"]) > 240 or len(command["title"]) > 300 or len(command["command"]) > 32768:
                    errors.append(f'{category_id}/{command["id"]}: oversized required field')
                if command.get("documentationURL"):
                    url = urlparse(command["documentationURL"])
                    if url.scheme != "https" or not url.hostname or url.username or url.password:
                        errors.append(f'{category_id}/{command["id"]}: documentationURL must be credential-free HTTPS')
                parameters = command.get("parameters", [])
                names = [parameter.get("name") for parameter in parameters]
                tokens = set(re.findall(r"<([A-Za-z][A-Za-z0-9_.-]*)>", command["command"]))
                if len(names) != len(set(names)) or any(name not in tokens for name in names):
                    errors.append(f'{category_id}/{command["id"]}: parameter names must uniquely match placeholders')
            count += len(commands)
    except (OSError, ValueError, TypeError, AttributeError) as error:
        errors.append(str(error))
    return errors, {"published_packs": published, "unpublished_packs": unpublished, "commands": count}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", nargs="?", type=Path, default=Path("."))
    args = parser.parse_args()
    errors, summary = validate(args.registry)
    print(json.dumps({**summary, "errors": errors}, indent=2))
    sys.exit(bool(errors))
