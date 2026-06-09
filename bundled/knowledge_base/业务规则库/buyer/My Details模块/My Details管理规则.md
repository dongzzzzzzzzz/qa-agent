# My Details管理规则

## 1. 功能概述
- **功能描述**: My Details 是 Gumtree 的个人账户管理中心,提供用户信息展示与编辑、评价管理、密码修改、支付地址管理、简历上传、营销偏好设置和账户停用等功能
- **用户角色**: 已登录用户(买家/卖家通用)
- **入口位置**: 
  - 直接访问: `https://www.{site}.gumtree.io/manage-account`
  - 顶部导航 Menu → My Details
- **依赖模块**: 
  - 登录模块(前置认证)
  - 支付模块(支付管理跳转)
  - 地址模块(配送地址管理)
  - 认证模块(身份验证、Google Review)

## 2. 核心流程

### 2.1 主流程(个人信息管理)
1. 用户登录后访问 My Details 页面
2. 页面展示个人信息区域(头像、姓名、邮箱)
3. 用户可以查看和编辑联系信息(姓名、电话)
4. 用户可以修改密码
5. 用户可以管理支付方式和配送地址
6. 用户可以设置营销偏好
7. 用户可以查看个人主页(View Profile)

### 2.2 联系信息编辑流程
1. 点击 "Edit contact details" 按钮
2. 弹出编辑对话框,显示当前信息
3. 修改 First name、Last name、Contact number
4. 点击 "Save changes" 保存或点击 "Close" 取消
5. 保存时进行前端验证(非空、纯字母)
6. 验证通过后保存并关闭对话框

### 2.3 密码修改流程
1. 点击 "Edit password" 按钮
2. 弹出密码编辑对话框
3. 填写 Current password、New password、Confirm password
4. 三个字段均填写后 "Continue" 按钮激活
5. 提交后验证密码强度和一致性
6. 验证通过后更新密码并关闭对话框

### 2.4 异常流程
- 未登录访问 → 自动跳转到登录页,callback 指向 /manage-account
- 联系信息为空提交 → 显示验证错误,不保存
- First name 包含数字 → 显示错误提示 "Please use letters only, no numbers"
- 密码字段未全部填写 → Continue 按钮保持 disabled
- 页面刷新 → 用户保持登录状态,数据正常展示

## 3. 业务规则

### 3.1 输入规则

| 字段 | 类型 | 必填 | 格式 | 说明 |
|-----|------|------|------|------|
| First name | String | 是 | 纯字母,不允许数字 | 用户显示名称 |
| Last name | String | 是 | 纯字母,不允许数字 | 用户姓氏 |
| Contact number | String | 是 | 手机号格式 | 联系电话 |
| Current password | String | 是(修改密码时) | 任意非空 | 当前密码验证 |
| New password | String | 是(修改密码时) | 符合密码强度要求 | 新密码 |
| Confirm password | String | 是(修改密码时) | 与新密码一致 | 确认新密码 |

### 3.2 校验规则

**联系信息编辑**:
- First name 和 Last name 不能为空
- First name 和 Last name 只能包含字母,不允许数字
- Contact number 不能为空
- 提示文字: "Your first name will be your display name. Please use letters only, no numbers."

**密码编辑**:
- Current password、New password、Confirm password 均为空时,Continue 按钮 disabled
- 三个字段均填写后,Continue 按钮激活
- New password 必须符合密码强度要求(具体要求需补充)
- Confirm password 必须与 New password 一致

**营销偏好**:
- 复选框可切换,状态立即保存
- 刷新后状态保持

**CV上传**:
- 支持格式: Word、PDF、Richtext
- 最大文件大小: 6MB

### 3.3 权限规则

| 角色 | 操作 | 行为 |
|-----|------|------|
| 未登录访客 | 访问 /manage-account | 跳转到登录页,URL 包含 callback=/manage-account |
| 已登录用户 | 访问 /manage-account | 正常显示 My Details 页面 |
| 已登录用户 | 编辑个人信息 | 可编辑联系信息、密码、营销偏好 |
| 已登录用户 | 查看 View Profile | 可查看公开个人主页 |

### 3.4 业务约束

**页面结构**:
- 页面顶部显示个人信息卡片(头像、姓名、邮箱、View profile 链接)
- 各功能模块按顺序排列: Contact details → Ratings → Verification → Password → Payments → Delivery Addresses → Your CV → Marketing Preferences → Account

**编辑对话框规则**:
- 对话框标题明确标识功能(Contact details、Edit your password)
- 显示 "Save changes"/"Continue" 和 "Close" 按钮
- Close 按钮关闭对话框,不保存更改
- 验证错误时对话框不关闭,显示错误提示

**跳转规则**:
- Start verification → 新标签页打开 `onboarding.gumtree.com`
- Manage payment → 跳转 `/manage-payment`
- Manage address → 跳转 `/manage-postage`
- View profile → 跳转 `/profile/account/`
- 所有跳转页面均有 "Back" 链接返回 My Details

**评价系统**:
- Gumtree reviews: 显示星级和评价数量
- Google reviews: 可选复选框,说明文字 "Enable Google ratings and reviews on my profile and all my Ads."

**Tab切换**:
- My Details tab 为当前选中状态
- 可切换到 "Manage my Ads" 等其他 tab
- 切换后返回时页面状态保持

## 4. 错误处理

| 错误场景 | 触发条件 | 用户提示位置 | 提示文案 |
|---------|---------|------------|---------|
| 未登录访问 | 直接访问 /manage-account | 跳转登录页 | - |
| First name 为空 | 点击 Save changes 时字段为空 | 对话框内字段提示 | "This field is required" |
| First name 包含数字 | 输入包含数字后点击 Save | 对话框内字段提示 | "Please use letters only, no numbers" |
| 密码字段未全部填写 | 修改密码时 | Continue 按钮 | 按钮 disabled(灰色) |
| CV文件超大 | 上传超过6MB文件 | 文件上传区域 | "Max 6MB" |

## 5. 依赖模块

### 5.1 上游依赖(谁调用我)
- **登录模块**: 用户必须先登录才能访问 My Details
- **顶部导航**: Menu → My Details 入口
- **首页**: 已登录用户通过顶栏访问

### 5.2 下游依赖(我调用谁)
- **支付模块**: Manage payment 按钮跳转到支付管理页面 `/manage-payment`
- **地址模块**: Manage address 按钮跳转到地址管理页面 `/manage-postage`
- **认证模块**: Start verification 按钮跳转到身份验证流程 `onboarding.gumtree.com`
- **个人主页模块**: View profile 链接跳转到公开个人主页 `/profile/account/`

### 5.3 跨域交互说明
- **身份验证**: 点击 Start verification 打开新标签页,跳转到外部认证服务 `onboarding.gumtree.com`
- **Google Review**: 启用 Google reviews 可能涉及 Google API 集成
- **CV存储**: CV上传可能涉及文件存储服务

## 6. 已知问题

### 6.1 产品待确认问题
1. **密码强度要求**: 密码编辑对话框提示"密码强度要求",但具体要求未明确(长度、特殊字符等)
2. **Google Review功能**: 复选框的具体效果和Google API集成细节未确认
3. **CV上传成功状态**: 上传成功后的展示效果(文件名、删除按钮)未确认
4. **账户停用流程**: 点击 "Deactivate my account" 后的完整流程(确认对话框、停用效果)未确认
5. **Gumtree Reviews点击行为**: 点击评分按钮的具体行为(跳转评价页面或弹窗)待确认

### 6.2 技术风险
- 对话框编辑与页面刷新的状态同步问题
- 跨页面跳转后的 session 保持
- CV文件上传的文件类型和大小校验
- 营销偏好复选框的即时保存可靠性

## 7. 变更历史

| 日期 | 版本 | 变更内容 | 变更人 |
|-----|------|---------|--------|
| 2026-04-22 | v1.0 | 初始版本,基于 TC_My_Details测试用例.md(38条用例)归档 | AI Assistant |
