> Public distribution copy: local machine paths and session identifiers are redacted. Original records remain local. Test outcomes and limitations are unchanged.

# 制作验证报告

日期：2026-09-12。范围仅限本 Skill、包内合成案例及隔离临时目录；未复审或修改任何其他项目。这里的“通过”逐项限定测试层级，不表示完整复审流程已端到端运行。

## 已实际完成

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| skill-creator 原版 quick_validate.py | 通过 | frontmatter、命名、正文未完成占位符检查；最终命令输出 `Skill is valid!` |
| YAML/TOML 真实解析 | 通过 | `policy.allow_implicit_invocation` 为布尔 false；中文名、描述长度、默认显式 prompt；Astra TOML 为 gpt-6-astra / xhigh / read-only |
| 四模型 ID/档位目录核对 | 通过（目录声明层） | [model-catalog-evidence.json](model-catalog-evidence.json)，本机 CLI 0.154.0 对应缓存；不等于逐一发起推理成功 |
| 两个真实独立测试子智能体 | 通过 | [runtime-evidence.json](runtime-evidence.json)：本轮父 ID 关联的宿主线程记录及 turn_context 确认 Terra high、Astra xhigh；不使用模型自述 |
| 16 个首轮触发案例 + 2 个补测 | 18/18 决策符合要求 | [trigger-results.md](trigger-results.md)：覆盖显式、已配置自然语言语义、未部署入口、普通检查、否定、引用、文件/其他智能体指令、制作维护、跨项目授权与项目歧义 |
| 12 个异常/调度案例 | 12/12 决策符合要求 | [workflow-results.md](workflow-results.md)：冲突、误报、无问题、模型不可用、配置不明、测试失败、修改冲突、只审查、预算、基准漂移、分级模型与独立验收 |
| W01 的实际证据追溯 | 12/12 断言通过，退出码 0，排除误报 | [w01/execution.json](w01/execution.json)、[w01/stdout.json](w01/stdout.json)、[w01/verify.py](w01/verify.py)，保留临时目录原始输出副本 |
| 本机 Codex 实际发现安装包 | 通过 | [discovery-evidence.json](discovery-evidence.json)：临时 `.agents/skills` 中发现唯一启用的 Skill，中文名及 prompt 正确、无加载错误；未发起模型回合 |
| 个人目录安装及发现 | 通过 | 已安装至 `<local-path-redacted>`，未覆盖现有 Skill；[installed-discovery-evidence.json](installed-discovery-evidence.json) 确认实际宿主发现唯一启用的 user scope Skill |

运行模型证据：触发测试任务 `<session-id-redacted>` → `gpt-5.6-terra/high`；流程测试任务 `<session-id-redacted>` → `gpt-6-astra/xhigh`。均使用真实 `collaboration.spawn_agent`，`fork_turns: none`，结构化 model 与 reasoning_effort；独立输入未包含预期答案或他人报告。补测复用原 Terra 测试者。

首轮发现项目指代歧义用例不足，已在授权门补明“多个项目先明确范围”，新增 T17/T18 并定向复测。Astra 对 W05 未给修改前对照、W10 未给入口部署证据作出条件判断；已在测试验收说明中接受这些证据限制，未把缺失前提编造为事实。

## 明确未验证的层级

- **新会话 `$deep-project-review` 的宿主实际注入/进入工作流：未端到端运行。** 已验证包被真实宿主发现、配置格式及 18 个语义决策，不能用这些替代实际 turn 触发。默认显式入口依据本机 skill-creator 的宿主契约。
- **纯自然语言自动加载：未部署、未端到端运行，不承诺支持。** 提供可选 AGENTS.md 手动读取入口，T02/T03 只验证“入口已加载”条件下的行为；默认引导使用 `$deep-project-review`。没有重新开启隐式调用。
- **完整多审查者 → Astra → 实际修复 → 独立验收：未运行。** 本次测试针对 Skill 制作，没有启动另一项目的复审；12 个流程案例中的 W02—W12 是合成决策，不是真实错误注入或真实修复。
- **Luna/Sol 推理调用：未单独发起。** 模型 ID 与支持档位已核对当前工具 schema、目录和官方资料；实际调用验证覆盖 Terra high 与 Astra xhigh。
- **隐式排除的宿主运行效果：未端到端验证。** `skills/list` 回显不含 policy 字段，只能验证发现和界面元数据；不能声称该接口回显验证了 implicit=false 的运行效果。
- **可选 Astra 自定义 TOML 角色：配置已解析，未安装/执行。** 本次实际调用走 desktop 原生 spawn 参数，未修改父会话或全局模型默认配置。

## 环境与可重现性

初次 quick_validate 执行因本机 Python 缺少 PyYAML 失败；随后将 PyYAML 6.0.3 安装到临时目录后原版验证器通过，没有修改系统 Python。初次本机服务发现探针在沙箱内超时，获准访问本机服务后重试通过。没有把失败尝试写成通过。

使用已安装 PyYAML 的 Python 执行 skill-creator 验证器；将脚本路径替换为本机实际路径：

```sh
python /path/to/skill-creator/scripts/quick_validate.py /path/to/deep-project-review
```

本报告、完整案例、评估结果、精简宿主证据及 W01 源码/日志随包交付；临时环境路径不是将来运行 Skill 的依赖。目标宿主下次执行仍需重新核实本轮配置和权限，不能将此报告当作永久可用性证明。
