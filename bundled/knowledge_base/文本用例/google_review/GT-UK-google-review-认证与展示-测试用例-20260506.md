# Gumtree UK — Google Review 认证与展示 测试用例

> **生成时间**: 2026-05-06  
> **测试范围**: Google Review 认证流程（My Ads 入口 → My Detail toggle → Google OAuth）与展示验证（VIP 页评分/评论 + BRP→VIP 路径）  
> **总用例数**: 4 条  
> **可自动化**: 4 条 (100%)

---

## 测试环境配置

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | uk | Gumtree UK |
| 基础URL | https://www.zoidberg.gumtree.io | zoidberg 测试环境 |
| 站点名称 | 英国站 | |
| 角色 | seller | 普通卖家 |

**测试账号说明**：
- **认证账户（TC001/TC002）**: `donnyproa@proton.me` / `Gumtree123!` — 有权限开启 Google Review 认证，用于验证 My Ads 推荐区域和 My Detail toggle 流程
- **展示账户（TC003/TC004）**: `donny.han@gumtree.com` / `Gumtree123!` — 已开启 Google Review，用于验证 VIP 页面的评分和评论展示

**注意事项**：
- 展示账户的第一条广告 VIP 页可能没有卖家卡片（取决于广告类型），脚本会自动遍历所有广告找到含 `/sellerads/` 链接的那条
- Cookie 同意弹窗和 OneTrust 遮罩层需要处理，脚本已内置 `_handle_cookie_banner` 兼容

---

## 📑 目录

- [分组一：认证流程（TC001-TC002）](#分组一认证流程)
- [分组二：展示验证（TC003-TC004）](#分组二展示验证)

---

## 分组一：认证流程

### TC001: My Ads 页 Google Review 推荐区域展示并跳转至 My Detail

#### 📋 前置条件
- 使用认证账户登录（donnyproa@proton.me）
- 进入 Manage my Ads 页面

#### 🎬 执行步骤
1. 验证 My Ads 页 Google Review 推荐区域标题可见（"Show Google ratings & reviews on your profile"）
2. 验证推荐文案 "Let others see your ratings and reviews to build buyer confidence." 可见
3. 验证 "Enable Google reviews" 按钮可见
4. 点击 "Enable Google reviews" 按钮
5. 验证页面跳转到 My Detail 页，URL 包含 `/manage-account#reviews`
6. 验证 Ratings 标题可见
7. 验证 Google reviews 区域和 toggle 可见
8. 验证 Enable 说明文案 "Enable Google ratings and reviews on my profile and all my Ads." 可见

#### ✅ 预期结果
- My Ads 页展示 Google Review 推荐区域，含标题、文案、Enable 按钮
- 点击后跳转到 My Detail `#reviews` 锚点
- My Detail 页展示 Ratings 区域，含 Google reviews 标签、toggle 开关、Enable 说明文案

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（case_id_GUMTREE_GR_CERT_001）

---

### TC002: My Detail 页点击 Google reviews toggle 进入 Google 认证流程

#### 📋 前置条件
- 使用认证账户登录（donnyproa@proton.me）
- 进入 Manage my Ads 页面

#### 🎬 执行步骤
1. 导航到 My Detail `#reviews` 页面
2. 验证 Ratings 区域可见
3. 验证 Google reviews 标签可见
4. 验证 Enable 说明文案可见
5. 验证 toggle 开关可见
6. 点击 Google reviews toggle
7. 验证弹出新标签页，URL 包含 `accounts.google.com`（Google OAuth 认证页面）
8. 关闭 Google 认证标签页

#### ✅ 预期结果
- My Detail Ratings 区域展示 Google reviews toggle
- 点击 toggle 后弹出 Google OAuth 认证页面（accounts.google.com）
- 认证页面在新标签页打开，原页面不受影响

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（case_id_GUMTREE_GR_CERT_002）

---

## 分组二：展示验证

### TC003: VIP 页面展示 Google Review 评分与 Powered by Google 标识

#### 📋 前置条件
- 使用展示账户登录（donny.han@gumtree.com，已开启 Google Review）
- 进入 Manage my Ads 页面

#### 🎬 执行步骤
1. 从 My Ads 遍历广告，找到 VIP 页含 `/sellerads/` 卖家卡片链接的那条广告
2. 进入该广告的 VIP 页
3. 验证卖家卡片上展示评分值（如 4.5）
4. 验证卖家卡片上展示评论数（如 "(12 reviews)"）
5. 点击 Reviews 标签滚动到评论区
6. 验证 Reviews 标题含评论数（如 "Reviews (12)"）
7. 验证 Google 合作说明文案 "provided by our partner, Google" 可见
8. 验证评分详情区域展示 "out of 5"
9. 验证至少一条评论展示（含评论日期、"Powered by Google" 标识）

#### ✅ 预期结果
- VIP 页卖家卡片展示 Google Review 评分和评论数
- Reviews 区域展示 Google 合作说明、评分详情、评论列表
- 每条评论展示评论日期和 "Powered by Google" 标识

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（case_id_GUMTREE_GR_DISPLAY_003）

---

### TC004: BRP 卖家档案页路径 → VIP 展示 Google Review 评分

#### 📋 前置条件
- 使用展示账户登录（donny.han@gumtree.com，已开启 Google Review）
- 进入 Manage my Ads 页面

#### 🎬 执行步骤
1. 从 My Ads 找到含卖家卡片的广告 VIP 页，获取 `/sellerads/` 卖家档案链接
2. 导航到卖家档案页（BRP），验证页面有广告卡片
3. 从 BRP 遍历广告卡片，找到 VIP 页含卖家卡片的那条，点击进入（模拟买家发现路径）
4. 验证 VIP 页卖家卡片展示 Google Review 评分值
5. 验证 VIP 页卖家卡片展示评论数

#### ✅ 预期结果
- 从 VIP → BRP → VIP 的完整用户旅程通畅
- BRP 页展示广告卡片列表
- 经 BRP 进入的 VIP 页卖家卡片正确展示 Google Review 评分与评论数

**说明**: staging 环境 BRP/SRP listing 卡片不渲染 Google Review 评分区块，本用例验证 BRP→VIP 的完整路径，确认 VIP 层评分可见

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（case_id_GUMTREE_GR_DISPLAY_004）

---

## 测试统计

| 指标 | 值 |
|------|-----|
| 总用例数 | 4 |
| P0 | 4 |
| 可自动化 | 4 (100%) |
| 认证流程 | 2 |
| 展示验证 | 2 |
