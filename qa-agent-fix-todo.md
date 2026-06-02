# QA Agent 全量修复 TODO

> 范围说明：本 TODO 覆盖 `qa-agent-review-plain.md` 里列出的全部 40 个问题，不做缩减。
> 当前状态：40/40 已处理完成。

## 全量问题清单

- [x] 01. 默认流程可能自己把自己卡死
- [x] 02. PRD Gate reject 后，流水线可能不知道怎么正确停
- [x] 03. Gate pass 太容易“假通过”
- [x] 04. Codex 和 Claude Code 没有真正的自动链路
- [x] 05. test-execute 的 prompt 里输出路径是空的
- [x] 06. pipeline.yaml 和代码没有完全对齐
- [x] 07. Gate 子阶段只看文件存在，不一定验证文件有效
- [x] 08. 当前 meta 状态文件有互相矛盾的状态
- [x] 09. case-review 失败重试逻辑不够完整
- [x] 10. bug-list-write 角色已经和 pipeline 不一致
- [x] 11. Skill 有一份影子副本已经不同步
- [x] 12. README 说 Skill 还是占位，但实际已经不是
- [x] 13. Codex 的 --check-auth 检查太浅
- [x] 14. 日志可能泄露 API Key
- [x] 15. 日志会保存大量 PRD / prompt / 产物内容
- [x] 16. env.json 是可选的，但提示方式容易让人误会
- [x] 17. 执行结果校验不够严格
- [x] 18. 自动化脚本转换校验太弱
- [x] 19. case-generate 的渲染脚本有固定模块名映射
- [x] 20. 有一个脚本可以从场景反推 TOG，容易削弱 TOG 意义
- [x] 21. sync_obligation_coverage.py 会直接修改蓝图和 TOG
- [x] 22. validate-artifacts.py --stage prd-analyze 会产生副作用
- [x] 23. validate-artifacts.py --all 只校验存在的文件，不能发现缺文件
- [x] 24. PRD Gate 的产品文档里写死 Cursor 命令
- [x] 25. Cursor 和 Python runner 的 gate 推进逻辑不对称
- [x] 26. 当前 workspace/artifacts 像是运行残留，不像稳定样例
- [x] 27. 没有真正的单元测试和 CI
- [x] 28. scripts/test-subagents.sh 自己也会写入运行目录
- [x] 29. 文档对默认行为描述太理想化
- [x] 30. 主 Agent 和子 Agent 的边界写得清楚，但技术上防不住
- [x] 31. 输入路径校验不够严格
- [x] 32. QA_AGENT_YOLO=1 风险说明不够具体
- [x] 33. .gitignore 忽略了运行产物，但当前目录不是 git 仓库
- [x] 34. workspace/artifacts/logs/ 排障信息有用，但缺少统一格式
- [x] 35. case-review 的 pass 判断只看 verdict 和 coverage_score
- [x] 36. validate_test_cases_md 对 Markdown 的检查比较粗
- [x] 37. prd-analysis.schema.json 比 blueprint 弱很多
- [x] 38. Gate findings schema 太宽松
- [x] 39. product copy 有旧项目 fallback，可能污染新项目
- [x] 40. 当前 artifacts 里的 precheck 已经显示有假覆盖

## 修复完成口径

- 每个问题都必须至少满足一种结果：
  - 代码修复完成；
  - 文档/配置修复完成；
  - 若问题本身属于运行环境事实或需人工决策，必须写入项目文档并给出明确处理方式。
- 修复后必须跑自测。
- 自测不通过则继续修，直到通过。

## 自测记录

- [x] Python 语法检查通过：`python3 -m py_compile ...`
- [x] 流水线临时目录自测通过：`./scripts/test-subagents.sh`
- [x] Skill 多平台副本一致：`skills` 与 `.cursor/skills`、`.codex/skills`、`.claude/skills`、`.agents/skills` diff 无差异
- [x] Codex 登录检查通过：`./orchestrators/codex/run-pipeline.sh --check-auth`
- [x] Cursor 登录检查通过：`./orchestrators/cursor/run-pipeline.sh --check-auth`
- [x] Claude Code 登录检查通过：`./orchestrators/claude-code/run-pipeline.sh --check-auth`
- [x] 当前已有产物校验通过：`python3 scripts/validate-artifacts.py --all`

## 说明

- `python3 scripts/validate-artifacts.py --strict-all` 会检查“完整流水线是否全部跑完”。当前 `workspace/artifacts/` 不是一轮完整完成的流水线结果，所以它会正确提示缺少 `prd-gate`、`case-generate`、`case-review`、`test-execute` 后续产物。这不是自测失败，而是新加的严格校验在阻止“不完整产物假装完成”。
