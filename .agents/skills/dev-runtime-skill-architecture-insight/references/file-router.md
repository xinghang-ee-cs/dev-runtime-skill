# File Router

Open the smallest listed set for the requested change.

## 1. CLI syntax, command names, or new subcommands

- `scripts/runtime-skills.py`
- `tests/test_runtime_skills.py`
- `src/content/docs/reference/versioning-and-updates.md`

Reason: the synchronization CLI owns parsing and behavior; tests and reference docs own its public contract.

## 2. Install, download, or version-resolution flow

- `scripts/runtime-skills.py`
- `scripts/select-obsolete-patch-tags.py` when changing public PATCH retention
- `skills-manifest.json`
- `tests/test_runtime_skills.py`
- `tests/test_release_retention.py` when changing public PATCH retention
- `.github/workflows/release-skills.yml`

Reason: these files own source resolution, managed deployment, lock generation, Release publication, and archival of superseded PATCH records.

## 3. Version switching, paths, or environment setup

- `scripts/runtime-skills.py`
- `AGENTS.md`
- `src/content/docs/reference/versioning-and-updates.md`

Reason: this repository has no shim manager; destination normalization, phase pinning, and environment guidance are the corresponding contracts.

## 4. Runtime data directory or layout changes

- The owning `skills/<skill-name>/SKILL.md`
- That Skill's `references/` and `assets/`
- Cross-runtime validators under `tests/`

Reason: Runtime locations and ownership are defined by each Skill and protected by contract tests.

## 5. One-click installation or orchestrated flow

- `README.md`
- `README.zh-CN.md`
- `scripts/runtime-skills.py`
- `AGENTS.md`

Reason: README prompts guide the Agent, while the tool and repository rules enforce installation behavior.

## 6. Dependency or package management

- `package.json`
- `package-lock.json`
- `astro.config.mjs`
- `.github/workflows/deploy-docs.yml`

Reason: these files own the documentation site's Node and Astro dependency surface.

## 7. Error diagnostics and user guidance

- `README.md`
- `README.zh-CN.md`
- `src/content/docs/`
- The emitting script or validator

Reason: keep user guidance synchronized with the actual validation or runtime behavior.

## 8. Security review hotspots

- `scripts/runtime-skills.py` for download, archive extraction, paths, and transactional writes
- `.github/workflows/release-skills.yml` for token permissions and tag publication
- `skills/*/SKILL.md` for authorization and destructive-operation boundaries
- `AGENTS.md` for GitHub and credential-handling rules

Focus checks:

- reject path traversal and unsafe extraction
- avoid credential output or persistence
- preserve destination-root containment
- prevent local-drift overwrite without confirmation
- keep database, deployment, and Git writes behind explicit authorization

## 9. Tests and fast verification

- `scripts/validate-skill-manifest.py`
- `tests/`
- `package.json`
- `.github/workflows/validate-skills.yml`

Run:

- `python scripts/validate-skill-manifest.py --compare-ref origin/main`
- `python -m unittest discover -s tests -p "test_*.py"`
- `npm run check`
- `npm run build`
