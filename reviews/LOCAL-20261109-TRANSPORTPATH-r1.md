Independent review | head: 1ae8f5c37beb294fb0729f459fc6b98daf81b5e3 | reviewer run: TRANSPORTPATH-REVIEW-01 | verdict: 建议采用

## 版本、范围与独立性

- 日期：2026-11-09。任务：LOCAL-20261109-TRANSPORTPATH；PR #427。
- 被审基线 B：f7a9d78911994a9b8c3a8254724e1b314eedbdda。
- 被审成果 H：1ae8f5c37beb294fb0729f459fc6b98daf81b5e3。仅覆盖 research/industry/transport-network-2037-choices.md、research/industry/transport-network-2037-sources.json 及 research/admissions/major-career-routing.md 新增的一段导航。
- 作者：author_transport_pathway_comparison / TRANSPORTPATH-AUTHOR-01；收集：collect_transport_pathway_evidence / TRANSPORTPATH-COLLECT-01；机械发布：publisher_transport_pathway / TRANSPORTPATH-PUBLISH-01。本审核由新运行 review_transport_pathway_research / TRANSPORTPATH-REVIEW-01 完成，未参加收集、分析写作或发布，也未修改候选。实际分工和各阶段记录已核；独立性不以不同模型名称或共享 GitHub 账号证明。
- 本审核请求配置为 gpt-6-astra / ultra；运行方未暴露可核的模型及强度报告值，reported 均为 null、verification 为 unknown，不作后端身份认证。作者同样保留其请求值与报告未知的区别。
- 这是 COMMENT 形式的独立内容审核，绝非 GitHub APPROVE，也不是合并操作或平台批准替代物。

## 方法与实际检查

依据 B 的 AGENTS.md、docs/agent-workflow.md、docs/agent-provenance.md、docs/experiment-protocol.md、docs/research-methods.md、docs/research-architecture.md、docs/gaokao-planning-core.md、reviews/README.md 及本批范围审核。先核版本、授权范围和证据身份，再从原件检查会影响资格、方向和取舍的事实，最后检验事实—条件机制—培养—职业连接。没有要求每一条明示的未来推断均先逐环实证。

1. 自行读取 PR，确认 open、nonDraft、H/B 与交接标记一致。远端所有变更仅为上述三文件，547 行增加、0 行删除；导航只增一段及空行，未修改已有候选计数。
2. 重哈希作者冻结清单16件和来源冻结清单88件，零差异；远端三文件与冻结候选逐字节一致。远端 diff 与作者 FULL.diff 的差别仅为 Git blob index 和 hunk 后的上下文标题；分别在隔离目录实际应用，两者均精确重建相同三文件，不存在以格式差别掩盖内容变化。
3. 来源索引 JSON 合法，9条来源记录与原件 URL、SHA-256 全部对应；S01/S01B 合成一个招生证据单元，因此8个逻辑单元与9条记录不矛盾。正文9个来源引用可解析；81个相对链接均指向 H 的实际文件。新来源与原件指针、日期口径、页码/条款均复核。实际差异未包含原件全文、截图、私人资料、内部日志或本机路径。
4. 不只读作者或收集摘要：直接读 S01 原 JSON、S01B 原图及承载 HTML、S07–S10 原 HTML；亲看 S02 的 PDF 页1/9/10/11/12/15、S03 页1/10/12/15、S06 页1/2。另从冻结原 PDF 独立重渲染 S02 页11、S03 页15、S06 页2并看像素，复核表头、必选修、学时及学历列。
5. 指定 [.github/workflows/validation.yml run 42589762392](https://github.com/mythpan1/pathwise-research/actions/runs/42589762392) 的 head_sha 为 H，completed/success；validate 作业及 Test review state transitions 步骤均 success。另在隔离目录运行仓库单测9/9通过。CI 和单测不是事实或后端身份认证。

三文件 SHA-256：
- transport-network-2037-choices.md：4ec80da0f63d42e2c456e0d8392e81012b30f92b00f1d39c472c978cada3f050
- transport-network-2037-sources.json：3efaab854c0c66d08beacc02814507f19dd15369ed554d59ab0096aa408ea71e
- major-career-routing.md：3bf684d1c3434be736df3b429c16c1377cd4b4572b7d2207bfd4bcaa494c2c17

## 关键内容结果

**招生和训练。** S01 确为北交2025江苏普通物理本科交通运输类计划2、物化均选，数字组/专业代码为空。S01B 的八项含专业和方向，不能拆成两个平行志愿或已得目标专业；稿件未这样拆分，也未补成2027资格。全国结构图与江苏计划分别使用，分流和全组接受未知保留。两份同校2020方案支持道路规划/流理论/控制及综合设计、与城轨运行组织/列车车站设计的真实训练差别，也保留交叉选修；没有认证2027实得或教学质量。S02课程内实践0未误写成无实践，S03重复 P404209B 未累加。

**岗位和学历。** S06 同一信号优化本科岗明确同时接受交通工程、交通运输；相邻信号控制算法岗硕士门槛独立。S07 规划/模型岗硕士要求没有被通用“本科及以上”句降级。S08 的运输技术专业匹配只作有限支点，统一本科起未下放为每岗最终学历，未将交通工程补入明确清单；南京宣讲与广州为主、部分全国的工作地分开，原定截止已过也已说明。公司业务/地址、法规职责和历史校招没有拼成同一雇主的已证本科雇佣链。

**机制和选择。** 公共交通条例的票价、财政承受、成本和服务评价、运营协议支持“服务持续但新人招聘未必同幅稳定”的机制；城轨办法把客流、自动化、应急和服务标准接到配员，15小时线路运营未误作个人工时。道路治理通过真实委托、资金、验收和持续服务才成为可支付工作，没有借公交补贴条款证明道路信号采购。人口通过空间、时段、出行方式、支付、人员接续和竞争进入，未用总人口或当年出生变化乘岗位数。

由此形成的当前顺序成立且可反转：道路网络/信号治理目标下交通工程弱前置；明确城轨运营组织目标且当届训练及目标岗位专业、学历接收兑现时，交通运输（城轨）前置；同一信号优化本科岗先并列。强弱指判断依据及条件完整性，不是录用胜率。规划/模型/算法的硕士目标独列2034路径，时间和机会成本没有被抹去。2027选择、2031本科、可选2034硕士及2037发展区分清楚；大类分流风险可以先于专业的微弱顺序。上述增量不同于既有低空/自动驾驶、城市/GIS或通用改造运行专题。

## 问题、处置及未核事项

**阻断：无。** 在本次明确的条件研究范围内，未发现关键事实错误、逻辑失效、隐藏修改或足以误导当前专业比较的越界。无需为通过本轮审核修改候选；不把“未来尚未发生”单独判为证据不足。

**非阻断 N1：来源本身的局限保留。** 2020旧方案、S03重复行、S01B文章日期与信息公开索引日期不同、S07无明确日期、S08历史截止等均已正确标注。处置：保留现有边界，不把索引日期强行统一，不对重复课程累计，不以旧页保证当前开放；无本轮修订要求。

**非阻断 N2：实际应用前的再核条件。** 未核2027正式计划/组成员/分流及当届实践，2031/2034单岗最终专业学历、新人与熟手任务、地区/排班/合同/带教，目标地区预算合同与付款、人口空间变化及同市场供给，亦未核2037实际结果。处置：按稿件第8节的优先级在对应决策阶段核对；只调整依赖变化的路径，不据此把全部条件推演取消。本轮不是个人志愿表、学校排序或已认证的未来就业通道。

其他未核：固定来源包之外的更新与地方减员原文、国铁/民航具体入口、平台完整保护要求及最终合并门禁。未追加搜索，未重试已拒绝来源，未恢复暂停的数据采集或研究。平台保护未核不能被理解为“无保护”或“可直接合并”。

## 后续版本关系

建议采用只绑定 B→H 的三文件成果。后续如仅追加忠实审核记录，仍需由后续执行者核 H→最终 F 的全部差异，并对 F 重核指定检查、阻断、基线影响和平台要求；任何研究正文、来源或实质性导航变化均不继承本结论。本审核未归档、未合并、未继续新研究。


---

Archive source: faithful full-text copy of the independent review by TRANSPORTPATH-REVIEW-01, submitted on PR #427 at 2026-11-09T09:13:48Z, bound to H `1ae8f5c37beb294fb0729f459fc6b98daf81b5e3`. Original GitHub review: https://github.com/mythpan1/pathwise-research/pull/427#pullrequestreview-5823770630. The review body was read back from GitHub and matches the local report (SHA-256 `822ec30d22d74bec1091be24b8850bf4e04d2a427402e517ea0ce47e3482c854`). This appended source note is outside the verbatim report.
