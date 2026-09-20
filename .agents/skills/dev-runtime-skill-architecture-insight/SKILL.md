---
name: dev-runtime-skill-architecture-insight
description: Fast architecture and file-routing guide for maintaining dev-runtime-skill. Use before changing Runtime Skill governance, version synchronization, release workflows, validators, or documentation.
---

# Dev Runtime Skill Architecture Insight

Use this repository-local Skill to minimize discovery before edits. It is not one of the four distributable Runtime Skills under `skills/`.

## Route in 30 seconds

1. Read `AGENTS.md` for repository governance and GitHub delivery rules.
2. Read `skills-manifest.json` for bundle, tool, and Skill versions.
3. Open only the owning Skill `SKILL.md`, script, workflow, or documentation entry.
4. Use `references/file-router.md` to select the smallest file set.

## Core module boundaries

- Keep distributable Runtime governance under `skills/<skill-name>/`.
- Keep versioned installation and synchronization in `scripts/runtime-skills.py`.
- Keep manifest and version policy in `skills-manifest.json` and `scripts/validate-skill-manifest.py`.
- Keep documentation-site code under `src/`, `public/`, and Astro configuration.
- Keep project-specific Runtime state out of distributable Skill packages.

## Architectural invariants

- Treat `skills-manifest.json` as the only version source.
- Keep each Skill's `SKILL.md` as its Runtime Governance Source.
- Do not mix target-project facts into shared Skills.
- Preserve Planning, Long, Testing, and Inspection ownership boundaries.
- Deliver GitHub changes through Issue, dedicated branch, PR, CI, and PR merge.

## Edit workflow

1. Choose a scenario from `references/file-router.md`.
2. Read only the listed owners and direct tests.
3. Change the lowest owning layer without duplicating contracts.
4. Update required bundle, tool, or Skill versions.
5. Run manifest validation, Python tests, and documentation checks as applicable.

## Search shortcuts

- `rg -n "release_version|repository.*channel|version" skills-manifest.json scripts README* src`
- `rg -n "Archive superseded|obsolete_patch_tags|--draft" .github scripts tests README* src`
- `rg -n "add_parser|command_install|command_sync|command_update" scripts/runtime-skills.py`
- `rg -n "planning_baseline_revision|ready_for_local_test|bugfix-case" skills tests`
- `rg -n "^## |^### " skills -g SKILL.md; rg -n "^## |^### " README.md README.zh-CN.md`
- `rg -n "validate|unittest|npm run" .github/workflows tests package.json`
