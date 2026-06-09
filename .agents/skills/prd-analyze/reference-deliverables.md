# PRD + Figma 理解清单（分析阶段）

> prd-analyzer 阅读 `prd.md` / Figma 时对照。用于产出蓝图前的交付物理解，**不**在此阶段打回产品。

## A. PRD 单文档

- 元信息：项目背景、目标、非目标、版本、发布时间、负责人、变更记录。
- 范围：in-scope/out-of-scope、平台、地区、用户角色、入口、上下游依赖。
- 主流程：用户触发、系统处理、页面/状态变化、成功结果。
- 分支流程：边界、异常、取消、回滚、重复操作、并发、超时、重试。
- 业务规则：权限、状态机、频控、额度、校验、优先级、排序、推荐、匹配、计费等。
- 数据规则：字段含义、来源、取值范围、默认值、空值、非法值、格式、单位、精度、兼容规则。
- 非功能：性能、稳定性、安全、隐私、可访问性、兼容性、可观测性；若写入 PRD，必须有可验收口径。
- 运营与评估：实验/灰度、埋点、报表、指标、上线/回滚条件；若作为验收依据，必须定义统计口径。

## B. Figma 单稿

- 详见 [reference-figma-analysis.md](reference-figma-analysis.md)：MCP 顺序、五层分析、`frames_inventory` 扩展字段

## C. PRD × Figma 对齐

- 详见 [reference-prd-figma-alignment.md](reference-prd-figma-alignment.md)：四色差距 → `resolutions[]` / gate `issues[]`

## D. 可测试性输入

- 核心能力可拆为可验证场景，每个 P0/P1 规则至少有一个可观察结果。
- 不可测项不直接伪造成 pass 场景；灰区进 `assumptions[]`，高风险灰区同时进 `risks` 或 `contradiction_candidate`。
- 方向性描述必须落成可判断标准，例如范围、阈值、样本、环境、时间窗口、统计口径。
- 每个需求验证点都能追溯到 PRD 段落、Figma frame 或明确 assumption。

这份清单用于 `prd-analyze` 阶段生成测试蓝图，不在本阶段打回产品；是否阻断由 `case-review` 统一裁决。
