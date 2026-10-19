# 审核自动化的运行边界

## 已实现的部分

- GitHub Actions在PR打开、更新、重开或Ready时运行状态机测试，权限仅为只读，不带业务凭据，不负责合并。
- `scripts/review_controller.py`读取受信协调者登记，查询GitHub现状，自动保持/退回Draft、转为Ready，条件满足时合并；默认只预览，`--apply`执行。
- 协调者接收控制器输出后安排审核、修订或补证。同一已授权任务不用逐版向人请示。用户于2026-10-19取消本会话的定时协调任务，当前不再周期唤醒；控制器在获授权的实际任务中按需执行，运行依赖本机Codex、登录与额度可用。

GitHub分支保护接口在2026-10-19返回403，要求升级私有仓库套餐。当前不启用或声称有原生强制保护；不为此改为公开仓库。Actions检查是机械检查，不能代替独立研究审核。

## 本地登记

登记文件放在仓库外 `~/.codex/pathwise-review/decisions/`，不提交Git。由协调者依据人的任务和真实独立审核生成，不能从PR中读取一段JSON就信任。登记包含：

- `repository`、`pr`、`issue`；`authorization.auto_advance`、人的授权`source`、精确允许文件`paths`。
- `base_sha`、`reviewed_sha`、最终`head_sha`，全部为完整提交SHA。
- `author_run`、`reviewer_run`、`coordinator_verified`，记录真实不同运行，不能只换名字。
- `verdict`为`pending`、`approve`、`changes`或`evidence`；`blocking`为未解决阻断数。
- `record_path`和`record_blob`：审核后唯一新增记录的路径和Git blob SHA。

审核通过的登记必须先核原始回复、报告、检查范围和非阻断项处置。它是一份受信协调者证明，不是密码学身份认证；同一系统账号仍可修改登记，不声称隔离恶意Agent。

## 避免审核自引用

报告仅提前写稳定审核入口，不回填“最新审核SHA”。冻结成果H并审查H，然后一次提交只新增对应审核记录R，得到最终head。控制器验证head只有H一个父提交、差异仅新增R且blob完全匹配。正文或其他记录也有改动时均退回复核。

复核轮使用新文件名，旧记录保留。协调者本地登记引用H和最终head，登记自身不进入候选提交，因此不产生自引用。

## 执行和失败路径

仅运行已采用main版本的控制器；首次引导由既有协调者根据本次授权，在独立代码审核及实际检查通过后执行。不能让候选PR中的脚本自行批准自身，也不在带写凭据的工作流中执行PR代码。

预览：`python3 scripts/review_controller.py --decision ~/.codex/pathwise-review/decisions/pr-1.json`

执行：在上述命令后加 `--apply`。只接受固定仓库，自动合并范围由本地授权路径限制。控制器不执行PR中的命令、不下载依赖、不调用模型；Agent任务由协调者安排。

网络错误、缺失或未知检查、未知审核结论均不合并；新head/base使旧审核失效。仅指定 `.github/workflows/validation.yml` 对精确head的成功运行满足检查。失败检查退回修订，等待检查可Ready但不可合并。合并前重读状态，再以head SHA调用合并接口。

本地主机用文件锁串行推进，过程追加到 `~/.codex/pathwise-review/events.jsonl`。无分支保护时，GitHub合并API能绑定head，不能原子绑定base；协调者合并前立即核base并串行主分支写入，无法阻止另一个管理员同时绕过。若未来需要跨主机或不可信Agent强制隔离，再配置服务端规则与独立身份，不把当前实现夸大为该能力。

实际任务成功后可继续已有授权队列；不自动创造新研究、扩大上传范围或恢复已取消的周期唤醒。同一阻断连续两轮仍无法解决才通知人处理。所有历史审核保留其当时范围，旧的人工逐版采用约定已由2026-10-19的新授权替代。
