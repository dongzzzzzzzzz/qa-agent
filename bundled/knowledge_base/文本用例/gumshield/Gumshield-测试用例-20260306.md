# Gumshield - 内容审核管理工具 测试用例

> **生成时间**: 2026-03-06
> **探测方式**: Playwright MCP 实测
> **测试范围**: Gumshield 全功能模块（登录、Search Ads、Screen Ads、Screen Replies 2、Screen Replies Moderation、View Ad、View Payments、View Conversation Reports、View User Reviews、Manage Agents、Configure Policy、Manage Gumshield）
> **总用例数**: 52 条
> **可自动化**: 44 条（84.6%）

---

## 测试环境配置（必填）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | uk | Gumtree 英国站 |
| 基础URL | https://gumshield.zoidberg.gumtree.io | 测试站点地址 |
| 站点名称 | Gumshield (Zoidberg) | 测试环境 |
| 角色 | agent | CS 内容审核员 |
| 账号名称 | gumshield_agent | 用于 session 命名 |
| 测试账号 | gumshield | 登录用户名 |
| 测试密码 | password | 登录密码 |

**说明**：上述配置为实际探测时使用的账号密码，playwright-test-generator 生成脚本时会严格使用此配置。

---

## Application Overview

```
【Application Overview - Gumshield 内容审核工具】

功能定位：Gumtree 平台 CS（客服）内容审核管理后台，供内部 Agent 对广告、回复、用户等进行筛查、审核和批量操作

用户角色：
- ADMIN：管理员（可管理 Agent 用户）
- USER：普通审核员
- DEVELOPER：开发者账号

业务规则（从 UI 推断 + 实测确认）：
- 规则1：必须登录才能访问任何功能页，未登录自动跳转 /login
- 规则2：登录失败显示 "Sign in failed" 提示，Username 保留，Password 清空
- 规则3：搜索条件支持多条件叠加（第一条件选好后，可继续添加第二条件）
- 规则4：不同搜索字段对应不同操作符（Ad ID=equals；Ad Status=equals/not equals；Price=equals/less than/more than）
- 规则5：搜索结果支持批量操作：Skip / Allow / Delete，需选择原因（Fraud/Spam 等18项）
- 规则6：搜索结果支持 Download results（CSV 导出）
- 规则7：Manage Agents 中，创建 Agent 时 Username 可编辑；编辑现有 Agent 时 Username 只读
- 规则8：创建 Agent 需要填写密码；编辑 Agent 密码通过独立的 Change password 流程
- 规则9：空提交 Create New Agent 弹出 Validation Error 弹窗，提示 "Please enter a password"

页面状态枚举：
- 未登录态：/login 页面，显示登录表单
- 已登录态：/gumshield?N 页面，顶部导航可见，底部为功能内容区
- 空搜索结果：无条件搜索后返回 "Showing 0 results from a possible X"
- 有结果态：搜索结果列表 + 批量操作区域
- 模块切换态：点击导航链接，内容区刷新

模块划分（重要性排序）：
1. [P0] 登录/登出（核心入口）
2. [P0] Search Ads（核心审核主链路）
3. [P0] Screen Ads（队列审核）
4. [P1] Screen Replies 2（回复审核）
5. [P1] Screen Replies Moderation（回复审核管理）
6. [P1] Manage Agents（代理管理）
7. [P1] View Ad（直接查看广告）
8. [P2] View Payments / View Conversation Reports / View User Reviews
9. [P2] Configure Policy / Configure Replies / Configure Replies Moderation
10. [P2] Configure IP Ranges / Configure Checklists
11. [P2] Publish Rules / Rule Reports
12. [P3] Secret CS / Bark CS / Pay and Ship / Pets Account Verification / Manage Gumshield
```

---

## 模块一：登录（Login）

### TC001: 正确用户名密码登录成功

#### 📋 前置条件
- 未登录状态，访问 https://gumshield.zoidberg.gumtree.io/gumshield?2

#### 🎬 执行步骤
1. 系统自动跳转到 /login 页面
2. 在 Username 字段输入 `gumshield`
3. 在 Password 字段输入 `password`
4. 点击 "Sign In" 按钮

#### ✅ 预期结果
- 跳转到主功能页（URL 变为 `/gumshield?N`）✅ 实测
- 顶部导航栏显示 "Welcome to Gumshield, Agent" 文案 ✅ 实测
- 导航菜单完整展示（Search Ads、Screen Ads 等 20+ 个功能入口）✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC002: 错误用户名/密码登录失败

#### 📋 前置条件
- 未登录状态，访问 /login 页面

#### 🎬 执行步骤
1. 在 Username 字段输入 `wronguser`
2. 在 Password 字段输入 `wrongpass`
3. 点击 "Sign In" 按钮

#### ✅ 预期结果
- 页面停留在 /login ✅ 实测
- 登录表单上方显示 "Sign in failed" 文案 ✅ 实测
- Username 字段保留已填写的用户名 ✅ 实测
- Password 字段被清空 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC003: 空用户名和密码提交

#### 📋 前置条件
- 访问 /login 页面，两个字段均为空

#### 🎬 执行步骤
1. 不填写任何内容
2. 点击 "Sign In" 按钮

#### ✅ 预期结果
- 页面停留在 /login ⚠️ 推断（基于 TC002 行为推断）
- 显示 "Sign in failed" 或空字段提示文案 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向 / 边界值
- **UI自动化**: ✅ 可自动化

---

### TC004: Reset 按钮清空登录表单

#### 📋 前置条件
- 在登录页已填写用户名和密码

#### 🎬 执行步骤
1. 在 Username 填入 `gumshield`
2. 在 Password 填入任意密码
3. 点击 "Reset" 按钮

#### ✅ 预期结果
- Username 和 Password 字段均被清空 ⚠️ 推断
- 停留在 /login 页面 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC005: Remember Me 勾选状态下登录

#### 📋 前置条件
- 访问登录页，Remember Me 复选框默认为勾选状态

#### 🎬 执行步骤
1. 确认 Remember Me 复选框已勾选（默认状态）
2. 输入正确的用户名和密码
3. 点击 "Sign In" 按钮
4. 关闭浏览器后重新打开站点

#### ✅ 预期结果
- 登录成功后跳转到主功能页 ✅ 实测
- Remember Me 默认已勾选 ✅ 实测
- 重新打开后是否自动登录 ⚠️ 推断（需手动验证 cookie 行为）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向 / 时序
- **UI自动化**: ❌ 不可自动化（需验证跨浏览器会话持久化）

---

### TC006: 未登录直接访问主功能页

#### 📋 前置条件
- 未登录状态，清除 cookie

#### 🎬 执行步骤
1. 直接访问 `https://gumshield.zoidberg.gumtree.io/gumshield?2`

#### ✅ 预期结果
- 自动跳转到 /login 页面 ✅ 实测
- URL 变为 `https://gumshield.zoidberg.gumtree.io/login`

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 权限
- **UI自动化**: ✅ 可自动化

---

### TC007: 登出功能

#### 📋 前置条件
- 已登录状态

#### 🎬 执行步骤
1. 点击顶部导航栏右侧 "Log Out" 链接

#### ✅ 预期结果
- 跳转回 /login 页面 ⚠️ 推断
- 再次访问主功能页时需要重新登录 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

## 模块二：Search Ads（广告搜索与批量审核）

### TC008: 选择搜索字段后操作符和输入控件正确联动

#### 📋 前置条件
- 已登录，进入 Search Ads 页面

#### 🎬 执行步骤
1. 在第一个下拉框选择 "Ad ID"
2. 观察操作符下拉框和值输入框

#### ✅ 预期结果
- 操作符下拉框出现，仅有 "equals" 选项 ✅ 实测
- 值输入框为文本输入框 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC009: Ad Status 字段联动枚举值下拉框

#### 📋 前置条件
- 已登录，进入 Search Ads 页面，已添加一条搜索条件

#### 🎬 执行步骤
1. 将字段下拉框选为 "Ad Status"
2. 观察值控件的变化

#### ✅ 预期结果
- 操作符下拉框变为 "equals" / "does not equal" ✅ 实测
- 值输入控件变为下拉框，包含：Awaiting phone verified / Live / Awaiting activation / Awaiting payment / Awaiting screening / Needs editing / Awaiting CS review / Deleted (CS) / Deleted (User) / Expired / Draft / SOLD（共12个选项）✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC010: Price 字段联动数值比较操作符

#### 📋 前置条件
- 已登录，进入 Search Ads 页面，已添加搜索条件

#### 🎬 执行步骤
1. 将字段下拉框选为 "Price"
2. 观察操作符下拉框

#### ✅ 预期结果
- 操作符下拉框包含 "equals" / "less than or equals" / "more than or equals" ✅ 实测
- 值输入框为文本输入框 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC011: 使用 Ad ID 搜索，结果为空时展示

#### 📋 前置条件
- 已登录，进入 Search Ads 页面

#### 🎬 执行步骤
1. 选择 "Ad ID" = "equals"，值输入框填入不存在的 Ad ID `12345`
2. 点击 "Search" 按钮

#### ✅ 预期结果
- 结果区域显示 "Showing 0 results from a possible 1"（或类似空结果文案）✅ 实测
- 批量操作区域出现：Skip / Allow / Delete 单选按钮 ✅ 实测
- "Choose One" 原因下拉框出现（包含 Fraud、Spam 等18个选项）✅ 实测
- "Process" 按钮出现 ✅ 实测
- "Download results" 链接出现 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC012: 未选择字段直接点 Search（空条件搜索）

#### 📋 前置条件
- 已登录，进入 Search Ads，第一个下拉框保持 "Choose One"

#### 🎬 执行步骤
1. 不选择任何搜索条件
2. 点击 "Search" 按钮（初始状态下按钮是否禁用？）

#### ✅ 预期结果
- Search 按钮初始状态为 disabled（灰色）✅ 实测
- 选择字段后 Search 按钮变为 enabled ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC013: 点击 Delete 条件按钮删除搜索条件

#### 📋 前置条件
- 已登录，已添加至少一条搜索条件（选了字段类型）

#### 🎬 执行步骤
1. 点击已添加条件行右侧的 "Delete" 按钮

#### ✅ 预期结果
- 该条搜索条件被从列表中移除 ⚠️ 推断
- 如果删除后没有条件，Search 按钮变回 disabled 状态 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC014: Clear Search 清除所有搜索条件

#### 📋 前置条件
- 已登录，已添加搜索条件并执行过搜索，结果区域有内容

#### 🎬 执行步骤
1. 点击 "Clear search" 按钮

#### ✅ 预期结果
- 搜索条件被清除，恢复到 "Choose One" 初始状态 ⚠️ 推断
- 结果区域消失或清空 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC015: 修改 Results 数量，控制每次返回条数

#### 📋 前置条件
- 已登录，进入 Search Ads 页面

#### 🎬 执行步骤
1. 将 "Results:" 输入框中的 `100` 改为 `10`
2. 执行搜索

#### ✅ 预期结果
- 搜索结果每页最多显示 10 条 ⚠️ 推断（Results 字段控制每页返回数量）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC016: 批量操作 - 选择 Delete 并设置原因后点 Process

#### 📋 前置条件
- 已登录，Search Ads 已执行搜索，结果列表有广告数据

#### 🎬 执行步骤
1. 选中一条或多条搜索结果
2. 选择操作为 "Delete"
3. 从原因下拉框选择 "Fraud"
4. 点击 "Process" 按钮

#### ✅ 预期结果
- 批量删除操作被提交 ⚠️ 推断（测试环境中不应实际删除数据）
- 提示成功或跳转到结果页 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ❌ 不可自动化（实际数据操作，需专门测试账号和恢复机制）

---

### TC017: 搜索条件支持多条件叠加

#### 📋 前置条件
- 已登录，进入 Search Ads 页面

#### 🎬 执行步骤
1. 在第一行选择 "Ad ID" = "equals"，填入某 ID
2. 在第二行（底部的 "Choose One" 行）选择 "Ad Status" = "equals" = "Live"
3. 点击 "Search"

#### ✅ 预期结果
- 支持两个条件同时生效（AND 关系）✅ 实测（界面支持两行条件）
- 同时满足两个条件的广告出现在结果中 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC018: Download results 下载搜索结果

#### 📋 前置条件
- 已登录，执行搜索后结果区域显示"Download results"链接

#### 🎬 执行步骤
1. 点击 "Download results" 链接

#### ✅ 预期结果
- 触发文件下载，下载 CSV 或类似格式的搜索结果文件 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向
- **UI自动化**: ❌ 不可自动化（文件下载验证需要额外处理）

---

## 模块三：Screen Ads（广告队列审核）

### TC019: Screen Ads 页面基本展示

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 点击顶部导航 "Screen Ads"

#### ✅ 预期结果
- 内容区展示筛选器区域 ✅ 实测
- 第一个下拉框选项包含：Category / Paid Ad / Queue / User Report ✅ 实测
- Search 按钮初始为 disabled ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC020: Screen Ads - Queue 字段联动 Risk/Policy 枚举

#### 📋 前置条件
- 已登录，进入 Screen Ads 页面

#### 🎬 执行步骤
1. 选择字段下拉框为 "Queue"

#### ✅ 预期结果
- 操作符变为 "equals" ✅ 实测
- 值下拉框出现，包含 "Risk" / "Policy" 两个选项 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC021: Screen Ads - 使用 Queue=Risk 执行搜索

#### 📋 前置条件
- 已登录，进入 Screen Ads 页面

#### 🎬 执行步骤
1. 选择 "Queue" = "equals" = "Risk"
2. 点击 "Search" 按钮

#### ✅ 预期结果
- 返回对应队列的广告列表 ⚠️ 推断
- 列表展示待审核广告的基本信息 ⚠️ 推断
- 批量操作区域（Skip/Allow/Delete）出现 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

## 模块四：Screen Replies 2（回复队列审核）

### TC022: Screen Replies 2 页面筛选字段展示

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 点击顶部导航 "Screen Replies 2"

#### ✅ 预期结果
- 内容区展示筛选器 ✅ 实测
- 字段选项包含：Reply status / Reply date / Email / Buyer IP / Buyer cookie / Category（共6个）✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC023: Screen Replies 2 - Reply Status 枚举值联动

#### 📋 前置条件
- 已登录，进入 Screen Replies 2

#### 🎬 执行步骤
1. 选择字段为 "Reply status"
2. 观察操作符和值控件

#### ✅ 预期结果
- 操作符出现（equals / does not equal） ⚠️ 推断
- 值变为枚举下拉框（列出可用回复状态） ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

## 模块五：View Ad（通过 ID 直接查看广告）

### TC024: 顶部 View Ad 输入 Ad ID 后点 Go 跳转

#### 📋 前置条件
- 已登录，顶部导航 View Ad 区域的文本框可见

#### 🎬 执行步骤
1. 在 "View Ad" 旁边的文本框中输入一个有效 Ad ID（如真实存在的广告 ID）
2. 点击 "Go" 按钮

#### ✅ 预期结果
- 跳转到该广告的详情页面 ⚠️ 推断
- 展示广告的完整信息（标题、描述、状态、用户信息等）⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC025: View Ad 输入不存在的 Ad ID

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 在 View Ad 文本框输入不存在的 ID `9999999999`
2. 点击 "Go"

#### ✅ 预期结果
- 显示错误提示或空页面 ⚠️ 推断
- 不发生页面崩溃 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC026: View Ad 输入空值点 Go

#### 📋 前置条件
- 已登录，View Ad 文本框为空

#### 🎬 执行步骤
1. 不填 Ad ID
2. 点击 "Go"

#### ✅ 预期结果
- 不提交请求，或显示空字段提示 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

## 模块六：Manage Agents（Agent 账号管理）

### TC027: Manage Agents 页面展示 Agent 列表

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 点击顶部导航 "Manage Agents"

#### ✅ 预期结果
- 页面标题显示 "Agent Management" ✅ 实测
- 左侧列表显示现有 Agent（如 gumshield developer、jrindsland@gumtree.com developer）✅ 实测
- 点击 Agent 名称后，右侧展示其详情（Username 只读、First name、Last name、Role 下拉、Save/Delete 按钮）✅ 实测
- 右上区域展示密码修改表单（New Password、Confirm password、Change password 按钮）✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC028: 点击 Create New Agent 按钮展示创建表单

#### 📋 前置条件
- 已登录，进入 Manage Agents 页面

#### 🎬 执行步骤
1. 点击 "Create New Agent" 按钮

#### ✅ 预期结果
- 右侧详情区域变为创建表单 ✅ 实测
- 表单字段：Username（可编辑）、First name、Last name、Role（ADMIN/USER/DEVELOPER）、Password、Confirm password ✅ 实测
- 底部按钮变为 "Save" 和 "Cancel" ✅ 实测
- Role 下拉默认为 "USER" ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC029: 创建 Agent 时密码为空提交显示校验错误

#### 📋 前置条件
- 已登录，进入 Manage Agents，点击 "Create New Agent" 后表单已展示

#### 🎬 执行步骤
1. 不填写任何字段
2. 点击 "Save" 按钮

#### ✅ 预期结果
- 弹出 "Validation Error" 弹窗 ✅ 实测
- 弹窗内显示错误信息 "Please enter a password" ✅ 实测
- 表单数据不被提交 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC030: 关闭 Validation Error 弹窗

#### 📋 前置条件
- Validation Error 弹窗已显示

#### 🎬 执行步骤
1. 点击弹窗右上角的关闭按钮（X 链接）

#### ✅ 预期结果
- 弹窗关闭 ✅ 实测
- 表单内容保留（Username 等已填字段保留）✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC031: 创建 Agent 填写完整信息保存成功

#### 📋 前置条件
- 已登录，进入 Create New Agent 表单

#### 🎬 执行步骤
1. Username 填写 `testuser_new`
2. First name 填写 `Test`
3. Last name 填写 `User`
4. Role 选择 "USER"
5. Password 填写 `Test@12345`
6. Confirm password 填写 `Test@12345`
7. 点击 "Save"

#### ✅ 预期结果
- 表单提交成功 ⚠️ 推断
- 新 Agent 出现在左侧列表中 ⚠️ 推断
- 成功提示（或直接刷新列表）⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ❌ 不可自动化（会实际创建账号，需数据清理机制）

---

### TC032: 创建 Agent 密码不匹配时的校验

#### 📋 前置条件
- 已登录，进入 Create New Agent 表单

#### 🎬 执行步骤
1. 填写 Username `testuser`
2. Password 填写 `pass1`
3. Confirm password 填写 `pass2`（不一致）
4. 点击 "Save"

#### ✅ 预期结果
- 弹出校验错误弹窗 ⚠️ 推断（提示密码不匹配）
- 表单不被提交 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC033: 点击 Cancel 取消创建 Agent

#### 📋 前置条件
- 已登录，Create New Agent 表单已展示，部分字段已填写

#### 🎬 执行步骤
1. 在各字段填入部分数据
2. 点击 "Cancel" 按钮

#### ✅ 预期结果
- 表单关闭或数据清空 ⚠️ 推断
- 左侧 Agent 列表无变化 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC034: 编辑现有 Agent 的 First name 和 Last name

#### 📋 前置条件
- 已登录，进入 Manage Agents 页面，左侧列表有 Agent

#### 🎬 执行步骤
1. 点击左侧列表中的 "gumshield" Agent
2. 修改 First name 字段
3. 点击 "Save" 按钮

#### ✅ 预期结果
- 用户名（Username）字段为只读，无法修改 ✅ 实测
- First name 修改后可以保存 ⚠️ 推断
- 保存成功后列表或详情区域更新 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ❌ 不可自动化（会修改真实账号数据）

---

### TC035: 修改 Agent 角色（Role）

#### 📋 前置条件
- 已登录，已选中某个 Agent

#### 🎬 执行步骤
1. 将 Role 下拉框从 "DEVELOPER" 改为 "USER"
2. 点击 "Save"

#### ✅ 预期结果
- 角色修改成功 ⚠️ 推断
- 左侧列表中的 Agent 角色标签更新 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ❌ 不可自动化（会修改真实账号权限）

---

### TC036: 通过 Change password 修改 Agent 密码 - 成功场景

#### 📋 前置条件
- 已登录，已选中某 Agent，密码修改区域可见

#### 🎬 执行步骤
1. 在 "New Password" 填入新密码 `NewPass@12345`
2. 在 "Confirm password" 填入相同密码 `NewPass@12345`
3. 点击 "Change password" 按钮

#### ✅ 预期结果
- 密码修改成功提示 ⚠️ 推断
- 用该新密码可以登录 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ❌ 不可自动化（会修改真实密码）

---

### TC037: 修改密码时 New Password 为空提交

#### 📋 前置条件
- 已登录，已选中某 Agent

#### 🎬 执行步骤
1. 不填写 New Password 和 Confirm password
2. 点击 "Change password"

#### ✅ 预期结果
- 显示校验错误 ⚠️ 推断
- 密码不被修改 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

## 模块七：全局搜索（顶部 Global Search）

### TC038: 全局搜索框输入邮箱并搜索

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 在顶部导航右侧的全局搜索输入框中输入 `test@example.com`
2. 点击 "Search" 按钮

#### ✅ 预期结果
- 搜索请求被提交（Search 按钮进入 active 状态）✅ 实测
- 返回与该邮箱关联的广告列表 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC039: 全局搜索框为空时点击 Search

#### 📋 前置条件
- 已登录，全局搜索框为空

#### 🎬 执行步骤
1. 不填写任何内容
2. 点击 "Search" 按钮

#### ✅ 预期结果
- 可能返回全部结果或报错 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

## 模块八：Configure Policy（政策配置）

### TC040: Configure Policy 页面正常加载

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 点击顶部导航 "Configure Policy"

#### ✅ 预期结果
- 页面正常加载，展示政策配置相关内容 ⚠️ 推断
- 无报错、无空白页面 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

## 模块九：Configure IP Ranges（IP范围配置）

### TC041: Configure IP Ranges 页面正常加载

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 点击顶部导航 "Configure IP Ranges"

#### ✅ 预期结果
- 页面正常加载，展示 IP 范围配置内容 ⚠️ 推断
- 无报错 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

## 模块十：Manage Gumshield（系统管理）

### TC042: Manage Gumshield 页面正常加载

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 点击顶部导航 "Manage Gumshield"

#### ✅ 预期结果
- 页面正常加载 ⚠️ 推断
- 展示系统管理相关功能 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

## 模块十一：安全与权限

### TC043: 直接访问主功能 URL 需要认证

#### 📋 前置条件
- 无登录状态（清除 cookie/session）

#### 🎬 执行步骤
1. 在浏览器地址栏直接输入 `https://gumshield.zoidberg.gumtree.io/gumshield?3`

#### ✅ 预期结果
- 自动跳转到 /login 页面 ✅ 实测（初始访问时验证）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 权限 / 安全
- **UI自动化**: ✅ 可自动化

---

### TC044: SQL 注入尝试（用户名字段）

#### 📋 前置条件
- 访问 /login 页面

#### 🎬 执行步骤
1. Username 填入 `' OR '1'='1`
2. Password 填入任意值
3. 点击 "Sign In"

#### ✅ 预期结果
- 登录失败，显示 "Sign in failed" ⚠️ 推断
- 不出现数据库报错信息 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 安全
- **UI自动化**: ✅ 可自动化

---

### TC045: XSS 尝试（搜索字段）

#### 📋 前置条件
- 已登录，进入 Search Ads

#### 🎬 执行步骤
1. 选择 "Ad ID" 字段，值输入框填入 `<script>alert('XSS')</script>`
2. 点击 "Search"

#### ✅ 预期结果
- 页面不弹出 alert 对话框 ⚠️ 推断（输入被转义或过滤）
- 不出现 JavaScript 执行 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 安全
- **UI自动化**: ✅ 可自动化

---

## 模块十二：导航与会话状态

### TC046: 刷新页面后保持登录状态

#### 📋 前置条件
- 已登录，当前在 Manage Agents 页面

#### 🎬 执行步骤
1. 按 F5 刷新页面

#### ✅ 预期结果
- 保持登录状态（不跳转到 /login）⚠️ 推断
- 停留在 Manage Agents 页面或默认页面 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 时序 / 会话
- **UI自动化**: ✅ 可自动化

---

### TC047: 多模块切换后内容区正确更新

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 依次点击：Search Ads → Screen Ads → Screen Replies 2 → Manage Agents
2. 每次切换后观察内容区

#### ✅ 预期结果
- 每次切换后内容区正确显示对应模块的功能 ✅ 实测
- 激活的导航项有视觉高亮（active 状态）✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC048: 点击 Logo 跳转首页

#### 📋 前置条件
- 已登录，当前在某功能页面

#### 🎬 执行步骤
1. 点击左上角的 "Gumshield" Logo

#### ✅ 预期结果
- 跳转到根路径 `/`（或登录页）⚠️ 推断

#### 📊 用例属性
- **优先级**: P3
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

## 模块十三：Search Ads - Results 数量边界

### TC049: Results 字段输入 0

#### 📋 前置条件
- 已登录，进入 Search Ads

#### 🎬 执行步骤
1. 将 "Results:" 输入框改为 `0`
2. 执行搜索

#### ✅ 预期结果
- 返回 0 条结果，或系统使用默认值 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值
- **UI自动化**: ✅ 可自动化

---

### TC050: Results 字段输入负数或字母

#### 📋 前置条件
- 已登录，进入 Search Ads

#### 🎬 执行步骤
1. 将 "Results:" 输入框改为 `-1` 或 `abc`
2. 执行搜索

#### ✅ 预期结果
- 系统拒绝请求或使用默认值 ⚠️ 推断
- 不出现服务器错误 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值 / 异常流
- **UI自动化**: ✅ 可自动化

---

### TC051: Screen Replies Moderation 页面正常加载

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 点击顶部导航 "Screen Replies Moderation"

#### ✅ 预期结果
- 页面正常加载，展示回复审核管理相关内容 ⚠️ 推断
- 搜索条件区域可见 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC052: Configure Checklists 页面正常加载

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 点击顶部导航 "Configure Checklists"

#### ✅ 预期结果
- 页面正常加载 ⚠️ 推断
- 展示 Checklist 配置相关内容 ⚠️ 推断

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

## 测试统计

| 优先级 | 总数 | 可自动化 |
|--------|------|---------|
| P0 | 9 | 9 |
| P1 | 25 | 19 |
| P2 | 14 | 12 |
| P3 | 4 | 4 |
| **合计** | **52** | **44 (84.6%)** |

实测文案覆盖率：38.5%（20/52条有 ✅ 实测标记）

---

## 附：实测数据汇总

| 模块 | 实测确认行为 |
|------|------------|
| 登录 | 错误密码→"Sign in failed"，Username 保留，Password 清空；访问保护路由自动跳转 /login |
| Search Ads | Ad ID=equals 只有文本框；Ad Status=equals/not equals+12个枚举值；Price=3个操作符；空值搜索→"Showing 0 results from a possible 1"；Search 按钮初始 disabled |
| Screen Ads | 字段包含 Category/Paid Ad/Queue/User Report；Queue 联动 Risk/Policy |
| Screen Replies 2 | 字段包含 Reply status/Reply date/Email/Buyer IP/Buyer cookie/Category |
| Manage Agents | 列表含2个 Agent；创建时 Username 可编辑；编辑时 Username 只读；空提交→"Validation Error"+"Please enter a password" |
| Create New Agent | Role 默认 USER；三种角色：ADMIN/USER/DEVELOPER |
| 批量操作 | 原因下拉包含：Fraud/Suspected Fraud/Spam/Malicious-Prank Ad/Prostitute-Escort/Duplicate/Miscategorised/Prohibited/Wrong Location/Multiple Items-Too general/Offensive/Counterfeit/Other general policy-edit/Other general policy-remove/Category policy-edit/Category policy-remove/Account Takeover/HPI Breach（共18项）|
