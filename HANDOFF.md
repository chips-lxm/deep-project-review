# 当前交接

更新于 2026-11-23（Asia/Shanghai），当前交付为 v0.4.0。

## 入口与现状

- 维护源为 `/Users/lxm/app1/github-preview/deep-project-review`，独立仓库和 `main` 分支。安装副本位于 `~/.codex/skills/deep-project-review`。需求依据见 [REQUIREMENTS.md](REQUIREMENTS.md)，使用入口见 [README.zh-CN.md](README.zh-CN.md)。
- 初审、修复和独立验收使用 GPT-6.2 Sol，固定复核和必要定向复核使用 GPT-6.2 Astra `xhigh`。继续要求明确启动、授权内修复、非修复者亲自验收和最多两轮修复—复验。结构检查的记录方式见 [证据检查](references/templates.md#结构化证据检查)。
- 本次更新说明见 [发布介绍](docs/launch-copy.md)，分发版本为 [GitHub v0.4.0](https://github.com/chips-lxm/deep-project-review/releases/tag/v0.4.0)。上版验证证据仍保留在 [2026-09-30 验证](tests/update-2026-09-30/VALIDATION.md)。安装中六份带本机证据的老测试文件保留原字节。

## 本轮验证

- 官方格式、配置与 50 个本地引用检查通过，快照测试 10/10、证据检查测试 13/13 通过。源包完成快照与回读，运行摘要为 `0f9de5b3e25347b057fe01df05fa5b6b41e37564de907997abf50a6d0f0ca8f5`。
- 在固定的合成发票基准上，两位独立 Sol 审查者先分别执行测试。旧 Astra 和 6.2 Astra 分别使用同一版原始要求、源文件和完整报告，以 `xhigh` 独立复核，归并到相同的四项缺陷，并分别区分币种分组与错误去重的影响。保存的基准源码哈希和两次复核的实际观察一致。
- Codex 本地 `turn_context` 确认两代 Astra 的模型与 `xhigh` 配置实际生效。Sol 修复四项缺陷后，未参与修复的审查者亲自执行原有 5 项测试和 17 项定向回归，全部通过。复验前后样例版本一致。证据检查器以该案例的实际记录通过 `review`、`repair` 和 `accept`。
- 这是一个隔离案例的同基准对照。未测真实项目的普遍覆盖率、端到端性能或不同客户端的表现。

## 检查点与接续

- 修改前仓库干净，恢复标签 `before-6-2-routing-2026-11-23` 指向 `b0e428bea03fc9a2d84043da15a925618787d508`。恢复前先保全当前和安装自定义内容，用指定标签导出到临时目录，比对并恢复相关文件。本地恢复标签已核实，未执行整套回滚演练。
- 后续改动先读取 [AGENTS.md](AGENTS.md)。有意改动运行文件后显式执行 `python3 -B scripts/freeze_run.py --seal`，再验证安装一致性；运行时继续使用固定快照。讨论、修改或安装本 Skill 本身仍只属于维护任务。
