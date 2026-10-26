# 知途研究 · Pathwise Research

## 当前建设入口（2026-10-26）
三条主线不变：政策、产业变迁、人口结构变化。方法试水用于检验可行性，本次进入[完整研究框架](docs/research-framework.md)设计与文档衔接，不以小范围试用稿作为最终项目框架。完整设计不等于全行业内容已填充或预测已验证。
依次阅读[完整框架](docs/research-framework.md)、[研究总图](docs/research-architecture.md)、[研究覆盖与推进](research/coverage.md)和[建设计划](docs/roadmap.md)。本次依据见[方向决定](docs/decisions/2026-10-26-complete-research-framework.md)。
下方旧阶段状态按其日期理解；当前任务与采用状态由对应 Issue、PR、reviews 维护，旧暂停或旧人工唤醒叙述不覆盖后续授权。常规执行沿用三个职责会话及[唯一主流程](docs/agent-workflow.md)。不因此恢复巡检、工具重测或导入本地知识库。


**升学与职业发展研究 · Education & Career Pathways**

以数据与证据为基础，研究教育选择与职业发展的路径。

> 研究每一种选择，理解每一条路。

## 当前有效入口（2026-10-25）

核心目的：支持中国未来十年的学业、职业选择及当前高考志愿和培养路径比较。三条主线为 **政策、产业变迁、人口结构变化**；国际环境只在影响具体机制时作为背景，不单列主线。产业变迁须连续研究技术工艺、产品需求、生产组织、上下游关系和能力迁移，不能只充当其他专题的下游汇总。

见[当前主线决定](docs/decisions/2026-10-25-three-research-lines.md)、[研究总图](docs/research-architecture.md)和[已采用／候选研究导航](research/README.md)。本次由知舟亲自分层梳理和修订，不派子智能体；作者自检不等于独立审核。视频13—15、旧候选 PR、实验和巡检不自动恢复。

下方阶段及人工唤醒／四小时巡检叙述保留为较早记录，不是当前调度状态；当前常规协作约束见 AGENTS 与主流程，四小时巡检仍暂停。

## 初始阶段记录（历史）

项目处于学习型研究与流程试验阶段：同时检验思维实验方法和 Chat—执行者—Dot 的协作方式，项目骨架尚在演进，不急于搭建完整生产系统。
已有 EXP-001 / G01 脱敏证据成果进入仓库；这不等于完成研究验证或获得新的资料上传授权。当前研究仍暂停，本轮只完善流程。

**每批上传范围单独受用户授权约束。** 现有“学业”仓库及其他本地知识库的资料不导入、不上传；后续通过研读逐步重建。先读[学习型研究协作闭环](docs/agent-workflow.md)：Chat 每次派发一个有界单元，执行者提交 PR 并显式交接，Dot 审核固定 SHA，用户手动唤醒 Chat 读取返工意见。通过不等于自动启动下一轮。当前每4小时巡检仅只读报告，不写 GitHub、不触发 Chat；新审核/条件合并授权没有自动接入该巡检。

当前研究从政策、产业变迁、人口结构变化三条主线追踪具体职业影响，再核对培养路径与个人条件；国际环境仅作相关背景。老龄化和少子化均须研究全社会的职业影响；个人兴趣在下游参与路径选择。

## 研究方向

| 方向 | 关注的问题 |
| --- | --- |
| 历史与结构变化 | 政策如何形成、实施与调整？人口、国内产业和国际条件怎样共同影响职业？ |
| 升学与招生 | 选科、招生计划、录取数据和填报规则如何影响选择？ |
| 院校与专业 | 专业学习内容、培养方式、转专业和升学路径有什么差异？ |
| 行业与职业 | 岗位做什么、需要哪些能力、有哪些进入和发展路径？ |
| 个人决策 | 如何结合兴趣、能力、家庭条件和风险偏好比较方案？ |

## 目录

| 目录或文件 | 用途 |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Codex 和外部 Agent 的协作规则 |
| [docs/research-framework.md](docs/research-framework.md) | 研究范围、证据要求和工作流程 |
| [docs/research-architecture.md](docs/research-architecture.md) | 自上而下的研究总图及人口—政策—职业连接 |
| [docs/research-methods.md](docs/research-methods.md) | 复杂系统文献与思维实验、定向求证和修订方法 |
| [docs/tavily-protocol.md](docs/tavily-protocol.md) | Research/Search/原文配套核验、wrapper入口与额度错误边界 |
| [docs/experiment-protocol.md](docs/experiment-protocol.md) | 实验项目、回合、分支、规则版本与回放约束 |
| [docs/agent-provenance.md](docs/agent-provenance.md) | Codex、Chat/RDC及外部Agent的身份、模型、思考强度与步骤归属 |
| [docs/agent-workflow.md](docs/agent-workflow.md) | 当前唯一主流程：单元派发、显式交接、审核、返工及合并 |
| [docs/review-automation.md](docs/review-automation.md) | 既有本地控制器、历史运行边界与平台限制 |
| [reviews/](reviews/README.md) | 独立审核、版本绑定、问题与复核记录 |
| [docs/roadmap.md](docs/roadmap.md) | 分阶段建设计划 |
| [research/](research/README.md) | 研究问题、任务和过程分析 |
| [sources/](sources/README.md) | 来源索引与证据摘录 |
| [data/](data/README.md) | 本地原始数据与整理结果 |
| [reports/](reports/README.md) | 经检查的研究报告和决策材料 |
| [templates/](templates/research-task.md) | 研究任务、来源记录和报告模板 |

## 获准恢复后，开始一个研究单元

1. 根据研究总图选定一个具体问题，明确地区、年份和适用对象。
2. 使用研究任务 Issue 模板分派任务；可先用[本地模板](templates/research-task.md)准备，Issue 建立后以其正文为准。
3. 用 [来源记录模板](templates/source-record.md) 登记证据，注明原文位置和适用范围。
4. 用 [研究报告模板](templates/research-report.md) 整理结论、限制和待核实事项。
5. 在独立分支提交 Draft PR，自检后按[主流程](docs/agent-workflow.md)退出 Draft，并在 PR 正文写明 `ready for independent review`、完整 head SHA、实际交接运行及独立审核角色。不同于作者的实际运行审核，Chat Work 调度器读回、跟进同 PR 返工及归档；只有精确版本、授权、指定检查和平台门禁全部满足才可合并。实际通知能力未知时如实说明并人工补位，不把旧的用户手动唤醒安排作为唯一现行路径。

本阶段不需要安装依赖或启动服务。

## English overview

Pathwise Research is a private research workspace for education and career pathways.
It connects admissions, universities, academic programs, occupations, and individual
decision-making through traceable evidence. The project is a learning-stage experiment in research methods and collaboration,
not a finished production architecture. It now includes scoped EXP-001/G01 evidence,
a developing scaffold, and a local review controller with tests. Existing local research
collections are not authorized for import. Research remains paused; the canonical
[workflow](docs/agent-workflow.md) requires explicit handoff and manual Chat wake-up.
The current four-hour monitor is read-only and does not write to GitHub or trigger Chat.

