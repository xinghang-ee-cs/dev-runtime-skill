# AI Development Runtime Skills

[English](README.md) | [简体中文](README.zh-CN.md)

A project-neutral set of Agent Skills for planning, implementation, testing, and code inspection. The repository contains reusable governance only; project-specific commands, credentials, paths, and environment facts stay in the target project.

## Quick install

The easiest option is to send this prompt to the Agent working in the target project:

```text
Install Runtime Skills in the current project from https://github.com/xinghang-ee-cs/dev-runtime-skill.
Skills: planning-layer-runtime, long-task-orchestrator, testing-layer-runtime, ai-code-inspection

Inspect the current execution platform, project instruction files, and existing Skill directories to determine every Agent platform and installation destination used by this project. Do not ask me to choose a platform: use .agents/skills for Codex; use .claude/skills for Claude Code; for GitHub Copilot, reuse an existing supported project directory and use .agents/skills when sharing with Codex. When evidence shows multiple platforms, install every destination in one operation.

If the source repository is not local, obtain its latest stable Release in a temporary directory. From the source repository run:
python scripts/runtime-skills.py install --release latest --project "<target-project-root>" --skill planning-layer-runtime --skill long-task-orchestrator --skill testing-layer-runtime --skill ai-code-inspection --destination "<automatically-detected Skill root>"
Repeat --destination for every detected installation directory. Then merge the applicable AGENTS.md rules and, when Claude Code is detected, maintain the CLAUDE.md import of AGENTS.md. Finish with:
python "<target-project-root>/.runtime-skills/runtime-skills.py" verify --project "<target-project-root>"
Report the detected platforms, destinations, Release, Skill versions, and verify result. Do not modify business code, deploy, commit, or push.
```

The AI must perform platform detection, destination selection, installation, and verification itself. See the [detailed installation guide](#install-in-an-agent-project) for partial installations and existing-project migration.

## Start in one sentence

After installation, send this in the target project:

```text
Use the Skills to start the first development phase for me.
```

Only the selected directories under `skills/` are installable Skill packages. `AGENTS.md` is the reusable project-entry template. `src/`, `public/`, `package*.json`, `astro.config.mjs`, `tsconfig.json`, and the documentation deployment workflow belong to this repository's Astro/Starlight documentation site and must not be copied into a target project. The version in `package.json` belongs to the documentation site and is not a Skill version.

## The four skills

| Skill | Use it for | Boundary |
| --- | --- | --- |
| [`planning-layer-runtime`](skills/planning-layer-runtime/SKILL.md) | Discover requirements, freeze an execution baseline, produce handoffs, and govern whether a defect can bypass Planning. | Does not write production code or execute tests; Fast Lane never edits the original 00–15. |
| [`long-task-orchestrator`](skills/long-task-orchestrator/SKILL.md) | Implement approved features with at least four units, or consume a confirmed Bugfix Case for a smaller exact patch. | Does not perform manual acceptance or absorb contract changes. |
| [`testing-layer-runtime`](skills/testing-layer-runtime/SKILL.md) | Manage phase acceptance plus Bugfix verification, production retest, and post-release similar-defect review. | Does not change business code or approve production release. |
| [`ai-code-inspection`](skills/ai-code-inspection/SKILL.md) | Route ten review/diagnosis scenarios and create the durable Bug Contract for a managed Fast Lane. | In the four-Skill flow, Long—not inspection—implements the patch. It is not a release or security gate. |

The normal delivery chain is:

```text
planning-layer-runtime
  -> approved handoff
  -> long-task-orchestrator
  -> ready_for_local_test
  -> testing-layer-runtime
  -> the target project's release/security process
```

`ai-code-inspection` is independent and can be used for focused review, diagnosis, confirmed repair, requirement-completeness review, audit, refactor assessment, merge readiness, hotfix closure, or standards governance.

After the planning baseline is frozen, accepted requirement or contract changes use an append-only Change Set and an incremental handoff. Long executes only the selected queues, and Testing classifies findings before routing them; neither stage reopens or reruns the whole phase by default.

Confirmed implementation defects whose existing contract is still valid use the v1.1 Bugfix Fast Lane instead of a new phase:

```text
Issue + ai-code-inspection Bug Contract
  -> append-only bugfix-case/v1 under the originating phase
  -> long-task-orchestrator exact patch
  -> testing-layer-runtime targeted verification
  -> PR/CI/merge/deploy + original production retest
  -> post-release similar-defect verification
  -> close the Case and Issue
```

The originating 00–15 documents stay read-only. `deployed` and `original_bug_production_verified` are not closure states: Testing must resume the persisted `post_release_similar_defect_verification` action, and a newly found sibling defect receives its own Bug ID, Issue, and Case.

## Versions and automatic synchronization

The repository has two version levels: a GitHub Release identifies one bundle snapshot, while each Skill has its own SemVer in [`skills-manifest.json`](skills-manifest.json). The manifest's release channel distinguishes prerelease evaluation bundles from jointly validated stable bundles. Neither the README nor `SKILL.md` is a version source.

The current bundle declared by the manifest is:

| Component | Version |
| --- | --- |
| Repository Release | `v1.1.2` (stable) |
| `planning-layer-runtime` | `1.1.0` |
| `long-task-orchestrator` | `1.1.0` |
| `testing-layer-runtime` | `1.1.0` |
| `ai-code-inspection` | `0.2.0` |
| Synchronization tool | `0.1.1` |

This table is a human-readable snapshot only. [`skills-manifest.json`](skills-manifest.json) remains the authoritative version source.

An installed target project receives:

```text
runtime-skills.lock.json               # release, commit, Skill versions, destinations, hashes
.runtime-skills/runtime-skills.py      # project-local synchronization entry point
```

Commit the lock file in the target project. It binds copies under `.agents/skills/`, `.claude/skills/`, and other platform directories to the same Release so different Agents cannot silently use mixed versions.

Before the first Runtime Skill use in each Agent session, run:

```bash
python .runtime-skills/runtime-skills.py sync --project .
```

Compatible patch updates are applied automatically by default. Minor and major updates are reported for confirmation. GitHub publicly exposes only the newest patch Release and tag within each `MAJOR.MINOR` series; superseded Release records are retained as drafts, while older `MAJOR.MINOR` series remain public for staged rollout. Local modifications or destination drift stop replacement. Pin an active phase so Planning, Long, and Testing keep using the same rules, then unpin after the phase closes.

See [Versioning and updates](src/content/docs/reference/versioning-and-updates.md) for the full command and release policy.

### Release tags and a copy-ready Skill + Runtime migration prompt

GitHub Release tags use `vMAJOR.MINOR.PATCH`; the current manifest declares the stable `v1.1.2` Release. The versions of the individual Skills inside that bundle still come from [`skills-manifest.json`](skills-manifest.json). Use `latest` to follow the latest stable Release. When a new patch is published, the release workflow archives older patch Releases from the same `MAJOR.MINOR` series as drafts and removes their public tags, so users receive `v1.1.2` instead of the unfixed `v1.1.0` or `v1.1.1`. Releases from a different `MAJOR.MINOR` series remain public for staged rollout. After installation, `runtime-skills.lock.json` records what that project actually uses.

Updating Skill files does not upgrade Runtime state already created inside a project. The `v1.0.0` forward ledgers and validation receipts remain the compatibility boundary for unfinished pre-1.0 phases. v1.1 adds Bugfix Cases without rewriting closed historical phases: new confirmed defects create `bugfix-case/v1` alongside the originating phase, while existing 00–15 files remain untouched.

Paste the following prompt directly into the Agent that is working in the target project. It handles the managed/unversioned Skill copies and the current project's unfinished legacy Runtime state. It uses the latest stable Release as-is.

```text
Adopt or update Runtime Skills in the current project.

Source repository: https://github.com/xinghang-ee-cs/dev-runtime-skill
Target Release: latest stable, unless I explicitly provide a vMAJOR.MINOR.PATCH tag.

Take responsibility for the workflow from inspection through verification. Treat the current project root as the only target; do not ask me to move or edit files manually.

1. Inspect runtime-skills.lock.json, .runtime-skills/runtime-skills.py, AGENTS.md, CLAUDE.md, and supported project-level Skill roots such as .agents/skills/, .claude/skills/, and .github/skills/. Identify the currently installed Runtime Skills, every destination copy, the Agent platforms in use, local Git changes, and any active phase pin. Do not scan unrelated projects.
2. If the lock file exists, treat this as a managed installation even when the project-local synchronization entry point or a managed copy is missing. When the entry point is healthy, first run verify and remote status, then run diff against the requested Release. When it is missing or verify reports drift, use a temporary trusted copy of the tool from the locked/requested Release to diagnose it; do not reclassify the project as an unmanaged installation or repair it without approval. Apply a compatible patch through sync. For a minor or major change, summarize the affected Release, Skill versions, added/modified/removed files, and compatibility impact, then wait for my explicit confirmation before running update with the required --allow level. Never silently bypass an active phase pin: normally defer the update; when the requested major update is specifically needed to migrate an unfinished legacy Runtime, offer one controlled transition for explicit confirmation—record the old lock/pin and Runtime sources, unpin with the tool, perform the approved update and steps 7–10, then pin the active phase to the new bundle again. If I do not approve that transition, leave everything pinned and unchanged.
3. If Runtime Skill directories exist without a lock file, treat them as unmanaged legacy copies. Obtain the requested stable Release from the source repository in a temporary location. Infer the exact existing Skill names and destination roots without adding or removing Skills. Run the install command once without --overwrite-local-changes so the tool reports the incoming additions, modifications, and removals. Show that comparison and wait for my explicit approval before rerunning with --overwrite-local-changes to adopt the Release, create runtime-skills.lock.json, and install .runtime-skills/runtime-skills.py.
4. If neither a managed installation nor legacy Runtime Skill copies exist, treat it as a first installation. Determine the Agent platform from the current execution platform, project instruction files, and existing platform directories; do not ask me to choose a platform. Ask only for a Skill selection that cannot be determined from the request or current project, then proceed directly with the repository's installation flow.
5. Preserve all project-specific instructions. Merge only applicable routing and safety rules into AGENTS.md, and maintain the CLAUDE.md import when Claude Code is used. Never replace either file wholesale. Never silently overwrite local Skill changes, mix copies from different Releases, downgrade a Skill, expose credentials, modify business code, run database migrations, deploy, commit, or push.
6. After an approved Skill migration or update, run verify. Report the previous Release and Skill versions -> installed Release and Skill versions, the exact destinations, lock-file state, phase-pin state, merged instruction files, and any unresolved drift or decisions. If remote access is unavailable, say so and distinguish local verification from a successful latest-version check.
7. After Skill verification, inspect only the current project's Planning, Long, and Testing state locations referenced by the project instructions, handoffs, and active phase. Classify each phase as: no Runtime state, closed historical state, unfinished legacy state, or already-current state. Never rewrite a closed historical phase merely to make it match the new schema.
8. For every unfinished pre-1.0 legacy phase, preserve its confirmed source-of-truth documents, requirement pool, user profile, interaction/event history, task facts, findings, and evidence as read-only migration sources. Do not fabricate a forward-state history or mutate old failed/blocked evidence into passed. Use the newly installed Skill's recovery/entry procedure to create a fresh current-version Runtime epoch from those sources; only an already-current Runtime may resume or open a new forward cycle. Retain traceability to the legacy location, and ask only about facts that remain genuinely unknown; do not ask the user to repeat already recorded answers.
9. Rebuild only the current contracts required by the installed Skills. Planning must restore persisted discovery, requirement-pool, user-profile, and environment-profile state. Reuse a known deployment identity unless the user declared a move, and migrate only sanitized project-process extrema/anomaly summaries rather than raw logs. For persistence, unchanged reuse must cite the real schema; created or changed storage must confirm every physical unit, field, key, constraint, index, and relation while forbidding extra tables. Planning must also validate applicable UI/UX contracts and prove every before-Long prerequisite. Long must declare project_root_ref, complete source_roots, a current Required Validation Matrix, and one machine_execution probe per success postcondition; treat the phase as the formal validation closure, enter the forward workflow in order, and rerun every current required item through run-long-validation.sh or run-long-validation.ps1 so each passed result cites a new machine-execution receipt. Testing may inherit only a currently valid Long readiness receipt, must bind reused validations to their source receipt/evidence hashes, and must rebuild the applicable local/cloud/release state and deployment identity through forward transitions. Treat legacy pass/ready/accepted labels as historical claims until the current validator proves them; never skip directly to a ready or final state.
10. Run every applicable validator from the newly installed Skill directories; if step 2 temporarily removed an active phase pin, restore that pin to the new bundle before stopping. Then report: migrated and untouched phase paths, the new Runtime epoch/cycle, preserved legacy sources, regenerated contracts/receipts, rerun checks and outcomes, final pin state, unresolved blockers, and the exact next permitted action. Do not start feature implementation, manual acceptance, deployment, database migration, commit, or push unless I separately requested it.
```

For an exact managed update, the synchronization commands accept a public Release tag directly. Superseded patch records are drafts and their tags are removed, so they cannot be selected; choose the newest patch in that `MAJOR.MINOR` series. Moving from a pre-1.0 Release requires explicit `update --allow major`; `sync` will report it but will not silently cross that boundary. Do not use a tag that has not been published as a GitHub Release.

## Install in an Agent project

No manual file copying is required. Give the Agent read access to this repository and write access to the target project, then run the initialization prompt below. The Agent should invoke the synchronization tool instead of maintaining an unversioned copy workflow.

The user only needs to provide a target project name, local path, or repository URL plus the Skills to install. The Agent determines the platform and destinations from the current execution platform, project instruction files, and existing Skill directories. With sufficient permissions, it locates the project, copies each selected Skill as a complete directory, and adapts it without requiring the user to choose a platform or move or edit files manually.

| Agent | Project skill location | Project instructions | Official documentation |
| --- | --- | --- | --- |
| OpenAI Codex | `.agents/skills/<skill-name>/` | Root `AGENTS.md` | [Codex Skills](https://developers.openai.com/codex/skills), [AGENTS.md](https://developers.openai.com/codex/guides/agents-md) |
| Claude Code | `.claude/skills/<skill-name>/` | `CLAUDE.md`; import this repository's rules with `@AGENTS.md` | [Claude Code Skills](https://code.claude.com/docs/en/skills), [CLAUDE.md and AGENTS.md](https://code.claude.com/docs/en/memory#agents-md) |
| GitHub Copilot | `.agents/skills/<skill-name>/` is recommended when sharing with Codex; `.github/skills/` and `.claude/skills/` are also supported | Root or nested `AGENTS.md` | [Copilot Agent Skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills), [repository instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions) |

The installation created by the Agent can look like this when all three platforms are used:

```text
your-project/
├── AGENTS.md
├── CLAUDE.md                   # only needed by Claude Code
├── runtime-skills.lock.json
├── .runtime-skills/
│   └── runtime-skills.py
├── .agents/skills/             # Codex + GitHub Copilot
│   ├── ai-code-inspection/
│   ├── planning-layer-runtime/
│   ├── long-task-orchestrator/
│   └── testing-layer-runtime/
└── .claude/skills/             # Claude Code
    ├── ai-code-inspection/
    ├── planning-layer-runtime/
    ├── long-task-orchestrator/
    └── testing-layer-runtime/
```

The Agent installs only the directories required by the automatically detected platforms; when evidence shows multiple platforms, it writes every corresponding destination in the same installation. If the target project already has `AGENTS.md` or `CLAUDE.md`, it merges the instructions instead of overwriting them. When only some Skills are installed, it removes unavailable Skills from the installed `AGENTS.md` inventory.

Claude Code does not read `AGENTS.md` directly. The Agent therefore creates or merges this minimal project file:

```markdown
# CLAUDE.md

@AGENTS.md
```

## Install and initialize the target project

Run this prompt from this Skill repository. The AI performs the complete installation and adaptation; the user does not copy files manually:

```text
Install and initialize Runtime Skills for the following target project:
- Target project: <required project name, local path, or repository URL>
- Skills to install: <one or more exact Skill names>

Take responsibility for the complete initialization. Do not ask me to copy, paste, or edit installation files manually.
Use the supplied project name or address to search the workspaces and repositories you can access. If exactly one matching local project is found, continue automatically. Ask me only when the target is missing, ambiguous, or outside your permissions.
Confirm internally that the source is this Skill repository and that the destination is the matched target project before writing.
Inspect the current execution platform, the target project's AGENTS.md and CLAUDE.md, and existing .agents/skills/, .claude/skills/, and .github/skills/ directories. Determine the actual Agent platforms and installation destinations without asking me to choose a platform. Use .agents/skills for Codex; use .claude/skills for Claude Code; for GitHub Copilot, reuse an existing supported project directory and use .agents/skills when sharing with Codex. Use every corresponding destination when evidence shows multiple platforms.
If the source repository is not local, obtain its latest stable Release in a temporary directory. From the source repository run `python scripts/runtime-skills.py install --release latest --project "<target-project-root>"`, repeating `--skill <name>` for every selected Skill and `--destination <directory>` for every automatically detected destination. This operation must also create runtime-skills.lock.json and the project-local synchronization entry point.
Merge the applicable routing and safety rules from this repository's AGENTS.md into the target project's AGENTS.md; never overwrite existing project instructions. For Claude Code, also create or merge CLAUDE.md so it imports AGENTS.md.
Do not copy this repository's README files, src/, public/, package.json, package-lock.json, astro.config.mjs, tsconfig.json, .github/workflows/, or any other documentation-site files.
Scan only the target project, list the installed Skills, and adapt their stable environment profiles or bootstrap files using facts from that project.
Do not create task/phase Runtime state before its skill entry gate is satisfied.
Do not modify business code, run database migrations, deploy, commit, or push.
Run `python "<target-project-root>/.runtime-skills/runtime-skills.py" verify --project "<target-project-root>"`. Report the automatically detected platforms, installed Release, commit, every Skill version and destination; copied, merged, and initialized files; detected components, languages, frameworks, persistence, test tools, CI workflows, and validation commands; and any unresolved facts.
```

AI initialization means locating the named target, installing the selected Skill packages, merging the Agent entry instructions, and adapting Skill-owned profiles or bootstrap files. It does not migrate this repository or its documentation site into that project.

You can also run the tool directly from this repository. For example, to install for both Codex and Claude Code:

```bash
python scripts/runtime-skills.py install \
  --release latest \
  --project /path/to/your-project \
  --skill planning-layer-runtime \
  --skill long-task-orchestrator \
  --destination .agents/skills \
  --destination .claude/skills
```

## Use the skills

Use natural language or invoke the skill explicitly where the agent supports it. Codex exposes skills through `/skills` or `$skill-name`; Claude Code uses `/skill-name`; Copilot selects skills from the request and the skill description.

```text
Use planning-layer-runtime to plan this feature. Do not implement it yet.

Use long-task-orchestrator to execute the approved planning handoff.

Use testing-layer-runtime to take over the current testing handoff.

Use ai-code-inspection to review the current Git changes, read-only, in one run.

Use ai-code-inspection to perform a full read-only audit of this project.
```

After installation, first ask the agent to list the loaded project instructions and installed skills. If a skill is missing, verify the directory name, the complete `SKILL.md` path, and restart or open a new agent session when the platform requires rediscovery.

The repository does not provide production release approval or enterprise security acceptance. Those remain the responsibility of the target project's own process.
