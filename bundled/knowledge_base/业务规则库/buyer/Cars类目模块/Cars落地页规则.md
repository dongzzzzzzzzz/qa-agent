# Cars 类目模块 - Cars 落地页业务规则

## 1. 功能概述

- **功能描述**: Cars 类目 SEO/导流落地页，聚合「按 Make/Model/价格/地区/关键词」结构化找车入口，并展示卖车 CTA、24 小时上新、Popular models、Browse by body type、Expert reviews、Browse by brands 等内容区块
- **用户角色**: 访客（未登录）为主；已登录用户体验一致，顶栏随登录态变化
- **入口位置**:
  - 首页热门分类「Cars & Vehicles」点击（含 UTM 参数，见首页规则）
  - 主导航「Cars & Vehicles」点击
  - 直接访问 URL：`https://www.unicorn.gumtree.io/cars-vans-motorbikes/cars`
- **依赖模块**: [首页模块](../首页模块/首页访问与浏览规则.md)（顶栏、全局导航）、搜索结果页（Search Cars 跳转目标）

## 2. 核心流程

### 2.1 主流程（结构化找车）

1. 访客打开 Cars 落地页，加载 Hero + 结构化搜索区
2. 可选：从 Make 下拉选择品牌 → 触发 Model 异步刷新 → 选择车型
3. 可选：设置 Price min/max 价格区间
4. 可选：填写 Location（城镇或邮编）
5. 可选：展开 More options → 填写 Keyword
6. 点击「Search Cars (N)」→ 跳转 SRP（URL 变化，不同于落地页）

### 2.2 辅助流程

- 点击「See all cars」→ 跳转全英车源搜索（含 `search_category=cars&search_location=uk`）
- 点击「Browse by body type」各车型卡片 → 进入对应类目筛选页
- 点击「Popular models」内链接 → 进入品牌/车型筛选页
- 点击「Learn more about how to sell your car」→ 跳转卖车介绍页（href 含 `sell-my-car`）
- 点击「Browse by brands」品牌 → 进入品牌筛选列表

### 2.3 异常流程

- Make 已选但对应 Make 下无 Model 数据 → Model 下拉无可选项，用户可跳过 Model 直接搜索
- Price min > Price max → 前端显示校验提示，但仍允许提交并跳转 SRP（URL 含 `search_category=cars&search_location=united+kingdom`）✅ 已实测（CARS-TC023）
- Keyword 含特殊字符（`<>&"'`）→ 自动化 selector 解析失败（script bug），实际产品行为尚未验证 ⚠️
- 首次访问 Cookie 横幅遮挡 → 点击 Accept all 后可正常操作搜索区

## 3. 业务规则

### 3.1 输入规则


| 字段        | 选择器                                 | 类型   | 必填  | 说明                                           |
| --------- | ----------------------------------- | ---- | --- | -------------------------------------------- |
| Make      | `#select-make`                      | 下拉选择 | 否   | 汽车品牌；初始值为占位（`INITIAL_VALUE`）；有数据时 option > 1 |
| Model     | `#select-model`                     | 下拉选择 | 否   | 依赖 Make 异步刷新；若 Make 下无数据则无可选项                |
| Price min | `#select-price-min`                 | 下拉选择 | 否   | 最低价格区间                                       |
| Price max | `#select-price-max`                 | 下拉选择 | 否   | 最高价格区间                                       |
| Location  | `[data-qa="search-location-field"]` | 文本输入 | 否   | placeholder：「Postcode or location」           |
| Keyword   | `#keyword-field-value`              | 文本输入 | 否   | 在 More options 展开后可见                         |


### 3.2 校验规则

- Make/Model/Price/Location 均为可选，可直接点击「Search Cars」不填任何筛选
- 选择有效 Make 后，Model 异步刷新；若该 Make 下无 Model 数据，Model 下拉保持无有效选项（测试需 skip/重试）
- Price min > Price max 时：前端显示校验提示，但仍允许跳转 SRP（已实测 PASS，CARS-TC023）

### 3.3 权限规则


| 角色    | 操作                                                    | 行为                              |
| ----- | ----------------------------------------------------- | ------------------------------- |
| 未登录访客 | 使用结构化搜索并进入 SRP                                        | ✅ 无需登录，完全可用                     |
| 未登录访客 | 查看顶栏                                                  | Post an ad、Sign up、Login（与首页一致） |
| 已登录用户 | 查看顶栏                                                  | Post an ad、Messages、Menu（与首页一致） |
| 所有用户  | 浏览内容区块（Popular models / Body type / Reviews / Brands） | 无需登录                            |


### 3.4 业务约束

**页面标识信息**：

- URL 路径：`/cars-vans-motorbikes/cars`
- 完整 URL：`https://www.unicorn.gumtree.io/cars-vans-motorbikes/cars`
- 浏览器标题：`Used Cars for Sale Across the UK | Gumtree`

**Hero 区规则**：

- 主标题：`Find Cars for Sale`（heading 或显著文本节点，H1 级别）
- 副标题（响应式二选一）：
  - 完整版：`Search thousands of ads on the UK's local motors marketplace`
  - 简短版：`The UK's local motors marketplace`

**Search Cars 按钮规则**：

- 文案格式：`Search Cars (N)`，N 为动态列表条数（含千位分隔符，如 `6,058`）
- 按钮始终 enabled（不含 disabled 状态）
- 点击后跳转 SRP，跳转 URL 与落地页 URL 不同（含 `/search` 或 `/s-cars` 或 `cars-vans` 等路径）

**See all cars 跳转规则**：

- 目标 URL 必须包含 `search_category=cars` 和 `search_location=uk` 两个参数

**Browse by body type 规则**：

- 显示车型：Hatchback、Saloon、Estate、MPV、Coupe、Convertible
- 每个车型卡片：含车型名称链接 + SVG 图标
- 链接 href 含 `/cars-vans-motorbikes/cars/`（站内类目链接）

**卖车 CTA 区块规则**：

- 标题：`Have a car to sell, why not sell it with Gumtree?`
- CTA 链接文案：`Learn more about how to sell your car`
- 链接 href 包含 `sell-my-car`

**24 小时上新区块规则**：

- 标题格式：`N new listings added in the past 24 hours`（N 为数字，可含逗号）
- 区块内至少 1 条广告链接（`a[href*='/p/']`）

**内容区块标题**（按页面顺序）：

1. `Popular models` — 站内链接，格式：`/cars-vans-motorbikes/cars/{brand}/{model}` ✅ 已实测（CARS-TC026）
2. `Browse by body type`
3. `Read our latest expert car reviews and articles` — 外链，跳转至 `https://www.gumtree.com/info/cars/reviews-hub/` ✅ 已实测（CARS-TC027）
4. `Browse by brands` — 站内链接，格式：`/cars-vans-motorbikes/cars/{brand}?distance=50` ✅ 已实测（CARS-TC028）

**Cookie 横幅规则**：

- 首次访问（无 Cookie）可能出现 OneTrust 横幅
- 点击 Accept all 后，Search Cars / Location 等搜索元素不被遮罩拦截
- 自动化测试需封装 `close_privacy_dialogs` 处理

**顶栏规则**：

- 与全站首页顶栏一致，不另行定制
- 访客态：Post an ad / Sign up / Login
- 已登录态：Post an ad / Messages / Menu

### 3.5 站点特殊规则

#### Unicorn 站（UK 测试站）

- 落地页 URL：`https://www.unicorn.gumtree.io/cars-vans-motorbikes/cars`
- 24h 上新实测数量（2026-04-10）：63 条（随数据变化）
- Search Cars 实测数量（2026-04-10）：6,058（随数据变化）
- 自动化对齐：`test_cases/cars/test_cars_landing_page.py`（`GUMTREE_CARS_LP_001`–`018`）

## 4. 错误处理


| 错误场景                  | 触发条件                              | 实测行为                                                                                                                                             |
| --------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Make 下 Model 无数据      | 选择特定 Make 后 Model 无可选项            | Model 下拉保持无有效选项；自动化测试 skip 该 case                                                                                                                |
| Price min > Price max | 用户手动设置倒序价格区间（如 min=2000, max=500） | ✅ 已实测：前端显示校验提示，但仍允许跳转 SRP（CARS-TC023）                                                                                                            |
| Keyword 含特殊字符         | 输入 `<>&"'` 等字符                    | ⚠️ 自动化 selector 解析失败（`button:has-text('More options')` 语法错），实际产品行为未验证（CARS-TC022）                                                                |
| Cookie 横幅遮挡           | 首次访问无 Cookie                      | ✅ 已实测：接受后搜索区可正常操作（CARS-TC020）                                                                                                                    |
| SRP 后退回落地页            | 从 Search Cars 跳转 SRP 后点浏览器后退      | ❌ 新发现：实测 SRP URL 显示为 `/cars-vans-motorbikes/cars`（同落地页），后退实际跳至 `/search?search_category=cars&search_location=united+kingdom`，行为与预期不符（CARS-TC025） |


## 5. 已知问题

- **TC023**：~~Price min > Price max 时前端校验行为未实测~~ → ✅ 已实测（2026-04-16）：前端显示校验提示，但仍允许跳转 SRP
- **TC026**：~~Popular models 区块链接可用性为推断~~ → ✅ 已实测（2026-04-16）：链接有效，格式 `/cars-vans-motorbikes/cars/{brand}/{model}`（示例：vauxhall-motors/corsa）
- **TC027**：~~Expert reviews 跳转目标未实测~~ → ✅ 已实测（2026-04-16）：外链跳转至 `https://www.gumtree.com/info/cars/reviews-hub/`（非 unicorn 域）
- **TC028**：~~Browse by brands 跳转目标未实测~~ → ✅ 已实测（2026-04-16）：站内链接格式 `/cars-vans-motorbikes/cars/{brand}?distance=50`（示例：audi?distance=50）
- **TC022**：Keyword 特殊字符搜索行为 — 自动化 selector 语法错误导致脚本未运行，实际产品行为仍未验证；参考首页 HP-TC016（特殊字符搜索）实测 PASS，Cars LP 行为待人工/修正脚本补验 ⚠️
- **TC025**：SRP 后退行为异常 ❌ 新发现 — 实测 SRP URL 与落地页相同（`/cars-vans-motorbikes/cars`），后退跳至 `/search?...` 而非落地页，与预期 SRP→LP 导航路径不符，需产品确认设计意图 ⚠️
- **TC030**：已登录态顶栏验证失败 — LOGIN-SETUP 登录 step 超时，无法验证已登录 Cars LP 顶栏；待登录流程自动化修复后重测 ⚠️
- **TC033**：首屏可见时间性能 SLA 无基线，暂不可自动化 ⚠️

## 6. 变更历史


| 日期         | 版本   | 变更内容                                                                         | 变更人       |
| ---------- | ---- | ---------------------------------------------------------------------------- | --------- |
| 2026-04-16 | v1.0 | 初始版本，基于 unicorn-cars-landing-测试用例-20260410.md（34条用例）归档                       | Arin Yang |
| 2026-04-16 | v1.1 | 根据实测结果更新：TC023/TC026/TC027/TC028 已验证，新增 TC025 SRP 后退异常、TC030 待重测、TC022 脚本待修复 | Arin Yang |


