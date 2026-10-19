# Issue #3：Astra Ultra 自动推进机制独立审核

- 任务：[Issue #3](https://github.com/mythpan1/pathwise-research/issues/3)；候选成果：[PR #1](https://github.com/mythpan1/pathwise-research/pull/1)。
- 日期：2026-10-19（Asia/Shanghai）。
- PR 总基线：`904c75e22051bcac433245d09e3b665dc7d8a6a6`。
- 本轮增量基线：`cc2efd05a0fccaa38409b0af234d39c7f3581000`。
- 被审成果：`b8159bf5e42ce6cdf1fcafcb0ac56a336e1e0e04`。
- 模型 / 推理配置：`gpt-6-astra` / `ultra`；运行标识：`/root/astra_ultra_review`。本运行没有另行提供可引用的 UUID。
- 独立性：未参与本轮实现或测试编写；读取冻结提交的全部 13 文件增量及必要上下文。本轮只写此审核稿，没有修改候选、提交、推送、合并或启动子 Agent。

**结论：建议采用。** 未发现需要阻断本轮的缺陷，也不为凑数提出非阻断修改。本结论限于“受信协调者登记、单一协调主机控制器、既有授权内自动推进”的实现；不表示已经具备服务端强制保护或跨账号隔离。

用户已授权通过后自动下一步、失败退修。审核完成后可按现有流程追加记录、登记最终版本并继续检查，无需逐版再请示；本次审核本身不替代最终版本的 CI 与合并前核验。

**重点审查结果**

1. **审批信任边界明确。** 放行依赖仓库外的协调者登记、真实不同运行及协调者核验，而不是 PR 正文、清单或作者写入的“通过”。代码核固定仓库、目标分支、精确允许路径，并拒绝规定的本地资料目录。登记真实性和内容授权仍由受信协调者负责，这与明示的共同信任域一致，不应解读为能抵抗同一系统账号下的恶意修改。见 [scripts/review_controller.py:18–53](https://github.com/mythpan1/pathwise-research/blob/b8159bf5e42ce6cdf1fcafcb0ac56a336e1e0e04/scripts/review_controller.py#L18-L53)、[docs/review-automation.md:13–21](https://github.com/mythpan1/pathwise-research/blob/b8159bf5e42ce6cdf1fcafcb0ac56a336e1e0e04/docs/review-automation.md#L13-L21)。

2. **审核自引用已解开。** 冻结 H 后只允许一次提交新增一份审核记录；控制器检查唯一父提交、单提交差异、added 状态、路径和 blob。报告不再回填最新审核 SHA。本地登记引用 H 与最终 head，自身不进入提交；旧记录或正文同时改变均不能沿用放行结果。前轮 N1 已解决。见 [scripts/review_controller.py:97–108](https://github.com/mythpan1/pathwise-research/blob/b8159bf5e42ce6cdf1fcafcb0ac56a336e1e0e04/scripts/review_controller.py#L97-L108)、[templates/research-report.md:26–28](https://github.com/mythpan1/pathwise-research/blob/b8159bf5e42ce6cdf1fcafcb0ac56a336e1e0e04/templates/research-report.md#L26-L28)。

3. **Draft、Ready 与 merge 的条件一致。** 缺少审核、新版本、阻断、检查失败或冲突不会合并；审核有效但检查等待时可以 Ready。人的既有任务授权不再被误写为每版采用确认，前轮 N2 已解决。合并前再次读取并重新判定，第二次检查失效会退回相应状态。见 [scripts/review_controller.py:37–63](https://github.com/mythpan1/pathwise-research/blob/b8159bf5e42ce6cdf1fcafcb0ac56a336e1e0e04/scripts/review_controller.py#L37-L63)、[同文件:138–171](https://github.com/mythpan1/pathwise-research/blob/b8159bf5e42ce6cdf1fcafcb0ac56a336e1e0e04/scripts/review_controller.py#L138-L171)、[.github/pull_request_template.md:18–29](https://github.com/mythpan1/pathwise-research/blob/b8159bf5e42ce6cdf1fcafcb0ac56a336e1e0e04/.github/pull_request_template.md#L18-L29)。

4. **CI 和错误路径没有明显放行缺口。** 控制器匹配指定工作流、pull_request 事件、PR 编号及 head/base，选择匹配运行中的最新 run；缺失、未完成或非成功结论不会合并。调用合并接口时绑定 head，模糊 API 错误不重试合并，并尽力将仍开放的 PR 退为 Draft。CI 权限只读，checkout 不保留凭据。见 [scripts/review_controller.py:109–134](https://github.com/mythpan1/pathwise-research/blob/b8159bf5e42ce6cdf1fcafcb0ac56a336e1e0e04/scripts/review_controller.py#L109-L134)、[.github/workflows/validation.yml:1–19](https://github.com/mythpan1/pathwise-research/blob/b8159bf5e42ce6cdf1fcafcb0ac56a336e1e0e04/.github/workflows/validation.yml#L1-L19)。

**实际执行的检查**

- 从固定 Git 对象在内存加载实现和测试，运行仓库的 **9 项 unittest，全部通过**；没有借当前工作树替代被审源码，也没有写入测试或缓存文件。
- 另执行 **24 个本地失败路径，全部满足不越过合并条件的断言**：错误或多个父提交、多次尾部提交、修改/重命名审核记录、记录越界、错误或缺失 blob、零记录；新运行等待或失败、重跑等待、缺失/取消/无结论运行、错误 head/base；第二次读取时检查失败、审核尾部失效、冲突或版本变化；合并响应丢失后远端分别已合并和未合并。后两种情形均只调用一次合并；仍开放时退回 Draft。
- `git diff --check` 通过；本轮 Markdown 中 **27 个相对链接均能定位**。核读全部 13 文件的实现、测试和约定，确认研究主线未被本轮自动化改写。

协调者另外提供：被审成果的 [GitHub Actions 运行 39184069933](https://github.com/mythpan1/pathwise-research/actions/runs/39184069933) 已成功，工作流路径、事件、PR 1、head 和 PR 总基线匹配，测试步骤成功。**这是协调者提供的验证信息，本审核未独立调用远端 API 核验。** 该运行也不能代替追加本审核记录后最终 head 的 CI。

**限制与下一步**

没有实际执行 Draft/Ready 变更或合并，未测试真实并发文件锁、网络中断及后台定时协调任务的持续运行。单元测试和额外模拟检验了状态与调用路径，不把它们写成真实远端端到端成功。

当前私有仓库无服务端保护；head 可原子绑定，base 只能合并前复查，另一个管理员仍可绕过或同时推进 base。这个已披露边界与本轮接受的信任模型一致，不列为新阻断问题。见 [docs/review-automation.md:31–41](https://github.com/mythpan1/pathwise-research/blob/b8159bf5e42ce6cdf1fcafcb0ac56a336e1e0e04/docs/review-automation.md#L31-L41)。控制器只核路径，原始资料混入允许文件或历史的风险仍须由协调者做内容和历史检查；不能把机械门禁当作上传范围审计。

下一步：忠实追加本记录为唯一新增文件，登记其 blob、被审 H、最终 head 与当前 base；最终 head 的指定 CI 成功后，由控制器重读状态并在既有授权内自动推进。若再修改正文、脚本、测试或其他记录，必须绑定新成果复核。本轮没有读取或搬运原学业库。
