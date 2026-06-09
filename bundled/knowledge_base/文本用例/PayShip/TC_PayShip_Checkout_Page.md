# Gumtree Pay & Ship - Checkout 页面测试用例

> **生成时间**: 2026-04-27  
> **测试方式**: Playwright 自动化脚本 + 手工测试  
> **测试账号**: 买家 gtauto25858@outlook.com  
> **测试站点**: https://www.unicorn.gumtree.io/  
> **页面范围**: Checkout 结账页面 (`/create-order`)  
> **文档版本**: v1.0

---

## 🔧 测试环境配置

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | uk | 英国站 |
| 测试环境基础URL | https://www.unicorn.gumtree.io/ | ⚠️ **注意：是 unicorn 测试环境，非 www.gumtree.com** |
| 买家账号 | gtauto25858@outlook.com | 登录邮箱 |
| 买家密码 | autoGt5858! | 登录密码 |
| 测试商品价格 | £20.00 | 小包裹配送广告 |

### 📌 测试数据占位符

| 占位符 | 含义 | 格式 | 示例 |
|--------|------|------|------|
| `{advertId}` | 广告 ID | 纯数字字符串 | `1001673677` |
| `{AD_TITLE}` | 广告标题 | 字符串 | `Ship Ad UI-Auto Autotest 20260424_153933` |
| `{ITEM_PRICE}` | 商品价格 | £xx.xx | `£20.00` |
| `{PICKUP_FEE}` | 自提点配送费 | £x.xx | `£2.59` |
| `{HOME_FEE}` | 到家配送费 | £x.xx | `£2.99` |
| `{BP_FEE}` | 买家保护费 | £x.xx | `£1.70` |

---

## 📑 目录

- [模块1：页面加载与基础展示](#模块1页面加载与基础展示)
- [模块2：配送方式切换](#模块2配送方式切换)
- [模块3：订单摘要与费用计算](#模块3订单摘要与费用计算)
- [模块4：地址信息展示](#模块4地址信息展示)
- [模块5：支付方式](#模块5支付方式)
- [模块6：订单提交](#模块6订单提交)
- [模块7：异常场景](#模块7异常场景)

---

## 模块1：页面加载与基础展示

### TC-CHKOUT-001: Checkout 页面加载-基础元素验证

#### 📋 前置条件
- 已登录买家账号（gtauto25858@outlook.com）
- 从广告 VIP 页点击 "Buy now" 按钮进入结账页
- 买家账号已绑定支付方式（VISA 尾号 1119）

#### 🎬 执行步骤
1. 从广告详情页点击 "Buy now" 按钮
2. 等待页面跳转至结账页
3. 验证页面 URL 格式
4. 验证页面主要元素展示

#### ✅ 预期结果

**URL 验证：**
- ✅ URL 格式：`/create-order?advertId={advertId}` 或 `/checkout?advertId={advertId}`
- ✅ advertId 参数存在且为纯数字

**页面标题区域：**
- ✅ 页面标题（h1）：`Checkout` 或 `Create order`
- ✅ 返回按钮：`← Back` 或 `< Back to item`

**商品信息区域：**
- ✅ 商品缩略图显示
- ✅ 商品标题：`{AD_TITLE}`
- ✅ 商品价格：`{ITEM_PRICE}`
- ✅ 商品数量：`Qty: 1` 或类似标识

**配送方式区域：**
- ✅ 区域标题：`Delivery options` 或 `Delivery method`
- ✅ 默认选中选项：`Deliver to pick-up point`（Radio 按钮选中状态）
- ✅ 另一选项：`Home delivery`（Radio 按钮未选中状态）

**地址信息区域：**
- ✅ 区域标题：`Delivery address`
- ✅ 买家姓名、地址、邮编、电话号码完整展示

**支付方式区域：**
- ✅ 区域标题：`Payment method`
- ✅ 已保存的支付卡片：`VISA ending in 1119` 或类似展示
- ✅ 支付卡片图标（VISA logo）

**订单摘要区域：**
- ✅ 区域标题：`Order summary`
- ✅ Item subtotal：显示
- ✅ Delivery：显示
- ✅ Buyer Protection：显示（含 ℹ️ 信息图标）
- ✅ Total to pay：显示（加粗/突出显示）

**提交按钮：**
- ✅ 主操作按钮：`Confirm & Pay` 或 `Place Order`（绿色，居中或右侧）
- ✅ 按钮状态：启用（非禁用）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/UI 元素验证
- **UI自动化**: ⚠️ 待自动化

---

### TC-CHKOUT-002: 页面响应式布局验证

#### 📋 前置条件
- 已登录买家账号
- 已进入 Checkout 页面

#### 🎬 执行步骤
1. 在桌面浏览器（宽度 ≥ 1024px）验证页面布局
2. 调整浏览器窗口至平板尺寸（768px - 1023px）
3. 调整浏览器窗口至移动端尺寸（< 768px）

#### ✅ 预期结果

**桌面布局（≥ 1024px）：**
- ✅ 左侧区域：商品信息、配送方式、地址信息、支付方式（垂直排列）
- ✅ 右侧固定栏：订单摘要（Fixed/Sticky 定位）
- ✅ 提交按钮：在右侧订单摘要底部

**平板布局（768px - 1023px）：**
- ✅ 单列布局，订单摘要移至页面底部
- ✅ 所有元素垂直排列
- ✅ 文字大小和间距适配

**移动端布局（< 768px）：**
- ✅ 单列布局，紧凑排版
- ✅ 订单摘要可能折叠为可展开区域
- ✅ 提交按钮固定在底部或跟随滚动

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI/响应式
- **UI自动化**: ⚠️ 待自动化

---

## 模块2：配送方式切换

### TC-CHKOUT-003: 配送方式-默认选中"自提点"

#### 📋 前置条件
- 已登录买家账号
- 广告已启用配送功能（支持自提点和到家配送）
- 首次进入 Checkout 页面

#### 🎬 执行步骤
1. 从广告 VIP 页点击 "Buy now" 进入结账页
2. 查看配送方式区域
3. 检查 Radio 按钮选中状态
4. 检查订单摘要中的配送费用

#### ✅ 预期结果

**配送方式区域：**
- ✅ `Deliver to pick-up point` Radio 按钮：**已选中**（checked）
- ✅ `Home delivery` Radio 按钮：**未选中**（unchecked）
- ✅ 自提点配送费显示：`Deliver to pick-up point £{PICKUP_FEE}`

**订单摘要费用：**
- ✅ Item subtotal：`{ITEM_PRICE}`
- ✅ Delivery：`£{PICKUP_FEE}`（自提点配送费，如 `£2.59`）
- ✅ Buyer Protection：`£{BP_FEE}`
- ✅ Total to pay：正确计算（Item + Delivery + BP）

> ⚠️ **注意**：默认选中"自提点"是 Pay & Ship 的产品逻辑，与"到家配送"相反。

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/默认行为验证
- **UI自动化**: ✅ 已自动化（Phase 3）

---

### TC-CHKOUT-004: 配送方式切换-自提点 → 到家配送

#### 📋 前置条件
- 已登录买家账号
- 结账页默认选中"Deliver to pick-up point"

#### 🎬 执行步骤
1. 在配送方式区域找到 `Home delivery` 选项
2. 点击 `Home delivery` Radio 按钮或 Label
3. 等待页面刷新/动态更新（可能有加载动画）
4. 查看配送方式选中状态变化
5. 查看订单摘要费用变化

#### ✅ 预期结果

**配送方式区域（切换后）：**
- ✅ `Deliver to pick-up point` Radio 按钮：**未选中**
- ✅ `Home delivery` Radio 按钮：**已选中**
- ✅ 到家配送费显示：`Home delivery £{HOME_FEE}`

**订单摘要费用（切换后）：**
- ✅ Item subtotal：`{ITEM_PRICE}`（不变）
- ✅ Delivery：从 `£{PICKUP_FEE}` → 更新为 `£{HOME_FEE}`（如 `£2.99`）
- ✅ Buyer Protection：`£{BP_FEE}`（不变）
- ✅ Total to pay：重新计算并更新（`{ITEM_PRICE}` + `{HOME_FEE}` + `{BP_FEE}`）

**示例（£20 商品）：**
- ✅ Item subtotal：`£20.00`
- ✅ Delivery：`£2.99`（到家配送费，小包裹）
- ✅ Buyer Protection：`£1.70`
- ✅ Total to pay：`£24.69`

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向（E2E 核心路径）
- **UI自动化**: ✅ 已自动化（Phase 3 - phase3_checkout.py）

---

### TC-CHKOUT-005: 配送方式切换-到家配送 → 自提点

#### 📋 前置条件
- 已登录买家账号
- 已手动切换至"Home delivery"（TC-CHKOUT-004）

#### 🎬 执行步骤
1. 点击 `Deliver to pick-up point` Radio 按钮
2. 等待页面更新
3. 验证配送方式和费用变化

#### ✅ 预期结果

**配送方式区域（切换回自提点）：**
- ✅ `Deliver to pick-up point`：**已选中**
- ✅ `Home delivery`：**未选中**
- ✅ 自提点配送费显示：`Deliver to pick-up point £{PICKUP_FEE}`

**订单摘要费用（切换回自提点）：**
- ✅ Delivery：从 `£{HOME_FEE}` → 恢复为 `£{PICKUP_FEE}`（如 `£2.59`）
- ✅ Total to pay：重新计算（`{ITEM_PRICE}` + `{PICKUP_FEE}` + `{BP_FEE}`）

**示例（£20 商品）：**
- ✅ Total to pay：从 `£24.69` → 恢复为 `£24.29`

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/反向切换
- **UI自动化**: ⚠️ 待自动化

---

### TC-CHKOUT-006: 配送方式-仅支持一种配送方式时的展示

#### 📋 前置条件
- 广告仅启用单一配送方式（例如：仅支持自提点，不支持到家配送）
- 或买家地址不在到家配送范围内

#### 🎬 执行步骤
1. 进入结账页
2. 查看配送方式区域

#### ✅ 预期结果

**配送方式区域（仅一种可选）：**
- ✅ 仅显示可用的配送方式（如：`Deliver to pick-up point`）
- ✅ 不显示不可用的配送方式，或显示为禁用状态（灰色，不可点击）
- ✅ 订单摘要中的配送费为唯一可用配送方式的费用

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界/单一选项
- **UI自动化**: ⚠️ 待自动化

---

## 模块3：订单摘要与费用计算

### TC-CHKOUT-007: 订单摘要-费用明细展示

#### 📋 前置条件
- 已登录买家账号
- 已进入 Checkout 页面
- 配送方式已选择（自提点或到家配送）

#### 🎬 执行步骤
1. 查看右侧（或底部）订单摘要区域
2. 逐项验证费用明细

#### ✅ 预期结果

**订单摘要结构：**
```
Order summary
├── Item subtotal        £{ITEM_PRICE}
├── Delivery             £{DELIVERY_FEE}
├── Buyer Protection ℹ️   £{BP_FEE}
└── Total to pay         £{TOTAL}  (加粗/突出)
```

**费用明细验证：**
- ✅ `Item subtotal`：显示商品原价，格式 `£xx.xx`
- ✅ `Delivery`：显示当前选中的配送费（自提点/到家配送）
- ✅ `Buyer Protection`：
  - 金额正确（计算公式：`商品价格 × 5% + £0.70`）
  - 含 ℹ️ 信息图标（鼠标悬停或点击显示说明）
- ✅ `Total to pay`：
  - 金额正确（= Item subtotal + Delivery + Buyer Protection）
  - 视觉突出（加粗/大字号/颜色强调）

**费用计算验证（£20 商品，到家配送）：**
- ✅ Item subtotal：`£20.00`
- ✅ Delivery：`£2.99`
- ✅ Buyer Protection：`£1.70`（= £20 × 5% + £0.70）
- ✅ Total to pay：`£24.69`

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/费用计算
- **UI自动化**: ✅ 已自动化（Phase 3）

---

### TC-CHKOUT-008: Buyer Protection 信息提示验证

#### 📋 前置条件
- 已进入 Checkout 页面

#### 🎬 执行步骤
1. 在订单摘要中找到 `Buyer Protection` 行
2. 点击或鼠标悬停 ℹ️ 信息图标
3. 查看弹出的提示信息

#### ✅ 预期结果

**Buyer Protection 说明（Tooltip/Modal）：**
- ✅ 显示买家保护费用说明，如：
  - `Buyer Protection covers you if the item doesn't arrive or isn't as described.`
  - 或类似保护政策说明
- ✅ 说明计算方式（可选）：`5% of item price + £0.70`
- ✅ 可关闭提示（点击关闭按钮或点击外部区域）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI/信息提示
- **UI自动化**: ⚠️ 待自动化

---

### TC-CHKOUT-009: 订单摘要-不同价格商品的费用计算

#### 📋 前置条件
- 准备不同价格的测试商品：£10、£50、£100、£250

#### 🎬 执行步骤
1. 分别对不同价格商品进入结账页
2. 验证 Buyer Protection 和 Total 计算是否正确

#### ✅ 预期结果

**费用计算公式：**
- Buyer Protection = 商品价格 × 5% + £0.70
- Total to pay = 商品价格 + 配送费 + Buyer Protection

**测试数据（到家配送 £2.99）：**

| 商品价格 | Buyer Protection | Total to pay |
|---------|-----------------|--------------|
| £10.00  | £1.20 (10×5%+0.70) | £14.19 (10+2.99+1.20) |
| £20.00  | £1.70 (20×5%+0.70) | £24.69 (20+2.99+1.70) |
| £50.00  | £3.20 (50×5%+0.70) | £56.19 (50+2.99+3.20) |
| £100.00 | £5.70 (100×5%+0.70) | £108.69 (100+2.99+5.70) |
| £250.00 | £13.20 (250×5%+0.70) | £266.19 (250+2.99+13.20) |

- ✅ 所有价格档位的费用计算正确
- ✅ 小数点保留2位

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/边界值
- **UI自动化**: ⚠️ 待自动化（数据驱动测试）

---

## 模块4：地址信息展示

### TC-CHKOUT-010: 配送地址-完整信息展示

#### 📋 前置条件
- 已登录买家账号
- 买家账号已设置配送地址
- 已进入 Checkout 页面

#### 🎬 执行步骤
1. 查看配送地址区域（`Delivery address`）
2. 验证地址信息完整性

#### ✅ 预期结果

**地址信息区域：**
- ✅ 区域标题：`Delivery address`
- ✅ 收件人姓名：买家姓名完整展示
- ✅ 街道地址：第1行和第2行（如有）
- ✅ 城市：City
- ✅ 邮编：Postcode（格式：`XX## #XX`）
- ✅ 电话号码：Phone（格式：`+44 XXXX XXXXXX` 或 `07XXX XXXXXX`）
- ✅ 编辑按钮：`Edit` 或 `Change address`（可选，根据产品设计）

**地址格式示例：**
```
Delivery address
gt2 auto
Swiss House, Bush Road
Great Yarmouth
NR29 4BY
07123456789
[Edit]
```

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/信息展示
- **UI自动化**: ✅ 已自动化（Phase 3 隐式验证）

---

### TC-CHKOUT-011: 配送地址-编辑功能（如支持）

#### 📋 前置条件
- Checkout 页面支持地址编辑（产品功能）
- 已进入 Checkout 页面

#### 🎬 执行步骤
1. 点击地址区域的 `Edit` 或 `Change address` 按钮
2. 修改地址信息（如：邮编、电话）
3. 保存修改
4. 验证地址更新后订单摘要是否重新计算（如到家配送费受地址影响）

#### ✅ 预期结果

**地址编辑：**
- ✅ 点击 `Edit` 后弹出地址编辑表单或跳转至地址编辑页
- ✅ 表单包含所有地址字段（姓名、街道、城市、邮编、电话）
- ✅ 保存后地址信息在结账页更新
- ✅ 如地址变更影响配送费（如不在到家配送范围），订单摘要自动更新

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/编辑功能
- **UI自动化**: ⚠️ 待自动化（取决于产品实现）

---

### TC-CHKOUT-012: 配送地址-未设置地址时的提示

#### 📋 前置条件
- 买家账号未设置配送地址
- 进入 Checkout 页面

#### 🎬 执行步骤
1. 使用未设置地址的买家账号登录
2. 尝试进入结账页

#### ✅ 预期结果

**未设置地址提示：**
- ✅ 结账页显示提示信息：`Please add a delivery address` 或类似文案
- ✅ 提供 `Add address` 按钮或链接
- ✅ `Confirm & Pay` 按钮禁用，或点击后提示需要先添加地址

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 异常/边界
- **UI自动化**: ⚠️ 待自动化

---

## 模块5：支付方式

### TC-CHKOUT-013: 支付方式-已保存卡片展示

#### 📋 前置条件
- 买家账号已绑定至少一张支付卡（如 VISA 尾号 1119）
- 已进入 Checkout 页面

#### 🎬 执行步骤
1. 查看支付方式区域（`Payment method`）
2. 验证已保存卡片信息展示

#### ✅ 预期结果

**支付方式区域：**
- ✅ 区域标题：`Payment method`
- ✅ 卡片类型图标：VISA / Mastercard / AMEX 等品牌 logo
- ✅ 卡片信息：`VISA ending in 1119` 或类似格式（脱敏展示）
- ✅ 选中状态：Radio 按钮选中或卡片高亮边框
- ✅ 编辑/切换按钮：`Change` 或 `Edit payment method`（如支持多卡片）

**卡片信息格式示例：**
```
Payment method
[VISA logo] VISA ending in 1119
[Change]
```

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/信息展示
- **UI自动化**: ✅ 已自动化（Phase 3 隐式验证）

---

### TC-CHKOUT-014: 支付方式-多卡片切换

#### 📋 前置条件
- 买家账号已绑定多张支付卡
- 已进入 Checkout 页面

#### 🎬 执行步骤
1. 点击 `Change payment method` 或卡片选择区域
2. 查看卡片列表弹窗/区域
3. 选择另一张卡片
4. 验证选中状态更新

#### ✅ 预期结果

**卡片选择：**
- ✅ 显示所有已保存的卡片列表
- ✅ 每张卡片显示类型、尾号、有效期（部分信息）
- ✅ 点击卡片后选中状态更新
- ✅ 关闭弹窗后结账页显示新选中的卡片

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/多选项
- **UI自动化**: ⚠️ 待自动化

---

### TC-CHKOUT-015: 支付方式-添加新卡片

#### 📋 前置条件
- 买家账号已登录
- 已进入 Checkout 页面

#### 🎬 执行步骤
1. 点击 `Add new card` 或 `+ Add payment method` 按钮
2. 填写新卡片信息（卡号、有效期、CVV、持卡人姓名）
3. 保存卡片
4. 验证新卡片在支付方式区域显示

#### ✅ 预期结果

**添加卡片流程：**
- ✅ 弹出卡片信息表单或跳转至添加卡片页
- ✅ 表单包含必填字段：Card number、Expiry date、CVV、Cardholder name
- ✅ 实时卡号格式验证（如：16位数字，自动分组）
- ✅ 保存成功后新卡片显示在结账页
- ✅ 新卡片自动选中为当前支付方式

**测试卡号（Unicorn 环境）：**
- VISA: `4970107111111119`（尾号 1119）
- Expiry: `12/28`
- CVV: `123`

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/添加功能
- **UI自动化**: ⚠️ 待自动化

---

### TC-CHKOUT-016: 支付方式-未绑定卡片时的提示

#### 📋 前置条件
- 买家账号未绑定任何支付方式
- 进入 Checkout 页面

#### 🎬 执行步骤
1. 使用未绑定支付方式的账号进入结账页
2. 查看支付方式区域

#### ✅ 预期结果

**未绑定支付方式：**
- ✅ 支付方式区域显示提示：`No payment method added` 或类似文案
- ✅ 提供 `Add payment method` 按钮
- ✅ `Confirm & Pay` 按钮禁用，或点击后提示需要先添加支付方式

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 异常/边界
- **UI自动化**: ⚠️ 待自动化

---

## 模块6：订单提交

### TC-CHKOUT-017: 订单提交-正常流程

#### 📋 前置条件
- 已登录买家账号
- 配送方式已选择
- 配送地址完整
- 支付方式已绑定
- 所有必填信息已填写

#### 🎬 执行步骤
1. 在结账页确认所有信息正确
2. 点击 `Confirm & Pay` 或 `Place Order` 按钮
3. 等待页面跳转（可能有加载动画，最多 60 秒）
4. 验证跳转后的页面

#### ✅ 预期结果

**提交过程：**
- ✅ 点击按钮后出现加载指示器（Spinner / Loading 动画）
- ✅ 按钮文字变为 `Processing...` 或按钮禁用
- ✅ 页面在合理时间内（< 60 秒）跳转

**支付成功页：**
- ✅ URL 跳转至 `/payment-result?orderId={ORDER_ID}` 或 `/order/{ORDER_ID}`
- ✅ 页面显示成功提示：`Thanks for your order` 或 `Order placed successfully`
- ✅ 显示订单号：`Order No. : {ORDER_NO}`（8位数字）
- ✅ 显示订单摘要（商品、价格、配送方式）
- ✅ 提供按钮：`View order details` 或 `Go to My Orders`

**订单生成验证：**
- ✅ 买家侧订单列表（`/manage/orders`）可查看到新订单
- ✅ 买家订单状态：`In progress | Awaiting dispatch`
- ✅ 卖家侧订单列表（`/manage/orders?type=sold`）可查看到新订单
- ✅ 卖家订单状态：`In progress | Awaiting dispatch`

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向（E2E 核心路径）
- **UI自动化**: ✅ 已自动化（Phase 4 - phase4_payment.py）

---

### TC-CHKOUT-018: 订单提交-加载超时处理

#### 📋 前置条件
- 已进入 Checkout 页面
- 模拟网络延迟或后端处理慢

#### 🎬 执行步骤
1. 点击 `Confirm & Pay` 按钮
2. 等待超过 60 秒
3. 观察页面行为

#### ✅ 预期结果

**超时处理：**
- ✅ 显示超时错误提示：`Request timed out. Please try again.` 或类似文案
- ✅ 提供重试按钮：`Retry` 或 `Try again`
- ✅ 或显示支持联系方式：`Contact Customer Service`

**防重复提交：**
- ✅ 超时期间按钮保持禁用，防止重复点击
- ✅ 后端应有幂等性保护，避免重复扣款

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 异常/超时
- **UI自动化**: ⚠️ 待自动化

---

### TC-CHKOUT-019: 订单提交-支付失败处理

#### 📋 前置条件
- 使用测试卡片模拟支付失败场景
- 或卡片余额不足

#### 🎬 执行步骤
1. 使用失败测试卡号或余额不足的卡片
2. 点击 `Confirm & Pay` 按钮
3. 等待支付处理

#### ✅ 预期结果

**支付失败提示：**
- ✅ 页面显示错误提示：`Payment failed. Please try again.` 或具体失败原因
- ✅ 错误原因可能包括：
  - `Insufficient funds`（余额不足）
  - `Card declined`（卡片被拒）
  - `Invalid card details`（卡片信息错误）
- ✅ 保持在结账页，允许用户修改支付方式或重试
- ✅ 订单未生成（买家/卖家侧订单列表中无此订单）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 异常/支付失败
- **UI自动化**: ⚠️ 待自动化

---

### TC-CHKOUT-020: 订单提交-3DS 验证流程

#### 📋 前置条件
- 使用需要 3DS 验证的测试卡（如 `4970105181818183`）
- 已进入 Checkout 页面

#### 🎬 执行步骤
1. 选择 3DS 测试卡
2. 点击 `Confirm & Pay` 按钮
3. 页面跳转至 3DS 验证页面（银行页面或模拟页面）
4. 输入验证码：`702100`（测试环境固定验证码）
5. 提交验证
6. 等待返回结账结果页

#### ✅ 预期结果

**3DS 验证流程：**
- ✅ 点击支付后跳转至 3DS 验证页面
- ✅ 验证页面显示银行名称、卡号尾号、支付金额
- ✅ 输入正确验证码后验证成功
- ✅ 验证成功后自动返回支付成功页
- ✅ 订单正常生成

**3DS 验证失败：**
- ✅ 输入错误验证码或取消验证后返回结账页
- ✅ 显示验证失败提示
- ✅ 订单未生成

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/3DS 验证
- **UI自动化**: ⚠️ 待自动化

---

## 模块7：异常场景

### TC-CHKOUT-021: 广告已下架-结账页访问

#### 📋 前置条件
- 广告已被卖家删除或下架
- 买家持有该广告的结账页 URL

#### 🎬 执行步骤
1. 广告下架后，买家直接访问 `/create-order?advertId={advertId}`
2. 观察页面响应

#### ✅ 预期结果

**广告不可用提示：**
- ✅ 页面显示错误提示：`This item is no longer available` 或类似文案
- ✅ 提供返回按钮：`Back to search` 或 `Go to homepage`
- ✅ 不允许继续下单

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 异常/广告不可用
- **UI自动化**: ⚠️ 待自动化

---

### TC-CHKOUT-022: 商品库存不足-结账页访问

#### 📋 前置条件
- 广告已被其他买家购买（库存为 0）
- 买家尝试进入结账页

#### 🎬 执行步骤
1. 商品被其他买家购买后，买家点击 "Buy now"
2. 观察页面响应

#### ✅ 预期结果

**库存不足提示：**
- ✅ 页面显示提示：`This item has been sold` 或 `Out of stock`
- ✅ 不允许进入结账页或在结账页显示错误提示
- ✅ 提供返回或继续浏览的选项

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 异常/库存不足
- **UI自动化**: ⚠️ 待自动化

---

### TC-CHKOUT-023: 未登录状态-结账页访问

#### 📋 前置条件
- 用户未登录
- 尝试直接访问结账页 URL

#### 🎬 执行步骤
1. 退出登录状态
2. 直接访问 `/create-order?advertId={advertId}`
3. 观察页面行为

#### ✅ 预期结果

**未登录跳转：**
- ✅ 自动跳转至登录页 `/signin`
- ✅ 登录成功后自动返回结账页（保留 advertId 参数）
- ✅ 或显示登录弹窗，登录后留在当前页

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 异常/未登录
- **UI自动化**: ⚠️ 待自动化

---

### TC-CHKOUT-024: 卖家自己购买-结账页限制

#### 📋 前置条件
- 使用卖家账号（发布广告的账号）
- 尝试购买自己的广告

#### 🎬 执行步骤
1. 卖家登录后访问自己发布的广告 VIP 页
2. 点击 "Buy now" 按钮（如果存在）
3. 尝试进入结账页

#### ✅ 预期结果

**自买限制：**
- ✅ VIP 页不显示 "Buy now" 按钮（对卖家隐藏）
- ✅ 或点击后显示提示：`You cannot buy your own item`
- ✅ 不允许卖家购买自己的商品

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 异常/自买限制
- **UI自动化**: ⚠️ 待自动化

---

### TC-CHKOUT-025: 表单验证-必填字段检查

#### 📋 前置条件
- 已进入 Checkout 页面
- 某些必填信息缺失（如：未选择配送方式、未填写地址）

#### 🎬 执行步骤
1. 在必填信息缺失的情况下点击 `Confirm & Pay` 按钮
2. 观察表单验证提示

#### ✅ 预期结果

**表单验证：**
- ✅ 显示错误提示：`Please select a delivery method` 或类似文案
- ✅ 错误字段高亮显示（红色边框或背景）
- ✅ 页面滚动至第一个错误字段位置
- ✅ 按钮保持启用，允许修正后重新提交

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 异常/表单验证
- **UI自动化**: ⚠️ 待自动化

---

## 📊 用例统计

| 模块 | 用例数 | 自动化 ✅ | 待自动化 ⚠️ | P0 | P1 | P2 |
|------|--------|----------|------------|----|----|-----|
| 模块1：页面加载与基础展示 | 2 | 0 | 2 | 1 | 1 | 0 |
| 模块2：配送方式切换 | 4 | 2 | 2 | 2 | 1 | 1 |
| 模块3：订单摘要与费用计算 | 3 | 1 | 2 | 1 | 2 | 0 |
| 模块4：地址信息展示 | 3 | 1 | 2 | 1 | 2 | 0 |
| 模块5：支付方式 | 4 | 1 | 3 | 1 | 3 | 0 |
| 模块6：订单提交 | 4 | 1 | 3 | 1 | 3 | 0 |
| 模块7：异常场景 | 5 | 0 | 5 | 0 | 3 | 2 |
| **合计** | **25** | **6** | **19** | **7** | **15** | **3** |

---

## 🛠️ 自动化实现参考

### 相关脚本文件
```
Phase 3 脚本（包含 Checkout 页面验证）:
test_cases/payship/homeDelivery_happyPath/phase3_checkout.py
test_cases/payship/homeDelivery_happyPath/phase4_payment.py
```

### 核心验证逻辑

#### 配送方式切换（TC-CHKOUT-004）
```python
# 切换至 Home delivery
home_delivery_radio = page.locator("input[type='radio'][value='HOME']")
if home_delivery_radio.count() > 0:
    home_delivery_radio.click()
else:
    # 备选策略：通过 label 点击
    page.locator("label:has-text('Home delivery')").click()

# 等待费用更新
page.wait_for_timeout(1000)

# 验证配送费更新
delivery_fee = page.locator("text=/Delivery.*£[0-9.]+/").text_content()
assert "£2.99" in delivery_fee
```

#### 订单摘要验证（TC-CHKOUT-007）
```python
page_text = page.text_content("body")

# 验证费用明细
assert "Item subtotal" in page_text
assert "£20.00" in page_text  # 商品价格
assert "Delivery" in page_text
assert "£2.99" in page_text   # 到家配送费
assert "Buyer Protection" in page_text
assert "£1.70" in page_text   # 买家保护费
assert "Total to pay" in page_text
assert "£24.69" in page_text  # 总计
```

#### 订单提交（TC-CHKOUT-017）
```python
# 点击提交按钮
confirm_button = page.locator("button:has-text('Confirm & Pay')")
confirm_button.click()

# 等待跳转
page.wait_for_load_state("domcontentloaded", timeout=60000)

# 验证支付成功页
assert "payment-result" in page.url or "/order/" in page.url
assert "Thanks for your order" in page.text_content("body")
```

---

## 📝 附录

### Checkout 页面元素定位器参考

```python
# 页面标题
page_title = page.locator("h1:has-text('Checkout')")

# 配送方式
pickup_radio = page.locator("input[type='radio'][value='PICKUP']")
home_radio = page.locator("input[type='radio'][value='HOME']")
pickup_label = page.locator("label:has-text('Deliver to pick-up point')")
home_label = page.locator("label:has-text('Home delivery')")

# 订单摘要
order_summary = page.locator("[class*='order-summary'], [class*='OrderSummary']")
item_subtotal = page.locator("text=/Item subtotal.*£[0-9.]+/")
delivery_fee = page.locator("text=/Delivery.*£[0-9.]+/")
buyer_protection = page.locator("text=/Buyer Protection.*£[0-9.]+/")
total_to_pay = page.locator("text=/Total to pay.*£[0-9.]+/")

# 地址信息
delivery_address = page.locator("[class*='delivery-address'], [class*='DeliveryAddress']")

# 支付方式
payment_method = page.locator("[class*='payment-method'], [class*='PaymentMethod']")

# 提交按钮
confirm_button = page.locator("button:has-text('Confirm & Pay'), button:has-text('Place Order')")
```

---

**文档生成时间**: 2026-04-27  
**文档版本**: v1.0  
**关联文档**: `TC_PayShip_HomeDelivery_HappyPath.md`  
**关联脚本**: `test_cases/payship/homeDelivery_happyPath/phase3_checkout.py`
