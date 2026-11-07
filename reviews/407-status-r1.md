Exact reviewed head: 64d208619a86e0b87ccb54d7f75edea6497be596
Original review comment: https://github.com/mythpan1/pathwise-research/pull/407#issuecomment-6714262195
Source report SHA-256: bb5d261beeec97097cdf4f036803b175ed4d813501065334c87ec290fbb6e56b
This archive preserves the source report text exactly and does not extend the review scope.

Independent review | head: 64d208619a86e0b87ccb54d7f75edea6497be596 | reviewer run: LOCAL-POSTMERGE-406-STATUS-INDEPENDENT-REVIEW-20261107 | verdict: 需修改

基线 main：56def2b594411e466b3e5a0e8935320a131ceeba。本人未参与本次候选编写、打包或发布；接续同一独立审核任务完成发布集成复核。本评论只绑定上述 H，不是 GitHub APPROVE，不是合并授权或平台门禁全部通过的证明，PR #406 的旧独审不覆盖本次修正。

已亲核实时 PR、main、H、完整14路径差异和远端文件字节。12个状态/依赖文件逐字、SHA-256及Git blob均等于已审本地R2，绑定manifest SHA-256 9715fd5a4921f39b8263aebaea398a8a4d19683b397cc4153a323ca80b3411c7、patch SHA-256 b12d3f4d05d93afe5774e355bccf4f78bfdecd219e99fa204c036aff3d327fe8、本地独审报告SHA-256 677d13b72eeb8107319a582813988aca6f6765df4fde5ed9f477e7e5a8ce2bcd。南京两处欠审尾句和玄武状态指针均已修好；没有研究事实或判断变化。全国sources与南京B5哈希精确匹配，旧scope_revision、本地R3审核、reviews/405-r1.md、reviews/405-r3.md及旧work记录保持不变。两棵完整tree的其他非目录条目没有额外差异，14文件完整补丁已逐项重建核对；未变研究原文不重抓。

**PB1：新增发布留痕仍缺必要归属与事后补录边界。** 仅涉及 work/runs/ISSUE-406-status-publication.json 和 work/steps/ISSUE-406-status-publication.jsonl。远端steps目前只有S1—S5五条completed摘要，未关联run_id、真实记录时间、started或posthoc性质及verification；也没有保留已存在于本地记录的上传准备失败，以及后续PR交审/检查结果。run已绑定manifest/patch并诚实保留模型unknown，但未串起实际状态修正作者、本地独审的输入输出版本及所读规则。CI成功不补足这些要求。

按 docs/agent-provenance.md 作最小补录即可，不需改12个正文文件：
1. 保留现有run字段值、steps S1—S5原文、原本地R1/R2产物和失败记录，不删除或重写旧记录。可在这两份新增文件内追加关联字段/后续步骤；标明哪些先前条目只是事后摘要。
2. 给实际作者/独审/发布的稳定run或actor、职责、父/来源关系及已有manifest/review哈希；明确本地材料哪些可核、哪些未上传。注明所读规则的完整基线和路径。模型请求/报告分别写来源，无法核的reported仍为null/unknown，不用默认配置补齐。
3. 新增步骤绑定run_id、任务、前序/原步骤，写实际补录时刻recorded_at与posthoc=true。过去操作时间不能核实就填null并说明；不得倒填过去的started或执行时间。本地若确有事前started记录，只陈述可核的存在与边界。
4. 追加上传准备失败且未发文件写调用、随后成功回读、H交审与指定检查的真实结果和输出版本；区分操作完成和verification。保留Issue尝试被拒且未重试的历史，不新建、重开或修改Issue。只提交脱敏摘要/哈希，不上传机器绝对路径、原始运行日志或完整会话。

我独立核得当前H的 .github/workflows/validation.yml run 42423374784 与 validate check-run 128556380852 均completed/success；另一个可见同H check-run 128555931324也成功。两者annotations_count均为2，详情未读，不声称零告警。审核前可见PR讨论、正式reviews及inline comments为空，没有其他已存在内容阻断；PR为open、非draft、未合并，交审标记绑定H。

验收：同PR只补上述两份新增记录及交接，12个正文blob必须原样保留；给完整新H后复核记录、差异及精确H检查。该补录不是“仅增加本次审核归档”，新H不能沿用本评论作为采用结论。未核完分支保护、所需独立账户批准及全部合并条件；合并者仍须按最新平台门禁执行，不得绕过。请求配置由协调者提供为gpt-6-astra/ultra，后端实际元数据不可核，reported unknown。
