# Pathwise v3 数据结构与公私存储隔离契约（D2 / D3 / D5）

> 本契约落实 `docs/architecture-v3.md` §4.2 中的 **D2**、**D3**、**D5** 三项数据结构定义，并与 [D1 路由清单](../index/manifest.json) 及 [D4/D6 计算接口契约](../scripts/README.md) 配套。  
> **红线声明**：公开仓库仅存放字段级 Schema 契约与可公开的标准化公共映射字典；**绝不存放任何真实考分/商业招生大表、真实考生个案文件或本机绝对路径**。

---

## 1. 公私存储隔离与路径注入契约（`3B` 解耦）

| 资产编号与类别 | 存储位置 | 入公开库权限 | 本地程序读取接口 |
| --- | --- | --- | --- |
| **D1** 知识资产路由与时效清单 | 公开仓库 `index/manifest.json`（`schema_version: 3.0.7`） | 允许公开 | 相对仓库根路径直接读取；强制校验 `43` 主干槽与 `FW/TPL` 白名单、`slot_id` 全局唯一性、非空 `target_regions` 与必填非空 `graduation_cohort`（常青项填 `["all_cohorts"]`，具体卡填 `^20\d{2}_in_20\d{2}_(?:bachelor\|5yr\|master\|phd\|md_residency)$`） |
| **D2** 江苏在苏招生专业组、历年投档/专业分底表与当年章程调剂规则表（`D2-A/B/C/D`） | 本地受控招生数据区 | **严格禁止入公开库** | 通过环境变量 `PATHWISE_CONTROLLED_DATA_DIR` 或 CLI 参数 `--controlled-data-dir` 注入 |
| **D3** 跨年专业组拆并映射明细与异常年标记表 | 明细留本地受控区；通用规则公开 | **明细严格禁止入公开库** | 同上，从 `$PATHWISE_CONTROLLED_DATA_DIR` 读取 |
| **D5** 教育部本科专业↔L2职业规格/L3培养与逐路径主备映射字典 | 公开仓库 `data/dictionaries/`（后续启用） | **允许公开**（仅含国标专业代码与公共研究卡 ID，零商业考分与个人数据） | 相对仓库根路径读取 |
| **D6 实例** 真实考生四维约束卡与冲稳保志愿输出 | 本地受控个案区 | **严格禁止入公开库** | 通过环境变量 `PATHWISE_CASES_DIR` 或 CLI 参数 `--cases-dir` 注入 |

**通用数据治理规则**：
1. **原始受控表只读**：所有清洗、合并、字段补齐均以可复跑脚本输出派生标准化表，绝不原地覆写原始 CSV/JSON。
2. **显式完整性状态（`completeness_status`）与字段级缺失→下游阻断映射**：全系数据表统一采用三值枚举 `complete` / `partial` / `unknown`，且严格区分辅助字段缺失与关键红线/分位字段缺失——**绝不允许借 `partial` 绕过保底池拦截或等权伪造水位**：

| 缺失字段类别 | 具体涉及字段 | 允许的表级 `completeness_status` | 下游 `D6` 强制行为（硬规则） |
| --- | --- | --- | --- |
| **一般辅助字段** | `moe_college_code`、`max_score`、`major_max_score`、`major_avg_score`、`notes` | `partial` | 不单独阻断红线核验或水位精算，仅在报告中保留降级备注 |
| **红线核验字段与当年章程规则** | `D2-A.subject_req`、`D2-B.physical_limit_codes`（`null` 表示未知，`[]` 表示已核无受限）、`D2-B.tuition_cny_per_year`、`D2-B.duration_years`、`D2-B.transfer_restriction=="unknown"`、`D2-D` 缺失或 `rule_completeness != "complete"`、`D2-D.group_wide_scenario_flags == null`、`D2-D.member_scenario_flags_by_seq == null` 或实际可调剂成员 `seq ∈ S` 在 `member_scenario_flags_by_seq` 中缺键/为 `null` | `partial` 或 `unknown` | 只要实际可调剂范围 `S` 内**任一成员**命中任一项未知，立即置 `unverified_redline_block_safety = true` 且 `safety_pool_blocked = true`，**严禁放行进 `safety` 保底池** |
| **分位计算核心字段** | 实际可调剂范围内任一成员的 `D2-B.major_min_rank` 或 `D2-B.admitted_count` 为 `null`（或 `D2-D` 可调剂范围未核清） | `partial`（缺成员分位）或 `unknown` | **一律强制输出 `water_level = "unknown"` 且 `safety_pool_blocked = true`**；删除“缺录取人数时退化为等权仍算 `top/mid`”的旧口径（除非存在经独立审核明确批准的同口径可比替代证据，默认无） |

3. **公共字段编码标准**：统一 UTF-8（无 BOM）编码；日期遵循 ISO 8601（`YYYY-MM-DD`）；缺失值在 JSON 中为 `null`，在 CSV 中为空字符串 `""`（绝不用 `0`、`-1` 或空数组 `[]` 冒充未核实的未知值）。

---

## 2. D2：江苏在苏招生专业组、历年投档/专业分与当年章程调剂规则底表

D2 拆分为四张规范化表：**D2-A（院校专业组投档表）**、**D2-B（组内各专业计划与录取明细表）**、**D2-C（江苏一分一段与报考规模辅助表）**、**D2-D（当年招生章程与组内调剂规则表）**，以完整支持 D4 超额漂移计算与 D6 绑定 `target_year` 当年调剂范围的硬红线拦截及组内 `water_level` 水位精算。

### 2.1 D2-A 院校专业组投档表（`admissions_group_cutoff`）

- **主键（PK）**：`(admission_year, track, batch, college_code, group_code)`
- **业务定位**：记录每一招生年度在苏投放的院校专业组整体投档线、等效位次及客观混编标识。

| 字段名 | 类型 | 可空 | 枚举 / 格式约束 | 业务含义 |
| --- | --- | --- | --- | --- |
| `admission_year` | `integer` | 否 | `2021`–`2099` | 招生年份（YYYY） |
| `province_source` | `string` | 否 | 固定 `"JS"`（外省扩展按 GB/T 2260 简称） | 生源地省份代码 |
| `track` | `string` | 否 | `physics` \| `history` | 科类（物理类 / 历史类） |
| `batch` | `string` | 否 | `undergrad_regular` \| `undergrad_early` \| `special_plan` | 录取批次（本科普通批 / 提前批 / 专项计划） |
| `college_code` | `string` | 否 | 江苏 4 位院校招生代码（如 `"1101"`） | 省考院专业组归属院校代码 |
| `moe_college_code` | `string` | 是 | 教育部 5 位国标学校标识码 | 跨省院校统一主键（用于跨库关联） |
| `college_name` | `string` | 否 | 非空规范全称 | 院校名称 |
| `college_tier` | `string` | 否 | `985` \| `211` \| `double_first_class` \| `public_undergrad` \| `private_undergrad` \| `independent` | 院校层次分类 |
| `college_province` | `string` | 否 | 标准省级行政区简称（如 `"北京"`、`"江苏"`） | 院校主办学地所属省份（用于 D4 地域多样性诊断） |
| `group_code` | `string` | 否 | 2–4 位专业组代码（如 `"01"`、`"05"`） | 院校专业组号 |
| `subject_req` | `string` | 否 | `PHY_CHEM` \| `PHY_ONLY` \| `PHY_BIO` \| `PHY_GEO` \| `PHY_POL` \| `HIST_ONLY` \| `HIST_POL` \| `HIST_GEO` \| `HIST_CHEM` \| `HIST_BIO` \| `UNLIMITED` | 再选科目硬门槛（物理/历史首选 + 再选要求） |
| `plan_count` | `integer` | 是 | `>= 0` | 该专业组当年在苏计划招生总数 |
| `admitted_count` | `integer` | 是 | `>= 0` | 该专业组实际录取人数 |
| `min_score` | `integer` | 是 | `0`–`750` | 专业组最低投档分 |
| `min_rank` | `integer` | 是 | `>= 1` | 专业组最低投档等效位次（数字越小位次越高） |
| `max_score` | `integer` | 是 | `0`–`750` | 专业组最高录取分 |
| `is_sino_foreign_group` | `boolean` | 否 | `true` \| `false` | 是否为纯中外合作办学/联合办学专业组 |
| `is_mixed_sino_foreign` | `boolean` | 否 | `true` \| `false` | 是否同组混编普通专业与高收费中外合作专业 |
| `is_cross_discipline_group` | `boolean` | 否 | `true` \| `false` | 组内专业是否跨越 2 个及以上教育部学科门类 |
| `campus_location` | `string` | 是 | 城市/校区名 | 组级办学地点（异地校区显式标出） |
| `data_source` | `string` | 否 | `official_jseea` \| `college_official` \| `paid_platform_controlled` | 数据来源渠道 |
| `completeness_status` | `string` | 否 | `complete` \| `partial` \| `unknown` | 记录完整性状态 |
| `notes` | `string` | 是 | 自由文本 | 补充说明（如征集志愿、专项标注等） |

### 2.2 D2-B 组内各专业计划与录取明细表（`admissions_group_majors`）

- **主键（PK）**：`(admission_year, track, batch, college_code, group_code, major_seq)`
- **外键（FK）**：`(admission_year, track, batch, college_code, group_code)` → `admissions_group_cutoff`；`moe_major_code` → D5 `major_pathway_dictionary.moe_major_code`（大类招生允许为 `null` 并通过别名表解析）
- **业务定位**：支撑 `2B` 硬红线整组否决（体检/学费/禁转/排斥专业核查）与非红线组内 `water_level` 相对水位精算。

| 字段名 | 类型 | 可空 | 枚举 / 格式约束 | 业务含义 |
| --- | --- | --- | --- | --- |
| `admission_year` | `integer` | 否 | `2021`–`2099` | 招生年份（FK） |
| `track` | `string` | 否 | `physics` \| `history` | 科类（FK） |
| `batch` | `string` | 否 | 同 D2-A | 录取批次（FK） |
| `college_code` | `string` | 否 | 同 D2-A | 院校代码（FK） |
| `group_code` | `string` | 否 | 同 D2-A | 专业组号（FK） |
| `major_seq` | `integer` | 否 | `>= 1` | 组内专业顺序号 |
| `moe_major_code` | `string` | 是 | `^[0-9]{6}[KT]?$` | 教育部标准本科专业代码（大类招生可为 `null`） |
| `raw_major_name` | `string` | 否 | 招生计划原名 | 招生章程/计划书中的专业（或大类）原始名称 |
| `is_broad_category` | `boolean` | 否 | `true` \| `false` | 是否按专业大类招生（需关联大类分流与 D5 别名） |
| `plan_count` | `integer` | 是 | `>= 0` | 单专业计划招生数 |
| `admitted_count` | `integer` | 是 | `>= 0` | 单专业实际录取人数（用于水位分位加权） |
| `tuition_cny_per_year` | `integer` | 是 | `>= 0` | 年学费（人民币元/年；用于 `dim2` 学费硬红线校验） |
| `duration_years` | `integer` | 是 | `4` \| `5` \| `6` \| `7` \| `8` | 培养学制（年；用于对齐 L2 毕业入职时钟） |
| `campus_location` | `string` | 是 | 城市/校区名 | 单专业实际办学地点 |
| `program_type` | `string` | 否 | `regular` \| `sino_foreign` \| `joint_degree` \| `honors_base` \| `targeted` \| `normal_public_funded` | 班型与办学类型（普通/中外合作/联合学士学位/拔尖基地/定向/公费师范） |
| `transfer_restriction` | `string` | 否 | `allowed` \| `restricted` \| `prohibited` \| `unknown` | 入校转专业约束状态（中外合作明文禁转记为 `prohibited`） |
| `physical_limit_codes` | `array<string>` | 是 | 教育部体检受限条款编号数组；**`[]` 仅表示已核实无受限条款，`null` 表示未核实未知（严禁混同）** | 体检限报/不予录取条款（如色盲/色弱/视力条款；命中交集即退档红线否决，为 `null` 即触发 `unverified_redline_block_safety=true`） |
| `major_min_score` | `integer` | 是 | `0`–`750` | 单专业最低录取分 |
| `major_min_rank` | `integer` | 是 | `>= 1` | 单专业最低录取位次（任一可调剂成员缺失即触发下游 `water_level=unknown`） |
| `major_max_score` | `integer` | 是 | `0`–`750` | 单专业最高录取分 |
| `major_avg_score` | `number` | 是 | `0`–`750` | 单专业平均录取分 |
| `completeness_status` | `string` | 否 | `complete` \| `partial` \| `unknown` | 单专业记录完整性状态（须同步配合 §1 字段级缺失映射规则；缺 `major_min_rank` 或 `admitted_count` 或红线字段均触发下游硬拦截） |
| `notes` | `string` | 是 | 自由文本 | 专业备注（含大类含具体专业清单等辅助信息；单科/外语/调剂硬条款须结构化落入 `D2-D`） |

### 2.3 D2-C 江苏一分一段与报考规模辅助表（`js_score_rank_scale`）

- **主键（PK）**：`(admission_year, track, score)`
- **字段**：`admission_year` (`integer`), `track` (`physics` | `history`), `score` (`integer`), `count_at_score` (`integer`, 本分人数), `cumulative_rank` (`integer`, 累计位次), `total_track_applicants` (`integer`, 当年该科类总参考/上线基准规模), `completeness_status` (`complete` | `partial` | `unknown`)。

### 2.4 D2-D 当年招生章程与组内调剂规则表（`admissions_group_charter_rules`）

- **主键（PK）**：`(target_year, track, batch, college_code, group_code)`
- **业务定位**：将 `D6` 要求的“绑定 `target_year` 当年有效招生章程、实际调剂覆盖/排除范围与标准化场景红线”落为结构化硬规则表，彻底消除靠自由文本或默认放行绕过最坏调剂暴露的漏洞。

| 字段名 | 类型 | 可空 | 枚举 / 格式约束 | 业务含义 |
| --- | --- | --- | --- | --- |
| `target_year` | `integer` | 否 | `2024`–`2099` | 规则适用的目标报考年份（YYYY） |
| `track` | `string` | 否 | `physics` \| `history` | 科类 |
| `batch` | `string` | 否 | `undergrad_regular` \| `undergrad_early` \| `special_plan` | 录取批次 |
| `college_code` | `string` | 否 | 江苏 4 位院校招生代码 | 院校代码 |
| `group_code` | `string` | 否 | 2–4 位专业组号 | 目标年份专业组号 |
| `charter_version` | `string` | 否 | 如 `"2026-official-v1"` | 当年正式招生章程版本号 |
| `charter_effective_date` | `string` | 是 | ISO `YYYY-MM-DD` | 章程正式发布/生效日期 |
| `charter_evidence_ref` | `string` | 否 | 阳光高考/高校官网章程或江苏省考试院招生计划专刊可定位出处（文号/页码/URL） | 调剂与限报条款的一手官方溯源凭证 |
| `adjustment_scope_mode` | `string` | 否 | `full_group_default` \| `subset_isolated_verified` \| `no_adjustment_written_promise_verified` \| `unknown` | 组内实际调剂范围模式（仅经官方书面核实方可标 `subset_isolated_verified` 或 `no_adjustment_written_promise_verified`） |
| `adjustable_major_seqs` | `array<integer>` | 是 | 引用当年 `D2-B.major_seq`；`adjustment_scope_mode == "unknown"` 时必为 `null` | 实际可能被调剂落入的专业序号集合（`D6` 红线扫描与水位计算的作用域） |
| `excluded_major_seqs` | `array<integer>` | 否 | 引用当年 `D2-B.major_seq`（无排除填 `[]`） | 官方明文规定**仅录取有专业志愿考生、不接受调剂**的专业序号集合（如明文不调剂的中外合作/定向项） |
| `written_no_adjustment_condition` | `string` | 是 | 自由文本（仅 `no_adjustment_written_promise_verified` 时必填） | 书面不调剂承诺的生效前提条件（如“填满 6 个不重复专业志愿且服从体检要求”） |
| `subject_score_limits` | `object` | 是 | 如 `{"english_min": 110, "math_min": 100}`；已核无限制填 `{}`，`null` 表示未知 | 当年章程规定的单科成绩硬门槛 |
| `foreign_language_limits` | `array<string>` | 是 | 允许语种数组如 `["english"]`；已核不限填 `[]`，`null` 表示未知 | 外语语种限报条款（如仅限英语考生报考） |
| `group_wide_scenario_flags` | `array<string>` | 是 | 元素枚举：`prohibited_transfer_sino_foreign` \| `remote_or_relocated_campus` \| `mandatory_service_bond_or_targeted` \| `five_year_or_longer_duration` \| `fieldwork_shift_high_hazard` \| `strict_single_subject_or_lang_gate` \| `non_clinical_no_physician_exam`；**仅记录无条件作用于整组的全局规则**（如整组外语/单科门槛、全组异地校区）；已核无填 `[]`，未核填 `null` | 无条件作用于整组的标准化场景红线标记（与 `D6Input.dim3.hard_redline_scenarios` 精确对齐） |
| `member_scenario_flags_by_seq` | `object<string, array<string>>` | 是 | 键为字符串化的 `D2-B.major_seq`（如 `"1"`、`"2"`、`"3"`），值为上述 7 类枚举数组（该专业无风险填 `[]`）；未核填 `null`；**实际可调剂成员 `seq ∈ S` 缺键或值为 `null` 均视为未知** | 按组内专业序号逐专业记录的场景红线标记（避免已书面排除专业的风险污染可调剂子集） |
| `rule_completeness` | `string` | 否 | `complete` \| `partial` \| `unknown` | 当年规则核验完整性；**凡缺失当年 `D2-D` 记录或 `rule_completeness != "complete"`，D6 必须按已知全组成员执行最坏暴露红线扫描，并强制置 `unverified_redline_block_safety = true`、`safety_pool_blocked = true`** |

- **排除后暴露集合与场景红线投影规则（`3.0.7`）**：设 `G` 为当年 `D2-B` 组内全部专业序号集合，`T` 为考生在该组主动填报的专业序号集合（`D6Input.candidate_group_targets[].target_major_seqs`），`A` 为 `adjustable_major_seqs`，`E` 为 `excluded_major_seqs`。
  - **严格区分两类回退成因**：① **考生填报合法性（`group_target_valid`）**：`D6Input.candidate_group_targets[]` 按归一化完整五元组键 `(target_year, track, batch, college_code, group_code)` 全局唯一且单条 `target_major_seqs` 内元素严格去重；**仅当**缺失、出现重复组键（`>= 2` 条）或 `target_major_seqs` 含重复/为空/非正整数/越界 `⊈ G` / `target_year` 不符时，判 `group_target_valid = false`（与顺序无关回退 `S = G`、强制阻断保底，且引用该组的配对 `binding_valid = false`）；② **章程调剂证据回退**：当考生填报合法（`group_target_valid == true`），在 `adjustment_scope_mode == "subset_isolated_verified"` 且 `rule_completeness == "complete"`、`A != null` 且 `(A ∪ E) ⊆ G` 时，实际录取暴露集合严格定义为 **`S = T ∪ (A \ E)`**——**`E` 仅从被动调剂集合 `A` 中剔除，绝不从考生主动填报集合 `T` 中剔除**；若 `subset_isolated_verified` 下 `A == null` 或 `(A ∪ E) ⊈ G`（或 `no_adjustment_written_promise_verified` 未满足书面生效条件，或缺失 `D2-D` / `adjustment_scope_mode == "unknown"` / `rule_completeness != "complete"`），则**保留 `group_target_valid = true`**（不误判为考生填报非法或 `binding_valid = false`），仅回退 `S = G` 最坏暴露并置 `unverified_redline_block_safety = true`、`water_level = "unknown"`、`water_level_percentile = null`、`safety_pool_blocked = true`，若该组被合法配对引用，已知同组共损（同属 `(college_code, group_code)` 且两端 `major_seq ∈ S`，或含 `same_admission_group_risk`）优先判 `group_isolation = "fail"`，未命中同组 `"fail"` 时（如跨组配对）由章程证据规则令 `group_isolation = "unknown_blocked"`（绝不判 `"pass"`）。
  - 若 `group_wide_scenario_flags == null`、`member_scenario_flags_by_seq == null`，或存在任意 `seq ∈ S` 在 `member_scenario_flags_by_seq` 中缺键或值为 `null`，D6 强制置 `unverified_redline_block_safety = true`、`safety_pool_blocked = true`；否则仅按投影集合 `effective_scenario_flags(S) = group_wide_scenario_flags ∪ (⋃_{seq ∈ S} member_scenario_flags_by_seq[str(seq)])` 与 `seq ∈ S` 的成员执行 `VETO_HARD_REDLINE_MAJOR`——未被考生主动填报且已书面排除调剂的 `seq ∈ E \ T` 不污染 `S`。

**D2-D 虚构占位示例（`[虚构占位示例，非真实院校章程；展示 major_seq=3 书面排除不污染可调剂子集 S=[1,2]]`）**：

```json
{
  "admissions_group_charter_rules_example": [
    {
      "target_year": 2026,
      "track": "physics",
      "batch": "undergrad_regular",
      "college_code": "9901",
      "group_code": "02",
      "charter_version": "2026-official-v1",
      "charter_effective_date": "2026-05-15",
      "charter_evidence_ref": "虚构占位示例：阳光高考网《示例理工大学 2026 年本科招生章程》第 14–18 条与江苏招生计划专刊对应页",
      "adjustment_scope_mode": "subset_isolated_verified",
      "adjustable_major_seqs": [1, 2],
      "excluded_major_seqs": [3],
      "written_no_adjustment_condition": null,
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
  ]
}
```

### 2.5 本地存量原始 CSV 清洗映射说明与虚构示例

历史本地受控 CSV（14 列扁平表）需经 ETL 脚本按 `类型`（投档线 / 专业分）拆入 D2-A 与 D2-B，并补齐院校代码、学费、学制与体检条款：

| 存量扁平列 | 目标表与目标字段 | 清洗口径 |
| --- | --- | --- |
| `校名` / `省份` / `层次` | D2-A `college_name` / `college_province` / `college_tier` | 标准化枚举并回查 `college_code` |
| `科类` / `年份` / `组号` | D2-A & D2-B `track` / `admission_year` / `group_code` | `物理类 -> physics`、`历史类 -> history`，组号零填充至 2 位 |
| `类型` | 路由分流键 | `投档线` 行写入 D2-A；`专业分` 行写入 D2-B |
| `最低分` / `最低位次` / `最高分` / `录取数` | D2-A 组级指标或 D2-B 专业级指标 | 空值置 `null`，缺专业分明细时组记录标注 `completeness_status=partial` |
| `专业名` / `选考要求` / `备注` | D2-B `raw_major_name` / D2-A `subject_req` / `notes` | 过滤非专业名控制标记，解析选考枚举与学费/校区备注 |

**D2-A / D2-B 虚构占位示例（`[虚构占位示例，非真实招生数据]`）**：

```csv
admission_year,province_source,track,batch,college_code,moe_college_code,college_name,college_tier,college_province,group_code,subject_req,plan_count,admitted_count,min_score,min_rank,max_score,is_sino_foreign_group,is_mixed_sino_foreign,is_cross_discipline_group,campus_location,data_source,completeness_status,notes
2025,JS,physics,undergrad_regular,9901,19901,示例理工大学,211,示例省,02,PHY_CHEM,40,40,612,24500,628,false,false,true,主校区,official_jseea,complete,虚构占位示例行
```

```csv
admission_year,track,batch,college_code,group_code,major_seq,moe_major_code,raw_major_name,is_broad_category,plan_count,admitted_count,tuition_cny_per_year,duration_years,campus_location,program_type,transfer_restriction,physical_limit_codes,major_min_score,major_min_rank,major_max_score,major_avg_score,completeness_status,notes
2025,physics,undergrad_regular,9901,02,1,080601,电气工程及其自动化,false,20,20,5800,4,主校区,regular,allowed,"[]",620,19200,628,623.5,complete,虚构占位示例行
2025,physics,undergrad_regular,9901,02,2,080401,材料科学与工程,false,20,20,5800,4,主校区,regular,allowed,"[""2.2""]",612,24500,619,615.0,complete,虚构占位示例行
```

---

## 3. D3：跨年专业组拆并映射与异常年标记表

D3 解决“同组号跨年换专业成员”导致的位次失真，以及一次性选科政策改革造成的结构性断裂年污染。

### 3.1 D3-A 跨年专业组拆并映射表（`group_cross_year_mapping`）

- **主键（PK）**：`(target_year, base_year, track, college_code, target_group_code, base_group_code)`（`newly_created` 时 `base_group_code` 记为空哨兵 `"NONE"`）

| 字段名 | 类型 | 可空 | 枚举 / 格式约束 | 业务含义 |
| --- | --- | --- | --- | --- |
| `target_year` | `integer` | 否 | YYYY | 目标参考年份（较新年份） |
| `base_year` | `integer` | 否 | YYYY（`< target_year`） | 历史基准年份 |
| `track` | `string` | 否 | `physics` \| `history` | 科类 |
| `college_code` | `string` | 否 | 院校代码 | 关联 D2 院校 |
| `target_group_code` | `string` | 否 | 专业组号 | 目标年份专业组号 |
| `base_group_code` | `string` | 否 | 专业组号或 `"NONE"` | 历史对应专业组号 |
| `change_type` | `string` | 否 | `unchanged` \| `member_added_cold_or_high_fee` \| `member_removed_or_minor_edit` \| `split` \| `merged` \| `newly_created` \| `discontinued` | 专业组结构变更枚举 |
| `jaccard_similarity` | `number` | 是 | `0.0`–`1.0` | 目标年与基准年组内专业集合 Jaccard 重合度 |
| `added_majors` | `array<string>` | 否 | 专业名称或代码数组 | 较基准年新增的组内专业 |
| `removed_majors` | `array<string>` | 否 | 专业名称或代码数组 | 较基准年移出的组内专业 |
| `rank_inheritability` | `string` | 否 | `high` \| `conditional` \| `none` | 历史位次可继承等级（`none` 时严禁直接按旧组投档线估值） |
| `composition_shift_risk` | `string` | 否 | `none` \| `low` \| `medium` \| `high` | 组内成分突变风险标签 |
| `completeness_status` | `string` | 否 | `complete` \| `partial` \| `unknown` | 映射核验完整性 |
| `rationale` | `string` | 否 | 非空说明 | 变动判定依据（如“新增高收费中外合作专业，历史组线不可直接沿用”） |

### 3.2 D3-B 异常年与政策断裂隔离表（`policy_shock_years`）

- **主键（PK）**：`(province_source, track, shock_year, transition_pair)`
- **一手核验与隔离硬规则**：仅当 `verification_status == "verified_primary_source"` 且 `evidence_ref` 具备省教育考试院正式选科指引或招生专刊可定位原件出处（发布机构、文号/标题、日期或页码）时，`exclude_from_drift_window` 方可置 `true` 供 `D4` 剔除；凡尚未回核官方原件的候选断裂年必须记为 `verification_status: "pending_verification"`、`exclude_from_drift_window: false` 并标注 `[待核未知]`，**严禁静默剔除或当作既定事实参与常态漂移估算**。

| 字段名 | 类型 | 可空 | 枚举 / 格式约束 | 业务含义 |
| --- | --- | --- | --- | --- |
| `province_source` | `string` | 否 | `"JS"` 等 | 生源省份 |
| `track` | `string` | 否 | `physics` \| `history` \| `all` | 受冲击科类 |
| `shock_year` | `integer` | 否 | YYYY | 发生断裂的基准年（须经一手官方原件核定） |
| `transition_pair` | `string` | 否 | `"YYYY->YYYY"`（如 `"2022->2023"`、`"2023->2024"`） | 受冲击的跨年转换对 |
| `shock_type` | `string` | 否 | `subject_binding_reform` \| `batch_merge` \| `scoring_rule_change` \| `enrollment_quota_jump` | 冲击类型 |
| `verification_status` | `string` | 否 | `verified_primary_source` \| `pending_verification` | 政策断裂年一手官方原件核验状态；核定前必为 `pending_verification`（`[待核未知]`） |
| `exclude_from_drift_window` | `boolean` | 否 | `true` \| `false` | D4 位次漂移计算是否强制剔除该年份/转换对；**仅当 `verification_status == "verified_primary_source"` 且 `evidence_ref` 含可定位官方原件出处时方可为 `true`** |
| `impact_summary` | `string` | 否 | 非空文本 | 结构冲击说明及待核差异说明 |
| `evidence_ref` | `string` | 否 | 省教育考试院正式选科指引/招生专刊可定位原件出处（发布机构、文号/标题、日期或页码）；未核定前须标明 `[待核未知]` 及待核原件项 | 政策依据一手溯源 |

> **江苏物化选科断裂年 `[待核未知]` 说明**：历史内部底稿在江苏物理类理工专业物化捆绑冲击转换对上存在两类记载差异——一类记录为 `2022->2023`，另一类依据教育部 2021 年《普通高校本科招生专业选考科目要求指引（通用版）》自 **2024 届起**实施的口径记录为 `2023->2024`。在回核江苏省教育考试院适用年份正式选科指引原件、当年招生计划专刊及本地受控分位复算底稿并完成一手定案前，下述示例将 `"2022->2023"` 与 `"2023->2024"` 均列为 `verification_status: "pending_verification"`、`exclude_from_drift_window: false`（`[待核未知]`），严禁将其写死为已剔除事实或静默忽略。

**D3 占位示例（`[D3-A 为虚构占位示例；D3-B 江苏物化改革断裂候选对均标 [待核未知]，待一手官方原件核定]`）**：

```json
{
  "group_cross_year_mapping_example": [
    {
      "target_year": 2025,
      "base_year": 2024,
      "track": "physics",
      "college_code": "9901",
      "target_group_code": "02",
      "base_group_code": "02",
      "change_type": "member_added_cold_or_high_fee",
      "jaccard_similarity": 0.67,
      "added_majors": ["示例高费合作专业"],
      "removed_majors": [],
      "rank_inheritability": "conditional",
      "composition_shift_risk": "high",
      "completeness_status": "complete",
      "rationale": "虚构占位示例：原组新增高收费合作办学专业，历史组位次可能下移但调剂风险上升"
    }
  ],
  "policy_shock_years_example": [
    {
      "province_source": "JS",
      "track": "physics",
      "shock_year": 2022,
      "transition_pair": "2022->2023",
      "shock_type": "subject_binding_reform",
      "verification_status": "pending_verification",
      "exclude_from_drift_window": false,
      "impact_summary": "[待核未知] 历史内部底稿曾将该转换对记为江苏物理类物化绑定冲击候选年，但与 2024 届起实施教育部通用版选科指引的记载存在冲突；官方原件与受控分位复算核定前严禁静默剔除。",
      "evidence_ref": "[待核未知] 待回核江苏省教育考试院 2022/2023 年在苏招生选科目录正式公告原件（发布机构、文号、日期/页码）及本地受控分位底稿"
    },
    {
      "province_source": "JS",
      "track": "physics",
      "shock_year": 2023,
      "transition_pair": "2023->2024",
      "shock_type": "subject_binding_reform",
      "verification_status": "pending_verification",
      "exclude_from_drift_window": false,
      "impact_summary": "[待核未知] 依据教育部 2021 年通用版选科指引自 2024 届起实施的记载，2023->2024 为江苏物理+化学双选绑定落地冲击候选转换对；官方原件与受控分位复算核定前严禁静默剔除。",
      "evidence_ref": "[待核未知] 待回核江苏省教育考试院 2024 年普通高校招生专业选科要求正式目录原件（发布机构、文号、日期/页码）及本地受控分位底稿"
    }
  ]
}
```

---

## 4. D5：教育部本科专业↔L2职业规格/L3培养与逐路径主备映射字典

- **主键（PK）**：`moe_major_code`（教育部 6 位标准本科专业代码，特设专业带 `T`，国家控制布点专业带 `K`）
- **公私权限**：本字典仅连接国标专业目录与公开库 `L2 / L3` 公共卡片 ID 及逐路径准入门槛，**不含真实考分与个案信息，允许公开入库**。
- **逐路径与跨专业全局配对原则（`3.0.7`）**：同一本科专业往往对应多个跨行业岗位族、不同就业地域与不同学历/执业准入门槛，且真实志愿中的主攻与备选常跨越**不同国标专业**（如法学 vs 知识产权、临床医学 vs 药学）。本契约以结构化对象数组 `primary_routes[]` 与 `backup_routes[]` 逐路径建模，强制 `route_id` 以 `moe_major_code` 为全局唯一前缀，并通过 `backup_routes[].paired_primary_refs[]`（含 `primary_major_code + primary_route_id + co_failure_status_by_dim`）实现同专业与跨专业的确定性主备配对及逐维共损审计，支撑 `D6` 结合个案端专业组绑定与 `D2-D` 规则执行四维独立性冲击核验。

### 4.1 专业级主记录字段

| 字段名 | 类型 | 可空 | 枚举 / 格式约束 | 业务含义 |
| --- | --- | --- | --- | --- |
| `moe_major_code` | `string` | 否 | `^[0-9]{6}[KT]?$` | 教育部标准本科专业代码（PK） |
| `moe_major_name` | `string` | 否 | 教育部目录规范名 | 标准本科专业名称 |
| `discipline_category` | `string` | 否 | 教育部 12/13 学科门类规范名（如 `工学`/`理学`/`医学`/`法学`） | 学科门类（用于客观判定 `cross_discipline_mix`） |
| `sub_category` | `string` | 否 | 教育部专业类规范名（如 `电气类`/`法学类`） | 所属本科专业类 |
| `is_special_major` | `boolean` | 否 | `true` \| `false` | 是否特设专业（代码含 `T`） |
| `is_controlled_major` | `boolean` | 否 | `true` \| `false` | 是否国家控制布点专业（代码含 `K`） |
| `broad_category_aliases` | `array<string>` | 否 | 常见高校大类招生名称列表 | 将 D2-B 宽口径大类名称映射回候选国标专业集合 |
| `role_family_tags` | `array<string>` | 否 | 跨行业岗位族规范标识数组（如 `power_grid_ops`、`industrial_control`、`corporate_ip_legal`） | 建立“专业↔岗位族↔多行业”多对多索引，防止将跨行业职能武断塞入单一产业槽位 |
| `l2_career_card_ids` | `array<string>` | 否 | 须命中 `index/manifest.json` 的 `L2` 卡片 `id` | 关联的 L2 毕业窗职业入口规格卡汇总 |
| `l3_pathway_card_ids` | `array<string>` | 否 | 须命中 `index/manifest.json` 的 `L3` 卡片 `id` | 关联的 L3 培养实得训练与大学执行轴卡片 |
| `primary_routes` | `array<object>` | 否 | 非空路径对象数组（结构见 §4.2） | 逐路径主职业入口定义（每条路径独立声明岗位族、地域、付款人、承接组织、学历与执业执照门槛） |
| `backup_routes` | `array<object>` | 否 | 路径对象数组（结构见 §4.2；无已核备选时填 `[]`） | 逐路径备选职业入口定义，通过 `paired_primary_refs[]`（见 §4.3）支持同专业与跨专业主备配对及逐维共损核验 |
| `l3_evidence_status` | `string` | 否 | `primary_complete` \| `proxy_1b_with_admissions_checklist` \| `pending` | L3 高校培养实证状态（支持 `1B` 结构代理降级推进） |
| `admissions_verification_questions` | `array<string>` | 否 | 当 `l3_evidence_status=proxy_1b_with_admissions_checklist` 时为 1–3 条可执行核实问题 | 自动透传给考生的招办/院系线下核实清单 |
| `completeness_status` | `string` | 否 | `complete` \| `partial` \| `unknown` | 字典条目完善状态（若任一主/备路径 `gate_completeness == "unknown"`，专业级不得标 `complete`） |

### 4.2 逐路径对象字段（`primary_routes[]` 与 `backup_routes[]`）

| 字段名 | 适用数组 | 类型 | 可空 | 枚举 / 格式约束 | 业务含义 |
| --- | --- | --- | --- | --- | --- |
| `route_id` | 主 / 备 | `string` | 否 | **全局唯一键**，正则 `^[0-9]{6}[KT]?-(?:PRI\|BKP)-[0-9]{2,}$`，且前缀必须严格等于所在记录的 `moe_major_code`（如 `"080601-PRI-01"`、`"030102T-BKP-01"`） | 跨专业全局唯一路径主键 |
| `role_family_id` | 主 / 备 | `string` | 否 | 具体岗位族规范标识（非空） | 该路径对应的跨行业岗位族 ID |
| `l2_career_card_id` | 主 / 备 | `string` | 是 | 非空时须命中 `index/manifest.json` 的 `L2` 卡片 `id` | 该路径挂载的 L2 规格卡 ID |
| `job_regions` | 主 / 备 | `array<string>` | 否 | 非空数组；元素枚举：`jiangsu_local` \| `yrd_cluster` \| `national_mobile` \| `remote_field_site` \| `unknown` | 该路径主要应届就业地域分布 |
| `payer_type` | 主 / 备 | `string` | 否 | `central_fiscal` \| `local_fiscal` \| `medical_insurance_fund` \| `monopoly_soe_opex` \| `competitive_mfg_capex_rd` \| `household_out_of_pocket` \| `mixed` \| `unknown` | 该路径最终持续付款人类型 |
| `org_category` | 主 / 备 | `string` | 否 | 承接组织类别枚举（如 `grid_energy_soe` \| `listed_private_mfg` \| `public_hospital` \| `commercial_firm` \| `gov_judicial_org` \| `unknown`） | 该路径典型签约承接组织类别 |
| `degree_threshold` | 主 / 备 | `string` | 否 | `bachelor_direct` \| `master_recommended` \| `master_mandatory` \| `phd_or_residency_mandatory` \| `unknown` | 该路径实际学历准入门槛（逐路径独立判定，防用专业平均口径遮蔽硕士刚性岗） |
| `license_ids` | 主 / 备 | `array<string>` | 是 | 具体法定执业资格编码数组（如 `["LIC_PHYSICIAN"]`、`["LIC_LEGAL_BAR"]`、`["LIC_TEACHER"]`）；**已核实无需法定准入证填 `[]`，未核清填 `null`** | 该路径法定执业准入证清单（用于 D6 识别主备共享高难执照单点故障） |
| `gate_completeness` | 主 / 备 | `string` | 否 | `complete` \| `unknown` | 路径门槛核验完整性；**凡学历（`degree_threshold`）、执照（`license_ids`）、地域（`job_regions`）、付款（`payer_type`）或组织（`org_category`）任一未核清（含 `unknown` / `null`），必为 `"unknown"`** |
| `paired_primary_refs` | 仅备选 | `array<object>` | 否 | 非空对象数组（字段定义见 §4.3） | 结构化跨专业/同专业主备配对引用与逐维共损审计清单 |

### 4.3 跨专业主备配对引用对象字段（`backup_routes[].paired_primary_refs[]`）

| 字段名 | 类型 | 可空 | 枚举 / 格式约束 | 业务含义 |
| --- | --- | --- | --- | --- |
| `primary_major_code` | `string` | 否 | `^[0-9]{6}[KT]?$` | 所配对主路径归属的国标专业代码（允许指向本专业记录或**另一国标专业记录**） |
| `primary_route_id` | `string` | 否 | `^[0-9]{6}[KT]?-PRI-[0-9]{2,}$`，且前缀须等于 `primary_major_code` | 所配对主路径的全局唯一 `route_id`（须命中 `primary_major_code` 对应记录的 `primary_routes[]`） |
| `co_failure_status_by_dim` | `object` | 否 | 必须严格包含且仅包含 `payer`、`entry_gate`、`region_exposure` 三键，每键取值仅限 `isolated \| shared_fail \| unknown`（严禁缺键、`null` 或超枚举值） | 逐维内在共损审计状态（`group_isolation` 由个案端 `D6` 绑定目标年院校专业组与 `D2-D` 动态裁定） |
| `shared_bottlenecks` | `array<string>` | 否 | 非空数组；元素枚举：`same_payer_pool` \| `same_admission_group_risk` \| `same_degree_master_gate` \| `same_license_gate` \| `same_region_cycle` \| `same_org_type_exposure` \| `none` \| `unknown` | 共享单点故障标签集；**严禁 `"none"` 与任何其他值混用，严禁 `"unknown"` 与 `"none"` 混用** |
| `shared_failure_notes` | `string` | 是 | 非空文字说明（当 `shared_bottlenecks` 非 `["none"]` 时必填） | 写明共享故障点的触发情景、传导边界或待核原因（供 D6 逐配对核验直接透出） |

- **共损对象合法性与双向一致性硬规则（`3.0.7`）**：
  1. **严格三键与枚举校验**：`co_failure_status_by_dim` 必须为非空对象且精确包含 `{"payer", "entry_gate", "region_exposure"}` 三键，每个键值必须属于 `{"isolated", "shared_fail", "unknown"}`；凡缺键、`null`、超枚举值或非对象结构，下游 `D6` 按正向白名单一律视同未核清并置 `"unknown_blocked"`，**严禁落入 `"pass"`**；
  2. **双向一致性约束**：仅当 `co_failure_status_by_dim` 严格合法且三键均为 `"isolated"` 时，`shared_bottlenecks` 方可填 `["none"]`（且不得与其他值混用）；任一维为 `"shared_fail"` 时，`shared_bottlenecks` 须包含对应故障标签且不得为 `["none"]`；任一维为 `"unknown"` 时，`shared_bottlenecks` 须包含 `"unknown"` 且不得包含 `"none"`；反之，若 `shared_bottlenecks` 包含 `"unknown"` 而 `co_failure_status_by_dim` 未显式标出对应 `"unknown"` 维度，下游 `D6` 将全部未命中 `"fail"` 的维度一律置为 `"unknown_blocked"`；**任何违反上述双向一致性（如 `co_failure_status_by_dim` 缺键或含 `shared_fail`/`unknown` 却填 `shared_bottlenecks: ["none"]`）均直接视同非法未核清，下游 `D6` 强制置 `"unknown_blocked"`，绝不判 `"pass"`**；
  3. **个案端临时配对降级规则**：若考生在 D6 组合的主备路径未在 `D5` 的 `paired_primary_refs[]` 中预登记共损审计，无法仅凭单路径字段交集证伪共损的维度（尤其是 `region_exposure`）及未通过正向白名单校验的维度一律判 `"unknown_blocked"`，严禁默认判 `"pass"`。

**D5 公共字典结构占位示例（`[结构示意示例，关联卡片 ID 待分批研究填充；含同专业双路径与跨专业主备配对 030101K <-> 030102T]`）**：

```json
{
  "schema_version": "3.0.7",
  "records": [
    {
      "moe_major_code": "080601",
      "moe_major_name": "电气工程及其自动化",
      "discipline_category": "工学",
      "sub_category": "电气类",
      "is_special_major": false,
      "is_controlled_major": false,
      "broad_category_aliases": ["电气类", "能源动力与电气类"],
      "role_family_tags": ["power_grid_ops", "industrial_control", "equipment_commissioning"],
      "l2_career_card_ids": [],
      "l3_pathway_card_ids": [],
      "primary_routes": [
        {
          "route_id": "080601-PRI-01",
          "role_family_id": "power_grid_ops",
          "l2_career_card_id": null,
          "job_regions": ["jiangsu_local", "yrd_cluster", "national_mobile"],
          "payer_type": "monopoly_soe_opex",
          "org_category": "grid_energy_soe",
          "degree_threshold": "bachelor_direct",
          "license_ids": [],
          "gate_completeness": "complete"
        }
      ],
      "backup_routes": [
        {
          "route_id": "080601-BKP-01",
          "role_family_id": "industrial_control",
          "l2_career_card_id": null,
          "job_regions": ["jiangsu_local", "yrd_cluster"],
          "payer_type": "competitive_mfg_capex_rd",
          "org_category": "listed_private_mfg",
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
                "region_exposure": "shared_fail"
              },
              "shared_bottlenecks": ["same_region_cycle"],
              "shared_failure_notes": "主攻电网运维（垄断央国企运维刚需）与备选长三角工控装备制造（竞争性制造业技改研发）付款主体独立且均不强绑单一法定执业证，但仍共同暴露于长三角电网投资节奏与区域用电增速周期。"
            }
          ]
        }
      ],
      "l3_evidence_status": "proxy_1b_with_admissions_checklist",
      "admissions_verification_questions": [
        "核实该校本专业近两届本科生进入电网及电力装备企业的人数占比与推免比例",
        "核实大类分流进入强电/电力系统方向的具体绩点门槛与名额上限"
      ],
      "completeness_status": "partial"
    },
    {
      "moe_major_code": "030101K",
      "moe_major_name": "法学",
      "discipline_category": "法学",
      "sub_category": "法学类",
      "is_special_major": false,
      "is_controlled_major": true,
      "broad_category_aliases": ["法学类"],
      "role_family_tags": ["judicial_prosecution_court", "corporate_legal_compliance"],
      "l2_career_card_ids": [],
      "l3_pathway_card_ids": [],
      "primary_routes": [
        {
          "route_id": "030101K-PRI-01",
          "role_family_id": "judicial_prosecution_court",
          "l2_career_card_id": null,
          "job_regions": ["jiangsu_local", "yrd_cluster"],
          "payer_type": "local_fiscal",
          "org_category": "gov_judicial_org",
          "degree_threshold": "master_recommended",
          "license_ids": ["LIC_LEGAL_BAR"],
          "gate_completeness": "complete"
        }
      ],
      "backup_routes": [],
      "l3_evidence_status": "pending",
      "admissions_verification_questions": [
        "核实该校法学本科应届生通过法考 A 证的实际比例及法硕推免去向分布"
      ],
      "completeness_status": "partial"
    },
    {
      "moe_major_code": "030102T",
      "moe_major_name": "知识产权",
      "discipline_category": "法学",
      "sub_category": "法学类",
      "is_special_major": true,
      "is_controlled_major": false,
      "broad_category_aliases": ["法学类"],
      "role_family_tags": ["corporate_ip_legal", "patent_agency_ops"],
      "l2_career_card_ids": [],
      "l3_pathway_card_ids": [],
      "primary_routes": [
        {
          "route_id": "030102T-PRI-01",
          "role_family_id": "patent_agency_ops",
          "l2_career_card_id": null,
          "job_regions": ["jiangsu_local", "yrd_cluster", "national_mobile"],
          "payer_type": "competitive_mfg_capex_rd",
          "org_category": "commercial_firm",
          "degree_threshold": "bachelor_direct",
          "license_ids": ["LIC_PATENT_AGENT"],
          "gate_completeness": "complete"
        }
      ],
      "backup_routes": [
        {
          "route_id": "030102T-BKP-01",
          "role_family_id": "corporate_ip_legal",
          "l2_career_card_id": null,
          "job_regions": ["jiangsu_local", "yrd_cluster"],
          "payer_type": "competitive_mfg_capex_rd",
          "org_category": "listed_private_mfg",
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
              "shared_failure_notes": "跨专业主备配对：科技制造企业法务知产岗（competitive_mfg_capex_rd）与法学地方司法机关主路径（local_fiscal）付款主体不同，但共卡国家统一法律职业资格证（LIC_LEGAL_BAR）且同处长三角区域周期；若在个案端还落入同一未隔离专业组，D6 须同步判 group_isolation=fail 与 entry_gate_isolation=fail。"
            }
          ]
        }
      ],
      "l3_evidence_status": "pending",
      "admissions_verification_questions": [
        "核实该校知识产权专业本科生报考法考 A 证资格与科技制造企业法务校招去向"
      ],
      "completeness_status": "partial"
    }
  ]
}
```
