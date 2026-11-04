# 独立审核归档 | LOCAL-lab-testing-choices-20261104-r1

来源：[PR #360 评论 #6622967297](https://github.com/mythpan1/pathwise-research/pull/360#issuecomment-6622967297)
评论时间：2026-11-04T04:58:25Z。
审核运行：lab-testing-independent-review-20261104-r1（按评论原文记录）。
GitHub 评论账号：mythpan1；此普通评论不是 GitHub APPROVE，也不证明独立账号身份。
审核 head：1ceedbe1a152ea43c2f2550bf7637b38980c1b6a；PR base：8367d9f53c4fefa69c3f60b5d077ce4c4a7c11f5。

真实历史：v1 的 R1 结论为“需修改”；作者返工形成 v2，原独审者 R2 复核变化后建议采用。不得将 v1/R1 表述为一次通过。

原 H 评论正文：2829 UTF-8 字节；SHA-256 `9385133a8ec1fb7cd3a4d7a1a2004b4dd9b82ecb11b7eacdbffff76c13a12fc2`。

---

Independent review | head: 1ceedbe1a152ea43c2f2550bf7637b38980c1b6a | reviewer run: lab-testing-independent-review-20261104-r1 | verdict: 建议采用

原独审对冻结 v1 做 R1、对返工 v2 做 R2 窄复核后，本次将真实审核绑定 PR #360 的精确成果 H。未参与作者分析、编写或发布；请求配置为 gpt-6-astra / ultra，实际运行报告值未暴露，不能据请求值认证后端身份。

**版本与范围**
- 研究基底：f4b66553bac16b3c1020f4a4b2e1e43325019a1f。
- 当前 PR base/main：8367d9f53c4fefa69c3f60b5d077ce4c4a7c11f5；head：1ceedbe1a152ea43c2f2550bf7637b38980c1b6a。已读取正文中的精确 head 交接，PR 为 open、非 Draft、未合并且 mergeable。
- H 的实际差异恰为三件新增文件和公共卫生导航追加两行。四件远端文件的完整字节分别匹配已审 v2：
  - research/admissions/jiangsu-lab-testing-choices.md：SHA-256 d35df91954e54b3956a57ddbddbd409feea7ddd8856614c857bc801a254232eb。
  - research/admissions/jiangsu-lab-testing-choices-sources.json：SHA-256 cf98eba7d9fded4326192763eced464e401cd7332c0bf3aecd16ae63f65488dc。
  - research/admissions/public-health-careers.md：SHA-256 c27af5019a6abc6eb32b71578dc2cabccbf5b073941383e166a1d91e9a174eb4。
  - work/runs/lab-testing-author-20261104.json：SHA-256 2d38b4ed5e4a74612020bd1e34f1a3fd7f0bbd26a7f19a8e2b94a6283bf6cd80。
- 研究基底到当前 main 的3个提交仅涉及 #359 的风景园林/品牌比较等5个文件。本题11件相关规则及旧卡的 Git blob（含原公共卫生导航）全部未变，因此没有因无关基线推进重复内容审核。

**真实返工历史与处置**
- R1 对 v1 的结论是“需修改”，不是一次通过。阻断 B1 是当前结果只给核验优先、没有同一 P 下可用的路径基准；非阻断 N1 是招聘清单与实际录用的措辞区别。R1 内容 SHA-256：1819baad7654acf1c9535cd17e2b9be2252faf790ae3aa92ced8c73eb7ab21ef。
- 原独审 R2 对 v1→v2 变化及受影响主张复核后“建议采用”，B1关闭、N1已采用并关闭。现在有同一非用户前提 P 下的两目标并列主比较，分别说明任务、付款连接、训练与地区成本、报考前条件备选；S1/S2以新人实际分工差异打破并列，S3保留共同下调。并列不是断言两者同样好，先核哪边也不再代替路径判断。R2 内容 SHA-256：88ae46119c12df6b13e6ff568a34b015f0b12af2d984d9df9107047637661d8f。
- 本次远端字节及基线核对没有发现新增内容阻断或未关闭建议。原 v1/R1 与 R2 历史保持不变；作者自检未当作独审。

**采用范围与限制**
- P1是国家医保局解释页：产出整合、部分人工确认加收、联检折扣及数据质量约束，不是南京已经落地、雇主回款或增员证明。付款、设备集约、存量熟手与新人训练之间的未证连接仍是明示条件推导。
- J1完整分子任务与J1b精确专业/南京字段保持分记录，不拼成一条完全匹配岗位，也不计为两个雇主。J2是广州已结束且暂停的本科食品QC招聘例，不补2027届或南京。允许申请不等于实际录用；当前暂停不支持2031路径次位。
- 江苏调配与广州不是同一市场，不按薪资或公告数排收益；P不是用户偏好，固定南京时广州不充作已落实备岗。企业公告省略资格不推出医院临床免证，CNAS不当个人医疗资格，两专业不等同预防医学/公卫医师，也不保证互相直接任职。
- 2027入学只有实际四年才约2031毕业；2037观察实际毕业后经历，不默认连续就业或读研。旧61030/68339、组77094/859及11成员只作历史比较，专业机会、组投档、服从调剂和不服从退档分开，用户位次与成员接受仍未知。

**CI实际核验，不只读取绿标**
- 已读 [validation run 41774668891](https://github.com/mythpan1/pathwise-research/actions/runs/41774668891)：path 为 .github/workflows/validation.yml，event 为 pull_request，head 是上述 H，attempt 1 completed/success。
- 已读 validate job 126392127442 的完整日志及实际工作流。checkout 的是 synthetic merge cae8f31c6a7c53eb4c53dfb9ec0da178ea5f603f；另取 Git commit 核其两个父提交依次为当前 base 8367d9f53c4fefa69c3f60b5d077ce4c4a7c11f5 和 H 1ceedbe1a152ea43c2f2550bf7637b38980c1b6a。
- 实际命令为 python3 -m unittest discover -s tests -v，日志显示9项 test_review_controller 单测全部 ok、Ran 9 tests、OK。它们验证审核控制器状态转换，**不是研究内容、真实政策或职业前景验证**。

本次未重新联网取研究来源、未读取原CSV或恢复2026录取采集，也未验证实际培养、地方价格、未来招聘、具体临床资格或2031/2037结果。未核当前分支保护及其他最终合并门禁；后续归档或新 head 仍须核最终差异与精确版本检查。本条是普通角色签名审核评论，不是 GitHub APPROVE；本审核者不归档、不合并。
