# 审核归档：LOCAL-STORAGE-GRADUATE-ENTRY-20261103 / r1

- 日期：2026-11-03
- 任务Issue：未建立；沿稳定LOCAL成果路径，不创建或模拟Issue。
- PR：[PR #342](https://github.com/mythpan1/pathwise-research/pull/342)
- 被审基线：`3cf14e514c9ce09d82cad140e767da1b3b766c7e`
- 被审成果H：`5ee7028c29bf11cc53f2bb58942be5aa3570ff9c`
- 作者/发布：advance_existing_career_paths
- 独立审核运行：review_storage_entry_update，未参与编写或发布。
- 原评论：[6593386523](https://github.com/mythpan1/pathwise-research/pull/342#issuecomment-6593386523)
- 以下忠实保存实际评论原文；归档不是作者内容审核，不是GitHub APPROVE，不代表F门禁完成或已合并。
- 评论首次写入在执行前被明确拒绝，没有评论ID且未重试/换路；随后用户对这条具体评论明确批准，原审核者先核H未变、评论尚未发布，再经相同连接器单次重试成功。实际评论已逐字回读，与已批准草稿完全一致；不将首次拒绝写成成功。

## 实际H审核评论原文

Independent review | head: 5ee7028c29bf11cc53f2bb58942be5aa3570ff9c | reviewer run: review_storage_entry_update | verdict: 建议采用

基线：3cf14e514c9ce09d82cad140e767da1b3b766c7e。审核者未参与研究正文、来源索引或发布记录编写。本评论是普通内容审核意见，不是 GitHub APPROVE，也不执行合并。

实际检查：
- 独立回读 PR 元数据、完整三文件 diff 及精确 H 的文件内容。PR 为 open、非 draft；head/base 与交接一致。三文件范围未扩大；两份研究文件与本地已审最终稿逐字节一致。
- 正文 SHA-256：9efb5c4f6331551ee0da4de84583934f619de57c05f8fcac0e6a2c60b52e096d。
- 来源索引 SHA-256：0b4340e4bc5d2bd0280316be2cd517c20f48d1602a64ad1efd7e6862482c64cb。
- 运行记录 SHA-256：1dbba6c982055d4e4e4df895069f5cd42076b8596d0a348dd372f550c40654e3。该记录中的 v1 建议采用、N1 最小时态修订及原审核者窄复核结果与实际审核历史一致；未把作者自查当独审。
- 已独立解析受控留存的湖南大学原HTML：[2027校招页](https://scc.hnu.edu.cn/detail/career?id=715358)同一 career 对象包含批次标题、career_talk_id=715358 与 jobs[14].publish_id=2384153，模板链接也绑定两个ID。具体岗的ID、名称、学历、地点、职责和专业要求与旧J2原HTML六项完全一致，不是公司通用专业清单或跨页拼接。
- 独立正常阅读[华科同批次页](https://job.hust.edu.cn/zjob/2434236.htm)，确认测试/深圳苏州/建议通信；该表没有此岗学历与任务细则，正文仅作同源参照，不计第二雇主或独立样本。审核者未下载该页HTML或重试作者遇到的403。
- JSON可解析、来源ID唯一；J2-C原HTML与J2-H定位摘要的字节数/哈希相符。原件未包含在本PR三文件中。

研究判断：
2027批次曾公开列具体本科光储测试岗的证据缺口已补。产品测试为主目标、本人愿读通信本职并核所需能力时，通信先于软件进行目标核验，作为有边界的条件方向成立；应用开发仍软件优先。没有据此改变真实接受声明、全组六成员状态或志愿顺序。正文保留2031接收与训练条件、2037迁移限制及入口关闭/自动化/熟手集中/无已确认备选的失败分支。

阻断：无研究内容阻断。
非阻断N1：已关闭。v1到最终稿唯一变化是J2“前批读取、本次沿用核批次关联”的时态澄清，索引未改，未改变事实或方向。

CI实际观察：
独立读取 run 41560556587，path=.github/workflows/validation.yml，event=pull_request，head_sha与上述H完全一致，status=completed、conclusion=success；validate job 125669867891 及 Test review state transitions 步骤均成功。[运行结果](https://github.com/mythpan1/pathwise-research/actions/runs/41560556587)。这是平台运行回读，不冒称审核者重跑了作者本地自查。

限制：
- 批次关联不证明零经验必录、带教兑现、当前名额、2026首次建岗、新增人数或2031持续接收。活动时间、详情展示发布时间和旧create_time不可互代；原因仍未知。
- 旧培养、政策、人口统计及费用依冻结基线复用，本轮没有全量重核；没有采集录取数据、联系HR或补写个人偏好。
- 本运行可见 reported_model=null、reported_reasoning=null、verification=unknown；当前运行上下文及角色状态回读未提供这两项运行报告。记录中的 Astra/ultra仅为启动请求，不能认证后端实际身份。
- 此结论只绑定上述H；后续变更须按影响复核。未核验全部分支保护、规则集及独立账户批准条件，不宣称平台合并门禁全部满足。
