# 知途研究 v3（Pathwise Research v3）

**一句话定位**：一套将中国未来十年上端宏观变迁（**国家政策 × 产业变迁 × 人口结构变化**）经中游付款链与培养实得转换，端到端闭合落地至下端（**江苏生源高考志愿填报与 4–7 年大学/职业规划**）的社会科学推演与决策底座。

- **当前状态**：`v3 框架骨架就绪（单一当前态，待按 Batch 1–4 分批填充主干槽位）`
- **总体实现蓝图**：[docs/architecture-v3.md](docs/architecture-v3.md)
- **主干防跑偏总表**：[index/master-map.md](index/master-map.md)

---

## 一、上下端四层闭合导览

知途研究 v3 摒弃“宏观热词直跳热门专业”的粗糙断言，也拒绝“因远期缺微观铁证而悬停于无主次分支”的防御性空转，通过四层双向架构实现上下端咬合：

| 层级与对应目录 | 核心职能（解决什么问题） | 关键内嵌闭合机制 |
| --- | --- | --- |
| **L1 上端外驱层**<br>[research/l1-drivers/](research/l1-drivers/README.md) | 交叉耦合国家政策、产业变迁与人口结构三主线，输出锚定地域与队列的外驱张力信号 | 官文潜台词与预算深解 + 权威产业年报 + **人口官方基准锚与商业财报/基层旁证蒸馏** + `target_regions` 地方分化校准 |
| **L2 中游传导与职业规格桥**<br>[research/l2-careers/](research/l2-careers/README.md) | 按**职业岗位族（多对多）**把宏观变化翻译为目标毕业队列与目标就业地的真实校招规格 | **三只时钟对齐**（政策期 / `graduation_cohort` 毕业窗 / 复利窗）+ 付款/组织/带教穿透 + **四维独立备选冲击核验** + 确定性梯度承压阀 |
| **L3 培养兑现与路径映射层**<br>[research/l3-pathways/](research/l3-pathways/README.md) | 对接教育部本科专业目录代码、本硕准入分流、江苏普通批可及院校实得与大学 4–7 年执行轴 | **`1B` 结构代理保守推进（冲突即标未知）+ 招办核实单** + 官网 `403` 第三方交叉验证降级 + 下游硬门槛反向回灌 |
| **L4 下端志愿与职业决策层**<br>[research/l4-decisions/](research/l4-decisions/README.md) + 本地受控区 | **`3B` 公私双模收口**：公开库沉淀锚定基准前提的 `Rank 1–3` 主序；本地受控区合成志愿表与路线图 | 本地挂载四维个体/家庭约束卡（零 MBTI）+ **`2B` 硬红线整组否决 + 非红线组内 `water_level` 相对水位与分段超额漂移分级** |

---

## 二、仓库目录导航（单一当前态）

| 路径 | 角色与内容定位 |
| --- | --- |
| [AGENTS.md](AGENTS.md) | 六岗协作边界、防投毒采集 + GitHub PR 双关审稿闭环、单态维护与公私隔离红线 |
| [docs/architecture-v3.md](docs/architecture-v3.md) | 总体实现框架蓝图（全景拓扑、四层接口、上下双向跑通路径与 `D1–D6` 数据契约总览） |
| [index/master-map.md](index/master-map.md) | **核心防走偏抓手**：L1–L4 共 43 个主干槽位（`slot_id`）版图、`Batch 1–4` 分批路线与立题三问闸门 |
| [index/routing.md](index/routing.md) | 按需加载路由表（立题排重路由 / 自上而下拐点刷新路由 / 自下而上个案倒推路由） |
| [index/manifest.json](index/manifest.json) | 全库知识卡片机器索引、时效属性（`evergreen` / `volatile`）与上下游重审依赖表 |
| [research/](research/l1-drivers/README.md) | 四层直映公共知识资产库：`l1-drivers/`、`l2-careers/`、`l3-pathways/`、`l4-decisions/` |
| [templates/](templates/driver-signal.md) | 5 份绑定 `slot_id` 的标准化单态卡片模板（含 4 份公共研究卡与 1 份本地空白四维约束卡） |
| [data/README.md](data/README.md) | 本地受控江苏招生底表、组号跨年映射与专业映射字典的字段级数据结构契约（公开库不含原始表） |
| [scripts/README.md](scripts/README.md) | 位次分段超额漂移、组内 `water_level` 水位分级算法契约及 [scripts/validate_framework.py](scripts/validate_framework.py) 校验说明 |

---

## 三、三层资产物理边界铁律

1. **GitHub `main` = 唯一当前态最终版权威底座**：仅存放通过 GitHub PR 双关审稿（红队挑刺 + 独立审核，审稿过程留 PR 评论不入 `main`）且经用户确认合入的去个案化公共成果。全库严禁叠放过期历史快照，历史演进交由 Git 提交记录管理。
2. **网页版 Deep Research + 长期纯净 Gemini Notebook = 研究过程工作台**：Deep Research 仅用于前置宽面侦察拆解切入点与待回溯原件清单（报告留本地侦察区，不入核心本）；所有入本资料须先抓取至本地受控原料区完成硬主体防投毒初筛并贴血统头标，再直传 Notebook 生成过程《加工简报》。过程线索未经回核官方一手原件不得直接升格入库。
3. **本地受控工作区 = 招生底表与个案隐私闭环区**：江苏历年及新增投档/专业分底表、组号拆并明细、真实考生四维约束卡与个案志愿规划报告 **100% 留存本地受控目录**（由 `.gitignore` 与 [scripts/validate_framework.py](scripts/validate_framework.py) 双重拦截），严禁上传公开仓库或传入云端 Notebook；历史 v1/v2 归档库仅作只读参考按需吸收。

---

## 四、先搭骨架、分批对槽填充原则

为防止研究滑向热门新闻跟风或边角知识堆积，全库严格遵守 [index/master-map.md](index/master-map.md) 确立的推进纪律：
- **对槽准入**：任何新课题必须绑定唯一主干 `slot_id` 并通过「立题防细枝三问闸门」；
- **循序合龙**：严格按 `Batch 1（人口与政策底盘）→ Batch 2（产业与职业入口穿透）→ Batch 3（专业培养与江苏院校实得映射）→ Batch 4（跨路径公共决策收口）` 推进，未经特批严禁跳层散抓。
