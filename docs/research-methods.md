# 复杂系统、思维实验与职业研究：方法参考

检索与整理日期：2026-10-19。用途：知途研究的方法提案。研究对象为中国2026—2036年的产业、职业与教育路径，国际研究用于提供方法，不能直接替代中国证据。

任务：[Issue #4](https://github.com/mythpan1/pathwise-research/issues/4)。独立审核按[审核模块](../reviews/README.md)记录；本文提出方法及案例设计，未完成案例实证或模型复现。

## 本轮检索做了什么

使用 Tavily 进行前导检索，再开展五轮中英文检索：跨领域系统模型、技术扩散与产业转型、中国人口与产业模型、情景一致性与迭代学习、验证与证据反馈。后续轮次根据前轮发现调整问题，并以原始论文、作者机构及研究机构的方法文件核对。两个独立子智能体分别查技术—就业、宏观—职业的文献。

本轮属于有针对性的范围检索，未按系统综述协议穷尽文献，也未复现任何模型。原始检索输出不随本文提交；下文仅保留核对过的引用、适用边界和本项目的分析建议。

## 判断

用户设想与“复杂系统中的迭代建模与学习”高度接近。非线性、延迟、反馈和主体适应，足以要求超越单链条推断，但不足以证明数学意义上的混沌。Lorenz 的经典工作研究的是确定性系统中特定的非周期动态及初值敏感性；我们的系统是否具有这些性质，需要另行定义和检验。[Lorenz，1963，原论文](https://doi.org/10.1175/1520-0469%281963%29020%3C0130%3Adnf%3E2.0.co%3B2)

对本项目的建议：以系统动力学的反馈和学习过程组织研究，以情景一致性分析帮助跨领域合成，必要时借助主体模型及经济模型检验具体机制，最后单独完成职业与培养路径的证据连接。这是本轮综合判断，不是任何一篇论文提出的完整方案。

## 核心参考

### 1. 推演为什么应当反过来提出取证问题

John D. Sterman（2001），*System Dynamics Modeling: Tools for Learning in a Complex World*，California Management Review 43(4)：8—25。

论文第21页明确提出：模拟实验可以指引新的数据收集和实验，现实结果再修正模型与决策者的认识。借鉴点是把建模视为持续学习过程，记录反馈、存量流量与延迟。模型内实验仍依赖设定，不能作为独立现实证据。

[期刊页面](https://journals.sagepub.com/doi/10.2307/41166098) · [大学存档全文，第21页](https://faculty.sites.iastate.edu/tesfatsi/archive/tesfatsi/SystemDynamics.JohnSterman2001.pdf)

前序文献：Sterman（1994），*Learning in and about complex systems*，System Dynamics Review 10(2—3)：291—330。该文将学习描述为信息反馈与认知模型修订，并分析复杂系统为何让这种学习困难。[原论文摘要](https://onlinelibrary.wiley.com/doi/abs/10.1002/sdr.4260100214)

### 2. 中国人口—产业政策的实际耦合研究

Michael Dotsey、Wenli Li、Fang Yang（2025），*Demographic transition, industrial policies, and Chinese economic growth*，Quantitative Economics 16(2)：615—657。

代际交叠模型连接家庭教育投资、储蓄、养老与企业融资政策。§6比较固定工资利率与允许价格反馈的结果：生育下降原本带来的储蓄效应可能被反馈抵消。借鉴其反事实比较。它主要解释历史，部门较粗，部分路径外生给定，不能直接当作中国职业预测。[原论文，尤其§3—8](https://onlinelibrary.wiley.com/doi/full/10.3982/QE1492)

### 3. 多领域条件能否相互成立

Wolfgang Weimer-Jehle（2006），*Cross-impact balances: A system-theoretical approach to cross-impact analysis*，Technological Forecasting & Social Change 73(4)：334—361。

CIB将因素的不同状态及相互影响判断组织起来，筛查在这些判断下自洽的情景，适用于跨学科知识难以充分公式化的情形。自洽不等于真实或高概率；影响判断仍须取证。当前可先借鉴其检查逻辑，尚不能称我们已实现正式CIB模型。[原论文，§1、§4](https://cross-impact.de/ressourcen/cib_weimer-jehle_2006.pdf)

作者2023年专著及应用项目可由[斯图加特大学CIB实验室](https://www.zirius.uni-stuttgart.de/en/forschung/cib-lab)继续追踪。

### 4. 宏观要素怎样放进同一反馈模型

Ye 等（2024），*FeliX 2.0: An integrated model of climate, economy, environment, and society interactions*，Environmental Modelling & Software 179：106121。

IIASA的FeliX将人口、教育、经济、能源、土地、食物等系统耦合，用存量流量和反馈表示相互作用。适合学习模块间的接口及时间尺度；全球模型的结构和结果不能直接落到中国某地职业，更不能自动预测尚未出现的发明。

[论文DOI](https://doi.org/10.1016/j.envsoft.2024.106121) · [官方模型介绍](https://iiasa.ac.at/models-tools-data/felix) · [模型文档](https://iiasa.github.io/felix_docs/)

核对范围：官方介绍和模型文档；论文全文下载遇到访问限制，未宣称已完成逐式审读。

### 5. 技术进步如何同时创造和消灭工作

Giovanni Dosi、Marcelo C. Pereira、Andrea Roventini、Maria Enrica Virgillito（2022），*Technological paradigms, labour creation and destruction in a multi-sector agent-based model*，Research Policy 51(10)：104565。

多部门主体模型同时研究工艺创新、新产品与行业、工资分配及消费需求的反馈。适合检验技术节省用工后，需求与新业务能否产生补偿。制度设定影响结果；其机制研究不能直接给出中国某专业未来岗位数。

[原论文](https://www.sciencedirect.com/science/article/abs/pii/S0048733322000889) · [作者机构工作论文](https://www.lem.sssup.it/WPLem/2021-17.html)

### 6. 技术突破为何不会自动变成产业替代

Frank W. Geels（2014），*Regime Resistance against Low-Carbon Transitions: Introducing Politics and Power into the Multi-Level Perspective*，Theory, Culture & Society 31(5)。

以英国电力为例，将技术转型与既有产业、政治权力及外部条件连接。可用于研究企业和政策主体怎样回应新技术，提出扩散所需的条件。它是历史解释框架，不能提供中国新技术产业化时间的现成答案。[原论文](https://journals.sagepub.com/doi/full/10.1177/0263276414531627)

### 7. 如何最终接到职业与招聘

Cedefop Skills Forecast：方法框架与2025版技术报告。

其模块将宏观及行业就业接到职业、学历与新增和替代招聘需求。但方法文件§1.2.3说明，技能供需预测未直接交互，另作协调；不能称其反馈完全闭合，学历层次也不能等同具体专业。[方法框架](https://www.cedefop.europa.eu/files/skills_forecast_methodological_framework.pdf)

2025版技术稿第26—29页提供一个验证案例：自动化修正虽在更细的荷兰职业分类研究中有效，迁入该框架后误差未改善，因此未采用此项定量修正。这不证明自动化无影响，而是说明增加机制需要验证适用性。技术稿署2024年12月，标注未编辑、非正式出版。[技术报告](https://www.cedefop.europa.eu/files/skills_forecast_2025_technical_report.pdf)

### 8. 未来无法押准时，怎样支持选择

RAND Robust Decision Making（RDM）。

比较策略在多种未来下的表现，查明失败条件，再修订策略或情景。可用于下游比较培养路径的稳健性；它不负责证明上游因果关系，情景中表现良好的比例也不能自动解释为现实成功概率。[RAND官方方法](https://www.rand.org/pubs/tools/TL320/tool/robust-decision-making.html)

## 对现有架构的具体启发

现有[研究总图](research-architecture.md)已包含政策谱系、人口队列、国际暴露、岗位补员、竞争解释、反馈时间和失效信号。需要补强的是执行这些要求的研究流程；本稿为这些要求提供方法参考，具体工作记录尚待局部案例检验。

首先区分两个循环：

- 现实系统的循环：人口、产业、工资、家庭与政策会相互改变，反馈有时间延迟。
- 研究工作的循环：证据支持某种机制假设，推演暴露未知，求证又改变机制、范围或情景。

把第二个循环嵌在各专题研究中，并在跨专题合成时检查第一个循环。不能让“推演得到的结果”变成支持同一推演的独立来源。

每个思维实验只需先写清七件事：

1. 地区、主体、时间及要回答的职业问题。
2. 当前事实、口径与来源。
3. 暂定机制和至少一个有实质区别的替代解释。
4. 中间环节、时间延迟、主体反应和反馈。
5. 各解释会产生哪些不同的可观察结果。
6. 最能区分解释、且可取得的下一项证据。
7. 新证据到来后，保留、修订、撤回或继续未知，以及受影响的下游判断。

这是建议的工作记录，不要求先建数据库或大型数值模拟器。关系已有可靠数据且确有计算需要时，再做局部定量模型；缺证据时保留分支，不用Agent共识补成事实。

执行时依照[实验项目与演进约束](experiment-protocol.md)及[参与者与步骤记录约束](agent-provenance.md)落盘：每个实验可独立组织，回合保留状态、规则、证据版本和执行归属；模板提供结构化字段，尚不代表已经实现自动采集或仿真。

## 两个用户案例怎样使用这些方法

以下都是待检验的思维实验设计，不是中国行业预测。

### 少子化与教师职业

问题限定为某地区、某学段、某毕业年份的新教师入口。先按对应出生队列核学生规模，再分别假设：学校主要减少新招；学校主要缩小班额并调整服务；学生向部分地区或学校集中。教师退休后的岗位是否补员，须另核。

可以区分这些路径的资料包括班额、学校布局、实际在岗、真实招录、转岗、财政支付和迁移。学生总量相同，政策及组织响应不同，新人入口就可能不同。教育与教培政策调整只能作为条件分支；人口压力本身不确定调整方向。

时间尤其要分开：今天出生减少对近期学前服务与家庭行为的影响，和相应队列多年后进入劳动力市场的影响，属于不同的研究路径。

### 二氧化碳制淀粉与产业职业

把用户提出的技术作为研究对象，分别提出实验可行、中试可运行、规模生产可竞争、市场可接受等条件；本轮没有核验其当前商业化状态。

需要逐步查明的变量包括全流程能耗及能源价格、设备和催化成本、连续运行表现、产品用途与质量要求，以及与既有生产的比较。再推演农业、能源、设备与加工环节的调整，最后核实际工作任务和用人。

同时保留替代、特定用途补充和长期未规模扩散等路径。能够让这些路径明显分化的成本、工程和需求证据，比继续扩写产业颠覆故事更有研究价值。

## 建议的采用顺序与边界

先用Sterman的学习循环和CIB的一致性思路，完成一个少子化—教育职业的小范围案例；用中国人口—产业论文检查反馈是否会改写第一轮结论。FeliX用于参考宏观接口，主体模型与技术转型框架用于需要深入的技术专题，Cedefop帮助拆解职业与招聘端，RDM留给下游路径比较。

本轮没有找到一套已经验证、可直接覆盖“中国政策—人口—所有产业—职业—具体专业”的现成统一模型；这仅说明此次检索未找到，不等于证明不存在。各参考模型的假设、时空口径与边界不同，不能直接拼接其结果。研究记录应保留版本；审核通过表示论证与证据满足要求，不代表未来情景已被现实证实。
