# 测试义务图谱（TOG）

在写 `scenarios[]` 之前或同时，从 PRD/Figma 抽取 **可判定验收义务** `O-xxx`。

## 产出

- `workspace/artifacts/00-test-obligations.json`（契约：`contracts/test-obligations.schema.json`）
- 每条 `scenarios[]` 必填 `covers_obligations: ["O-001", ...]`

## 义务字段

| 字段 | 要求 |
|------|------|
| `statement` | 业务语言描述 |
| `predicate` | **可验证断言**（步骤/预期能检验的命题） |
| `kind` | `rule` / `state_transition` / `combination` / `nfr` / `contradiction_candidate` |
| `risk` | P0/P1/P2 |
| `source` | prd / figma / assumption |

## 抽取策略

1. **规则**：PRD 明文业务规则 → 每条 1 个 O
2. **状态机**：AI 匹配、报告刷新等 → `state_machines[]` + 每边 1 个 O（`state_transition`）
3. **组合**：筛选多因子 → 关键二元组 `combination`（不必全笛卡尔积）
4. **矛盾候选**：PRD 两处冲突 → `contradiction_candidate`（gate 产品视角会审）

## 与场景映射

- 每个 P0 义务至少 1 条 SC 覆盖
- 一条 SC 可覆盖多个 O
- 完成后：`python3 scripts/sync_obligation_coverage.py --write`

## 校验

```bash
python3 scripts/validate-artifacts.py --stage test-obligations
python3 scripts/validate-artifacts.py --stage test-ready-blueprint
```
