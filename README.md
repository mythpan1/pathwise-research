# 知途研究 · Pathwise Research

**升学与职业发展研究 · Education & Career Pathways**

以数据与证据为基础，研究教育选择与职业发展的路径。

> 研究每一种选择，理解每一条路。

## 当前阶段

项目处于研究框架搭建阶段，由个人负责，Codex 与经 ACP 调用的外部 Agent 协助。
当前建立研究架构、任务与审核流程，尚未导入研究资料或实现应用功能。

**当前上传范围：通用骨架、本轮整理的研究架构提案、多 Agent 协作与审核约定，以及审核自动化代码与测试。** 现有“学业”仓库及其他本地知识库的资料不导入、不上传；后续通过研读逐步重建，每批内容另行确定范围。本轮提案先通过 Draft PR 提交，已授权范围内审核与检查通过后自动推进，异常才交项目负责人。

研究从中国的政策脉络、人口结构、产业基础及国际环境开始，追踪它们如何改变具体职业，再核对培养路径与个人条件。老龄化和少子化均须研究全社会的职业影响；个人兴趣在下游参与路径选择。

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
| [docs/agent-workflow.md](docs/agent-workflow.md) | Issue、分支、PR 与多 Agent 分工、交接 |
| [docs/review-automation.md](docs/review-automation.md) | 自动状态机、后台协调与平台限制 |
| [reviews/](reviews/README.md) | 独立审核、版本绑定、问题与复核记录 |
| [docs/roadmap.md](docs/roadmap.md) | 分阶段建设计划 |
| [research/](research/README.md) | 研究问题、任务和过程分析 |
| [sources/](sources/README.md) | 来源索引与证据摘录 |
| [data/](data/README.md) | 本地原始数据与整理结果 |
| [reports/](reports/README.md) | 经检查的研究报告和决策材料 |
| [templates/](templates/research-task.md) | 研究任务、来源记录和报告模板 |

## 开始第一项研究

1. 根据研究总图选定一个具体问题，明确地区、年份和适用对象。
2. 使用研究任务 Issue 模板分派任务；可先用[本地模板](templates/research-task.md)准备，Issue 建立后以其正文为准。
3. 用 [来源记录模板](templates/source-record.md) 登记证据，注明原文位置和适用范围。
4. 用 [研究报告模板](templates/research-report.md) 整理结论、限制和待核实事项。
5. 在独立分支提交 Draft PR，由未编写本次成果的 Agent 审核并记录到 `reviews/`，协调者按授权、版本与自动检查条件继续推进。

本阶段不需要安装依赖或启动服务。

## English overview

Pathwise Research is a private research workspace for education and career pathways.
It connects admissions, universities, academic programs, occupations, and individual
decision-making through traceable evidence. The initial repository contains only the
project scaffold, a proposed top-down research architecture, and a documented multi-agent
review workflow with a local controller and automated tests. Existing local research
collections have not been imported or uploaded.
