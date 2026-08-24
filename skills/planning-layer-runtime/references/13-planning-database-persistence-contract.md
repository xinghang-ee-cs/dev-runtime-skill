# Database And Persistence Planning Contract

## 1. Scope

本文档负责数据库与持久化规划在两个阶段中的边界：

- 第一阶段只发现会影响数据方案的业务事实，并保持引导式、业务化表达。
- 第二阶段在 `06` 解释业务数据与状态，在 `09` 形成并向用户确认数据库与持久化决策合同。
- 根据长期用户画像与本期 Discovery 表现调整第二阶段术语解释深度。
- 把数据库依赖、风险、待决策项和执行门禁精确传递给 `12`、`13`、Handoff、Long 与 Testing。

加载条件：

- 本期新增或修改持久化业务事实、数据库结构、数据迁移、数据环境、数据库部署或远程数据库依赖。
- 项目从 0 开始且需要保存业务数据。
- 现有数据库是否复用、是否可提供或是否可以安全访问尚未明确。
- 06、09、12、13 或 Handoff 正在生成、确认或恢复，且存在数据库相关任务。

本文件不定义数据库表名、字段类型、索引、外键、SQL、ORM Model、Migration 文件名、连接串、账号、密码或实际执行命令。

## 2. Responsibility Boundary

唯一责任链：

```text
第一阶段 Discovery
-> 业务数据来源、保留、迁移、使用方式与安全边界

06
-> 业务事实、是否持久化、状态来源、状态迁移与数据域语义

09
-> 数据库与持久化决策合同、环境拓扑、复用/新建、远程依赖、迁移与回退边界

12
-> 尚未满足的远程库、现有库材料、访问授权、备份、迁移或数据政策 RISK / DEP / OPEN

13 / Handoff
-> 引用已确认合同和阻断项，不重新选择数据库
```

规则：

- `06` 不定义物理数据库实现；它回答“哪些业务事实必须长期保留，以及怎样变化才合法”。
- `09` 是数据库与持久化实现方向的唯一规划 SoT；它回答“复用什么、选什么、各环境放在哪里、如何迁移和回退”。
- `12` 不复制数据库方案正文，只承接尚未关闭的风险、依赖和待决策项。
- `13` 不使用“开发时再看”替代数据库决策，只引用 `09` 的已确认或明确委托结论。
- 不新增独立数据库规划文档、数据库 Runtime、数据库资产台账或第二份用户画像。

## 3. First-Stage Guided Data Discovery

### 3.1 Hard Language Boundary

第一阶段继续使用业务语言。即使当前用户熟悉技术，也不得把 Discovery 退化成数据库配置问卷。

禁止把以下内容作为主动提问主体：

```text
PostgreSQL / MySQL / SQLite
ORM / Schema / Migration / Seed
主从、读写分离、连接池、事务隔离级别
连接串、端口、账号、密码、Token
云数据库产品规格或具体部署参数
```

用户主动使用专业词时，可以识别并保存为项目证据或候选事实，但下一问仍优先回到业务影响。确实必须复述专业词时，先用一句业务白话说明其含义，不以术语要求用户继续作答。

### 3.2 Evidence Before Questions

提出数据相关问题前，先检查不会暴露凭证的项目证据：

- Project Current Baseline 与已确认规划。
- 依赖清单、ORM/数据访问依赖、Schema、Migration、Seed、Docker Compose、公开环境变量示例和部署说明。
- 已有数据库测试、数据导入导出、备份恢复和环境隔离约定。
- 已有 ER 图、脱敏结构说明、数据字典或只读资料入口。

只记录会影响规划的最小结论与真实来源。不得读取、输出或持久化 `.env` 中的真实凭证、连接串、内网地址或生产账号。项目证据已经足以回答的事实不得再问用户。

### 3.3 Business Facts To Discover

仅在其会改变范围、迁移、安全、验收或数据库方向时，用自然问题按需确认：

- 当前是否已经有正式业务记录，以及这些记录现在由什么系统或位置保存。
- 已有记录是否需要继续使用、只读保留、迁入新系统或清理。
- 用户后续能否提供现有系统的结构说明、脱敏样例、备份文件或受控只读入口；第一阶段只确认“能否提供”和负责人，不索取凭证。
- 正式使用是单人本机、多人联网、跨组织使用，还是断网时也必须继续工作。
- 测试是否允许使用脱敏资料，哪些正式数据绝不能进入开发与测试。
- 哪些记录必须长期保留、允许修改或删除，以及删除后是否仍需审计留痕。
- 本期是否需要把旧数据带入新流程，迁移失败会阻断什么业务结果。

推荐问法：

```text
现在已经有正式的客户、任务或历史记录了吗？这些记录是在现有系统里继续使用，还是需要带到新系统里？

后面做开发和验证时，你们能提供不含敏感信息的样例资料，或者由负责人提供受控的查看方式吗？现在只需要确认能不能提供，不需要发送账号或密码。

正式使用时，是一台电脑自己使用，还是多人通过网络一起使用？如果断网，是否仍必须继续记录？
```

错误问法：

```text
用 PostgreSQL 还是 MySQL？
远程数据库地址和密码是什么？
ORM 和 Migration 怎么做？
```

### 3.4 First-Stage Sufficiency Boundary

第一阶段通过只要求足够生成数据库候选方案，不要求用户确认物理实现细节。至少应能区分：

- 已有数据 / 无已有数据 / 仍未知。
- 复用、迁移、只读保留、清理或新建中的业务方向。
- 单机、多人联网、跨组织或离线要求。
- 正式数据、脱敏测试资料与禁止使用资料的边界。
- 现有数据库或资料是否可能提供，以及由谁在后续阶段提供。
- 是否存在会让第二阶段无法形成安全候选方案的业务未知项。

数据库引擎、版本、环境实例、Migration 工具和远程接入方式可以在第二阶段由证据与推荐方案补齐；不得为了这些纯技术字段延长第一阶段访谈。

## 4. User-Profile-Based Explanation Adaptation

第二阶段在解释 `06`、`09`、`12`、`13` 的数据库相关内容前，必须合并以下信息：

```text
用户当前明确要求
-> 本期 Discovery 中反复体现的用词、纠正方式和理解程度
-> .runtime/planning-layer-runtime/user-profile.yaml 中高置信长期偏好
-> 信息不足时采用安全的人话解释默认值
```

优先级：当前明确表达高于本期观察，本期观察高于无冲突的长期画像。长期画像与当前表现冲突时只调整本期解释，不立即覆盖长期画像；Planning 最终收尾时再按 Interaction Preference Consolidation 规则决定是否更新。

把本期适配结果写入既有 `current-interaction.yaml.explanation_adaptation`。它只是当前期次的可恢复解释快照，不是第二份长期画像，不保存原始聊天、心理判断、职位推断或完整用户输入。

模式只允许：

- `plain_language`：专业词第一次出现时同时给出一句业务解释和实际影响。
- `adaptive`：常见词简洁使用，首次出现或可能歧义的词补一句解释。
- `technical_concise`：可以直接展示专业字段和值，但仍说明对业务、开发、测试和上线的影响。

拿不准时使用 `plain_language`。不得在用户态说“你是非技术用户”“画像判断你不懂技术”或展示内部画像字段。

## 5. Second-Stage Database And Persistence Decision Contract

本期涉及数据库或持久化时，`09-架构设计与关键决策.md` 必须包含以下唯一结构。初始批量草案允许 `blocking_open`，但 09 确认和相关 TASK Ready 前必须达到 `confirmed`、合法的 `explicitly_delegated` 或 `not_applicable`。

```yaml
database_persistence_contract:
  contract_version: database-persistence/v1
  applicable: true
  decision_status: <confirmed | explicitly_delegated | blocking_open | not_applicable>
  decision_source: <project_evidence | user_confirmation | recommended_default_confirmed | explicit_delegation>
  current_baseline:
    evidence_status: <verified | partial | none>
    existing_database: <存在、无或未知>
    engine_and_version: <已核实值、候选值或不适用>
    location_mode: <local | remote | managed_remote | embedded | unknown | not_applicable>
    evidence_refs: []
  reuse_decision: <reuse_existing | extend_existing | create_new | replace_existing | not_applicable>
  target_engine_and_version: <已确认值、明确候选或委托边界>
  environment_topology:
    local_development: <本地开发如何获得隔离且可重建的数据环境>
    test: <自动化或共享测试环境>
    staging: <预发布环境或不适用>
    production: <正式环境目标；未就绪不得写成已存在>
  remote_database:
    availability: <available | can_be_provided | unavailable | not_required | unknown>
    purpose: <existing_source | development | test | staging | production | not_applicable>
    owner_or_provider: <责任主体、提供方或待确认>
    provision_or_access_evidence: <实际证据引用、后续提供条件或阻断引用>
  existing_assets:
    schema_or_migrations: <available | can_be_provided | unavailable | not_required | unknown>
    sanitized_data_or_backup: <available | can_be_provided | unavailable | not_allowed | not_required | unknown>
    access_mode: <local_copy | sanitized_dump | read_only | controlled_session | none | unknown>
  migration:
    required: <true | false | unknown>
    source_and_scope: <来源与范围>
    compatibility_strategy: <兼容、只读、转换、切断或不适用>
    rollback_boundary: <失败后恢复到什么安全状态>
  data_governance:
    environment_isolation: <开发、测试、预发布、生产如何隔离>
    backup_restore: <备份与恢复要求或不适用>
    retention_deletion: <保留、删除与审计边界>
    sensitive_data: <脱敏、禁止复制与访问边界>
  credential_boundary: <不在规划文档或聊天保存凭证；实际凭证只由批准的秘密管理渠道提供>
  blocking_items: []
  delegation_boundary: <非委托时写 not_applicable；委托时写允许选择、既有规范、禁止影响和验证方式>
  verification_requirements: []
```

规则：

- `current_baseline` 只写已核实事实；仓库中出现依赖不等于生产正在使用。
- 正式生产远程数据库没有实际证据时只能写目标或依赖，不得写成 `available`。
- `blocking_open` 必须至少有一个 `blocking_items`，并移交 `12` 的 OPEN / DEP / RISK。
- `explicitly_delegated` 只适用于不会改变已确认业务结果、安全边界、兼容性、成本等级或上线方式的纯技术选择；必须填写非空 `delegation_boundary` 和验证要求。
- 数据库引擎、复用/替换、正式环境位置、生产数据迁移和敏感数据处理会改变业务或风险时，不得静默委托。
- 任何状态都不得包含真实连接串、账号、密码、Token、私钥、内网地址或生产数据内容。

## 6. Safe Recommendation Defaults

用户没有技术偏好时，AI 必须给出解释后的推荐方案，而不是静默假设：

1. 已有项目存在可靠数据库、ORM、Migration 和运行证据时，默认推荐复用或扩展现有体系；替换必须有明确收益、迁移与回退依据。
2. 从 0 开始的多人联网服务，在业务约束无冲突时可推荐“本地独立 PostgreSQL 开发实例 + 测试/预发布/生产相互隔离”，但必须在第二阶段标记为候选并让用户确认后才成为 `recommended_default_confirmed`。
3. 单人本机、嵌入式或明确离线的小型应用，在并发、远程共享和扩展要求无冲突时可以推荐 SQLite；不得把它推广为通用默认。
4. 本地开发默认使用隔离、可重建、非生产的数据环境。禁止默认连接生产数据库，禁止把正式数据复制到本地测试。
5. 远程数据库、正式实例、备份或只读访问没有证据时，保持 `can_be_provided`、`unknown` 或 `blocking_open`；不得推断已经就绪。
6. 推荐默认值必须说明“为什么适合当前已确认业务”“它不会替用户决定什么”“后续可如何纠正”。

## 7. Second-Stage User-Facing Confirmation

轮到 `06` 时，用用户能理解的方式说明：

- 系统要长期保留哪些业务记录。
- 哪些变化必须由系统判断，哪些只是页面暂时显示。
- 旧记录是否继续影响新流程。
- 开发、测试和正式数据为什么要分开。

轮到 `09` 时，聊天回复必须直接包含数据库方案摘要，不得只让用户打开文档：

- 现在有没有可复用的库和数据。
- 开发阶段在哪里启动数据环境。
- 正式阶段是否需要远程数据库，目前是否已具备。
- 使用什么数据库及为什么适合。
- 是否需要旧数据、结构资料、脱敏样例、迁移与回退。
- 哪些资料由谁在什么时候提供，缺失会阻断什么。
- 当前采用的是证据结论、用户确认、推荐默认值还是明确委托。

`plain_language` 示例：

```text
这份草案建议开发时先在本机启动一套独立数据环境，不连接正式业务数据；正式上线再使用单独的远程数据库。这样开发出错不会影响真实记录。这里写的 PostgreSQL 是保存多人业务数据的软件，你不需要配置它，只需要确认这个方向是否可以。
```

`technical_concise` 示例：

```text
当前候选为 PostgreSQL 16：local/test 使用隔离实例，staging/production 独立远程实例；复用现有 Migration 体系，不允许开发环境直连生产。现有 Schema 与脱敏 Seed 尚待提供，属于开发入口依赖。请确认引擎、环境拓扑和迁移边界。
```

用户确认默认推荐后才允许写 `confirmed`。用户纠正时回写 09 并只重建受影响的 10–13、14/15 空白框架和 Handoff；不得重跑无关 Discovery 或重建未受影响文档。

## 8. Gate And Validation

Database And Persistence Decision Gate：

- 06 已说明哪些事实需要持久化及数据域语义。
- 09 存在唯一 `database_persistence_contract`。
- 当前事实、候选、用户确认、默认推荐和委托没有混写。
- 现有库复用或新建、目标引擎、各环境拓扑、远程库状态、可提供材料、迁移、回退、隔离、备份、保留删除和敏感数据边界均已覆盖。
- 用户态解释已按 `explanation_adaptation` 输出；专业文档可以保留术语，但不得把裸术语作为用户确认对象。
- 无真实凭证、连接串、生产数据或伪造的远程就绪结论。
- `blocking_open` 已移交 12；相关 TASK 不得 Ready。
- `explicitly_delegated` 有完整边界和验证要求。

初始草案或受阻状态校验：

```text
python skills/planning-layer-runtime/scripts/validate_database_persistence_contract.py <09-path> --allow-blocked
```

09 确认、13 生成和 Handoff 前校验：

```text
python skills/planning-layer-runtime/scripts/validate_database_persistence_contract.py <09-path>
```

校验失败时，回写真正拥有事实的 06、09 或 12；不得在 13 中临时补造数据库方案。
