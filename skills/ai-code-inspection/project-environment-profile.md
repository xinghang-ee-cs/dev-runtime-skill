# 项目环境档案

本文件记录 `ai-code-inspection` 使用的稳定环境事实。

不得在这里记录临时运行状态、Step 输出、命令日志、检查发现或执行历史。只有稳定项目环境事实变化时，才允许更新本文件。

本文件是模板。首次在具体项目中使用 `ai-code-inspection` 前，必须先检查当前仓库的真实文件、包管理器、脚本、框架、CI/CD 和数据库迁移方式，再填写或更新本档案。不得从其他项目复制环境事实。

## 工作区

workspace:
  package_manager:
  monorepo:
  workspace_packages: []
  root_scripts:
    build:
    test:
    verify:

## 前端

frontend:
  present:
  path:
  framework:
  language:
  build_tool:
  router:
  state_management:
  ui_library:
  test_runner:
  package_scripts:
    build:
    test:
    test_coverage:

## 后端

backend:
  present:
  path:
  framework:
  language:
  orm:
  database:
  validation:
  test_runner:
  package_scripts:
    build:
    build_deploy:
    test:
    test_integration:
    test_coverage:
    orm_generate:
    schema_validate:
    migrate_dev:

## 远程平台与 CI/CD

ci_cd:
  remote_platform:
  ci_enabled:
  workflow_path:
  ci_capabilities: []

## 日常验证命令

validation_commands:
  broad_verify:
  root_build:
  root_test:
  frontend_test:
  backend_test:
  schema_validate:

## 数据库迁移处理

database_migrations:
  schema_path:
  migration_path:
  routine_schema_validation:
  migration_deploy_command:
  migration_execution_policy: 常规代码检查 Skill 不执行数据库迁移命令；只有开发者明确确认目标数据库、目标环境和具体命令后，才能进入相应操作。
