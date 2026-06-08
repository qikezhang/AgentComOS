# Active Implementation Note for v2.8.6

> 中文备注：本文件是 **AgentComOS v2.8 完整产品目标基线**，保留完整功能审计要点。v2.8.6 的开发期执行策略以 `docs/19_DECISION_FEYNMAN_ADOPTION_POLICY.md`、`docs/17_PHASED_DELIVERY_PLAN.md`、`docs/18_ACCEPTANCE_GATES.md` 为准：开发初期采用显式启用，过渡期系统建议，工业化期自动判断。


# AgentComOS v2.8.6 Implementation Overlay

> 中文备注：`docs/00_PRODUCT_SPEC_V2_8.md` 仍以完整 v2.8 产品方案为核心基准。v2.8.6 不删除 v2.8 的功能审计要点，而是把落地策略调整为“受控交付 → 辅助自动化 → 工业化自动判断”的分阶段模式。

## v2.8.6 核心调整

1. **分阶段落地**：项目不再一次性实现全部智能模块，而是按 Phase 0-10 分段开发、测试、验收和部署。
2. **Controller 优先**：Controller 是第一个必须实现到可运行、可恢复、可审计的核心模块。所有后续 OpenCode、Hermes Worker、Loop、Manual、Versioning 都依赖 Controller 的状态机、事件日志和 job ledger。
3. **Decision Market / Feynman 的分阶段门槛**：
   - 开发初期 `development_explicit`：默认不自动启用；只有用户显式指定、任务文件显式 required、或高风险强制 gate 才启用。
   - 过渡期 `transition_assisted`：系统给出建议，但默认需要 GM/用户或任务策略确认。
   - 工业化期 `industrial_auto`：系统根据 Task Classification、Decision Need Score、risk_level、release policy 自动判断是否启用，以增强长期运营稳定性。
4. **Codex / Antigravity 协作合同**：Codex 是项目管理、文档、schema、审计和验收方；Antigravity 是代码开发、部署和运营实例维护方。任何阶段都必须通过 acceptance gates。
5. **数据驱动开发**：所有关键动作必须产生 event、status、artifact、test 和 evidence，Codex 能据此审计商业化部署版本是否合格。

---

# **AgentComOS v2.8**

## **AI-Native Company Operating Platform**

AgentComOS v2.8 是一个用于自动化运营 AI-native 公司的核心支撑平台。

它不是普通多 Agent 系统，也不是单纯 coding assistant，而是一套长期运行的公司操作系统：

**GM 负责经营和用户沟通，OpenCode 负责工程和 Worker 管理，Controller 负责稳定调度，Hermes Worker 承载公司能力，Core Worker Starter Pack 让系统第一天就具备基础部门能力，Decision Market 负责方案发现与裁决，Task Frontier 控制任务前沿，Loop Execution Engine 负责循环执行，Feynman Engine 负责默认对抗检查，Manual OS 沉淀公司智慧，Worker Evolution Engine 进化公司能力，GitTree / Auto Versioner / Environment KB 保证系统可控、可审计、可回滚、可长期运行。**

OpenCode 是开源 AI 编程代理 / coding agent。其 CLI 支持 TUI、非交互 `run`、`serve` 后端服务、`attach` 连接运行中的 backend server、agent 管理、session list/export 等能力，适合作为 AgentComOS 的常驻工程 runtime。 

Hermes Agent 是 Nous Research 的 self-improving AI agent。官方文档说明它内置 learning loop，可以从经验创建 skills、在使用中改进 skills，并跨会话积累理解；AgentComOS 将它用于 GM runtime 和通过 tmux 启动的 Hermes Worker runtime。 

---

# **1\. 最终系统总览**

User / Founder

  ↓ Discord

GM Hermes

  ↓ Operating Intent / Daily Operating Packet

AgentComOS Controller

  ↓

OpenCode Runtime

  ↓

Task Classification

  ↓

Decision Need Score

  ↓

Decision Market: skip / mini / standard / full

  ↓

Feynman Pre-Execution Check: skip / lite / standard / full

  ↓

Task Frontier / Loop Execution Request / Worker Invocation

  ↓

Core Worker Starter Pack / Hermes Workers via tmux

  ↓

Feynman Batch Gate / Evidence Audit / Release Judge

  ↓

OpenCode Synthesis / Build / Delivery

  ↓

Evidence Packet

  ↓

GitTree / Auto Versioner

  ↓

Delivery Packet / User Report Packet

  ↓

GM

  ↓ Discord

User / Founder

长期飞轮：

运营任务

  ↓

执行结果

  ↓

Evidence

  ↓

Learning Packet

  ↓

Knowledge Card

  ↓

Manual Update Proposal

  ↓

Manual Release

  ↓

Worker / Skill / GM Evolution

  ↓

下一轮运营更强

---

# **2\. 核心原则**

1\. 用户默认只和 GM 沟通。

2\. GM 不碰 Worker。

3\. Worker 只能由 OpenCode 调用。

4\. OpenCode 是工程总包、Worker Manager 和唯一 Worker 调用者。

5\. Controller 执行 Worker Invocation，但不做认知判断。

6\. Hermes Worker 不是新写的 worker 程序，而是 tmux 启动的 Hermes CLI 实例。

7\. Hermes subagent 不进入 AgentComOS 设计层。

8\. Core Worker Starter Pack 是系统初始化默认能力库。

9\. Decision Market 不是只用于重大任务，而是用于所有有方案不确定性的任务。

10\. Feynman Engine 不是 Loop 专用，而是所有非极简单任务的默认对抗检查机制。

11\. Task Frontier 选任务，Loop Execution Engine 跑任务批次，Controller 管运行时。

12\. Manual 是公司最核心资产。

13\. 所有非 trivial 任务必须有 Evidence Packet。

14\. 所有工程和能力资产变更必须走 GitTree / Auto Versioner。

15\. 运营原始数据不作为 GitTree 版本对象，只做 ledger、snapshot、evidence reference。

16\. 所有环境事实走 Environment KB，Agent 不允许猜版本、命令、路径、时区。

17\. 长期目标必须成为 Operating Program。

18\. GM 必须能给用户清楚汇报状态、进展、风险、卡点和下一步。

---

# **3\. 关键角色定义**

## **3.1 GM Hermes**

GM 是常驻 Hermes 实例，通过 Discord 与用户沟通。

GM 可以：

理解用户目标

生成 Operating Intent

生成 Daily Operating Packet

查看系统状态摘要

查看 OpenCode 任务进展摘要

查看产品健康摘要

查看 Manual / Knowledge 状态摘要

查看收入、流量、运营指标

读取 Delivery Packet / User Report Packet

向用户汇报进展、风险、卡点和下一步

请求授权、凭证、收款、法律或高风险确认

GM 不可以：

直接调用 Worker

创建 Worker Invocation

读取 Worker 原始输出作为最终依据

启动 tmux

直接改代码

直接 shell

直接 git merge

直接 deploy

直接修改自己的 system / genome

GM 的定位：

**AI 公司的 CEO / COO。**

---

## **3.2 OpenCode Runtime**

OpenCode 是工程总包、Worker Manager、方案综合者。

OpenCode 负责：

读取 GM 的 Operating Intent / Daily Operating Packet

进行 Task Classification

计算 Decision Need Score

决定是否需要 skip / mini / standard / full Decision Market

创建 Decision Market Request

执行或请求 Feynman 检查

Plan 模式拆解任务

Build 模式实施任务

创建 Task Frontier Seed

创建 Loop Execution Request

判断是否需要 Worker

从 Core Worker Registry 选择已有 Worker

创建新 Worker spec / skill / rubric

生成 Worker Invocation

读取 Worker 输出

综合 Worker 结果

生成 Evidence Packet

生成 Delivery Packet

提出 Worker / Skill / Manual / GM Evolution Ticket

OpenCode 是唯一可以调用 Worker 的主体。

---

## **3.3 Controller**

Controller 是 AgentComOS 自研的确定性守护程序，不是 LLM Agent。

Controller 负责：

启动和监管 GM Hermes

启动和监管 OpenCode serve

监听 GM 产生的任务

创建 run 目录

创建 GitTree worktree

生成 Environment Context Bundle

把任务投递给 OpenCode

管理 OpenCode job / session / timeout / stalled 状态

执行 OpenCode 生成的 Worker Invocation

管理 tmux Hermes Worker Pool

执行 Loop Execution Engine 的任务批次

收集 Evidence

触发 Release Judge

触发 Auto Versioner

把 Delivery Packet / User Report Packet 交回 GM

Controller 不负责：

替 GM 做经营判断

替 OpenCode 决定调用哪个 Worker

替 Worker 下审查结论

直接修改业务文件

一句话：

**Controller 不思考业务，只保证系统稳定执行。**

---

## **3.4 Hermes Worker**

**Hermes Worker 不是 AgentComOS 重新写的独立 worker 程序，而是 Controller 通过 tmux 启动的 Hermes CLI 实例。**

工程上它就是：

tmux session

  ↓

hermes chat \-Q \-q "\<读取 Worker Invocation 并执行\>"

  ↓

输出文件写入 worker\_outputs/

Hermes Worker 只做一件事：

读取 OpenCode 生成的 Worker Invocation

完成其中定义的明确任务

把 required outputs 写到 output\_dir

它不做：

长期调度

队列管理

全局任务拆解

直接和 GM 沟通

直接和用户沟通

直接修改主项目

直接发布

直接更新正式 Manual

---

# **4\. Hermes Worker 调用方式**

## **4.1 Worker Invocation**

OpenCode 必须先生成 Worker Invocation。

worker\_invocation:

  invocation\_id: HWI-TF-001

  created\_by: opencode

  called\_by: opencode

  executed\_by: controller

  output\_receiver: opencode

  worker\_id: research\_worker

  worker\_version: "0.3.1"

  runtime: hermes\_tmux

  task:

    task\_id: TF-001

    goal: "研究 techai8.com 的 AI 工具收入页内容机会。"

    task\_type: research

  inputs:

    \- task\_contract.yaml

    \- runtime\_context\_bundle.yaml

    \- relevant\_manual\_capsule.yaml

    \- evidence\_refs.yaml

  output\_dir: ".agentcomos/runs/OI-TECHAI8-001/worker\_outputs/TF-001/"

  required\_outputs:

    \- result.yaml

    \- reasoning\_summary.md

    \- unknown\_facts.yaml

    \- failure\_report.md

    \- DONE.md

  stop\_conditions:

    \- required\_outputs\_exist

    \- unknown\_facts\_listed

    \- no\_blocking\_error

    \- max\_runtime\_reached

  forbidden:

    \- edit\_project\_files

    \- merge\_git

    \- deploy

    \- call\_gm

    \- call\_user

## **4.2 tmux 启动模板**

Controller 通过 tmux 启动 Hermes Worker：

tmux new-session \-d \-s agentcomos\_OI-TECHAI8-001\_research\_worker\_TF001 \\

  "cd /path/to/worktree && hermes chat \-Q \-q 'Read .agentcomos/runs/OI-TECHAI8-001/worker\_invocations/HWI-TF-001.yaml and write all required outputs to .agentcomos/runs/OI-TECHAI8-001/worker\_outputs/TF-001/'"

可以封装成 wrapper：

agentcomos worker start-tmux \\

  \--run OI-TECHAI8-001 \\

  \--task TF-001 \\

  \--worker research\_worker \\

  \--invocation .agentcomos/runs/OI-TECHAI8-001/worker\_invocations/HWI-TF-001.yaml

但 wrapper 只是便捷封装，本质仍然是：

tmux \+ hermes chat \-Q \-q

不能重新实现一个独立 Worker 程序来替代 Hermes。

## **4.3 tmux session 命名**

agentcomos\_\<run\_id\>\_\<worker\_id\>\_\<task\_id\>

示例：

agentcomos\_OI-TECHAI8-001\_research\_worker\_TF001

agentcomos\_OI-TECHAI8-001\_seo\_worker\_TF002

agentcomos\_OI-TECHAI8-001\_evidence\_audit\_worker\_TF003

## **4.4 Worker Job 记录**

worker\_job:

  job\_id: HWJ-TF-001

  run\_id: OI-TECHAI8-001

  batch\_id: LB-TECHAI8-2026-0608-001

  worker\_id: research\_worker

  runtime: hermes\_tmux

  tmux\_session: agentcomos\_OI-TECHAI8-001\_research\_worker\_TF001

  invocation\_file: ".agentcomos/runs/OI-TECHAI8-001/worker\_invocations/HWI-TF-001.yaml"

  output\_dir: ".agentcomos/runs/OI-TECHAI8-001/worker\_outputs/TF-001/"

  status: running

  started\_at: "2026-06-08T10:00:00-07:00"

  last\_output\_at: "2026-06-08T10:08:00-07:00"

  timeouts:

    soft\_timeout\_minutes: 30

    hard\_timeout\_minutes: 90

    no\_output\_timeout\_minutes: 10

Controller 通过这些信号判断 Worker 是否正常：

tmux session 是否存在

output\_dir 是否有新文件

required\_outputs 是否存在

DONE.md 是否出现

failure\_report.md 是否出现

日志是否增长

是否超过 timeout

---

# **5\. OpenCode 常驻运行机制**

生产形态下，OpenCode 作为常驻 runtime：

opencode serve \--hostname 127.0.0.1 \--port 4096

Controller 通过 attach 派任务：

opencode run \\

  \--attach http://127.0.0.1:4096 \\

  \--agent agentcomos-planner \\

  \--dir .worktrees/OI-TECHAI8-001/opencode \\

  \--title "OI-TECHAI8-001 plan" \\

  \--format json \\

  "Read operating\_intent.yaml and runtime\_context\_bundle.yaml. Execute .opencode/commands/accept-gm-intent.md."

Session 策略：

Plan：fresh session

Build：fork from plan 或 continue build session

Review：fresh session

Release Judge：fresh session

GM Evolution Review：fresh session

Controller 记录：

session\_id

phase

agent

stdout / json log

exported session

expected outputs

timeout state

---

# **6\. Core Worker Starter Pack**

AgentComOS 初始化时必须预置一批经典能力 Worker，让系统第一天就可以运营、开发、设计、财务、运维、评审、Manual 更新和 Worker 进化。

这些 Worker 不是自由 Agent，而是：

**OpenCode 管理和调用的标准能力单元。**

它们全部遵守边界：

GM 不调用 Worker

用户不调用 Worker

Controller 不决定用哪个 Worker

OpenCode 才能创建 Worker Invocation

Controller 只负责执行 Invocation

Worker 输出回到 OpenCode

OpenCode 综合后交给 GM

## **6.1 Core Worker Starter Pack 目录**

.agentcomos/workers/

  registry/

    core\_worker\_registry.yaml

  specs/

    feynman\_review\_worker.yaml

    evidence\_audit\_worker.yaml

    release\_judge\_worker.yaml

    risk\_audit\_worker.yaml

    operating\_planner\_worker.yaml

    ...

  invocation\_templates/

    feynman\_review\_invocation.yaml

    evidence\_audit\_invocation.yaml

    release\_judge\_invocation.yaml

    ...

  rubrics/

    feynman\_review\_rubric.yaml

    evidence\_audit\_rubric.yaml

    release\_judge\_rubric.yaml

    worker\_evaluation\_rubric.yaml

    proposal\_scoring\_rubric.yaml

  evals/

    seed\_cases/

      feynman\_review\_cases.yaml

      evidence\_audit\_cases.yaml

      seo\_content\_cases.yaml

      worker\_evolution\_cases.yaml

  scorecards/

    initial\_scorecards.yaml

  evolution/

    worker\_evolution\_policy.yaml

    ratchet\_policy.yaml

## **6.2 Tier 0：系统启动必须预置**

Tier 0 是系统审查、裁决、稳定性和自进化底座：

feynman\_review\_worker

evidence\_audit\_worker

risk\_audit\_worker

release\_judge\_worker

failure\_attribution\_worker

worker\_evaluator\_worker

ratchet\_judge\_worker

runtime\_health\_audit\_worker

environment\_probe\_review\_worker

## **6.3 Tier 1：默认启用的方案发现与运营能力**

因为 Decision Market 现在是“有不确定性就用”的默认方案发现机制，所以 proposal 系列 Worker 要前置到 Tier 1。

proposal\_builder\_worker

proposal\_scorer\_worker

critic\_worker

synthesis\_worker

final\_decision\_judge\_worker

operating\_planner\_worker

growth\_diagnosis\_worker

daily\_ops\_review\_worker

product\_health\_check\_worker

seo\_research\_worker

content\_strategy\_worker

conversion\_audit\_worker

finance\_reconciliation\_worker

unit\_economics\_worker

data\_quality\_audit\_worker

knowledge\_extraction\_worker

manual\_update\_worker

## **6.4 Tier 2：按需启用**

architecture\_review\_worker

code\_review\_worker

test\_failure\_analysis\_worker

deployment\_review\_worker

incident\_analysis\_worker

manual\_contradiction\_audit\_worker

context\_capsule\_builder\_worker

worker\_evolver\_worker

revenue\_ops\_worker

## **6.5 Worker Spec 标准**

每个预置 Worker 都必须有完整 spec。

worker\_spec:

  worker\_id: feynman\_review\_worker

  version: "0.1.0"

  tier: 0

  owner: opencode

  runtime: hermes\_tmux

  purpose: "对计划、batch、release candidate 做多角度可行性和质量审查。"

  allowed\_called\_by:

    \- opencode

  forbidden\_called\_by:

    \- gm

    \- user

    \- controller\_direct\_decision

  inputs:

    required:

      \- task\_contract

      \- runtime\_context\_bundle

      \- relevant\_manual\_capsule

      \- artifact\_under\_review

      \- evidence\_refs

  outputs:

    required:

      \- feynman\_review.yaml

      \- vetoes.yaml

      \- required\_revisions.yaml

      \- DONE.md

  rubric:

    \- goal\_alignment

    \- technical\_feasibility

    \- business\_value

    \- evidence\_quality

    \- risk\_control

    \- manual\_consistency

  failure\_modes:

    \- "Reviewed only summary, not raw evidence"

    \- "Missed business goal alignment"

    \- "Allowed unsupported claim"

  evolution\_policy:

    eval\_required: true

    ratchet\_required: true

    rollback\_if\_score\_drops: true

## **6.6 OpenCode 如何选择 Worker**

OpenCode 通过 Worker Selection Policy 选择 Worker。

worker\_selection\_policy:

  rules:

    \- if\_task\_type: risk\_review

      use\_worker: risk\_audit\_worker

    \- if\_task\_type: evidence\_check

      use\_worker: evidence\_audit\_worker

    \- if\_task\_type: release\_decision

      use\_worker: release\_judge\_worker

    \- if\_task\_type: growth\_diagnosis

      use\_worker: growth\_diagnosis\_worker

    \- if\_task\_type: worker\_failure

      use\_workers:

        \- failure\_attribution\_worker

        \- worker\_evaluator\_worker

    \- if\_task\_type: decision\_market

      use\_workers:

        \- proposal\_builder\_worker

        \- proposal\_scorer\_worker

        \- critic\_worker

        \- synthesis\_worker

        \- final\_decision\_judge\_worker

OpenCode 的逻辑：

先查 registry

如果有合适 Worker → 调用

如果没有 → 创建 worker\_candidate

worker\_candidate 先作为 experimental worker

通过 eval / ratchet 后转 active

## **6.7 新 Worker 如何创建**

当没有合适 Worker 时，OpenCode 可以创建新 Worker，但必须走流程：

OpenCode identifies capability gap

  ↓

create Worker Candidate Spec

  ↓

Decision / Review if high impact

  ↓

seed eval cases

  ↓

test on historical evidence

  ↓

Worker Evaluator scores

  ↓

Ratchet Judge approves

  ↓

Auto Versioner registers worker

Worker 生命周期：

worker\_lifecycle:

  candidate:

    allowed\_for: test\_runs\_only

  experimental:

    allowed\_for: low\_risk\_runs

  active:

    allowed\_for: production\_runs

  deprecated:

    allowed\_for: none

## **6.8 Worker 和 Manual 的关系**

每个 Worker 都必须绑定 Manual。

worker\_manual\_binding:

  worker\_id: seo\_research\_worker

  required\_manuals:

    \- growth-manual

    \- product-manual

    \- revenue-manual

    \- risk-manual

Worker 执行前注入：

relevant\_manual\_capsule.yaml

Worker 执行后可能产出：

manual\_update\_candidate.yaml

这样 Worker 不是孤立执行，而是在公司 Manual 约束下执行，并反哺 Manual。

---

# **7\. Decision Market / Option Discovery & Decision Engine**

Decision Market 的新定位是：

**所有存在方案不确定性的任务，都应该先进入 Decision Market。**

它不只是重大决策系统，而是默认的方案发现与裁决机制。

它解决：

不知道选哪个方案

不知道用哪个 Worker

不知道任务怎么拆更好

不知道要不要做

不知道怎么做最稳

不知道怎么设计更合理

不知道当前计划是否遗漏关键角度

## **7.1 Decision Market 何时进入流程**

每个任务进入 OpenCode 后，先做：

Task Classification

  ↓

Decision Need Score

  ↓

选择 skip / mini / standard / full Decision Market

---

## **7.2 极简单任务：可以跳过 Decision Market**

例如：

修正文档错别字

更新一个已知字段

追加一条 ledger

生成 daily snapshot

格式化一个 yaml

把已完成文件归档

刷新状态文件

必须同时满足：

trivial\_task\_policy:

  can\_skip\_decision\_market\_if\_all\_true:

    \- single\_known\_action

    \- no\_strategy\_choice

    \- no\_architecture\_choice

    \- no\_worker\_choice\_uncertainty

    \- no\_manual\_policy\_change

    \- no\_user\_visible\_product\_change

    \- no\_release\_risk

    \- reversible

    \- expected\_runtime\_under\_5\_minutes

流程：

Task

  ↓

Direct Execution

  ↓

Light Self Check

  ↓

Evidence Lite

---

## **7.3 普通任务：Mini Decision Market**

适合：

写一篇内容

优化一个页面

设计一个小组件

修复一个非紧急 bug

更新一个 worker prompt

新增一个运营检查

生成一个内容计划

配置：

mini\_decision\_market:

  proposals: 3

  profiles:

    \- fast\_and\_simple

    \- robust\_and\_safe

    \- high\_leverage

  scoring\_dimensions:

    \- goal\_alignment

    \- feasibility

    \- risk

    \- time\_to\_value

    \- evidence\_quality

  critic\_required: true

  synthesis\_required: true

---

## **7.4 中高不确定任务：Standard Decision Market**

适合：

增长方案

产品功能设计

内容集群设计

Worker 进化方案

Manual 更新方案

Loop 策略

技术架构调整

运营纠偏

财务优化

配置：

standard\_decision\_market:

  proposals: 5-7

  profiles:

    \- business\_value

    \- execution

    \- risk

    \- evidence

    \- user\_value

    \- contrarian

  scoring\_dimensions:

    \- goal\_alignment

    \- expected\_value

    \- feasibility

    \- time\_to\_value

    \- evidence\_quality

    \- risk\_control

    \- learning\_value

    \- reversibility

    \- cost\_efficiency

  adversarial\_review: true

  synthesis: true

  final\_judge: true

---

## **7.5 高风险任务：Full Decision Market \+ 审批**

适合：

生产部署

付款 / 收款配置

法律政策

GM system 修改

权限模型变化

重大架构变化

Manual 高优先级原则更新

数据迁移

安全相关修改

流程：

Task

  ↓

Full Decision Market

  ↓

Feynman Review

  ↓

Risk Audit

  ↓

Evidence Audit

  ↓

Release Judge

  ↓

Founder Approval if needed

  ↓

Execute / Release

---

## **7.6 Decision Need Score**

不用“重大”作为唯一条件，而使用 Decision Need Score。

decision\_need\_score:

  dimensions:

    uncertainty:

      weight: 0.25

    number\_of\_possible\_paths:

      weight: 0.20

    expected\_impact:

      weight: 0.20

    reversibility\_risk:

      weight: 0.15

    manual\_or\_worker\_change:

      weight: 0.10

    user\_visible\_change:

      weight: 0.10

  thresholds:

    skip\_decision\_market: "\< 20"

    mini\_decision\_market: "20-49"

    standard\_decision\_market: "50-79"

    full\_decision\_market: "\>= 80"

---

## **7.7 Proposal Profiles 示例**

proposal\_profiles:

  \- profile\_id: seo\_growth\_operator

    lens: "Search traffic, topic clusters, indexing, CTR, internal links"

  \- profile\_id: affiliate\_revenue\_operator

    lens: "Affiliate conversion, tool comparisons, CTA placement, revenue per page"

  \- profile\_id: ai\_news\_editor

    lens: "AI news freshness, trend capture, news-to-evergreen conversion"

  \- profile\_id: product\_growth\_operator

    lens: "Newsletter, retention, productized tools, repeat visits"

  \- profile\_id: technical\_operator

    lens: "CMS, tracking, automation, content pipeline, site performance"

  \- profile\_id: risk\_and\_compliance\_reviewer

    lens: "Factuality, disclosure, copyright, platform rules, legal risk"

  \- profile\_id: contrarian\_operator

    lens: "Challenge assumptions, find simpler or higher-leverage alternatives"

---

## **7.8 Scoring Rubric**

scoring\_rubric:

  dimensions:

    goal\_alignment:

      weight: 0.20

    expected\_value:

      weight: 0.18

    feasibility:

      weight: 0.15

    time\_to\_value:

      weight: 0.10

    evidence\_quality:

      weight: 0.12

    risk\_control:

      weight: 0.10

    learning\_value:

      weight: 0.07

    reversibility:

      weight: 0.04

    cost\_efficiency:

      weight: 0.04

  score\_range: 0-100

  minimum\_viable\_score: 75

  approval\_threshold: 85

规则：

Proposal Builder 不能给自己最终打分。

Final Judge 必须独立于 Proposal Builder。

Risk Judge 必须看 assumptions 和 evidence，不只看 summary。

---

# **8\. Feynman Engine / Adversarial Check**

Feynman Engine 的新定位：

**它不是 Loop 专用，而是所有非极简单任务的默认对抗性检查机制。**

它贯穿：

Plan Check

Batch Check

Delivery Check

Release Check

---

## **8.1 极简单任务：可以跳过 Feynman**

必须同时满足：

can\_skip\_feynman\_if\_all\_true:

  \- trivial\_task

  \- deterministic\_action

  \- reversible

  \- no\_user\_visible\_change

  \- no\_policy\_change

  \- no\_worker\_change

  \- no\_manual\_change

  \- no\_release\_risk

---

## **8.2 普通任务：Feynman Lite**

普通任务至少要有轻量检查。

feynman\_lite:

  reviewers:

    \- goal\_alignment\_checker

    \- risk\_checker

  required\_questions:

    \- "这个任务是否真的对齐目标？"

    \- "有没有明显风险或遗漏？"

    \- "是否有必要证据？"

    \- "是否可回滚？"

  outputs:

    \- feynman\_lite\_check.yaml

---

## **8.3 标准任务：Standard Feynman Review**

standard\_feynman\_review:

  reviewers:

    \- technical\_feasibility

    \- business\_value

    \- risk

    \- evidence\_quality

  veto\_blocks:

    \- fabricated\_fact

    \- missing\_required\_output

    \- no\_evidence

    \- violates\_manual

    \- unsafe\_action

    \- not\_linked\_to\_goal

  outputs:

    \- feynman\_review.yaml

    \- required\_revisions.yaml

    \- vetoes.yaml

---

## **8.4 高风险任务：Full Feynman Gate**

full\_feynman\_gate:

  reviewers:

    \- technical\_feasibility

    \- business\_value

    \- risk

    \- evidence\_quality

    \- security

    \- rollback

    \- manual\_consistency

  final\_outcomes:

    \- accept

    \- accept\_with\_conditions

    \- retry

    \- revise

    \- reject

    \- founder\_approval\_required

---

## **8.5 Feynman Engine 放在哪里**

执行前：

Decision Market 输出方案

  ↓

Feynman Review 检查方案是否能执行、是否有风险、是否缺证据

  ↓

OpenCode 执行

执行中：

Loop Batch 完成

  ↓

Feynman Gate 检查 batch 是否通过

  ↓

决定继续 / retry / split / stop

执行后：

Evidence Packet 生成

  ↓

Feynman / Evidence Audit 检查是否真完成

  ↓

Release Judge

---

# **9\. 修正后的任务执行总流程**

1\. Task Intake

   GM / Scheduler / Operating Program / Incident / Manual / Worker Evolution 产生任务

2\. Task Classification

   OpenCode 判断任务类型、风险、复杂度、不确定性

3\. Decision Need Score

   判断是否需要抽卡：

     skip / mini / standard / full

4\. Decision Market

   生成候选方案、评分、critic、合成、裁决

5\. Plan Formation

   OpenCode 根据裁决生成 Project Plan / Task Frontier Seed / Worker Invocation / Loop Request

6\. Feynman Pre-Execution Check

   检查方案是否可执行、是否风险可控、是否证据足够

7\. Execution

   低风险：OpenCode 直接 Build

   批量任务：Loop Execution

   Worker 任务：Controller 通过 tmux 启动 Hermes Worker

8\. Feynman / Evidence Check

   检查产物、batch、evidence

9\. OpenCode Synthesis

   生成 Evidence Packet / Delivery Packet / Manual Update Candidate / Worker Evolution Candidate

10\. Release Judge / Auto Versioner

   根据风险决定自动合并、Judge、审批、版本、回滚点

11\. GM Report

   GM 读取 User Report Packet，向用户汇报

---

# **10\. 执行模式矩阵**

| 任务类型 | Decision Market | Feynman | 执行方式 |
| ----- | ----- | ----- | ----- |
| 极简单确定性任务 | 跳过 | 跳过或 self-check | OpenCode 直接执行 |
| 普通低风险任务 | Mini | Lite | OpenCode 执行 |
| 普通但有方案选择 | Mini / Standard | Lite / Standard | OpenCode \+ Worker |
| 增长 / 产品 / 内容策略 | Standard | Standard | Decision → Frontier → Loop |
| Worker 进化 | Standard | Standard | Worker Eval → Evolver → Ratchet |
| Manual 更新 | Standard | Standard / Full | Evidence → Manual Patch → Judge |
| 发布 / 部署 | Full | Full | Release Judge \+ Approval |
| GM system 修改 | Full | Full | Evolution Ticket \+ Approval |
| 财务 / 收款 / 法律 | Full | Full | Founder Approval required |

---

# **11\. 循环任务由谁触发、谁检查**

## **11.1 Hourly Loop**

小时级循环是系统健康检查。

触发者：

Controller Scheduler

检查内容：

GM 是否在线

OpenCode serve 是否在线

tmux Worker 是否卡住

active jobs 是否 stalled

关键页面是否在线

pending escalation 是否存在

blocked run 是否存在

输出：

hourly\_health\_snapshot.yaml

runtime\_alerts.yaml

blocked\_jobs.yaml

处理规则：

低风险 runtime 问题 → Controller 自动处理

中风险任务问题 → 创建 OpenCode Review Request

高风险问题 → 通知 GM，由 GM 汇报用户或请求授权

---

## **11.2 4-Hour Operating Loop**

4 小时循环属于运营节奏，需要 GM 做经营判断，但不直接执行。

触发者：

Controller Scheduler 到点触发

  ↓

GM 生成 4-hour operating check

  ↓

Controller 交给 OpenCode

流程：

Controller 定时触发

  ↓

GM 读取运营摘要、产品摘要、任务摘要

  ↓

GM 判断是否需要补救、加速、暂停、升级

  ↓

GM 生成 Four-Hour Operating Packet

  ↓

Controller 投递给 OpenCode

  ↓

OpenCode 决定是否需要 Worker / Loop / 小修任务

---

## **11.3 Daily Loop**

触发者：

Controller Scheduler 到点

  ↓

GM 生成 Daily Operating Packet

流程：

GM collect signals

GM generate operating state snapshot

GM select daily tasks

GM create Daily Operating Packet

Controller dispatches to OpenCode

OpenCode creates task plan / worker invocations / loop requests

Controller executes OpenCode jobs and Worker jobs

OpenCode synthesizes results

Controller verifies evidence

GM receives Delivery Packet

GM sends passive daily brief

---

## **11.4 Weekly Loop**

GM growth review

OpenCode audits GM behavior

OpenCode reviews Worker / Skill performance

Manual update candidates generated

Knowledge cards reviewed

Task Frontier backlog cleaned

Decision outcomes reviewed

---

## **11.5 Monthly Loop**

Strategy review

GM performance review

Manual release

Worker evolution review

Operating Program evolution

Versioned release

Possible GM Evolution

---

# **12\. Loop Execution Engine**

Loop Execution 不由 GM 直接触发。

正确触发链：

GM 生成目标或 Daily Packet

  ↓

Controller 投递给 OpenCode

  ↓

OpenCode 判断这是一个需要循环执行的任务

  ↓

OpenCode 创建 Loop Execution Request

  ↓

Controller 启动 Loop Execution Engine

Loop Execution Request：

loop\_execution\_request:

  request\_id: LER-TECHAI8-001

  created\_by: opencode

  executed\_by: controller

  source:

    run\_id: OI-TECHAI8-001

    operating\_program: OP-TECHAI8-REVENUE-100D

    task\_frontier\_graph: TF-GRAPH-TECHAI8-001

  queue\_type: dynamic

  batch\_policy:

    max\_parallel\_workers: 3

    max\_tasks\_per\_batch: 9

    max\_iterations: 5

  required\_outputs:

    \- loop\_batch\_results/

    \- batch\_feynman\_review.yaml

    \- next\_frontier\_candidates.yaml

    \- loop\_summary.yaml

## **12.1 Manual Queue**

适合明确、短中程、边界清楚的任务。

manual\_queue:

  queue\_id: MQ-TECHAI8-DAILY-2026-0608

  mode: manual

  source: daily\_operating\_packet

  tasks:

    \- task\_id: T001

      title: "刷新 3 篇低 CTR 文章标题"

    \- task\_id: T002

      title: "检查 AI 工具页 CTA 是否缺失"

## **12.2 Dynamic Queue**

适合超大复杂任务、长期知识填充、市场研究、Manual 更新、内容集群建设。

dynamic\_queue:

  queue\_id: DQ-TECHAI8-GROWTH-001

  mode: dynamic

  source: task\_frontier

  root\_goal: "Grow techai8.com to $100/day"

  expansion\_policy:

    max\_new\_tasks\_per\_round: 20

    max\_active\_tasks: 9

    max\_total\_open\_tasks: 100

    max\_depth: 3

  stop\_policy:

    max\_runtime\_hours: 4

    max\_iterations: 5

    stop\_if\_no\_high\_value\_tasks: true

    stop\_if\_quality\_gate\_fails\_twice: true

## **12.3 Loop Batch**

loop\_batch:

  batch\_id: LB-TECHAI8-2026-0608-001

  source\_queue: DQ-TECHAI8-GROWTH-001

  created\_by: task\_frontier

  executed\_by: loop\_execution\_engine

  max\_parallel\_workers: 3

  max\_tasks: 9

  tasks:

    \- task\_id: TF-001

      worker\_type: research\_worker

      priority: 0.91

    \- task\_id: TF-002

      worker\_type: seo\_content\_worker

      priority: 0.87

    \- task\_id: TF-003

      worker\_type: evidence\_audit\_worker

      priority: 0.82

  batch\_stop\_conditions:

    \- all\_required\_outputs\_exist

    \- no\_blocking\_feynman\_veto

    \- max\_runtime\_reached

    \- max\_failed\_tasks\_reached

  required\_outputs:

    \- batch\_result.yaml

    \- worker\_outputs/

    \- feynman\_review.yaml

    \- next\_frontier\_candidates.yaml

---

# **13\. Loop 结果由谁检查**

分三层检查。

第一层：Controller 机械检查。

required\_outputs 是否存在

DONE.md 是否存在

output\_dir 是否有内容

tmux session 是否正常退出

是否 timeout

是否 stalled

是否有 failure\_report

Controller 不判断内容质量。

第二层：Feynman Engine / Evidence Audit 质量检查。

是否完成目标

是否缺输出

是否有幻觉

是否违反 Manual

是否没有证据

是否偏离业务目标

是否需要 retry / split / merge / stop

第三层：OpenCode 综合判断。

OpenCode 读取：

worker\_outputs/

batch\_result.yaml

feynman\_gate\_result.yaml

evidence\_audit.yaml

next\_frontier\_candidates.yaml

然后决定：

继续下一批

修正任务

拆分任务

合并任务

停止 loop

生成 Delivery Packet

提出 Manual Update

提出 Worker Evolution Ticket

GM 只看 OpenCode 的 Delivery Packet 和 User Report Packet。

---

# **14\. Task Frontier**

Task Frontier 是大型任务前沿控制器，不是 Controller，也不是 Loop Engine。

它负责：

任务图

候选任务

去重

评分

优先级

active window

batch selection

停止条件

任务选择机制：

Decision Market final plan

  ↓

Task Frontier seed

  ↓

task graph

  ↓

candidate tasks

  ↓

score / dedupe / prioritize

  ↓

Loop Batch

Task Node：

task\_node:

  task\_id: TF-TECHAI8-001

  program\_id: OP-TECHAI8-REVENUE-100D

  parent\_id: ROOT

  depth: 1

  title: "建立 AI 工具收入页内容集群"

  task\_type: planning

  status: candidate

  reason:

    \- "目标是 $100/day，收入页比普通资讯更有转化价值"

  evidence\_refs:

    \- enhanced\_plan.yaml

    \- growth\_manual\_capsule.yaml

  expected\_outputs:

    \- content\_cluster\_plan.yaml

    \- priority\_pages.yaml

  score:

    expected\_value: 0.9

    urgency: 0.8

    uncertainty: 0.5

    cost: 0.4

    priority: 0.82

  stop\_conditions:

    \- "content\_cluster\_plan exists"

    \- "priority\_pages exists"

    \- "Feynman review passes"

没有 `expected_outputs` 和 `stop_conditions` 的任务不能进入执行队列。

---

# **15\. Operating Program 和运营节奏**

长期目标必须成为 Operating Program。

operating\_program:

  program\_id: OP-TECHAI8-REVENUE-100D

  owner\_agent: gm

  implementation\_agent: opencode

  goal:

    metric: daily\_revenue\_usd

    target: 100

    success\_condition: "14-day average \>= 100"

  milestones:

    \- id: M1

      name: "Tracking ready"

      target\_day: 3

    \- id: M2

      name: "$10/day validation"

      target\_day: 30

    \- id: M3

      name: "$30/day growth"

      target\_day: 60

    \- id: M4

      name: "$100/day scale"

      target\_day: 90

首次搭建必须产出：

operating\_program.yaml

operating\_calendar.yaml

hourly\_loop.yaml

four\_hour\_loop.yaml

operating\_metrics.yaml

stage\_strategy.yaml

trigger\_rules.yaml

correction\_policy.yaml

gm\_evaluation\_policy.yaml

gm\_evolution\_policy.yaml

backlog\_generation\_policy.yaml

daily\_operating\_packet\_template.yaml

weekly\_growth\_review\_template.yaml

monthly\_strategy\_review\_template.yaml

---

# **16\. GM 用户汇报机制**

GM 必须能给用户汇报清楚：

当前在做什么

已完成什么

卡在哪里

谁在执行

质量检查是否通过

是否有风险

是否需要用户授权或凭证

下一步是什么

GM 不直接读 Worker 原始输出，而是读取：

run\_status.yaml

opencode\_job\_status.yaml

loop\_status.yaml

worker\_job\_summary.yaml

feynman\_gate\_result.yaml

delivery\_packet.yaml

user\_report\_packet.yaml

risk\_summary.yaml

next\_actions.yaml

User Report Packet：

user\_report\_packet:

  packet\_id: URP-OI-TECHAI8-001-001

  receiver: gm

  produced\_by:

    \- controller

    \- opencode

  summary:

    status: yellow

    headline: "第一批增长任务正在执行，主要缺口是 affiliate 证据。"

  completed:

    \- "Decision Market completed"

    \- "Task Frontier seeded"

    \- "6/9 tasks completed in current loop batch"

  running:

    \- "2 Hermes Workers still running in tmux"

  blocked:

    \- "No production publish until affiliate availability is verified"

  risks:

    \- severity: medium

      issue: "affiliate availability missing"

  recommended\_message\_to\_user:

    \- "当前不需要你操作。后续可能需要 affiliate 账号或收款信息。"

---

# **17\. Worker Evolution Engine**

Worker Evolution Engine 包含：

Worker Evaluator

Worker Evolver

Failure Attribution Engine

Ratchet Policy

Regression Eval

流程：

Worker Run

  ↓

Result \+ Evidence

  ↓

Worker Evaluator 打分

  ↓

Failure Attribution 分类

  ↓

Candidate Worker Patch

  ↓

Regression Eval

  ↓

Ratchet Check

  ↓

Version Bump / Revert

失败归因分类：

worker\_defect

execution\_error

task\_input\_defect

environment\_defect

external\_uncertainty

manual\_conflict

棘轮规则：

分数提高才保留

出现关键退步就回滚

schema 破坏就回滚

安全性下降就回滚

提升不足则停止继续优化

---

# **18\. Manual OS**

Manual 是公司运行的宪法、流程、经验、策略、风险边界和执行标准。

目录：

.agentcomos/manual-os/

  company-manual/

  operating-manual/

  product-manual/

  growth-manual/

  engineering-manual/

  worker-manual/

  customer-manual/

  revenue-manual/

  risk-manual/

  environment-manual/

  decision-manual/

  manual-ledger/

  manual-release/

Manual 使用方式：

GM 决策前读取

OpenCode plan 前读取

Worker invocation 前注入

Decision Market 评分时参考

Skill / Worker evolution 时参考

Release Judge 审查时对照

Operating Program 每周更新候选

Manual 更新流程：

Task Evidence

  ↓

Learning Packet

  ↓

Observation

  ↓

Pattern Candidate

  ↓

Knowledge Card

  ↓

Manual Update Proposal

  ↓

OpenCode edits manual patch

  ↓

Worker Evidence Audit

  ↓

Manual Release Judge

  ↓

GitTree / Auto Versioner

  ↓

Manual version bump

Manual 不能由 GM 或 Worker 直接修改。

---

# **19\. Environment KB**

Environment KB 管真实环境事实。

每次任务执行前生成：

runtime\_env\_snapshot

runtime\_context\_bundle

包含：

Python / Node / Bash 版本

包管理器

项目命令

当前分支

worktree 路径

timezone

当前日期

allowed commands

forbidden commands

unknown fact policy

retry policy

铁律：

Agent 不允许猜版本

Agent 不允许猜命令

Agent 不允许猜时区

Agent 不允许猜路径

Agent 不允许重复失败命令死循环

---

# **20\. Model & Runtime Adapter**

Model & Runtime Adapter 负责模型和执行后端选择。

目录：

.agentcomos/model-runtime/

  model\_registry.yaml

  provider\_registry.yaml

  runtime\_registry.yaml

  capability\_matrix.yaml

  routing\_policy.yaml

  cost\_policy.yaml

  fallback\_policy.yaml

  model\_scorecards/

  usage\_ledger/

职责：

不同 LLM provider 适配

不同模型能力登记

OpenCode / Hermes / Direct API / tmux / Kanban runtime 选择

按任务类型路由模型

成本控制

fallback

Builder / Judge 独立性

模型表现 scorecard

usage ledger

---

# **21\. GitTree / Auto Versioner 管理范围**

GitTree / Auto Versioner 管 AgentComOS 平台与能力资产：

AgentComOS Controller 代码

GM system / policy / manual

OpenCode Project Kit

.opencode/commands

.opencode/agents

OpenCode 配置

Worker specs

Worker skills

Worker rubrics

Worker scorecards

Manual OS

Environment KB

Model Runtime policies

Operating Program 定义

Task Frontier policies

Loop Execution policies

Decision Market policies

Release Judge policies

GitTree policies

Versioning policies

也管理被 OpenCode 实施的项目配置和代码改动：

techai8-site 代码

内容模板

组件

tracking 配置

SEO schema

CMS 配置

部署配置

不管理大量运营原始数据：

Analytics 原始事件

Search Console 原始数据

广告平台原始明细

affiliate 原始点击流

产品业务数据库

日志流

大体积爬虫数据

这些进入：

data warehouse

object storage

runtime ledger

daily snapshot

evidence reference

rollup summary

---

# **22\. 版本与回滚**

版本对象：

agentcomos-core v0.4.0

gm v0.3.2

opencode-project-kit v0.2.0

worker/seo\_content\_worker v0.3.1

skill/ai\_tool\_review\_writer v0.2.4

manual/growth-manual v2026.06.08

program/techai8-revenue-100d v0.5.0

environment-kb/local-dev v0.2.1

model-runtime/routing-policy v0.1.3

decision-market/scoring-rubric v0.1.0

loop-execution/policy v0.1.0

版本升级规则：

patch：

  文档小修、prompt 小修、rubric threshold 微调、非破坏性修复

minor：

  新 worker、新 manual section、新 operating loop、新 trigger rule、新 eval case、worker 能力增强

major：

  schema breaking change、GM system 重写、权限模型变化、Release Judge policy 变化、deployment architecture 变化

回滚对象：

GM version

Worker version

Skill version

Manual version

Operating Program version

OpenCode Project Kit version

Environment KB version

Model Runtime policy version

Decision Market policy version

Loop Execution policy version

Project repo release

回滚不是还原运营数据，而是还原：

平台逻辑

worker 能力

manual 结论

配置

代码

策略

部署定义

运营数据只保留历史，不回滚。

---

# **23\. Evidence Packet**

所有非 trivial 任务必须有 Evidence Packet。

evidence\_packet/

  original\_intent.yaml

  opencode\_project\_plan.yaml

  decision\_market\_record.yaml

  enhanced\_plan.yaml

  runtime\_context\_bundle.yaml

  manual\_context/

    relevant\_manual\_capsules.yaml

  environment\_evidence/

    env\_snapshot.yaml

    tool\_versions.yaml

    project\_commands.yaml

    command\_attempt\_log.yaml

    unknown\_facts.yaml

  worker\_outputs/

  loop\_execution/

    loop\_batch.yaml

    batch\_result.yaml

    feynman\_gate\_result.yaml

  git\_evidence/

    base\_commit.txt

    branch.txt

    changed\_files.txt

    patch.diff

    unauthorized\_path\_report.yaml

  tests/

  reviews/

    feynman\_review.yaml

    risk\_audit.yaml

    evidence\_audit.yaml

  release/

    release\_judge\_decision.yaml

    rollback\_target.txt

完成依据是 Evidence，不是 Agent 自称完成。

---

# **24\. 最终目录结构**

.agentcomos/

  gm/

  controller/

  opencode/

  opencode-runtime/

  workers/

  worker-evolution/

  decision-market/

  task-frontier/

  loop-execution/

  manual-os/

  knowledge-os/

  model-runtime/

  environment-kb/

  cognition/

  operating-programs/

  gittree/

  versioning/

  quality/

  runs/

  ledgers/

  observability/

  deployment/

---

# **25\. 推荐落地路线**

## **Phase 1：运行底座**

Controller

GM Discord bridge

OpenCode serve 管理

run 目录

job/session ledger

Environment KB 最小 probe

## **Phase 2：OpenCode 闭环**

GM → Operating Intent

Controller → OpenCode run \--attach

OpenCode → Project Plan

Delivery Packet → GM

## **Phase 3：Core Worker Starter Pack Tier 0 / Tier 1**

feynman\_review\_worker

evidence\_audit\_worker

risk\_audit\_worker

release\_judge\_worker

failure\_attribution\_worker

worker\_evaluator\_worker

ratchet\_judge\_worker

proposal\_builder\_worker

proposal\_scorer\_worker

critic\_worker

synthesis\_worker

final\_decision\_judge\_worker

## **Phase 4：tmux Hermes Worker Pool**

Worker Invocation

tmux session registry

worker output collection

timeout / stalled handling

## **Phase 5：Decision Market \+ Feynman 默认流程**

Task Classification

Decision Need Score

Mini / Standard / Full Decision Market

Feynman Lite / Standard / Full

## **Phase 6：Loop Execution \+ Task Frontier**

manual queue

dynamic queue

loop batch

Feynman Gate

batch result

next frontier candidates

## **Phase 7：Manual OS \+ Worker Evolution**

manual update proposal

manual release

worker scorecard

failure attribution

ratchet

version bump / revert

## **Phase 8：Operating Program**

hourly loop

4-hour loop

daily loop

weekly loop

monthly loop

correction policy

GM evaluation

---

# **26\. 最终无冲突规则**

1\. 用户只和 GM 沟通。

2\. GM 不碰 Worker。

3\. Worker 只能由 OpenCode 调用。

4\. Hermes Worker 是 tmux 启动的 Hermes CLI 实例，不是新写的 worker 程序。

5\. Controller 执行 Worker Invocation，但不决定调用哪个 Worker。

6\. OpenCode 是工程总包、Worker Manager 和唯一 Worker 调用者。

7\. Core Worker Starter Pack 是系统初始化默认能力库。

8\. Hermes subagent 不进入 AgentComOS 设计层。

9\. OpenCode Runtime 常驻，session 由 Controller 管。

10\. 长任务异步 job 化，Controller 不同步阻塞等待。

11\. Task Frontier 和 Controller 是两个模块：一个选任务，一个跑任务。

12\. Loop Execution Engine 执行任务批次，不做公司战略判断。

13\. tmux 只是一种 Hermes Worker runtime，由 Controller 管。

14\. Decision Market 是所有有方案不确定性任务的默认方案发现与裁决机制。

15\. Decision Market 不直接执行任务，只输出裁决、方案和 Task Frontier seed。

16\. Feynman Engine 是所有非极简单任务的默认对抗检查机制。

17\. Feynman Engine 覆盖执行前、执行中、执行后。

18\. Manual 是公司最核心资产。

19\. Knowledge OS 负责产出 Manual 的候选知识。

20\. Manual 更新必须走 Evidence、Review、Release 和 Version。

21\. Worker 进化必须走 Evaluation、Failure Attribution、Regression 和 Ratchet。

22\. GitTree / Auto Versioner 管平台、agent、worker、manual、skill、项目代码和策略版本。

23\. 运营原始数据不作为 GitTree 版本对象，只做 ledger、snapshot、evidence reference。

24\. 所有环境事实走 Environment KB。

25\. 所有非 trivial 任务走 Evidence Packet。

26\. 长期目标必须是 Operating Program。

27\. 小时级、4 小时级、每日、每周、每月循环共同构成运营节奏。

28\. GM 必须能向用户清楚汇报当前状态、执行进展、风险、卡点和下一步。

---

# **27\. 最终版本定义**

AgentComOS v2.8

AI-Native Company Operating Platform

Single-GM Interface

Controller-Governed Runtime

OpenCode-Managed Worker System

Core-Worker-Starter-Pack

Hermes-CLI-Worker-Powered

tmux-Hermes-Worker-Pool

Decision-Market-Default

Feynman-Default-Adversarial-Check

Task-Frontier-Controlled

Loop-Execution-Driven

Manual-OS-Centered

Worker-Evolution-Driven

GitTree-Governed

Auto-Versioned

Environment-KB-Grounded

Evidence-Judged

Operating-Program-Driven

Knowledge / Manual / Worker / Skill / GM Evolving

最核心的一句话：

**AgentComOS v2.8 是 AI-native 公司的核心支撑平台：GM 负责经营和用户沟通，OpenCode 负责工程、方案发现和 Worker 管理，Controller 通过 OpenCode serve、tmux 和 Hermes CLI 稳定执行任务，Decision Market 默认用于所有有不确定性的方案选择，Feynman Engine 默认用于所有非极简单任务的对抗检查，Core Worker Starter Pack 让系统第一天具备运营、增长、开发、财务、运维、评审、Manual 和进化能力，Task Frontier 与 Loop Execution 负责复杂任务批量推进，Manual 沉淀公司智慧，Worker Evolution 进化公司能力，GitTree / Auto Versioner / Environment KB 保证整个平台长期可控、可审计、可回滚。**

