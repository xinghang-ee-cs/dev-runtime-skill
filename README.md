# AI Development Runtime Skills

[English](README.md) | [简体中文](README.zh-CN.md)

A project-neutral set of Agent Skills for planning, implementation, testing, and code inspection. The repository contains reusable governance only; project-specific commands, credentials, paths, and environment facts stay in the target project.

Only the selected directories under `skills/` are installable Skill packages. `AGENTS.md` is the reusable project-entry template. `src/`, `public/`, `package*.json`, `astro.config.mjs`, `tsconfig.json`, and the documentation deployment workflow belong to this repository's Astro/Starlight documentation site and must not be copied into a target project.

## The five skills

| Skill | Use it for | Boundary |
| --- | --- | --- |
| [`dev-runtime`](skills/dev-runtime/SKILL.md) | Route complete or vague development requests across the installed Runtime Skills, starting with planning and preserving each current entry and handoff gate. | Does not replace phase governance, handle single-stage requests, assume a fixed Skill directory, or approve release. Work below four implementation units uses the normal Agent path instead of long-task orchestration. |
| [`planning-layer-runtime`](skills/planning-layer-runtime/SKILL.md) | Discover requirements and produce an approved planning handoff before implementation. | Does not write production code or execute tests. |
| [`long-task-orchestrator`](skills/long-task-orchestrator/SKILL.md) | Implement an approved feature with at least four implementation units, run automation, and hand off at `ready_for_local_test`. | Does not perform manual acceptance or release approval. |
| [`testing-layer-runtime`](skills/testing-layer-runtime/SKILL.md) | Reuse long-task automation evidence and manage manual, device, server, external-capability, and final acceptance testing. | Does not change business code or approve production release. |
| [`ai-code-inspection`](skills/ai-code-inspection/SKILL.md) | Route reviews, diagnosis, confirmed fixes, completeness checks, audits, refactor assessments, merge checks, hotfixes, and standards governance by ten real work scenarios. | Scenarios 1–9 are single-run; only standards governance uses the interactive seven-step flow. Project state lives under `.runtime/ai-code-inspection/`. It is not a release or security gate. |

For a complete request, `dev-runtime` discovers the installed Skills and routes the delivery chain:

```text
dev-runtime
  -> planning-layer-runtime
  -> approved handoff
  -> planning_only: stop after planning
  -> execution_ready with fewer than 4 implementation units: normal Agent implementation and project validation
  -> execution_ready with at least 4 implementation units:
     long-task-orchestrator
     -> ready_for_local_test
     -> testing-layer-runtime
  -> optional ai-code-inspection scene selected from the actual request
  -> the target project's release/security process
```

`ai-code-inspection` is independent and can be used for focused review, diagnosis, confirmed repair, requirement-completeness review, audit, refactor assessment, merge readiness, hotfix closure, or standards governance. Scenarios 1–9 are `single_run`; only `standards_compliance_correction` uses the interactive seven-step flow.

## Install in an Agent project

No manual file copying is required. Give the Agent read access to this repository and write access to the target project, then run the initialization prompt below.

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
├── .agents/skills/             # Codex + GitHub Copilot
│   ├── ai-code-inspection/
│   ├── dev-runtime/
│   ├── planning-layer-runtime/
│   ├── long-task-orchestrator/
│   └── testing-layer-runtime/
└── .claude/skills/             # Claude Code
    ├── ai-code-inspection/
    ├── dev-runtime/
    ├── planning-layer-runtime/
    ├── long-task-orchestrator/
    └── testing-layer-runtime/
```

The Agent installs only the directories required by the selected platforms. If the target project already has `AGENTS.md` or `CLAUDE.md`, it merges the instructions instead of overwriting them. When only some Skills are installed, it removes unavailable Skills from the installed `AGENTS.md` inventory.

For the complete lifecycle, install `dev-runtime` together with the four phase Skills it discovers. If a phase Skill is not installed, `dev-runtime` reports the missing dependency instead of guessing a path or pretending the phase ran.

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
From this repository, copy only the complete directories of the selected Skills under skills/ into the project-level Skill directory supported by the selected Agent platform.
Merge the applicable routing and safety rules from this repository's AGENTS.md into the target project's AGENTS.md; never overwrite existing project instructions. For Claude Code, also create or merge CLAUDE.md so it imports AGENTS.md.
Do not copy this repository's README files, src/, public/, package.json, package-lock.json, astro.config.mjs, tsconfig.json, .github/workflows/, or any other documentation-site files.
Scan only the target project, list the installed Skills, and adapt their stable environment profiles or bootstrap files using facts from that project.
Do not create task/phase Runtime state before its skill entry gate is satisfied.
Do not modify business code, run database migrations, deploy, commit, or push.
Report the copied, merged, and initialized files; detected components, languages, frameworks, persistence, test tools, CI workflows, and validation commands; and any unresolved facts.
```

AI initialization means locating the named target, installing the selected Skill packages, merging the Agent entry instructions, and adapting Skill-owned profiles or bootstrap files. It does not migrate this repository or its documentation site into that project.

## Use the skills

Use natural language or invoke the skill explicitly where the agent supports it. Codex exposes skills through `/skills` or `$skill-name`; Claude Code uses `/skill-name`; Copilot selects skills from the request and the skill description.

```text
Use dev-runtime to route this complete development request through the installed Runtime Skills.

Use planning-layer-runtime to plan this feature. Do not implement it yet.

Use long-task-orchestrator to execute the approved planning handoff.

Use testing-layer-runtime to take over the current testing handoff.

Use ai-code-inspection to review the current Git changes, read-only, in one run.

Use ai-code-inspection to perform a full read-only audit of this project.
```

After installation, first ask the agent to list the loaded project instructions and installed skills. If a skill is missing, verify the directory name, the complete `SKILL.md` path, and restart or open a new agent session when the platform requires rediscovery.

The repository does not provide production release approval or enterprise security acceptance. Those remain the responsibility of the target project's own process.
