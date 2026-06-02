# QA Agent 项目审查报告（大白话版）

## 先说结论

这个项目的方向是对的：想把 PRD 分析、门禁评审、用例生成、用例评审、测试执行、脚本转换这些 QA 工作串成一条多 Agent 流水线。

但现在的问题是：**说明文档看起来像全自动流水线，实际代码里还有很多地方会卡住、误判、跳过检查，或者让不同平台行为不一致。**

简单打分：**2 / 5 分**。

目前不是“完全不能用”，而是更像一个半成品自动化系统：

- Cursor 路径做得最多，因为有 Hook 自动推进。
- Codex / Claude Code 路径还不够闭环，主要靠主 Agent 自己记得继续。
- Gate 校验不够硬，有“假通过”的风险。
- 状态文件和运行产物容易留下互相矛盾的状态。

---

## 1. 默认流程可能自己把自己卡死

代码里有个逻辑：只要从 `prd-analyze` 开始跑，就默认强制重跑。

这本来是好意：防止旧产物被误用。

但问题是，子 Agent 已经跑完、产物已经生成之后，编排器还是会继续说：

> 我不认旧产物，你这个阶段没完成。

于是流水线可能一直卡在同一个阶段。

大白话解释：

> 员工已经交了作业，但系统一直说“我不看，你必须重新交”，所以永远过不了。

影响：

- `--auto` 自动模式可能跑不完。
- Codex 默认从 `prd-analyze` 开始时尤其容易卡。
- 断点续跑会变得不可靠。

证据：

- `/Users/a58/qa-agent/scripts/pipeline_runner.py:723-727`
- `/Users/a58/qa-agent/scripts/pipeline_runner.py:290-292`
- `/Users/a58/qa-agent/scripts/pipeline_runner.py:571-575`

建议：

- “强制重跑”只能影响是否启动子 Agent。
- 子 Agent 跑完以后，检查产物时不能继续因为 force 而拒绝产物。

---

## 2. PRD Gate reject 后，流水线可能不知道怎么正确停

设计上应该是：

- gate pass：继续进入用例生成。
- gate reject：停下来，把问题交给产品。

但 Python 编排器现在判断 `prd-gate` 是否完成时，只认 `pass`。

如果 gate 结果是 `reject`，它可能不认为这个阶段完成了，于是不会正常进入“停线 + 输出打回文档”的逻辑。

大白话解释：

> 红灯亮了，本来应该停车；但系统说“我只认识绿灯，红灯不算结果”，于是车卡在路口。

影响：

- 产品打回文档可能不会稳定生成。
- Codex / Claude Code 路径容易卡在 gate 阶段。
- Cursor Hook 对 reject 做了额外处理，但 Python runner 没有同样的处理，三平台行为不一致。

证据：

- `/Users/a58/qa-agent/scripts/pipeline_runner.py:298-325`
- `/Users/a58/qa-agent/scripts/pipeline_runner.py:450-481`
- `/Users/a58/qa-agent/scripts/pipeline_runner.py:849-878`
- `/Users/a58/qa-agent/.cursor/hooks/qa-pipeline-next.sh:157-172`

建议：

- `prd-gate` 阶段只要有 gate report，就应该算“有结果”。
- 具体是 pass 还是 reject，交给 `finalize_stage()` 处理。

---

## 3. Gate pass 太容易“假通过”

PRD Gate 是整个流水线最重要的门。

它应该严格检查：

- 产品视角是否通过。
- 研发视角是否通过。
- QA 视角是否通过。
- 红队是否通过。
- 测试义务是否真的被覆盖。
- 有没有假覆盖。

但现在有些关键字段不是强制的。

比如 gate report 里可以缺少 `test_point_review`，也可能没有严格要求 `false_coverage_count=0`。

大白话解释：

> 考试本来要检查语文、数学、英语都及格；现在只要写了“我及格了”，系统可能就放行。

影响：

- PRD 可能还没有真正测试就绪，却进入用例生成。
- “场景声称覆盖了某条测试义务，但步骤根本没验证它”的假覆盖可能漏过去。

证据：

- `/Users/a58/qa-agent/contracts/prd-gate-report.schema.json:6`
- `/Users/a58/qa-agent/contracts/prd-gate-report.schema.json:74-82`
- `/Users/a58/qa-agent/scripts/validate-artifacts.py:147-172`
- `/Users/a58/qa-agent/scripts/validate_obligation_coverage.py:123-130`
- `/Users/a58/qa-agent/scripts/validate_obligation_coverage.py:156-162`
- `/Users/a58/qa-agent/workspace/artifacts/.test-point-coverage-precheck.json:1-53`

建议：

- gate pass 时必须要求 `test_point_review` 存在。
- gate pass 时必须要求四个评审角色都 pass。
- gate pass 时必须要求 `false_coverage_count=0`。
- 如果 precheck 里 `ok=false`，不能 pass。

---

## 4. Codex 和 Claude Code 没有真正的自动链路

Cursor 有 Hook，可以在一个子 Agent 跑完后自动推进下一个阶段。

但 Codex / Claude Code 没有同等机制。

文档里写的是：

> 每阶段脚本生成 prompt 后退出，主 Agent 拉起子 Agent，完成后再运行同一条命令。

这不是完整自动化，而是依赖主 Agent 自己记得做下一步。

大白话解释：

> Cursor 像有传送带；Codex 和 Claude Code 更像“师傅喊一声，下一个人再接着干”。如果没人喊，流水线就停了。

影响：

- Codex 默认 IDE 模式不是真正自动。
- prompt 生成后可能没人执行。
- 子 Agent 完成后，如果没有再次运行命令，流程不会继续。

证据：

- `/Users/a58/qa-agent/AGENTS.md:43-45`
- `/Users/a58/qa-agent/scripts/pipeline_runner.py:759-761`
- `/Users/a58/qa-agent/scripts/pipeline_runner.py:873-877`
- `/Users/a58/qa-agent/orchestrators/codex/run-pipeline.sh:21-24`

建议：

- 把 Cursor Hook 里的阶段推进逻辑移到 Python runner 里，让三平台共享。
- Codex 如果无法自动拉子 Agent，就在文档里明确写成“半自动”。
- 临时方案：Codex 子 Agent 完成后，用 `--no-force` 推进已有产物。

---

## 5. test-execute 的 prompt 里输出路径是空的

`test-execute` 阶段应该输出：

- `workspace/artifacts/04-execution-result.json`
- 如果有失败，还要输出 `workspace/artifacts/05b-bug-list.md`

但实际生成的 prompt 里出现了：

```text
Write to: ``
```

大白话解释：

> 你叫员工交作业，但交作业地址是空白的。

影响：

- 子 Agent 可能不知道应该写哪个文件。
- 测试执行结果可能缺失或写错地方。
- Bug 清单可能漏写。

证据：

- `/Users/a58/qa-agent/scripts/pipeline_runner.py:143-170`
- `/Users/a58/qa-agent/pipeline.yaml:127-130`
- `/Users/a58/qa-agent/workspace/artifacts/prompts/test-execute.md:45-52`

建议：

- prompt 生成逻辑要同时支持 `output` 和 `outputs`。
- 如果阶段定义里只有 `outputs[]`，prompt 里也要完整列出来。

---

## 6. pipeline.yaml 和代码没有完全对齐

`pipeline.yaml` 应该是单一真相源。

但现在很多规则在 yaml 里写了一遍，Python runner 里又写了一遍，Cursor Hook 里又写了一遍。

大白话解释：

> 同一套流程有三份说明书，每份都写了一点，迟早会对不上。

影响：

- 改一个阶段时，要改很多地方。
- 很容易出现 yaml 说要产出 A/B/C，代码只认 A。
- Cursor 能跑的逻辑，Codex 不一定能跑。

证据：

- `/Users/a58/qa-agent/pipeline.yaml:42-144`
- `/Users/a58/qa-agent/scripts/pipeline_runner.py:34-35`
- `/Users/a58/qa-agent/scripts/pipeline_runner.py:300-305`
- `/Users/a58/qa-agent/.cursor/hooks/qa-pipeline-next.sh:98-122`

建议：

- 尽量让 runner 读取 `pipeline.yaml` 的 `outputs`、`depends_on`、`gate`、`branches`。
- 不要在 hook 和 runner 里重复写一套阶段规则。

---

## 7. Gate 子阶段只看文件存在，不一定验证文件有效

PRD Gate 分成四个评审子阶段：

- 产品评审
- 研发评审
- QA 评审
- 红队评审

auto 模式里，某个子阶段跑完后，代码主要检查对应文件是否存在。

但“文件存在”不等于“文件有效”。

大白话解释：

> 桌上有一张纸，不代表纸上的内容是对的。

影响：

- 旧文件可能被误用。
- 空洞 findings 可能被 gatekeeper 合并。
- gatekeeper 可能基于坏数据做结论。

证据：

- `/Users/a58/qa-agent/scripts/pipeline_runner.py:254-263`
- `/Users/a58/qa-agent/scripts/validate-artifacts.py:266-281`

建议：

- 每个 gate 子阶段完成后，都要跑对应校验。
- 比如：
  - `prd-gate-product-review`
  - `prd-gate-dev-review`
  - `prd-gate-qa-review`
  - `prd-gate-red-team`

---

## 8. 当前 meta 状态文件有互相矛盾的状态

当前 `00-meta.json` 顶层写着：

```json
"status": "completed"
```

但里面阶段状态又写着：

- `prd-analyze` 是 `waiting_ide_task`
- `prd-gate` 是 `failed`

大白话解释：

> 总报告说“项目已完成”，但任务清单里又写着“第一步还在等人，第二步失败了”。

影响：

- 主 Agent 不知道该从哪里继续。
- 断点续跑容易判断错。
- 用户看到状态会困惑。

证据：

- `/Users/a58/qa-agent/workspace/artifacts/00-meta.json:5-8`
- `/Users/a58/qa-agent/workspace/artifacts/00-meta.json:24-31`
- `/Users/a58/qa-agent/workspace/artifacts/00-meta.json:51`

建议：

- meta 的顶层状态应该由阶段状态自动计算。
- 只要还有 waiting/failed，就不能写 completed。
- 写 meta 时最好用原子写，避免脏读。

---

## 9. case-review 失败重试逻辑不够完整

设计上：

- case-review fail
- 回 case-generate 重试
- 最多重试 2 次
- 超过后升级人工

代码里有这个逻辑，但还有几个隐患：

- 重试时没有清理旧的 `02-test-cases.md`
- 可能继续读取旧产物
- retry_count 只在 meta 里记，状态不够强

大白话解释：

> 评审说作业不合格，要重写；但旧作业还放在那里，系统可能又拿旧作业去评。

影响：

- 重试可能没有真正发生。
- 旧用例可能被误认为新用例。

证据：

- `/Users/a58/qa-agent/scripts/pipeline_runner.py:483-498`
- `/Users/a58/qa-agent/scripts/pipeline_runner.py:905-908`
- `/Users/a58/qa-agent/pipeline.yaml:110-114`

建议：

- 进入 retry_generate 前清理或标记旧的 case-generate 产物。
- 每次重试记录 retry run id。

---

## 10. bug-list-write 角色已经和 pipeline 不一致

现在设计上，失败用例的 bug list 是在 `test-execute` 阶段直接写的。

但 `bug-list-write` skill 还写着自己是 post-process 的独立分支。

大白话解释：

> 项目已经决定“厨师顺手把盘子洗了”，但另一本说明书还写着“有专门洗碗工”。

影响：

- 子 Agent 可能误以为还有独立 bug-list-writer。
- smoke test 也还在尝试生成 bug-list-write prompt。

证据：

- `/Users/a58/qa-agent/skills/test-execute/SKILL.md:23-30`
- `/Users/a58/qa-agent/skills/bug-list-write/SKILL.md:3-5`
- `/Users/a58/qa-agent/pipeline.yaml:132-144`
- `/Users/a58/qa-agent/scripts/test-subagents.sh:91-100`

建议：

- 如果不再需要独立 bug-list-write，就把它改成“格式参考 skill”。
- 如果仍要独立分支，就把它加回 `pipeline.yaml`。

---

## 11. Skill 有一份影子副本已经不同步

主 skill 在：

```text
skills/
```

同步脚本会同步到：

```text
.cursor/skills/
.codex/skills/
.claude/skills/
```

但仓库里还有：

```text
.agents/skills/
```

这份不在同步脚本里，而且已经和主版本不一致。

大白话解释：

> 有一本旧说明书躲在角落里，已经写错了，但没人负责更新它。

影响：

- 如果某个平台读了 `.agents/skills`，就会拿到错误指令。
- 以后维护者可能改了 `skills/`，但忘记 `.agents/skills`。

证据：

- `/Users/a58/qa-agent/scripts/sync-skills.sh:8-10`
- `/Users/a58/qa-agent/scripts/sync-skills.sh:26-33`
- `/Users/a58/qa-agent/.agents/skills/qa-pipeline-start/SKILL.md:26-29`
- `/Users/a58/qa-agent/.agents/skills/qa-pipeline-start/SKILL.md:44`

建议：

- 要么删除 `.agents/skills`。
- 要么把 `.agents/skills` 纳入 `sync-skills.sh`。

---

## 12. README 说 Skill 还是占位，但实际已经不是

README 最后写着：

> Phase 1/2 Skill 内容为占位

但现在很多 Skill 已经有具体流程了，比如：

- `prd-analyze`
- `prd-gate`
- `case-generate`
- `case-review`
- `test-execute`

大白话解释：

> README 说“房子还只是草图”，但实际已经盖了几层楼。

影响：

- 维护者会误判项目成熟度。
- 新人不知道哪些东西能用，哪些还是占位。

证据：

- `/Users/a58/qa-agent/README.md:182-185`
- `/Users/a58/qa-agent/skills/prd-analyze/SKILL.md:12-19`
- `/Users/a58/qa-agent/skills/prd-gate/SKILL.md:11-27`

建议：

- 更新 README。
- 明确哪些 Skill 是可用的，哪些还只是参考。

---

## 13. Codex 的 --check-auth 检查太浅

`--check-auth` 对 Cursor 做了更细的登录态检查。

但对 Codex 和 Claude Code，主要只是检查命令是否存在。

大白话解释：

> 系统只检查“电脑上有没有安装钥匙孔”，没检查“你手里有没有钥匙”。

影响：

- `--check-auth` 可能显示通过。
- 但真正 `--auto` 跑起来时，才发现没登录。

证据：

- `/Users/a58/qa-agent/scripts/launch_subagent.py:35-47`
- `/Users/a58/qa-agent/scripts/launch_subagent.py:179-203`
- `/Users/a58/qa-agent/scripts/pipeline_runner.py:605-617`

建议：

- Codex 要检查真实登录态。
- Claude Code 也要检查真实登录态。
- 不要只检查 CLI 是否存在。

---

## 14. 日志可能泄露 API Key

Cursor auto 模式下，如果设置了 `CURSOR_API_KEY`，代码会把它拼到命令参数里。

然后又把完整命令写进日志。

大白话解释：

> 你把钥匙挂在门上，还把钥匙照片贴到了工作日志里。

影响：

- 本地日志可能泄露 API Key。
- 如果日志被提交、上传或共享，就更危险。

证据：

- `/Users/a58/qa-agent/scripts/launch_subagent.py:67-70`
- `/Users/a58/qa-agent/scripts/launch_subagent.py:139-140`

建议：

- 日志里隐藏 API Key。
- 不要把密钥作为命令行参数写入日志。
- 最好通过环境变量传，不打印。

---

## 15. 日志会保存大量 PRD / prompt / 产物内容

当前日志目录里已经有很多 Cursor 运行日志。

日志里包含：

- prompt 全文
- PRD 相关内容
- gate findings 内容
- 测试义务和场景内容

大白话解释：

> 日志不只是“系统运行记录”，里面可能还有业务需求和评审结论。

影响：

- 业务信息泄露风险。
- 日志越来越大。
- 排障时有用，但需要保留策略。

证据：

- `/Users/a58/qa-agent/workspace/artifacts/logs/`
- `/Users/a58/qa-agent/scripts/launch_subagent.py:151-155`

建议：

- 给日志做保留时间。
- 敏感信息脱敏。
- 区分 debug 日志和普通运行日志。

---

## 16. env.json 是可选的，但提示方式容易让人误会

`test-execute` 阶段里，`env.json` 是可选的。

代码里也确实把它当成可选。

但生成 prompt 时会显示：

```text
workspace/inputs/env.json (MISSING — create before run)
```

大白话解释：

> 明明是可选材料，却提示得像必须补齐。

影响：

- 子 Agent 或用户可能以为不能继续执行测试。
- 实际逻辑和提示不一致。

证据：

- `/Users/a58/qa-agent/scripts/pipeline_runner.py:358-365`
- `/Users/a58/qa-agent/workspace/artifacts/prompts/test-execute.md:45-49`

建议：

- prompt 中标记为 optional。
- 不要写成 `MISSING — create before run`。

---

## 17. 执行结果校验不够严格

`execution-result` schema 要求有 summary 和 cases。

但校验器只检查：

- summary.total 是否等于 cases 数量
- 有失败时是否有 bug list

它没有严格检查：

- summary.pass 是否等于 cases 里 pass 的数量
- summary.fail 是否等于 fail 的数量
- summary.skip 是否等于 skip 的数量
- summary.block 是否等于 block 的数量
- 失败用例是否都有 failure_reason
- evidence 路径是否真的存在

大白话解释：

> 报表说通过 10 个、失败 0 个，但系统没有认真数每一条是不是真的这样。

影响：

- 假执行结果可能通过。
- 没有证据的失败也可能通过。

证据：

- `/Users/a58/qa-agent/contracts/execution-result.schema.json:6-49`
- `/Users/a58/qa-agent/scripts/validate-artifacts.py:337-349`

建议：

- 校验 summary 里的各项计数。
- fail/block 必须有 failure_reason。
- evidence 路径存在性也要校验。

---

## 18. 自动化脚本转换校验太弱

`script-convert` 只检查：

- `05a-scripts/` 目录存在
- 里面有文件

但没有检查：

- 是否每个可自动化且 pass 的用例都有脚本
- manifest 是否符合 schema
- 脚本文件是否真的可运行

大白话解释：

> 只要文件夹里有张纸，就算脚本转换完成；但纸上写的是不是测试脚本没人管。

影响：

- 可能漏转用例。
- 可能生成无效脚本。

证据：

- `/Users/a58/qa-agent/scripts/validate-artifacts.py:99-106`
- `/Users/a58/qa-agent/agents/script-converter.md:20-23`
- `/Users/a58/qa-agent/contracts/automation-script.schema.json:6-23`

建议：

- 如果有 manifest，就必须校验 manifest。
- 根据 `04-execution-result.json` 检查每个 pass + automatable 的用例是否有脚本。
- 至少对 Playwright 脚本跑一次语法检查。

---

## 19. case-generate 的渲染脚本有固定模块名映射

`render_cases_from_blueprint.py` 里写死了一些模块名：

```python
MODULE_HEADING = {
  "mod-phone-password-login": "手机号密码登录",
  ...
}
```

如果是其他项目，模块名就只能退回 module_id。

大白话解释：

> 脚本里还残留着某个旧项目的菜单名。

影响：

- 输出的测试用例可读性不稳定。
- 新项目不一定有好看的模块标题。

证据：

- `/Users/a58/qa-agent/scripts/render_cases_from_blueprint.py:15-21`
- `/Users/a58/qa-agent/scripts/render_cases_from_blueprint.py:43-46`

建议：

- 优先从 blueprint 的 `modules[].name` 读取模块名。
- 不要写死旧项目模块。

---

## 20. 有一个脚本可以从场景反推 TOG，容易削弱 TOG 意义

`bootstrap_obligations_from_scenarios.py` 可以从现有 scenarios 生成 obligations。

这个脚本也许是迁移期工具。

但如果被误用，就会变成：

> 先写场景，再倒推出测试义务。

这和 TOG 的目标相反。

TOG 本来应该来自 PRD / Figma 的可验证义务。

大白话解释：

> 正常应该是“按需求列考试大纲，再出题”；这个脚本可能变成“先出题，再倒编考试大纲”。

影响：

- TOG 可能失去真实门禁意义。
- 假覆盖更容易出现。

证据：

- `/Users/a58/qa-agent/scripts/bootstrap_obligations_from_scenarios.py:1-3`
- `/Users/a58/qa-agent/scripts/bootstrap_obligations_from_scenarios.py:23-42`

建议：

- 明确标记为维护者迁移工具。
- 不要在正常流水线 prompt 里推荐它。
- 如果使用了这个脚本，gate 应该标记为非生产级 TOG。

---

## 21. `sync_obligation_coverage.py` 会直接修改蓝图和 TOG

这个脚本会同时写：

- `00-test-obligations.json`
- `00-test-ready-blueprint.json`

它把场景里的 covers_obligations 同步回 obligations。

大白话解释：

> 一个“同步工具”会改两份核心作业，如果用错了，可能把错误关系固化下来。

影响：

- 假覆盖可能被同步成正式覆盖关系。
- 人很难分清哪些是 Agent 分析出来的，哪些是脚本补上的。

证据：

- `/Users/a58/qa-agent/scripts/sync_obligation_coverage.py:27-34`

建议：

- 同步前先校验 obligation 是否真实存在。
- 同步后保留变更摘要。
- 对 gate 来说，不能只看同步后的覆盖关系，还要看步骤是否真的验证。

---

## 22. `validate-artifacts.py --stage prd-analyze` 会产生副作用

校验器通常应该只检查，不应该修改东西。

但这里 `validate-artifacts.py --stage prd-analyze` 会：

- 写 `.prd-analyze-complete.ok`
- 调用 `sync_obligation_coverage.py`

大白话解释：

> 检查作业的人，不只是打分，还顺手改了作业并盖章。

影响：

- 只读检查和写入动作混在一起。
- 排查问题时，不容易知道文件是 Agent 写的还是校验器改的。

证据：

- `/Users/a58/qa-agent/scripts/validate-artifacts.py:305-315`
- `/Users/a58/qa-agent/scripts/analyze_gate_prerequisites.py:65-80`

建议：

- 把“检查”和“写 marker / 同步覆盖”拆成两个命令。
- 比如：
  - `validate`
  - `finalize-prd-analyze`

---

## 23. `--all` 校验只校验存在的文件，不能发现缺文件

`validate-artifacts.py --all` 逻辑是：

> 哪些产物存在，就校验哪些。

这对临时检查有用。

但如果你想知道“流水线是否完整”，它不够。

大白话解释：

> 体检只检查你带来的报告，没带来的项目就当不存在。

影响：

- 缺少关键产物时，`--all` 不一定报错。
- 容易误以为全量校验通过。

证据：

- `/Users/a58/qa-agent/scripts/validate-artifacts.py:428-447`

建议：

- 增加一个 `--strict-all`。
- 根据 `pipeline.yaml` 检查当前应该存在的产物是否都存在。

---

## 24. PRD Gate 的产品文档里写死 Cursor 命令

产品打回/通过文档里，有些地方写的是 Cursor 命令：

```bash
./orchestrators/cursor/run-pipeline.sh --from-stage prd-analyze
```

但这个仓库支持 Cursor、Codex、Claude Code。

大白话解释：

> 三个平台都能用，但提示只告诉你开 Cursor。

影响：

- Codex 用户看到文档会困惑。
- Claude Code 用户也会困惑。

证据：

- `/Users/a58/qa-agent/scripts/render_prd_gate_notice.py:176`
- `/Users/a58/qa-agent/scripts/render_prd_gate_notice.py:213`

建议：

- 根据当前 platform 渲染对应命令。
- 或写成通用说明：`./orchestrators/<platform>/run-pipeline.sh --from-stage prd-analyze`。

---

## 25. Cursor 和 Python runner 的 gate 推进逻辑不对称

Cursor Hook 里专门写了 gate 子阶段顺序：

- product review
- dev review
- qa review
- red team
- gatekeeper

但 Python runner 在 Codex/Claude IDE-chain 下，不会同样自动一段一段推进。

大白话解释：

> Cursor 有一套详细的排班表；Codex 只拿到一句“你自己安排一下”。

影响：

- Cursor 能跑的流程，Codex 不一定能跑。
- 同一个项目在不同平台上行为不同。

证据：

- `/Users/a58/qa-agent/.cursor/hooks/qa-pipeline-next.sh:131-150`
- `/Users/a58/qa-agent/scripts/pipeline_runner.py:838-878`

建议：

- 把 gate 子阶段推进逻辑移入 Python runner。
- Hook 只负责触发，不负责决定流程。

---

## 26. 当前 workspace/artifacts 像是运行残留，不像稳定样例

当前 artifacts 里有：

- gate slices
- prompts
- logs
- meta
- precheck
- blueprint
- obligations

但没有完整后续产物，比如：

- `02-test-cases.md`
- `03-review-report.json`
- `04-execution-result.json`

同时 meta 又写了 completed。

大白话解释：

> 文件夹看起来像一次跑到一半的现场，但状态文件说已经结束。

影响：

- 新人不知道这些是样例，还是残留。
- 编排器可能误读这些旧产物。

证据：

- `/Users/a58/qa-agent/workspace/artifacts/00-meta.json:1-52`
- `/Users/a58/qa-agent/workspace/artifacts/`

建议：

- 把样例产物放到 `examples/` 或 `fixtures/`。
- `workspace/artifacts/` 只放当前运行产物。
- 启动新 run 前清楚说明是否清理旧产物。

---

## 27. 没有真正的单元测试和 CI

仓库里有一个 `scripts/test-subagents.sh`。

它是 smoke test，主要检查：

- 文件是否存在
- prompt 是否能生成
- 入口是否可执行

但没有系统化测试：

- 没有 pytest
- 没有 CI
- 没有状态机测试
- 没有 schema 反例测试

大白话解释：

> 现在只是检查“机器能不能开机”，还没检查“刹车、方向盘、安全气囊是否可靠”。

影响：

- 改 runner 很容易改坏。
- gate reject/pass 这种关键逻辑没有自动防回归。

证据：

- `/Users/a58/qa-agent/scripts/test-subagents.sh:1-3`
- `/Users/a58/qa-agent/scripts/test-subagents.sh:67-74`
- `/Users/a58/qa-agent/scripts/test-subagents.sh:145-155`
- 当前没有 `tests/` 或 `.github/` 测试文件。

建议：

- 增加 pytest。
- 增加 CI。
- 至少覆盖：
  - force 续跑
  - gate reject
  - gate pass
  - case-review retry
  - sync-skills 一致性
  - validate-artifacts 负例

---

## 28. `scripts/test-subagents.sh` 自己也会写入运行目录

这个 smoke test 会生成 prompt，也可能初始化或改动 meta。

大白话解释：

> 测试工具不是纯检查，它也会动现场。

影响：

- 不适合当只读 CI。
- 可能污染真实运行产物。

证据：

- `/Users/a58/qa-agent/scripts/test-subagents.sh:67-74`
- `/Users/a58/qa-agent/scripts/test-subagents.sh:91-100`
- `/Users/a58/qa-agent/scripts/test-subagents.sh:145-155`

建议：

- 测试应使用临时目录。
- 不要直接写真实 `workspace/artifacts/`。

---

## 29. 文档对默认行为描述太理想化

文档多次说：

> 默认 IDE 模式，自动启动子 Agent。

但 Codex / Claude Code 实际没有 Cursor 那样的自动 Hook。

大白话解释：

> 说明书说“按一下按钮机器自己跑完”，但其中两个平台其实需要人工接力。

影响：

- 用户预期和实际体验不一致。
- 主 Agent 容易被迫“解释下一步怎么做”。

证据：

- `/Users/a58/qa-agent/README.md:49`
- `/Users/a58/qa-agent/AGENTS.md:43-45`
- `/Users/a58/qa-agent/agents/qa-orchestrator.md:36-39`

建议：

- 文档里明确区分：
  - Cursor：Hook 自动推进
  - Codex：半自动推进，除非接入子 Agent 机制
  - Claude Code：半自动推进，除非接入子 Agent 机制

---

## 30. 主 Agent 和子 Agent 的边界写得清楚，但技术上防不住

文档反复说：

- 主 Agent 不要代写阶段产物
- 子 Agent 才能写蓝图、gate report 等

但技术上主要靠 prompt 约束。

虽然 `delivery_coverage.executed_by` 要求是 `prd-analyzer-subagent`，但这仍然是模型自己写的字段。

大白话解释：

> 规章制度写得很清楚，但门口没有门禁卡，全靠大家自觉。

影响：

- 主会话如果误写产物，系统不一定能真正识别。
- `executed_by` 字段可以被伪造。

证据：

- `/Users/a58/qa-agent/agents/qa-orchestrator.md:61-65`
- `/Users/a58/qa-agent/agents/prd-analyzer.md:12-17`
- `/Users/a58/qa-agent/contracts/test-ready-blueprint.schema.json:176-189`
- `/Users/a58/qa-agent/scripts/validate_test_ready_blueprint.py:99-103`

建议：

- 增加运行元信息，比如 launcher 写入 stage execution token。
- 校验产物时检查 token 或 run id。
- 至少记录每个阶段产物由哪个 launcher 创建。

---

## 31. 输入路径校验不够严格

当前主要检查文件是否存在。

但没有更强的路径安全检查，比如：

- 用户提供的 PRD 路径是否越界
- Figma URL 是否可信
- env.json 中是否包含敏感字段

大白话解释：

> 只检查“有没有这个文件”，没检查“这个文件是不是该读的文件”。

影响：

- 如果以后支持用户自定义路径，可能有路径穿越风险。
- env.json 可能放入敏感环境信息。

证据：

- `/Users/a58/qa-agent/scripts/pipeline_runner.py:358-366`
- `/Users/a58/qa-agent/workspace/inputs/env.json.example:1-5`
- `/Users/a58/qa-agent/pipeline.yaml:21-25`

建议：

- 所有输入路径限制在 `workspace/inputs/`。
- env.json 明确禁止写 token/password，或做脱敏。

---

## 32. `QA_AGENT_YOLO=1` 风险说明不够具体

README 写了：

```bash
export QA_AGENT_YOLO=1
```

并说慎用。

但代码实际会传：

- Codex：`--dangerously-bypass-approvals-and-sandbox`
- Claude：`--allow-dangerously-skip-permissions`

大白话解释：

> README 只是说“开快车请小心”，但实际是“关闭安全带和刹车辅助”。

影响：

- Agent 可以跳过确认和沙箱。
- 如果 prompt 或输入有问题，风险会放大。

证据：

- `/Users/a58/qa-agent/README.md:121-125`
- `/Users/a58/qa-agent/scripts/launch_subagent.py:77-88`

建议：

- README 明确写风险。
- 默认禁止在非隔离环境使用。
- 最好要求二次确认，或只允许维护者模式使用。

---

## 33. `.gitignore` 忽略了运行产物，但当前目录不是 git 仓库

`.gitignore` 设计上忽略了：

- workspace artifacts
- 用户输入
- env.json
- skill 副本
- logs

这是合理的。

但当前目录不是 git repo，所以这些规则当前没有实际保护作用。

大白话解释：

> 写了“不要把钥匙带出门”的纸条，但这间房子现在还没接入门禁系统。

影响：

- 如果以后初始化 git 或复制目录，仍需确认这些文件不会被提交。

证据：

- `/Users/a58/qa-agent/.gitignore:1-25`
- 执行 `git status` 显示当前不是 git repository。

建议：

- 如果这是项目源码仓库，应初始化或确认 git 根目录。
- 确保运行产物不会进入版本控制。

---

## 34. `workspace/artifacts/logs/` 排障信息有用，但缺少统一格式

日志能看到平台和阶段，例如：

```text
cursor-prd-analyze.log
cursor-prd-gate.log
```

但没有统一的结构化摘要。

大白话解释：

> 日志很多，但像聊天记录，不像一张清晰的故障单。

影响：

- 子 Agent 失败后，主 Agent 需要人工翻大量日志。
- 很难自动判断失败原因。

证据：

- `/Users/a58/qa-agent/scripts/launch_subagent.py:125-160`
- `/Users/a58/qa-agent/workspace/artifacts/logs/`

建议：

- 每个阶段额外写一个结构化 summary：
  - stage
  - platform
  - exit_code
  - artifact_found
  - validation_result
  - error_summary

---

## 35. case-review 的 pass 判断只看 verdict 和 coverage_score

runner 里 review 是否通过的判断是：

```python
verdict == "pass" and coverage_score >= threshold
```

但 case-review report 里还可能有 gaps、duplicate_cases 等字段。

大白话解释：

> 只看总分和“通过”两个字，不看老师有没有写“这里有严重问题”。

影响：

- 如果 report 写了 pass，但 gaps 非空，仍可能继续。

证据：

- `/Users/a58/qa-agent/scripts/pipeline_runner.py:369-376`
- `/Users/a58/qa-agent/contracts/review-report.schema.json:6-24`

建议：

- pass 时强制 `gaps=[]`。
- pass 时强制 `duplicate_cases=[]` 或无严重重复。

---

## 36. `validate_test_cases_md` 对 Markdown 的检查比较粗

它主要检查：

- 有没有编号表格
- 有没有 `#`
- 有没有 `###`
- 表格不是空的

真正的用例内容质量主要靠 fidelity 检查和 case-review。

大白话解释：

> 只检查文档长得像测试用例，不保证每条测试真的能执行。

影响：

- Markdown 格式可能过关，但步骤/预期质量不一定好。

证据：

- `/Users/a58/qa-agent/scripts/validate-artifacts.py:70-84`

建议：

- 检查每行是否有完整列。
- 检查步骤和预期不能为空。
- 检查每个 SC 是否出现一次且仅一次。

---

## 37. `prd-analysis.schema.json` 比 blueprint 弱很多

`01-prd-analysis.json` 是从 blueprint 同步出来的。

但它自己的 schema 比 blueprint 宽松，并且允许 additionalProperties。

大白话解释：

> 真正严格的是蓝图，分析 JSON 更像摘要，不能当成强校验依据。

影响：

- 如果只看 `01-prd-analysis.json`，很容易漏掉质量问题。

证据：

- `/Users/a58/qa-agent/contracts/prd-analysis.schema.json:6-10`
- `/Users/a58/qa-agent/contracts/prd-analysis.schema.json:89`
- `/Users/a58/qa-agent/scripts/sync_blueprint_to_analysis.py:17-43`

建议：

- 明确 `01-prd-analysis.json` 只是兼容产物。
- Gate 主要依据应该是 `00-test-ready-blueprint.json` 和 TOG。

---

## 38. Gate findings schema 太宽松

`gate-review-findings.schema.json` 要求每个 finding 只有：

- check_id
- verdict
- note

其他关键字段如 root cause、audience、obligation_ids 都不是必填。

大白话解释：

> 评审只要写“我发现了点东西”就能过格式，没强制说明是谁的问题、该谁修。

影响：

- gatekeeper 后续归因压力大。
- findings 质量不稳定。

证据：

- `/Users/a58/qa-agent/contracts/gate-review-findings.schema.json:6-20`
- `/Users/a58/qa-agent/contracts/gate-review-findings.schema.json:31-37`

建议：

- 当 finding verdict 为 fail 时，强制要求：
  - root_cause_draft
  - audience_draft
  - suggestion_draft
  - 至少一个 obligation_id / scenario_id / prd_section

---

## 39. product copy 有旧项目 fallback，可能污染新项目

`gate_product_copy.py` 里有大量写死的 `GATE-001`、`GATE-002` 文案，内容是某个 HP Feed 价格项目。

大白话解释：

> 如果 gatekeeper 没写产品文案，系统可能拿旧项目的话术来补。

影响：

- 新项目打回文档可能出现不相关内容。
- 产品会被错误信息误导。

证据：

- `/Users/a58/qa-agent/scripts/gate_product_copy.py:34-169`
- `/Users/a58/qa-agent/scripts/gate_product_copy.py:172-194`

建议：

- 删除项目特定 fallback。
- fallback 只做通用清洗，不写具体业务内容。
- 或把这些放到 example，不进入通用脚本。

---

## 40. 当前 artifacts 里的 precheck 已经显示有假覆盖

当前 `.test-point-coverage-precheck.json` 里：

```json
"ok": false,
"false_coverage_count": 6
```

这说明当前样例已经存在 6 个假覆盖。

大白话解释：

> 系统自己已经发现“有 6 道题声称考了知识点，但其实没考到”。

影响：

- 当前样例不应该被当作通过态。
- 如果 gate pass 不强制看这个字段，就会有风险。

证据：

- `/Users/a58/qa-agent/workspace/artifacts/.test-point-coverage-precheck.json:1-53`

建议：

- precheck `ok=false` 时，gate 不能 pass。
- 当前样例应标记为 rejected/rework，而不是 completed。

---

## 建议修复路线

### 第一天先修

1. 修掉 `--from-stage prd-analyze` 默认 force 导致不认产物的问题。
2. 修掉 `prd-gate reject` 不能正常停线的问题。
3. 修掉 prompt 里 `Write to: `` ` 输出路径为空的问题。
4. 日志里不要记录 API Key。
5. gate pass 必须强制检查 `test_point_review` 和 `false_coverage_count`。

### 1 到 3 天内修

1. gate 四个子阶段完成后都要立刻 validate。
2. 清理或同步 `.agents/skills`。
3. 统一 `bug-list-write` 的定位。
4. 补强 `execution-result` 校验。
5. 补强 `script-convert` 校验。
6. 更新 README，去掉“Skill 还是占位”的旧说法。

### 1 到 2 周内修

1. 把 Cursor Hook 的流程判断移到 Python runner。
2. 做统一状态机，三平台共用。
3. 加 pytest 和 CI。
4. 把样例产物和运行产物分开。
5. 做日志脱敏和保留策略。
6. 给 Codex / Claude Code 明确补齐 IDE 链式推进方案。

---

## 最终大白话总结

这个项目最大的问题不是“缺功能”，而是：

> 很多规则写在文档里，看起来很严，但代码没有完全把它们变成硬门禁。

现在最优先要保证三件事：

1. **流水线真的能稳定跑下去。**
2. **gate reject 能正确停，gate pass 不能假通过。**
3. **Cursor / Codex / Claude Code 不要三套行为。**

只要先把这三件事修好，项目就会从“看起来像自动化”变成“真的能作为 QA 流水线使用”。

