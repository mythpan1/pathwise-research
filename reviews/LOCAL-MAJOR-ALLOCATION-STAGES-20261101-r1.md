# 审核归档：LOCAL-MAJOR-ALLOCATION-STAGES-20261101 / r1

- 日期：2026-11-01；[PR #308](https://github.com/mythpan1/pathwise-research/pull/308)，分支 `research/major-allocation-stages-20261101`。
- 被审基线：`1f4eb81ee70a7d65f64f95937f73dcb3edb1323d`；被审成果 H：`6d9849245b301eeffd2ec750fac88f86d4ce56f7`。
- 真实独立审核来源：[原评论6556239342](https://github.com/mythpan1/pathwise-research/pull/308#issuecomment-6556239342)。审核者 `/root/review_mechanical_path_card`；作者 `/root/build_mechanical_path_card`；父调度 `/root`。
- 以下原评论逐字代录，由作者运行机械归档，不是作者自审。模型、思考强度及检查执行边界依原文保留，不补造认证或结果。
- 提交前本地v1预审、v2变化复核及实际H映射的顺序见原评论；非阻断增强已落实，无未解决内容阻断。归档提交只新增本记录，研究正文不变。
- 归档后须核H→F差异、忠实性及精确最终head检查；本记录不是GitHub APPROVE，也不预填合并结果。

## 真实独立审核评论正文（完整代录）

Independent review | head: 6d9849245b301eeffd2ec750fac88f86d4ce56f7 | reviewer run: /root/review_mechanical_path_card | verdict: 建议采用

## 版本、范围与独立性
- 任务：LOCAL-MAJOR-ALLOCATION-STAGES-20261101；PR #308。
- 被审基线：`1f4eb81ee70a7d65f64f95937f73dcb3edb1323d`；成果 H：`6d9849245b301eeffd2ec750fac88f86d4ce56f7`。
- 作者／发布运行：`/root/build_mechanical_path_card`；审核运行：`/root/review_mechanical_path_card`，父调度 `/root`。我未编写、修改或发布被审正文；提出审核建议后由作者修订，我再独立核对。
- 原生子智能体运行；本运行模型及思考强度报告未暴露，reported 为 unknown，不以角色名称认证后端身份。
- 已核PR head/base、远端全文与compare：仅 `research/admissions/major-adjustment-position.md`，+36/-0，1个提交。远端文件blob `303c194ff23af4ce746728aee65f03f90725a0f6`与本地已审v2的git hash-object一致；v2 SHA256为`4811e93c364fa0a6983fbceed28e9fe3bb2800759fdb7772adc52531ac77f7c2`。删除新增节后原文与基线一致。

## 真实预审与修订过程
1. 先审提交前固定v1，SHA256 `fd849f9221a30e4c708006ad1e38700e50541231cce98ebb99cfd8e4201c973b`：无阻断；建议加强江苏退档后果与服从范围的明确性。
2. 作者采纳后审v2。将L41、L47还原为v1文本后可重得v1完整哈希，确认仅两处修改。增强已准确落实，不改变三人基例。
3. 此前结论仅绑定本地哈希；本次完成远端映射后才将结论绑定实际H，未把本地预审冒称此前已完成提交版本审核。

## 实际规则与案例核对
已亲读两份官方原文，未采集录取结果、位次或真实专业计划：
- [南京邮电大学2026普通本科招生章程](https://zs.njupt.edu.cn/2026/0521/c2562a302356/pagem.htm)，页面标注2026-05-20，第四章第十二条：支持专业志愿先按成绩安排、调剂最后处理，同组内合资格且未录满专业方可调剂；不服从且所报不能满足者退档；不退档承诺保留已进档、服从及符合要求的前提。
- [江苏省教育考试院《志愿填报热点问题》](https://www.jseea.cn/webfile/index/index_zkxx/2026-07-25/7486762353556459520.html)，2026年页面，第5问支持退档后不再补投该批次平行志愿后续其他组；第8问支持服从涵盖该校本批次本组全部专业，不只是已填几项。正文未把服从解释为免除专业条件。
- L27–37：三人、三专业及每专业1名额均明示合成；甲→A、丙→B、乙最后调C符合分阶段机制。没有把高分待调剂者提前安排到B。
- L41–43：乙不服从则退档；增报B后乙→B、丙最后调C；不符合C条件则原调C结论失效，三个变体正确。
- L19–23、L47–49：明确单校单年、普通类及已进档边界，未扩为全省全国统一算法；未补造全部余缺匹配细则、实际录取概率或未来年份保证。

## 问题与限制
无未解决阻断；v1非阻断增强已在v2落实。未核真实考生资格、实际专业组名额、余缺和录取结果，不以本例承诺个体录取；将来实际填报仍需当年逐校规则。
本次未运行作者的小程序或本地单元测试，作者自检不记作我的执行结果。

## CI与后续边界
已读取精确H的[Knowledge review checks / validate](https://github.com/mythpan1/pathwise-research/actions/runs/41294098609/job/124811211402)：completed / success，Test review state transitions步骤成功。CI不验证招生事实；本评论不是GitHub APPROVE，不替代平台保护、独立账户批准或合并授权。
本结论仅覆盖上述基线与H。若仅追加真实审核归档，再核归档忠实性及最终head；正文变化须复核受影响内容。本运行不改正文、不合并。
