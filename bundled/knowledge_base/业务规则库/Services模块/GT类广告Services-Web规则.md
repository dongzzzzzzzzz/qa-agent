# Services 模块 - GT 类广告（Services Web, e_002:B）业务规则

> **知识来源**: `senior-qa-brain/scripts/GT-Ads-Services-Web-testcases.md`（生成时间 2026-04-03）  
> **自动化对齐**: `tests_py/generated/test_gt_ads_services_web_e002b.py` — 用例编号 **TC001–TC024** 与 `test_tc001_*` … `test_tc024_*` 一一对应。

## 1. 功能概述

- **功能描述**: 在 **e_002:B** 实验下，对 **Service Landing Page**（`/business-services`）、**Services SRP/BRP** 与 **Business profile（VIP）** 的 GT 类广告相关能力进行验证：入口页关键元素、导航至 SRP、筛选区与卡片 CTA、分页及 VIP 页核心模块可见性等。
- **用户角色**: 访客（visitor，未登录）。
- **入口位置**: 直接访问 `{base}/business-services`（脚本不依赖顶部导航点击）；实验 Header 固定为 `gt_gb_exp_ovr=e_002:B`。
- **依赖模块**: Landing 页组件、SRP 列表与筛选、赞助/Sponsored 区块、VIP（含 Overview、Services、Manage ads 等）及自动化页面对象封装。

**基础 URL 示例**: `https://www.unicorn.gumtree.io`；落地页：`https://www.unicorn.gumtree.io/business-services`。

## 2. 核心流程

### 2.1 主流程

1. 设置 `gt_gb_exp_ovr=e_002:B`，进入 `/business-services`（`domcontentloaded`），按需接受 Cookie。
2. 校验 Landing：URL、主文案、`data-testid=input-header-search-location`、`Search Services` / `Search Services (n)` 等。
3. 通过填地区、**Search Services** / **All Categories** 或类目入口进入 **SRP/BRP** 结果态（URL 含 `search` 或 `business-services` 等脚本约定）。
4. 在 SRP 校验 Filters 文案、距离更新、卡片 **`Request a quote`**、可选 Sponsored 外链、分页到第 2 页等。
5. 从 SRP 打开 listing，进入含 **Overview + Services** 的 VIP，校验标题区与 Manage ads 等（TC019–TC024 当前脚本路径一致，仅函数名不同）。

### 2.2 异常流程

| 场景 | 处理方式 |
|------|----------|
| Search 区控件不可见 / 类目不可点 | 脚本 **skip**（如 TC005、TC006、部分导航 fallback） |
| 无 `GtTestAd` 文案 | TC016 **skip** |
| 无 Sponsored | TC017 **skip** |
| SRP 无可用 listing 或 VIP 不匹配 | TC019–TC024 **skip**（最多尝试 6 条） |
| Placeholder 轮播 / hover tooltip | 仅当环境变量开启时执行（易波动） |

## 3. 业务规则

### 3.1 输入规则

| 字段/变量 | 类型 | 必填 | 说明 |
|-----------|------|------|------|
| `gt_gb_exp_ovr` | Header | 是（本合集） | 固定 `e_002:B` |
| `GT_SRP_LOCATION` | 环境变量 | 否 | 默认 `SE114DF`；SRP/VIP 相关进入结果页后 postcode（legacy fallback） |
| `GT_SRP_ENTRY_LOCATION` | 环境变量 | 否 | 默认 `United Kingdom`；Landing→SRP 填地区 |
| `GT_SRP_ENTRY_CATEGORY` | 环境变量 | 否 | 默认 `Health & Beauty`；Search/All Categories 不可用时的类目备选 |
| `GT_ENABLE_PLACEHOLDER_CAROUSEL` | 0/1 | 否 | `1` 时执行可选 TC004 placeholder 轮播 |
| `GT_ENABLE_HOVER_TOOLTIP` | 0/1 | 否 | `1` 时执行可选 TC007 hover tooltip |

### 3.2 校验规则

- **Landing TC001**: URL 匹配 `/business-services`；主文案含 `Find local professionals`；`input-header-search-location` 可见；主按钮匹配 `^Search Services(\s*\(\s*\d+\s*\))?$`。
- **TC003**: 填地区进入 SRP → 经顶部 **Service/Services** 回 landing 或 fallback 打开 `/business-services` → 再次用 Search Services / All Categories 进入 SRP。
- **TC008–TC010**: `All Categories`、热门类目 **Removal**（URL `/business-services/.*/removal-services`）、Discovery 分区标题等按脚本正则/可见性校验。
- **SRP TC013–TC018**: Filters 显示 `Location`、`Category`；距离 **Update** 可点击则执行；列表卡片 **必须** 可见 **`Request a quote`**；`Show phone number` **非必**；存在 **`GtTestAd`** 时其容器内须有 **`Request a quote`**；分页到达 `page=2` 或 `/page2`。
- **VIP TC019–TC024**: 经 `_go_to_srp_results` → `_open_vip_with_overview_services`；断言 **Overview**、**Services** 可见；当前 Python 实现六条路径相同，产品细分检查点见用例表（文档与脚本一致时引用 TC019 前置）。

### 3.3 权限规则

- 未登录访客浏览；Join us 外链等跳转到 `gumtree.com/info/life/advertise-with-us`（TC011）。

### 3.4 业务约束

- **可选用例默认关闭**: TC004、TC007 依赖环境变量，避免不稳定干扰 CI。
- **VIP 打开策略**: 最多尝试 6 条结果以找到兼容 VIP 模板。

## 4. 错误处理

| 类型 | 触发条件 | 预期 |
|------|----------|------|
| 控件缺失 | 页面改版或实验差异 | 对应用例 **skip**，不判失败 |
| 外链新标签 | Sponsored 点击 | 新 tab 加载（TC017） |
| FAQ 抽样 | 仅展开一条 FAQ | 答案中含 `100% free` 片段（TC012） |

## 5. 已知问题

- **TC019–TC024**: 自动化实现与各用例 docstring「意图」不完全一一对应，以脚本函数与共用步骤为准；产品细化断言需后续对齐脚本或拆分代码路径。
- **可选用例**: Placeholder 与 tooltip 易受环境与时机影响，默认关闭。

## 6. 变更历史

| 日期 | 版本 | 变更内容 | 变更人 |
|------|------|----------|--------|
| 2026-04-15 | v1.0 | 从 GT-Ads-Services-Web-testcases.md 归档至知识库 | 知识库管理器 |
