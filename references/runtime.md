# 宿主与模型适配

## 当前路由映射

修订：2026-09-30；按每轮宿主能力核实。主会话保持用户选择，以下用于子任务。

| 用户称呼 | 实际 model ID | 本 Skill 使用的推理值 |
| --- | --- | --- |
| GPT-6 Luna | gpt-6-luna | 固定 high |
| GPT-6.1 Sol（默认实现、集成、审查与验收） | gpt-6.1-sol | high 起步；允许直接 xhigh / max |
| GPT-6 Sol（已有验证支持的适用路径） | gpt-6-sol | medium / high / xhigh |
| Astra | gpt-6-astra | high / xhigh |
| Astra·极高（固定复核） | gpt-6-astra | xhigh |

高 = `high`，极高 = `xhigh`，`max` 是独立档位。6.1 Sol 的困难核心任务可直接使用 max；不要把 Astra 固定复核的 xhigh 改成 max，也不从昵称推断模型。6.1 Sol 默认 high，不自动降到 medium 或更低。旧 6 Sol 不是必经中间层，替代路由须说明依据，不能静默回退。

当前 desktop 工具声明列出这四个 ID 及本表档位；API 支持不证明本轮调用成功。缓存可能滞后，缺项不能单独否决工具明确支持的合法调用；目录存在也不证明生效。结合工具契约、实际调用及可信运行证据分别记录 requested/effective。历史测试与缓存保留原日期，不改写成 6.1 Sol 已验证。

本轮新模型不可用时保留已完成证据并报告受影响阶段，不静默回退旧模型、降低强度或把其他配置写成指定配置。Astra xhigh 是必需阶段，不得由 Sol 替代。不要因缓存缺项先行阻止工具声明支持的合法调用，也不要因实际失败而无限重试。

## 固定本轮规则

在已授权的本轮证据目录或临时目录创建一次运行快照：

```sh
python3 scripts/freeze_run.py --output /绝对路径/本轮证据/skill-snapshot
```

脚本固定正文、参考、配置、脚本、示例、说明和素材，输出入口及内容摘要；Git、项目维护文档与历史测试不属于运行快照。输出目录不能在任何 Codex skills 安装目录中。每个分支、续答、补查、修复及复验均引用同一快照路径，保留到本轮结束；不能只记录旧摘要后继续读全局新文件。

使用 `python3 scripts/freeze_run.py --verify /绝对路径/skill-snapshot` 检查完整性。快照缺失或被改动时先恢复；确需换版本则显式记录新旧版本，核对受影响决定和证据，保持本轮授权及修复轮数。快照仅固定 Skill 规则，项目基准和环境仍单独记录，不能代替权限控制。

## 当前 desktop 原生调用

当前工具为 `collaboration.spawn_agent`，模型和推理参数必须放在结构化参数中：

```json
{
  "task_name": "review_core",
  "fork_turns": "none",
  "model": "gpt-6.1-sol",
  "reasoning_effort": "high",
  "message": "只审查本轮已授权基准的核心逻辑。读取本轮规则快照、原始要求及实际材料；不修改正式项目或读取其他首轮审查者报告；按快照内模板返回证据。派发前补齐真实快照路径、共同记录、范围和验收项。"
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

1. 检查当前工具声明及可取得的模型目录；保存来源、时间、支持档位和实际参数名。目录缓存与工具声明不一致时保留差异，不能仅凭缓存否决当前工具明确支持的配置。
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
- [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol)、[GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)、[GPT-6 Sol](https://developers.openai.com/api/docs/models/gpt-6-sol)、[GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)：模型 ID 和 API 推理支持；不证明账号调用成功。6.1 Sol high 起步、Luna 固定 high 是本 Skill 要求。接近 Astra 的定位不构成 max 与 Astra 全面等价的保证。
- 本机 skill-creator 的 `references/openai_yaml.md` 与当前宿主工具声明：`allow_implicit_invocation: false` 保留显式入口。官方 skills 页面本次重定向到 [Build skills](https://learn.chatgpt.com/docs/build-skills)，抓取正文未找到该 policy 字段，因此不冒称已从该网页核实字段。

运行快照须先匹配随包的 `runtime-manifest.json`，部分安装或清单缺失时失败并保留源文件。运行中不调用 `--seal` 掩盖不一致；该选项仅供维护者在有意修改后重建包清单。脚本拦截常见用户、仓库和插件缓存安装目录；调用方仍须避开宿主额外配置的发现目录。摘要用于内容一致性检查，不提供权限隔离或对抗性身份认证。
