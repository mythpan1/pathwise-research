# 独立审核归档：PR #368 base integration R2

- PR: https://github.com/mythpan1/pathwise-research/pull/368
- 原审核评论: https://github.com/mythpan1/pathwise-research/pull/368#issuecomment-6646850198
- 被审版本: H2 `b85301e9e952541868ccabb35090d1e3b8520a22`，base `9a1cea6158544a39ed33e5baf10ef0335fd41200`。
- 结论: 精确冻结的最小基线衔接建议采用，阻断 0 项；仅复核 #367 合并后 coverage 同插点衔接及作者记录，没有重审未变研究内容。
- 归属与边界: 以下是原独立审核者对 H2 发布的普通 PR 评论，按原字节保留；不是 GitHub APPROVE，也不是合并。原 R1 评论仍独立归档于本批前一记录。
- 原评论正文: 4205 bytes，SHA-256 `2504109201b6b54a55f5603bcdfc1cc32aa36e2ae1168dffb64060e6a2aca12f`；远端回读与本地正文逐字节相同，原文无末尾 LF。

---

Independent review | head: b85301e9e952541868ccabb35090d1e3b8520a22 | reviewer run: REVIEW-20261104-njau-public-service-trade | verdict: 建议采用

本次为原独审对最小基线衔接的受影响范围复核，0阻断。原v1 R1已建议采用、0阻断；N1只是已在v2处理并通过窄核的非阻断措辞精度提示。本次因PR #367先合并而处理coverage同插点，不是研究结论返工或初审失败。审核者未参与作者编写、发布或合并；请求Astra/ultra，实际模型/强度元数据unknown。普通评论不等平台APPROVE。

## H2及保留范围

fresh PR #368为open、非draft，head为本H2，base/main均为9a1cea6158544a39ed33e5baf10ef0335fd41200；mergeable=true、mergeable_state=clean。H2树为45b635e5c296b77ebbc6aedc29e341ca6b336914，实际双亲依次为旧H 8319152970d17580767976a11f658b2398c43d9d与新main 9a1cea6158544a39ed33e5baf10ef0335fd41200，保留双方祖先。

独立读取远端五件，字节、SHA-256和计算Git blob均匹配已审base-integration-20261105冻结稿。冻结清单SHA-256为b401b561408a4eb30edfba76ff60067c72b0a0c4675311296a8a3eb104b9107d；本地受影响复核报告SHA-256为348008fd58dc551d8f5683bc6d22f49fd64c91eaea859dbce1aedf1951cf3e1f。

| 路径 | 字节 | SHA-256 | Git blob |
| --- | ---: | --- | --- |
| research/admissions/jiangsu-njau-social-public-trade-sources.json | 6402 | d0d0af4fe432ee46d6c238fe4a793f9e04832bf171d4d4f945178fc32510691e | 59f34ded09f9a3646155bd64cc14f64736a6f582 |
| research/admissions/jiangsu-njau-social-public-trade.md | 15037 | d8c57b6502ea679f0c151fd496d6758e836ae59d5c19360096452c2b1de45014 | a9cffba0c85d4629ac1014ed9985af67148838f6 |
| research/admissions/public-sociology-careers.md | 3505 | 94da51e42b8539e106d41a22166ae2a4df7d11fcbb5c4c7684dfbddc5e18f65d | 0f22680cc81001c8d7e7f7d2c13b5173af635b6d |
| research/coverage.md | 15929 | 988fadd897c6dd70e3db9f0e8eb6b2717bf7c11c8d2a4e6356b783b84af607de | 95651b36d67c3240c69693af7fc656cb9a3dd381 |
| work/runs/njau-public-service-trade-author-20261104.json | 5353 | 0ef06656e7ecf794a9c655db5d26619f45940ccdbb7c25ea6a385e078a42ba16 | 29b550a93f5e0ccbbcf08b22fdebfba63ceba730 |

独立比较两份非截断完整Git树：新main树eefeef44eea7930557b33d60355c574dc708fde2到H2仅上述五叶不同，其余全部leaf的路径、blob、mode、type一致，PR #367的其他成果未被撤销。报告、来源索引、专题导航与已审v2字节不变；coverage在完整保留新main后仅加南农v2原字独立同级段，苏州/南农段各一次，旧历史及F1—F6/分母不变。作者record仅追加真实发布基线及衔接说明，研究输入基线和审核历史未改。

原H的[独审评论6646380442](https://github.com/mythpan1/pathwise-research/pull/368#issuecomment-6646380442)fresh读回与原始正文逐字节一致，继续保留为原版本已审事实。本评论将实际H2变动及影响明确绑定，不把旧H批准自动继承到新版本。

## 实际CI及内容边界

[validation run 41946728408](https://github.com/mythpan1/pathwise-research/actions/runs/41946728408)绑定本H2，path为.github/workflows/validation.yml，状态completed/success；[validate job/check 126980675494](https://github.com/mythpan1/pathwise-research/actions/runs/41946728408/job/126980675494)亦success。实际日志执行python3 -m unittest discover -s tests -v，9 tests，OK。checkout为合成提交1dec96d826c0ad3e03491f9311c9d125a36388ec；已核其父为新main与H2、tree与H2同为45b635e5c296b77ebbc6aedc29e341ca6b336914。控制器测试不替代研究事实审核。

此次只核基线衔接及影响，没有重新研究未变报告，没有新取源或2026录取采集。原来源限制仍成立：仅既得岗位转换文字，原PDF403后另XLS403再全部停止；不恢复受拒附件/替代源访问，不认证原表单元格、个人/未来资格或未知付款链。

当前无内容阻断；本结论仅适用于本H2及上述已核基线。后续可以忠实归档原H与本H2两条实际评论，归档后最终F仍须另核只含真实审核记录及其实际门禁。本评论未执行归档、合并或正式APPROVE，也未裁定管理保护或其他平台批准。