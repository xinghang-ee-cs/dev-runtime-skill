from __future__ import annotations

import re
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


def contract(
    status: str = "confirmed",
    blocking_items: str = "[]",
    version: str = "database-persistence/v2",
) -> str:
    return textwrap.dedent(
        f"""
        # 09-架构设计与关键决策

        ## 数据库与持久化决策合同

        ```yaml
        database_persistence_contract:
          contract_version: {version}
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
          physical_data_design:
            design_mode: create_new
            storage_model: relational
            schema_source_refs: []
            prohibited_extra_storage_units: true
            storage_units:
              - storage_unit_id: DATASTORE-CUSTOMER
                unit_kind: table
                physical_name: customers
                change_action: create
                business_object_refs: [OBJECT-CUSTOMER]
                fields:
                  - physical_name: id
                    storage_type: uuid
                    nullable: false
                    default_or_generation: generated_uuid
                    business_meaning: 客户记录唯一标识
                    fact_or_state_refs: [OBJECT-CUSTOMER.identity]
                    sensitive_classification: internal
                  - physical_name: display_name
                    storage_type: varchar_200
                    nullable: false
                    default_or_generation: not_applicable
                    business_meaning: 客户显示名称
                    fact_or_state_refs: [OBJECT-CUSTOMER.display_name]
                    sensitive_classification: internal
                identity_key: [id]
                unique_constraints: [uq_customers_display_name(display_name)]
                indexes: [idx_customers_display_name(display_name)]
                relations: []
                tenant_and_access_boundary: 单租户项目内受权限合同约束
                lifecycle_and_deletion: 删除时保留审计记录
                migration_and_backfill: not_applicable
          credential_boundary: 凭证只通过批准的秘密管理渠道提供
          execution_prerequisites:
            - prerequisite_ref: DB-PREREQ-001
              purpose: 支持本地启动与最小业务验证
              responsible_party: agent_task
              earliest_required_stage: before_long
              provision_channel: 项目公开配置入口
              safe_verification: 只验证配置入口和目标进程绑定，不读取值
              secret_handling: never_in_chat_or_planning_docs
              covers_contract_paths: []
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

    def test_legacy_v1_without_execution_prerequisites_still_passes(self) -> None:
        body = re.sub(
            r"(?ms)^\s*execution_prerequisites:\n(?:\s+- prerequisite_ref:.*?)(?=^\s*blocking_items:)",
            "",
            contract(version="database-persistence/v1"),
        )
        body = re.sub(
            r"(?ms)^\s*physical_data_design:\n.*?(?=^\s*credential_boundary:)",
            "",
            body,
        )
        result = self.run_validator(body)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("legacy v1", result.stdout)

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
        for connection_string in (
            "postgresql://app:unsafe-password@example.invalid/database",
            "redis://app:unsafe-password@example.invalid/0",
        ):
            with self.subTest(connection_string=connection_string):
                body = contract().replace(
                    "凭证只通过批准的秘密管理渠道提供",
                    connection_string,
                )
                result = self.run_validator(body)
                self.assertEqual(result.returncode, 1)
                self.assertIn("credential", result.stderr)

    def test_sensitive_assignment_fails(self) -> None:
        for field in (
            "api_key",
            "client_secret",
            "access_token",
            "auth_token",
            "bearer_token",
            "id_token",
            "webhook_secret",
            "signing_secret",
            "ssh_key",
            "jwt",
            "DATABASE_URL",
        ):
            with self.subTest(field=field):
                body = contract().replace(
                    "credential_boundary: 凭证只通过批准的秘密管理渠道提供",
                    "credential_boundary: 凭证只通过批准的秘密管理渠道提供\n"
                    f"  {field}: unsafe-live-value",
                )
                result = self.run_validator(body)
                self.assertEqual(result.returncode, 1)
                self.assertIn("credential", result.stderr)

        bracketed_secret = contract().replace(
            "credential_boundary: 凭证只通过批准的秘密管理渠道提供",
            "credential_boundary: 凭证只通过批准的秘密管理渠道提供\n"
            "  api_key: [sk-live-example]",
        )
        result = self.run_validator(bracketed_secret)
        self.assertEqual(result.returncode, 1)
        self.assertIn("credential", result.stderr)

    def test_connection_string_or_private_network_address_fails(self) -> None:
        for forbidden_value in (
            "postgresql://db.example.invalid:5432/private",
            "https://10.0.0.7/private",
            "db.service.internal",
            "localhost:5432",
        ):
            with self.subTest(forbidden_value=forbidden_value):
                body = contract().replace(
                    "credential_boundary: 凭证只通过批准的秘密管理渠道提供",
                    "credential_boundary: 凭证只通过批准的秘密管理渠道提供\n"
                    f"  internal_endpoint: {forbidden_value}",
                )
                result = self.run_validator(body)
                self.assertEqual(result.returncode, 1)
                self.assertIn("private network", result.stderr)

    def test_duplicate_mapping_keys_fail(self) -> None:
        variants = (
            contract().replace(
                "  blocking_items: []",
                "  decision_status: blocking_open\n  blocking_items: []",
            ),
            contract().replace(
                "    provision_or_access_evidence: 上线准备阶段提供",
                "    provision_or_access_evidence: 上线准备阶段提供\n"
                "  remote_database:\n"
                "    availability: unavailable",
            ),
            contract().replace(
                "      responsible_party: agent_task",
                "      responsible_party: agent_task\n"
                "      responsible_party: somebody",
            ),
        )
        for body in variants:
            with self.subTest(body=body):
                result = self.run_validator(body)
                self.assertEqual(result.returncode, 1)
                self.assertIn("duplicate mapping key", result.stderr)

    def test_unknown_fact_requires_one_prerequisite_binding(self) -> None:
        unbound = contract().replace(
            "availability: can_be_provided", "availability: unknown"
        )
        result = self.run_validator(unbound)
        self.assertEqual(result.returncode, 1)
        self.assertIn("remote_database.availability", result.stderr)

        bound = unbound.replace(
            "earliest_required_stage: before_long",
            "earliest_required_stage: before_release",
        ).replace(
            "covers_contract_paths: []",
            "covers_contract_paths: [remote_database.availability]",
        )
        result = self.run_validator(bound)
        self.assertEqual(result.returncode, 0, result.stderr)

        duplicate_binding = bound.replace(
            "covers_contract_paths: [remote_database.availability]",
            "covers_contract_paths: [remote_database.availability]\n"
            "            - prerequisite_ref: DB-PREREQ-002\n"
            "              purpose: 支持正式环境数据库准备\n"
            "              responsible_party: external_party\n"
            "              earliest_required_stage: before_release\n"
            "              provision_channel: 批准的秘密管理渠道\n"
            "              safe_verification: 只验证受控就绪结果，不读取值\n"
            "              secret_handling: never_in_chat_or_planning_docs\n"
            "              covers_contract_paths: [remote_database.availability]",
        )
        result = self.run_validator(duplicate_binding)
        self.assertEqual(result.returncode, 1)
        self.assertIn("more than one", result.stderr)

    def test_required_fields_must_exist_at_the_declared_path(self) -> None:
        body = contract().replace("    purpose: production\n", "")
        result = self.run_validator(body)
        self.assertEqual(result.returncode, 1)
        self.assertIn("remote_database.purpose", result.stderr)

    def test_prerequisite_field_does_not_compensate_for_remote_database_field(self) -> None:
        body = contract().replace("    purpose: production\n", "")
        self.assertIn("purpose: 支持本地启动与最小业务验证", body)
        result = self.run_validator(body)
        self.assertEqual(result.returncode, 1)
        self.assertIn("remote_database.purpose", result.stderr)

    def test_v2_applicable_confirmed_contract_requires_execution_prerequisite(self) -> None:
        body = re.sub(
            r"(?ms)^\s*execution_prerequisites:\n(?:\s+- prerequisite_ref:.*?)(?=^\s*blocking_items:)",
            "",
            contract(),
        )
        result = self.run_validator(body)
        self.assertEqual(result.returncode, 1)
        self.assertIn("execution_prerequisites", result.stderr)

    def test_execution_prerequisite_enums_are_validated(self) -> None:
        for version in ("database-persistence/v1", "database-persistence/v2"):
            with self.subTest(version=version):
                body = contract(version=version).replace(
                    "responsible_party: agent_task", "responsible_party: somebody"
                )
                result = self.run_validator(body)
                self.assertEqual(result.returncode, 1)
                self.assertIn("responsible_party", result.stderr)

    def test_unknown_contract_version_fails(self) -> None:
        result = self.run_validator(
            contract(version="database-persistence/v3")
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("contract_version", result.stderr)

    def test_v2_requires_physical_data_design(self) -> None:
        body = re.sub(
            r"(?ms)^\s*physical_data_design:\n.*?(?=^\s*credential_boundary:)",
            "",
            contract(),
        )
        result = self.run_validator(body)
        self.assertEqual(result.returncode, 1)
        self.assertIn("physical_data_design", result.stderr)

    def test_new_design_requires_concrete_storage_units_and_fields(self) -> None:
        no_units = re.sub(
            r"(?ms)^\s*storage_units:\n.*?(?=^\s*credential_boundary:)",
            "    storage_units: []\n",
            contract(),
        )
        result = self.run_validator(no_units)
        self.assertEqual(result.returncode, 1)
        self.assertIn("requires at least one physical storage unit", result.stderr)

        no_fields = re.sub(
            r"(?ms)^\s*fields:\n.*?(?=^\s*identity_key:)",
            "        fields: []\n",
            contract(),
        )
        result = self.run_validator(no_fields)
        self.assertEqual(result.returncode, 1)
        self.assertIn("requires concrete fields", result.stderr)

    def test_extra_storage_units_must_be_forbidden(self) -> None:
        body = contract().replace(
            "prohibited_extra_storage_units: true",
            "prohibited_extra_storage_units: false",
        )
        result = self.run_validator(body)
        self.assertEqual(result.returncode, 1)
        self.assertIn("prohibited_extra_storage_units must be true", result.stderr)

    def test_physical_fields_and_identity_must_be_executable(self) -> None:
        blank_type = contract().replace("storage_type: uuid", "storage_type:")
        result = self.run_validator(blank_type)
        self.assertEqual(result.returncode, 1)
        self.assertIn("requires concrete storage_type", result.stderr)

        unknown_identity = contract().replace("identity_key: [id]", "identity_key: [missing_id]")
        result = self.run_validator(unknown_identity)
        self.assertEqual(result.returncode, 1)
        self.assertIn("is not a declared field", result.stderr)

    def test_multi_field_index_text_remains_one_contract_item(self) -> None:
        body = contract().replace(
            "idx_customers_display_name(display_name)",
            "idx_customers_scope(tenant_id,display_name)",
        )
        result = self.run_validator(body)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_reuse_unchanged_uses_schema_source_without_redefining_tables(self) -> None:
        body = re.sub(
            r"(?ms)^\s*physical_data_design:\n.*?(?=^\s*credential_boundary:)",
            "  physical_data_design:\n"
            "    design_mode: reuse_existing_unchanged\n"
            "    storage_model: relational\n"
            "    schema_source_refs: [prisma/schema.prisma]\n"
            "    prohibited_extra_storage_units: true\n"
            "    storage_units: []\n",
            contract(),
        )
        result = self.run_validator(body)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_duplicate_or_planning_named_physical_units_fail(self) -> None:
        duplicate = contract().replace(
            "        tenant_and_access_boundary: 单租户项目内受权限合同约束",
            "        tenant_and_access_boundary: 单租户项目内受权限合同约束\n"
            "      - storage_unit_id: DATASTORE-CUSTOMER-COPY\n"
            "        unit_kind: external\n"
            "        physical_name: customers\n"
            "        change_action: reuse\n"
            "        business_object_refs: [OBJECT-CUSTOMER]\n"
            "        fields: []\n"
            "        identity_key: []\n"
            "        unique_constraints: []\n"
            "        indexes: []\n"
            "        relations: []\n"
            "        tenant_and_access_boundary: 与客户记录相同\n"
            "        lifecycle_and_deletion: 跟随外部来源\n"
            "        migration_and_backfill: not_applicable",
        )
        result = self.run_validator(duplicate)
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate physical storage unit name", result.stderr)

        planning_named = contract().replace("physical_name: customers", "physical_name: phase_01_customers")
        result = self.run_validator(planning_named)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Planning or phase naming", result.stderr)


if __name__ == "__main__":
    unittest.main()
