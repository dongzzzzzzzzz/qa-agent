# Unicorn Gumtree - Cars 类目落地页 测试用例

> **业务逻辑**：见 [carsLandingPage.md](carsLandingPage.md)  
> **生成时间**: 2026-04-10  
> **探测方式**: ① **Cursor Playwright MCP**（2026-04-10）已对 Unicorn Cars LP 执行 `browser_navigate` + `browser_snapshot`，证明存档见 [unicorn-cars-landing-MCP证明存档.md](unicorn-cars-landing-MCP证明存档.md)；② 仓库 Playwright 自动化（`test_cases/cars/test_cars_landing_page.py`）与 Page Object 对齐。  
> **测试范围**: `https://www.unicorn.gumtree.io/cars-vans-motorbikes/cars` — Cars 类目落地页（Hero、结构化搜索、卖车导流、24h 上新、内容区块、Body type 等）  
> **总用例数**: 34 条  
> **可自动化**: 33 条（约 97%）  

---

## MCP 证明存档（enforcement-gates 格式）

| 项 | 路径 |
|----|------|
| **MCP 证明存档正文**（含真实 `Ran Playwright code`、`ref` 列表） | [unicorn-cars-landing-MCP证明存档.md](unicorn-cars-landing-MCP证明存档.md) |
| **MCP 完整快照 YAML（提交仓库）** | [_proof_archives/unicorn-cars-landing-mcp-snapshot-20260410.yml](_proof_archives/unicorn-cars-landing-mcp-snapshot-20260410.yml) |
| **本地回退：无障碍 JSON**（MCP 不可用时） | [_proof_archives/unicorn-cars-landing-a11y.json](_proof_archives/unicorn-cars-landing-a11y.json) |
| **MCP 故障排查与本地再生** | [mcp-playwright-troubleshooting.md](mcp-playwright-troubleshooting.md) |
| **本地回退脚本**（默认输出 `unicorn-cars-landing-本地回退证明存档.md`，不覆盖 MCP 主存档） | `./venv/bin/python scripts/unicorn_cars_mcp_proof_archive.py` |

**MCP 实测摘录（2026-04-10）**：标题 **Used Cars for Sale Across the UK \| Gumtree**；Hero **Find Cars for Sale**；**Search Cars (6,058)**（数量随数据变化）；**63 new listings added in the past 24 hours**；顶栏 **Post an ad、Sign up、Login**。

---

## 测试环境配置（必填）


| 字段       | 值                                                                                                                    | 说明                              |
| -------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| 站点       | unicorn                                                                                                              | UK 测试环境                         |
| 基础URL    | [https://www.unicorn.gumtree.io](https://www.unicorn.gumtree.io)                                                     | 主站根                             |
| 目标路径     | /cars-vans-motorbikes/cars                                                                                           | Cars 类目落地页完整 URL 见下             |
| 完整目标 URL | [https://www.unicorn.gumtree.io/cars-vans-motorbikes/cars](https://www.unicorn.gumtree.io/cars-vans-motorbikes/cars) | 被测页面                            |
| 站点名称     | Unicorn / Gumtree UK                                                                                                 | 可选                              |
| 角色       | buyer                                                                                                                | 浏览/搜车为主；发帖见全局规则                 |
| 账号名称     | arin_yang_unicorn_cars                                                                                               | session 命名建议                    |
| 测试账号     | [arin.yang@gumtree.com](mailto:arin.yang@gumtree.com)                                                                | 用户提供                            |
| 测试密码     | （用户本地保管，勿写入仓库）                                                                                                       | 落地页主路径通常 **无需登录**；登录用于交叉验证顶栏/会话 |


**说明**：结构化文案与选择器以仓库自动化为准；若 Unicorn 数据延迟导致 Make/Model 选项为空，部分用例需重试或跳过（与 `test_make_select` / `test_model_select` 一致）。

---

## Application Overview（阶段一）

**功能定位**：Cars 类目 **SEO/导流落地页**，聚合「按 Make/Model/价格/地区/关键词」结构化找车入口，并展示卖车 CTA、24 小时上新、Popular models、Body type、评测与品牌等内容块。

**用户角色**：未登录即可使用主流程（与主站一致）；顶栏行为同全局首页（访客见 Login，已登录见 Messages/Menu）。

**业务规则（自自动化与 UI 推断）**：

- Hero 主标题 **Find Cars for Sale**，副标题为「Search thousands of ads…」或 **The UK's local motors marketplace**（响应式二选一）。
- 结构化搜索含 **Make**（`#select-make`）、**Model**（`#select-model`）、**Price min/max**、**Location**（`data-qa="search-location-field"`）、**More options → Keyword**（`#keyword-field-value`）。
- 主按钮 **Search Cars (N)** 中 **N** 为列表条数样式，点击跳转 SRP/类目结果 URL。
- **See all cars** 跳转搜索 URL，含 `search_category=cars`、`search_location=uk`（✅ 自动化断言）。
- **Browse by body type** 下 Hatchback、Saloon 等为站内类目链接，且含 SVG 图标。

**页面状态**：默认有数据；Make 选后 Model 异步刷新；极端数据不足时 Model 可能无可选项。

**模块划分 [P0]**：Hero、结构化搜索、Search Cars 跳转、Make/Model 选择。  
**[P1]**：Location、More options/Keyword、卖车区块、24h 上新、See all cars、内容区块、Body type、Recently listed。  
**[P2]**：Cookie 首访、边界输入。

---

## 测试用例

### 核心流程（正向）

#### TC001: 页面标题与 URL 为 Cars 类目落地页

#### 📋 前置条件

- 可访问 Unicorn 网络

#### 🎬 执行步骤

1. 打开 `https://www.unicorn.gumtree.io/cars-vans-motorbikes/cars`

#### ✅ 预期结果

- 地址栏路径包含 `cars-vans-motorbikes/cars` ✅ 实测（自动化导航）
- 浏览器标题为 Gumtree 车辆相关英文标题（含 Cars / UK 等）✅ 实测（模板）

#### 📊 用例属性

- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC002: Hero 主标题展示 Find Cars for Sale

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 查看首屏 Hero 主标题（heading 或等价文本节点）

#### ✅ 预期结果

- 可见 **「Find Cars for Sale」**（不区分大小写）✅ 实测（`GUMTREE_CARS_LP_001`）

#### 📊 用例属性

- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC003: Hero 副标题为 motors marketplace 两类文案之一

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 查看 Hero 副文案

#### ✅ 预期结果

- 可见 **「Search thousands of ads on the UK's local motors marketplace」** 或 **「The UK's local motors marketplace」** 之一（视断点/响应式）✅ 实测（`GUMTREE_CARS_LP_002`）

#### 📊 用例属性

- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC004: 结构化搜索 — Make / Model 标签与下拉可见

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 查看 Make、Model 区域

#### ✅ 预期结果

- 可见文案 **Make**、**Model** ✅ 实测（`GUMTREE_CARS_LP_003`）
- 存在 `#select-make`、`#select-model` 且可见 ✅ 实测

#### 📊 用例属性

- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC005: Search Cars 按钮展示列表数量 Search Cars (N)

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 查看主搜索按钮文案

#### ✅ 预期结果

- 按钮匹配 **Search Cars (数字)**，数字可含千位分隔 ✅ 实测（`GUMTREE_CARS_LP_004`）

#### 📊 用例属性

- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC006: Location 占位与 data-qa 搜索地址框

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 查看 Location 输入

#### ✅ 预期结果

- 占位符匹配 **Postcode or location**（不区分大小写）✅ 实测（`GUMTREE_CARS_LP_005`）
- 存在 `[data-qa="search-location-field"]` 且已挂载 ✅ 实测

#### 📊 用例属性

- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC007: More options 展开后显示 Keyword 与输入框

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 点击 **More options**
2. 查看 Keyword 区域

#### ✅ 预期结果

- 可见 **Keyword** 文案 ✅ 实测（`GUMTREE_CARS_LP_006`）
- 存在可见的 `#keyword-field-value` ✅ 实测

#### 📊 用例属性

- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC008: 卖车区块标题与 Learn more 链接指向卖车介绍

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 滚动至卖车推广区块
2. 查看 **Learn more about how to sell your car** 链接 href

#### ✅ 预期结果

- 可见 **「Have a car to sell, why not sell it with Gumtree?」** ✅ 实测（`GUMTREE_CARS_LP_007`）
- **Learn more** 链接 href 包含 **sell-my-car** ✅ 实测

#### 📊 用例属性

- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC009: 24 小时内上新统计标题

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 滚动至「past 24 hours」统计区域

#### ✅ 预期结果

- 可见形如 **「N new listings added in the past 24 hours」** 的标题（N 为数字，可含逗号）✅ 实测（`GUMTREE_CARS_LP_008`）

#### 📊 用例属性

- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC010: See all cars 跳转全英车源搜索 URL 参数

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 点击 **See all cars**

#### ✅ 预期结果

- 跳转后 URL 含 **search_category=cars** 与 **search_location=uk** ✅ 实测（`GUMTREE_CARS_LP_009`）

#### 📊 用例属性

- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC011: 内容区块标题 — Popular models / Body type / 评测 / Brands

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 依次滚动并查看各内容区块标题

#### ✅ 预期结果

- 可见 **Popular models**、**Browse by body type**、**Read our latest expert car reviews and articles**、**Browse by brands** ✅ 实测（`GUMTREE_CARS_LP_010`）

#### 📊 用例属性

- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC012: 点击 Search Cars 离开落地页进入搜索结果类页面

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 点击 **Search Cars (N)**

#### ✅ 预期结果

- URL 变为搜索/类目结果形态（含 `/search` 或 `/s-cars` 或 `cars-vans` 等路径片段）且 **不同于** 落地页 URL ✅ 实测（`GUMTREE_CARS_LP_011`）

#### 📊 用例属性

- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### 表单与筛选（Make / Model / Price）

#### TC013: Make 下拉可选且能选中非占位项

#### 📋 前置条件

- Make 下拉已加载，option 数量 > 1

#### 🎬 执行步骤

1. 打开 `#select-make`
2. 选择第一个非占位选项（如 index=1）

#### ✅ 预期结果

- 选中后值 **不为** `INITIAL_VALUE` ✅ 实测（`GUMTREE_CARS_LP_012`）

#### 📊 用例属性

- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC014: 选择 Make 后 Model 下拉刷新并可选项

#### 📋 前置条件

- 已选择有效 Make

#### 🎬 执行步骤

1. 等待 Model 选项刷新
2. 若 option>1，选择第一项非占位 Model

#### ✅ 预期结果

- Model 选中后值 **不为** `INITIAL_VALUE`；若当前 Make 下无 Model 数据则跳过 ⚠️ 实测（`GUMTREE_CARS_LP_013`，含 skip 分支）

#### 📊 用例属性

- **优先级**: P0
- **测试类型**: 正向 / 异常流
- **UI自动化**: ✅ 可自动化

---

#### TC015: Price 最低价与最高价下拉存在且可选

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 查看 `#select-price-min`、`#select-price-max`
2. 若有多个 option，各选第二项

#### ✅ 预期结果

- 两个下拉均存在 option ✅ 实测（`GUMTREE_CARS_LP_014`）

#### 📊 用例属性

- **优先级**: P1
- **测试类型**: 正向 / 边界值
- **UI自动化**: ✅ 可自动化

---

#### TC016: Search Cars 按钮可点击且展示数量

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 检查 **Search Cars (N)** 可见、enabled

#### ✅ 预期结果

- 按钮 **enabled**，文案匹配 **Search Cars (数量)** ✅ 实测（`GUMTREE_CARS_LP_015`）

#### 📊 用例属性

- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### 列表与内容卡片

#### TC017: Browse by body type — 各车型链接、标题与 SVG

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 滚动至 **Browse by body type**
2. 检查 Hatchback、Saloon、Estate、MPV、Coupe、Convertible 链接

#### ✅ 预期结果

- 各名称链接可见，含 **svg**，href 含 `/cars-vans-motorbikes/cars/` ✅ 实测（`GUMTREE_CARS_LP_016`）

#### 📊 用例属性

- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC018: Location 输入框可点击并获得焦点

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 滚动至 Location 字段
2. 点击 `[data-qa="search-location-field"]`

#### ✅ 预期结果

- 元素可见；点击后 **focused** ✅ 实测（`GUMTREE_CARS_LP_017`）

#### 📊 用例属性

- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC019: Recently listed（24h 区块）内至少一条车源卡片链向详情

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 定位「new listings added in the past 24 hours」所在 `section`
2. 统计其中 `a[href*='/p/']`

#### ✅ 预期结果

- 至少 **1** 条广告链接 ✅ 实测（`GUMTREE_CARS_LP_018`）

#### 📊 用例属性

- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### Cookie / 合规与顶栏（交叉）

#### TC020: 首次访问可能出现 OneTrust，关闭后可操作搜索区

#### 📋 前置条件

- 新会话或清除站点 Cookie

#### 🎬 执行步骤

1. 打开 Cars 落地页
2. 若出现 Cookie 横幅，点击 **Accept all**（或项目封装的关闭逻辑）

#### ✅ 预期结果

- 同意后可点击 **Search Cars**、Location 等不被遮罩拦截 ✅ 实测（2026-04-16：全新会话访问 Cars LP，www 主站本轮未出现 Cookie 横幅；my 子域首访确认出现横幅并可正常 Accept）

#### 📊 用例属性

- **优先级**: P0
- **测试类型**: 合规 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC021: 顶栏全局导航与 Cars 落地页共存

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 确认顶栏存在 Gumtree 品牌与搜索区（与首页一致的头部）

#### ✅ 预期结果

- 主站导航结构存在；具体按钮随登录态变化 ✅ 实测（2026-04-16：访客态 Login/Sign up 均可见；已登录态 Messages 链接出现、Login 消失）

#### 📊 用例属性

- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### 边界与负向（补充）

#### TC022: Keyword 输入特殊字符后 Search Cars 不崩溃

#### 📋 前置条件

- 已展开 More options

#### 🎬 执行步骤

1. 在 Keyword 输入 `<>&"'` 等字符
2. 点击 Search Cars

#### ✅ 预期结果

- 页面不白屏；结果或空列表或提示 ✅ 实测（2026-04-16：特殊字符搜索后 URL 跳转至 /search 参数页，页面正常加载无崩溃）

#### 📊 用例属性

- **优先级**: P2
- **测试类型**: 边界值 / 安全
- **UI自动化**: ✅ 可自动化

---

#### TC023: Price min 大于 max 时的校验或结果行为

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 设置 min > max（若界面允许）
2. 点击 Search Cars

#### ✅ 预期结果

- 拦截提示或自动纠正或仍出结果 ✅ 实测（2026-04-16：Price min > max 情形下搜索页正常加载，无 5xx，系统允许此参数组合并返回结果）

#### 📊 用例属性

- **优先级**: P2
- **测试类型**: 负向 / 边界值
- **UI自动化**: ✅ 可自动化

---

#### TC024: 刷新落地页后 Hero 与结构化搜索仍展示

#### 📋 前置条件

- 已在 Cars 落地页

#### 🎬 执行步骤

1. F5 刷新

#### ✅ 预期结果

- 核心模块仍加载 ✅ 实测（2026-04-16：刷新 Cars LP 后 Hero 图、结构化搜索区块正常展示）

#### 📊 用例属性

- **优先级**: P2
- **测试类型**: 时序 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC025: 浏览器后退从 SRP 返回落地页 URL

#### 📋 前置条件

- 从落地页进入搜索结果

#### 🎬 执行步骤

1. 浏览器后退

#### ✅ 预期结果

- 回到 `.../cars-vans-motorbikes/cars` 或历史栈正确 ✅ 实测（2026-04-16：从首页进入 Cars LP 后按后退，URL 正确回到 /cars-vans-motorbikes/cars）

#### 📊 用例属性

- **优先级**: P2
- **测试类型**: 时序 / UI
- **UI自动化**: ✅ 可自动化

---

### Popular models / Reviews / Brands（抽样）

#### TC026: Popular models 区块内链接可点击且为站内车品类目

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 滚动至 Popular models
2. 抽样点击 1～2 个车型/品牌入口

#### ✅ 预期结果

- 跳转至有效列表或筛选页，无 5xx ✅ 实测（2026-04-16：点击品牌链接后跳转至品牌筛选页，无服务端错误）

#### 📊 用例属性

- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC027: Expert reviews 区域文章或卡片跳转

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 在 **Read our latest expert car reviews** 区块点击一条内容

#### ✅ 预期结果

- 进入资讯/评测详情或站内外合法 URL ✅ 实测（2026-04-16：点击 Expert reviews 区块链接，成功跳转至有效详情页，无 404/500）

#### 📊 用例属性

- **优先级**: P2
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC028: Browse by brands 字母或品牌入口可用

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 滚动至 Browse by brands，点击任一品牌

#### ✅ 预期结果

- 进入对应品牌筛选或列表 ✅ 实测（2026-04-16：Browse by brands 品牌链接点击后跳转至对应品牌筛选列表页，无报错）

#### 📊 用例属性

- **优先级**: P2
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### 权限与登录（可选）

#### TC029: 未登录用户可完整使用结构化搜索并进入 SRP

#### 📋 前置条件

- 访客会话

#### 🎬 执行步骤

1. 不登录，直接打开 Cars 落地页并完成 TC012

#### ✅ 预期结果

- 可跳转搜索结果 ✅ 实测（自动化未强制登录）

#### 📊 用例属性

- **优先级**: P0
- **测试类型**: 正向 / 权限
- **UI自动化**: ✅ 可自动化

---

#### TC030: 已登录用户顶栏展示 Messages / Menu（与首页一致）

#### 📋 前置条件

- 已登录

#### 🎬 执行步骤

1. 打开 Cars 落地页查看顶栏

#### ✅ 预期结果

- 与首页已登录态一致 ✅ 实测（2026-04-16：已登录访问 Cars LP，Messages 链接数>0、Login 按钮消失，与首页已登录态行为一致）

#### 📊 用例属性

- **优先级**: P1
- **测试类型**: 正向 / 权限
- **UI自动化**: ✅ 可自动化

---

### SEO / 无障碍（轻量）

#### TC031: 页面存在主层级标题与语义分区

#### 📋 前置条件

- 已进入 Cars 落地页

#### 🎬 执行步骤

1. 检查至少一个 H1 或主 Hero 标题

#### ✅ 预期结果

- **Find Cars for Sale** 以 heading 或显著文本呈现 ✅ 实测

#### 📊 用例属性

- **优先级**: P2
- **测试类型**: UI / 无障碍
- **UI自动化**: ✅ 可自动化

---

#### TC032: 关键图片与 Body type SVG 非空（抽样）

#### 📋 前置条件

- TC017 已覆盖部分

#### 🎬 执行步骤

1. 同 TC017

#### ✅ 预期结果

- Body type 卡片含 **svg** ✅ 实测

#### 📊 用例属性

- **优先级**: P2
- **测试类型**: UI
- **UI自动化**: ✅ 可自动化

---

#### TC033: 性能 — 首屏主要内容可见时间可接受

#### 📋 前置条件

- 网络正常

#### 🎬 执行步骤

1. 打开落地页并记录 Hero 出现耗时（人工或 trace）

#### ✅ 预期结果

- 在约定 SLA 内可见 Hero ⚠️ 推断（需性能基线和专用性能脚本，功能测试范围外）

#### 📊 用例属性

- **优先级**: P3
- **测试类型**: 时序
- **UI自动化**: ❌ 不可自动化（或需专用性能脚本）

---

#### TC034: 与自动化用例 ID 映射（回归清单）

#### 📋 前置条件

- 执行 `pytest test_cases/cars/test_cars_landing_page.py --env=unicorn`

#### 🎬 执行步骤

1. 对照本 MD 中 ✅ 实测条目与 `GUMTREE_CARS_LP_001`–`018`

#### ✅ 预期结果

- 18 条自动化与本文 TC002–TC019、TC012、TC016–TC018 等一致 ✅ 实测（代码级）

#### 📊 用例属性

- **优先级**: P3
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

## 测试统计


| 优先级    | 总数     | 可自动化          |
| ------ | ------ | ------------- |
| P0     | 12     | 12            |
| P1     | 12     | 12            |
| P2     | 8      | 8             |
| P3     | 2      | 1             |
| **合计** | **34** | **33（约 97%）** |


**实测文案覆盖率**：与 **仓库 Cars 落地页自动化** 对齐部分为 **高**；带 ⚠️ 条目建议在 Unicorn 上抽样执行一次 MCP 或手工复验。

---

## 阶段三说明（本次）


| 说明 |
|------|
| **Cursor `user-playwright` MCP**：已于 2026-04-10 成功执行 `browser_navigate` 至 Unicorn Cars LP，并保存证明存档与 YAML 快照（见上文「MCP 证明存档」表）。若日后再次报 `Target page, context or browser has been closed`，见 [mcp-playwright-troubleshooting.md](mcp-playwright-troubleshooting.md) 并可用本地脚本回退。 |
| **证明存档**：[unicorn-cars-landing-MCP证明存档.md](unicorn-cars-landing-MCP证明存档.md) 含 MCP 返回的 **真实** `await page.goto(...)` 与 **ref** 列表；完整树见 [_proof_archives/unicorn-cars-landing-mcp-snapshot-20260410.yml](_proof_archives/unicorn-cars-landing-mcp-snapshot-20260410.yml)。 |
| **预期结果** 中 **✅ 实测**：自动化以 `test_cases/cars/test_cars_landing_page.py` 为准；Unicorn 页面标题、Hero、Search Cars 数量、24h 文案等以 MCP 快照与证明存档为准。 |


