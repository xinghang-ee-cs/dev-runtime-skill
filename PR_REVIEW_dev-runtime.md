## Review Feedback

Thank you for this contribution. A unified `dev-runtime` entry point is a valuable addition, and routing complete development requests through planning, implementation, testing, and inspection fits the project’s overall direction.

Since this PR was opened, `main` has changed significantly. The READMEs now support AI-driven installation for Codex, Claude Code, and GitHub Copilot; the root `AGENTS.md` owns Skill discovery and routing; and the existing Skill lifecycle rules have been updated. As a result, this branch now conflicts with both README files and cannot be merged as-is.

Could you please rebase onto the latest `main` and make the following adjustments?

1. Preserve the current README installation flow and add `dev-runtime` without restoring the older Codex-only instructions.
2. Add `dev-runtime` to the root `AGENTS.md` and the documentation-site Skill catalog.
3. Avoid fixed root paths such as `skills/...`; sibling Skills may be installed under `.agents/skills/`, `.claude/skills/`, or another supported directory.
4. Align with the current `ai-code-inspection` rules: the first ten modes are single-run, while only standards correction uses the interactive seven-step flow.
5. Handle tasks with fewer than four implementation units, since they are outside `long-task-orchestrator`’s scope.
6. Remove the unsupported `interface.description` field from `agents/openai.yaml`.

The basic Skill validation and `git diff --check` already pass, so the implementation has a good foundation. Once these compatibility issues are addressed, we will be happy to review it again and move it toward merging.

Thank you again for your work, and sorry that the recent changes on `main` created extra effort for this PR.
