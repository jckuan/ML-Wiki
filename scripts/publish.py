#!/usr/bin/env python3
"""Publish the next ready concept from the topic queue.

Usage: python3 scripts/publish.py
Exit code: 0 = published (or nothing to publish), 1 = error
"""

import sys
import os
import subprocess
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPICS_YAML = os.path.join(REPO_ROOT, "topics.yaml")
README_PATH = os.path.join(REPO_ROOT, "README.md")


def parse_yaml_queue(text):
    """Parse topics.yaml queue entries using regex (no pyyaml dependency)."""
    entries = []
    blocks = re.split(r'\n(?=  - slug:)', text)
    for block in blocks:
        slug_m = re.search(r'slug:\s*["\']?([^"\'\n]+)["\']?', block)
        title_m = re.search(r'title:\s*["\']([^"\']+)["\']', block)
        tags_m = re.search(r'tags:\s*\[([^\]]+)\]', block)
        status_m = re.search(r'status:\s*([^\s#\n]+)', block)
        if not slug_m or not status_m:
            continue
        entries.append({
            "slug": slug_m.group(1).strip(),
            "title": title_m.group(1).strip() if title_m else slug_m.group(1).strip(),
            "tags": [t.strip().strip('"\'') for t in tags_m.group(1).split(",")] if tags_m else [],
            "status": status_m.group(1).strip(),
        })
    return entries


def build_table(entries):
    """Build markdown table rows for all published entries."""
    lines = [
        "| Concept | Tags |",
        "|---------|------|",
    ]
    for e in entries:
        if e["status"] != "published":
            continue
        tags_str = " ".join(f"`{t}`" for t in e["tags"])
        lines.append(f"| [{e['title']}](wiki/{e['slug']}.md) | {tags_str} |")
    return "\n".join(lines)


def rebuild_readme(entries):
    """Replace content between sentinel comments with fresh table."""
    with open(README_PATH) as f:
        content = f.read()

    table = build_table(entries)
    start_sentinel = "<!-- CONCEPTS_TABLE_START -->"
    end_sentinel = "<!-- CONCEPTS_TABLE_END -->"

    if start_sentinel in content and end_sentinel in content:
        start_idx = content.index(start_sentinel) + len(start_sentinel)
        end_idx = content.index(end_sentinel)
        new_content = content[:start_idx] + "\n\n" + table + "\n\n" + content[end_idx:]
    else:
        new_content = content.rstrip() + "\n\n## Concepts\n\n" + start_sentinel + "\n\n" + table + "\n\n" + end_sentinel + "\n"

    with open(README_PATH, "w") as f:
        f.write(new_content)


def main():
    if not os.path.exists(TOPICS_YAML):
        print(f"ERROR: topics.yaml not found at {TOPICS_YAML}")
        return 1

    with open(TOPICS_YAML) as f:
        yaml_text = f.read()

    entries = parse_yaml_queue(yaml_text)
    if not entries:
        print("ERROR: Could not parse topics.yaml")
        return 1

    target = next((e for e in entries if e["status"] == "ready"), None)
    if target is None:
        print("No topics ready to publish.")
        return 0

    slug = target["slug"]
    wiki_path = os.path.join(REPO_ROOT, "wiki", f"{slug}.md")

    if not os.path.exists(wiki_path):
        print(f"ERROR: wiki page not found: {wiki_path}")
        return 1

    # Lint
    lint_script = os.path.join(REPO_ROOT, "scripts", "lint-concept.py")
    result = subprocess.run(
        [sys.executable, lint_script, wiki_path],
        capture_output=True, text=True
    )
    print(result.stdout, end="")
    if result.returncode != 0:
        print(result.stderr, end="")
        print(f"ERROR: Lint failed for {wiki_path}")
        return 1

    # Mark published in topics.yaml
    yq_result = subprocess.run(
        ["yq", "e", f'(.queue[] | select(.slug == "{slug}") | .status) = "published"', "-i", TOPICS_YAML],
        capture_output=True, text=True
    )
    if yq_result.returncode != 0:
        new_yaml = re.sub(
            rf'(slug:\s*["\']?{re.escape(slug)}["\']?.*?\n(?:.*?\n)*?\s+status:)\s*ready',
            r'\1 published',
            yaml_text,
            flags=re.DOTALL,
            count=1,
        )
        with open(TOPICS_YAML, "w") as f:
            f.write(new_yaml)

    # Rebuild README table
    with open(TOPICS_YAML) as f:
        yaml_text = f.read()
    entries = parse_yaml_queue(yaml_text)
    rebuild_readme(entries)
    print("README updated with concepts table.")

    print(f"Published: {slug}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
