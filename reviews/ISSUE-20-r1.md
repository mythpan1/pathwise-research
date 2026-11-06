# 审核记录：ISSUE-20 / r1

- 日期：2026-10-23 UTC。
- 任务：[Issue #20](https://github.com/mythpan1/pathwise-research/issues/20)；[PR #21](https://github.com/mythpan1/pathwise-research/pull/21)。
- 被审基线 SHA：`524f664d2445987eaba36ab1a2ed6aad8c5bdd20`。
- 被审成果 SHA（H）：`6c5fed545ec54b4119f77587da293c5724e77d3c`。
- 首次完整审查快照 H0：`96151251bbd330abf4e6f8f610e97450f5c1d687`；H0→H 的唯一追加提交已单独复核。
- 审核运行：`REVIEW-ISSUE20-20261023-R1`，Dot（知舟）最终审核关口的独立 Astra 执行者，不是第二道批准。协调者报告请求配置为 `gpt-6-astra/xhigh`；未暴露单独运行时/后端身份报告，reported 保持 unknown，不写成 ultra 或已认证。
- 独立性：审核者未参与被审成果编写、证据分析产出、包装或发布；此前预审意见不算正式批准，本次重新绑定远端 H。
- 作者与步骤范围：H 中 `work/runs/`、`work/steps/` 的 workflow-author、collector、Search-fix-check、closeout-analysis 及各 publisher 选择性记录；归属、未知元数据和后继纠正按原记录保留。
- 实际材料：全部 22 个变更文件、H0 的 18 个提交补丁及最后一条记录修复提交，固定版本规则/测试、PR/Issue/CI 状态，以及三个受控字段脱敏完整 JSON 副本和映射 manifest。未取得全部未脱敏原件或账单。
- 签名审核：[PR 原评论](https://github.com/mythpan1/pathwise-research/pull/21#issuecomment-6356781991)。
- 结论：**建议采用**，仅覆盖流程与如实限定的已有 Search 结果记录。

## 实际检查及结果

1. **需求与范围：**Chat Work/Sol high 调度与收集、收集后另开 Astra ultra 分析、Luna high 机械发布、单一 Dot 独立 Astra 最终审核关口均符合要求。不能自审或静默替代模型，阶段切换不重置预算、不自动重启研究。证据原件/位置/版本、脱敏调用及错误、结论映射、反例和历史留存要求完整。
2. **暂停与工具策略：**当前文档明确巡检暂停、研究仍暂停，不将 Work 完成通知等同于定时扫描。暂停回执来自协调者，不冒充本审核重新查询自动化。Tavily 默认、Exa 备用，不例行双查/逐 key 或额外余额探测；用户经验没有冒充逐 key 测量，旧 DSH 适用守门未被取消。
3. **证据核对：**独立解析 E-FAIL-01、E-SUCCESS-01、E-SEARCH-FIX-RESULT 的字段脱敏完整副本；副本长度/哈希与 manifest 相符，原件哈希映射与仓库索引一致，嵌套 JSON 的参数、trace、结果、错误、耗时及三个实际 URL 字段与发布索引一致。两个 query 不同，未用作同题质量/根因对照；未读取结果 URL 内容。原件哈希为提供方声明，未由本审核重算，副本不是后端或提供商独立认证。
4. **版本与修复：**H0→H 仅 `work/steps/RUN-ISSUE20-20261023-PUBLISH-04.jsonl` 增加一条既有完成记录。旧 3,896 字节前缀不变，新文件 5,787 字节/4 行有效 JSON。追加行绑定 H0 和原 action，描述当时 Draft/待归档状态，未冒称当前状态；本审核直接读回 H、非 Draft、匹配的 ready 标记和未变 base。正文与证据未改。
5. **机械检查：**当前变更文件 JSON/JSONL 均可解析，相对链接目标存在、无尾随空白、所检查敏感模式未命中当前文件；分析作者八项最终输出哈希与 H0 一致且 H 未改变它们。旧 resume 前六行字段缺项有明确后继纠正，未宣称全部历史记录符合 schema。
6. **测试：**本审核在独立固定快照运行 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`，9/9 通过；未运行生产控制器。直接读取 [validation.yml run 39](https://github.com/mythpan1/pathwise-research/actions/runs/39892603131) 验证 H0，修复后再读 [run 40](https://github.com/mythpan1/pathwise-research/actions/runs/39895215977)，指定 workflow 与 H 匹配且 success。CI 不代替证据或身份核验。

### 受控副本的审核定位

原件继续留在受控位置，映射见 H 的 `work/evidence/ISSUE20-TAVILY-20261023/receipt-index.json` 与受控 manifest。以下仅为本审核重算的副本哈希，不上传受控包：

| 证据 ID | 脱敏副本 SHA-256 |
| --- | --- |
| E-FAIL-01 | `6c2b2b57d4041fe3a2dc6d83eecc72b2b6450827600febad0b176010129c5362` |
| E-SUCCESS-01 | `8169d8042605370e58550a087bf2e1546de0c800b4c78c2288203130f44272ef` |
| E-SEARCH-FIX-RESULT | `da673404aef7d488ad16163928d43966a52d9bb472521c275e31baf34b40c9d6` |

副本删去匿名槽位、公开摘录中的邮箱/示例身份字段；嵌套 JSON 重序列化也改变哈希。副本内原有脱敏注释和原件哈希仍描述原记录，以 manifest 映射为准。

## 问题与处置

| 编号 | 状态 | 事实与处置 |
| --- | --- | --- |
| N1 | 已解决；失败历史保留 | PUBLISH-04 完成行曾因截断载荷未上传，现已追加。协调者说明新完整载荷经同接口校验后写入；本审核直接确认远端唯一增量、内容与状态，不冒充重读全部拒绝回执。较早 blob 创建结果仍 unknown、可能为未引用对象，不称未执行；当前树没有该不明载荷替换。无需无限为日志上传继续追加完成日志。 |
| N2 | 非阻断，已显式纠正 | 历史模型/角色/parent、时间和字段缺项，以及首次 Search 缺同 action 开始行已披露并有后继纠正/受控开始回执定位。保留旧记录，不倒填时刻，不把 self-check 当独立审核。 |
| N3 | 非阻断，已披露 | 历史提交曾含通用云工作区绝对路径，当前树已移除。已审历史补丁中该路径不含凭据或个人主目录；不进行历史重写，模式检查不是绝对无秘密的保证。 |
| N4 | 限制本次结论 | Research create/status/result、目标 RFC 原文对照未完成。结果/计划/PR 一致保留未完成，PR 无自动关闭关键字，Issue #20 保持开放。不得称全部验收或以合并恢复研究。 |

未发现阻断本次有限采用的问题。未核收费、全部 key/参数、后端部署身份、未来可用性；修复代码/测试/部署仅按 operator 报告层级记载。本审核没有新增 Search、Research、Exa、余额、ACP 或原文请求。

## 平台与精确版本合并边界

本次只读 GitHub 返回仓库 private，main 的 `protected=false`、`protection.enabled=false`，base 未变。但详细 branch-protection 接口返回 integration 访问限制 403；rulesets 接口返回计划功能限制 403；有效分支规则 URL 被连接器列为不支持。未绕过这些限制，不将不可读的详细规则写成已核通过。合并者必须据实际可取得的平台状态判断，不能以管理员权限绕过。

签名评论不是 GitHub APPROVE，不替代平台要求的独立账户批准。本归档自身不属于 H。仅追加本记录得到 F 后，合并者须确认 H→F 仅有本记录、内容忠实，核对 F 的指定 CI、head/base、冲突及实际平台门禁并留下绑定 F 的最终核验，再以预期完整 SHA 决定合并。任何其他内容变更须复核。本审核运行不执行合并。
