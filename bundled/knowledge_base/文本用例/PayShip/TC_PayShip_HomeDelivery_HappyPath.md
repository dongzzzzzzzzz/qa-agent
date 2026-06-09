# Gumtree Pay & Ship - 端到端完整流程测试用例（配送到家版）

> **生成时间**: 2026-03-24  
> **测试方式**: Playwright 自动化脚本（`TC_PayShip_HomeDelivery_HappyPath.py`）  
> **探测账号**: 卖家 gtauto5858@outlook.com / 买家 gtauto25858@outlook.com  
> **测试站点**: https://www.unicorn.gumtree.io/  
> **流程覆盖**: 卖家 API 发帖 → 买家选择到家配送下单支付 → 卖家创建面单 → Webhook AC/IT/AT/DE(HOME) 物流状态推进 → 每阶段买卖双方订单页面校验 → 买家点击确认收货 → 订单完成 → 买卖双方最终状态校验  
> **文档版本**: v1.0（基于脚本逻辑及 PickupStore 实测经验推断，待实测补全）

---

## 🔧 测试环境配置

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | uk | 英国站 |
| 测试环境基础URL | https://www.unicorn.gumtree.io/ | ⚠️ **注意：是 unicorn 测试环境，非 www.gumtree.com** |
| 卖家账号 | gtauto5858@outlook.com | 登录邮箱 |
| 卖家密码 | autoGt5858! | 登录密码 |
| 买家账号 | gtauto25858@outlook.com | 登录邮箱 |
| 买家密码 | autoGt5858! | 登录密码 |

### 📌 文档占位符格式说明

本文档中所有动态值使用以下占位符，**测试脚本中必须动态获取，不可硬编码**：

| 占位符 | 含义 | 格式 | 示例 | 获取方式 |
|--------|------|------|------|---------|
| `{ORDER_ID}` | 订单详情页 URL 中的订单 ID | 纯数字长串 | `1380036800000000000002997260` | 从 `/order/{ORDER_ID}?type=sold` 提取 |
| `{ORDER_NO}` | 页面展示的订单编号 | 8位纯数字 | `13800368` | 从 `Order No. : {ORDER_NO}` 提取 |
| `{TRACKING_NUMBER}` | 物流追踪号（完整） | 字母+数字 | `H06Z5A0000017876` | `get_tracking_number(order_id, env="unicorn")` |
| `{AD_TITLE}` | 广告标题 | 字符串 | `Delivery Store 20260413T200931 TW9` | 发布时动态生成 |
| `{D MMM}` | 进度条节点日期 | `D MMM`（无年份） | `13 Apr` | 页面动态显示，可用正则 `\d{1,2} [A-Z][a-z]{2}` |
| `{D MMM YYYY}` | 发货截止日期 | `D MMM YYYY` | `22 Apr 2026` | 页面动态显示，断言格式即可 |

---

## 🔑 与自提点（PickupStore）流程的关键差异

| 差异项 | 自提点（PickupStore） | 到家（HomeDelivery） |
|--------|----------------------|---------------------|
| 结账页默认配送方式 | **默认选中** "Deliver to pick-up point" | 需手动切换至 "Home delivery" |
| 到家配送费（Small 包裹） | — | **£2.99** |
| 自提点配送费（Small 包裹） | £2.59 | — |
| 物流状态流转 | AC → IT → AT → **SP → DE(STORE)** | AC → IT → AT → **DE(HOME)** |
| 包裹到达后买家状态 | `Arrived at pick-up point` | — |
| 投递完成后买家状态 | `Picked up` | **`Delivered`** |
| 进度条节点（买家侧） | Paid / Dispatched / Arrived / Picked up | **Paid / Dispatched / Delivered** |
| Buyer Protection（£20商品） | £1.70 | £1.70（相同） |
| 总计（£20商品）| £24.29 | **£24.69** |

---

## 📑 目录

- [模块1：卖家发布广告（API 发帖）](#模块1卖家发布广告api-发帖)
- [模块2：买家浏览与下单（选择到家配送）](#模块2买家浏览与下单选择到家配送)
- [模块3：买家支付](#模块3买家支付)
- [模块4：卖家创建物流面单](#模块4卖家创建物流面单)
- [模块5：物流状态正向流转（AC → IT → AT → DE HOME）](#模块5物流状态正向流转ac--it--at--de-home)
- [模块6：买家签收与确认收货](#模块6买家签收与确认收货)

---

## 模块1：卖家发布广告（API 发帖）

### TC-HD-001: API 创建支持配送广告-完整正向流程（小包裹）

#### 📋 前置条件
- 卖家账号已登录（gtauto5858@outlook.com）
- 测试框架可访问 AdvertCreationHelper API
- 站点：https://www.unicorn.gumtree.io/

#### 🎬 执行步骤
1. 调用 `AdvertCreationHelper` 工具类，以卖家账号 API 创建小包裹物流广告：
   ```python
   helper = AdvertCreationHelper(env="unicorn", email=SELLER_EMAIL, password=SELLER_PASSWORD)
   info: AdvertInfo = helper.create_delivery_advert(parcel_size="small")
   ```
2. 验证返回的 `AdvertInfo` 不为 None
3. 记录广告 ID（`info.advert_id`）和广告标题（`info.title`）
4. 卖家进入 `/manage/ads`，等待广告上线（最多重试 6 次，每次间隔 5 秒）
5. 从 Manage Ads 列表中找到对应广告，获取 VIP 链接

#### ✅ 预期结果
- ✅ API 返回 AdvertInfo 对象，`advert_id` 非空
- ✅ 广告标题格式：`Delivery Store {YYYYMMDDTHHmmss} {时区}`（每次唯一）
- ✅ 商品价格：£20
- ✅ 包裹规格：small
- ✅ 卖家 Manage Ads 页面出现该广告（最迟约 30 秒内上线）
- ✅ 广告 VIP 链接格式：`/p/other-footwear/{title}/{ad-id}` 或 `/p/{advert_id}`

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向（E2E 前置）
- **Case ID**: `case_id_PAYSHIP_E2E_HOME_001`（前置步骤）
- **UI自动化**: ✅ 已自动化（脚本 class_setup fixture）

---

## 模块2：买家浏览与下单（选择到家配送）

### TC-HD-005: 广告详情页-Buy now 按钮展示验证

#### 📋 前置条件
- 已登录**买家账号**（gtauto25858@outlook.com）
- 访问卖家发布的已启用配送广告（TC-HD-001 创建的广告）

#### 🎬 执行步骤
1. 导航到广告详情页（`{advert_vip_url}`）
2. 查看右侧区域
3. 滚动页面至底部，触发浮动窗口展示

#### ✅ 预期结果
- ✅ 右侧显示价格 **£20** 和绿色 "**Buy now**" 按钮
- ✅ 显示 "Delivery from **£2.59** | Buyer Protection **£1.70**"
- ✅ 页面同时显示 "Message" 按钮（私信卖家）
- ✅ **浮动窗口验证**：当页面滚动到底部时，页面顶部出现浮动窗口（sticky footer），包含：
  - 商品价格：**£20**
  - 配送费信息：**£2.59**
  - 买家保护费：**£1.70**
  - 绿色 "**Buy now**" 按钮（可点击）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 已自动化（Phase 2，包含浮动窗口 5 项验证）

---

### TC-HD-006: 浮动窗口 Buy now 按钮-跳转结账页验证

#### 📋 前置条件
- 已登录**买家账号**（gtauto25858@outlook.com）
- 访问卖家发布的已启用配送广告（TC-HD-001 创建的广告）
- 页面已滚动至底部，浮动窗口已展示

#### 🎬 执行步骤
1. 滚动页面至底部，触发浮动窗口展示
2. 验证浮动窗口中包含绿色 "**Buy now**" 按钮
3. 点击浮动窗口中的 "**Buy now**" 按钮
4. 等待页面跳转完成

#### ✅ 预期结果
- ✅ 浮动窗口中的 Buy now 按钮可点击（未被禁用）
- ✅ 点击后页面成功跳转至结账页
- ✅ 跳转后的 URL 包含 `/create-order?advertId=` 或 `/checkout`
- ✅ 结账页面正确加载，显示商品信息和配送选项
- ✅ 跳转后的 `advertId` 参数与当前广告 ID 一致

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向（交互验证）
- **UI自动化**: ✅ 已自动化（Phase 2，浮动窗口跳转验证）

---

### TC-HD-007: 结账页-切换"配送到家"并验证费用（E2E 核心路径）

#### 📋 前置条件
- 已登录买家账号（gtauto25858@outlook.com）
- 已在广告 VIP 页确认 Buy now 按钮可见
- 买家账号已绑定支付方式（测试账号预绑 VISA 尾号 1119）

#### 🎬 执行步骤
1. 在广告详情页点击 "**Buy now**" 按钮
2. 页面跳转至结账页（URL 应包含 `create-order` 或 `checkout`）
3. 确认默认选中 "**Deliver to pick-up point**"
4. 手动切换配送方式为 "**Home delivery**"（通过 radio 按钮或 label 点击）：
   - 优先策略：找到 `input[type='radio'][value='HOME']` 并点击
   - 备选策略：找到 `label:has-text('Home delivery')` 并点击
5. 查看右侧订单摘要，确认费用展示

#### ✅ 预期结果
- ✅ 点击 Buy now 后，URL 跳转至 `/create-order?advertId={advertId}`
- ✅ 结账页初始默认选中 "Deliver to pick-up point"（⚠️ 与 Home Delivery 相反，需手动切换）
- ✅ 切换到 Home delivery 后，配送选项显示 "Home delivery **£2.99**"
- ✅ 订单摘要费用（切换到家后）：
  - Item subtotal：**£20.00**
  - Delivery：**£2.99**（Home delivery 小包裹）
  - Buyer Protection：**£1.70**（£20 × 5% + £0.70）
  - Total to pay：**£24.69**

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向（E2E 核心路径）
- **UI自动化**: ✅ 已自动化（Phase 1 - _phase1_buyer_purchase）

---

## 模块3：买家支付

### TC-HD-011: 使用已保存银行卡支付-E2E 核心路径

#### 📋 前置条件
- 已登录买家账号（测试账号已绑定 VISA 尾号 1119）
- 已在结账页切换为 Home delivery（TC-HD-007 完成）
- 结账页显示 "Confirm & Pay" 按钮

#### 🎬 执行步骤
1. 在结账页确认：
   - 配送方式：Home delivery
   - 费用摘要：£20.00 + £2.99 + £1.70 = £24.69
   - 支付方式：VISA 尾号 1119
2. 点击 "**Confirm & Pay**"（或 "Place Order" / "Pay now"）按钮
3. 等待页面跳转（最多 60 秒）

#### ✅ 预期结果

**支付成功后跳转页：**
- ✅ 页面 URL 包含 `payment-result` 或 `order`（不含 `/p/`）
- ✅ 页面包含成功提示文案，如 "Thanks for your order"
- ✅ 买家侧自动生成订单（可在 My Orders → Bought 查看，状态：`In progress | Awaiting dispatch`）
- ✅ 卖家侧自动生成订单（可在 My Orders → Sold 查看，状态：`In progress | Awaiting dispatch`）
- ⚠️ 支付结果页显示 8 位 Order No.（可供提取）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向（E2E 核心路径）
- **UI自动化**: ✅ 已自动化（Phase 1 - _phase1_buyer_purchase）

---

### TC-HD-011b: 买家订单列表（Bought Tab）-下单成功后元素校验

#### 📋 前置条件
- 已登录买家账号
- TC-HD-011 支付成功后进入：Menu → My Orders

#### 🎬 执行步骤
1. 导航到 `/manage/orders`
2. 默认显示 `Bought` Tab
3. 找到 TC-HD-001 广告对应的订单
4. 点击 "**View order details**"，进入订单详情页
5. 从 URL 中提取完整订单 ID（格式：`/order/{ORDER_ID}?type=bought`）

#### ✅ 预期结果

**页面级元素：**
- ✅ URL：`/manage/orders`
- ✅ 页面标题：`My orders`
- ✅ 内部 Tab：`Bought`（选中）/ `Sold`
- ✅ 筛选下拉框（Filter）：`All` / `In progress` / `Completed` / `Cancelled` / `Suspended`

**目标订单卡片：**
- ✅ 订单状态标签：`In progress | Awaiting dispatch`
- ✅ 商品缩略图（可点击）
- ✅ 商品标题（可点击，链接到 `/order/{ORDER_ID}?type=bought`）
- ✅ 商品价格：`£20.00`
- ✅ `View order details` 按钮
- ✅ 订单编号格式：`Order number: {ORDER_NO}`（8位数字）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/UI元素校验
- **UI自动化**: ✅ 已自动化（Phase 2 - _phase2_extract_order_id）

---

### TC-HD-011c: 买家订单详情页-下单成功后全量元素校验

#### 📋 前置条件
- 已登录买家账号
- 从订单列表点击 "View order details" 进入对应订单详情页

#### 🎬 执行步骤
1. 进入买家订单详情页（`/order/{ORDER_ID}?type=bought`）
2. 逐一校验页面所有展示元素

#### ✅ 预期结果（订单详情页元素全量校验）

**页面级元素：**
- ✅ URL 格式：`/order/{ORDER_ID}?type=bought`
- ✅ `← Back` 返回按钮

**订单头部区域：**
- ✅ 区域标题：`Order details`
- ✅ 订单号格式：`Order No. : {ORDER_NO}`
- ✅ 当前状态：`Awaiting Dispatch`
- ✅ 截止发货提示：`Will be dispatched by: {D MMM YYYY}`

**进度条区域（Home Delivery 订单）：**
- ⚠️ 推断：进度条显示 **3 个节点**（到家配送）：
  - 第1节点：`Paid`（已激活，含日期 `{D MMM}`）
  - 第2节点：`Dispatched`（未激活）
  - 第3节点：`Delivered`（未激活）

**商品信息区域：**
- ✅ 区域标题：`Item`
- ✅ 商品数量徽章：`1`
- ✅ 商品缩略图（可点击，链接到快照页）
- ✅ 商品标题（可点击）
- ✅ 商品价格：`£20.00`
- ✅ `View Snapshot` 按钮
- ✅ `Message seller` 按钮

**费用明细区域：**
- ✅ 区域标题：`Order summary`
- ✅ Item subtotal：`£20.00`
- ✅ Delivery：`£2.99`（Home delivery）
- ✅ Buyer Protection：`£1.70`（含 ℹ️ 图标）
- ✅ Total：`£24.69`

**配送信息区域：**
- ✅ 区域标题1：`Delivery options`，内容：`Home delivery`
- ✅ 区域标题2：`Delivery address`，包含：买家姓名 / 街道地址 / 邮编 / 电话

**支付信息区域：**
- ✅ 区域标题：`Payment method`
- ✅ 展示格式：`VISA ending in 1119`
- ✅ 支付时间戳：`{DD-MM-YYYY, HH:MM:SS}`

**底部操作按钮（Awaiting Dispatch 状态）：**
- ✅ `Contact Customer Service` 按钮
- ✅ `Cancel order` 按钮

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/UI元素校验
- **UI自动化**: ⚠️ 部分自动化（Phase 2 提取 ORDER_ID，详细元素校验待补充）

---

### TC-HD-011d: 卖家订单列表页（Sold Tab）-下单成功后元素校验

#### 📋 前置条件
- 已登录卖家账号（gtauto5858@outlook.com）
- 买家支付成功后，进入：Menu → My Orders → 切换至 `Sold` Tab

#### 🎬 执行步骤
1. 使用卖家账号登录
2. 导航到 `/manage/orders?type=sold`
3. 在列表中找到 TC-HD-001 广告对应的订单

#### ✅ 预期结果

**目标订单卡片：**
- ✅ 订单状态标签：`In progress | Awaiting dispatch`
- ✅ 商品标题（含广告标题）
- ✅ 商品售价：`£20.00`
- ✅ 发货倒计时提示：⏰ 图标 + `7 day(s) left to send`
- ✅ `Create Label` 按钮（Awaiting dispatch 状态下直接展示）
- ✅ 订单编号格式：`Order number: {ORDER_NO}`

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/UI元素校验
- **UI自动化**: ✅ 已自动化（Phase 3 前置检查）

---

## 模块4：卖家创建物流面单

### TC-HD-018: 卖家创建面单-完整流程

#### 📋 前置条件
- 已登录卖家账号（gtauto5858@outlook.com，已完成 MangoPay 卖家注册）
- 买家支付成功，卖家订单列表可见该订单（状态：`Awaiting dispatch`）

#### 🎬 执行步骤

**Step 1：进入卖家订单 Sold 列表**
1. 导航到 `/manage/orders?type=sold`
2. 找到对应订单

**Step 2：点击 Create Label**
3. 在订单卡片或订单详情页点击 `Create Label` 按钮

**Step 3：查看创建面单确认页**
4. 确认页面跳转至 `/shipping-label/create?orderId={ORDER_ID}&source=OrderDetail`
5. 检查 "Send with"、"Return address"、"Recipient address" 各区域信息

**Step 4：点击 Continue 生成面单（最多重试 5 次）**
6. 点击 `Continue` 按钮触发面单生成
7. 若出现 "Label generation failed" 弹窗，点击 `Retry` 重试
8. 等待面单生成成功页（URL 变为 `/shipping-label/{ORDER_ID}`，不含 "create"）

**Step 5：API 获取完整 Tracking Number**
9. 调用 `get_tracking_number(order_id="{ORDER_ID}", env="unicorn")` 获取完整追踪号

#### ✅ 预期结果

**创建面单确认页（Step 3）：**
- ✅ URL：`/shipping-label/create?orderId={ORDER_ID}&source=OrderDetail`
- ✅ 页面标题（h1）：`Create label`
- ✅ "Send with" 区域（h2）：
  - 子标题（h3）：`Evri drop-off point`
  - 说明文本：`paid by buyer`
  - 可点击区域：`Find a drop-off location`
- ✅ "Return address" 区域（h2）：
  - 卖家姓名（h3）：`gt auto`（从卖家账号自动读取）
  - 地址：`Swiss House, Bush Road, Great Yarmouth` / `NR29 4BY`
  - 手机：`07123456789`
- ✅ "Recipient address" 区域（h2）：
  - 买家姓名（h3）：`gt2 auto`
  - 说明文本：`This address is automatically added to the shipping label.`（收件地址自动写入面单，页面不显示详细地址）
- ✅ `Continue` 按钮

**面单生成成功页（Step 4）：**
- ✅ URL 跳转至 `/shipping-label/{ORDER_ID}`（不含 "create"）
- ✅ 页面标题（h1）：`Your label is ready!`
- ✅ 确认说明文本含到期日期，如：`drop your item off at an Evri drop-off point by {D MMM YYYY}`
- ✅ **QR 码图片**显示
- ✅ **Tracking Number 短码**显示（完整追踪号需通过 proxy API 获取）
- ✅ `Save QR code` 按钮
- ✅ `Download label` 按钮
- ✅ `Find a drop-off location` 链接

**面单创建后卖家订单状态变化：**
- ✅ 卖家订单列表 `Create Label` 按钮 → 变为 `View Label` 按钮
- ✅ 卖家订单详情 `Create Label` → 变为 `View Label`
- ✅ 订单状态仍为 `Awaiting Dispatch`（面单已创建，尚未交承运商）

**API 获取 Tracking Number（Step 5）：**
- ✅ `get_tracking_number(order_id, env="unicorn")` 返回非空字符串
- ✅ 格式示例：`H06Z5A0000017876`（字母+数字）

> ⚠️ **环境注意**：若 Continue 后出现弹窗 "Label generation failed - Calling logistics service failed. Please try again later."，点击 `Retry` 重试，最多 5 次。5 次仍失败则报告环境问题并停止测试。

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向（E2E 核心路径）
- **UI自动化**: ✅ 已自动化（Phase 3 - _phase3_seller_create_label，含 5 次重试逻辑）

---

## 模块5：物流状态正向流转（AC → IT → AT → DE HOME）

> **注意**：以下场景通过调用 **`test_cases/payship/utils/ship_webhook.py`** 工具类模拟物流商（EVRi）回调状态变更。
>
> **工具类使用方式（Python）：**
> ```python
> from test_cases.payship.utils.order_api import get_tracking_number
> from test_cases.payship.utils.ship_webhook import ShipWebhook
>
> # 从面单成功页 / proxy API 获取完整追踪号
> tracking_number = get_tracking_number(order_id="{ORDER_ID}", env="unicorn")
>
> webhook = ShipWebhook(env_name="unicorn")
>
> # AC：承运商接收
> response = webhook.trigger(tracking_number=tracking_number, status_code="AC")
>
> # IT：包裹在途中
> response = webhook.trigger(tracking_number=tracking_number, status_code="IT")
>
> # AT：包裹派送中（到家配送专用）
> response = webhook.trigger(tracking_number=tracking_number, status_code="AT")
>
> # DE：已投递到家（必须传 delivery_method="HOME"）
> response = webhook.trigger(
>     tracking_number=tracking_number,
>     status_code="DE",
>     delivery_method="HOME"
> )
> ```
>
> **到家配送完整物流流转**：AC → IT → AT → DE(HOME)
>
> **各状态说明**：
> | Status Code | 触发时机 | 订单状态变化 |
> |-------------|----------|-------------|
> | AC | 承运商揽收包裹 | `Awaiting dispatch` → **`On its way`** |
> | IT | 包裹在途中 | `On its way`（无变化，仅追踪更新）|
> | AT | 包裹派送中（派件员上门投递） | `On its way`（无变化，仅追踪更新）|
> | DE(HOME) | 已投递到家 | `On its way` → **`Delivered`** |

---

### TC-HD-020: 物流状态-AC（承运商接收）→ 订单"On its way"

#### 📋 前置条件
- TC-HD-018 面单已创建，Tracking Number 已记录
- 订单当前状态：`Awaiting Dispatch`

#### 🎬 执行步骤
1. 调用 Webhook 触发 AC 状态：
   ```python
   response = webhook.trigger(tracking_number=tracking_number, status_code="AC")
   assert response.status_code == 200
   ```
2. 等待 3 秒（后端状态同步）
3. 卖家导航到 `/order/{ORDER_ID}?type=sold` 查看状态
4. 买家导航到 `/order/{ORDER_ID}?type=bought` 查看状态

#### ✅ 预期结果

**Webhook 调用：**
- ✅ HTTP 响应状态码：`200`

**卖家订单列表页（AC 后）：**
- ✅ 订单卡片状态文字：`In progress | On its way`
- ✅ `View Label` 按钮 → 变为 `Track order` 按钮

**卖家订单详情页（AC 后）：**
- ✅ `Order details` 区域状态：`On its way`
- ✅ 进度条激活节点：`Paid ({D MMM})` + `Dispatched ({D MMM})`（两个已激活）
- ✅ `Delivered` 节点**未**激活（灰色）
- ✅ `View Label` → 变为 `Track order` 按钮
- ✅ `Cancel order` 按钮**消失**（已发货后不可取消）
- ✅ 底部操作按钮：`Message buyer` + `Track order` + `Contact Customer Service`

**买家订单列表页（AC 后）：**
- ✅ 订单卡片状态文字：`In progress | On its way`
- ✅ `Track order` 按钮显示

**买家订单详情页（AC 后）：**
- ✅ 订单状态：`On its way`
- ✅ 进度条激活节点：`Paid` + `Dispatched`（两个已激活）
- ✅ `Delivered` 节点**未**激活
- ✅ `Cancel order` 按钮**消失**
- ✅ 底部操作按钮：`Message seller` + `Track order` + `Contact Customer Service`

#### 📊 用例属性
- **优先级**: P0
- **Case ID**: `case_id_PAYSHIP_E2E_HOME_001`（Phase 4a）
- **UI自动化**: ✅ 已自动化（_trigger_and_verify + _check_seller/buyer_order_status）

---

### TC-HD-020b: 物流状态-IT（在途中）→ 订单追踪更新，状态无变化

#### 📋 前置条件
- AC 状态已触发（TC-HD-020），订单状态：`On its way`

#### 🎬 执行步骤
```python
response = webhook.trigger(tracking_number=tracking_number, status_code="IT")
assert response.status_code == 200
```

#### ✅ 预期结果

**买家/卖家订单列表页（IT 后）：**
- ✅ 订单卡片状态文字：`In progress | On its way`（与 AC 后**一致**，**无变化**）
- ✅ `Track order` 按钮保持显示

**买家/卖家订单详情页（IT 后）：**
- ✅ 订单状态保持 `On its way`（IT **不触发**页面状态变化）
- ✅ 进度条节点与 AC 后相同（`Paid + Dispatched` 激活，`Delivered` 未激活）
- ⚠️ 推断：物流轨迹追踪页最新记录更新为 `IT - Collected from ParcelShop`（未额外验证）

#### 📊 用例属性
- **优先级**: P1
- **Case ID**: `case_id_PAYSHIP_E2E_HOME_001`（Phase 4b）
- **UI自动化**: ✅ 已自动化

---

### TC-HD-020c: 物流状态-AT（派送中）→ 订单追踪更新，状态无变化

#### 📋 前置条件
- IT 状态已触发（TC-HD-020b），订单状态：`On its way`

#### 🎬 执行步骤
```python
response = webhook.trigger(tracking_number=tracking_number, status_code="AT")
assert response.status_code == 200
```

#### ✅ 预期结果

**买家/卖家订单列表页（AT 后）：**
- ✅ 订单卡片状态文字：`In progress | On its way`（与 IT 后**一致**，**无变化**）

**买家/卖家订单详情页（AT 后）：**
- ✅ 订单状态保持 `On its way`（AT **不触发**页面状态变化）
- ✅ 进度条节点与 IT 后相同
- ⚠️ 推断：物流追踪记录更新为 `AT - Out For Delivery`

> 💡 **注意**：AT 状态专用于到家配送的"派件员正在派送中"场景（自提点订单通常跳过 AT 直接进入 SP）。

#### 📊 用例属性
- **优先级**: P1
- **Case ID**: `case_id_PAYSHIP_E2E_HOME_001`（Phase 4c）
- **UI自动化**: ✅ 已自动化

---

### TC-HD-022: 物流状态-DE(HOME)（已投递到家）→ 订单"Delivered"

#### 📋 前置条件
- AT 状态已触发（TC-HD-020c），订单状态：`On its way`

#### 🎬 执行步骤
```python
response = webhook.trigger(
    tracking_number=tracking_number,
    status_code="DE",
    delivery_method="HOME"   # ⚠️ 到家配送必须传入 HOME
)
assert response.status_code == 200
```

#### ✅ 预期结果

**Webhook 调用：**
- ✅ HTTP 响应状态码：`200`
- ✅ event_code：`4238`，event_description：`This parcel has been delivered`

**买家订单列表页（DE 后）：**
- ✅ 订单卡片状态文字：`In progress | Delivered`
- ✅ `Track order` 按钮显示

**买家订单详情页（DE 后）：**
- ✅ `Order details` 区域状态：`Delivered`
- ✅ 显示 `Confirm by {D MMM}`（DE 触发后 +48小时 截止确认）
- ✅ 进度条激活节点：`Paid` + `Dispatched` + `Delivered ({D MMM})`（三个全部激活）
- ✅ 商品区域出现 **`I'm happy with my item`** 按钮（主操作：买家确认收货）
- ✅ 底部操作按钮：`Message seller` + `Track order` + `Report an issue`

**卖家订单列表页（DE 后）：**
- ✅ 状态文字：`In progress | Delivered`
- ✅ `Track order` 按钮显示

**卖家订单详情页（DE 后）：**
- ⚠️ 推断：状态显示 `Delivered`，等待买家确认
- ⚠️ 推断：支付状态消息变为：`The parcel is already delivered. Once the item is confirmed by the buyer, we will transfer the funds to your bank account.`

> ⚠️ **与自提点订单的区别**：
> - 自提点 DE：状态显示 `Picked up`（买家到店取件）
> - 到家 DE：状态显示 `Delivered`（投递到门）

#### 📊 用例属性
- **优先级**: P0
- **Case ID**: `case_id_PAYSHIP_E2E_HOME_001`（Phase 4d）
- **UI自动化**: ✅ 已自动化（_check_buyer_order_status 含 DE 后额外验证 "I'm happy with my item" 按钮）

---

## 模块6：买家签收与确认收货

### TC-HD-023: 买家手动确认收货-点击"I'm happy with my item"

#### 📋 前置条件
- 已登录买家账号
- 订单状态：`Delivered`（DE(HOME) Webhook 已触发）
- 买家订单详情页显示 `Confirm by {D MMM}` 且 `I'm happy with my item` 按钮可见

#### 🎬 执行步骤
1. 买家导航到订单详情页（`/order/{ORDER_ID}?type=bought`）
2. 查看商品区域，确认 "**I'm happy with my item**" 按钮可见
3. 点击 "**I'm happy with my item**" 按钮
4. 弹出 "Check your item" 确认弹窗
5. 在弹窗中再次点击 "**I'm happy with my item**" 确认按钮

#### ✅ 预期结果

**"Check your item" 确认弹窗（步骤 3 后）：**
- ✅ 弹窗标题：`Check your item`
- ✅ 说明文字：`Before confirming, please make sure you are happy with the item you have received. Once confirmed, your payment will be released to the seller.`（或类似文字）
- ✅ 确认按钮：`I'm happy with my item`（绿色/主操作）
- ✅ 问题按钮：`Report an issue`（次要操作）
- ✅ 关闭按钮：`Close`（或 ×）

**确认收货后买家订单详情页（步骤 5 后）：**
- ✅ `Order details` 区域状态变更为：**`Order Completed`**
- ✅ 进度条全部激活：`Paid ({D MMM})` + `Dispatched ({D MMM})` + `Delivered ({D MMM})` + **`Completed ({D MMM})`**
- ✅ 商品区域：`I'm happy with my item` → 变为 **`Leave a review`** 按钮
- ✅ `Report an issue` 按钮**消失**
- ✅ `Confirm by {D MMM}` 文字**消失**
- ✅ 底部操作按钮：`Message seller` + `Track order` + `Contact Customer Service`

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向（E2E 核心路径）
- **Case ID**: `case_id_PAYSHIP_E2E_HOME_001`（Phase 5）
- **UI自动化**: ✅ 已自动化（Phase 5 - _phase5_buyer_confirm_receipt，含弹窗二次确认逻辑）

---

### TC-HD-024: 最终状态校验-买卖双方订单均为 Order Completed

#### 📋 前置条件
- 买家已完成确认收货（TC-HD-023）

#### 🎬 执行步骤
1. **买家订单详情页**：导航到 `/order/{ORDER_ID}?type=bought`，校验状态
2. **买家订单列表页**：导航到 `/manage/orders`，查看订单状态
3. **卖家订单详情页**：导航到 `/order/{ORDER_ID}?type=sold`，校验状态
4. **卖家订单列表页**：导航到 `/manage/orders?type=sold`，查看订单状态

#### ✅ 预期结果

**买家订单详情页（Order Completed 状态）：**
- ✅ 状态：`Order Completed`
- ✅ 进度条全部激活（含 `Completed ({D MMM})`）
- ✅ 商品区域：`Leave a review` 按钮可见

**买家订单列表页：**
- ✅ 目标订单状态：`Completed`

**卖家订单详情页（Order Completed 状态）：**
- ✅ 状态：`Order Completed`
- ✅ 进度条全部激活
- ✅ 支付状态消息：`The order is complete and £20.00 will be transferred to your bank account.`
- ✅ `Leave a review` 按钮可见

**卖家订单列表页（Sold Tab）：**
- ✅ 目标订单状态：`Completed`

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/状态验收
- **Case ID**: `case_id_PAYSHIP_E2E_HOME_001`（Phase 6）
- **UI自动化**: ✅ 已自动化（Phase 6 - _phase6_verify_completed，含买卖双方详情+列表四处校验）

---

## 📊 用例统计

| 模块 | 用例数 | 实测 ✅ | 待实测 ⚠️ | P0 | P1 |
|------|--------|--------|----------|----|----|
| 模块1：卖家 API 发帖 | 1 | 0 | 1 | 1 | 0 |
| 模块2：买家浏览与下单 | 2 | 0 | 2 | 2 | 0 |
| 模块3：买家支付及订单校验 | 3 | 0 | 3 | 2 | 1 |
| 模块4：卖家创建物流面单 | 1 | 0 | 1 | 1 | 0 |
| 模块5：物流状态流转 | 4 | 0 | 4 | 2 | 2 |
| 模块6：签收与最终校验 | 2 | 0 | 2 | 2 | 0 |
| **合计** | **13** | **0** | **13** | **10** | **3** |

---

## 📋 附：Home Delivery Webhook 物流状态 UI 变化汇总（推断）

| Webhook 阶段 | 买家订单列表状态 | 买家订单详情状态 | 进度条激活节点 | 买家操作按钮变化 | 卖家操作按钮变化 |
|---|---|---|---|---|---|
| **下单成功（初始）** | In progress \| Awaiting dispatch | Awaiting Dispatch | Paid | View order details | Create Label |
| **创建面单后** | In progress \| Awaiting dispatch | Awaiting Dispatch | Paid | View order details | View Label |
| **AC（揽收）** | In progress \| On its way | On its way | Paid + Dispatched | Track order（Cancel消失） | Track order |
| **IT（运输中）** | In progress \| On its way（同AC） | On its way（同AC） | Paid + Dispatched | Track order | Track order |
| **AT（派送中）** | In progress \| On its way（同IT） | On its way（同IT） | Paid + Dispatched | Track order | Track order |
| **DE(HOME)（投递到家）** | In progress \| Delivered | Delivered，显示 `Confirm by {D MMM}` | Paid + Dispatched + Delivered | **I'm happy with my item**（商品区）+ Track order + Report an issue | Track order |
| **买家确认收货** | Completed | Order Completed | 全部激活 + Completed | Leave a review（商品区）+ Track order + Contact CS | Leave a review（商品区）+ Message buyer + Track order + Contact CS |

> ⚠️ **与自提点（PickupStore）流转的核心差异**：
> - 自提点：AC → IT → AT → **SP（到达自提点）→ DE(STORE)（取件）** → 买家确认
> - 到家：AC → IT → AT → **DE(HOME)（投递到家）** → 买家确认
> - 自提点 DE 后状态：`Picked up`；到家 DE 后状态：`Delivered`

---

## 🛠️ 测试工具配置

### 脚本文件
```
脚本路径: test_cases/payship/TC_PayShip_HomeDelivery_HappyPath.py
pytest 命令: pytest test_cases/payship/TC_PayShip_HomeDelivery_HappyPath.py --env=unicorn -v
Case ID Marker: case_id_PAYSHIP_E2E_HOME_001
```

### 物流状态 Webhook 工具类
```
工具类路径: test_cases/payship/utils/ship_webhook.py
类名: ShipWebhook

初始化参数:
  env_name (str): 环境名称，含 zoidberg/bixi/gaga/unicorn/stage 之一即可

trigger() 参数:
  tracking_number (str): TC-HD-018 面单创建后通过 API 获取的追踪号（必填）
  status_code (str): 物流状态码，取值 AC/IT/AT/DE（必填）
  delivery_method (str): DE 时必填，到家配送传 "HOME"

状态码与事件码对照（到家配送）:
  AC       → event_code: 1409 | Customer Sent via ParcelShop
  IT       → event_code: 1410 | Collected from ParcelShop
  AT       → event_code: 1032 | Out For Delivery
  DE+HOME  → event_code: 4238 | This parcel has been delivered
```

### 费用计算参考
```
商品价格: £20.00
到家配送费（Small 包裹）: £2.99
Buyer Protection: £20 × 5% + £0.70 = £1.70
总计: £20.00 + £2.99 + £1.70 = £24.69
```

### MangoPay 测试配置
```
卖家注册电话: +33 611111111
验证码: 702100
3DS 测试卡: 4970105181818183（Expiry: 12/28, CVV: 123）
普通测试卡: 4970107111111119（Expiry: 12/28, CVV: 123，VISA 尾号 1119）
```

---

**文档生成时间**: 2026-03-24  
**文档版本**: v1.0（基于脚本逻辑及 PickupStore v5.0 实测经验推断，待真实环境执行后补全实测结果）  
**关联脚本**: `test_cases/payship/TC_PayShip_HomeDelivery_HappyPath.py`  
**关联参考文档**: `test_cases/payship/TC_PayShip_PickupStore_HappyPath.md`
