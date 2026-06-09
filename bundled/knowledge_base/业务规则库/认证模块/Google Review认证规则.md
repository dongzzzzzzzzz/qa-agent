# 认证模块 - Google Review 认证业务规则

## 1. 功能概述
- **功能描述**: 允许 Pro/Business 卖家通过 Google OAuth 授权，将 Google Business Profile 的评分和评论同步展示到 Gumtree 个人资料页和所有广告中，提升买家信任度
- **用户角色**: Pro/Business 卖家（需拥有 Google Business Profile）
- **入口位置**:
  - My Ads 页面 → Google Review 推荐区域 → "Enable Google reviews" 按钮
  - My Detail 页面（`/manage-account#reviews`）→ Ratings 区域 → Google reviews toggle
- **依赖模块**: Google OAuth 2.0 授权、My Detail 模块、My Ads 模块、VIP 广告详情页、BRP 卖家档案页

## 2. 核心流程
### 2.1 主流程
1. 卖家登录 Gumtree 进入 My Ads 页面（`/manage/ads`）
2. 看到 Google Review 推荐区域：标题 "Show Google ratings & reviews on your profile" + 描述文案 + "Enable Google reviews" 按钮
3. 点击 "Enable Google reviews" 按钮
4. 跳转到 My Detail 页面 Ratings 区域（URL: `/manage-account#reviews`）
5. 看到 "Ratings" heading、"Google reviews" 标签、toggle 开关、说明文案
6. 点击 Google reviews toggle
7. 系统打开新标签页，跳转到 `accounts.google.com` 进行 OAuth 授权
8. 卖家在 Google 页面完成授权
9. 返回 Gumtree，toggle 状态更新为已开启
10. Google 评分和评论开始展示在卖家资料页和所有广告中

### 2.2 异常流程
- Google OAuth 授权取消 → toggle 状态不变（保持未开启），无错误提示
- Google OAuth 授权失败（网络异常） → 保持原状态，可重试
- Google 账号无 Business Profile → 授权成功但无评分数据展示

## 3. 业务规则
### 3.1 输入规则
| 字段 | 类型 | 必填 | 长度 | 格式 | 默认值 | 说明 |
|------|------|------|------|------|--------|------|
| Google reviews toggle | Boolean | 否 | - | 开/关 | 关（未选中） | 启用/禁用 Google 评价同步 |
| Google OAuth 授权 | OAuth 2.0 | 是（开启时） | - | Google 标准流程 | - | 需关联 Google Business Profile 的 Google 账号 |

### 3.2 校验规则
- 点击 toggle 前必须已登录 Gumtree 账户
- OAuth 授权必须使用与 Google Business Profile 关联的 Google 账号
- 点击 toggle 后系统在新标签页打开 `accounts.google.com`，主页面不跳转
- 授权成功后 toggle 状态自动更新为已开启

### 3.3 权限规则
- 仅 Pro/Business 卖家账户可见 Google Review 功能入口
- My Ads 推荐区域仅对未开启 Google Review 的卖家展示
- 已开启 Google Review 的账户，My Ads 推荐区域不再展示

### 3.4 业务约束
- 授权成功后，Google 评价将展示在以下页面：
  - My Detail 页面 Ratings 区域
  - VIP 广告详情页卖家卡片（评分值 + 评论数）
  - VIP 广告详情页 Reviews 区域（评论列表 + Powered by Google）
  - BRP 卖家档案页 → VIP 页面（用户旅程）
- 评分值格式：`X.X`（一位小数，满分 5.0，如 4.5）
- 评论数格式：`(N reviews)`（括号包裹）
- Reviews 区域标题格式：`Reviews (N)`（含评论总数）
- 评论日期格式：`DD Month YYYY`（如 15 April 2026）
- 评论区底部展示 "Powered by Google" 品牌标识
- 评论区展示 "provided by our partner, Google" 合作声明
- 评分详情展示 "out of 5"（满分说明）
- staging 环境 BRP/SRP listing 卡片不渲染 Google Review 评分区块（仅 VIP 层可见）

## 4. 错误处理
| 错误码 | 错误信息 | 触发条件 | 用户提示 |
|--------|---------|---------|---------|
| - | OAuth 授权取消 | 用户在 Google 页面取消授权 | toggle 状态不变，无错误提示 |
| - | OAuth 授权失败 | 网络异常或 Google 服务不可用 | 保持原状态，可重试 |
| - | 无评分数据 | Google Business Profile 无评论 | 开启成功但无评分/评论展示 |

## 5. 已知问题
- staging 环境 BRP/SRP listing 卡片不渲染 Google Review 评分区块（仅 VIP 层可见）
- Google OAuth 授权流程的取消/失败处理不在 My Detail 模块测试范围内（独立模块测试）

## 6. 变更历史
| 日期 | 版本 | 变更内容 | 变更人 |
|------|------|----------|--------|
| 2026-04-15 | v1.0 | 初始版本，从 Web UI 测试用例提取（test_google_review.py） | 知识库管理器 |
