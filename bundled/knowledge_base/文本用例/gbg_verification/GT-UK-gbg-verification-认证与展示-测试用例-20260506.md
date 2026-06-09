# Gumtree UK — GBG Identity Verification 认证与展示 测试用例

> **生成时间**: 2026-05-06  
> **测试范围**: GBG 身份认证入口（未认证账户 My Detail → Start verification → GBG Onboarding）与已认证展示（My Detail 已认证状态 + VIP 页 ID Verified + SRP 广告卡片 ID Verified）  
> **总用例数**: 5 条  
> **可自动化**: 5 条 (100%)

---

## 测试环境配置

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | uk | Gumtree UK |
| 站点名称 | 英国站 | |

**测试账号说明**：
- **未认证账户（TC001/TC002）**: `donnyproa@proton.me` / `Gumtree123!` — 消费者账户，未完成 GBG 身份认证，运行环境 zoidberg（`https://www.zoidberg.gumtree.io`）
- **已认证账户（TC003/TC004/TC005）**: `staging_pro@gumtree.com` / `Gumtree123!` — Pro/Business 账户，已完成 GBG 身份认证，运行环境 staging（`https://www.staging.gumtree.io`）

**注意事项**：
- 未认证账户和已认证账户在不同环境运行，脚本通过 `--env` 参数切换
- Pro 账户使用 `my.{env}.gumtree.io/login` 路径登录（非站内弹窗）
- Cookie 同意弹窗和 OneTrust 遮罩层需要处理，脚本已内置 `_handle_cookie_banner` 兼容

---

## 📑 目录

- [分组一：认证入口（TC001-TC002）](#分组一认证入口)
- [分组二：展示验证（TC003-TC005）](#分组二展示验证)

---

## 分组一：认证入口

### TC001: My Detail 页 Verification 区域展示（未认证账户）

#### 📋 前置条件
- 使用未认证账户登录（donnyproa@proton.me），环境 zoidberg
- 进入 My Detail（`/manage-account`）页面

#### 🎬 执行步骤
1. 验证页面 URL 包含 `/manage-account`
2. 验证 "My Details" 标签处于选中状态（`aria-selected="true"`）
3. 验证 "Verification" heading 可见
4. 验证 Verification 区域有引导描述文案（长度 > 20 字符）
5. 验证 "Start verification" 按钮可见且可点击（enabled）

#### ✅ 预期结果
- My Detail 页展示 Verification 区域，含标题、引导文案和 Start verification 按钮
- Start verification 按钮处于可用状态

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（case_id_GUMTREE_GBG_ENTRY_001）

---

### TC002: My Detail 页点击 Start verification 进入 GBG 认证流程（未认证账户）

#### 📋 前置条件
- 使用未认证账户登录（donnyproa@proton.me），环境 zoidberg
- 进入 My Detail（`/manage-account`）页面

#### 🎬 执行步骤
1. 验证 "Start verification" 按钮可见
2. 点击 "Start verification" 按钮
3. 验证弹出新标签页，URL 包含 `onboarding`
4. 验证新标签页标题包含 "Welcome"
5. 关闭 GBG 认证标签页
6. 验证原页面 URL 仍包含 `/manage-account` 且 Verification heading 可见

#### ✅ 预期结果
- 点击 Start verification 后弹出 GBG onboarding 认证页面（新标签页）
- GBG 页面 URL 含 `onboarding`，标题含 "Welcome"
- 关闭新标签页后原页面状态正常

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（case_id_GUMTREE_GBG_ENTRY_002）

---

## 分组二：展示验证

### TC003: My Detail 页已认证账户 Verification 状态展示

#### 📋 前置条件
- 使用已认证 Pro 账户登录（staging_pro@gumtree.com），环境 staging
- 进入 Manage my Ads 页面

#### 🎬 执行步骤
1. 导航到 My Detail（`/manage-account`）页面
2. 验证页面 URL 包含 `/manage-account`
3. 验证 "Verification" heading 可见
4. 验证已认证状态文案 "now verified" 可见
5. 验证文案 "verification badge will show on your Ads" 可见
6. 验证无 "Start verification" 按钮（已认证不应显示）

#### ✅ 预期结果
- 已认证账户的 My Detail 页展示 "now verified" 已认证状态
- 展示 badge 说明文案
- 不展示 Start verification 按钮

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（case_id_GUMTREE_GBG_DISPLAY_003）

---

### TC004: VIP 页面展示 ID Verified 认证标识及卖家信息（已认证账户）

#### 📋 前置条件
- 使用已认证 Pro 账户登录（staging_pro@gumtree.com），环境 staging
- 进入 Manage my Ads 页面

#### 🎬 执行步骤
1. 从 Manage my Ads 点击第一条广告进入 VIP 页
2. 验证广告标题（H1）展示且非空
3. 验证面包屑导航 "Home" 链接存在
4. 验证 "Overview" heading 可见
5. 验证 Overview 区域展示 "ID Verified" 标识
6. 验证 Overview 区域展示运营地点（"Operates in ..."）
7. 验证 Overview 区域展示注册年限（"Posting since/for ..."）
8. 验证卖家卡片名称可见（含 `/sellerads/` 链接）且非空

#### ✅ 预期结果
- VIP 页展示广告标题和面包屑导航
- Overview 区域展示 "ID Verified" 标识、运营地点、注册年限
- 卖家卡片展示卖家名称和档案链接

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（case_id_GUMTREE_GBG_DISPLAY_004）

---

### TC005: SRP 搜索结果展示 ID Verified 认证标识及广告信息（已认证账户）

#### 📋 前置条件
- 使用已认证 Pro 账户登录（staging_pro@gumtree.com），环境 staging
- 进入 Manage my Ads 页面

#### 🎬 执行步骤
1. 从 Manage my Ads 找到第一条广告的分类名称
2. 导航到首页，在搜索框输入广告名并回车
3. 验证到达搜索结果页（URL 含 `/search` 或 `/p/`）
4. 在搜索结果中定位含广告名和 "ID Verified" 的广告卡片（`article` 元素）
5. 验证该卡片展示广告名
6. 验证该卡片展示 "ID Verified" 标识
7. 验证该卡片展示运营地点（"Operates in ..."）
8. 验证该卡片展示服务分类标签（如 Training / Services / Dog Training 等）

#### ✅ 预期结果
- SRP 搜索结果中能定位到自己的广告卡片
- 卡片展示 "ID Verified" 标识、运营地点、服务分类标签

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（case_id_GUMTREE_GBG_DISPLAY_005）

---

## 测试统计

| 指标 | 值 |
|------|-----|
| 总用例数 | 5 |
| P0 | 5 |
| 可自动化 | 5 (100%) |
| 认证入口 | 2 |
| 展示验证 | 3 |
