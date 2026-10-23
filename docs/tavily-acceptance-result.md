# Issue #20：已有 Tavily 验收结果（2026-10-23）

**当前结论：Search 修复后的单次验证成功；mini/pro 各一次 Research 链路成功，但两份报告的内容质量均未通过。本单元测试已停止，有限负面结果已由知舟复核；Issue #20 保持 open。** 本次只整理冻结证据并修订流程，不新增业务调用或原文网络读取。本次新流程 PR 仍待知舟组织最终独立审核，作者与发布者自检不替代该审核。

## mini/pro 当前结果与终止边界

两次 Research 输入均为 621 UTF-8 字节，SHA-256 相同，仅请求的 `model` 与提交标记变化；原始受控参数不上传。两次各一个样本，内部检索过程不可见，不能据此推断全局质量、稳定优劣或差异根因。

| 维度 | 冻结证据支持的结果 |
| --- | --- |
| 调用链 | mini create/status/result＝1/1/1，另有 Search 1 次、原文读取 3 次；pro＝1/2/1，无新增 Search、原文读取、Usage 或重试。两次均取得成功回执及非空结果；pro 复用 mini 的 Search 与原文，不表示服务端内部检索次数为零。 |
| 原文与对照 | 官方 RFC 9110 目标章节的 42 个工具标记行（L1745–1765、L2000–2020）已实际取得并用于报告对照；是已返回片段，不是整份 RFC 字节原件。早期未取得目标正文的历史失败继续保留。 |
| mini 内容 | 将 HEAD 相同头字段的 SHOULD、Content-Length 可发送的 MAY 强化为 MUST，形成关键错答；请求 content 的语义、风险及条件缺失。 |
| pro 内容 | 避免了对应明确错答，但把关键规则改标“未核”，并未补齐答案；请求 content 的语义、风险及条件仍缺。未核本身不是幻觉，也不能计作回答正确。 |
| 来源字段 | mini `sources`＝0；pro 有 3 条 url/title/favicon 元数据，不是全部来源丢失。独立萃取仍不可见；pro 声称仅用官方来源，却引用 rfcinfo。来源元数据不证明实际取得正文或完整三方核验。 |
| 解释边界 | 这是两份报告的有限负面结果，不将缺陷归因于未核实的后台模型、wrapper 或提供商。运行时部署、实际后台模型与费用仍 unknown；成功回执不认证这些未知项。 |

具体主张定位、文件哈希与受控审核包指针见[mini/pro 结果索引](../work/evidence/ISSUE20-TAVILY-20261023/mini-pro-result-index.json)。pro 旧 metadata/handoff 中残留 `sources=[]` 的解释已另追加勘误，原件未覆盖；应以实际三条来源字段为准。

本轮知舟交接报告已完成独立研究审核，确认审核包 41/41 证据项、621 字节同输入哈希、报告与结果字段一致及 42 行原文齐全。**该状态来自知舟交接；正式 reviewer run、评论或审核归档定位未随交接提供，本文件不补造。** 这项结果复核与本次新流程 PR 的最终独立审核分别记录。

采用 Search 找线索 → 保存并核对原文 → 另开 Astra 加工 → 知舟组织独立审核；Research 仅作可选线索与补盲区工具，不作为事实证据或原文替代，未解差异不采信。本单元不继续测试，不例行重测；未来确有任务需要时仍可在既有授权和预算内选用 Research。新 PR 采用及负面结果归档后，由知舟确认是否收尾 Issue；本轮不自动关闭，其他研究和定时巡检继续暂停。

## 历史阶段：Search 失败与修复验证

以下保留 mini/pro 执行前的记录及当时未知；其中尚未调用 Research、未取得目标正文等描述仅适用于该历史阶段。

### Search 时间线（UTC）

| 时间 | 实际记录与边界（两次分别有界） |
| --- | --- |
| 2026-10-23 前序配置单读；精确调用时刻未留存 | 既有 setup 回执为 `isError=false`、`mode=live`、`simulated=false`，报告 live 已启用、配置和存储已绑定、适用提供商限制、凭据有效性 `not_probed`。这是配置状态回执，不证明每个 key 可用、余额或调用成功；本轮未重复 setup。 |
| 01:43:58 首次验收：1 次 Search 失败 | `basic`、`max_results=3`，问题为 RFC 9110 §9.3.1/§9.3.2 的 GET/HEAD 用途和响应内容区别。`trace_id=4cec8221-412d-483f-8d5a-901dcd1c6586`，`attempt=1`，`duration_ms=465`；外层 `isError=true` / `INVALID_ARGUMENT`，内层 `ok=false` / `transport_error`，无自动重试。HTTP 状态未暴露；提供商是否收到/执行及计费均 unknown。该失败原件保持不变。 |
| 01:44:22–01:44:27 两次 RFC 原文尝试 | 文本请求 DNS 失败；第二次仅取得文档开头及目录，未取得目标章节正文。故未完成原文对照，也未形成经验证的 RFC 结论。此处仅复核既有回执，未补读原文。 |
| 01:53:40 母任务报告修复部署成功 | 母任务报告源提交 `626dffeb944fd295856154e075c94b0a5f6b601d`、部署 `appgdep_6adabe1a479c8191ab9079f202f040fb`、环境 `revision4` 不变；报告 Cloudflare 不支持 `redirect:error`，改为 `manual` 并拒绝 3xx，40 项 Node 与 1 项 workerd 离线测试通过。**均为 operator 提供的信息**：本轮未读源码、未重跑测试，未独立证实根因或运行时部署身份。 |
| 01:56:26 另行授权修复验证：1 次 Search 成功 | 实际 query 为 `Tavily Search API official documentation`，`search_depth=basic`、`max_results=3`。`trace_id=109b093c-b13f-4764-93a1-d4641bf90fc8`，`attempt=1`，`duration_ms=2678`；外层 `isError=false`，内层 `mode=live`、`simulated=false`、`ok=true`，返回三个 URL，外层及内嵌 JSON 可解析。未读取 URL 内容，未验证研究结论、排名或广告。HTTP 状态与收费仍 unknown。 |

成功响应实际 URL 字段为：

- <https://github.com/tavily-ai>
- <https://docs.tavily.com/documentation/api-reference/introduction>
- <https://docs.tavily.com>

两次调用各属独立有界执行，未静默扩充首次预算；query 不同，不构成同题质量或根因对照。以上 URL 未打开；耗时为回执值，观察时间不是精确发送时间。

### Search 历史证据层级与当时未验收范围

实际工具入口为 `mcp__codex_apps__tavily_search`。当时可见工具描述同时保留“初版仅模拟测试”的旧措辞和 LIVE 描述；两次实际返回均报告 `mode=live`、`simulated=false`，据此记录回执所示状态，不把描述或成功响应当作提供商独立认证。runtime 插件版本、源提交和部署 ID 未暴露；`v4` 与修复部署信息均来自 operator。执行运行请求的模型/强度与实际报告分开，后者未暴露即为 null/unknown。

截至上述 Search 修复验证阶段，Research 的 create、status、result 均未调用；未发送 Research POST，先前准备的提交 token 未使用，其值留在本机。未查 Usage/余额，失败未被改写成零执行或零费用，成功也不证明实际扣费金额。

已成功的同版本、同路径正常使用无需每次重新验收；出现新故障、版本/配置/路径变化或证据矛盾，再针对受影响部分复核。runtime 版本未知，不能认证具体部署。结论不外推至 500 个 key、所有参数或未来永久可用，不代替未完成的 Research 与原文核验。

### 历史材料留存与交接

[脱敏回执索引](../work/evidence/ISSUE20-TAVILY-20261023/receipt-index.json)给出最小调用参数、可见元数据、三条 URL、原件不透明 ID/SHA-256，以及结论到 JSON 字段的映射。完整响应、内部日志、提交 token 和匿名槽位只保留在受控本地；不上传凭据或机器绝对路径。远端读者可核对已发布摘录与哈希声明，但不能仅凭哈希读取或独立验证未上传原件；最终审核者如无法访问原件，须明示该盲区，不能声称读过全件。

[原计划](tavily-acceptance-plan.md)保留历史目标，mini/pro 的当前状态以上文为准；[使用协议](tavily-protocol.md)规定 Tavily 默认、Exa 备用，不每次双查。用户使用经验不转写成逐 key 测量。定时巡检已暂停；研究不因交接、审核或合并自动恢复。
