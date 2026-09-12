# 宿主与模型适配

## 经核实的映射（2026-09-12，Codex desktop / CLI 0.154.0）

| 用户称呼 | 实际 model ID | 本 Skill 使用的推理值 |
| --- | --- | --- |
| 5.6 Luna | gpt-5.6-luna | medium / high |
| 5.6 Terra | gpt-5.6-terra | medium / high / xhigh |
| 5.6 Sol | gpt-5.6-sol | medium / high / xhigh |
| Astra | gpt-6-astra | high / xhigh |
| Astra·极高（固定复核） | gpt-6-astra | xhigh |

中 = `medium`，高 = `high`，极高 = `xhigh`（本机模型目录描述为 “Extra high reasoning depth for complex problems”）。`max` 与 `ultra` 是另外的档位，不是“极高”的替代值。不要使用 `Astra`、`Sol` 等昵称作为 model ID，也不要依赖可能变化的 `gpt-5.6` 别名。

本机 `~/.codex/models_cache.json` 的 2026-09-12 快照及本次工具 schema 均列出四个 ID 的 `medium/high/xhigh` 支持；缓存只能证明目录声明，不能证明本次执行成功。官方模型页也列出这些档位，但 API 可用性不代表 Codex 当前账号一定能调用。

## 当前 desktop 原生调用

当前工具为 `collaboration.spawn_agent`，模型和推理参数必须放在结构化参数中：

```json
{
  "task_name": "review_core",
  "fork_turns": "none",
  "model": "gpt-5.6-sol",
  "reasoning_effort": "high",
  "message": "本轮已获用户授权。只审查指定基准的核心逻辑；读取提供的原始要求与实际文件；禁止修改正式项目或读取其他审查者报告；按报告模板返回证据。这里应补齐本轮绝对路径、范围、基准和验收标准。"
}
```

Astra 结论复核独立调用如下；调用前填齐实际材料，不要原样发送泛化示例：

```json
{
  "task_name": "astra_adjudication",
  "fork_turns": "none",
  "model": "gpt-6-astra",
  "reasoning_effort": "xhigh",
  "message": "独立复核本轮所有审查结论。读取原始需求、完整报告、覆盖矩阵、基准与实际证据；解决冲突、误报和重复；对重大问题追溯验证；按四类结论输出修复边界和验收标准。这里应补齐所有材料绝对路径及完整报告索引。"
}
```

此宿主全历史 fork 继承父配置且不接受 model/effort 覆盖，故使用 `fork_turns: "none"`。提示词写模型名称不等于切换。每个任务都显式设置两个参数，包括后续新建的验收者；需要换模型时新建相应子智能体，不能假定 followup 能改变既有配置。

等待使用 `collaboration.wait_agent`，状态使用 `list_agents`，必要定向补查用 `send_message` 或 `followup_task`；按实际工具 schema 调用。当前最多同时 4 个智能体（含主会话），因此默认可同时 2—3 个审查者，4 个审查任务要分批。不要通过创建用户侧新任务替代本轮子智能体。

这些工具共享磁盘，`fork_turns: "none"` 只隔离对话上下文，并不强制只读。审查提示必须限制写入，副作用测试复制到隔离目录；需要强制只读保障时使用宿主实际支持的权限控制。不要给 spawn 臆造 `sandbox_mode` 参数。

## 每轮配置生效证据

1. 检查当前工具声明及可用模型目录；保存来源、时间、支持档位和实际参数名。
2. 保存结构化调用参数、工具返回的 agent ID/任务 ID、成功/失败结果。
3. 读取宿主返回的运行模型与档位，或该子任务可定位的运行事件/会话元数据。记录 `requested` 与 `effective` 分开列出。仅保存必要字段，不读取或传播凭据和其他任务内容。
4. 某些宿主的列表只显示名称和状态、不显示配置。可检查对应子任务的 `turn_context` 等可信运行记录；不能把子智能体自己的“我是 Astra”当作证据。工具若明确保证接受即采用指定配置，可记录该契约及成功返回，但仍应注明无独立 effective 回显。
5. 如果宿主既没有有效配置回显/运行元数据，也没有足够明确的采用参数契约，标为“配置生效无法验证”，停止依赖该配置的后续阶段。禁止声称完成指定多模型流程。

配置验证应复用实际审查任务的运行记录，不为每轮额外启动一群无目标探针。预检失败保留已完成证据，报告缺少什么；恢复后从受阻阶段继续，不能把此前未发生的步骤补写为通过。

## 其他 Codex 宿主的配置示例

当前官方说明支持 `.codex/agents/*.toml`（项目）或 `~/.codex/agents/*.toml`（个人）中的自定义 agent，字段为 `model`、`model_reasoning_effort`。见 [Astra 配置示例](../examples/astra-reviewer.toml)。这是另一种宿主适配示例，不是 `agents/openai.yaml` 内可设置的模型配置。复制前验证目标版本，不能覆盖全局父会话模型或所有子智能体默认值。

如果实际 spawn 工具接受角色名而不是本页的参数，读取该宿主的 schema、选择已验证自定义角色，并验证配置生效。不要把 desktop 的 `reasoning_effort`、TOML 的 `model_reasoning_effort`、API 的 `reasoning.effort` 混用。没有真实子智能体或 Astra xhigh 时没有“等价单模型模拟”模式。

## 来源

- [官方子智能体说明](https://learn.chatgpt.com/docs/agent-configuration/subagents)：配置字段、继承与自定义 agent。以实际宿主 schema 为调用依据。
- [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)、[GPT-5.6 Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra)、[GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol)、[GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)：模型 ID 和 API 推理支持；不证明账号调用成功。
- 本机 skill-creator 的 `references/openai_yaml.md` 与当前宿主工具声明：`allow_implicit_invocation: false` 保留显式入口。官方 skills 页面本次重定向到 [Build skills](https://learn.chatgpt.com/docs/build-skills)，抓取正文未找到该 policy 字段，因此不冒称已从该网页核实字段。
