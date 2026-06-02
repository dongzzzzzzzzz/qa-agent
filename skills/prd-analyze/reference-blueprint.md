# 测试就绪蓝图字段

## 目标

在尚无 `02-test-cases.md` 时，先设计 **测试义务** `O-xxx`（见 reference-obligations.md），再设计 `scenarios[]`，每条场景必填 `covers_obligations`。不清楚之处写入 `assumptions[]` 并附 `test_rule`。analyze 阶段场景标题/步骤中，不要写「请产品确认」类措辞（应进 assumptions 或留给 gate）。

## 工作顺序

1. 结构：`modules`、`roles`、`main_flows`、`api_endpoints`、`field_rules`、`figma_mapping`、`risks`
2. `resolutions[]`：PRD 与 Figma 冲突的决议
3. `assumptions[]`：未闭合项 + 仍如何测试
4. `scenarios[]`：主路径、数据、状态、组合、时序
5. `coverage_matrix`：P0 模块须 functional/boundary/exception 均为 true
6. `delivery_coverage`：阅读证明 + 清单

`blocking_gaps` 必须保持 `[]`。未闭合缺口在 analyze 之后由 gate 记 issue，不要写进该字段。

## 场景字段

| 字段 | 说明 |
|------|------|
| `id` | `SC-001` … 递增 |
| `source` | `prd` / `figma` / `assumption` |
| `assumption_id` | `source=assumption` 时必填 |
| `type` | 功能 / 边界 / 异常 / 安全 / 兼容 / 性能 |
| `covers_obligations` | `["O-001", ...]` 必填（P0/P1） |
| `prd_section` 或 `figma_ref` | 追溯必填 |

## 脚本

```bash
python3 scripts/validate-artifacts.py --stage test-ready-blueprint
python3 scripts/sync_blueprint_to_analysis.py
python3 scripts/validate-artifacts.py --stage prd-analyze
python3 scripts/render_test_ready_internal.py
```
