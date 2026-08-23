# AI Development Runtime Skills

[English](README.md) | [简体中文](README.zh-CN.md)

A project-neutral set of Agent Skills for planning, implementation, testing, and code inspection. The repository contains reusable governance only; project-specific commands, credentials, paths, and environment facts stay in the target project.

Only the selected directories under `skills/` are installable Skill packages. `AGENTS.md` is the reusable project-entry template. `src/`, `public/`, `package*.json`, `astro.config.mjs`, `tsconfig.json`, and the documentation deployment workflow belong to this repository's Astro/Starlight documentation site and must not be copied into a target project. The version in `package.json` belongs to the documentation site and is not a Skill version.

## The four skills

| Skill | Use it for | Boundary |
| --- | --- | --- |
| [`planning-layer-runtime`](skills/planning-layer-runtime/SKILL.md) | Discover requirements, freeze an execution baseline, produce initial/incremental handoffs, and precisely re-enter planning after accepted change triage. | Does not write production code or execute tests. |
| [`long-task-orchestrator`](skills/long-task-orchestrator/SKILL.md) | Consume revisioned execution queues, implement an approved feature with at least four units, preserve unaffected/completed work, run automation, and hand off at `ready_for_local_test`. | Does not perform manual acceptance or absorb untriaged contract changes. |
| [`testing-layer-runtime`](skills/testing-layer-runtime/SKILL.md) | Reuse revisioned long-task evidence, manage manual/device/server/external/final acceptance testing, and triage findings back to Testing, Long, or Planning. | Phase state stays in its bound writeback target; it does not change business code or approve production release. |
| [`ai-code-inspection`](skills/ai-code-inspection/SKILL.md) | Route reviews, diagnosis, confirmed fixes, completeness checks, audits, refactor assessments, merge checks, hotfixes, and standards governance by ten real work scenarios. | Scenarios 1–9 are single-run; only standards governance uses the interactive seven-step flow. Project state lives under `.runtime/ai-code-inspection/`. It is not a release or security gate. |

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

## Versions and automatic synchronization

The repository has two version levels: a GitHub Release identifies one jointly validated bundle, while each Skill has its own SemVer in [`skills-manifest.json`](skills-manifest.json). Neither the README nor `SKILL.md` is a version source.

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

Compatible patch updates are applied automatically by default. Minor and major updates are reported for confirmation. Local modifications or destination drift stop replacement. Pin an active phase so Planning, Long, and Testing keep using the same rules, then unpin after the phase closes.

See [Versioning and updates](src/content/docs/reference/versioning-and-updates.md) for the full command and release policy.

## Install in an Agent project

No manual file copying is required. Give the Agent read access to this repository and write access to the target project, then run the initialization prompt below. The Agent should invoke the synchronization tool instead of maintaining an unversioned copy workflow.

The user only needs to provide a target project name, local path, or repository URL, plus the Agent platform and Skills to install. With sufficient permissions, the Agent locates the project, copies each selected Skill as a complete directory, and adapts it without requiring the user to move or edit files manually.

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

The Agent installs only the directories required by the selected platforms. If the target project already has `AGENTS.md` or `CLAUDE.md`, it merges the instructions instead of overwriting them. When only some Skills are installed, it removes unavailable Skills from the installed `AGENTS.md` inventory.

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
- Agent platform: <Codex / Claude Code / GitHub Copilot>
- Skills to install: <one or more exact Skill names>

Take responsibility for the complete initialization. Do not ask me to copy, paste, or edit installation files manually.
Use the supplied project name or address to search the workspaces and repositories you can access. If exactly one matching local project is found, continue automatically. Ask me only when the target is missing, ambiguous, or outside your permissions.
Confirm internally that the source is this Skill repository and that the destination is the matched target project before writing.
Run scripts/runtime-skills.py install --release latest to place the complete selected Skill directories from the latest stable Release in the project-level Skill directory supported by the selected Agent platform. Also create runtime-skills.lock.json and the project-local synchronization entry point. Pass every target directory in the same installation when multiple Agent platforms are used.
Merge the applicable routing and safety rules from this repository's AGENTS.md into the target project's AGENTS.md; never overwrite existing project instructions. For Claude Code, also create or merge CLAUDE.md so it imports AGENTS.md.
Do not copy this repository's README files, src/, public/, package.json, package-lock.json, astro.config.mjs, tsconfig.json, .github/workflows/, or any other documentation-site files.
Scan only the target project, list the installed Skills, and adapt their stable environment profiles or bootstrap files using facts from that project.
Do not create task/phase Runtime state before its skill entry gate is satisfied.
Do not modify business code, run database migrations, deploy, commit, or push.
Run the synchronization tool's verify command. Report the installed Release, commit, every Skill version and destination; copied, merged, and initialized files; detected components, languages, frameworks, persistence, test tools, CI workflows, and validation commands; and any unresolved facts.
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
