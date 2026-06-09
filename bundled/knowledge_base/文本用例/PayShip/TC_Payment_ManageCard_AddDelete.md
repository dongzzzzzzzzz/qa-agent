# Gumtree - 支付卡管理（添加 & 删除）测试用例

> **生成时间**: 2026-05-15
> **探测方式**: Playwright MCP 实测
> **测试范围**: manage-payment 页面 — 新增银行卡（表单校验 + 成功添加）、删除银行卡（二次确认流程）
> **总用例数**: 12 条
> **可自动化**: 12 条（100%）

---

## 测试环境配置（必填）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | gaga | Gumtree gaga 环境 |
| 基础URL | https://www.gaga.gumtree.io | 测试站点地址 |
| 站点名称 | Gumtree GAGA | 测试环境 |
| 角色 | buyer | 已登录买家账号 |
| 账号名称 | fzoe4955_gaga | 用于 session 命名，必须唯一 |
| 测试账号 | fzoe4955@gmail.com | 登录邮箱 |
| 测试密码 | Yesung1106$ | 登录密码 |
| 目标页面 | /manage-payment | 支付方式管理页 |

**说明**：上述配置为实际探测时使用的账号密码，playwright-test-generator 生成脚本时会严格使用此配置。

---

## 整体前置条件

### 验证登录账号正确性

#### 📋 操作步骤
1. 使用账号 `fzoe4955@gmail.com` / `Yesung1106$` 登录
2. 访问 https://www.gaga.gumtree.io/manage-account

#### ✅ 验证点
- 页面显示用户名 "Fu Zoe" ✅ 实测
- 页面显示邮箱 `fzoe4955@gmail.com` ✅ 实测
- "My Details" tab 处于选中状态 ✅ 实测

> 上述验证通过后，方可继续执行以下测试用例。

---

## 核心流程（正向）

### TC001: 已登录用户成功访问支付管理页并查看已有卡列表

#### 📋 前置条件
- 已完成整体前置条件验证（账号为 fzoe4955@gmail.com）
- 访问 https://www.gaga.gumtree.io/manage-payment

#### 🎬 执行步骤
1. 登录后直接导航至 /manage-payment

#### ✅ 预期结果
- 页面标题区域显示 "Payment methods" ✅ 实测
- 已存在的银行卡以列表形式展示，每张卡显示卡组织 logo（如 VISA）和末四位数字（如 "VISA, ending in 1119"）✅ 实测
- 每张卡右侧有删除图标 ✅ 实测
- 页面底部有 "Add new card" 按钮 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC002: 点击 Add new card 弹出添加卡表单弹窗

#### 📋 前置条件
- 已登录，已进入 /manage-payment 页面

#### 🎬 执行步骤
1. 点击 "Add new card" 按钮

#### ✅ 预期结果
- 弹窗弹出，标题为 "Card details" ✅ 实测
- 弹窗显示提示文案 "Your payment details are secure and won't be shared with sellers" ✅ 实测
- 弹窗展示 VISA 和 MASTERCARD 卡组织 logo ✅ 实测
- 表单包含以下字段：Card holder's name（placeholder: Enter your full name）、Card number（placeholder: e.g. 1234 1234 1234 1234）、Expiry date (MM/YY)（placeholder: MM/YY）、Security code（placeholder: e.g. 123）✅ 实测
- 弹窗底部有 "Save card details" 按钮和右上角 "Close" 按钮 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC003: 所有字段为空直接点击 Save card details — 四个字段同时报错

#### 📋 前置条件
- 已登录，已打开 Add new card 弹窗，所有字段未填写任何内容

#### 🎬 执行步骤
1. 不填写任何字段，直接点击 "Save card details"

#### ✅ 预期结果
- 弹窗保持展开，提交被阻断 ✅ 实测
- Card holder's name 字段下方显示错误文案 `Full name can't be blank` ✅ 实测
- Card number 字段下方显示错误文案 `Please enter a valid card number` ✅ 实测
- Expiry date (MM/YY) 字段下方显示错误文案 `Please enter a valid expiry date` ✅ 实测
- Security code 字段下方显示错误文案 `Please enter a valid security code` ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC004: 填写有效测试卡信息后点击 Save card details 添加成功

#### 📋 前置条件
- 已登录，已打开 Add new card 弹窗

#### 🎬 执行步骤
1. 在 Card holder's name 填写 `Zoe Ui`
2. 在 Card number 填写 `4970107111111119`
3. 在 Expiry date (MM/YY) 填写 `0930`
4. 在 Security code 填写 `123`
5. 点击 "Save card details"

#### ✅ 预期结果
- 弹窗关闭 ✅ 实测
- 支付方式列表新增一张 "VISA, ending in 1119" 的卡 ✅ 实测
- 无错误提示，页面停留在 /manage-payment ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

## 表单校验（负向 / 边界）

### TC005: Card number 填写格式无效（位数不足）— 仅 Card number 字段报错

#### 📋 前置条件
- 已登录，已打开 Add new card 弹窗

#### 🎬 执行步骤
1. Card holder's name 填写 `Zoe Ui`
2. Card number 填写 `1234`（位数不足）
3. Expiry date 填写 `0930`
4. Security code 填写 `123`
5. 点击 "Save card details"

#### ✅ 预期结果
- 弹窗保持展开，提交被阻断 ✅ 实测
- 仅 Card number 字段下方显示 `Please enter a valid card number` ✅ 实测
- Card holder's name、Expiry date、Security code 无错误提示 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向 / 边界值
- **UI自动化**: ✅ 可自动化

---

### TC006: Expiry date 填写已过期日期（0120）— 表单级错误提示

#### 📋 前置条件
- 已登录，已打开 Add new card 弹窗

#### 🎬 执行步骤
1. Card holder's name 填写 `Zoe Ui`
2. Card number 填写 `4970107111111119`
3. Expiry date 填写 `0120`（2020年1月，已过期）
4. Security code 填写 `123`
5. 点击 "Save card details"

#### ✅ 预期结果
- 弹窗保持展开，提交被阻断 ✅ 实测
- 字段下方无单独错误文案，而是在 "Save card details" 按钮下方显示表单级错误提示：`Card Details Incorrect - please check your details or try another payment card` ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向 / 边界值
- **UI自动化**: ✅ 可自动化

---

## 弹窗交互

### TC007: 点击 Close 按钮关闭 Add new card 弹窗 — 数据不保存

#### 📋 前置条件
- 已登录，已打开 Add new card 弹窗，已填入部分数据

#### 🎬 执行步骤
1. 在 Card holder's name 填写 `Test User`
2. 点击弹窗右上角 "Close" 按钮

#### ✅ 预期结果
- 弹窗关闭 ✅ 实测
- 卡列表无新增记录，列表总数不变 ✅ 实测
- 页面停留在 /manage-payment ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

## 危险操作（删除银行卡）

### TC008: 点击卡片删除图标弹出二次确认弹窗

#### 📋 前置条件
- 已登录，/manage-payment 页面，已有至少一张银行卡

#### 🎬 执行步骤
1. 点击某张银行卡右侧的删除图标

#### ✅ 预期结果
- 出现确认弹窗，标题为 `Are you sure?` ✅ 实测
- 弹窗正文显示 `You won't be able to undo this action.` ✅ 实测
- 弹窗包含 `Yes, delete` 和 `No, cancel` 两个按钮 ✅ 实测
- 弹窗右上角有 `Close` 按钮 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC009: 点击 Yes, delete 确认删除银行卡 — 删除成功

#### 📋 前置条件
- 已登录，/manage-payment 页面，删除确认弹窗已弹出

#### 🎬 执行步骤
1. 在确认弹窗中点击 "Yes, delete"

#### ✅ 预期结果
- 弹窗关闭 ✅ 实测
- 该张银行卡从列表中消失，列表总数减少 1 ✅ 实测
- 页面停留在 /manage-payment ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC010: 点击 No, cancel 取消删除 — 卡数据保留

#### 📋 前置条件
- 已登录，/manage-payment 页面，删除确认弹窗已弹出

#### 🎬 执行步骤
1. 在确认弹窗中点击 "No, cancel"

#### ✅ 预期结果
- 弹窗关闭 ✅ 实测
- 该张银行卡仍保留在列表中，列表总数不变 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC011: 点击删除确认弹窗的 Close 按钮取消删除 — 卡数据保留

#### 📋 前置条件
- 已登录，/manage-payment 页面，删除确认弹窗已弹出

#### 🎬 执行步骤
1. 点击确认弹窗右上角 "Close" 按钮

#### ✅ 预期结果
- 弹窗关闭 ✅ 实测
- 该张银行卡仍保留在列表中，列表总数不变 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC012: 页面有 2 张或 2 张以上尾号相同的卡时 — 删除其中一张后剩余卡正常保留

#### 📋 前置条件
- 已登录，/manage-payment 页面
- 当前存在 ≥2 张尾号相同（如均为 1119）的银行卡

#### 🎬 执行步骤
1. 点击其中一张尾号 1119 卡的删除图标
2. 确认弹窗弹出后点击 "Yes, delete"

#### ✅ 预期结果
- 被删除的卡从列表移除 ✅ 实测
- 其余尾号 1119 的卡仍正常显示，其他卡（如 8183）也不受影响 ✅ 实测
- 列表总数减少 1 ✅ 实测

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

## 测试统计

| 优先级 | 总数 | 可自动化 |
|--------|------|---------|
| P1 | 12 | 12 |
| **合计** | **12** | **12 (100%)** |

实测文案覆盖率：**100%**（所有 ⚠️ 推断已全部通过 Playwright MCP 实测替换）

> **Oracle 修正记录**：
> - TC006：过期日期触发的是**表单级**错误（接口返回）`Card Details Incorrect - please check your details or try another payment card`，而非字段级 `Please enter a valid expiry date`
