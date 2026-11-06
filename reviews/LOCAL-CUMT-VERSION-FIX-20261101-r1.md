# LOCAL-CUMT-VERSION-FIX-20261101：独立审核归档

任务为已合并 #310 的最小版本事实纠错；作者/发布 `/root/identify_admission_rules_gap`，独立审核 `/root/identify_admission_rules_gap/review_cumt_version_fix`。本文件由发布者忠实代录下列真实普通评论，不是作者自审，不是 GitHub 正式 APPROVE。成果 H 为 `6d4f8e03243b343bea37b84b07c2f572a92fb7dd`；归档之后仅核最终差异和门禁，不扩大研究。

原评论：https://github.com/mythpan1/pathwise-research/pull/311#issuecomment-6557493362

Independent review | head: 6d4f8e03243b343bea37b84b07c2f572a92fb7dd | reviewer run: /root/identify_admission_rules_gap/review_cumt_version_fix | verdict: 建议采用

基线：`84539b7f9a1c889166fa185addf130f24ecee4f9`。本人未参与本候选的编写、修改或发布，独立读取基线全文、候选全文、远端 H 和两份校方原文。

- **精确范围：** PR 为 open、非 Draft；实际差异仅 `research/admissions/cumt-mechanical-class-pathways.md` 在 S1 后、S2 前增加一个版本补核段落及空行（+2/-0），没有改动其他研究内容。远端 H 正文与本地候选仅相差文件末尾一个换行，正文一致，非逐字节一致。远端文件 SHA-256：`8f2e78614dcb4752da427d9b4bb939a660d7bb5b294551e7d2f668d07f647ce9`。
- **已独立核原文：** [2024 级方案](https://cmee.cumt.edu.cn/info/1084/9860.htm)第六、七条以高数（1）（2）的学分加权均分处理同分；[2025 级方案](https://cmee.cumt.edu.cn/info/1073/10638.htm)第六、七条改为平均学分绩点。两去向、第 3 学期起分专业培养、志愿顺序与同序加权均分的概述均有原文依据。2024 页通过 web.open、2025 页通过 Exa web_fetch_exa 读取同一官方 URL，未把提取器附加元数据当校方事实。
- **日期矛盾与适用边界：** 2025 页标题及第五条指向 2025 级，页面时间为 2026-04-03，第七条日程与落款仍为 2025 年。补段保留该冲突，不擅改年份、不当作可执行日程；“未核实 2026、2027 级正式方案”也没有被写成“不存在”。没有将历史同分规则、容量或首选机会外推为未来保障。
- **决策与停止边界：** 补段只提醒当前江苏高三志愿选择须辨认届别、先确认能否接受大类去向，仅在会改变当前选择时补核。未开展新院校研究、名单/成绩附件核查或暂停中的 2026 录取数据采集。不复审本次未变的课程、岗位等论据，亦不声称核实了 2026/2027 正式分流规则。

阻断项：无。需修改项：无。结论仅覆盖上述版本补核及受影响的历史/未来边界，不替代最终精确 head 的 CI、其他阻断和平台保护核验。

模型/强度请求据父运行的启动配置记录为 `gpt-6-astra / ultra`；本运行未暴露实际模型/强度报告，reported=unknown，不以请求值认证后端身份。本条是实际独立运行的普通审核评论，**不是 GitHub APPROVE，也不能替代平台要求的独立账户批准**。
