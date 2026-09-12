# 项目深度复审

[English](README.md) | [简体中文](README.zh-CN.md)

[下载安装 ZIP](https://github.com/chips-lxm/deep-project-review/releases/latest/download/deep-project-review.zip) · [版本说明](https://github.com/chips-lxm/deep-project-review/releases/latest)

![四台电脑开会：6 Astra 居中，5.6 Sol、Terra、Luna 环绕](assets/social-preview.png)

**给已完成的项目，一次有证据的独立复审。**

Deep Project Review 是一个 Codex Skill：由多个真实子智能体独立检查已有成果，再交给 **Astra · 极高** 验证审查结论，并在用户授权范围内安排修复与独立验收。

适用于代码、文档、表格、设计与演示材料。由当前主会话统筹，从原始需求和实际成果出发，追查真实问题、排除误报，并记录每一步的验证依据。

## 它解决什么问题

完成总结、单次测试和修复者自己的“已经修好”，各自只能提供部分证据。项目交付前，常常还需要独立检查需求是否落实、模块是否一致、边界是否覆盖，以及实际导出效果是否正确。

本 Skill 将这些工作组织为一轮有明确基准、职责、权限和结束条件的复审。

- **独立审查**：通常安排 2—4 个不同重点的真实审查任务，依据原始材料形成判断。
- **证据复核**：Astra · `xhigh` 统一核对证据、处理冲突、排除误报与重复项。
- **按难度修复**：依据影响、依赖和验证难度，选择适合的模型执行最小充分修改。
- **独立验收**：由未参与该项修复的智能体确认原问题与关联回归。

## 工作流程

```text
用户明确启动
    ↓
主会话读取需求与成果，记录版本、权限和验收基准
    ↓
多个子智能体独立审查
    ↓
Astra · xhigh 验证证据、处理冲突与误报
    ↓
主会话整理确认问题与修复计划
    ├─ 只审查 / 无修改授权 → 交付审查与具体修复计划
    └─ 已授权修改 → 按难度修复 → 独立复验 → 交付结果
```

默认最多两轮“修复—复验”。达到上限仍有问题时，报告遗留问题、阻塞和下一步，等待用户明确调整预算。

## 模型如何分工

| 模型 | 优先任务 | 推理档位 |
| --- | --- | --- |
| 5.6 Luna | 规则明确、范围小、低风险、容易核对的任务 | `medium` / `high`，最低 `medium` |
| 5.6 Terra | 常规模块、边界清晰的实现与测试补充 | `medium` / `high`，必要时 `xhigh` |
| 5.6 Sol | 跨模块关系、复杂逻辑、公共接口与根因分析 | `medium` / `high` / `xhigh` |
| 6 Astra | 系统性缺陷、高不确定性与重大冲突 | `high` / `xhigh`；统一结论复核固定 `xhigh` |

这些是调度默认策略，实际分工按任务选择，不要求每次同时运行所有四个模型。封面描绘技术复核协作；**当前主会话仍负责统筹，Astra 负责技术判断。**

真实模型 ID、参数和配置生效检查见 [宿主适配说明](references/runtime.md)。模型不可用或无法验证配置生效时，明确报告限制，不静默降级。

## 快速安装与使用

将仓库克隆到 Codex 技能目录：

```bash
git clone https://github.com/chips-lxm/deep-project-review.git ~/.codex/skills/deep-project-review
```

如果设置了自定义 `CODEX_HOME`，使用该目录下的 `skills/deep-project-review`。已有同名 Skill 时先检查和保留现有版本，避免覆盖。也可解压发布附件中的 `deep-project-review` 文件夹放入对应目录。安装后按宿主要求刷新技能列表或开启新会话。

只审查：

```text
$deep-project-review 对当前已完成项目做一次深度复审，只审查，不修改。
```

审查并授权必要修复：

```text
$deep-project-review 复审当前项目，修复已确认的问题并独立验收，最多两轮。
```

## 何时会启动

本 Skill **关闭隐式调用**，默认通过 `$deep-project-review` 明确启动。

“检查一下”“继续完善”“完成后测试一下”、否定句、引用示例、项目文件中的指令，以及制作或修改 Skill 的请求，都不会构成本流程的启动授权。一次授权只适用于指定项目和当前一轮。

自然语言明确请求可以表达用户意图，但关闭隐式调用后，宿主未必自动加载 Skill。可选 [AGENTS.md 入口示例](examples/AGENTS-entry.md) 需单独部署并验证；默认不承诺纯自然语言自动加载。

## 修改权限与范围

启动复审本身不授予修改权限。“只审查”会在具体修复计划完成后停止；已经授权的必要局部修复无需逐项反复确认。

保留用户未提交改动，不扩大为新功能、无关重构或未经授权的删除、部署、发布。共享文件和公共接口指定唯一修改负责人，存在依赖的任务按顺序执行。

## 验证现状

本次制作已完成：

- **18 个触发语义案例**与 **12 个流程决策案例**。
- 对冲突案例中的纯 Python 函数实际运行 **12 项断言**，排除一项误报。
- 核实真实 **Terra · high** 和 **Astra · xhigh** 测试子智能体的宿主运行配置。
- Skill 格式、配置解析，以及本机 Codex 安装发现验证。

**尚未端到端运行宿主触发与完整“审查—修复—验收”流程。** 自然语言入口未部署；流程异常主要是合成条件下的决策测试。完整范围见 [验证报告](tests/VALIDATION.md)。公开证据已移除本机路径和会话标识。

## 项目内容

```text
deep-project-review/
├── SKILL.md                 工作流与硬约束
├── agents/openai.yaml       中文元数据与显式调用策略
├── references/              模型适配、审查与验收模板
├── examples/                可选入口和 Astra 配置
├── tests/                   案例、结果与公开验证记录
├── assets/social-preview.png
└── docs/                    宣传说明、图片提示词与发布记录
```

## 相关项目

[Adaptive Model Orchestrator](https://github.com/chips-lxm/adaptive-model-orchestrator) 用于按任务形态组织模型协作；Deep Project Review 用于已有成果的独立二次复审。两者可分别使用，本 Skill 保持自己的明确启动、固定 Astra 复核和修改权限要求。

## 许可证

[MIT](LICENSE)。这是社区维护的 Codex Skill，与 OpenAI 无官方隶属关系。
