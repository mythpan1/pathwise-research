# 知途研究 v3.1 场景化按需加载路由表（Routing Index · v3.1.0）

本文件指导各岗位在**按槽填充排重、自上而下拐点刷新、自下而上私人志愿倒推**三类核心工作场景下，从 `4 层 × 17 二级子目录 × 107 篇细枝卡片` 中精准读取最小必要文件集，将单次会话上下文开销压至最低，彻底杜绝全库盲目扫描。

---

## 一、全局必读最小锚点（按任务类型选择，禁全库盲读）

| 任务场景 | 第一步必读索引 | 第二步按需定向加载 | 严禁盲目全量加载的内容 |
| --- | --- | --- | --- |
| **场景 A：单篇 `draft` 提纲填充与开题排重** | [master-map.md](master-map.md) + [manifest.json](manifest.json) | 目标 `slot_id` 对应的单篇提纲卡、所属二级子目录 `README.md` 及其 `upstream_ids` 直接关联卡片 | 其他无关二级子目录的数十篇卡片、本地大体积招生 CSV 全表 |
| **场景 B：宏观/政策/人口拐点自上而下刷新** | [manifest.json](manifest.json)（查 `volatile` 到期与 `upstream_ids` 有向图） | 发生变动的 `L1` 叶子卡 → 下游引用它的 `L2` 岗位卡 → 关联 `L3` 培养/通道卡 → 关联 `L4` 收口卡 | 未受该外驱主线波及的其余二级子目录文档 |
| **场景 C：江苏考生志愿与 4–7 年规划自下而上倒推** | 本地受控区考生四维约束卡 + [../scripts/README.md](../scripts/README.md) | 必读 `4.1/4.2` 风控底座 + 对应分段 `4.3.*` 收口卡 + `D4` 命中的专业代码所映射的 `3.1.* / 3.2.* / 2.x.*` 叶子卡 | 未进入该考生位次窗、选科不符或已被硬红线否决的专业簇卡片 |
| **场景 D：框架规范与接口门禁校验** | [../README.md](../README.md) + [../AGENTS.md](../AGENTS.md) | [../docs/architecture-v3.md](../docs/architecture-v3.md)、[../data/README.md](../data/README.md)、[../scripts/validate_framework.py](../scripts/validate_framework.py) | 历史归档旧库全文 |

---

## 二、三条标准执行路由详解

### 2.1 路由一：按槽填充与排重准入路由（总控 + 资料员 + 研究主笔）

1. **查版图锁单篇**：打开 [master-map.md](master-map.md) §三，确认待填充课题对应的精确 `slot_id`（`L*-***-dd.dd`）、`parent_slot_id`（43 母槽之一）与 `card_id`，确认其 `upstream_ids` 前置批次卡片已就绪（或登记为紧急纵向切片）。
2. **读提纲定靶点**：直接读取目标单篇 `draft` 提纲卡及同二级子目录 `README.md`，核对其“不越界声明”以防与同目录姊妹卡重复，提取卡内已列明的待抓一手信源与 `- [ ]` 核查清单交资料员走本地防投毒筛源与纯净 Notebook 加工。
3. **套模板升格提 PR**：研究主笔回核一手原件，对齐 [../templates/](../templates/driver-signal.md) 规范填充实证正文，将顶部 YAML `status` 由 `"draft"` 升格为 `"active"`，由数据工程师同步 [manifest.json](manifest.json) 并运行 [../scripts/validate_framework.py](../scripts/validate_framework.py) 通过后发起分支 PR。

### 2.2 路由二：自上而下拐点联动与下游反向回灌路由（资料员 + 研究主笔 + 数据工程师）

1. **触发源识别**：当 [manifest.json](manifest.json) 中某张 `volatile` 叶子卡临近 `valid_until`（如年度人口/财政决算发布、新一轮国网/公考招录公示、教育部本科专业备案撤销名单或江苏招生政策更新），或监测到重大政策/行业拐点时启动。
2. **精准影响域展开**：以变更的 `card_id` 为起点，在 [manifest.json](manifest.json) 中沿 `upstream_ids` 有向无环图反查直接下游卡片；仅当上游核心结论、毕业窗景气度或准入硬门槛发生实质改判时，才继续向下展开重审关联的 `L3` 与 `L4` 叶子卡。
3. **单态就地升版与下游反向回灌（双向联动）**：
   - 正向刷新：在同一分支 PR 内就地更新受影响卡片正文、`last_verified` 与 `manifest.json` 有效期，不保留废止旧段落；
   - **反向回灌路由**：当 `Batch 3/4` 实证发现下游硬门槛（如普遍刚性读硕、江苏专业组同组调剂暴露或 `target_regions` 地方供需分化）推翻上游 `L1/L2` 既有假设时，逆向沿 `upstream_ids` 定位上游 `card_id`，在同一 PR 内联立修订上游卡片或在 `manifest.json` 将其状态置为 `needs_reverify`。

### 2.3 路由三：自下而上私人志愿与职业规划合成路由（本地受控区专用）

> **隔离提醒**：本路由全程在本地受控工作区执行，仅单向只读引用公开仓库的 `L1–L4` 卡片结论，严禁将任何真实考生输入或产出写回本仓库。

1. **建档切分红线**：基于 [../templates/individual-constraints.md](../templates/individual-constraints.md) 与 [../research/l4-decisions/4.1-个体家庭约束与防偏底座/README.md](../research/l4-decisions/4.1-个体家庭约束与防偏底座/README.md) 在本地受控区建立考生四维约束实例，切分硬红线排斥集与一般弱偏好集。
2. **受控表漂移初筛**：数据工程师按 [../data/README.md](../data/README.md) 与 [../scripts/README.md](../scripts/README.md) 契约，在本地受控招生数据上执行跨年组号拆并核对、硬红线整组一票否决（`2B`）与分段超额漂移计算（`D4`），生成冲/稳/保候选专业组池（含长三角扎堆检测与外省同档补充）。
3. **定向挂载细枝卡片**：通过专业代码映射字典（`D5`），仅定向读取候选专业组涉及的 `3.1.*` 专业实得卡、`3.2.*` 特殊通道卡、`3.3/3.4` 本硕执行卡、`2.1–2.5` 岗位规格卡及对应位次段的 `4.3.*` 两难收口卡，汇总 `[结构代理降级]`（`1B`）项目的招办线下核实单（配合 `4.2.6` 招办十问）。
4. **水位分级与四维冲击收口**：调用 `D6` 接口计算非红线混编组的组内相对水位（`water_level`），对主攻组与备选组执行**四维独立备选冲击核验**，在本地受控区输出最终冲稳保专业组方案与 4–7 年大学及职业路线图。
