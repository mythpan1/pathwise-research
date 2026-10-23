# Issue #20：已有 Tavily 验收结果（2026-10-23）

**结论：特定可见私有插件 MCP 调用路径的一次 Search 修复验证成功；Research 仍未验收，Issue #20 保持 open。** 本文整理冻结材料，不新增 Search、Research、Exa、ACP、WorkBuddy、配置/额度查询或原文请求。最终独立审核尚待知舟组织；分析作者和发布者自检均不替代该审核。

## 已发生的时间线（UTC）

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

## 证据层级与未验收范围

实际工具入口为 `mcp__codex_apps__tavily_search`。当时可见工具描述同时保留“初版仅模拟测试”的旧措辞和 LIVE 描述；两次实际返回均报告 `mode=live`、`simulated=false`，据此记录回执所示状态，不把描述或成功响应当作提供商独立认证。runtime 插件版本、源提交和部署 ID 未暴露；`v4` 与修复部署信息均来自 operator。执行运行请求的模型/强度与实际报告分开，后者未暴露即为 null/unknown。

Research 的 create、status、result 均从未调用；未发送 Research POST，先前准备的提交 token 未使用，其值留在本机。未查 Usage/余额，失败未被改写成零执行或零费用，成功也不证明实际扣费金额。

已成功的同版本、同路径正常使用无需每次重新验收；出现新故障、版本/配置/路径变化或证据矛盾，再针对受影响部分复核。runtime 版本未知，不能认证具体部署。结论不外推至 500 个 key、所有参数或未来永久可用，不代替未完成的 Research 与原文核验。

## 留存与交接

[脱敏回执索引](../work/evidence/ISSUE20-TAVILY-20261023/receipt-index.json)给出最小调用参数、可见元数据、三条 URL、原件不透明 ID/SHA-256，以及结论到 JSON 字段的映射。完整响应、内部日志、提交 token 和匿名槽位只保留在受控本地；不上传凭据或机器绝对路径。远端读者可核对已发布摘录与哈希声明，但不能仅凭哈希读取或独立验证未上传原件；最终审核者如无法访问原件，须明示该盲区，不能声称读过全件。

[原计划](tavily-acceptance-plan.md)保留未完成目标；[使用协议](tavily-protocol.md)规定 Tavily 默认、Exa 备用，不每次双查。用户使用经验不转写成逐 key 测量。定时巡检已暂停；研究不因交接、审核或合并自动恢复。
