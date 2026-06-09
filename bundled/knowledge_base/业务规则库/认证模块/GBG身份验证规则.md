# 认证模块 - GBG 身份验证业务规则

## 1. 功能概述
- **功能描述**: 用户可通过 GBG 第三方平台完成 ID 和 Business Verification，获得 "ID Verified" 认证徽章，在个人资料和广告中展示以提升可信度
- **用户角色**:
  - 未认证消费者账户（可发起认证）
  - 已认证 Pro/Business 账户（展示认证状态和 ID Verified 徽章）
  - 买家/游客（浏览时可看到卖家的 ID Verified 标识）
- **入口位置**: My Detail 页面（`/manage-account`）→ Verification 区域 → "Start verification" 按钮
- **依赖模块**: GBG Onboarding 第三方平台（`onboarding.gumtree.com`）、My Detail 模块、VIP 广告详情页、SRP 搜索结果页

## 2. 核心流程
### 2.1 主流程
1. 未认证用户登录 Gumtree 进入 My Detail 页面（`/manage-account`）
2. 确认 "My Details" 标签处于选中状态（`aria-selected="true"`）
3. 看到 Verification 区域标题 "Verification"
4. 看到引导文案："Complete ID and Business Verification to receive verification badges and stand out from competitors."
5. 看到 "Start verification" 按钮（可见且可点击）
6. 点击 "Start verification" 按钮
7. 系统打开新标签页，跳转到 GBG Onboarding 页面（URL 含 `onboarding`，页面标题含 "Welcome"）
8. 用户在 GBG 平台完成认证（确认注册详情 → 提供身份信息 → 上传支持文档）
9. 认证通过后，账户获得 "ID Verified" 徽章
10. 关闭 GBG 标签页后原 My Detail 页面状态正常

### 2.2 异常流程
- 认证中断（关闭 GBG 页面）→ 原 My Detail 页面 URL 仍为 `/manage-account`，Verification heading 仍可见，认证状态不变
- 认证失败（文档不合格）→ GBG 平台提示，需重新提交
- 已认证账户再次访问 Verification 区域 → 展示 "now verified" 状态 + "verification badge will show on your Ads"，不展示 Start 按钮

## 3. 业务规则
### 3.1 输入规则
| 字段 | 类型 | 必填 | 长度 | 格式 | 默认值 | 说明 |
|------|------|------|------|------|--------|------|
| 身份信息 | - | 是 | - | GBG 平台定义 | - | 在 GBG 第三方平台填写 |
| 支持文档 | File | 是 | - | GBG 平台定义 | - | 身份证明文档上传 |

### 3.2 校验规则
- 发起认证前必须已登录 Gumtree 账户
- GBG Onboarding URL 包含 `onboarding` 关键字
- GBG 页面标题必须包含 "Welcome"（用于验证跳转成功）
- 认证流程在 GBG 独立页面完成，Gumtree 不参与校验
- 关闭 GBG 标签页后原页面 URL 需保持 `/manage-account` 不变

### 3.3 权限规则
- 所有已登录用户均可在 My Detail 页面看到 Verification 区域
- 未认证用户：展示 "Start verification" 按钮（可见且可点击）
- 已认证用户：展示 "now verified" 状态文案 + "verification badge will show on your Ads"，`Start verification` 按钮不可见
- ID Verified 徽章对所有用户可见（包括未登录的买家/游客）

### 3.4 业务约束
- 验证流程在独立第三方页面（GBG Onboarding）完成，通过新标签页打开
- 验证通过后 "ID Verified" 徽章展示位置：
  - My Detail 页面 Verification 区域（"now verified" 状态）
  - VIP 广告详情页 Overview 区域（"ID Verified" 文本标识）
  - VIP 广告详情页卖家卡片（卖家名称可点击，链接 `/sellerads/`）
  - SRP 搜索结果页广告卡片（"ID Verified" 文本标识）
- VIP Overview 区域同时展示：
  - "ID Verified" 标识
  - "Operates in {地区}"（运营地点）
  - "Posting since/for {年限}"（注册年限）
  - 面包屑导航含 "Home" 链接
  - 广告标题（H1）
- SRP 广告卡片同时展示：
  - "ID Verified" 标识
  - "Operates in {地区}"（运营地点）
  - 服务分类标签（如 Training、Services、Dog Training、Computer Services）

## 4. 错误处理
| 错误码 | 错误信息 | 触发条件 | 用户提示 |
|--------|---------|---------|---------|
| - | GBG 页面加载失败 | 网络异常 | 新标签页显示加载错误 |
| - | 认证中断 | 用户关闭 GBG 页面 | 原 My Detail 页面状态不变 |
| - | 文档审核不通过 | GBG 审核失败 | GBG 平台提示重新提交 |

## 5. 已知问题
- GBG Onboarding 页面标题需包含 "Welcome"（用于验证跳转成功），标题格式可能随 GBG 平台更新变化
- GBG 认证结果的回调/状态同步机制待确认（产品侧）
- SRP 搜索广告名需精确匹配，模糊搜索可能导致无法定位目标广告卡片

## 6. 变更历史
| 日期 | 版本 | 变更内容 | 变更人 |
|------|------|----------|--------|
| 2026-04-15 | v1.0 | 初始版本，从 Web UI 测试用例提取（test_gbg_verification.py） | 知识库管理器 |
