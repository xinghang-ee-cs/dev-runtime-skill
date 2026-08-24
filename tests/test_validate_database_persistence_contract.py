from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = (
    REPOSITORY_ROOT
    / "skills/planning-layer-runtime/scripts/validate_database_persistence_contract.py"
)


def contract(status: str = "confirmed", blocking_items: str = "[]") -> str:
    return textwrap.dedent(
        f"""
        # 09-架构设计与关键决策

        ## 数据库与持久化决策合同

        ```yaml
        database_persistence_contract:
          contract_version: database-persistence/v1
          applicable: true
          decision_status: {status}
          decision_source: user_confirmation
          current_baseline:
            evidence_status: verified
            existing_database: 无
            engine_and_version: not_applicable
            location_mode: not_applicable
            evidence_refs: []
          reuse_decision: create_new
          target_engine_and_version: PostgreSQL 16
          environment_topology:
            local_development: 本地隔离实例
            test: 独立测试实例
            staging: 独立预发布实例
            production: 独立正式实例，尚待后续提供
          remote_database:
            availability: can_be_provided
            purpose: production
            owner_or_provider: 项目负责人
            provision_or_access_evidence: 上线准备阶段提供
          existing_assets:
            schema_or_migrations: not_required
            sanitized_data_or_backup: not_required
            access_mode: none
          migration:
            required: false
            source_and_scope: not_applicable
            compatibility_strategy: not_applicable
            rollback_boundary: 回到迁移前备份
          data_governance:
            environment_isolation: 各环境完全隔离
            backup_restore: 上线前验证备份恢复
            retention_deletion: 按业务保留规则执行
            sensitive_data: 正式数据不得进入开发与测试
          credential_boundary: 凭证只通过批准的秘密管理渠道提供
          blocking_items: {blocking_items}
          delegation_boundary: not_applicable
          verification_requirements:
            - 验证各环境互不串库
        ```
        """
    ).strip() + "\n"


class DatabasePersistenceContractValidatorTests(unittest.TestCase):
    def run_validator(self, body: str, *args: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "09.md"
            path.write_text(body, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(path), *args],
                capture_output=True,
                text=True,
            )

    def test_confirmed_contract_passes(self) -> None:
        result = self.run_validator(contract())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_contract_fails(self) -> None:
        result = self.run_validator("# 09\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing database_persistence_contract", result.stderr)

    def test_blocked_contract_requires_flag_and_item(self) -> None:
        rejected = self.run_validator(contract("blocking_open", "[DEP-DB-001]"))
        self.assertEqual(rejected.returncode, 1)

        accepted = self.run_validator(
            contract("blocking_open", "[DEP-DB-001]"), "--allow-blocked"
        )
        self.assertEqual(accepted.returncode, 0, accepted.stderr)

        empty = self.run_validator(contract("blocking_open"), "--allow-blocked")
        self.assertEqual(empty.returncode, 1)
        self.assertIn("blocking_items", empty.stderr)

    def test_explicit_delegation_requires_boundary(self) -> None:
        result = self.run_validator(contract("explicitly_delegated"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("delegation_boundary", result.stderr)

    def test_credential_bearing_connection_string_fails(self) -> None:
        body = contract().replace(
            "凭证只通过批准的秘密管理渠道提供",
            "postgresql://app:unsafe-password@example.invalid/database",
        )
        result = self.run_validator(body)
        self.assertEqual(result.returncode, 1)
        self.assertIn("credential", result.stderr)


if __name__ == "__main__":
    unittest.main()
