---
name: script-convert
description: >-
  将为 pass 且可自动化的用例转换为自动化测试脚本。在 post-process 的
  script-convert 分支由 script-converter 子 Agent 调用。
---

# 脚本转换 Skill

## 何时使用

- post-process 分支，条件：`04-execution-result.json` 中 `has_pass=true`
- 或存在 `automatable: true` 且 `status=pass` 的用例

## 步骤

1. 读取 `04-execution-result.json`，筛选可自动化且通过的 `case_id`。
2. 从 `02-test-cases.md` 取对应用例步骤与断言。
3. 生成脚本至 `workspace/artifacts/05a-scripts/`：
   - Web 默认 Playwright（`.spec.ts`）
   - 移动端默认 Appium/WebDriver（按 env 配置）
4. 可选生成 `05a-scripts/manifest.json`（framework、scripts 列表）。
5. 脚本应含：用例 ID 注释、 arrange/act/assert 结构、与 evidence 路径无关的可重复执行逻辑。

## 后续扩展

- 复用已有 Page Object
- 参数化环境与测试数据
