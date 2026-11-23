# 发布介绍文案

## GitHub About

Independent Codex project reviews with GPT-6.2 Sol, GPT-6.2 Astra xhigh adjudication, scoped repairs, and verifiable acceptance evidence.

## 中文分享文案

给已完成的项目，一次有证据的独立复审。

Deep Project Review「项目深度复审」是一个 Codex Skill。用户明确启动后，多位真实子智能体独立审查，再由单独的 GPT-6.2 Astra `xhigh` 核对完整报告、原始需求和关键证据。初审、修复与独立验收统一使用 GPT-6.2 Sol，按任务选择推理强度。主会话保留用户选定的模型，统筹授权范围和实际交付。

支持代码、文档、表格、设计和演示材料。最多两轮修复—复验。证据检查器核对基准、覆盖、修复授权与验收职责，记录通过、失败、未运行和无法验证的状态。

本次迁移的验证范围见 [当前交接](../HANDOFF.md)。

## English share copy

Give finished work an independent review backed by evidence.

Deep Project Review is a Codex skill for explicitly invoked independent reviews, with separate GPT-6.2 Astra `xhigh` adjudication. GPT-6.2 Sol handles initial reviews, repairs, and independent acceptance at the reasoning effort each task needs. The lead keeps the user's selected model.

The evidence checker checks revisions, coverage, repair authorization, and reviewer independence. The workflow allows up to two repair–verification rounds and reports whether each check passed, failed, was skipped, or could not be verified.

The [current handoff](../HANDOFF.md) records the validation scope for this release.

## v0.4.0 更新说明 / Release notes (2026-11-23)

### 中文

- **统一常规任务路由。** GPT-6.2 Sol 负责初审、授权内修复和独立验收。`high` 是默认档位，`medium` 适合边界明确且易核对的任务，`xhigh` 用于复杂根因和跨模块影响，`max` 留给决定交付的疑难判断。
- **更新独立裁决。** GPT-6.2 Astra `xhigh` 负责正式裁决和必要的定向复核，依据原始需求、完整报告和关键验证证据。每轮保留请求配置和可信宿主证据。
- **增加证据检查器。** 检查需求与版本的对应关系、关键验收覆盖、修复授权、轮数和验收者身份。保留显式调用、至少两位独立初审者，以及最多两轮修复—复验。验收者亲自执行关键检查。
- **安装。** 下载 `deep-project-review.zip` 和 `SHA256SUMS.txt`，核对校验和后升级完整目录。保留自定义文件，让已有复审继续使用各自的规则快照。

### English

- **Unified routine routing.** Initial reviews, scoped repairs, and independent acceptance use GPT-6.2 Sol. The default is `high`. Use `medium` for bounded checks, `xhigh` for complex dependencies or root causes, and `max` for hard decisions that determine delivery.
- **Updated independent adjudication.** GPT-6.2 Astra `xhigh` reviews the original requirements, complete reviewer reports, and key evidence. It also performs required focused rechecks. Record requested settings and trusted runtime evidence.
- **Evidence checker.** Verify the links among requirements, revisions, coverage, repair authorization, round counts, and acceptance agents. Explicit invocation, at least two independent first-pass reviewers, and the two-round limit are retained.
- **Installation.** Verify `deep-project-review.zip` against `SHA256SUMS.txt` and upgrade the complete skill directory. Preserve local customizations and allow existing reviews to finish with their pinned rules.

### 验证 / Verification

23 项快照与证据检查测试通过。同一合成案例中，两代 Astra 都确认四项缺陷。新版完成一次修复后，独立验收通过原有 5 项测试及 17 项定向回归，并通过证据检查器的三个阶段。

All 23 snapshot and evidence-check tests passed. Both Astra generations confirmed the same four defects on one synthetic case. After one repair round, independent acceptance passed all five provided tests and 17 targeted regression checks, and the record cleared all three workflow gates.

[使用与配置 / Usage and configuration](../README.md) · [验证详情 / Validation details](../HANDOFF.md) · [全部变更 / Full changes](https://github.com/chips-lxm/deep-project-review/compare/v0.3.0...v0.4.0)

## v0.3.0 更新说明（2026-09-30）

本次更新把默认实现、常规审查和独立验收路由改为 GPT-6.1 Sol high，并允许按难点直接使用 xhigh/max，同时保留项目深度复审的完整独立审核流程。

## 中文更新说明

- **模型选择**：6.1 Sol 从 `high` 起步，可按明确难点直接选 `xhigh` 或 `max`，不要求先逐级失败。Luna 固定 `high`，只处理边界明确、低风险、易核对的任务；旧 6 Sol 保留已有验证支持的适用路径，不作为必经中间层或静默回退。
- **审核要求**：明确启动；多个真实审查者独立形成首轮判断；单独 Astra xhigh 复核；授权范围内修复；未参与修复者亲自验收；默认最多两轮修复—复验。
- **减少重复工作**：共同背景与原始事实集中维护，分支引用必要材料；精简交接但保留全部发现、失败和反对证据。已有验证仅在需求、版本、输入、环境与依赖仍适用时复用，独立验收者仍亲自执行关键检查。
- **固定运行版本**：新增 `scripts/freeze_run.py` 和随包 `runtime-manifest.json`。长任务与分支可固定一次规则快照；缺失清单、部分更新、文件漂移和常见 Skill 发现目录中的输出均拒绝。`--seal` 仅供维护者有意修改后的清单更新，正常运行不能用它掩盖不一致。
- **问题修正**：补齐插件缓存路径检查，澄清协调职责、困难任务模型选择及审查者复用为验收者的边界；同步中英文说明，并保留历史验证原始结果。

### 验证与边界

本包快照测试 **10/10 通过**，两个包合计 20 项；官方 Skill 格式、配置解析和本地文档引用检查通过。两路独立评估提出的问题已修复并完成定向复查。完整源包与已安装版本均通过快照创建及自带脚本校验；本机 Codex `skills/list` 实际识别两个已启用的 Skill。

上述结果是 Skill 维护验证，不是新版在真实项目上的完整多模型复审验收。未进行同任务 Token/费用/延迟对照，也未实测 6.1 Sol xhigh/max 的项目效果；不保证固定节省比例，不宣称 max 与 Astra 全面等价。模型和推理强度仍须按目标宿主的实际支持与调用证据核实。

### 升级方法

下载附件 `deep-project-review.zip` 与 `SHA256SUMS.txt`，核对校验和后，将 ZIP 内的 `deep-project-review` 文件夹安装到 Codex 的 skills 目录。先保存现有自定义内容，并在任务空闲或明确版本切换点更新；运行文件与 `runtime-manifest.json` 必须来自同一版本，不能只替换 `SKILL.md`。已有任务的固定快照可继续使用旧规则；安装更新不会追溯改写已载入的上下文。

## English release notes

GPT-6.1 Sol is the default execution and ordinary-review route at **high**, with direct **xhigh/max** selection for justified difficulty. Luna remains high for bounded, low-risk work; GPT-6 Sol remains an evidence-backed option rather than a mandatory intermediate tier or silent fallback.

Deep Project Review retains explicit invocation, multiple real independent reviewers, separate Astra xhigh adjudication, permission-scoped repairs, personal verification by a non-fixer, and the two-round repair–verification limit.

Shared source facts, focused handoffs, and version-aware evidence reuse reduce unnecessary repetition without replacing personal independent checks. The new snapshot helper checks a separately maintained runtime manifest, pins a run's instructions, rejects partial installations and common discovery-root destinations, and never automatically reseals inconsistent input.

Validation includes 10 passing snapshot tests in this package, format/configuration/reference checks, independent evaluations with targeted rechecks, source and installed-package snapshot verification, and actual local Codex skill discovery. These checks do not establish end-to-end project review quality, a fixed token/latency improvement, or equivalence between Sol max and Astra.

Preserve customizations before upgrading. Install the complete enclosed folder, including its runtime manifest, at an idle or explicit version boundary. Existing frozen runs may continue using their pinned version.

[完整验证记录 / Validation report](https://github.com/chips-lxm/deep-project-review/blob/v0.3.0/tests/update-2026-09-30/VALIDATION.md) · [全部变更 / Full changes](https://github.com/chips-lxm/deep-project-review/compare/v0.2.0...v0.3.0)

## 首次发布说明（v0.1.0）

- 项目深度复审 Skill 与显式调用策略。
- 四模型调度映射、固定 Astra xhigh 结论复核及运行配置验证要求。
- 基准、独立报告、修复任务与验收模板。
- 中英双语项目介绍及四电脑会议主题封面。
- 脱敏测试记录、行为案例、可选入口与自定义 agent 示例。
- 安装用 ZIP 与 SHA-256 校验文件。

限制：完整流程与宿主触发未端到端验证；自然语言入口须单独部署和验证。此版本不承诺无缺陷结果或所有宿主兼容。
