# 审核记录：ISSUE-20 / r2

- 日期：2026-10-23 UTC。
- 任务：[Issue #20](https://github.com/mythpan1/pathwise-research/issues/20)；[PR #22](https://github.com/mythpan1/pathwise-research/pull/22)。
- 分支：`docs/search-first-workflow-20261023`。
- 被审基线 SHA：`f96057cacedd169c8ae6158aeb1386afdab40b30`。
- 被审成果 SHA（H）：`534da237bfa1150e48147e3593762d12a603e512`。
- 初审快照 H0：`0c51c3f07ea5f1cb6bd9bb67e33b024a0854cb8d`；H0→H 仅有下述纠正映射追加，已复核。
- 作者：`RUN-ISSUE20-20261023-SEARCH-FIRST-AUTHOR-01`；发布者：`RUN-ISSUE20-20261023-SEARCH-FIRST-PUBLISH-01`。运行及步骤引用为 H 中对应 `work/runs/` 与 `work/steps/` 文件。
- 审核者与独立运行：Dot（知舟）最终审核关口执行者，`REVIEW-ISSUE20-20261023-R2`，实际委派任务 `/root/review_mini_research_evidence`。
- 模型与强度：协调者确认原始启动请求为 `gpt-6-astra/xhigh`（2026-10-23 05:30:59 UTC），后续委派沿用同一运行；独立 runtime 报告及后端身份未暴露，reported/verification 保持 unknown。启动请求不是后端身份认证。
- 独立性：未参与本次被审文档、分析产物或发布内容的编写。本运行此前独立审查同一 mini/pro 受控材料，不是其分析作者；本次重新核对远端固定成果及新增差异。
- 实际材料：10 个变更文件、PR 的三个新提交及 H0→H 差异、现行规则与前轮归档、PR/Issue/CI 状态；此前已实际取得的 mini/pro 脱敏审核包及冻结 RFC 目标片段；另收到追加 sources 勘误全文。未取得全部未脱敏原始日志、提供商内部数据或账单。
- 签名审核：[PR 原评论](https://github.com/mythpan1/pathwise-research/pull/22#issuecomment-6358999705)。
- 结论：**建议采用**，仅覆盖 Search-first 流程及本次如实限定的有限负面结果归档，不表示 Research 内容质量通过。

## 实际检查及结果

1. **需求与范围。** 用户采用的 Search 找线索 → 保存并核对原文 → 另开 Astra 加工 → 知舟组织独立审核，已写入 AGENTS、主流程和 Tavily 协议。收集、分析、机械发布及最终审核继续分离。Research 仅在既有授权和预算内按缺口选用，不是事实证据或默认必经步骤；选用时仍配套 Search、原文逐项核对及差异处置。摘要、萃取、生成报告均不能替代原文，未解差异不采信。
2. **有限结果。** mini/pro 各一个样本，客户端记录分别为 Search/create/status/result=1/1/1/1 与 create/status/result=1/2/1；mini 原文读取3次，pro未新增原文/Search/Usage/重试。链路成功与内容验收分开。mini 把 HEAD 头字段 SHOULD 和 Content-Length MAY 条件强化为 MUST；pro 避免对应明确错答，却将关键规则标未核，仍缺请求 content 的语义、风险和条件。未核本身不是幻觉，也不能计为已答对。
3. **来源与归因。** 实际返回 mini sources=0，pro sources=3，后者仅含 url/title/favicon 元数据，并引用 rfcinfo，不能把“仅依据官方原文”的声明当作已满足。元数据不证明读到完整正文或三方核验，HTML/PDF同一规范不等于独立证据。没有把缺陷归因于未经核实的模型、wrapper 或提供商，也未据单样本判定全局优劣。
4. **实际证据访问。** 此前独立核对审核包101184字节/SHA256 `6ba193cda54870166cb96e22f14d2dcbe72313857dbed48bae6cb964b03fb2f2`、41/41清单项、复用mini文件、两份报告与结果字段一致，以及42个RFC目标工具标记行。可见两份非敏感创建参数中的input均621字节，SHA256为 `56f246adda8abd5c5f0cbb95181f1738f12ff1ec9463d11512e5f91809b2f749`；受控原始参数对象未随包提供，不冒称直接重算其原件。此次仓库索引的5份可用证据哈希与该包一致；另从授权Work回读勘误完整文本，重算为1318字节、SHA256 `b5dcd58eff434b931e64e67236ad1d87e3411dcab197540790eda74fe970aa8d`，与索引一致。哈希/指针不替代访问，包中没有全部原始collection文件。
5. **机械与隐私。** 10个文件内容重算Git blob一致，JSON/JSONL可解析，无尾随空格；新增相对引用目标及新主流程锚点可定位。当前差异和本PR首提交补丁未命中所检查的凭据、私钥、Bearer及机器绝对路径模式；正文手工检查未见原始参数、实际提交token、匿名槽位或完整内部日志。模式检查不是绝对无秘密保证。既有Search历史行未被本PR改写；本轮不重新验证旧修复源码、账单或其全部原件。
6. **修复差异。** H0→H只有 `work/steps/RUN-ISSUE20-20261023-SEARCH-FIRST-PUBLISH-01.jsonl` 追加一行，当前前三行逐字不变。PUBLISH-04-CORRECTION-MAP准确引用原提交 `2188c33f0646e045eda370fa534d013bd9c3a39c` 和直接改写提交H0，承认旧步骤ID含义被改写、9/9计数不实以及无依据的午夜起始时间；8作者文件＋2发布记录的10文件范围可核。未知起始时间保留null，记录时间不冒充启动时间。作者文档和证据结论未因此改变。
7. **检查。** 直接读取指定 `.github/workflows/validation.yml` [run 47](https://github.com/mythpan1/pathwise-research/actions/runs/39911195869)：head_sha=H，completed/success，validate成功；H0的run45也已核。此次没有重新运行本地单测、生产控制器、Search、Research、原文网络请求或其他研究。
8. **状态。** PR非Draft，ready标记与H一致，base未变；Issue #20仍open，PR正文仅Refs，无自动关闭指令。测试单元停止、研究和巡检仍暂停；采用流程不自动开启下一研究或例行重测。

## 问题与处置

| 编号 | 状态 | 事实、边界和处置 |
| --- | --- | --- |
| N1 | 已处置，历史偏差保留 | 发布记录曾直接改写完成行，违反严格追加方式；H新增映射明确承认该偏差并定位旧值，未把旧历史改称合规。当前审查不以无限日志修复扩大任务，不据最小摘要认证全部远端操作日志。 |
| N2 | 已核纠正 | pro metadata/handoff残留sources=[]解释不适用于pro。实际sources为3，追加勘误与证据相符；原件保持历史含义，仓库未冒称重建原包。 |
| N3 | 仅限本次采用 | 未见提供商内部检索、实际费用、runtime部署和后台身份；字段不透明不自动证明接口违约。Research内容未通过与本流程可采用分别记录。 |
| N4 | 已获具体授权后重试 | 第一次签名评论写回被自动审查拒绝；回读确认无评论，未绕过。用户于06:32:18 UTC明确同意PR22审核评论、归档及最终检查后条件合并后，仅原接口重试一次成功。本审核运行仍不执行合并。 |

未发现阻断本次有限采用的问题。未核事项不补写为通过；本归档不扩大资料上传权限，也不变更Issue状态。

## 版本关系与最终门禁

前轮为 [ISSUE-20-r1](ISSUE-20-r1.md)，覆盖PR21的旧流程与Search结果，不是mini/pro或本PR的批准。本轮覆盖随后新增的Search-first流程、有限测试结果及记录修复，且已绑定H。

本归档自身不属于H。仅追加本文件得到F后，协调者须核H→F只有此记录且内容忠实，并重新核F的指定CI、head/base、冲突及实际平台门禁；新head不继承旧head的CI。存在其他正文变化时复核其影响。签名评论不是GitHub APPROVE，不能替代平台要求的独立账户批准，不允许管理员绕过。最终核验和按精确SHA决定是否合并由协调者负责；本审核运行不合并、不关闭Issue。
