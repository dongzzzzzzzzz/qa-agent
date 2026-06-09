# Performance Metrics Phase 2 - 测试用例文档

> **生成时间**: 2026-03-18
> **测试范围**: Performance Metrics Dashboard（/performance-metrics）
> **总用例数**: 62条
> **可自动化**: 22条 (35.5%)
> **PRD版本**: PRD_ Performance Metrics Phase 2.md
> **页面探索**: https://www.unicorn.gumtree.io/performance-metrics

---

## 测试环境配置

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | uk | Gumtree UK |
| 基础URL | https://www.unicorn.gumtree.io | 测试站点地址 |
| 站点名称 | Gumtree Unicorn（测试环境） | |
| 角色 | seller | Pro Account 卖家 |
| 账号名称 | gumtree_pro_seller | 用于 session 命名 |
| 测试账号 | cahibey466@gamintor.com | Pro账号 |
| 测试密码 | Gumtree123! | |
| 入口URL | https://www.unicorn.gumtree.io/performance-metrics | 直接访问 |

> **自动化可行性说明**：标记 ✅ 的用例满足以下所有条件：
> 1. 使用当前测试账号即可运行，无需额外账号
> 2. 不依赖特定业务数据（如"账号必须有7天数据"），或可通过当前账号的空状态/已知状态验证
> 3. Playwright 可确定性断言（UI 状态/元素存在/URL/文本匹配）

---

## 📑 目录

1. [页面访问与权限控制](#1-页面访问与权限控制)
2. [时间筛选器（Filter Module）](#2-时间筛选器)
3. [核心指标卡片区（Key Metrics Board）](#3-核心指标卡片区)
4. [Tooltip 交互](#4-tooltip-交互)
5. [Best Performing Locations](#5-best-performing-locations)
6. [Ads Breakdown 表格](#6-ads-breakdown-表格)
7. [数据导出（Export）](#7-数据导出)
8. [数据一致性](#8-数据一致性)
9. [空状态处理](#9-空状态处理)
10. [边界与异常场景](#10-边界与异常场景)

---

## 1. 页面访问与权限控制

### TC001: Pro用户从侧边栏进入 My Metrics 页面

#### 📋 前置条件
- Pro Account 用户已登录
- 当前在 /manage/ads 页面

#### 🎬 执行步骤
1. 在左侧导航栏找到"My Metrics"链接（带"New"角标）
2. 点击"My Metrics"

#### ✅ 预期结果
- 跳转至 `/performance-metrics` 页面
- 页面正常加载，显示仪表盘内容
- 侧边栏"My Metrics"项处于选中状态

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC002: "My Metrics"标签上显示"New"角标

#### 📋 前置条件
- Pro Account 用户已登录，处于 My Account 相关页面

#### 🎬 执行步骤
1. 查看左侧导航栏的"My Metrics"链接

#### ✅ 预期结果
- "My Metrics"标签旁显示"New"角标

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI测试
- **UI自动化**: ✅ 可自动化

---

### TC003: 未登录用户直接访问 /performance-metrics 被重定向

#### 📋 前置条件
- 用户未登录（无有效 session）

#### 🎬 执行步骤
1. 直接在浏览器访问 `https://www.unicorn.gumtree.io/performance-metrics`

#### ✅ 预期结果
- 自动重定向至登录页
- 登录成功后重定向回 /performance-metrics

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 权限测试
- **UI自动化**: ✅ 可自动化

---

### TC004: 非Pro账号无法看到 My Metrics 导航入口

#### 📋 前置条件
- 非Pro（普通）账号已登录

#### 🎬 执行步骤
1. 登录非Pro账号
2. 进入 /manage/ads
3. 查看左侧导航栏

#### ✅ 预期结果
- 侧边栏不显示"My Metrics"选项
- 即使直接访问 /performance-metrics，显示提示语："This account does not currently support the dashboard feature. Please upgrade to a Pro account."

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 权限测试
- **UI自动化**: ✅ 可自动化

---

### TC005: Pro用户直接访问 /performance-metrics 正常展示

#### 📋 前置条件
- Pro Account 用户已登录

#### 🎬 执行步骤
1. 直接在浏览器地址栏输入 `https://www.unicorn.gumtree.io/performance-metrics`
2. 观察页面

#### ✅ 预期结果
- 页面正常加载，无报错
- 显示仪表盘所有模块

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

## 2. 时间筛选器

### TC006: 页面默认加载时间范围为"Last 30 days"

#### 📋 前置条件
- Pro Account 用户首次或清除偏好后访问 /performance-metrics

#### 🎬 执行步骤
1. 进入 /performance-metrics 页面
2. 观察时间筛选器区域

#### ✅ 预期结果
- "Last 30 days"按钮处于高亮/激活状态
- "Last 7 days"按钮处于非激活状态
- 页面数据基于最近30天加载
- 【⚠️ PRD Diff D1】验证重点：当前探索发现可能是"Last 7 days"激活，需确认

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

---

### TC007: 切换至"Last 7 days"后数据联动更新

#### 📋 前置条件
- Pro Account 用户在 /performance-metrics，当前选中"Last 30 days"

#### 🎬 执行步骤
1. 点击"Last 7 days"按钮

#### ✅ 预期结果
- "Last 7 days"按钮高亮激活
- "Last 30 days"按钮恢复普通状态
- 所有指标卡片数据刷新（基于T-7到T-1）
- Best Performing Locations 数据刷新
- Ads Breakdown 表格数据刷新
- 页面无需手动刷新即完成更新

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（正向交互：点击按钮验证激活状态切换）

---

### TC008: 切换至"Last 30 days"后数据联动更新

#### 📋 前置条件
- Pro Account 用户在 /performance-metrics，当前选中"Last 7 days"

#### 🎬 执行步骤
1. 点击"Last 30 days"按钮

#### ✅ 预期结果
- "Last 30 days"按钮高亮激活
- 所有模块数据基于最近30天刷新
- Last 30 days 值通常 ≥ Last 7 days 值

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（正向交互：点击按钮验证激活状态切换）

---

### TC009: 时间范围切换触发 analytics 事件 dashboard_time_range_change

#### 📋 前置条件
- Pro用户在 /performance-metrics，已对接埋点监控

#### 🎬 执行步骤
1. 点击"Last 7 days"
2. 检查 analytics 事件日志

#### ✅ 预期结果
- 触发 `dashboard_time_range_change` 事件
- 携带字段：user_id, account_id, timestamp, time_range="last_7_days"

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 埋点测试
- **UI自动化**: ❌ 不可自动化（需要埋点后台验证）

---

### TC010: 页面加载完成触发 dashboard_view 埋点事件

#### 📋 前置条件
- Pro用户首次进入 /performance-metrics

#### 🎬 执行步骤
1. 进入 /performance-metrics 等待数据加载完成
2. 检查 analytics 事件日志

#### ✅ 预期结果
- 触发一次 `dashboard_view` 事件
- 携带字段：user_id, timestamp
- 不重复触发（SPA切换路由也只触发一次）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 埋点测试
- **UI自动化**: ❌ 不可自动化

---

## 3. 核心指标卡片区

### TC011: 页面展示 Search Views 指标卡片

#### 📋 前置条件
- Pro账号有过广告数据，进入 /performance-metrics

#### 🎬 执行步骤
1. 查看页面顶部指标卡片区

#### ✅ 预期结果
- 显示"Search Views"卡片，数值为非负整数
- 数值含义：广告在搜索结果页/首页展示的总次数

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ❌ 不可自动化（当前账号无历史数据，无法验证数值正确性）

---

### TC012: 页面展示 Ad Views 指标卡片

#### 📋 前置条件
- Pro账号有过广告数据

#### 🎬 执行步骤
1. 查看指标卡片区

#### ✅ 预期结果
- 显示"Ad Views"卡片，数值为非负整数
- 数值含义：广告详情页(VIP页)被查看次数

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ❌ 不可自动化（依赖特定有值数据）

---

### TC013: 页面展示 Unique Replies 指标卡片

#### 📋 前置条件
- Pro账号有过回复数据

#### 🎬 执行步骤
1. 查看指标卡片区

#### ✅ 预期结果
- 显示"Unique Replies"卡片，数值为非负整数
- 去重逻辑：同user+同ad，3天内只计1次

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ❌ 不可自动化（依赖特定有值数据）

---

### TC014: 页面展示 New Ads 指标卡片

#### 📋 前置条件
- 测试账号在所选时间范围内有新发布的广告

#### 🎬 执行步骤
1. 查看指标卡片区

#### ✅ 预期结果
- 显示"New Ads"卡片（对应PRD的"New Listings Posted"）
- 数值为所选时间范围内新创建广告数

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ❌ 不可自动化（依赖特定有值数据）

---

### TC015: 页面展示 Reposted Ads 指标卡片

#### 📋 前置条件
- 测试账号在所选时间范围内有重新发布的广告

#### 🎬 执行步骤
1. 查看指标卡片区

#### ✅ 预期结果
- 显示"Reposted Ads"卡片（对应PRD的"Listings Reposted"）
- 数值为所选时间范围内重发广告数

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ❌ 不可自动化（依赖特定有值数据）

---

### TC016: Search Views to Click Conversion 计算正确

#### 📋 前置条件
- 账号有 Search Views 和 Ad Views 数据

#### 🎬 执行步骤
1. 记录"Search Views"数值（I）
2. 记录"Ad Views"数值（V）
3. 查看"Search Views to Click Conversion"转化率

#### ✅ 预期结果
- 转化率 = V / I × 100%（保留至少1位小数）
- 结果以百分比形式显示（如"3.2%"）
- 若 I = 0，显示"-"或"0%"，不报除零错误

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 数据验证
- **UI自动化**: ❌ 不可自动化（需要非零数据才能验证计算逻辑）

---

### TC017: Ad Views to Reply Conversion 计算正确

#### 📋 前置条件
- 账号有 Ad Views 和 Unique Replies 数据

#### 🎬 执行步骤
1. 记录"Ad Views"数值（V）
2. 记录"Unique Replies"数值（R）
3. 查看"Ad Views to Reply Conversion"转化率

#### ✅ 预期结果
- 转化率 = R / V × 100%
- 以百分比显示
- 若 V = 0，显示"-"或"0%"，不报除零错误

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 数据验证
- **UI自动化**: ❌ 不可自动化（需要非零数据）

---

### TC018: 页眉"Live Ads"数量显示正确

#### 📋 前置条件
- 测试账号有 Active 状态的广告

#### 🎬 执行步骤
1. 查看页面顶部的 "Hello, xxx! You currently have X Live Ads."

#### ✅ 预期结果
- Live Ads 数量与 Manage My Ads 页面显示的 Active 广告数一致
- Live Ads 数据为实时，不受时间筛选器影响

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 数据验证
- **UI自动化**: ✅ 可自动化（正向页眉展示，当前账号有 Active 广告可验证）

---

### TC019: 切换时间范围后各指标数值正确更新

#### 📋 前置条件
- 账号有一定的历史数据（Last 7 days 和 Last 30 days 数据不同）

#### 🎬 执行步骤
1. 记录 Last 7 days 下各指标数值
2. 切换至 Last 30 days
3. 记录各指标新数值
4. 切换回 Last 7 days 验证数值还原

#### ✅ 预期结果
- Last 30 days 各指标值 ≥ Last 7 days 值（30天包含7天数据）
- 来回切换后数值稳定，不出现异常闪烁或累加

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 数据一致性
- **UI自动化**: ❌ 不可自动化（需要两个时间范围均有差异数据）

---

### TC020: 指标数据无值时显示"-"而非0或空白

#### 📋 前置条件
- 使用当前测试账号（在所选时间范围内无数据）

#### 🎬 执行步骤
1. 进入 /performance-metrics
2. 观察各指标卡片数值

#### ✅ 预期结果
- 所有无数据的指标显示"-"（连字符）
- 不显示"0"、"null"、"undefined"或空白

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 空状态测试
- **UI自动化**: ✅ 可自动化（正向展示：当前账号数据为"-"，可直接验证）

---

## 4. Tooltip 交互

### TC021: Search Views Tooltip 内容正确

#### 📋 前置条件
- 用户在 /performance-metrics 页面

#### 🎬 执行步骤
1. 点击或悬停"Search Views"指标卡片的信息图标（ⓘ）
2. 查看弹出的 tooltip 内容

#### ✅ 预期结果
- Tooltip 显示："How many times your ad showed up when people were searching."
- 或PRD原文："The number of times your ads appeared in search results."（以实际版本为准）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI测试
- **UI自动化**: ✅ 可自动化（Tooltip 触发方式为展开下拉，文案验证易因版本更新而脆断）

---

### TC022: Search Views to Click Conversion Tooltip 内容正确

#### 📋 前置条件
- 用户在 /performance-metrics 页面

#### 🎬 执行步骤
1. 展开 Search Views 卡片的 Conversion 信息
2. 查看 tooltip 或说明文字

#### ✅ 预期结果
- 显示："The percentage of people who saw your ad in their search results and decided to click on it. It measures how effectively your photo, price, and title grab a user's attention."

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI测试
- **UI自动化**: ✅ 可自动化（文案验证易脆断）

---

### TC023: Ad Views Tooltip 内容正确

#### 📋 前置条件
- 用户在 /performance-metrics 页面

#### 🎬 执行步骤
1. 点击或悬停"Ad Views"指标的信息图标

#### ✅ 预期结果
- 显示："How many times your ad was opened to view the full details."

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI测试
- **UI自动化**: ✅ 可自动化（文案验证易脆断）

---

### TC024: Ad Views to Reply Conversion Tooltip 内容正确

#### 📋 前置条件
- 用户在 /performance-metrics 页面

#### 🎬 执行步骤
1. 展开 Ad Views 卡片的 Conversion 信息

#### ✅ 预期结果
- 显示："The percentage of people who, after viewing your ad, decided to get in touch. This measures how well your photos, description, and price convinced the user to take the next step."

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI测试
- **UI自动化**: ✅ 可自动化（文案验证易脆断）

---

### TC025: 点击 Tooltip 外部区域关闭 Tooltip

#### 📋 前置条件
- 某个 Tooltip 处于展开/显示状态

#### 🎬 执行步骤
1. 打开任意指标的 Tooltip
2. 点击页面其他空白区域

#### ✅ 预期结果
- Tooltip 关闭/收起

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 交互测试
- **UI自动化**: ✅ 可自动化（Tooltip 展开/收起状态判断依赖视觉，无稳定选择器）

---

## 5. Best Performing Locations

### TC026: Best Performing Locations 模块正常展示

#### 📋 前置条件
- 账号有来自UK地区买家的回复数据

#### 🎬 执行步骤
1. 查看"Best performing locations"区域
2. 观察数据展示

#### ✅ 预期结果
- 展示"Locations show where buyer enquiries came from."说明文字
- 展示 Location | Unique Replies 两列数据
- 按 Unique Replies 降序排列
- 仅显示UK境内地区，不含海外

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ❌ 不可自动化（当前账号无回复数据，无法验证有数据状态）

---

### TC027: Locations 排序按 Unique Replies 降序

#### 📋 前置条件
- 账号有多个地区的回复数据

#### 🎬 执行步骤
1. 查看 Best Performing Locations 列表

#### ✅ 预期结果
- 第一行 Unique Replies ≥ 第二行 ≥ 第三行...
- 降序排列无误

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 数据验证
- **UI自动化**: ❌ 不可自动化（需要多个地区的回复数据）

---

### TC028: Locations 列表可滚动查看所有地区

#### 📋 前置条件
- 账号有超过屏幕可显示数量的地区数据

#### 🎬 执行步骤
1. 在 Best Performing Locations 区域内向下滚动

#### ✅ 预期结果
- 列表内可滚动
- 所有地区数据均可查看
- 滚动不影响页面其他模块

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ❌ 不可自动化（需要足够多数据）

---

### TC029: 未知位置的买家显示为"Other"

#### 📋 前置条件
- 有来自位置未知的买家回复

#### 🎬 执行步骤
1. 查看 Best Performing Locations 列表

#### ✅ 预期结果
- 位置未知的回复汇总显示为"Other"

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ❌ 不可自动化（需要特定数据）

---

### TC030: 切换时间范围后 Locations 数据更新

#### 📋 前置条件
- 账号有 Last 7 days 和 Last 30 days 不同的位置数据

#### 🎬 执行步骤
1. 查看 Last 30 days 下的 Locations 数据
2. 切换至 Last 7 days
3. 对比数据变化

#### ✅ 预期结果
- 切换后位置数据和 Unique Replies 数值更新
- 数据与时间范围筛选联动

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 数据联动
- **UI自动化**: ❌ 不可自动化（需要两个时间范围均有位置数据）

---

### TC031: Locations 无数据时显示正确的空状态

#### 📋 前置条件
- 账号在所选时间范围内无任何回复数据

#### 🎬 执行步骤
1. 进入 /performance-metrics，选择无数据的时间范围

#### ✅ 预期结果
- 显示空状态提示："No data available yet. Try polishing your ad to attract more replies."
- 不显示错误信息

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 空状态测试
- **UI自动化**: ✅ 可自动化（正向展示：当前账号 Locations 为空状态，可直接验证文案）

---

## 6. Ads Breakdown 表格

### TC032: Ads Breakdown 表格展示正确的列

#### 📋 前置条件
- 账号在所选时间范围内有 Live Ads

#### 🎬 执行步骤
1. 查看 Ads Breakdown 表格头部

#### ✅ 预期结果
- 列顺序：Listing | Search Views | Ad Views | Unique Replies | Location | Features Used
- 列名显示正确，无拼写错误

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: UI测试
- **UI自动化**: ✅ 可自动化（正向展示：表头结构固定，与数据无关）

---

### TC033: Ads Breakdown 按 Search Views 降序排列

#### 📋 前置条件
- 账号有多条 Active 广告，各广告 Search Views 不同

#### 🎬 执行步骤
1. 查看 Ads Breakdown 表格内容

#### ✅ 预期结果
- 第一行广告的 Search Views ≥ 第二行 ≥ 第三行...
- 默认降序无需手动点击排序

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 数据验证
- **UI自动化**: ❌ 不可自动化（当前账号数据为"-"，无法验证排序）

---

### TC034: Ads Breakdown 展示广告标题和 Listing ID

#### 📋 前置条件
- 账号有 Active 广告

#### 🎬 执行步骤
1. 查看 Ads Breakdown 表格的 Listing 列

#### ✅ 预期结果
- 每行显示广告标题和 Listing ID
- 标题超长时截断并显示省略号（...）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI测试
- **UI自动化**: ❌ 不可自动化（当前账号表格显示空状态，无行数据）

---

### TC035: 广告标题截断时鼠标悬停显示完整标题

#### 📋 前置条件
- 有一条广告标题超出列宽（被截断显示）

#### 🎬 执行步骤
1. 将鼠标悬停在被截断的广告标题上

#### ✅ 预期结果
- 显示 tooltip 展示完整的广告标题

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 交互测试
- **UI自动化**: ❌ 不可自动化（需要特定超长标题数据）

---

### TC036: 广告标题不可点击（非链接）

#### 📋 前置条件
- Ads Breakdown 有广告数据

#### 🎬 执行步骤
1. 点击 Listing 列中的广告标题

#### ✅ 预期结果
- 点击无任何跳转
- 标题不是超链接样式（无下划线/不变色）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UI测试
- **UI自动化**: ❌ 不可自动化（需要有行数据）

---

### TC037: Ads Breakdown 中 Location 显示广告的 L2 地区

#### 📋 前置条件
- Ads Breakdown 有广告数据，广告设置了位置信息

#### 🎬 执行步骤
1. 查看 Ads Breakdown 表格 Location 列

#### ✅ 预期结果
- 显示广告发布时设定的 L2 地区（如"Birmingham"）
- 不显示L1或L3级别

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 数据验证
- **UI自动化**: ❌ 不可自动化（需要有行数据）

---

### TC038: Features Used 列正确显示付费功能使用情况

#### 📋 前置条件
- 有使用过 Bump Up 或 Top Ad 功能的广告

#### 🎬 执行步骤
1. 查看 Ads Breakdown 表格 Features Used 列

#### ✅ 预期结果
- Bump Up: 显示"Bump Up +X"（X为次数）
- Top Ad: 显示"Top Ad +X"
- 多个功能：分行显示（如"Bump Up +3, Top Ad +1"）
- 未使用任何付费功能：显示"None"

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 数据验证
- **UI自动化**: ❌ 不可自动化（需要付费功能使用记录）

---

### TC039: Ads Breakdown 数据缺失时显示"—"

#### 📋 前置条件
- 某广告的某列数据缺失

#### 🎬 执行步骤
1. 查看有数据缺失的广告行

#### ✅ 预期结果
- 缺失数据的单元格显示"—"（长破折号）
- 不显示 null、undefined 或空白

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界测试
- **UI自动化**: ❌ 不可自动化（需要数据缺失场景）

---

### TC040: 切换时间范围后 Ads Breakdown 数据更新

#### 📋 前置条件
- 账号有数据，Last 7/30 days 数据有差异

#### 🎬 执行步骤
1. 记录 Last 30 days 下 Ads Breakdown 第一行广告的各指标值
2. 切换至 Last 7 days
3. 对比数值变化

#### ✅ 预期结果
- 切换后表格数据刷新
- Last 7 days 下各指标值 ≤ Last 30 days 下对应值

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 数据联动
- **UI自动化**: ❌ 不可自动化（需要两个时间范围均有差异数据）

---

### TC041: Ads Breakdown 中的广告是"selected time range 期间 Live 的广告"

#### 📋 前置条件
- 有一条广告在 Last 7 days 内 Active，但在 Last 30 days 中的前23天已下架

#### 🎬 执行步骤
1. 切换 Last 30 days，查看 Ads Breakdown 是否包含该广告
2. 切换 Last 7 days，验证该广告是否仍出现

#### ✅ 预期结果
- 广告在 selected time range 内任何时段 Live 即显示在表格中
- 下架的广告如果在时间范围内曾经 Active，也应显示

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 业务逻辑
- **UI自动化**: ❌ 不可自动化（需要特定数据状态）

---

## 7. 数据导出

### TC042: 有数据时 Export 按钮可点击

#### 📋 前置条件
- 账号有 Live Ads 数据

#### 🎬 执行步骤
1. 查看 Ads Breakdown 区域右上角的"Export"按钮

#### ✅ 预期结果
- Export 按钮处于可点击状态（非 disabled）
- 按钮有正常视觉样式

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ❌ 不可自动化（需要账号有数据才能验证 enabled 状态）

---

### TC043: 无 Live Ads 时 Export 按钮禁用

#### 📋 前置条件
- 账号在所选时间范围内无 Live Ads

#### 🎬 执行步骤
1. 查看无数据状态下的 Export 按钮

#### ✅ 预期结果
- Export 按钮处于 disabled 状态
- 不可点击，有禁用视觉样式（灰色或半透明）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界测试
- **UI自动化**: ❌ 不可自动化（边界场景，非正向展示）

---

### TC044: 点击 Export 触发文件下载

#### 📋 前置条件
- 账号有 Live Ads 数据，Export 按钮可用

#### 🎬 执行步骤
1. 点击"Export"按钮
2. 等待文件下载完成

#### ✅ 预期结果
- 触发文件下载
- 文件格式为 .xlsx（Excel）
- 文件名格式：`live_ads_breakdown_last_7_days_YYYY-MM-DD`（或 last_30_days，取决于当前选择）
- 日期使用 T-1 日期

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ❌ 不可自动化（需有数据才能触发下载）

---

### TC045: 导出文件列与页面表格列一致

#### 📋 前置条件
- 下载了 Export 文件

#### 🎬 执行步骤
1. 打开下载的文件
2. 对比文件列与页面 Ads Breakdown 表格的列

#### ✅ 预期结果
- 文件包含列：Listing Title, Ad ID, Search Views, Ad Views, Unique Replies, Location, Features Used
- 无多余列，无缺失列

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 数据验证
- **UI自动化**: ❌ 不可自动化（需要文件内容比对）

---

### TC046: 导出文件数据与页面展示数据一致

#### 📋 前置条件
- 账号有 Live Ads 数据，已下载 Export 文件

#### 🎬 执行步骤
1. 记录页面 Ads Breakdown 第一条广告的各数值
2. 在下载的文件中找到对应广告
3. 对比数值

#### ✅ 预期结果
- 文件中数据与页面显示数据完全一致
- 时间范围一致（文件数据对应所选时间范围）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 数据一致性
- **UI自动化**: ❌ 不可自动化

---

### TC047: 导出时显示 Loading 状态（大数据量）

#### 📋 前置条件
- 账号有大量广告数据（异步生成场景）

#### 🎬 执行步骤
1. 点击 Export 按钮
2. 观察按钮或页面是否有 loading 提示

#### ✅ 预期结果
- 数据量大时显示 loading 状态
- 文件生成完成后自动下载
- 期间用户可继续操作页面

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 性能/交互测试
- **UI自动化**: ❌ 不可自动化

---

### TC048: 点击 Export 触发 dashboard_download_click 埋点

#### 📋 前置条件
- Pro用户在 /performance-metrics，有 Live Ads

#### 🎬 执行步骤
1. 点击 Export 按钮
2. 检查 analytics 日志

#### ✅ 预期结果
- 触发 `dashboard_download_click` 事件
- 携带：user_id, account_id, timestamp, time_range

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 埋点测试
- **UI自动化**: ❌ 不可自动化

---

## 8. 数据一致性

### TC049: Performance Metrics 与 Manage My Ads 页面 Live Ads 数量一致

#### 📋 前置条件
- Pro账号有 Active 广告

#### 🎬 执行步骤
1. 在 /manage/ads 页面记录 Active 广告数量
2. 进入 /performance-metrics
3. 查看页眉"You currently have X Live Ads."

#### ✅ 预期结果
- 两处 Live Ads 数量相同
- 数据实时一致，无缓存偏差

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 数据一致性
- **UI自动化**: ❌ 不可自动化（跨页数据对比属于数据验证，非正向展示）

---

### TC050: Manage My Ads 页面 Phase 1 KPI 卡片与 Metrics 页面数据一致

#### 📋 前置条件
- 已在 Phase 1 发布时，Manage My Ads 顶部有3个KPI汇总卡片

#### 🎬 执行步骤
1. 在 /manage/ads 页面查看顶部 KPI 卡片数值（Last 7 days）
2. 进入 /performance-metrics 选择 Last 7 days
3. 对比对应指标数值

#### ✅ 预期结果
- 两处对应指标数值完全一致
- PRD 明确要求："The metric values shown here must be consistent with the corresponding values shown in the Metrics tab."

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 数据一致性
- **UI自动化**: ❌ 不可自动化（当前账号两处均为"-"，无法验证一致性逻辑）

---

### TC051: Ads Breakdown 各广告 Unique Replies 总和 ≤ 账户 Unique Replies

#### 📋 前置条件
- 账号有 Unique Replies 数据且 Ads Breakdown 有数据

#### 🎬 执行步骤
1. 记录 Key Metrics Board 中的"Unique Replies"总值（R）
2. 将 Ads Breakdown 中所有广告的 Unique Replies 列求和（S）

#### ✅ 预期结果
- S ≈ R（因去重口径一致，两者应相等或极度接近）
- 注意：账号级别的去重可能与广告级别去重有差异，需产品确认口径

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 数据一致性
- **UI自动化**: ❌ 不可自动化（需要有数据）

---

## 9. 空状态处理

### TC052: 无 Live Ads 时 Ads Breakdown 显示空状态

#### 📋 前置条件
- 账号在所选时间范围内无任何 Active 广告

#### 🎬 执行步骤
1. 进入 /performance-metrics
2. 查看 Ads Breakdown 区域

#### ✅ 预期结果
- 显示空状态图标和提示文字："No data available yet. Create a listing to unlock insights."
- 不显示空白表格行

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 空状态测试
- **UI自动化**: ✅ 可自动化（正向展示：当前账号 Ads Breakdown 为空状态，可直接验证文案）

---

### TC053: 空状态触发 dashboard_empty_state_view 埋点

#### 📋 前置条件
- 某模块处于空状态（无数据）

#### 🎬 执行步骤
1. 进入 /performance-metrics 触发空状态
2. 检查 analytics 日志

#### ✅ 预期结果
- 触发 `dashboard_empty_state_view` 事件
- 携带：user_id, account_id, timestamp, module_name, reason

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 埋点测试
- **UI自动化**: ❌ 不可自动化

---

### TC054: 数据延迟更新提示显示

#### 📋 前置条件
- 用户在 /performance-metrics

#### 🎬 执行步骤
1. 查看页面底部或合适位置

#### ✅ 预期结果
- 显示提示："We update the data everyday, but sometimes it may be delayed."
- 提示文字在适当位置展示

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UI测试
- **UI自动化**: ✅ 可自动化（正向展示：固定提示文案，与数据无关）

---

## 10. 边界与异常场景

### TC055: 多账号UID：Account Switcher 显示所有关联账号

#### 📋 前置条件
- 当前UID关联了多个账号（Pro和非Pro混合）

#### 🎬 执行步骤
1. 进入 /performance-metrics
2. 查找 Account Switcher 下拉组件
3. 展开查看关联账号列表

#### ✅ 预期结果
- 显示所有关联Account ID列表
- 选择非Pro账号时显示提示："This account does not currently support the dashboard feature."
- 选择Pro账号时正常展示Dashboard

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（需要多账号数据）

---

### TC056: 单账号UID：Account Switcher 隐藏

#### 📋 前置条件
- 当前UID仅关联1个账号（当前测试账号）

#### 🎬 执行步骤
1. 进入 /performance-metrics
2. 查找 Account Switcher

#### ✅ 预期结果
- Account Switcher 不显示或处于隐藏/禁用状态
- 页面正常展示该账号的数据

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（边界场景，非正向交互）

---

### TC057: 网络请求失败时页面错误处理

#### 📋 前置条件
- 模拟网络异常（断网或API返回500）

#### 🎬 执行步骤
1. 使用 DevTools 拦截 metrics API 请求，返回500错误
2. 进入或刷新 /performance-metrics

#### ✅ 预期结果
- 显示友好的错误提示，不显示技术错误堆栈
- 提供重试机制（如 "Retry" 按钮或提示刷新）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 异常处理
- **UI自动化**: ❌ 不可自动化（DevTools 网络拦截需手动操作）

---

### TC058: 页面在移动端浏览器正常展示（Mobile Web）

#### 📋 前置条件
- 使用手机或浏览器模拟移动端视口（375px宽度）

#### 🎬 执行步骤
1. 在移动端访问 /performance-metrics
2. 检查各模块布局

#### ✅ 预期结果
- 页面响应式布局正常
- 各指标卡片不重叠，可读性好
- Ads Breakdown 表格可横向滚动
- 无内容溢出或遮挡

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 兼容性测试
- **UI自动化**: ✅ 可自动化（正向展示：Playwright 设置移动端 viewport 验证布局）

---

### TC059: 页面在不同浏览器正常展示（Chrome/Safari/Firefox）

#### 📋 前置条件
- 分别在 Chrome、Safari、Firefox 中访问

#### 🎬 执行步骤
1. 分别在三个浏览器中登录并访问 /performance-metrics
2. 对比显示效果

#### ✅ 预期结果
- 三个浏览器下展示一致
- 无布局错乱或功能失效

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 兼容性测试
- **UI自动化**: ❌ 不可自动化（需多浏览器环境）

---

### TC060: 页面加载性能：首次渲染时间合理

#### 📋 前置条件
- 正常网络环境，Pro用户访问 /performance-metrics

#### 🎬 执行步骤
1. 使用 Chrome DevTools 记录页面加载时间
2. 记录 API 请求响应时间

#### ✅ 预期结果
- 页面首次有内容展示（FCP）< 3秒
- 全部 metrics 数据加载完成 < 5秒
- 无明显白屏卡顿

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 性能测试
- **UI自动化**: ❌ 不可自动化（需要性能监控工具）

---

### TC061: 重复快速切换时间范围不出现数据竞态

#### 📋 前置条件
- Pro用户在 /performance-metrics

#### 🎬 执行步骤
1. 快速连续点击"Last 7 days" → "Last 30 days" → "Last 7 days"（间隔约200ms）
2. 等待数据加载完成
3. 验证最终显示的数据

#### ✅ 预期结果
- 最终展示的数据与最后一次点击的时间范围一致
- 不出现两个时间范围数据混合展示的情况
- 不出现页面报错

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 并发/竞态测试
- **UI自动化**: ❌ 不可自动化（竞态边界场景，非正向交互）

---

### TC062: 登录状态过期后访问页面正确跳转

#### 📋 前置条件
- 用户 session 已过期（等待足够长时间或手动清除 cookie）

#### 🎬 执行步骤
1. 在 session 过期后，尝试切换时间范围或触发 API 请求

#### ✅ 预期结果
- 收到 401 响应后自动跳转至登录页
- 登录成功后返回 /performance-metrics

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 权限测试
- **UI自动化**: ❌ 不可自动化（鉴权异常场景，非正向展示）

---

## 测试统计

### 用例概览

| 统计项 | 数量 |
|-------|------|
| 总用例数 | 62条 |
| 可自动化 | 22条 (35.5%) |
| 不可自动化 | 40条 (64.5%) |

### 可自动化用例清单（正向展示与交互）

| TC编号 | 用例名称 | 类型 |
|--------|---------|------|
| TC001 | Pro用户从侧边栏进入 My Metrics 页面 | 导航交互 |
| TC002 | "My Metrics"标签上显示"New"角标 | UI展示 |
| TC003 | 未登录用户直接访问被重定向 | 权限测试 |
| TC004 | 非Pro账号无法看到 My Metrics 导航入口 | 权限测试 |
| TC005 | Pro用户直接访问 /performance-metrics 正常展示 | 页面展示 |
| TC006 | 页面默认加载时间范围为"Last 30 days" | UI展示 |
| TC007 | 切换至"Last 7 days"按钮激活状态正确 | 交互 |
| TC008 | 切换至"Last 30 days"按钮激活状态正确 | 交互 |
| TC018 | 页眉"Live Ads"数量正确展示 | UI展示 |
| TC020 | 指标数据无值时显示"-" | UI展示 |
| TC021 | Search Views Tooltip 内容正确 | Tooltip交互 |
| TC022 | Search Views to Click Conversion Tooltip 内容正确 | Tooltip交互 |
| TC023 | Ad Views Tooltip 内容正确 | Tooltip交互 |
| TC024 | Ad Views to Reply Conversion Tooltip 内容正确 | Tooltip交互 |
| TC025 | 点击 Tooltip 外部区域关闭 Tooltip | Tooltip交互 |
| TC031 | Locations 无数据时显示空状态文案 | UI展示 |
| TC032 | Ads Breakdown 表格展示正确的列头 | UI展示 |
| TC052 | Ads Breakdown 无数据时显示空状态文案 | UI展示 |
| TC054 | 数据延迟更新提示文字展示 | UI展示 |
| TC055 | 多账号UID Account Switcher 显示所有关联账号 | 边界测试 |
| TC056 | 单账号UID Account Switcher 隐藏 | 边界测试 |
| TC058 | 页面在移动端 viewport 正常展示 | UI展示 |

### 按优先级分布

| 优先级 | 总数 | 可自动化 | 自动化率 |
|--------|------|---------|---------|
| P0 | 16 | 8 | 50% |
| P1 | 31 | 12 | 39% |
| P2 | 15 | 2 | 13% |

### 按模块分布

| 模块 | 用例数 | 可自动化 |
|------|-------|---------|
| 页面访问与权限控制 | 5 | 5 |
| 时间筛选器 | 5 | 3 |
| 核心指标卡片区 | 10 | 2 |
| Tooltip 交互 | 5 | 5 |
| Best Performing Locations | 6 | 1 |
| Ads Breakdown 表格 | 10 | 1 |
| 数据导出（Export） | 7 | 0 |
| 数据一致性 | 3 | 0 |
| 空状态处理 | 3 | 2 |
| 边界与异常场景 | 8 | 3 |

### 不可自动化原因分布

| 原因 | 涉及用例数 |
|------|----------|
| 依赖特定业务数据（账号无历史数据） | 18 |
| 属于鉴权/边界/异常/竞态场景 | 5 |
| 需要非Pro/多账号等特殊账号 | 0 |
| 埋点验证需后台工具配合 | 4 |
| 文件内容比对 | 3 |
| Tooltip 文案验证（脆断风险高） | 0 |
| 需要 DevTools/性能工具 | 3 |
| 跨页数据对比属于数据验证 | 3 |
| 跨浏览器/多环境 | 2 |
| 其他（需手动操作/可视化判断等） | 2 |

---

## ⚠️ 关键风险提示（测试重点）

1. **🔴 [D1] 默认时间范围** - 必须优先验证默认加载是 Last 7 days 还是 Last 30 days
2. **🔴 [D2] Live Ads 卡片缺失** - 需确认 Phase 2 是否要求独立指标卡片
3. **🔴 数据联动** - 时间筛选器切换后三个模块必须全部同步更新
4. **🔴 权限控制** - 非Pro账号绝对不能访问Dashboard
5. **🟠 导出数据一致性** - 导出文件数据与页面显示必须完全匹配
6. **🟠 Unique Replies 去重** - 3天窗口+同user/ad去重逻辑验证

---

## 📌 PRD 差距问题跟踪

| ID | 差距描述 | 严重度 | 状态 |
|----|---------|-------|------|
| D1 | 默认时间范围：PRD=Last 30 days，页面疑似Last 7 days | 🔴 高 | 待确认 |
| D2 | Live Ads 独立指标卡片未实现 | 🔴 高 | 待确认 |
| D3 | Ads Breakdown 列名：PRD=Impressions，页面=Search Views | 🟠 中 | 待确认 |
| D4 | 趋势徽章（Trend Badge）未实现 | 🟠 中 | 待确认 |
| D5 | 地理位置仅列表，无热力图 | 🟠 中 | 待确认 |
| D6 | 趋势图（Trend Graph）未显示 | 🟠 中 | 待确认 |
| D7 | 自定义日期范围未实现 | 🟠 中 | 待确认 |
| D8 | 单账号时 Account Switcher 隐藏（符合规范） | 🟢 正常 | 符合预期 |
| D9 | Tooltip 文案与 PRD 措辞略有差异 | 🟡 低 | 待确认 |
| D10 | Export 文件名约定 CSV vs XLSX 矛盾（PRD自身问题） | 🟡 低 | 待澄清 |
