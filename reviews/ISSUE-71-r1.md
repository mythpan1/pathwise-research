# Issue #71 设计独立审核归档

本文件由知舟忠实归档审核者实际评论，不是作者自审。原评论：https://github.com/mythpan1/pathwise-research/pull/72#issuecomment-6393864668

被审内容 H：ddbd4f316d0450bdf54d6e8701d41876913d3a9a。归档只新增本文件，不改变提案；审核仅认可设计，未验证运行、不授权部署或自动合并。下文原文保留非阻断建议及实施前验收条件。

---

## 独立设计审核：建议采用（仅设计，不可据此立即实施）

Independent review | head: ddbd4f316d0450bdf54d6e8701d41876913d3a9a | reviewer run: /root/review_handoff_gate_design | verdict: 建议采用

- **基线：** `9a3978308d0059b3ff56a20138c0a57848c65bb5`
- **被审成果 H：** `ddbd4f316d0450bdf54d6e8701d41876913d3a9a`
- **范围：** [设计稿全文 1–150 行](https://github.com/mythpan1/pathwise-research/blob/ddbd4f316d0450bdf54d6e8701d41876913d3a9a/docs/proposals/2026-10-25-versioned-handoff-gates.md)；只评审协议、安全边界和有限任务适用性，不审核现实研究结论。
- **独立性：** 作者为知舟母会话；我在成果冻结后进入独立子运行，未参与撰写、未修改稿件、未另派子智能体。启动方确认请求为 `gpt-6-astra / ultra`、`fork_turns=none`；这是请求记录，不是提供商后端身份认证。本评论是实际独立运行的审核留痕，不是不同 GitHub 账户的 APPROVE，不能替代平台要求的独立账户批准。

### 结论与阻断

**设计评审可采用；阻断项 B：0。** 可以将其作为后续分阶段、另行授权实施的设计依据，不等于批准启动器、采用器、自动化或服务端保护上线，也不等于本 PR 已合并。

理由：
1. §3–4 把“冻结任务规定应交集合”“实际 manifest”和不可由执行者改写的外部锚点分开，能在信任前提成立时发现规定产物缺失及文件与清单一同替换；没有把哈希当来源真实性、发送前无遗漏或完整理解的证明。
2. §4.2、§5 正确区分原始字节、派生物、片段、受控原件和内容判断。允许明示条件推演及有限验收，不要求为了过关重做搜索。
3. §6–8 正面处理 H/F 全尾部归档、base 影响、expected-head 的能力边界、未知合并结果、导航补偿、过期回执和失效租约；§7 也没有将提示约束、不同 run_id、红叉 CI 或共享账户评论包装成技术强制。
4. 六类逻辑记录可合并承载、仅一道独立内容审核、无须逐阶段合并；§10 先离线验证再影子运行的顺序合理。不要反过来把完整调度/身份平台建好当成一切有限研究的先决条件；未具备强保证时应准确声明 L0/受控入口级边界。

### 非阻断建议及后续实施验收要求

以下是把稿件已有不变量落到具体实现时必须细化的合同，不要求本设计 PR 直接实现或预填通过。

**N1｜全集与跨记录绑定要可判定。** §3、§4.1 [L33–60](https://github.com/mythpan1/pathwise-research/blob/ddbd4f316d0450bdf54d6e8701d41876913d3a9a/docs/proposals/2026-10-25-versioned-handoff-gates.md#L33-L60)：“任务书规定‘应交什么’”“绑定 C1、清单路径和清单 sha256”。
后续 schema 应明确共同绑定 `task_id + task_revision + charter/rule_version + stage + manifest_digest`，并在 receipt/review 中绑定实际接收者、审核者和来源记录；旧材料可以复用，但复用必须在当前任务中被明确引用，不能重放旧任务回执来满足新 revision。必需 artifact 集合应由冻结任务确定或由其确定性规则产生，不能由发送者当场重新定义；额外产物检查须限定已授权交付根/提交树，而非声称检查了整个环境。明确条目的“源 commit”与外层 C1 的区别，避免新产物又要求在清单中写入包含清单自身的 commit。验收增加“缺文件同时删清单项”“跨任务/旧 revision 回执重放”“多个清单合并漏掉一个来源”。

**N2｜完整字节校验与实际内容阅读分别记。** §4.1、§4.2、G1 [L55–78](https://github.com/mythpan1/pathwise-research/blob/ddbd4f316d0450bdf54d6e8701d41876913d3a9a/docs/proposals/2026-10-25-versioned-handoff-gates.md#L55-L78)：“按任务需要实际取回”“接收者重算”“limited_receipt”。
实现时至少分开记录：接收端对哪些完整原始字节独立重算成功；分析/审核实际读取了哪些文件、页段或块；哪些主张仍依赖未读/不可访问原件。可以流式校验完整文件而只将必要段落送进模型，不能把完整 checksum 等同全部内容已审；反之，只读首块不能凭发送方提供的全文件 hash 签完整接收。接口仅返回解析文本/片段时，不得重编码该文本后声称验过原件字节。增加“大文件仅首块可读但全 hash 已给出”的验收例，并按原批准范围决定 limited_receipt 是否足够，而不是自动放行或无差别阻断。

**N3｜真实审核及 H→F/base 的“无影响”判断不能退化成自证。** §6–7 [L90–107](https://github.com/mythpan1/pathwise-research/blob/ddbd4f316d0450bdf54d6e8701d41876913d3a9a/docs/proposals/2026-10-25-versioned-handoff-gates.md#L90-L107)：“验证评论/回执来源及归档内容”“协调者必须从实际已授权审核会话/身份或受信服务回执核对”。
后续选定的信任宿主须证明执行者不能修改锚点/审核回执，单纯“放在仓库外”但仍由同一可写系统账号控制不够。归档应保存原审核内容的受信快照/摘要、来源与更正关系，而不只保存可编辑评论 URL；勘误保留原结论。H→F 按预定路径和所有提交验证，不能只看最终净差异。base 影响判断涉及证据/假设/方向时交回独立内容审核者，不让机械合并者凭“无关”字符串代裁；版本组合应进入最终核验记录。验收加入共享账号可编辑评论、尾部中途改正文再改回、旧 base 检查复用等反例。

**N4｜状态 CAS 不是外部副作用的 fencing。** §8 [L113–115](https://github.com/mythpan1/pathwise-research/blob/ddbd4f316d0450bdf54d6e8701d41876913d3a9a/docs/proposals/2026-10-25-versioned-handoff-gates.md#L113-L115) 已要求“核对或隔离其写入后再接管”，方向正确。
实现时须选定可兑现该要求的写入隔离/唯一受信写入口：旧 worker 即使不能更新账本，仍可能持旧凭据发出 merge。必须在真正写入边界核对当前 revision/授权/租约；不能做到隔离时停止接管写操作。明确暂停/取消与已发出未确认操作的顺序及 RECONCILE 规则，不承诺能撤回在途请求。验收要覆盖“最后一次读取后暂停/换 revision”“旧 worker 租约到期仍活着并继续写”“外部成功但结果落账失败”，而不只测过期回调不能覆盖状态。

**N5｜三主线一致性留一张小型语义对照，不新增审批链。** §1、§3、§5 [L9](https://github.com/mythpan1/pathwise-research/blob/ddbd4f316d0450bdf54d6e8701d41876913d3a9a/docs/proposals/2026-10-25-versioned-handoff-gates.md#L9)、[L36–40](https://github.com/mythpan1/pathwise-research/blob/ddbd4f316d0450bdf54d6e8701d41876913d3a9a/docs/proposals/2026-10-25-versioned-handoff-gates.md#L36-L40)、[L77–84](https://github.com/mythpan1/pathwise-research/blob/ddbd4f316d0450bdf54d6e8701d41876913d3a9a/docs/proposals/2026-10-25-versioned-handoff-gates.md#L77-L84)。
在同一任务/审核记录用短段落说明：本单元对应哪些政策/产业变迁/人口结构主线；怎样连到未来十年学业职业判断及当前选择；哪些假设或缺口会改变判断；若偏离 charter，指向哪项用户决定。不是要求每个有限单元同时研究三条主线，也不能以填满标签替代 G2 内容判断。实施前冻结可追溯的用户决定与生效 charter；不要把本提案通过理解为 PR70 已采用或历史方向已自动同步。

### 实际读取与核对

通过 GitHub connector 实际读取：
- 上述固定 H 的设计稿全文，及 base→H compare：**一个提交、仅新增本文件、150 行**。
- 固定 base 上 `scripts/review_controller.py`、`tests/test_review_controller.py`、`.github/workflows/validation.yml` 全文；以及 `AGENTS.md`、`docs/agent-workflow.md`、`docs/review-automation.md`、`reviews/README.md`。
- Issue #71、PR #72 元数据与评论、main 分支和 rulesets 读取；发布前复读 PR，仍为 open、非 Draft、未合并，head/base 与本审核一致。
- [CI run 40164917263](https://github.com/mythpan1/pathwise-research/actions/runs/40164917263)：`pull_request`、指定 validation.yml、H 及 base 匹配，completed/success。该 CI 只运行已有控制器单测，不证明本设计已执行。

当前 main 返回 `protected=false`、required-status enforcement `off`；rulesets GET 返回 **403，提示升级套餐或公开仓库**。未取得完整规则集，不能认证 L2，也没有据此更改套餐、可见性、权限或换入口重试。稿件对当前限制的披露与我的读取一致。

**未核：** TB 原始材料及其运行接线、用户三主线决定的原始会话证据（本次只核提案与 Issue #71 的一致性）、任何现实研究事实；未执行控制器/本地测试、故障注入、真实收据验收、权限隔离或服务端绕过测试。本次文本审阅不是 G1 原始字节交接验收，也未验证尚不存在的 H→F 归档与采用收尾实现。

**停止边界：** 本运行仅发表此审核评论；未修改文件、PR 状态、现行规则或配置，未合并、部署、恢复研究，也未操作 PR32/70。
