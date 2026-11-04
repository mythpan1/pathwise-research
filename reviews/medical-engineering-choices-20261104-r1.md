# LOCAL-medical-engineering-choices-20261104-r1

- Date: 2026-11-04; exact comment timestamp was not exposed by the connector.
- PR: https://github.com/mythpan1/pathwise-research/pull/364
- Branch: research/medical-engineering-20261104
- Base commit: fd640406b2fa6230b77799a75652432cc0683f95
- Reviewed head: b0e357d346aa02a6165ccfffe0ca84bc84b24aa5
- Author run: medical-engineering-author-20261104
- Independent reviewer run: medical-engineering-independent-review-20261104; requested gpt-6-astra / ultra, actual model and effort unknown.
- Original GitHub comment: https://github.com/mythpan1/pathwise-research/pull/364#issuecomment-6630073678
- Original comment body SHA-256: 93fe2766ac04cc06a2d43758ea459e2e41504c949ab007113ec826ff6c65288e
- The comment body below is archived verbatim. This record is an archive, not a GitHub APPROVE or merge.

## Original GitHub review comment (verbatim)

Independent review | head: b0e357d346aa02a6165ccfffe0ca84bc84b24aa5 | reviewer run: medical-engineering-independent-review-20261104 | verdict: 建议采用

## 精确版本与独立性

- 基线：fd640406b2fa6230b77799a75652432cc0683f95。本次fresh回读PR #364为open、non-draft，正文交接H一致，变更仅下列四文件。
- 本人是与作者、收集者和发布者分离的独立审核运行。请求gpt-6-astra / ultra，实际reported model/effort未暴露，记unknown，不作后端认证。普通角色评论不是GitHub APPROVE或平台要求的独立账户批准。
- 逐件从远端H读取UTF-8完整内容，与已审v2本地四件逐字节相等，SHA-256及Git blob均相符。v2冻结清单SHA-256：7f5f23b9d712cc234c2245123ea3ba8dcfee03cf056872bcdca357454c8e50c2。

| 文件 | SHA-256 |
| --- | --- |
| research/admissions/jiangsu-medical-engineering-choices.md | 97d95ac48e3ea0f35ec3bc96222c4baef63167a0050bc378b085970768f9fcee |
| research/admissions/jiangsu-medical-engineering-choices-sources.json | 6f72f5f3f5352b577b6471525e848fd08f5097d3a02c8171764981587727223b |
| research/admissions/pharma-device-careers.md | 4ff0945f28eb037c87a73b57d385c1613ce89700caecaa109077b4d352c7cccf |
| work/runs/medical-engineering-author-20261104.json | af169b15a819eb8f047542fa9e9a1c747609b806eed827785e12ea2b3f3b00b4 |

## R1及N1真实轨迹

本地R1原本为“建议采用、无内容阻断”。N1仅指出同校两专业比较中“两校项目训练质量”的局部措辞不准。作者v2只把该处改为“两专业的实际训练质量”，并追加真实修订事件；来源索引及导航保持原字节。本人已独立核完整差异，无其他正文变化，N1采纳不构成内容返工，也不把原R1改写成“需修改”。

- 原R1 SHA-256：ebc20c69e4e9ff477cef9633fd797802d0a3f33a894e4f47429b1952898fba3a。
- N1精确差异补记SHA-256：98bf35785a60c360707db770bd23de4b9b44b2903e62e310f9cdf3b5d1af4c85。
- 输入清单SHA-256：bc37156d971bfc6014bcbbcb7298735859bfab07545d81af6c59899aa992bb60。此前38输入及25冻结repo blob已独立核验；本次只绑定相同成果的远端H，不重复宣称新做一轮原件研究。

## 沿用的实质审核结论与边界

1. 本人此前亲读H1原PDF第3页及PNG，099的C类/病理科/智能医学工程/本科与092的B类/CT磁共振科/生物医学工程等/硕博分别成立；C类历史届别、年龄、取证和高考门槛保留。099无职责，未补数字病理、算法、诊断、职称或编制，历史本科申请口径不等录用或2031承诺。
2. J1逐岗支持A本科深圳整机测试、五城用户服务和南京Java，以及指定硕士图像/信号/控制算法。未借总表或课程认专业；B未点名仍为认可未知而非永久拒收。服务差旅、共享营销和读研分别接受与计成本，同雇主多岗不算独立样本。
3. 宽P下保留A/B两本科路线，不用资料详略排就业优势；明确测试/Java的窄目标才暂前A。S1/S2保持共同P/R/资源，以真实新人任务、反馈与总补差相对变化改判，未把医院未知职责补成事实。11成员接受及用户位次仍未知，两同组目标不是两次平行保底。
4. 人口需要经实际使用/支付、医院预算或企业研发资金、组织分工才到新人任务；旧江宁数字维保采购不证硬件订单、回款或招聘。两雇主可共依医院支出。AI/远程/标准化为条件机制，2037按实际经历重核，不自动晋升或免费换学位。

四文件范围与已审版本相同：正文、有限概述/定位/哈希的来源索引、既有导航原文加两行、作者记录。无原PDF/PNG、转换全文、联系人、CSV内容、完整工具返回或内部绝对路径；本次未扩源、采录取、运行作者脚本或读取保护管理端点。2026录取采集仍暂停。

## 实际CI读取及限制

已独立读取关联H的workflow run 41825147220：.github/workflows/validation.yml，pull_request事件，head_sha与H相等，completed/success；validate job/check 126557862874也为completed/success。专用job日志显示Test review state transitions执行python3 -m unittest discover -s tests -v，9项测试通过。日志实际检出PR测试合并提交aa97867ee8b65610f5f481b65f24ef4ae81cbdb6，该提交合并本H与上述base，不冒称日志直接检出H。

check记录有2条annotations，未逐条读取annotation明细；已读job日志有checkout旧Node.js 20动作被强制Node.js 24运行的警告，不称零警告。legacy statuses为空，不把空列表当额外检查通过。这里的9项是既有审核控制器测试，不验证研究事实或未来职业结果，也不依赖另一批尚未发布的覆盖盘点修复。运行元数据显示仓库private=true。

**结论：建议采用本H，无未解决内容阻断，N1已处置。** 本评论不表示已归档或已合并，不预判未来F上的CI、平台批准或门禁成功。归档后须另核H→F只有真实审核记录、原四件不变，并核当时精确版本与平台条件。
