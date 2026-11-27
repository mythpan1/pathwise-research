# Pathwise v3 计算接口契约与仓库静态校验说明（D4 / D6 / Gate）

> 本契约落实 `docs/architecture-v3.md` §4.2 中的 **D4**（位次购买力分段超额漂移计算接口）与 **D6**（四维个体约束输入与 `2B` 组内 `water_level` 精算输出接口），并给出仓库静态门禁脚本 `scripts/validate_framework.py` 的运行说明。  
> **方法论红线**：全链路严格遵循 `1B / 2B / 3B`——**零拍脑袋固定加权总分**（严禁主观加减分扣分表与“天坑”主观标签）、**零 MBTI 或通俗性格标签**、**硬红线整组一票否决 + 非红线组内 `water_level` 相对水位分级**。真实考生计算仅在本地受控区运行。

---

## 1. D4：位次购买力分段超额漂移计算接口与跨省多样性触发规则

### 1.1 接口职责与上游依赖
- **上游依赖**：本地受控 D2-A（`admissions_group_cutoff`）、D2-C（`js_score_rank_scale`）、D3-A（`group_cross_year_mapping`）、D3-B（`policy_shock_years`），均通过 [data/README.md](../data/README.md) 约定的受控目录环境变量加载。
- **核心原理**：单校位次受组号拆并等结构事件主导噪声极大，需按同分段院校群构建“分段行业指数”，先仅剔除 `D3-B` 中经官方一手原件核定（`verification_status == "verified_primary_source"` 且 `exclude_from_drift_window == true`）的一次性政策断裂转换对，再将位次变动拆解为“考生规模增长贡献”与“段内超额漂移”，输出自适应冲/稳/保检索窗及跨省多样性诊断；**凡窗口覆盖任何待核断裂候选对（`verification_status == "pending_verification"`），严禁静默剔除或返回常态 `"ok"`**。

### 1.2 输入契约（`D4Request` JSON Schema）

```json
{
  "target_year": 2026,
  "province_source": "JS",
  "track": "physics",
  "student_rank": 22000,
  "equivalent_score": 615,
  "window_years": [2023, 2024, 2025],
  "segment_score_half_width": 10,
  "horizon_years": 4,
  "multipliers": {
    "reach_range": [0.80, 0.95],
    "match_range": [0.95, 1.05],
    "base_safety_upper": 1.30,
    "safety_upper_clamp": [1.25, 1.50]
  },
  "deep_safety_policy": {
    "off_below_rank": 25000,
    "mandatory_from_rank": 40000,
    "min_safety_college_count": 15
  },
  "diversity_policy": {
    "home_province": "江苏",
    "cluster_provinces": ["江苏", "上海", "浙江"],
    "max_home_share": 0.40,
    "max_cluster_share": 0.65,
    "min_out_of_cluster_groups": 5
  }
}
```

| 输入字段 | 类型 | 必填 | 约束说明 |
| --- | --- | --- | --- |
| `target_year` | `integer` | 是 | 目标填报年份（YYYY） |
| `province_source` | `string` | 是 | 生源省份代码（默认 `"JS"`） |
| `track` | `string` | 是 | `physics` \| `history` |
| `student_rank` | `integer` | 是 | `>= 1`；考生等效位次 |
| `equivalent_score` | `integer` | 否 | 若为 `null`，由 D2-C 一分一段表按 `student_rank` 反查最新基准年等效分 |
| `window_years` | `array<integer>` | 是 | 候选回测年份序列；执行期强制对照 D3-B，仅剔除 `verification_status == "verified_primary_source" && exclude_from_drift_window == true` 的转换对；若覆盖任何 `pending_verification` 候选对须强制降级为 `"degraded"` |
| `segment_score_half_width` | `integer` | 否 | 分段行业指数窗口半宽（默认 `10`，即等效分 `±10` 分） |
| `horizon_years` | `integer` | 否 | 累计漂移换算跨度（默认 `4` 年） |
| `multipliers` | `object` | 否 | 冲/稳区间保持 `[0.80, 0.95]` 与 `[0.95, 1.05]` 不作漂移放大；保底上界按超额漂移自适应并钳位在 `[1.25, 1.50]` |
| `deep_safety_policy` | `object` | 否 | 深保触发位次与学校数安全边际阈值 |
| `diversity_policy` | `object` | 否 | 防省内/长三角扎堆的跨省多样性触发阈值 |

### 1.3 数学分解、状态机与触发规则

1. **断裂年一手核验与隔离**：读取 D3-B：
   - **仅当** `verification_status == "verified_primary_source"` 且 `exclude_from_drift_window == true` 时，方可从相邻转换对中剔除该转换对，并记录于 `excluded_shock_years[]`；
   - **待核候选对降级硬规则**：若 `window_years` 构成的任意相邻转换对命中 D3-B 中 `verification_status == "pending_verification"` 的待核断裂候选对（如江苏物理类在官方原件核定前均标 `[待核未知]` 的 `"2022->2023"` 与 `"2023->2024"`），**严禁静默剔除，亦严禁当作已核清窗口返回常态 `"ok"`**——必须强制置 `calculation_status = "degraded"`，在 `D4Response` 输出 `pending_shock_candidates[]` 并在 `warnings` 返回 `"UNVERIFIED_POLICY_SHOCK_CANDIDATE"`，同时保守回退至 `base_safety_upper`（禁止据此缩窄保底上界）。
2. **分段超额漂移分解**（对每个有效相邻年对 `Y1 -> Y2`，仅纳入 D3-A 中 `rank_inheritability != "none"` 的同分段专业组）：
   - 考生规模增长比：`growth_ratio = total_track_applicants(Y2) / total_track_applicants(Y1)`
   - 规模预测位次：`predicted_rank_y2 = actual_rank_y1 * growth_ratio`
   - 考生增长贡献：`applicant_growth_contribution = predicted_rank_y2 - actual_rank_y1`
   - 段内超额漂移：`segment_excess_drift = actual_rank_y2 - predicted_rank_y2`（负值表示该分段位次升值，正值表示位次贬值）
   - 总漂移恒等式：`total_drift = applicant_growth_contribution + segment_excess_drift`
   - 对有效年对取中位数或均值，得 `annual_excess_drift`（若命中 `UNVERIFIED_POLICY_SHOCK_CANDIDATE`，仅作诊断透出，不用于缩窄保底窗）。
3. **自适应检索窗计算**：
   - `safety_upper_multiplier = clamp(base_safety_upper + (annual_excess_drift * horizon_years) / student_rank, safety_upper_clamp[0], safety_upper_clamp[1])`（`calculation_status == "degraded"` 且命中未核实断裂候选或有效窗口不足时，保守取 `max(base_safety_upper, safety_upper_multiplier)` 或直接回退 `base_safety_upper`）
   - 冲（`reach`）：`[round(student_rank * 0.80), round(student_rank * 0.95)]`
   - 稳（`match`）：`[round(student_rank * 0.95), round(student_rank * 1.05)]`
   - 保（`safety`）：`[round(student_rank * 1.05), round(student_rank * safety_upper_multiplier)]`
4. **深保状态机（`deep_safety_mode`）**：
   - `OFF`：`student_rank < off_below_rank` 且保底池达标院校数 `>= min_safety_college_count`；
   - `ENABLED`：`off_below_rank <= student_rank < mandatory_from_rank`，或低位次段安全边际收窄导致保底院校数不足；
   - `MANDATORY`：`student_rank >= mandatory_from_rank`（高密度分段必须深挖外省/非热门同档院校）。
5. **跨省多样性触发规则（`diversity_diagnosis.trigger_status`）**：
   - 统计初筛候选专业组中 `college_province == home_province` 占比（`home_share`）与 `college_province in cluster_provinces` 占比（`cluster_share`）；
   - 当 `home_share > max_home_share` 或 `cluster_share > max_cluster_share` 或长三角外候选组数 `< min_out_of_cluster_groups` 时，触发 `OUT_OF_CLUSTER_RECALL_TRIGGERED`，自动扩大检索外省同档位次院校并标记 `recalled_by_diversity_rule=true`。

### 1.4 输出契约（`D4Response` JSON Schema）

> **示例说明**：下例对应 `window_years = [2023, 2024, 2025]` 且江苏物理类 `"2023->2024"` 尚处于 `D3-B` `verification_status: "pending_verification"`（`[待核未知]`）的情形，展示强制降级 `calculation_status: "degraded"` 与保守保底上界回退；待官方原件核定后方可转入已核剔除或常态窗口。

```json
{
  "schema_version": "3.0.7",
  "calculation_status": "degraded",
  "excluded_shock_years": [],
  "pending_shock_candidates": ["2023->2024"],
  "effective_transitions": ["2024->2025"],
  "drift_decomposition": {
    "segment_score_center": 615,
    "segment_sample_groups": 38,
    "annual_applicant_growth_contribution": 760,
    "annual_excess_drift": null,
    "annual_total_drift": null,
    "horizon_cumulative_excess_drift": null
  },
  "search_windows": {
    "reach_rank_range": [17600, 20900],
    "match_rank_range": [20900, 23100],
    "safety_rank_range": [23100, 28600],
    "safety_upper_multiplier": 1.30,
    "deep_safety_mode": "OFF"
  },
  "diversity_diagnosis": {
    "home_province_share": 0.44,
    "cluster_share": 0.68,
    "out_of_cluster_group_count": 4,
    "trigger_status": "OUT_OF_CLUSTER_RECALL_TRIGGERED"
  },
  "candidate_groups": [
    {
      "college_code": "9901",
      "college_name": "示例理工大学",
      "college_province": "示例省",
      "group_code": "02",
      "latest_min_rank": 24500,
      "tier_bucket": "safety",
      "rank_inheritability": "conditional",
      "composition_shift_risk": "high",
      "recalled_by_diversity_rule": true,
      "completeness_status": "complete"
    }
  ],
  "warnings": [
    "UNVERIFIED_POLICY_SHOCK_CANDIDATE"
  ]
}
```

### 1.5 边界与异常处置（D4）

| 异常情形 | 系统状态 | 处理方式（绝不伪造数据） |
| --- | --- | --- |
| `window_years` 覆盖任一 `D3-B` 中 `verification_status == "pending_verification"` 的待核断裂候选对（如江苏物理类 `2022->2023`、`2023->2024`） | `calculation_status: "degraded"` | 禁止静默剔除或返回 `"ok"`；在 `pending_shock_candidates[]` 列出全部命中候选对，在 `warnings` 返回 `UNVERIFIED_POLICY_SHOCK_CANDIDATE`，并回退保守基准系数 `base_safety_upper`（不缩窄保底上界），待省考试院一手原件核定后解锁 |
| 剔除已核实政策断裂年后有效相邻年对 `< 1` | `calculation_status: "degraded"` | 停止估算 `annual_excess_drift`，回退至保守基准系数 `base_safety_upper` 并在 `warnings` 返回 `INSUFFICIENT_DRIFT_WINDOW` |
| 同分段有效样本组数 `< 10` | `calculation_status: "degraded"` | 自动提示扩大分段半宽或标记 `LOW_SEGMENT_SAMPLE_SIZE`，不伪造平滑系数 |
| 某专业组 `rank_inheritability == "none"` | 单组标记 `tier_bucket: "uncalibrated"` | 保留在候选提示清单但禁止直接归入 `safety` 池，要求结合当年招生计划人工复核 |

---

## 2. D6：四维个体约束输入与 `2B` 组内 `water_level` 精算接口

### 2.1 输入契约（`D6Input` 四维个体/家庭约束卡 JSON Schema）

> **隐私铁律**：`case_id` 仅允许使用匿名编号（如 `CASE-DEMO-001`），严禁写入真实考生姓名、身份证号、手机号或学校班级信息；实填实例 100% 留存本地受控区。

```json
{
  "schema_version": "3.0.7",
  "target_year": 2026,
  "case_id": "CASE-DEMO-001",
  "dim1_academic_physical": {
    "track": "physics",
    "subject_combo": ["physics", "chemistry", "biology"],
    "student_rank": 22000,
    "foreign_language": "english",
    "subject_scores": {
      "chinese": 118,
      "math": 128,
      "foreign_language": 122
    },
    "math_physics_load_tolerance": "high",
    "foreign_language_proficiency": "medium",
    "physical_limit_codes": []
  },
  "dim2_financial_horizon": {
    "max_annual_tuition_cny": 10000,
    "grad_school_budget_tolerance": "conditional",
    "early_low_pay_buffer_years": 3
  },
  "dim3_preference_boundaries": {
    "stability_elasticity_floor": "balanced",
    "target_job_regions": ["长三角", "华北"],
    "hard_redline_majors": ["101101", "081001"],
    "hard_redline_scenarios": ["prohibited_transfer_sino_foreign"],
    "soft_dislike_majors": ["080401"]
  },
  "dim4_consensus_debias": {
    "family_disagreement_topics": ["是否接受跨省就读"],
    "out_of_province_willingness": "moderate",
    "debias_checklist_ack": {
      "no_min_score_anchoring": true,
      "no_yrd_clustering_blindspot": true,
      "no_blind_transfer_assumption": true,
      "no_pseudo_independent_backup": true
    }
  },
  "candidate_group_targets": [
    {
      "target_year": 2026,
      "batch": "undergrad_regular",
      "college_code": "9901",
      "group_code": "02",
      "target_major_seqs": [1, 2]
    },
    {
      "target_year": 2026,
      "batch": "undergrad_regular",
      "college_code": "9904",
      "group_code": "01",
      "target_major_seqs": [1]
    }
  ],
  "candidate_pair_bindings": [
    {
      "pair_id": "PAIR-01",
      "primary": {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9901",
        "group_code": "02",
        "major_seq": 1,
        "moe_major_code": "080601",
        "route_id": "080601-PRI-01"
      },
      "backup": {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9904",
        "group_code": "01",
        "major_seq": 1,
        "moe_major_code": "080601",
        "route_id": "080601-BKP-01"
      }
    }
  ]
}
```

| 维度 | 核心字段 | 允许枚举 / 类型 | 业务用途 |
| --- | --- | --- | --- |
| **规则版本锚定** | `target_year` | `integer`（YYYY，必填） | 强制关联当年 `D2-D`（`admissions_group_charter_rules`）有效招生章程、实际调剂范围与选科/体检/单科条款，禁止拿旧年规则误放行或误否决 |
| **维度一**（学科与身体硬门槛） | `track`, `subject_combo`, `student_rank`, `foreign_language`, `subject_scores`, `math_physics_load_tolerance`, `foreign_language_proficiency`, `physical_limit_codes` | `foreign_language`: 语种代码（如 `"english"`、可空）；`subject_scores`: 单科分对象（可空）；`tolerance`: `high` \| `medium` \| `low`; `physical_limit_codes`: 体检受限条款数组（无受限填 `[]`） | 选科硬匹配、退档体检红线否决、当年 `D2-D` 单科与外语语种硬门槛核对、硬核数理课表负荷校核 |
| **维度二**（财务与长周期缓冲） | `max_annual_tuition_cny`, `grad_school_budget_tolerance`, `early_low_pay_buffer_years` | `grad_school_budget_tolerance`: `full_support` \| `conditional` \| `bachelor_direct_only` | 学费红线否决、结合 `D5.primary_routes[]` 逐路径学历门槛校验、成长期缓冲匹配 |
| **维度三**（稳态弹性与红线边界） | `stability_elasticity_floor`, `target_job_regions`, `hard_redline_majors`, `hard_redline_scenarios`, `soft_dislike_majors` | `floor`: `public_soe_priority` \| `balanced` \| `market_elastic`; `hard_redline_scenarios`: 与 `D2-D.group_wide_scenario_flags` / `member_scenario_flags_by_seq` 对齐的 7 类标准枚举 | **严格分离**绝对红线（触发整组一票否决）与一般弱偏好（转入 `water_level` 精算） |
| **维度四**（家庭共识与认知防偏） | `family_disagreement_topics`, `out_of_province_willingness`, `debias_checklist_ack` | `willingness`: `high` \| `moderate` \| `low`; **防偏 4 项布尔确认**（与 `templates/individual-constraints.md` 必检四问一一对应：`no_min_score_anchoring`、`no_yrd_clustering_blindspot`、`no_blind_transfer_assumption`、`no_pseudo_independent_backup`） | 防最低分锚定、防长三角扎堆溢价盲区、防盲信进校转专业幻觉、防假独立双保险盲区 |
| **逐组主动填报专业**（`3.0.7`） | `candidate_group_targets[]` | 必填数组，元素含 `{target_year, batch, college_code, group_code, target_major_seqs: [integer, ...]}`（可选显式 `track` 须严格等于 `dim1.track`） | 按归一化五元组唯一键 `(target_year, track, batch, college_code, group_code)` 全局唯一，且单条 `target_major_seqs` 为非空正整数数组并严格去重（`len(set(T)) == len(T)`）、`target_year == D6Input.target_year` 且 `T ⊆ G`；缺失、出现重复组键（`>= 2` 条）或重复/非法序号一律判 `group_target_valid = false`，与数组顺序无关地回退 `S = G` 并阻断保底 |
| **主备志愿组绑定**（`3.0.7`） | `candidate_pair_bindings[]` | 数组元素含全局唯一 `pair_id`、`primary` 与 `backup`，两端均必填 `{target_year, batch, college_code, group_code, major_seq, moe_major_code, route_id}` | 将同专业或**跨专业**的主备路径在个案端显式绑定至具体院校专业组与当年 `D2-D` 规则，须通过 §2.2 第 5 点 `pair_id` 唯一性、跨表引用完整性与可达性（`major_seq ∈ T` 且 `group_target_valid == true`）硬校验 |

### 2.2 `2B` 两阶段判定状态机（绑定 `D2-D` 当年调剂规则，严禁主观加权总分）

> **当年章程 `D2-D` 暴露集合 `S` 裁定与按成员序号投影铁律（贯穿阶段一与阶段二，`3.0.7`）**：  
> 设 `G` 为目标年 `D2-B` 该专业组全部专业序号集合，`A` 为 `D2-D.adjustable_major_seqs`，`E` 为 `D2-D.excluded_major_seqs`。定义候选组归一化唯一键为五元组 `K = (target_year, track, batch, college_code, group_code)`（其中 `track` 继承自 `D6Input.dim1_academic_physical.track`，若条目显式携带 `track` 则须严格等于 `dim1.track`；字符串字段去首尾空白且 `college_code / group_code` 与目标年 `D2-A` 规范编码精确对齐）。
> 1. **显式接入 `D2-D`（`admissions_group_charter_rules`，见 [data/README.md §2.4](../data/README.md)）裁定实际录取暴露专业序号集合 `S`**：
>    - **逐组主动填报集合 `T` 唯一性与合法性前置校验（闭环 `#16`，顺序无关铁律）**：`group_target_valid == true` **当且仅当**该待评组在 `candidate_group_targets[]` 中按归一化五元组键 `K` **恰好出现 1 次**（严禁同组出现 `>= 2` 条记录，无论 `target_major_seqs` 相同或不同），`target_year == D6Input.target_year`，且 `target_major_seqs` 为非空正整数数组、元素**严格唯一无重复**（`len(set(T)) == len(T)`）并满足 `T ⊆ G`。凡缺失该组记录、出现重复组键（`>= 2` 条）、或 `target_major_seqs` 含重复元素/非正整数/空数组/越界 `⊈ G` / `target_year` 不符，一律记 **`group_target_valid = false`**——**严禁取首条、取末条或覆盖合并为子集**，必须与数组顺序无关地强制令 **`S = G`（全组成员最坏暴露集合）**执行阶段一全量 `VETO_*` 硬红线扫描，且**无论阶段一是否 `VETOED`**，一律强制置 `unverified_redline_block_safety = true`、`water_level = "unknown"`、`water_level_percentile = null`、`safety_pool_blocked = true`；同时任何引用 `group_target_valid == false` 专业组的 `candidate_pair_bindings[]` 端点自动置 `binding_valid = false`；
>    - `adjustment_scope_mode == "full_group_default"`（且 `rule_completeness == "complete"`）：`S = G`（若 `group_target_valid == false` 仍同步触发上述阻断保底与 `water_level = "unknown"`）；
>    - `adjustment_scope_mode == "subset_isolated_verified"`（且 `rule_completeness == "complete"`、`group_target_valid == true`、`A != null` 且 `(A ∪ E) ⊆ G`）：**`S = T ∪ (A \ E)`**——**`E` 仅从被动调剂集合 `A` 中剔除，绝不从考生主动填报集合 `T` 中剔除**（主动填报的排除调剂专业仍可能被志愿直接录取，必须保留在 `S` 内接受全量硬红线与水位扫描）；若考生填报合法（`group_target_valid == true`）但 `A == null` 或 `(A ∪ E) ⊈ G`，**保留 `group_target_valid == true`（不伪造为考生填报非法，亦不因此置 `binding_valid = false`）**，仅按章程规则不完整回退 `S = G` 并置 `unverified_redline_block_safety = true`、`water_level = "unknown"`、`water_level_percentile = null`、`safety_pool_blocked = true`；
>    - `adjustment_scope_mode == "no_adjustment_written_promise_verified"`（且 `rule_completeness == "complete"`、`group_target_valid == true` 且满足 `written_no_adjustment_condition`）：`S = T`（若未满足书面生效条件，同样保留 `group_target_valid == true` 并按章程回退 `S = G` 阻断保底）；
>    - **凡缺失当年 `D2-D` 记录、`adjustment_scope_mode == "unknown"` 或 `rule_completeness != "complete"`**：在保留真实 `group_target_valid` 状态的前提下，回退 `S = G` 执行最坏暴露红线扫描，并强制置 `unverified_redline_block_safety = true`、`water_level = "unknown"`、`water_level_percentile = null`、`safety_pool_blocked = true`。
> 2. **场景红线排除后投影规则（`3.0.7`）**：
>    - 若 `D2-D.group_wide_scenario_flags == null`、`D2-D.member_scenario_flags_by_seq == null`，或存在任意 `seq ∈ S` 在 `member_scenario_flags_by_seq` 中缺键或值为 `null`，强制置 `unverified_redline_block_safety = true`、`safety_pool_blocked = true`；
>    - 否则计算投影集合 `effective_scenario_flags(S) = group_wide_scenario_flags ∪ (⋃_{seq ∈ S} member_scenario_flags_by_seq[str(seq)])`，仅按 `effective_scenario_flags(S)` 与 `seq ∈ S` 的成员执行 `VETO_HARD_REDLINE_MAJOR`——未被考生主动填报且已书面排除调剂的 `seq ∈ E \ T` 不污染 `S`，但考生主动填报的 `seq ∈ T ∩ E` 必保留在 `S` 内接受红线否决。
> 3. **缺失绝不等价于安全**：`S` 内任一成员的选科要求（`D2-A.subject_req`）、体检限报条款（`D2-B.physical_limit_codes == null`）、年学费（`tuition_cny_per_year == null`）、学制（`duration_years == null`）、转专业约束（`transfer_restriction == "unknown"`），或当年 `D2-D.group_wide_scenario_flags == null`、`D2-D.member_scenario_flags_by_seq == null`（或任意 `seq ∈ S` 缺键/`null`）、`D2-D.subject_score_limits == null`、`D2-D.foreign_language_limits == null`（以及缺考生 `subject_scores` / `foreign_language` 导致无法排除单科/语种限报）任一命中，均必须置 `unverified_redline_block_safety = true`、`safety_pool_blocked = true`，**严禁默认放行进入 `safety` 保底池**。

#### 阶段一：串联硬关卡与硬红线整组否决（`gate1_status: PASS | VETOED`）
在 `target_year` 当年 `D2-D` 裁定的实际可调剂专业集合 `S` 内，任一已确认条件命中即对整个专业组输出 `gate1_status = "VETOED"` 并记录全部 `veto_reasons[]`，**不再进入水位精算**：
1. `VETO_SUBJECT_MISMATCH`：`dim1.subject_combo` 不满足当年 D2-A `subject_req`；
2. `VETO_PHYSICAL_LIMIT`：`seq ∈ S` 中任一专业在 D2-B 的 `physical_limit_codes`（非空）与考生 `dim1.physical_limit_codes` 存在交集（防进档后因体检受限退档）；
3. `VETO_TUITION_CAP`：`seq ∈ S` 中任一专业 `tuition_cny_per_year > dim2.max_annual_tuition_cny`（或整组属超出预算的中外合作办学组）；
4. `VETO_SINGLE_SUBJECT_OR_LANG`：当年 `D2-D.subject_score_limits` 非空且考生 `dim1.subject_scores` 未达单科线，或 `D2-D.foreign_language_limits` 非空且考生 `dim1.foreign_language` 不在允许语种集合内；
5. `VETO_HARD_REDLINE_MAJOR`：`seq ∈ S` 中任一专业命中 `dim3.hard_redline_majors`，或按下方确定性映射表在投影集合 `effective_scenario_flags(S)` / `seq ∈ S` 成员上命中考生声明的任一 `dim3.hard_redline_scenarios`；
6. `VETO_DEGREE_MISMATCH`：组内全部目标专业在 `D5.primary_routes[]` 中的全部主路径均为 `degree_threshold ∈ {"master_mandatory", "phd_or_residency_mandatory"}`，而 `dim2.grad_school_budget_tolerance == "bachelor_direct_only"`（若目标主路径含 `degree_threshold == "unknown"` 或 `gate_completeness == "unknown"` 且无已核可直就主路径，则置 `unverified_redline_block_safety = true`）。

**`dim3.hard_redline_scenarios`（7 类标准枚举）按可调剂集合 `S` 投影的确定性判定映射表**：

| 场景红线枚举（对齐 `D2-D` 全局/逐序号旗标） | 确定性 `VETO_HARD_REDLINE_MAJOR` 命中条件（仅扫描 `effective_scenario_flags(S)` 与 `seq ∈ S`） | 未知拦截条件（触发 `unverified_redline_block_safety = true`） |
| --- | --- | --- |
| `prohibited_transfer_sino_foreign` | `effective_scenario_flags(S)` 含本项，或任一 `seq ∈ S` 满足 `D2-B.program_type == "sino_foreign"` 且 `D2-B.transfer_restriction == "prohibited"` | 任一旗标字段为 `null`（含 `seq ∈ S` 缺键），或 `seq ∈ S` 中外合作成员 `transfer_restriction == "unknown"` |
| `remote_or_relocated_campus` | `effective_scenario_flags(S)` 含本项，或任一 `seq ∈ S` 的 `D2-B.campus_location` / `D2-A.campus_location` 为异地/偏远分校区 | 任一旗标字段为 `null`（含 `seq ∈ S` 缺键）且 `seq ∈ S` 成员 `campus_location == null` |
| `mandatory_service_bond_or_targeted` | `effective_scenario_flags(S)` 含本项，或任一 `seq ∈ S` 的 `D2-B.program_type ∈ {"targeted", "normal_public_funded"}` | 任一旗标字段为 `null`（含 `seq ∈ S` 缺键）且章程未核清定向/服务期条款 |
| `five_year_or_longer_duration` | `effective_scenario_flags(S)` 含本项，或任一 `seq ∈ S` 的 `D2-B.duration_years >= 5` | 任一旗标字段为 `null`（含 `seq ∈ S` 缺键）且任一 `seq ∈ S` 成员 `D2-B.duration_years == null` |
| `fieldwork_shift_high_hazard` | `effective_scenario_flags(S)` 含本项，或 `seq ∈ S` 关联 `D5.primary_routes[]` 全路径 `job_regions` 仅含 `remote_field_site` | 任一旗标字段为 `null`（含 `seq ∈ S` 缺键）且 `seq ∈ S` 关联 `D5` 路径 `job_regions` 含 `"unknown"` |
| `strict_single_subject_or_lang_gate` | `effective_scenario_flags(S)` 含本项，或 `D2-D.subject_score_limits` 非空且考生单科未达标，或 `D2-D.foreign_language_limits` 非空且考生语种不符 | `D2-D.subject_score_limits == null`、`D2-D.foreign_language_limits == null`，或存在非空门槛但缺考生 `subject_scores` / `foreign_language` 输入导致无法排除 |
| `non_clinical_no_physician_exam` | `effective_scenario_flags(S)` 含本项，或 `seq ∈ S` 中医学门类专业在 `D5.primary_routes[]` 已核实不含 `"LIC_PHYSICIAN"` 执业医师报考资格 | 任一旗标字段为 `null`（含 `seq ∈ S` 缺键）且 `seq ∈ S` 关联 `D5` 路径 `license_ids == null` |

> 若阶段一未命中已确认违约，但上述任一红线核验字段或当年 `D2-D` 规则存在未知/缺失，则 `gate1_status = "PASS"` 且必须同时置 `unverified_redline_block_safety = true`、`safety_pool_blocked = true`（强制禁止入 `safety` 保底池）。

#### 阶段二：非红线组内 `water_level` 相对水位精算（仅对 `gate1_status == PASS` 执行）
1. **分位计算（严禁等权退化，与 [data/README.md §1](../data/README.md) 严格一致）**：
   - 仅当当年 `D2-D` 已核清实际可调剂范围（`rule_completeness == "complete"` 且 `adjustment_scope_mode != "unknown"`）、经 `D3-A` 核验跨年可比性，且实际可调剂范围内**全部成员专业**均具备完整的历史录取最低位次（`D2-B.major_min_rank` 非空，严禁直接拿不可比原始分跨年排序）与实际录取人数（`D2-B.admitted_count` 非空且 `> 0`）时，方可按录取人数加权计算考生位次 `student_rank` 在组内由高到低累积录取分布中的相对位置比例 `p ∈ [0, 1]`（数值越小位次越靠前）。
   - **缺失硬阻断规则**：只要实际可调剂范围内**任一成员**缺失 `major_min_rank` 或 `admitted_count`，或 `D2-D` 实际调剂范围未核清，**一律强制置 `water_level = "unknown"`、`water_level_percentile = null` 且 `safety_pool_blocked = true`**，严禁改用等权近似继续计算 `top/mid`（除非存在经独立审核明确批准的同口径可比替代证据，默认无）。
2. **水位五态判定（`water_level`）**：
   - `top`：`p <= 0.20`（组内前 20%，高概率直录组内高分目标专业）；
   - `mid`：`0.20 < p <= 0.50`（组内 20%–50%，中段水位，可能进目标也可能调剂至组内其他专业）；
   - `low`：`0.50 < p <= 0.80`（组内 50%–80%，大概率被调剂）；
   - `bottom`：`p > 0.80`（组内 80% 以后踩线位置，几乎必然被调剂）；
   - `unknown`：实际可调剂范围内任一成员缺 `major_min_rank` 或 `admitted_count`，或 `D2-D` 调剂范围未核清，**严禁虚构或等权估算分位**。
3. **客观混编结构标签（`mixed_structure_tags[]`，零主观加减分）**：
   - `contains_soft_dislike_major`（实际可调剂范围内含 `dim3.soft_dislike_majors` 成员）
   - `cross_discipline_mix`（组内专业跨 2 个及以上教育部学科门类）
   - `sino_foreign_mix`（同组混编普通专业与中外合作专业）
   - `high_tuition_mix`（同组不同专业学费极差超过 2 倍）
   - `transfer_restricted_present`（组内存在 `transfer_restriction` 为 `restricted` 或 `prohibited` 的专业）
   - `proxy_1b_degraded_present`（组内关联 D5/L3 条目处于 `proxy_1b_with_admissions_checklist` 降级态）
   - `unverified_redline_block_safety`（选科/体检/学费/单科外语或当年 `D2-D` 规则存在未知，已硬拦截出 `safety` 保底池）
4. **保底池准入与调剂建议映射**：

| `water_level` | 是否含 `soft_dislike` / 未知红线 | `safety_pool_blocked` | `allowed_pools` | `adjustment_advice` |
| --- | --- | --- | --- | --- |
| `top` | 均无 / 仅含 `soft_dislike`（无未知红线） | `false` | `["reach", "match", "safety"]` | `accept_adjustment`（高水位稳进目标，可服从调剂） |
| `mid` | 均无 | `false` | `["reach", "match", "safety"]` | `accept_with_contingency`（可进稳/保，附入校分流预案） |
| `mid` | 含 `soft_dislike`（无未知红线） | `false` | `["reach", "match"]` | `conditional_review`（进冲/稳并核验分流与转专业规则，谨慎作保底） |
| `low` / `bottom` | 均无 | `false` | `["reach", "match"]` | `accept_with_caution`（踩线仅作冲/稳，不建议作唯一保底） |
| `low` / `bottom` | 含 `soft_dislike` | **`true`（硬拦截）** | `["reach"]`（或建议回避） | `avoid_or_reach_only_high_risk`（严禁入保底池） |
| 任意 | 存在未知红线或当年 `D2-D` 未核全（`unverified_redline_block_safety=true`） | **`true`（硬拦截）** | `["unverified_manual_review"]` | `block_safety_until_redlines_verified`（红线或章程调剂规则未知严禁入保底池，须先核当年官方章程） |
| `unknown` | 任意（含任一可调剂成员缺位次或录取人数） | **`true`（硬拦截）** | `["unverified_manual_review"]` | `block_until_major_ranks_verified`（缺成员分位/录取人数或调剂范围未核清，严禁等权伪算，先线下核查） |

5. **跨专业逐配对四维主备独立性冲击核验（`backup_independence_check`，基于 `candidate_pair_bindings[]` × `D5.paired_primary_refs[]` × `D2-D`，`3.0.7`）**：
   - 仅证明“付款主体不同”不足以宣称备选独立；系统必须以 `D6Input.candidate_pair_bindings[]` 中的每一组 `(primary, backup)` 为单位，先执行**跨表引用完整性与可达性校验**及**共损对象前置合法性校验**，再按**正向白名单**与**唯一四级优先序**执行确定性四维冲击核验（彻底废除“否则→pass”兜底，且消除 `A5 / C / D / §2.4` 之间的优先级冲突）：
   - **枚举锁定**：
     - 单维状态（`payer` / `group_isolation` / `entry_gate_isolation` / `region_exposure`）：`pass` \| `fail` \| `unknown_blocked`
     - 总状态（`pair_status` 与全局 `backup_independence_check`）：`pass` \| `warn_shared_failure_points` \| `unknown_blocked`
   - **A. `candidate_pair_bindings[]` 跨表引用完整性与可达性硬规则（闭环 `#14 / #16 / #17`）**：
     1. **`pair_id` 与专业组存在性/合法性**：`pair_id` 在 `candidate_pair_bindings[]` 中必须全局唯一（重复 `pair_id` 视同相关配对 `binding_valid = false`）；两端归一化五元组键 `(target_year, track, batch, college_code, group_code)` 须存在且与 `D6Input` 一致、对应组满足 **`group_target_valid == true`**（无重复组键或非法 `T`）、`major_seq ∈ G` 须存在于目标年 `D2-B`，且两端所在专业组均未 `gate1_status == "VETOED"`；
     2. **`D2-B` 专业代码与大类映射校验**：若 `D2-B.is_broad_category == false`，绑定端 `moe_major_code` 须严格等于 `D2-B.moe_major_code`；若 `D2-B.is_broad_category == true`（如 `D2-B.moe_major_code == null`），`D2-B.raw_major_name` 须命中对应 `D5` 记录的 `broad_category_aliases`，且**除非该校该大类下全部分流候选专业均已逐一核验不引入共损或未知门槛，否则视同 `binding_valid = false`**；
     3. **`D5` 路径存在性与主备角色校验**：`moe_major_code` 须存在于 `D5`，`primary.route_id` 须匹配 `^{moe_major_code}-PRI-[0-9]{2,}$` 且存在于 `primary_routes[]`，`backup.route_id` 须匹配 `^{moe_major_code}-BKP-[0-9]{2,}$` 且存在于 `backup_routes[]`（主备角色写反或查无此路径一律视为引用非法）；
     4. **可达性约束**：两端 `major_seq` 必须属于考生在该组的主动填报集合 `T`（从而必有 `major_seq ∈ S`；**严禁将备选端绑在考生未填报且不接受调剂的不可达专业 `seq ∈ E \ T` 上**）；
     5. **违反处置（与 C、D、§2.4 严格统一）**：凡违反上述任一规则，记 **`binding_valid = false`**。维度层：`group_isolation` 必为 `"unknown_blocked"`；其余三个内在维（`payer`、`entry_gate_isolation`、`region_exposure`）若两端在 `D5` 可解析且命中确定性 `"fail"` 条件（如两端 `payer_type` 相同），**维度层保留 `"fail"` 并照常写入 `shared_single_points_of_failure[]`（不掩盖已知共损）**，未命中 `"fail"` 的内在维一律置 `"unknown_blocked"`。聚合层：**`binding_valid == false` 为最高优先级，无条件强制 `pair_status = "unknown_blocked"` 与全局 `backup_independence_check = "unknown_blocked"`**（并在 `unknown_reasons[]` 记录非法绑定根因，绝不被 `"warn_shared_failure_points"` 覆盖，亦绝不判 `"pass"`）。
   - **B. 配对共损对象前置合法性与双向一致性硬校验（闭环 `#13`）**：
     - 在 `backup_route.paired_primary_refs[]` 中精确匹配 `primary_major_code == primary.moe_major_code && primary_route_id == primary.route_id`，记为 `ref`；
     - `ref_schema_valid == true` **当且仅当**同时满足：① 命中唯一 `ref`（非临时未登记配对）；② `co_failure_status_by_dim` 为精确包含且仅包含 `{"payer", "entry_gate", "region_exposure"}` 三键的对象，每键值均属于 `{"isolated", "shared_fail", "unknown"}`（无缺键、无 `null`、无超枚举）；③ `shared_bottlenecks` 为非空合法枚举数组且满足双向一致性——仅三键全 `"isolated"` 方允许 `["none"]`（禁与其他值混用），任一 `"shared_fail"` 须含对应故障标签（`payer -> same_payer_pool`、`entry_gate -> same_degree_master_gate | same_license_gate`、`region_exposure -> same_region_cycle | same_org_type_exposure`）且不得为 `["none"]`，任一 `"unknown"` 须含 `"unknown"` 且不得含 `"none"`；
     - 凡临时未登记配对、缺键、`null`、超枚举或违反双向一致性（如 `co_failure_status_by_dim = {}` 却填 `shared_bottlenecks = ["none"]`），一律记 `ref_schema_valid = false`，**禁止任何内在维落入 `"pass"`**。
   - **C. 四维逐维正向白名单判定规则（闭环 `#13 / #14 / #17`：先判确定性 `fail`，再仅按正向白名单判 `pass`，其余一切情形一律 `unknown_blocked`）**：
     1. **`payer`（独立付款主体隔离）**：
        - **`"fail"`**：两端 `D5` 路径可解析且 `payer_type` 均合法非 `"unknown"` 且相同，或 `co_failure_status_by_dim.payer == "shared_fail"`，或 `"same_payer_pool" ∈ shared_bottlenecks`（即使 `binding_valid == false`，该已知共损仍保留在维度层与 `shared_single_points_of_failure[]`）；
        - **`"pass"`（正向白名单）**：`binding_valid == true`（大类已全量核验）、`ref_schema_valid == true`、两端 `gate_completeness == "complete"` 且 `payer_type` 均合法非 `"unknown"` 且互不相同、`co_failure_status_by_dim.payer == "isolated"`、`"same_payer_pool" ∉ shared_bottlenecks` 且无未窄化 `"unknown"`；
        - **其余一切情形**（含 `binding_valid == false` 且无已知 `fail`、缺键/`null`/非法 `ref`/临时配对/未窄化 `"unknown"`）→ **`"unknown_blocked"`**。
     2. **`group_isolation`（集合化院校专业组隔离，设主备两端组暴露集为 `S_1, S_2`、主动填报集为 `T_1, T_2`）**：
        - **引用/可达性前置阻断**：若 `binding_valid == false`（含 `group_target_valid == false`、`pair_id` 重复、代码不符、大类未全核、任一端所在组 `gate1_status == "VETOED"` 或任一端 `major_seq_i ∉ T_i` 如落在 `E_i \ T_i` 不可达）→ 立即 **`"unknown_blocked"`**；
        - **`"fail"`**：`binding_valid == true` 且同属 `(college_code, group_code)` 且两端 `major_seq` 均 `∈ S`（按 `#12` 修正后的 `S`），或 `"same_admission_group_risk" ∈ shared_bottlenecks`；
        - **`"pass"`（正向白名单）**：`binding_valid == true`（两端均未 `VETOED` 且 `major_seq_i ∈ T_i ⊆ S_i`）、两端分属不同 `(college_code, group_code)`、两端组当年 `D2-D` 均为 `rule_completeness == "complete"` 且 `adjustment_scope_mode != "unknown"`、**且两端组均未触发章程子集/书面承诺回退**（即 `subset_isolated_verified` 下须满足 `A != null && (A ∪ E) ⊆ G`，`no_adjustment_written_promise_verified` 下须满足书面生效条件）、`"same_admission_group_risk" ∉ shared_bottlenecks` 且无未窄化 `"unknown"`；
        - **其余一切情形**（含**未命中上述同组 `"fail"` 且**任一端触发章程 `A == null` / `(A ∪ E) ⊈ G` / 书面承诺回退，即使 `binding_valid == true`，亦由章程证据规则判为 `"unknown_blocked"`）→ **`"unknown_blocked"`**。
     3. **`entry_gate_isolation`（学历与执业执照门槛隔离）**：
        - **`"fail"`**：两端 `D5` 路径可解析且均属高门槛刚性学历（`master_mandatory` / `phd_or_residency_mandatory`），或两端非空 `license_ids` 存在交集（如共卡 `LIC_LEGAL_BAR` / `LIC_PHYSICIAN`），或 `co_failure_status_by_dim.entry_gate == "shared_fail"`，或 `"same_degree_master_gate" / "same_license_gate" ∈ shared_bottlenecks`（即使 `binding_valid == false` 亦保留已知 `"fail"`）；
        - **`"pass"`（正向白名单）**：`binding_valid == true`（大类已全量核验）、`ref_schema_valid == true`、两端 `gate_completeness == "complete"`、`degree_threshold` 均合法非 `"unknown"` 且未同为高门槛刚性学历、`license_ids` 均为非 `null` 数组且无交集、`co_failure_status_by_dim.entry_gate == "isolated"`、不含学历/执照共损标签且无未窄化 `"unknown"`；
        - **其余一切情形** → **`"unknown_blocked"`**。
     4. **`region_exposure`（目标就业地域与组织周期隔离）**：
        - **`"fail"`**：`co_failure_status_by_dim.region_exposure == "shared_fail"`，或 `"same_region_cycle" / "same_org_type_exposure" ∈ shared_bottlenecks`（即使 `binding_valid == false` 亦保留已知 `"fail"`）；
        - **`"pass"`（正向白名单）**：`binding_valid == true`（大类已全量核验）、`ref_schema_valid == true`、两端 `gate_completeness == "complete"`、`org_category` 均合法非 `"unknown"`、`job_regions` 均非空且不含 `"unknown"`、`co_failure_status_by_dim.region_exposure == "isolated"`、不含地域/组织共损标签且无未窄化 `"unknown"`；
        - **其余一切情形** → **`"unknown_blocked"`**。
   - **D. 未知共损与严格四级总状态聚合优先序（闭环 `#17`，统一 A5 / C / D / §2.4，严禁任何未知或非法结构聚合为 `pass`）**：
     - **未窄化 `"unknown"` 全维阻断**：对任一配对，只要 `shared_bottlenecks` 包含 `"unknown"` 而 `co_failure_status_by_dim` 未显式标出任何 `"unknown"` 维度（即仅填笼统 `["unknown"]` 未窄化），**所有未命中 `"fail"` 的维度一律强制置为 `"unknown_blocked"`**；
     - **单对 `pair_status` 严格四级优先序**：
       1. **优先级 1（最高）**：若 `binding_valid == false` → 无条件强制 **`pair_status = "unknown_blocked"`**（即使 `dimensions` 中并存已知 `"fail"` 维；`unknown_reasons[]` 必记录非法绑定根因，同时保留 `dimensions` 与 `shared_single_points_of_failure[]` 中的已知 `"fail"`）；
       2. **优先级 2**：`binding_valid == true` 且四维含任意 `"fail"` → `pair_status = "warn_shared_failure_points"`（并存的 `"unknown_blocked"` 维同步写入 `unknown_reasons[]`）；
       3. **优先级 3**：`binding_valid == true`、无 `"fail"` 但四维含任意 `"unknown_blocked"`（或 `ref_schema_valid == false` / `shared_bottlenecks` 含 `"unknown"`）→ `pair_status = "unknown_blocked"`（**绝对严禁返回 `"pass"`**）；
       4. **优先级 4**：`binding_valid == true` 且四维全部通过正向白名单为 `"pass"` → `pair_status = "pass"`；
     - **全局 `backup_independence_check` 跨配对严格四级优先序**：
       1. **优先级 1（最高）**：`candidate_pair_bindings[]` 为空、存在重复 `pair_id`，或**任一配对 `binding_valid == false`** → 全局强制 **`backup_independence_check = "unknown_blocked"`**（顶层 `independence_dimensions` 按跨配对维度最坏序 `"fail" > "unknown_blocked" > "pass"` 汇总，并完整保留 `shared_single_points_of_failure[]` 与 `unknown_independence_dimensions[]`）；
       2. **优先级 2**：非空、全部配对 `binding_valid == true` 且任一配对 `pair_status == "warn_shared_failure_points"` → 全局 `"warn_shared_failure_points"`；
       3. **优先级 3**：非空、全部配对 `binding_valid == true`、无 `"warn_shared_failure_points"` 且任一配对 `pair_status == "unknown_blocked"` → 全局 `"unknown_blocked"`；
       4. **优先级 4**：非空且全部配对 `binding_valid == true` 且 `pair_status == "pass"` → 全局 `"pass"`。

### 2.3 输出契约（`D6Output` JSON Schema 与八组最小反例 Fixture）

#### 2.3.1 标准输出示例（`D6Output`，`3.0.7`）

```json
{
  "schema_version": "3.0.7",
  "target_year": 2026,
  "case_id": "CASE-DEMO-001",
  "summary": {
    "evaluated_groups": 2,
    "vetoed_groups": 0,
    "passed_groups": 2,
    "safety_pool_blocked_groups": 0,
    "backup_independence_check": "warn_shared_failure_points",
    "independence_dimensions": {
      "payer": "pass",
      "group_isolation": "pass",
      "entry_gate_isolation": "pass",
      "region_exposure": "fail"
    },
    "unknown_independence_dimensions": [],
    "pair_independence_results": [
      {
        "pair_id": "PAIR-01",
        "primary": {
          "moe_major_code": "080601",
          "route_id": "080601-PRI-01",
          "college_code": "9901",
          "group_code": "02",
          "major_seq": 1
        },
        "backup": {
          "moe_major_code": "080601",
          "route_id": "080601-BKP-01",
          "college_code": "9904",
          "group_code": "01",
          "major_seq": 1
        },
        "pair_status": "warn_shared_failure_points",
        "dimensions": {
          "payer": "pass",
          "group_isolation": "pass",
          "entry_gate_isolation": "pass",
          "region_exposure": "fail"
        },
        "shared_bottlenecks": ["same_region_cycle"],
        "unknown_reasons": []
      }
    ],
    "shared_single_points_of_failure": [
      "PAIR-01 (080601/080601-PRI-01@9901-02 <-> 080601/080601-BKP-01@9904-01) [same_region_cycle]: 主攻电网运维与备选长三角工控装备制造均高度暴露于长三角电网投资节奏与区域用电增速周期"
    ],
    "covered_primary_payers": ["monopoly_soe_opex", "competitive_mfg_capex_rd"]
  },
  "group_evaluations": [
    {
      "college_code": "9901",
      "college_name": "示例理工大学",
      "group_code": "02",
      "target_year_rule_bound": 2026,
      "charter_version": "2026-official-v1",
      "adjustment_scope_mode": "subset_isolated_verified",
      "target_major_seqs": [1, 2],
      "adjustable_major_seqs": [1, 2],
      "excluded_major_seqs": [3],
      "evaluated_scope_seqs": [1, 2],
      "effective_scenario_flags": [],
      "tier_bucket_from_d4": "safety",
      "gate1_status": "PASS",
      "veto_reasons": [],
      "unverified_redline_block_safety": false,
      "water_level": "top",
      "water_level_percentile": 0.18,
      "water_level_completeness": "complete",
      "mixed_structure_tags": [
        "contains_soft_dislike_major",
        "cross_discipline_mix",
        "proxy_1b_degraded_present"
      ],
      "safety_pool_blocked": false,
      "allowed_pools": ["reach", "match", "safety"],
      "adjustment_advice": "accept_adjustment",
      "matched_routes": [
        {
          "role": "primary",
          "moe_major_code": "080601",
          "route_id": "080601-PRI-01",
          "major_seq": 1
        }
      ],
      "admissions_verification_questions": [
        "核实该校本专业近两届本科生进入电网及电力装备企业的人数占比与推免比例"
      ]
    },
    {
      "college_code": "9904",
      "college_name": "示例工业大学",
      "group_code": "01",
      "target_year_rule_bound": 2026,
      "charter_version": "2026-official-v1",
      "adjustment_scope_mode": "full_group_default",
      "target_major_seqs": [1],
      "adjustable_major_seqs": [1, 2],
      "excluded_major_seqs": [],
      "evaluated_scope_seqs": [1, 2],
      "effective_scenario_flags": [],
      "tier_bucket_from_d4": "safety",
      "gate1_status": "PASS",
      "veto_reasons": [],
      "unverified_redline_block_safety": false,
      "water_level": "top",
      "water_level_percentile": 0.15,
      "water_level_completeness": "complete",
      "mixed_structure_tags": [
        "proxy_1b_degraded_present"
      ],
      "safety_pool_blocked": false,
      "allowed_pools": ["reach", "match", "safety"],
      "adjustment_advice": "accept_adjustment",
      "matched_routes": [
        {
          "role": "backup",
          "moe_major_code": "080601",
          "route_id": "080601-BKP-01",
          "major_seq": 1
        }
      ],
      "admissions_verification_questions": [
        "核实该校电气工程及其自动化专业工控方向实验学分占比及长三角装备制造企业校招名单"
      ]
    }
  ],
  "warnings": []
}
```

#### 2.3.2 最小契约验证反例集（Fixture A / B / B′ / C / C′ / D / E / F，闭环 `#9–#19`）

> 以下八组 `[虚构契约验证 Fixture]` 统一使用复数数组 `paired_primary_refs[]` 与 `candidate_group_targets[]`，保留 `Fixture A–E` 原例，新增 `Fixture F` 验证多合法配对下“单对 `pair_status` 与全局 `backup_independence_check` 严格分离”（`#19`），并附 `#18` 章程 `A=null` 与 `group_target_valid=true` 分离对照说明：

**Fixture A（`#9 / #14`｜跨专业、不同付款人，但共卡 `LIC_LEGAL_BAR` 且同处未隔离组 `9902-04` → 必判 `fail`）**：

```json
{
  "fixture_id": "FIXTURE-A-CROSS-MAJOR-CO-FAILURE",
  "schema_version": "3.0.7",
  "input": {
    "candidate_group_targets": [
      {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9902",
        "group_code": "04",
        "target_major_seqs": [1, 2]
      }
    ],
    "d2b_majors": {
      "9902-04": [
        {"major_seq": 1, "moe_major_code": "030101K", "is_broad_category": false},
        {"major_seq": 2, "moe_major_code": "030102T", "is_broad_category": false}
      ]
    },
    "pair_binding": {
      "pair_id": "PAIR-FIX-A",
      "primary": {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9902",
        "group_code": "04",
        "major_seq": 1,
        "moe_major_code": "030101K",
        "route_id": "030101K-PRI-01"
      },
      "backup": {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9902",
        "group_code": "04",
        "major_seq": 2,
        "moe_major_code": "030102T",
        "route_id": "030102T-BKP-01"
      }
    },
    "d5_routes": {
      "primary": {
        "moe_major_code": "030101K",
        "route_id": "030101K-PRI-01",
        "payer_type": "local_fiscal",
        "org_category": "gov_judicial_org",
        "job_regions": ["jiangsu_local", "yrd_cluster"],
        "degree_threshold": "master_recommended",
        "license_ids": ["LIC_LEGAL_BAR"],
        "gate_completeness": "complete"
      },
      "backup": {
        "moe_major_code": "030102T",
        "route_id": "030102T-BKP-01",
        "payer_type": "competitive_mfg_capex_rd",
        "org_category": "listed_private_mfg",
        "job_regions": ["jiangsu_local", "yrd_cluster"],
        "degree_threshold": "master_recommended",
        "license_ids": ["LIC_LEGAL_BAR"],
        "gate_completeness": "complete",
        "paired_primary_refs": [
          {
            "primary_major_code": "030101K",
            "primary_route_id": "030101K-PRI-01",
            "co_failure_status_by_dim": {
              "payer": "isolated",
              "entry_gate": "shared_fail",
              "region_exposure": "shared_fail"
            },
            "shared_bottlenecks": ["same_license_gate", "same_region_cycle"],
            "shared_failure_notes": "跨专业但共卡 LIC_LEGAL_BAR 且同处长三角周期"
          }
        ]
      }
    },
    "d2d_rule_9902_04": {
      "target_year": 2026,
      "college_code": "9902",
      "group_code": "04",
      "adjustment_scope_mode": "full_group_default",
      "adjustable_major_seqs": [1, 2],
      "excluded_major_seqs": [],
      "rule_completeness": "complete"
    }
  },
  "expected_output": {
    "pair_id": "PAIR-FIX-A",
    "primary": {
      "moe_major_code": "030101K",
      "route_id": "030101K-PRI-01",
      "college_code": "9902",
      "group_code": "04",
      "major_seq": 1
    },
    "backup": {
      "moe_major_code": "030102T",
      "route_id": "030102T-BKP-01",
      "college_code": "9902",
      "group_code": "04",
      "major_seq": 2
    },
    "dimensions": {
      "payer": "pass",
      "group_isolation": "fail",
      "entry_gate_isolation": "fail",
      "region_exposure": "fail"
    },
    "pair_status": "warn_shared_failure_points",
    "backup_independence_check": "warn_shared_failure_points",
    "shared_bottlenecks": ["same_admission_group_risk", "same_license_gate", "same_region_cycle"],
    "unknown_reasons": []
  }
}
```

**Fixture B（`#10`｜单路径 `gate_completeness: "complete"`、异组、异付款、无执照交集，但 `shared_bottlenecks: ["unknown"]` → 必返 `unknown_blocked`，绝不聚合成 `pass`）**：

```json
{
  "fixture_id": "FIXTURE-B-UNKNOWN-CO-FAILURE-NO-PASS",
  "schema_version": "3.0.7",
  "input": {
    "candidate_group_targets": [
      {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9901",
        "group_code": "02",
        "target_major_seqs": [1, 2]
      },
      {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9903",
        "group_code": "05",
        "target_major_seqs": [1]
      }
    ],
    "d2b_majors": {
      "9901-02": [
        {"major_seq": 1, "moe_major_code": "080601", "is_broad_category": false},
        {"major_seq": 2, "moe_major_code": "080401", "is_broad_category": false},
        {"major_seq": 3, "moe_major_code": "080701", "is_broad_category": false}
      ],
      "9903-05": [
        {"major_seq": 1, "moe_major_code": "080801", "is_broad_category": false},
        {"major_seq": 2, "moe_major_code": "080202", "is_broad_category": false}
      ]
    },
    "pair_binding": {
      "pair_id": "PAIR-FIX-B",
      "primary": {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9901",
        "group_code": "02",
        "major_seq": 1,
        "moe_major_code": "080601",
        "route_id": "080601-PRI-01"
      },
      "backup": {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9903",
        "group_code": "05",
        "major_seq": 1,
        "moe_major_code": "080801",
        "route_id": "080801-BKP-01"
      }
    },
    "d5_routes": {
      "primary": {
        "moe_major_code": "080601",
        "route_id": "080601-PRI-01",
        "payer_type": "monopoly_soe_opex",
        "org_category": "grid_energy_soe",
        "job_regions": ["jiangsu_local", "yrd_cluster"],
        "degree_threshold": "bachelor_direct",
        "license_ids": [],
        "gate_completeness": "complete"
      },
      "backup": {
        "moe_major_code": "080801",
        "route_id": "080801-BKP-01",
        "payer_type": "competitive_mfg_capex_rd",
        "org_category": "listed_private_mfg",
        "job_regions": ["national_mobile"],
        "degree_threshold": "bachelor_direct",
        "license_ids": [],
        "gate_completeness": "complete",
        "paired_primary_refs": [
          {
            "primary_major_code": "080601",
            "primary_route_id": "080601-PRI-01",
            "co_failure_status_by_dim": {
              "payer": "isolated",
              "entry_gate": "isolated",
              "region_exposure": "unknown"
            },
            "shared_bottlenecks": ["unknown"],
            "shared_failure_notes": "待核两路径承接行业在区域宏观投资周期上的联动相关性"
          }
        ]
      }
    },
    "d2d_rules": {
      "9901-02": {
        "adjustment_scope_mode": "subset_isolated_verified",
        "adjustable_major_seqs": [1, 2],
        "excluded_major_seqs": [3],
        "rule_completeness": "complete"
      },
      "9903-05": {
        "adjustment_scope_mode": "full_group_default",
        "adjustable_major_seqs": [1, 2],
        "excluded_major_seqs": [],
        "rule_completeness": "complete"
      }
    }
  },
  "expected_output": {
    "pair_id": "PAIR-FIX-B",
    "dimensions": {
      "payer": "pass",
      "group_isolation": "pass",
      "entry_gate_isolation": "pass",
      "region_exposure": "unknown_blocked"
    },
    "pair_status": "unknown_blocked",
    "backup_independence_check": "unknown_blocked",
    "unknown_independence_dimensions": ["region_exposure"],
    "unknown_reasons": [
      "region_exposure: co_failure_status_by_dim.region_exposure == 'unknown' 且 shared_bottlenecks 含 'unknown'"
    ]
  }
}
```

**Fixture B′（`#13`｜`co_failure_status_by_dim: {}` 缺键且填 `shared_bottlenecks: ["none"]` → 正向白名单拦截，内在三维与 `pair_status` 必返 `unknown_blocked`，绝不返 `pass`）**：

```json
{
  "fixture_id": "FIXTURE-B-PRIME-MALFORMED-CO-FAILURE-NO-PASS",
  "schema_version": "3.0.7",
  "input": {
    "candidate_group_targets": [
      {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9901",
        "group_code": "02",
        "target_major_seqs": [1, 2]
      },
      {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9903",
        "group_code": "05",
        "target_major_seqs": [1]
      }
    ],
    "d2b_majors": {
      "9901-02": [
        {"major_seq": 1, "moe_major_code": "080601", "is_broad_category": false},
        {"major_seq": 2, "moe_major_code": "080401", "is_broad_category": false},
        {"major_seq": 3, "moe_major_code": "080701", "is_broad_category": false}
      ],
      "9903-05": [
        {"major_seq": 1, "moe_major_code": "080801", "is_broad_category": false},
        {"major_seq": 2, "moe_major_code": "080202", "is_broad_category": false}
      ]
    },
    "pair_binding": {
      "pair_id": "PAIR-FIX-B-PRIME",
      "primary": {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9901",
        "group_code": "02",
        "major_seq": 1,
        "moe_major_code": "080601",
        "route_id": "080601-PRI-01"
      },
      "backup": {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9903",
        "group_code": "05",
        "major_seq": 1,
        "moe_major_code": "080801",
        "route_id": "080801-BKP-01"
      }
    },
    "d5_routes": {
      "primary": {
        "moe_major_code": "080601",
        "route_id": "080601-PRI-01",
        "payer_type": "monopoly_soe_opex",
        "org_category": "grid_energy_soe",
        "job_regions": ["jiangsu_local", "yrd_cluster"],
        "degree_threshold": "bachelor_direct",
        "license_ids": [],
        "gate_completeness": "complete"
      },
      "backup": {
        "moe_major_code": "080801",
        "route_id": "080801-BKP-01",
        "payer_type": "competitive_mfg_capex_rd",
        "org_category": "listed_private_mfg",
        "job_regions": ["national_mobile"],
        "degree_threshold": "bachelor_direct",
        "license_ids": [],
        "gate_completeness": "complete",
        "paired_primary_refs": [
          {
            "primary_major_code": "080601",
            "primary_route_id": "080601-PRI-01",
            "co_failure_status_by_dim": {},
            "shared_bottlenecks": ["none"],
            "shared_failure_notes": null
          }
        ]
      }
    },
    "d2d_rules": {
      "9901-02": {
        "adjustment_scope_mode": "subset_isolated_verified",
        "adjustable_major_seqs": [1, 2],
        "excluded_major_seqs": [3],
        "rule_completeness": "complete"
      },
      "9903-05": {
        "adjustment_scope_mode": "full_group_default",
        "adjustable_major_seqs": [1, 2],
        "excluded_major_seqs": [],
        "rule_completeness": "complete"
      }
    }
  },
  "expected_output": {
    "pair_id": "PAIR-FIX-B-PRIME",
    "dimensions": {
      "payer": "unknown_blocked",
      "group_isolation": "pass",
      "entry_gate_isolation": "unknown_blocked",
      "region_exposure": "unknown_blocked"
    },
    "pair_status": "unknown_blocked",
    "backup_independence_check": "unknown_blocked",
    "unknown_independence_dimensions": ["payer", "entry_gate_isolation", "region_exposure"],
    "unknown_reasons": [
      "ref_schema_invalid: co_failure_status_by_dim 缺键且与 shared_bottlenecks=['none'] 矛盾，禁止内在三维通过正向白名单判 pass"
    ]
  }
}
```

**Fixture C（`#11`｜`T=[1,2], A=[1,2], E=[3]`，`major_seq=3` 未主动填报且书面排除调剂 → `S = [1,2] ∪ ([1,2] \ [3]) = [1,2]`，`effective_scenario_flags=[]`，`gate1_status="PASS"` 不误否决）**：

```json
{
  "fixture_id": "FIXTURE-C-EXCLUDED-SEQ-SCENARIO-PROJECTION",
  "schema_version": "3.0.7",
  "input": {
    "hard_redline_scenarios": ["prohibited_transfer_sino_foreign"],
    "d2b_group_seqs": [1, 2, 3],
    "candidate_group_targets": [
      {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9901",
        "group_code": "02",
        "target_major_seqs": [1, 2]
      }
    ],
    "d2d_rule_9901_02": {
      "target_year": 2026,
      "college_code": "9901",
      "group_code": "02",
      "adjustment_scope_mode": "subset_isolated_verified",
      "adjustable_major_seqs": [1, 2],
      "excluded_major_seqs": [3],
      "subject_score_limits": {},
      "foreign_language_limits": [],
      "group_wide_scenario_flags": [],
      "member_scenario_flags_by_seq": {
        "1": [],
        "2": [],
        "3": ["prohibited_transfer_sino_foreign"]
      },
      "rule_completeness": "complete"
    }
  },
  "expected_output": {
    "evaluated_scope_seqs": [1, 2],
    "excluded_major_seqs": [3],
    "effective_scenario_flags": [],
    "gate1_status": "PASS",
    "veto_reasons": [],
    "unverified_redline_block_safety": false,
    "safety_pool_blocked": false
  }
}
```

**Fixture C′（`#12`｜`T=[1,3], A=[1,2], E=[3]`，考生主动填报了书面排除调剂的 `major_seq=3` 且其触碰红线 → `S = [1,3] ∪ ([1,2] \ [3]) = [1,2,3]`，必判 `VETOED`）**：

```json
{
  "fixture_id": "FIXTURE-C-PRIME-TARGETED-EXCLUDED-SEQ-VETO",
  "schema_version": "3.0.7",
  "input": {
    "hard_redline_scenarios": ["prohibited_transfer_sino_foreign"],
    "d2b_group_seqs": [1, 2, 3],
    "candidate_group_targets": [
      {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9901",
        "group_code": "02",
        "target_major_seqs": [1, 3]
      }
    ],
    "d2d_rule_9901_02": {
      "target_year": 2026,
      "college_code": "9901",
      "group_code": "02",
      "adjustment_scope_mode": "subset_isolated_verified",
      "adjustable_major_seqs": [1, 2],
      "excluded_major_seqs": [3],
      "subject_score_limits": {},
      "foreign_language_limits": [],
      "group_wide_scenario_flags": [],
      "member_scenario_flags_by_seq": {
        "1": [],
        "2": [],
        "3": ["prohibited_transfer_sino_foreign"]
      },
      "rule_completeness": "complete"
    }
  },
  "expected_output": {
    "evaluated_scope_seqs": [1, 2, 3],
    "excluded_major_seqs": [3],
    "effective_scenario_flags": ["prohibited_transfer_sino_foreign"],
    "gate1_status": "VETOED",
    "veto_reasons": ["VETO_HARD_REDLINE_MAJOR"],
    "unverified_redline_block_safety": false,
    "safety_pool_blocked": true
  }
}
```

**Fixture D（`#16`｜`candidate_group_targets[]` 同组键重复冲突：`[1,2]` 与 `[1,3]` 并存 → 无论正序或逆序均确定性判 `group_target_valid=false`、回退 `S=[1,2,3]` 触发 `VETOED` 且 `water_level="unknown"` / `safety_pool_blocked=true`）**：

```json
{
  "fixture_id": "FIXTURE-D-DUPLICATE-GROUP-TARGET-CONFLICT",
  "schema_version": "3.0.7",
  "input": {
    "target_year": 2026,
    "track": "physics",
    "hard_redline_scenarios": ["prohibited_transfer_sino_foreign"],
    "d2b_group_seqs": [1, 2, 3],
    "candidate_group_targets": [
      {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9901",
        "group_code": "02",
        "target_major_seqs": [1, 2]
      },
      {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9901",
        "group_code": "02",
        "target_major_seqs": [1, 3]
      }
    ],
    "d2d_rule_9901_02": {
      "target_year": 2026,
      "college_code": "9901",
      "group_code": "02",
      "adjustment_scope_mode": "subset_isolated_verified",
      "adjustable_major_seqs": [1, 2],
      "excluded_major_seqs": [3],
      "subject_score_limits": {},
      "foreign_language_limits": [],
      "group_wide_scenario_flags": [],
      "member_scenario_flags_by_seq": {
        "1": [],
        "2": [],
        "3": ["prohibited_transfer_sino_foreign"]
      },
      "rule_completeness": "complete"
    }
  },
  "expected_output": {
    "group_target_valid": false,
    "evaluated_scope_seqs": [1, 2, 3],
    "effective_scenario_flags": ["prohibited_transfer_sino_foreign"],
    "gate1_status": "VETOED",
    "veto_reasons": ["VETO_HARD_REDLINE_MAJOR"],
    "unverified_redline_block_safety": true,
    "water_level": "unknown",
    "water_level_percentile": null,
    "safety_pool_blocked": true
  }
}
```

**Fixture E（`#17`｜非法绑定 `binding_valid=false` 与已知 `payer="fail"` 并存 → 维度层保留 `payer="fail"` 进故障清单，聚合层最高优先级强制 `pair_status="unknown_blocked"` 与 `backup_independence_check="unknown_blocked"`）**：

```json
{
  "fixture_id": "FIXTURE-E-INVALID-BINDING-WITH-SAME-PAYER",
  "schema_version": "3.0.7",
  "input": {
    "target_year": 2026,
    "track": "physics",
    "candidate_group_targets": [
      {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9902",
        "group_code": "04",
        "target_major_seqs": [1]
      },
      {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9903",
        "group_code": "05",
        "target_major_seqs": [1]
      }
    ],
    "d2b_majors": {
      "9902-04": [
        {"major_seq": 1, "moe_major_code": "030101K", "is_broad_category": false}
      ],
      "9903-05": [
        {"major_seq": 1, "moe_major_code": "080801", "is_broad_category": false}
      ]
    },
    "pair_binding": {
      "pair_id": "PAIR-FIX-E",
      "primary": {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9902",
        "group_code": "04",
        "major_seq": 1,
        "moe_major_code": "030101K",
        "route_id": "030101K-PRI-01"
      },
      "backup": {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9903",
        "group_code": "05",
        "major_seq": 1,
        "moe_major_code": "030102T",
        "route_id": "030102T-BKP-02"
      }
    },
    "d5_routes": {
      "primary": {
        "moe_major_code": "030101K",
        "route_id": "030101K-PRI-01",
        "payer_type": "local_fiscal",
        "org_category": "gov_judicial_org",
        "job_regions": ["jiangsu_local", "yrd_cluster"],
        "degree_threshold": "master_recommended",
        "license_ids": ["LIC_LEGAL_BAR"],
        "gate_completeness": "complete"
      },
      "backup": {
        "moe_major_code": "030102T",
        "route_id": "030102T-BKP-02",
        "payer_type": "local_fiscal",
        "org_category": "gov_judicial_org",
        "job_regions": ["national_mobile"],
        "degree_threshold": "bachelor_direct",
        "license_ids": [],
        "gate_completeness": "complete",
        "paired_primary_refs": [
          {
            "primary_major_code": "030101K",
            "primary_route_id": "030101K-PRI-01",
            "co_failure_status_by_dim": {
              "payer": "shared_fail",
              "entry_gate": "isolated",
              "region_exposure": "isolated"
            },
            "shared_bottlenecks": ["same_payer_pool"],
            "shared_failure_notes": "主备两端付款主体均为 local_fiscal"
          }
        ]
      }
    },
    "d2d_rules": {
      "9902-04": {
        "adjustment_scope_mode": "full_group_default",
        "adjustable_major_seqs": [1],
        "excluded_major_seqs": [],
        "rule_completeness": "complete"
      },
      "9903-05": {
        "adjustment_scope_mode": "full_group_default",
        "adjustable_major_seqs": [1],
        "excluded_major_seqs": [],
        "rule_completeness": "complete"
      }
    }
  },
  "expected_output": {
    "pair_id": "PAIR-FIX-E",
    "binding_valid": false,
    "dimensions": {
      "payer": "fail",
      "group_isolation": "unknown_blocked",
      "entry_gate_isolation": "unknown_blocked",
      "region_exposure": "unknown_blocked"
    },
    "pair_status": "unknown_blocked",
    "backup_independence_check": "unknown_blocked",
    "shared_single_points_of_failure": [
      "PAIR-FIX-E [same_payer_pool]: 主备两端付款主体均为 local_fiscal"
    ],
    "unknown_independence_dimensions": [
      "group_isolation",
      "entry_gate_isolation",
      "region_exposure"
    ],
    "unknown_reasons": [
      "binding_invalid: backup 端绑定 moe_major_code='030102T' 与目标年 D2-B (9903-05 seq=1) 实际代码 '080801' 不符"
    ]
  }
}
```

**Fixture F（`#19`｜双合法配对并存：`P` 仅未知无 `fail` + `Q` 含已知 `fail` → 严格分离单对与全局状态：`P="unknown_blocked"`、`Q="warn_shared_failure_points"`、全局 `"warn_shared_failure_points"`）**：

```json
{
  "fixture_id": "FIXTURE-F-MULTI-PAIR-SCOPE-SEPARATION",
  "schema_version": "3.0.7",
  "input": {
    "target_year": 2026,
    "track": "physics",
    "candidate_group_targets": [
      {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9901",
        "group_code": "02",
        "target_major_seqs": [1, 2]
      },
      {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9903",
        "group_code": "05",
        "target_major_seqs": [1]
      },
      {
        "target_year": 2026,
        "batch": "undergrad_regular",
        "college_code": "9902",
        "group_code": "04",
        "target_major_seqs": [1, 2]
      }
    ],
    "d2b_majors": {
      "9901-02": [
        {"major_seq": 1, "moe_major_code": "080601", "is_broad_category": false},
        {"major_seq": 2, "moe_major_code": "080401", "is_broad_category": false},
        {"major_seq": 3, "moe_major_code": "080701", "is_broad_category": false}
      ],
      "9903-05": [
        {"major_seq": 1, "moe_major_code": "080801", "is_broad_category": false},
        {"major_seq": 2, "moe_major_code": "080202", "is_broad_category": false}
      ],
      "9902-04": [
        {"major_seq": 1, "moe_major_code": "030101K", "is_broad_category": false},
        {"major_seq": 2, "moe_major_code": "030102T", "is_broad_category": false}
      ]
    },
    "candidate_pair_bindings": [
      {
        "pair_id": "PAIR-FIX-F-P",
        "primary": {
          "target_year": 2026,
          "batch": "undergrad_regular",
          "college_code": "9901",
          "group_code": "02",
          "major_seq": 1,
          "moe_major_code": "080601",
          "route_id": "080601-PRI-01"
        },
        "backup": {
          "target_year": 2026,
          "batch": "undergrad_regular",
          "college_code": "9903",
          "group_code": "05",
          "major_seq": 1,
          "moe_major_code": "080801",
          "route_id": "080801-BKP-01"
        }
      },
      {
        "pair_id": "PAIR-FIX-F-Q",
        "primary": {
          "target_year": 2026,
          "batch": "undergrad_regular",
          "college_code": "9902",
          "group_code": "04",
          "major_seq": 1,
          "moe_major_code": "030101K",
          "route_id": "030101K-PRI-01"
        },
        "backup": {
          "target_year": 2026,
          "batch": "undergrad_regular",
          "college_code": "9902",
          "group_code": "04",
          "major_seq": 2,
          "moe_major_code": "030102T",
          "route_id": "030102T-BKP-01"
        }
      }
    ],
    "d5_routes_by_pair": {
      "PAIR-FIX-F-P": {
        "primary": {
          "moe_major_code": "080601",
          "route_id": "080601-PRI-01",
          "payer_type": "monopoly_soe_opex",
          "org_category": "grid_energy_soe",
          "job_regions": ["jiangsu_local", "yrd_cluster"],
          "degree_threshold": "bachelor_direct",
          "license_ids": [],
          "gate_completeness": "complete"
        },
        "backup": {
          "moe_major_code": "080801",
          "route_id": "080801-BKP-01",
          "payer_type": "competitive_mfg_capex_rd",
          "org_category": "listed_private_mfg",
          "job_regions": ["national_mobile"],
          "degree_threshold": "bachelor_direct",
          "license_ids": [],
          "gate_completeness": "complete",
          "paired_primary_refs": [
            {
              "primary_major_code": "080601",
              "primary_route_id": "080601-PRI-01",
              "co_failure_status_by_dim": {
                "payer": "isolated",
                "entry_gate": "isolated",
                "region_exposure": "unknown"
              },
              "shared_bottlenecks": ["unknown"],
              "shared_failure_notes": "仅 P 存在区域周期未知，无已知 fail"
            }
          ]
        }
      },
      "PAIR-FIX-F-Q": {
        "primary": {
          "moe_major_code": "030101K",
          "route_id": "030101K-PRI-01",
          "payer_type": "local_fiscal",
          "org_category": "gov_judicial_org",
          "job_regions": ["jiangsu_local", "yrd_cluster"],
          "degree_threshold": "master_recommended",
          "license_ids": ["LIC_LEGAL_BAR"],
          "gate_completeness": "complete"
        },
        "backup": {
          "moe_major_code": "030102T",
          "route_id": "030102T-BKP-01",
          "payer_type": "competitive_mfg_capex_rd",
          "org_category": "listed_private_mfg",
          "job_regions": ["jiangsu_local", "yrd_cluster"],
          "degree_threshold": "master_recommended",
          "license_ids": ["LIC_LEGAL_BAR"],
          "gate_completeness": "complete",
          "paired_primary_refs": [
            {
              "primary_major_code": "030101K",
              "primary_route_id": "030101K-PRI-01",
              "co_failure_status_by_dim": {
                "payer": "isolated",
                "entry_gate": "shared_fail",
                "region_exposure": "shared_fail"
              },
              "shared_bottlenecks": ["same_license_gate", "same_region_cycle"],
              "shared_failure_notes": "仅 Q 存在同组与共执照/区域共损"
            }
          ]
        }
      }
    },
    "d2d_rules": {
      "9901-02": {
        "adjustment_scope_mode": "subset_isolated_verified",
        "adjustable_major_seqs": [1, 2],
        "excluded_major_seqs": [3],
        "rule_completeness": "complete"
      },
      "9903-05": {
        "adjustment_scope_mode": "full_group_default",
        "adjustable_major_seqs": [1, 2],
        "excluded_major_seqs": [],
        "rule_completeness": "complete"
      },
      "9902-04": {
        "adjustment_scope_mode": "full_group_default",
        "adjustable_major_seqs": [1, 2],
        "excluded_major_seqs": [],
        "rule_completeness": "complete"
      }
    }
  },
  "expected_output": {
    "pair_independence_results": [
      {
        "pair_id": "PAIR-FIX-F-P",
        "binding_valid": true,
        "dimensions": {
          "payer": "pass",
          "group_isolation": "pass",
          "entry_gate_isolation": "pass",
          "region_exposure": "unknown_blocked"
        },
        "pair_status": "unknown_blocked"
      },
      {
        "pair_id": "PAIR-FIX-F-Q",
        "binding_valid": true,
        "dimensions": {
          "payer": "pass",
          "group_isolation": "fail",
          "entry_gate_isolation": "fail",
          "region_exposure": "fail"
        },
        "pair_status": "warn_shared_failure_points"
      }
    ],
    "backup_independence_check": "warn_shared_failure_points",
    "independence_dimensions": {
      "payer": "pass",
      "group_isolation": "fail",
      "entry_gate_isolation": "fail",
      "region_exposure": "fail"
    },
    "unknown_independence_dimensions": ["region_exposure"]
  }
}
```

> **`#18` 章程回退与填报合法性分离对照说明**：当单组 `T = [1]` 满足五元组唯一键与去重校验（`G = [1, 2, 3]`），但 `subset_isolated_verified` 章程记录中 `adjustable_major_seqs = null`（`A = null`）时，正文 §2.2.1、§2.2 C.2 与 §2.4 异常表同解为：`group_target_valid = true`（不伪造为考生填报非法）、回退 `S = [1, 2, 3]`、`unverified_redline_block_safety = true`、`water_level = "unknown"`、`water_level_percentile = null`、`safety_pool_blocked = true`；若该组被合法配对引用，则 `binding_valid = true`，并严格区分两类合法配对：① 若两端同属同一 `(college_code, group_code)` 且两端 `major_seq ∈ S`（或含 `same_admission_group_risk`），按 §2.2 C.2 优先判 `group_isolation = "fail"`；② 若两端跨组且无 `same_admission_group_risk`，则由章程证据规则令 `group_isolation = "unknown_blocked"`（绝不判 `"pass"`）。

### 2.4 边界与异常处置（D6）

| 异常情形 | 处置规则 |
| --- | --- |
| 同一专业同时出现在 `hard_redline_majors` 与 `soft_dislike_majors` | 硬红线优先（按 `hard_redline` 处理并输出 `CONFLICTING_MAJOR_PREFERENCE` 警告） |
| 考生填报集合非法：待评专业组缺失 `candidate_group_targets[]` 条目、按归一化五元组键出现 `>= 2` 条重复组记录、或 `target_major_seqs` 含重复元素/为空/非正整数/越界 `⊈ G` / `target_year` 不符 | **仅此类考生填报缺陷**判定 `group_target_valid = false`，**严禁取首项或末项**，与数组顺序无关地强制令 `S = G` 执行全量红线扫描，且无论阶段一是否 `VETOED` 均强制置 `unverified_redline_block_safety = true`、`water_level = "unknown"`、`water_level_percentile = null`、`safety_pool_blocked = true`；引用该组的 `candidate_pair_bindings[]` 端点自动置 `binding_valid = false` |
| 章程调剂证据不完整（考生填报合法 `group_target_valid == true`）：缺失当年 `D2-D` 记录、`adjustment_scope_mode == "unknown"`、`rule_completeness != "complete"`、`subset_isolated_verified` 下 `A == null` 或 `(A ∪ E) ⊈ G`，或 `no_adjustment_written_promise_verified` 未满足书面生效条件 | **保留 `group_target_valid = true`**（不伪造为考生填报非法，亦不因此置 `binding_valid = false`）；按 §2.2.1 回退 `S = G` 全组最坏暴露执行红线扫描，强制置 `unverified_redline_block_safety = true`、`water_level = "unknown"`、`water_level_percentile = null`、`safety_pool_blocked = true`；若该组被合法配对引用，按 §2.2 C.2 **保留已知同组共损优先**（同属 `(college_code, group_code)` 且两端 `major_seq ∈ S` 或含 `same_admission_group_risk` 则 `group_isolation = "fail"`），**否则（未命中同组 `"fail"` 时）**令 `group_isolation = "unknown_blocked"`（绝不判 `"pass"`） |
| 选科、体检限报条款、学费、学制、`D2-D.group_wide_scenario_flags` / `member_scenario_flags_by_seq`（含任意 `seq ∈ S` 缺键或 `null`） / `subject_score_limits` / `foreign_language_limits` 为未知，或缺考生单科/语种输入无法排除限报 | 标记 `unverified_redline_block_safety = true` 且 `safety_pool_blocked = true`，**严禁默认放行进 `safety` 保底池** |
| 实际暴露集合 `S` 内任一成员缺失 `major_min_rank` 或 `admitted_count` | 强制置 `water_level = "unknown"`、`water_level_percentile = null` 且 `safety_pool_blocked = true`，**严禁改用等权伪算 `top/mid`** |
| `candidate_pair_bindings[]` 为空、`pair_id` 重复，或任一端违反跨表引用完整性（专业代码不匹配、大类未逐一核验、路径不存在或角色写反、引用 `group_target_valid == false` 的组）、所在组 `VETOED` 或落在不可达专业 `seq ∉ T`（含 `E \ T`） | 置 `binding_valid = false`：`group_isolation` 必为 `"unknown_blocked"`，三个内在维若命中确定性 `"fail"` 则保留 `"fail"` 进 `dimensions` 与 `shared_single_points_of_failure[]`、其余置 `"unknown_blocked"`；**聚合层按 §2.2 D 最高优先级 1 强制本对 `pair_status = "unknown_blocked"` 与全局 `backup_independence_check = "unknown_blocked"`**（在 `unknown_reasons[]` 记非法绑定根因） |
| 单对 `binding_valid == true` 且本对四维存在任意 `"unknown_blocked"`（含 `co_failure_status_by_dim` 缺键/`null`/超枚举、双向一致性冲突、`gate_completeness == "unknown"`、`degree_threshold == "unknown"`、`license_ids == null`、章程证据不完整/回退、`shared_bottlenecks` 含 `"unknown"` 或临时未登记配对） | **单对与全局严格分离**：按 §2.2 D 单对优先序**仅读本配对自身四维**——本对无已知 `"fail"` 时本对 `pair_status` 必为 `"unknown_blocked"`（**绝不因其他配对的 `"fail"` 将本对改标为 `"warn_shared_failure_points"`**）；本对自身并存已知 `"fail"` 时本对 `pair_status` 为 `"warn_shared_failure_points"` 并在本对 `unknown_reasons[]` 列明未知维。全局 `backup_independence_check` 在汇总全部配对后另行按 §2.2 D 全局四级优先序计算 |
| 单对 `binding_valid == true` 且本对四维含 `>= 1` 项已知 `"fail"`；或多配对汇总（全部配对 `binding_valid == true`）存在至少 1 对 `pair_status == "warn_shared_failure_points"` | **单对层面**：仅将该含 `"fail"` 配对的 `pair_status` 置为 `"warn_shared_failure_points"` 并在 `shared_single_points_of_failure[]` 逐对明示（其他无 `"fail"` 且含未知的合法配对维持各自 `pair_status = "unknown_blocked"`）；**全局层面**：仅当全部配对均 `binding_valid == true` 且至少 1 对为 `"warn_shared_failure_points"` 时，全局 `backup_independence_check` 置为 `"warn_shared_failure_points"` 并同步汇总 `unknown_independence_dimensions[]`（若任一配对 `binding_valid == false`，全局按优先级 1 置为 `"unknown_blocked"`） |
| `dim4.debias_checklist_ack`（必检四问对应 4 个布尔键）存在 `false` 项 | 允许输出诊断但附加 `DEBIAS_ACK_INCOMPLETE` 阻断提示，提醒填报前完成全部四项认知核对 |

---

## 3. 仓库静态门禁校验脚本（`scripts/validate_framework.py`）

纯 Python 3 标准库实现（零第三方依赖），用于在提交 PR 与合并 `main` 前执行仓库级结构与防泄漏硬门禁。

### 3.1 校验项目（`3.0.7`）
1. **`index/manifest.json` 契约与引用自洽校验**：
   - JSON 语法、顶层必填字段（`schema_version` / `updated_at` / `layers` / `slot_prefixes` / `items`）与受控前缀精确集合（`FW` / `TPL` / `L1-POL` / `L1-IND` / `L1-DEM` / `L2-CAR` / `L3-PTH` / `L4-DEC`，拦截表外或废弃前缀）；
   - **受控槽位精确白名单与 `slot_id` 全局唯一性校验**：强校验 43 个业务主干槽位（`L1-DEM-01..03`、`L1-POL-01..08`、`L1-IND-01..09`、`L2-CAR-01..09`、`L3-PTH-01..08`、`L4-DEC-01..06`）与框架/模板白名单（`FW-001..007`、`TPL-001..005`），并与 `index/master-map.md` 主干槽位清单双向一致性核对，阻断表外野槽；同时执行**`slot_id` 全局唯一性硬校验**（单态主干架构下严禁两个条目共用同一 `slot_id`，命中重复立即失败退出 `1`）；
   - **必填非空 `graduation_cohort` 与数组去重校验**：强制校验逐项必填非空 `target_regions`（禁占位符）与必填非空 `graduation_cohort`（常青/通用项仅允许 `["all_cohorts"]` 且禁与具体届混用；具体研究卡须匹配 `^20\d{2}_in_20\d{2}_(?:bachelor|5yr|master|phd|md_residency)$` 且毕业年严格大于入学年、禁占位符）；强制校验 `L1–L4` 条目 `drivers` 非空，并对 `drivers`、`major_codes`、`target_regions`、`graduation_cohort`、`upstream_ids` 执行数组去重校验；
   - **唯一待复核状态机与图完整性**：锁定 `status` 唯一允许枚举 `active | draft | needs_reverify | deprecated`（拦截非标词如旧态冲突词）、`volatile` 条目 `valid_until` 非空 ISO 日期、`upstream_ids` 目标存在性与三色 DFS DAG 无环校验、条目 `path` 真实存在且位于仓库根内。
2. **全仓 Markdown 本地相对链接校验**：扫描所有 `.md` 文件（自动剥离围栏代码块与行内代码），忽略 `http/https/mailto/tel/data/#`，核验所有本地相对链接目标存在、非绝对路径且未越界。
3. **硬性隐私、编码格式、本机路径、凭据与受控个案/商业表防泄漏扫描**：
   - **二进制与非 `UTF-8` 文件默认拒绝**：凡包含空字节（`NUL` / `\x00`）的二进制文件或无法按 `UTF-8` 解码的文件一律拒绝，防非文本绕过扫描；
   - **独立 `.json` 个案字段内容级隐私拦截**：对仓库内除 `index/manifest.json` 外的全部 `.json` 文件执行 JSON 解析与键/值扫描，拦截包含 `case_id` / `CASE-*` 标识、个人身份键（`student_name`、`id_card`、`phone`、`wechat` 等）或出现 `>= 2` 个个案/计算实例键（如 `student_rank`、`gaokao_score`、`max_annual_tuition_cny`、`dim1_academic_physical`、`group_evaluations` 等）的独立 JSON 文件，不依赖文件名约定；
   - 拦截各类本机绝对路径（macOS/Linux 用户目录与外置挂载卷路径、Windows 盘符用户路径）；
   - 自动检测当前运行环境操作系统用户名与内建受限标识加盐摘要，并支持加载外部本地敏感词黑名单（`--blocklist-file` 或环境变量 `PATHWISE_PRIVACY_BLOCKLIST`）；
   - 拦截真实个人姓名填报字段、个人电子邮箱（仅豁免 RFC 2606 保留示例域名与 GitHub noreply 域名）、常见 API Key/Token/私钥特征、以及受控商业招生平台/原始招生大表文件名与数据行特征。

### 3.2 运行命令与退出码

```bash
# 默认全仓严格校验（建议加 -B 避免在公开仓库生成 __pycache__）
python3 -B scripts/validate_framework.py

# 指定目标仓库根目录，并附加本地受控敏感词黑名单（黑名单文件严禁放在公开仓库内）
python3 -B scripts/validate_framework.py /path/to/repo --blocklist-file /path/to/local-blocklist.txt
```

| 退出码 | 含义 |
| --- | --- |
| `0` | 全部结构、相对链接与隐私防泄漏校验均通过（0 失败） |
| `1` | 命中至少 1 项硬门禁失败（manifest 缺陷、断链或隐私/路径/受控表泄漏） |
| `2` | 命令行参数错误或指定仓库根路径不存在 |

> **检验边界声明**：`validate_framework.py` 仅作为自动化结构、引用与防泄漏静态门禁，**不可替代**「红队顾问」的逻辑抗压测试与「独立审核」的一手原件与语义终审。
