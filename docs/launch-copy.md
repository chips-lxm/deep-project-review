# 发布介绍文案

## GitHub About

Codex project reviews with GPT-6 Sol, Luna high, mandatory Astra xhigh adjudication, scoped repairs, and independent verification.

## 中文分享文案

给已完成的项目，一次有证据的独立复审。

Deep Project Review「项目深度复审」是一个 Codex Skill：用户明确启动后，通常由 2—4 个真实子智能体独立检查，单独的 gpt-6-astra · xhigh 核对证据、处理冲突与误报。保持用户选定模型的主会话统筹授权内修复和独立验收。gpt-6-sol 承接原 Sol 与 Terra 的分析及实现职责，使用 medium/high、必要时 xhigh；gpt-6-luna 只处理边界明确、低风险且可核对的任务，始终使用 high。模型路由合并不合并独立审查与修复职责。

支持代码、文档、表格、设计和演示材料。用户明确启动，默认最多两轮修复—复验，保留未提交改动，明确区分通过、失败、未运行和无法验证。

早期 v0.1.0 的测试结果属于历史记录。当前模型迁移的检查与限制见 [迁移验证报告](../tests/migration-2026-09-23/VALIDATION.md)；不承诺普遍的质量、耗时或 Token 用量收益。

## English share copy

Give finished work an independent review backed by evidence.

Deep Project Review is a Codex skill with explicit invocation, usually 2–4 focused independent reviewers, mandatory separate gpt-6-astra xhigh adjudication, authorized repairs, and independent acceptance checks. The lead remains on the user's selected model. gpt-6-sol covers former Sol and Terra analysis and implementation at medium/high, with xhigh when needed; gpt-6-luna handles only bounded, low-risk, verifiable work at high. Consolidated model routes keep reviewer and fixer roles independent.

Explicit invocation. Scoped changes. Two repair–verification rounds by default. Clear reporting of what passed, failed, or could not be verified.

Earlier v0.1.0 results are historical. The [migration validation report](../tests/migration-2026-09-23/VALIDATION.md) records current checks and limits. No universal quality, latency, or token savings are claimed.

## 首次发布说明（v0.1.0）

- 项目深度复审 Skill 与显式调用策略。
- 四模型调度映射、固定 Astra xhigh 结论复核及运行配置验证要求。
- 基准、独立报告、修复任务与验收模板。
- 中英双语项目介绍及四电脑会议主题封面。
- 脱敏测试记录、行为案例、可选入口与自定义 agent 示例。
- 安装用 ZIP 与 SHA-256 校验文件。

限制：完整流程与宿主触发未端到端验证；自然语言入口须单独部署和验证。此版本不承诺无缺陷结果或所有宿主兼容。
