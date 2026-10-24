# 蟠龙幼儿园：原文基线已核，一次mini尝试失败

[Issue #18](https://github.com/mythpan1/pathwise-research/issues/18) · [PR #19](https://github.com/mythpan1/pathwise-research/pull/19) · 运行 `RUN-EXP001-20261022-PANLONG-COMPARE-01`。范围为上海青浦区蟠龙民办幼儿园2025暑秋原幼儿是否被公办园实际接收；允许后发资料明确回溯。本单元不换案例、不推人口或教师因果。

**行政终止办学批准已核；物理停止、注销完成及同窗口公办实际接收仍未核实。** 唯一一次mini Research创建调用在原生前检通过后，业务POST返回HTTP 422，没有任务ID或报告，无法完成Research主张与原文的逐项比较。这个失败不证明现实不存在接收，也不能说明额度耗尽或限流。

## Search与原文结果

先完成两批、每批两条非重复advanced Search。两批均未增加能把本园原幼儿与某公办接收园、实际时间对应的线索，遂冻结有限基线；不是互联网穷尽，也没有因达到四条就拒读可用原文。四条精确查询、相关性和八次官方网络读取尝试见[sources.json](sources.json)。三次网页截图/图片读取超时；两次官方直接下载分别恢复PDF和图片，包含在八次内。

- [教育局原始批复PDF](https://www.shqp.gov.cn/edu/edu/upload/202510/1013_133349_363.pdf)两页逐页视觉核读：青教〔2025〕82号，署期2025-07-18，同意终止办学并要求依法办理注销；第2页印发栏为7月21日。这些日期不等于物理关闭或儿童安置日。
- [2025转园插班安排](https://www.shanghai.gov.cn/nw17239/20250416/e32bef7227bc4f2db7dc94df52916b0c.html)及其[公办计划表原图](https://www.shanghai.gov.cn/cmsres/06/06ae8d51bd784db08d61bef5ddc23875/a143181aee28e7b1e80576ddc32de895.jpg)只提供一般程序与计划，没有本园原幼儿到公办园的实际完成映射。不能把插班计划人数当已接收人数。
- [官方入园问答](https://www.shqp.gov.cn/edu/eduzwgk/lm/jy/zs/xq/20250415/1277266.html)Q16/Q17区分转园安排、登记与录取，没有本案实际去向记录。

原园幼儿名单、接收公办园、公办属性对应证据、实际同窗口日期与人数均为`null`。可改变判断的材料是能明确连起本园原幼儿、接收园及公办属性、2025暑秋实际入园时间的官方或可核原始记录；一般招生或拟安置不足以补齐。

## 冻结与唯一一次mini

Search/原文的五项事实、两类未知见不可回填的[BASELINE.md](BASELINE.md)。2026-10-22T12:52:02.157077+00:00冻结，随后提交检查点`33aa7c91f6e8805813b0c996b7ab4269314c5f99`，再于12:53:15.861Z发起mini。文本SHA256为`45114f11ba9fe515f3bf5ad8ed8bc6c604f7b62102868cda616c643cdf8073f7`；本地冻结证据快照SHA256为`192523a1b43e77e0c4a95d14f49f42069bf7764d7fbe1bd9b8a84c4c7da63d3b`。

实际只调用一次原生`tavily_research`，显式`model=mini`、`max_wait_ms=180000`、`citation_format=markdown`。原生准入通过后，一次业务POST返回422，被原生记录为`non_quota_http`并停止；没有轮转、同ID轮询或第二次创建。任务获受理未确认，`request_id=null`。工具没有暴露错误响应体，不能判定具体参数、后端状态或错误根因，未为诊断再发请求。 `citation_format=markdown`由执行者主动选择，原生schema允许`numbered/markdown`且没有默认；这不证明远端接受，也不足以认定422由此造成。

[COMPARISON.md](COMPARISON.md)如实列出对照不可完成。没有Research原句、引文、新来源或可见内部萃取，不能把Search摘要当Research萃取、编造错误类型，或声称Research与原文一致。

## 额度、停止与限制

沿用未改动的已安装0.2.5原生工具定义及守门。advanced Search每次准入2；四次保守预留8/20 credits，实际账单未知。mini准入250是守门门槛，不是本次实付。匿名slot496四次Search前检及mini前后可见余额均884；Search成功后测按原生策略跳过，没有叠加余额查询。mini原生后测记录可见差值0，仍不据此宣称零费用。没有额外quota/usage探测、手动切换、脚本修改、ACP或凭据操作。

本单元已按授权尝试一次mini；在原生错误后停止，方法比较目标未实现。后续若要诊断422或再次研究，需要另行确认具体范围，不能把本交付当作重试授权。原始网页/PDF/图片、完整工具返回、回执和匿名审计只留本地；仓库提交脱敏摘要、索引、冻结信息与运行步骤。

执行者自检不是独立审核。交接PR19当前完整head给知舟（Dot）仅审核；本单元不自行合并、不启动下一轮研究。机械检查与CI实况以PR正文固定head交接为准。
