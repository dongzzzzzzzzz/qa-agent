# GT 类广告（Services Web, e_002:B）测试用例合集

> **生成时间**: 2026-04-03（编号修订 2026-05-11）  
> **实验 Header**: `gt_gb_exp_ovr=e_002:B`  
> **自动化对齐**: `tests_py/generated/test_gt_ads_services_web_e002b.py` — 用例编号 **连续 TC001–TC021**。  
`test_tcXXX_*`，每条用例下的 "**脚本**" 字段给出函数名对照。  
> **覆盖范围（合并自两份文档）**:
>
> - **Service Landing Page（入口页/导流页）**：来自 PRD `Service landing page for web (v1.0)` + 对应 Figma
> - **Services SRP + Business profile（VIP）**：来自 Figma `Services.-Introducing-Service-skills`
>
> 说明：本合集统一归类为 **GT 类广告测试用例**，仍按「入口页 → BRP/SRP → VIP」流程分章节组织。

---

## 测试环境配置（必填）


| 字段          | 值                                                  |
| ----------- | -------------------------------------------------- |
| 基础URL       | `https://www.unicorn.gumtree.io`                   |
| Services 入口 | 落地页可直接访问：`/business-services`（脚本不依赖顶部导航点击） |
| 入口/落地       | `https://www.unicorn.gumtree.io/business-services` |
| 实验 Header   | `gt_gb_exp_ovr=e_002:B`                            |
| 账号/登录       | visitor（未登录）                                       |


### 自动化可选环境变量（与脚本一致）

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `GT_SRP_LOCATION` | `SE114DF` | SRP / VIP 相关用例进入结果页后使用的 postcode（legacy fallback 等） |
| `GT_SRP_ENTRY_LOCATION` | `United Kingdom` | Landing → SRP 流程中填写的地区（TC003、`_go_to_srp_results`） |
| `GT_SRP_ENTRY_CATEGORY` | `Health & Beauty` | 当 Search Services / All Categories 不可用时，作为类目入口备选 |

> 删除说明：原 `GT_ENABLE_PLACEHOLDER_CAROUSEL`（旧 TC004） / `GT_ENABLE_HOVER_TOOLTIP`（旧 TC007）两个可选开关随对应可选用例一并下线。

---

## A. Service Landing Page（Web）— GT 类广告用例

### TC001: 直接打开 `/business-services` 并校验关键元素（e_002:B）

#### 执行步骤

1. 设置实验 Header `gt_gb_exp_ovr=e_002:B`
2. 直接访问 `{base}/business-services`（`domcontentloaded`）
3. 接受 Cookie（若出现）

#### 预期结果

- URL 匹配 `/business-services`
- 主文案可见（含 `Find local professionals`）
- `data-testid=input-header-search-location` 可见
- 主按钮文案为 **`Search Services`** 或带数量后缀的 **`Search Services (n)`**（`n≥0`，正则 `^Search Services(\s*\(\s*\d+\s*\))?$`）

**脚本**: `test_tc001_open_services_landing_via_top_nav_e002b`

---

### TC002: Search 区域可见（关键词 textbox、地区、Search Services）

#### 执行步骤

1. 同 TC001 进入 landing
2. 校验地区输入（`input-header-search-location`）可见
3. 校验至少一个 `role=textbox` 可见
4. 校验 **`Search Services` / `Search Services (n)`** 按钮或等价文案可见

#### 预期结果

- 上述控件可见（脚本 **不** 执行 fill/click，仅可见性）

**脚本**: `test_tc002_search_section_visible_e002b`

---

### TC003: 填地区进入 SRP → `Services` 回 landing → 再次进入 landing 后用 Search 进入 SRP

#### 执行步骤

1. 进入 landing（`{base}/business-services`）
2. 在地区输入填入 **`United Kingdom`**（`GT_SRP_ENTRY_LOCATION` 可覆盖）；若页面对象失败则 fallback 到 testid 输入并 Enter（**不**在此步点击「Search Services / All Categories」；依赖填区后的跳转/结果态）
3. 断言 URL 进入 `search` 或 `business-services` 结果态
4. 点击顶部导航 **`Service`/`Services`** 链回首页 landing（若当前 SRP 无该链，脚本 **fallback**：直接打开 `{base}/business-services`）
5. 断言 URL 仍为 `/business-services`
6. 重新访问 **`{base}/business-services`**
7. 访问后再次执行：点击离开 landing 进入 SRP，优先级：**`Search Services` / `Search Services (n)`** → 否则 **`All Categories`**
8. 断言 URL 再次进入 `search` 或 `business-services` 结果态

#### 预期结果

- 第一次：填地区后能进入结果态，并能通过 header `Services` 或 fallback 回到 `/business-services`
- 第二次：从干净的 landing 再次通过 Search Services / All Categories 进入 SRP

**脚本**: `test_tc003_navigate_to_srp_then_services_nav_home_e002b`

---

### TC004: `Most popular categories` 区域 **标题**可见

> 原 TC005

#### 执行步骤

1. 进入 landing
2. 定位文案 `Most popular categories`（不校验卡片数量）

#### 预期结果

- 标题可见；若页面无该区域则 **skip**

**脚本**: `test_tc005_most_popular_categories_section_visible_e002b`

---

### TC005: `All Categories` 在 landing 上可见（点击在 TC006）

> 原 TC006

#### 执行步骤

1. 进入 landing
2. 校验 `All Categories` 文案可见

#### 预期结果

- 可见；若无则 skip

**脚本**: `test_tc006_all_categories_control_visible_e002b`

---

### TC006: 点击 `All Categories` 进入全量 services 结果（URL 断言）

> 原 TC008

#### 执行步骤

1. 进入 landing
2. 点击 `All Categories`

#### 预期结果

- URL 匹配：`/business-services`（根或带 query），或 `search` 且 `search_category=business-services` 等脚本所用正则

**脚本**: `test_tc008_click_all_categories_goes_to_business_services_root_e002b`

---

### TC007: 点击热门类目 **Removal** 进入对应 BRP

> 原 TC009

#### 执行步骤

1. 进入 landing
2. 点击链接或文案 **Removal**

#### 预期结果

- URL 匹配 `/business-services/.*/removal-services`

**脚本**: `test_tc009_click_popular_category_navigates_to_brp_removal_e002b`

---

### TC008: Discovery more — 三个分区 **标题**可见（不校验卡片数量/对齐）

> 原 TC010

#### 执行步骤

1. 进入 landing
2. 分别校验标题模式：
   - `Home Improvement.*Trades`
   - `Moving.*Cleaning`
   - `Professional.*Event`

#### 预期结果

- 三个标题均可见；若无则 skip

**脚本**: `test_tc010_discovery_more_sections_visible_e002b`

---

### TC009: Join us — `advertise-with-us` 外链

> 原 TC011

#### 执行步骤

1. 进入 landing
2. 点击 `href` 含 `advertise-with-us` 的链接(可能 JS click）

#### 预期结果

- 打开 `gumtree.com/info/life/advertise-with-us`

**脚本**: `test_tc011_join_us_links_out_e002b`

---

### TC010: FAQ — 抽样展开第 1 条并校验答案片段

> 原 TC012

#### 执行步骤

1. 进入 landing
2. 点击 `Is it free to get quotes?`（正则含可选 `?`）
3. 断言答案中出现 `100% free`

#### 预期结果

- 展开后答案可见（脚本 **不** 强制展开全部 FAQ）

**脚本**: `test_tc012_faq_expand_sample_question_e002b`

---

## B. Services SRP（Search Results/BRP）— GT 类广告用例

> **共同前置**：脚本通过 `_go_to_srp_results` 进入 SRP：landing → 填 `GT_SRP_ENTRY_LOCATION`（默认 United Kingdom）→ 优先 **Search Services / All Categories** → 否则 **Health & Beauty** 类目 → 再否则 legacy hover 搜索。部分用例在无控件时 **skip**。

### TC011: SRP Filters — `Location`、`Category` 文案可见

> 原 TC013

#### 执行步骤

1. 进入 SRP
2. 断言精确文案 `Location`、`Category`（行首匹配）

#### 预期结果

- 均可见

**脚本**: `test_tc013_srp_filters_location_category_visible_e002b`

---

### TC012: Distance 下拉 + `Update`（若页面支持）

> 原 TC014

#### 执行步骤

1. 进入 SRP
2. 调用页面对象 `set_distance_10_miles_and_update()`；失败则 skip

#### 预期结果

- 仍停留在 SRP，且可见 `Request a quote` 链接（列表非空语境）

**脚本**: `test_tc014_srp_distance_update_clickable_e002b`

---

### TC013: SRP 卡片存在 `Request a quote`

> 原 TC015

#### 执行步骤

1. 进入 SRP
2. 断言按钮 **`Request a quote`** 可见（脚本 **不** 点击）

#### 预期结果

- **`Request a quote` 必校验**；**`Show phone number` 非必**，脚本不强制断言

**脚本**: `test_tc015_srp_card_has_request_quote_e002b`

---

### TC014: GtTestAd 测试广告卡片识别（结构化判定）

> 原 TC016

#### 背景与判定口径

GtTestAd 卡片不再依赖页面上的 `GtTestAd` 文案探针，改为按 **DOM 结构** 判定（与脚本 `_gumtree_ads()` 一致）：

- **是 GtTestAd**：卡片 `<a>` 内同时满足
  - 包含 `<button>` 文案 **`Request a quote`**
  - **不包含** `<button>` 文案 **`Request a call back`** / **`Request a call`**（即非 Bark 卡）

> 与之相对：Bark 卡片识别口径仍为「卡片按钮包含 `Request a call(back)?`」。

#### 前置条件

- SRP 上至少存在一张满足上述结构的 GtTestAd 卡片（否则 skip）

#### 执行步骤

1. 进入 SRP（`_go_to_srp_results`）
2. 用结构化 locator 定位：
   - `page.locator("a").filter(has=Request a quote button).filter(has_not=Request a call back button)`
3. 校验首张匹配卡片可见
4. 校验该卡片内 **`Request a quote`** 按钮可见

#### 预期结果

- 找到至少 1 张符合结构化判定的 GtTestAd 卡片
- 卡片内 **`Request a quote` 必校验**；**`Show phone number` 非必**
- 卡片内**不应**出现 `Request a call back` 按钮（口径互斥保障）

**脚本**: `test_tc016_gt_ad_card_has_ctas_when_marker_present_e002b`

---

### TC015: Pagination — 翻到第 2 页

> 原 TC018

#### 执行步骤

1. 进入 SRP
2. 优先点击 **`View page 2`**；否则 URL/API `go_to_page_number(2)`

#### 预期结果

- URL 含 `page=2` 或 `/page2`

**脚本**: `test_tc018_srp_pagination_click_page_2_e002b`

---

## C. Business profile（VIP）— GT 类广告用例

> **共同前置**：`gt_gb_exp_ovr=e_002:B`；经 `_go_to_srp_results` 进入 Services SRP；SRP 上需存在可点的 listing（`/p/`、`data-q=search-result-anchor` 等，见 `_srp_listing_anchors`）；脚本会尝试最多 **6** 条结果，直到打开含 **Overview + Services** 的 VIP，否则 skip。

### TC016–TC021（当前脚本实现一致）

> 原 TC019–TC024。  
> **与函数 docstring 的差异**：各用例名对应不同产品检查点，但 **当前 Python 实现中六条用例代码路径相同**，仅断言 **Overview**、**Services** 可见。

#### 执行步骤（TC016–TC021 共用）

1. `_go_to_srp_results`
2. `_open_vip_with_overview_services`
3. 断言 **Overview**、**Services** 可见

#### 预期结果

- 上述两项可见；无兼容 VIP 或 SRP 无 listing 时 **skip**

| 新 TC | 原 TC | 说明（docstring 意图） | 脚本函数名 |
| --- | --- | --- | --- |
| TC016 | TC019 | VIP 标题 Business profile | `test_tc019_vip_business_profile_title_visible_e002b` |
| TC017 | TC020 | Services and skills | `test_tc020_vip_services_and_skills_visible_e002b` |
| TC018 | TC021 | Manage skills 卡片 | `test_tc021_vip_manage_skills_card_has_items_e002b` |
| TC019 | TC022 | More options / Edit set / Delete | `test_tc022_vip_more_options_contains_edit_set_and_delete_e002b` |
| TC020 | TC023 | Manage ads 入口可见 | `test_tc023_vip_manage_ads_visible_and_has_entry_e002b` |
| TC021 | TC024 | Manage ads 打开推广流程 | `test_tc024_vip_manage_ads_entry_opens_flow_e002b` |

Preconditions 文档与脚本一致时写作「同 **TC016**（SRP + listing + VIP 模板含 Overview/Services）」。
