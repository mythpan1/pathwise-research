# 知途研究 v3 场景化按需加载路由表（Routing Index）

本文件继承轻量化按需检索原则，指导各岗位在**立题排重、自上而下拐点刷新、自下而上个案志愿倒推**三类核心工作场景下精准读取最小必要文件集，将单次会话上下文开销控制在最低水平，彻底替代百 KB 级全量扫描。

---

## 一、全局必读最小锚点（按任务类型选择，禁全库盲读）

| 任务场景 | 第一步必读索引 | 第二步按需定向加载 | 严禁盲目全量加载的内容 |
| --- | --- | --- | --- |
| **场景 A：新课题立项与防跑偏排重** | [master-map.md](master-map.md) + [manifest.json](manifest.json) | 拟归属 `slot_id` 所在目录的 `README.md` 及同簇已入库上下游卡片 | 其他无关领域的 `L1–L4` 卡片、本地大体积招生 CSV 全表 |
| **场景 B：宏观/政策/人口拐点自上而下刷新** | [manifest.json](manifest.json)（查 `volatile` 到期与 `upstream_ids` 依赖链） | 发生变动的 `L1` 卡片 → 受波及的 `L2-CAR-*` → 关联 `L3-PTH-*` → 关联 `L4-DEC-*` | 未受该外驱主线波及的其余行业与专业簇卡片 |
| **场景 C：江苏考生志愿与 4–7 年规划自下而上倒推** | 本地受控区考生四维约束卡 + [../scripts/README.md](../scripts/README.md) | 经 `D4` 超额漂移初筛命中的专业代码 → 查 `D5` 映射字典 → 定向读取命中的 `L4-DEC-*`、`L3-PTH-*`、`L2-CAR-*` 卡片 | 未进入该考生位次窗或已被硬红线否决的专业簇文档 |
| **场景 D：框架规范与接口校验** | [../README.md](../README.md) + [../AGENTS.md](../AGENTS.md) | [../docs/architecture-v3.md](../docs/architecture-v3.md)、[../data/README.md](../data/README.md)、[../scripts/validate_framework.py](../scripts/validate_framework.py) | 历史归档旧库全文 |

---

## 二、三条标准执行路由详解

### 2.1 路由一：开题排重与对槽准入路由（总控 + 研究主笔）

1. **查版图定槽位**：打开 [master-map.md](master-map.md)，核对拟研究问题落在 43 个主干槽位（`L1-DEM-*` / `L1-POL-*` / `L1-IND-*` / `L2-CAR-*` / `L3-PTH-*` / `L4-DEC-*`）中的哪一项，并确认是否符合当前 `Batch 1 → Batch 4` 推进阶段。
2. **查索引排重复（逻辑 `AND` 三问 + 普通批可及性）**：检索 [manifest.json](manifest.json) 中该 `slot_id` 及多对多关联岗位族卡片，严格校验「防细枝末节立题三问」是否**同时满足（`AND`）**——凡跨行业通用岗位已有主槽、或仅涉极少数人特殊班细则/冷门小证书而缺乏江苏普通批现实可及性的议题，一律并入既有主干卡附注或终止立项。
3. **定信源派采集**：立项通过后，对照目标层目录说明（[../research/l1-drivers/README.md](../research/l1-drivers/README.md) 至 [../research/l4-decisions/README.md](../research/l4-decisions/README.md)）明确 1–3 个靶向求证断点，交资料员走本地防投毒筛源与纯净 Notebook 加工。
4. **套模板提 PR**：研究主笔使用 [../templates/](../templates/driver-signal.md) 对应单态模板成稿，绑定 `slot_id` 与 `upstream_ids`，登记 [manifest.json](manifest.json) 并运行 [../scripts/validate_framework.py](../scripts/validate_framework.py) 后发起分支 PR。

### 2.2 路由二：自上而下拐点联动刷新路由（资料员 + 研究主笔 + 数据工程师）

1. **触发源识别**：当 `manifest.json` 中某张 `volatile` 卡片临近 `valid_until`（如年度人口/财政决算发布、新一轮国央企一批校招简章更新、教育部本科专业目录调整），或监测到重大政策/行业拐点时启动。
2. **精准影响域展开**：以变更的 `L1` 卡片 ID 为起点，在 [manifest.json](manifest.json) 中反查所有将其列入 `upstream_ids` 的 `L2-CAR-*` 卡片；仅当 `L2` 的毕业窗景气等级、付款稳定度或应届带教入口发生实质改判时，才继续向下展开重审关联的 `L3-PTH-*` 与 `L4-DEC-*` 卡片。
3. **单态就地升版与下游反向回灌（双向联动）**：
   - 正向刷新：在同一分支 PR 内同步更新受影响的下游卡片正文与 `manifest.json` 有效期，不保留旧结论平行段落；
   - **反向回灌路由**：当 `Batch 3/4` 实证发现下游硬门槛（如普遍刚性读硕、江苏专业组同组调剂暴露或 `target_regions` 地方供需分化）推翻上游 `L1/L2` 排序前提时，逆向沿 `upstream_ids` 定位上游 `slot_id`，在同一 PR 内联立修订上游卡片或在 `manifest.json` 中将其状态置为 `needs_reverify`，经红队与独立审核通过后合入 `main`。

### 2.3 路由三：自下而上个案志愿与职业规划合成路由（本地受控区专用）

> **隔离提醒**：本路由全程在本地受控工作区执行，仅单向只读引用公开仓库的 `L2–L4` 卡片结论，严禁将任何个案输入或产出写回本仓库。

1. **建档切分红线**：基于 [../templates/individual-constraints.md](../templates/individual-constraints.md) 在本地受控区建立考生四维约束实例，明确选科、位次、体检代码、本硕学费预算及**硬红线排斥集 vs 一般弱偏好集**。
2. **底表漂移初筛**：数据工程师按 [../data/README.md](../data/README.md) 与 [../scripts/README.md](../scripts/README.md) 契约，在本地受控招生底表上执行跨年组号拆并核对、硬红线整组一票否决（`2B`）与分段超额漂移计算，生成冲/稳/保候选专业组池（含长三角扎堆检测与外省同档补充）。
3. **挂载公共机制卡**：通过专业代码映射表（`D5`），仅按需加载候选专业组涉及的 `L4-DEC-*`、`L3-PTH-*` 与 `L2-CAR-*` 公共卡片，核验考生 `T+4 / T+7` 毕业窗景气、本硕门槛匹配度，并汇总 `[结构代理降级]`（`1B`）项目的招办线下核实单。
4. **水位分级与四维冲击收口**：调用 `D6` 接口计算非红线混编组的组内相对水位（`water_level`），对主攻组与备选组执行**四维独立备选冲击核验**（核查付款主体、同组调剂隔离、学历/执照门槛及地域/组织单点），收口输出个案志愿梯度表与 4–7 年大学及职业路线图。
