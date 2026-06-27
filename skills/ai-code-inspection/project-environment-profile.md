# 项目环境档案

本文件是 `ai-code-inspection` 的环境事实档案模板。

Skill 启动后，由 Skill 根据当前项目自动探测并填充以下内容。检查结束后，如需保留环境事实用于后续运行，可回写本文件；否则应保持为空模板状态。

## 使用规则

- 本文件只保存当前项目的稳定环境事实。
- 不得在这里记录临时运行状态、检查输出、命令日志、发现项或执行历史。
- 只有稳定环境事实发生变化时（如迁移构建工具、替换测试框架），才需要更新本文件。

## 工作区

```yaml
workspace:
  package_manager: <detected: pnpm | npm | yarn | bun>
  monorepo: <detected: true | false>
  workspace_packages:
    - <detected: package name>
  root_scripts:
    build: <detected: root build command>
    test: <detected: root test command>
    verify: <detected: root verify command, or omit>
```

## 前端

```yaml
frontend:
  path: <detected: frontend directory path>
  framework: <detected: Vue | React | Svelte | Angular | other>
  language: <detected: TypeScript | JavaScript>
  build_tool: <detected: Vite | Webpack | Rollup | esbuild | other>
  router: <detected: Vue Router | React Router | other | not_declared>
  state_management: <detected: Pinia | Vuex | Redux | Zustand | other | not_declared>
  ui_library: <detected: Element Plus | Ant Design | MUI | other | not_declared>
  test_runner: <detected: Vitest | Jest | Cypress | Playwright | other>
  package_scripts:
    build: <detected: frontend build command>
    test: <detected: frontend test command>
    test_coverage: <detected: frontend coverage command, or omit>
```

## 后端

```yaml
backend:
  path: <detected: backend directory path>
  framework: <detected: NestJS | Express | Fastify | Django | other>
  language: <detected: TypeScript | JavaScript | Python | Go | other>
  orm: <detected: Prisma | TypeORM | Sequelize | other | not_declared>
  database: <detected: PostgreSQL | MySQL | SQLite | MongoDB | other | not_declared>
  validation: <detected: class-validator | zod | joi | other | not_declared>
  test_runner: <detected: Vitest | Jest | other>
  package_scripts:
    build: <detected: backend build command>
    build_deploy: <detected: backend deploy build command, or omit>
    test: <detected: backend test command>
    test_integration: <detected: backend integration test command, or omit>
    test_coverage: <detected: backend coverage command, or omit>
    prisma_generate: <detected: Prisma generate command, or omit>
    prisma_validate: <detected: Prisma validate command, or omit>
    prisma_migrate_dev: <detected: Prisma migrate command, or omit>
```

## 远程平台与 CI/CD

```yaml
ci_cd:
  remote_platform: <detected: GitHub Actions | GitLab CI | Jenkins | other | none>
  ci_enabled: <detected: true | false>
  workflow_path: <detected: CI workflow file path, or omit>
  ci_capabilities:
    - <detected: clean install>
    - <detected: backend tests>
    - <detected: frontend tests>
    - <detected: backend deploy build>
    - <detected: frontend build>
    - <detected: database migration deploy>
    - <detected: deployment script execution>
```

## 日常验证命令

```yaml
validation_commands:
  broad_verify: <detected: root-level verify command, or omit>
  root_build: <detected: root build command>
  root_test: <detected: root test command>
  frontend_test: <detected: frontend test command>
  backend_test: <detected: backend test command>
  prisma_validate: <detected: Prisma validate command, or omit>
```

## 数据库迁移处理

```yaml
database_migrations:
  schema_path: <detected: ORM schema file path, or omit>
  migration_path: <detected: migration directory path, or omit>
  routine_schema_validation: <detected: schema validation command, or omit>
  migration_deploy_command: <detected: migration deploy command, or omit>
  migration_execution_policy: 代码检查 Skill 不执行数据库迁移命令；只有开发者明确确认目标数据库和命令后，才能进入相应操作。
```
