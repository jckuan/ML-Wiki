# ML-Wiki Design

## Current Workflow

**Content creation (local)**
1. Run `/write-ml-wiki` — researches the concept, writes `wiki/{slug}.md`, sets `status: draft` in `topics.yaml`
2. Review and edit the draft; add images to `assets/`
3. Set `status: ready` in `topics.yaml` and push

**Publishing (automated)**
- GitHub Actions runs every Monday 9am UTC
- Finds the first `status: ready` entry (FIFO), lints it, marks it `published`, rebuilds the README table, commits and pushes

---

## Problem Statement

A GitHub repository of ML concepts optimized for interview prep and quick review. Not a course, not a link dump — inline explainers with an interview angle.

The gap: every existing ML repo assumes you're learning from scratch. This is built for "I have 30 minutes before a technical screen and need to reconstruct how attention works."

---

## Content Format

Each concept lives in `wiki/{slug}.md`. Structure is fixed:

```markdown
# {Concept Name}

> [!TIP]
> One-sentence intuition.

## The Core Idea
{150-250 words. Problem first, then intuition. Image below.}

<p align="center">
  <img src="../assets/{slug}_1.png" alt="{alt}" style="height: 240px;">
  <br>
  <em>Source: <a href="{URL}">{Source Name}</a></em>
</p>

## How It Works
{150-250 words. Mechanism via numbered steps. Math inline ($formula$) or block:}

$$
{formula}
$$

## Interview Angle

**What gets asked:** ...
**What trips people up:** ...
**A great answer:** ...
```

**Rules:**
- No frontmatter
- Exactly 3 h2 headings in that order
- No AI-generated images — always cite the source
- Block math: `$$` on its own line

---

## Pipeline

### topics.yaml

Single source of truth for the queue. Status lifecycle: `queued → draft → ready → published`

```yaml
queue:
  - slug: batch-normalization
    title: "Batch Normalization"
    tags: [Training]
    status: queued
```

Tags: `Fundamentals`, `Architectures`, `Training`, `Inference`

### scripts/publish.py

Finds the first `ready` entry, lints `wiki/{slug}.md`, marks it `published`, rebuilds the README concepts table from `topics.yaml`.

### .github/workflows/publish.yml

Runs weekly (Monday 9am UTC) or on `workflow_dispatch`. Calls `publish.py`, commits and pushes if a concept was published.

```yaml
permissions:
  contents: write
concurrency:
  group: publish
  cancel-in-progress: true
```

### scripts/lint-concept.py

Validates: h1 present, `> [!TIP]` callout present, exactly 3 h2 headings in correct order, no frontmatter.

---

## Repository Structure

```
wiki/           # Published and in-progress concept pages
assets/         # Source images (cited, no AI-generated)
scripts/
  lint-concept.py
  publish.py
.github/workflows/publish.yml
topics.yaml
template.md
README.md       # Concepts table (auto-rebuilt on publish)
docs/design.md
```

---

## Distribution

- **GitHub**: primary destination. README as tagged index.
- **Instagram**: carousel posts (10-slide) + Reels (teaser). Pipeline deferred — manual posting for now.

---

## Open Questions

1. **Instagram carousel pipeline**: slide design and rendering not yet built. Manual Canva posting until ready.
2. **Topic curation**: fully manual for now. Claude suggests topics via `/write-ml-wiki` but the queue is human-curated.

---

## Success Criteria

- [ ] 20+ concepts in `wiki/`, all tagged and linked in README
- [ ] GitHub Actions publishes on schedule without manual intervention
- [ ] Every concept passes lint
- [ ] At least one Instagram carousel posted and linked back to GitHub
- [ ] Repo is the first place you open before a technical screen
