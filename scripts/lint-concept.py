#!/usr/bin/env python3
"""Lint a concept markdown file against the ML-Wiki template rules.

Usage: python3 scripts/lint-concept.py wiki/foo.md
Exit code: 0 = pass, 1 = fail
"""

import sys
import os
import re

REQUIRED_H2 = ["## The Core Idea", "## How It Works", "## Interview Angle"]


def lint(path):
    errors = []

    abs_path = path if os.path.isabs(path) else os.path.join(os.getcwd(), path)

    if not os.path.exists(abs_path):
        print(f"FAIL {path}")
        print(f"  ERROR: file not found: {abs_path}")
        return 1

    with open(abs_path) as f:
        text = f.read()

    # --- No frontmatter ---
    if text.startswith("---"):
        errors.append("File must not start with YAML frontmatter (remove the '---' block)")

    # --- h1 title present ---
    if not re.search(r"^# .+", text, re.MULTILINE):
        errors.append("Missing h1 title (e.g. '# Attention')")

    # --- TIP callout present ---
    if "> [!TIP]" not in text:
        errors.append("Missing '> [!TIP]' callout after the h1 title")

    # --- Exactly 3 h2 headings in correct order ---
    h2_headings = re.findall(r"^## .+", text, re.MULTILINE)

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
        print("Usage: python3 scripts/lint-concept.py <path-to-wiki-page.md>")
        sys.exit(1)
    sys.exit(lint(sys.argv[1]))
