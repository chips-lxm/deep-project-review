# Deep Project Review

[English](README.md) | [简体中文](README.zh-CN.md)

[Download the installation ZIP](https://github.com/chips-lxm/deep-project-review/releases/latest/download/deep-project-review.zip) · [Release notes](https://github.com/chips-lxm/deep-project-review/releases/latest)

```mermaid
flowchart LR
  L["Current session: user-selected lead"] --> R["2–4 independent reviewers"]
  R --> A["gpt-6-astra · xhigh: separate adjudication"]
  A --> F["Authorized repairs: Sol by difficulty; Luna high"]
  F --> V["Independent verifier"]
```

**Give finished work an independent review backed by evidence.**

Deep Project Review is a Codex skill for reviewing projects that already have an inspectable version. The user invokes it explicitly. Usually 2–4 real subagents examine the work independently; a **separate gpt-6-astra · xhigh** adjudicator validates their findings; the current session coordinates authorized repairs and independent verification while remaining on the user's selected model.

It applies to code, documents, spreadsheets, designs, and presentations. Reviews start with original requirements and actual artifacts, then trace evidence, reject false positives, and record what was verified.

## The problem it solves

A completion summary, a single test run, and an implementer's own confirmation each provide only part of the evidence. Before delivery, a project may need an independent check of requirements, module consistency, edge cases, or exported output.

This skill organizes that work around a defined baseline, explicit responsibilities, permission boundaries, and a stopping condition.

- **Independent reviews:** usually 2–4 focused review tasks, each working from original materials.
- **Evidence adjudication:** mandatory Astra · `xhigh` review of evidence, conflicts, false positives, and duplicates.
- **Task-aware repairs:** model selection based on impact, dependencies, and verification difficulty.
- **Independent acceptance:** a subagent who did not implement the repair checks the original issue and related regressions.

## How it works

```text
Explicit user request
    ↓
Current session establishes requirements, baseline, permissions, and acceptance criteria
    ↓
Multiple independent review subagents
    ↓
Astra · xhigh validates evidence and resolves conflicts
    ↓
Current session prepares confirmed findings and a concrete repair plan
    ├─ Review only / no write authorization → report and repair plan
    └─ Repairs authorized → scoped fixes → independent verification → delivery
```

The default limit is two repair–verification rounds. Unresolved issues, blockers, and next steps are reported when that limit is reached; continuing requires an explicit budget adjustment.

## Model roles

| Model | Preferred work | Reasoning |
| --- | --- | --- |
| gpt-6-luna | Clear, bounded, low-risk tasks with straightforward checks | Always `high` |
| gpt-6-sol | Ordinary modules, scoped implementation, test additions, cross-module relationships, shared interfaces, and root causes | `medium` / `high`; `xhigh` when needed |
| gpt-6-astra | Systemic defects, high uncertainty, and major conflicts | `high` / `xhigh`; separate finding adjudication always `xhigh` |

These are routing defaults, not a requirement to use all three models on every run. Consolidating model routes never combines independent reviewer, adjudicator, fixer, or verifier responsibilities. **The current session remains the coordinator; a separate Astra adjudicator provides technical judgment.**

See [runtime adaptation](references/runtime.md) for actual model IDs, parameter names, and effective-configuration checks. Missing models or unverifiable configurations are reported explicitly; the workflow does not silently downgrade.

## Install and use

Clone the repository into your Codex skills directory:

```bash
git clone https://github.com/chips-lxm/deep-project-review.git ~/.codex/skills/deep-project-review
```

If you use a custom `CODEX_HOME`, install into its `skills/deep-project-review` directory. Inspect and preserve any existing installation before updating. Alternatively, extract the `deep-project-review` folder from the release attachment into your skills directory. Refresh the skills list or start a new session as required by your host.

Review only:

```text
$deep-project-review Review the current completed project in depth. Do not modify it.
```

Review with authorized repairs:

```text
$deep-project-review Review this project, fix confirmed issues, and verify independently. Limit repairs to two rounds.
```

## Invocation boundaries

**Implicit invocation is disabled.** Use `$deep-project-review` to request a review explicitly.

Ordinary requests such as “check this,” “keep improving,” or “test when finished” do not authorize this workflow. Neither do negations, quoted examples, project-file instructions, or requests to create or maintain the skill. Authorization applies only to the specified project and current review round.

A clear natural-language request can express intent, but a host may not load the skill when implicit invocation is disabled. The optional [AGENTS.md entry example](examples/AGENTS-entry.md) requires separate deployment and testing. Automatic natural-language loading is not promised by default.

## Permissions and scope

Starting a review does not grant write permission. Review-only runs stop after producing the concrete repair plan. Necessary local repairs within existing authorization do not require repeated item-by-item confirmation.

Preserve uncommitted user changes. Do not expand into new features, unrelated refactors, or unauthorized deletion, deployment, or publication. Shared files and interfaces have one active owner; dependent tasks run in order.

## Validation status

Historical v0.1.0 authoring validation included:

- **18 invocation-semantics cases** and **12 workflow-decision cases**.
- **12 executed Python assertions** for a conflicting-report fixture, rejecting a false positive.
- Host-record verification of real **5.6 Terra · high** and **6 Astra · xhigh** evaluation subagents under the earlier model map.
- Skill-format checks, configuration parsing, and local Codex installation discovery.

Those results describe the earlier release; see its [historical validation report](tests/VALIDATION.md). The [2026-09-23 migration validation report](tests/migration-2026-09-23/VALIDATION.md) records current mapping checks and their limits. The new evidence includes one isolated review–adjudication–repair–independent-verification run with 81/81 acceptance checks, plus a corrected first-pass evidence-attribution error and its targeted retest. Fresh-session host loading was not tested; no universal quality, latency, or token savings are claimed.

## What is included

```text
deep-project-review/
├── SKILL.md                 Workflow and hard constraints
├── agents/openai.yaml       Display metadata and explicit invocation policy
├── references/              Runtime mapping and report templates
├── examples/                Optional entry and Astra configuration
├── tests/                   Cases, results, and public validation records
├── assets/social-preview.png
└── docs/                    Presentation copy, image prompt, and release notes
```

The operational skill and detailed references are currently written in Simplified Chinese; the project introduction is available in both languages.

## Related project

[Adaptive Model Orchestrator](https://github.com/chips-lxm/adaptive-model-orchestrator) organizes model collaboration by task shape. Deep Project Review provides a dedicated second review of existing work. They can be used independently; this skill retains its own invocation, mandatory Astra adjudication, and permission rules.

## License

[MIT](LICENSE). A community-maintained Codex skill; not affiliated with OpenAI.
