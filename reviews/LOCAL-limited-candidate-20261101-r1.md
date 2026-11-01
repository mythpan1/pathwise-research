# LOCAL-limited-candidate-20261101：独立审核归档

- 范围：已发布历史可用性检查、有限合成候选接入已有情景与组内接受压力走查；不采录取数据。
- 基线：ae550ecf9340cf0399ae6d84d49147e8d514237f
- 冻结成果 H：71b7cf0b3f7862f3c019bbbad2271fcf47447696
- 作者/发布运行：/root/build_mechanical_path_card；独立审核运行：/root/review_mechanical_path_card。
- PR：[#317](https://github.com/mythpan1/pathwise-research/pull/317)。
- 以下由发布者完整代录真实[独立审核普通评论](https://github.com/mythpan1/pathwise-research/pull/317#issuecomment-6559094256)；代录不等于作者独审，不以共享身份或角色名称认证后端配置，实际模型/思考强度不可见。
- 保留真实v1 R1→v2修复过程及获准核验边界，不上传受控旧表、个人资料、错误v1全文或原始内部日志。评论不是正式 APPROVE。

## 原独立审核评论（完整代录）

Independent review | head: 71b7cf0b3f7862f3c019bbbad2271fcf47447696 | reviewer run: /root/review_mechanical_path_card | verdict: 建议采用

## 版本映射与真实 R1
- 审核者与作者分离；reported_model=unknown、reported_effort=unknown，运行配置不可见，不以角色标签代称平台批准。
- 已回读实际 H，base=ae550ecf9340cf0399ae6d84d49147e8d514237f；2 个顺序提交，仅新走查 +46 与原 #312 例导航 +2，无删除。
- 远端两文件全文与已审本地 v2 逐字一致。UTF-8 SHA256：
  - research/admissions/limited-candidate-retrieval-walkthrough.md：7744dbef9344d40b0fb1823a8d29c6a685f65080ba63044445ff8641ee21a613
  - research/admissions/bidirectional-path-comparison-example.md：20f82c81993edd3b889917143e282c4936930e9278355417d380d8f386d8ace6
- 本地 v1 有阻断 R1，并非初稿全部通过：L27 的 S2 已限定 A 新人入口不可接受，L37–38 却在 B 未确认/不接受后回到 P0 比较 A；P0 愿意就读/训练前提不能消去 S2 的职业限制。我要求纠正，作者 v2 仅修改这两行动列，已独立复核关闭：B 未知保留条件优先并补决定性条件；B 不接受时承认本集合无已确认可接受主方案，A 只在新增可接受技术入口条件下恢复备选，仍保留其他条件情景和待补候选。PR 返工记录真实，当前无剩余阻断。

## 实质增量与证据范围
本批不是新造宏观卡，也不是把 #312 改名：新增的是现有历史材料可用性检查、把已发布 #316 组织重组 S1/S2/S3 映射到固定 A/B，以及预算 AND 校区三变体对组级 ACCEPT 和当前返回结果的影响。原 #312 全组接受输入未被暗改。
本轮只核既有仓库证据与本环境指针存在性，不重新下载招生原件、不采新录取数据：
- 基线[江苏物理历史单元](https://github.com/mythpan1/pathwise-research/blob/ae550ecf9340cf0399ae6d84d49147e8d514237f/research/admissions/jiangsu-physics-reference.md) blob 68d8de152a0c57467f86a10883e55ce0cd6a6578：东南1102的2025普通本科物理06组化学657、07组不限再选654转述一致。组线不是专业线，未猜组成员或把它们当2027可报，不声称本轮重读官方表。
- 已读基线物理/历史两单元的受控 CSV 指针，并仅检查当前执行环境对应文件不存在，未读、复制或上传原表；不据此推断用户原设备没数据、其他候选不存在或旧底座无用。
- 原例 blob 38525e3205fcf92807f59a8b553d5b9a448c66f8、组织重组单元 blob 62964bce584061e66a93b131ecec683a69fd2778 与所引版本一致；原例仅加导航。历史招聘和原源核验沿用原批记录，未伪称本批重核所有原件。

## 条件比较与门槛
- L16–20 明确江苏2027合成选择、同一市场R、2031本科新人→2037观察，P0 仅是假设，A未枚举、B两成员仅合成，不包装成真实完整GROUP或有效保底。
- L26–28 保留 A/B 有方向且可反转的比较，并沿客户依赖检查共同失效；业务量不直接等于新人，核算与独立审计不偷换同任务、资格不互认。
- L32–40 与[契约3.3](https://github.com/mythpan1/pathwise-research/blob/ae550ecf9340cf0399ae6d84d49147e8d514237f/docs/planning-knowledge-contract.md)相符：条件全部满足仍保留条件标签；未知不是不满足；已知不满足不永久改写成员声明，组级输出不能遮蔽不可接受成员。
- 对[既有组决策](https://github.com/mythpan1/pathwise-research/blob/ae550ecf9340cf0399ae6d84d49147e8d514237f/research/admissions/major-group-decision.md)的分阶段引用有适用条件，不确认为2027规则，不承诺退档后自动接上本轮其他组。
- 缺实际考生、完整候选和当年条件时不捏造可提交清单，但未停止有条件规划；R1修复后也不为填满梯度强选失效A。此为手工走查，不证明自动检索、真实回测或预测准确性。

## 精确 H 检查
已回读 [validation run 41314887381](https://github.com/mythpan1/pathwise-research/actions/runs/41314887381)：.github/workflows/validation.yml、pull_request、head_sha 与 H 一致，completed/success；validate job 124872705608 与 review state transitions 步骤成功。check-run 显示 2 条 annotations，明细受现有连接器读取限制未读，不称零警告；CI 不替代研究核验。

本普通评论为精确 H 的真实独审，不是正式 APPROVE；若追加机械归档，仍核最终 F 的唯一差异、逐字忠实性与精确检查。未修改研究、未合并、未新增采集。
