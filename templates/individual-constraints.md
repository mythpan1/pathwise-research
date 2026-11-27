# 四维个体与家庭决策收敛卡（本地受控区空白模板 · `v3.2.0`）

> **隐私与公私物理隔离最高红线声明**：
> 1. 本文件在公开仓库中**仅提供空白四维结构定义**（**严格零 MBTI 或通俗性格测试标签，零拍脑袋主观加减分打分表**）。
> 2. 任何填入真实考生姓名、考分、位次、体检代码、家庭预算或主动填报志愿配对的实填文件，**必须 100% 存放于本地受控工作区（`$PATHWISE_CASES_DIR`）**，由 `.gitignore` 与 [../scripts/validate_framework.py](../scripts/validate_framework.py) 双重强制拦截，**严禁提交至公开 GitHub 仓库或上传至云端 Gemini Notebook**！

---

## 零、运行挂载说明（对接 `v3.2.0` `D4 / D6` 本地受控引擎）

本模板对应 [../docs/architecture-v3.md](../docs/architecture-v3.md) 中的 `L4B 本地闭环态` 输入契约（`schema_version: "3.2.0"`，字段契约与输入 JSON 示例 `D6Input` 详见 [../scripts/README.md](../scripts/README.md) §2.1，底层受控表契约详见 [../data/README.md](../data/README.md)；上述相对路径基准为公开库 `templates/` 目录，复制至本地受控区实填时仅在本地运行，不入公开仓）。本地引擎将结合目标年 `D2-A/B/C/D`、`D3-A/B` 与公开库 `D5` 字典及 `L2–L4` 卡片，输出去伪备选后的《冲稳保 40 专业组志愿方案》与《4–10 年培养与职业主备路线图》。

---

## 维度一：客观报考基线、CHC 学科负荷底线与 `D2-B` 章程体检退档码

| 字段项（对齐 `dim1_academic_physical`） | 本地实填槽位（公开库保持空白） | 下端串联关卡用途 |
| --- | --- | --- |
| **目标报考年份与生源省**（`target_year`） | `（本地填写目标年份与省份代码，公开库留空）` | 强制绑定目标年有效招生章程 `D2-D` 与毕业入职时钟（`T+4 / T+5 / T+7 / T+8`） |
| **科类与 `3+1+2` 选科组合**（`track / subject_combo`） | `（本地填写物理或历史及再选两科，公开库留空）` | 校验 `D2-A.subject_req`（无损覆盖双科及 `PHY_CHEM_BIO` 物化生全选等三科合取枚举；未识别原文转人工复核、严禁压宽条件），不符即触发 `VETO_SUBJECT_MISMATCH` |
| **高考总分、等效位次与单科/语种**（`student_rank / subject_scores / foreign_language`） | `（本地填写总分位次及语数外单科分与外语语种，公开库留空）` | 输入 `D4` 超额漂移接口（命中待核断裂年自动降级保守上界）并核对 `D2-D` 单科语种线 |
| **数理与外语真实负荷耐受度**（`math_physics_load_tolerance / foreign_language_proficiency`） | `（本地填写 high / medium / low，公开库留空）` | 基于高中三年客观学业稳定度校核微电子/工业软件强数理课表或全英合办负荷（零 MBTI） |
| **`D2-B` 高考体检受限条款代码**（`physical_limit_codes`） | `（本地填写体检指导意见受限条款代码，无受限填无，公开库留空）` | **仅与高校当年章程 `D2-B` 退档条款比对触发 `VETO_PHYSICAL_LIMIT`；严禁把企业招聘 `D5` 用工色觉/夜班风险提示混作退档红线误否决整个专业组** |
| **已获多元特殊通道资格** | `（本地填写强基/综评A或B/军警政审体测/招飞/农村专项资格，公开库留空）` | 开启 `3.2.*` 与 `4.2.5` 多批次锁档时序协同筛查 |

---

## 维度二：家庭财务硬上限与长周期培养缓冲力

| 字段项（对齐 `dim2_financial_horizon`） | 本地实填槽位（公开库保持空白） | 路径剪枝用途 |
| --- | --- | --- |
| **本科年度学费硬上限（元/年）**（`max_annual_tuition_cny`） | `（本地填写年度学费人民币上限整数，公开库留空）` | 暴露集 `S` 内任一专业超上限即触发 `VETO_TUITION_CAP` 整组否决 |
| **本硕深造时间与经费支持度**（`grad_school_budget_tolerance`） | `（本地填写 full_support / conditional / bachelor_direct_only，公开库留空）` | 若选仅支持本科直就：仅当主动目标集 `T` 全部目标专业的全部可达主路径均刚性要求硕博/规培时触发 `VETO_DEGREE_MISMATCH` 整组否决；`T` 含本科直就主路径但暴露集 `S` 含刚性深造/未知成员时拦出保底池 |
| **毕业初低起薪爬坡缓冲年限**（`early_low_pay_buffer_years`） | `（本地填写可承受缓冲年数 0–5，公开库留空）` | 校准临床规培（`5+3+X`）、重装现场学徒期与脱产考公考证承受力 |

---

## 维度三：稳态弹性底线、地域半径与 `2B` 双层排斥集

| 字段项（对齐 `dim3_preference_boundaries`） | 本地实填槽位（公开库保持空白） | `2B` 整组否决与 `water_level` 水位精算用途 |
| --- | --- | --- |
| **体制稳态 vs 产业弹性底线**（`stability_elasticity_floor`） | `（本地填写 public_soe_priority / balanced / market_elastic，公开库留空）` | 匹配 `4.1.4` 十维协商与 `4.3.*` 一级换序分支 |
| **目标就业地域与驻场耐受**（`target_job_regions`） | `（本地填写目标就业城市圈及是否排斥远郊驻场倒班，公开库留空）` | 配合 `D4` 跨省多样性召回（防长三角盲目扎堆）与 `D5` 工作场景提示 |
| **A 类：绝对排斥硬红线专业与 7 类场景红线**（`hard_redline_majors / hard_redline_scenarios`） | `（本地填写绝对排斥的 6 位代码或标准场景枚举，公开库留空）` | **阶段一整组一票否决**：按当年 `D2-D` 模式裁定暴露集 `S`（全组 `S = G` / 已核子集 `S = T ∪ (A \ E)` / 已核书面不调剂 `S = T`，大类核该校当年分流集）扫描，命中即 `VETOED`；分流集不完整或字段未知置 `unverified_redline_block_safety=true` 拦出保底池 |
| **B 类：一般弱偏好专业集**（`soft_dislike_majors`） | `（本地填写非首选但未触底线的 6 位代码，公开库留空）` | **阶段二 `water_level` 水位区间分级**：仅当同口径组内位次分布或区间证据唯一锁定分位档时输出对应档位（`top` 放行，`low/bottom` 拦出保底池）；仅知最低位次与人数致区间跨档或字段缺失一律置 `unknown` 拦出保底池 |

---

## 维度四：家庭共识状态、逐组主动填报绑定与认知防偏必检四问

- **亲子核心分歧记录**（`family_disagreement_topics` / `out_of_province_willingness`）：`（本地记录亲子在跨省就读、学校光环、电网体制 vs 专精特新制造上的分歧点，公开库留空）`
- **逐组主动填报专业集合与主备配对绑定**（`candidate_group_targets[]` + `candidate_pair_bindings[]`）：
  - 在本地 JSON 实例中按归一化五元组键唯一声明每组主动填报序号集合 `T`（缺记录或重复组键自动回退全组最坏暴露 `S = G` 并阻断保底），并显式绑定主备 `(primary, backup)` 路径供 `D6` 执行正向白名单四维冲击核验（按四级优先序区分单维与整对：非法绑定置 `unknown_blocked`；合法绑定已知共损先判 `warn_shared_failure_points` 并披露单维 `unknown_blocked`；零已知共损含未知维置 `unknown_blocked`；仅四维全 `pass` 标独立）。
- **填报前认知防偏必检四问（对齐 `debias_checklist_ack` 4 项布尔确认，逐项勾选）**：
  - [ ] **防“最低分锚定”偏差（`no_min_score_anchoring`）**：是否已确认往年专业组最低分对应组内末位冷门专业而非王牌专业，绝不压线裸冲高危混编组？
  - [ ] **防“长三角扎堆”溢价盲区（`no_yrd_clustering_blindspot`）**：是否已对照 `D4` 召回的外省同分段高一档次（985 / 原部属 211）纯净硬工科组购买力差异？
  - [ ] **防“盲信进校转专业”幻觉（`no_blind_transfer_assumption`）**：是否已核验保底组的真实转出转入获批分母及中外合作/强基/定向明文禁转条款，不把低概率转专业当救命稻草？
  - [ ] **防“假独立双保险”盲区（`no_pseudo_independent_backup`）**：主攻与 `Rank 3` 备选配对是否已通过 **`D6` 正向白名单四维独立冲击核验**（未共享双电网/医保/财政同一付款池、未捆绑同一专业组承受同一次调剂、未共卡单一刚性考研或同张法考/医师执照、且整对状态达四维全 `pass` 而非 `warn_shared_failure_points` 或 `unknown_blocked`）？
