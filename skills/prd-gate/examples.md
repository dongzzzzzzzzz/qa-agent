# prd-gate 输出示例

## pass（issues 为空）

```json
{
  "version": "1.0",
  "checked_at": "2026-06-01T12:00:00Z",
  "verdict": "pass",
  "summary": "PRD/Figma 与测试就绪蓝图、分析产物一致，可进入用例生成。",
  "issues": [],
  "figma_accessible": true
}
```

前置条件：`00-test-ready-blueprint.json`、`01-prd-analysis.json` 已由 prd-analyze 产出。

## reject

```json
{
  "version": "1.0",
  "checked_at": "2026-06-01T12:00:00Z",
  "verdict": "reject",
  "summary": "PRD 未定义账号锁定规则，蓝图假设无法闭合。",
  "issues": [
    {
      "id": "GATE-001",
      "severity": "blocker",
      "category": "prd_functional",
      "description": "PRD 登录章节未说明连续失败次数与锁定时长。",
      "suggestion": "在 PRD 登录安全小节补充：失败 N 次锁定 M 分钟、解锁方式及错误文案。"
    }
  ],
  "figma_accessible": true
}
```

产品修订后：`--from-stage prd-analyze` → 再跑 `prd-gate`。
