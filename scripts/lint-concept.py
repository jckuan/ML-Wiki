#!/usr/bin/env python3
"""Lint a concept markdown file against the ML-Wiki template rules.

Usage: python3 scripts/lint-concept.py wiki/foo.md
Exit code: 0 = pass, 1 = fail
"""

import sys
import os
import re

REQUIRED_FIELDS = ["title", "tags"]
REQUIRED_H2 = ["## The Core Idea", "## How It Works", "## Interview Angle"]


def parse_frontmatter(text):
    """Return (frontmatter_dict, body) or raise ValueError."""
    if not text.startswith("---"):
        raise ValueError("File does not start with YAML frontmatter delimiter '---'")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("Frontmatter closing '---' not found")
    fm_text = text[3:end].strip()
    body = text[end + 4:].strip()

    # Simple YAML parser for flat key: value and key: [list] structures
    fields = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if val.startswith("[") and val.endswith("]"):
            val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",")]
        fields[key] = val
    return fields, body


def lint(path):
    errors = []

    # Resolve path relative to repo root (script can be run from anywhere)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    abs_path = path if os.path.isabs(path) else os.path.join(os.getcwd(), path)

    if not os.path.exists(abs_path):
        print(f"FAIL {path}")
        print(f"  ERROR: file not found: {abs_path}")
        return 1

    with open(abs_path) as f:
        text = f.read()

    # --- Frontmatter ---
    try:
        fm, body = parse_frontmatter(text)
    except ValueError as e:
        print(f"FAIL {path}")
        print(f"  ERROR: {e}")
        return 1

    for field in REQUIRED_FIELDS:
        if field not in fm or not fm[field]:
            errors.append(f"Missing required frontmatter field: '{field}'")

    # --- Image path exists ---
    if "image_path" in fm and fm["image_path"]:
        img_path = os.path.join(repo_root, fm["image_path"])
        if not os.path.exists(img_path):
            errors.append(f"image_path '{fm['image_path']}' does not exist on disk (checked: {img_path})")

    # --- Exactly 3 h2 headings in correct order ---
    h2_pattern = re.compile(r"^## .+", re.MULTILINE)
    h2_headings = h2_pattern.findall(text)

    if len(h2_headings) != 3:
        errors.append(f"Expected exactly 3 h2 headings, found {len(h2_headings)}: {h2_headings}")
    else:
        for i, (found, expected) in enumerate(zip(h2_headings, REQUIRED_H2)):
            if found.strip() != expected:
                errors.append(f"h2 heading {i+1}: expected '{expected}', got '{found.strip()}'")

    if errors:
        print(f"FAIL {path}")
        for e in errors:
            print(f"  ERROR: {e}")
        return 1

    print(f"PASS {path}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/lint-concept.py <path-to-concept.md>")
        sys.exit(1)
    sys.exit(lint(sys.argv[1]))
