# AI Development Runtime Skills

[English](README.md) | [简体中文](README.zh-CN.md)

A project-neutral set of Codex skills for planning, implementation, testing, and everyday code inspection.

Three skills form a controlled delivery pipeline:

```text
Planning -> Implementation and automated validation -> Manual and environment testing
```

`ai-code-inspection` is an independent review workflow that can be used before a commit or whenever the current changes need a focused check.

This repository does not include a production release or security-approval skill. `testing-layer-runtime` prepares the handoff, but the target project's own release and security process must make the final decision.

## Included Skills

| Skill | Use it when | Do not use it for |
|---|---|---|
| [`planning-layer-runtime`](skills/planning-layer-runtime/SKILL.md) | A feature still needs discovery, scope decisions, architecture choices, acceptance criteria, or planning documents before implementation. | Writing code, running tests, or recording actual test results. |
| [`long-task-orchestrator`](skills/long-task-orchestrator/SKILL.md) | A confirmed planning handoff is ready for implementation and the work contains at least four implementation units, or confirmed test feedback needs a structured patch. | Manual testing, real-device testing, server acceptance, final acceptance, or release approval. |
| [`testing-layer-runtime`](skills/testing-layer-runtime/SKILL.md) | Long-task implementation has reached `ready_for_local_test` and the project needs manual, device, cloud, external-capability, or final acceptance testing. | Re-running passed long-task automation by default, changing business code, or approving a production release. |
| [`ai-code-inspection`](skills/ai-code-inspection/SKILL.md) | Modified frontend or backend code needs a practical seven-step review for naming, quality, architecture, tests, docs, comments, and commit readiness. | Release readiness, production gates, or enterprise security approval. |

## How the Workflow Fits Together

```text
planning-layer-runtime
  -> confirmed planning handoff
  -> long-task-orchestrator
  -> ready_for_local_test + automated-test evidence
  -> testing-layer-runtime
  -> release/security handoff
  -> target project's release process
```

The handoff states matter:

- `ready_for_local_test` means implementation and the required automated validation are complete and recorded. It does not mean manual acceptance or release approval has passed.
- Testing inherits valid automated results from the long-task handoff and records them as `reused_from_long`. It does not repeat them just to produce a new pass result.
- Planning defines what must be proved. Long-task execution writes code and runs automation. Testing manages human and environment evidence.
- Code inspection reports findings first. When it finds a fixable issue, a separate `continue` authorizes that step's repair and validation.

## Deploy to a Codex Project

### 1. Copy the skills

Copy the complete `skills/` directory into the root of the target repository. Keep every skill's `SKILL.md`, `references/`, `agents/`, and template files together.

The target layout should look like this:

```text
your-project/
  AGENTS.md
  skills/
    ai-code-inspection/
    planning-layer-runtime/
    long-task-orchestrator/
    testing-layer-runtime/
```

### 2. Add the project-specific facts

Before running `ai-code-inspection`, fill in `skills/ai-code-inspection/project-environment-profile.md` from the target repository's real framework, package manager, database, commands, and CI setup.

Do not copy environment facts from another project. The planning skill creates the target project's minimal `.plan/` bootstrap files when needed; its current user profile is `.plan/user-profile.yaml`, not the legacy `runtime-user-profile.md` template.

### 3. Create `AGENTS.md`

Create `AGENTS.md` in the target repository root. This is the durable project instruction file Codex uses to understand local rules. Copying the skill folders alone is not enough for this portable layout: `AGENTS.md` should tell Codex exactly which local skill owns each kind of work.

Use this as a starting point:

```markdown
# Codex Project Instructions

## Local Runtime Skills

Before acting, decide whether the task matches one of the local skills below. When it matches, read that skill's complete `SKILL.md` first and follow the references it routes for the current task.

- `skills/planning-layer-runtime/SKILL.md`
  - Use for requirement discovery, scope and architecture decisions, acceptance design, and planning documents before implementation.
  - Do not write code, execute tests, or record actual test results in this skill.

- `skills/long-task-orchestrator/SKILL.md`
  - Use after a confirmed planning handoff for a complete feature or module with at least four implementation units, or for a confirmed testing patch.
  - Own implementation, migrations, automated test code, automated execution, evidence, and the handoff up to `ready_for_local_test` or `ready_for_local_retest`.
  - Do not perform manual acceptance, real-device testing, server acceptance, or release approval.

- `skills/testing-layer-runtime/SKILL.md`
  - Use after the long-task handoff for manual testing, real-device testing, cloud or server verification, external-capability verification, final acceptance, and release handoff.
  - Reuse valid long-task automation evidence. Do not rerun passed automation unless the skill's exception rules allow it.
  - Do not change business code or approve a production release.

- `skills/ai-code-inspection/SKILL.md`
  - Use for everyday review of modified frontend or backend code and commit preparation.
  - Report findings before fixing them. A separate user `continue` is required for the current step's repair.
  - Do not use it as a release, production, or enterprise security gate.

## Workflow Boundaries

- Normal delivery order: planning -> long-task implementation -> testing -> the project's release/security process.
- Use one owning skill at a time unless the active skill explicitly hands work to another skill.
- `ready_for_local_test` is a development handoff, not final acceptance or release approval.
- Keep project facts, credentials, server details, and runtime evidence in the target project's own files. Do not write them back into generic skill rules.
- Preserve unrelated working-tree changes. Do not stage, commit, push, deploy, or run destructive operations unless the user explicitly asks.
```

Add the target project's own commands, environment source of truth, Git rules, and release process below this block. Those facts belong in the target project's `AGENTS.md` or project documentation, not in this shared repository.

### 4. Start Codex from the target repository

Open the target repository in Codex and make the requested phase explicit. For example:

```text
Use planning-layer-runtime to plan this feature before implementation.
Use long-task-orchestrator to implement the confirmed handoff.
Use testing-layer-runtime to take over the current phase testing.
Use ai-code-inspection to review the current Git changes only.
```

Natural-language requests also work when `AGENTS.md` routes them clearly, but Codex must still respect each skill's entry gates. A single "start development" message does not automatically bypass planning confirmation, implementation preflight, or testing handoff requirements.

### 5. Check the installation

Confirm that these files exist in the target repository:

```text
AGENTS.md
skills/ai-code-inspection/SKILL.md
skills/planning-layer-runtime/SKILL.md
skills/long-task-orchestrator/SKILL.md
skills/testing-layer-runtime/SKILL.md
```

Then ask Codex to explain which skill it would use for a sample task and why. This catches missing paths or unclear `AGENTS.md` routing before real work starts.

## Good Fit

- Individuals or small teams using Codex for multi-step software work.
- Projects that need structured planning, traceable implementation, and human acceptance evidence.
- Features with frontend, backend, database, device, cloud, or external-platform dependencies.
- Teams that want to reuse one workflow without leaking one project's private facts into another.

For a tiny edit that needs no planning or formal test lifecycle, use normal Codex instructions instead of forcing the full pipeline.

## Project-Neutrality Rules

This repository stores generic procedures, templates, and neutral examples only. Do not add:

- Real names, email addresses, accounts, tokens, keys, or internal identities.
- Customer names, private repository paths, server addresses, or production environment details.
- A specific project's technology conclusions, CI/CD commands, migration commands, or operations facts.
- Project-only test IDs, page names, business objects, or approval flows.

Put those facts in the target project's planning documents, runtime output, environment profile, or `AGENTS.md`.

## Compatibility

This repository is maintained for Codex and includes `agents/openai.yaml` metadata alongside each `SKILL.md`. Other coding agents may be able to reuse the Markdown instructions, but their discovery and execution behavior is tool-specific and is not guaranteed by this repository.
