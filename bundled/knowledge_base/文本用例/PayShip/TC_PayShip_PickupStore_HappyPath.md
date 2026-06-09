# Gumtree Pay & Ship - 端到端完整流程测试用例（实测版）

> **生成时间**: 2026-04-13  
> **探测方式**: Playwright MCP 工具实际探测 ✅（测试环境已恢复，基于真实行为输出）  
> **探测账号**: 卖家 gtauto5858@outlook.com / 买家 gtauto25858@outlook.com  
> **测试站点**: https://www.unicorn.gumtree.io/  
> **探测覆盖**: 卖家发布广告 → 买家购买（选择自提点）→ 支付成功 → 买卖双方订单列表/详情/快照全量元素校验 → 卖家创建面单（成功）→ Webhook AC/IT/SP/DE 物流状态推进 → 每阶段买卖双方订单列表/详情校验 → 买家点击确认收货 → 订单完成 → 买卖双方 Leave a review 评价流程  
> **文档版本**: v5.3（2026-04-16 更新：补充脚本健壮性实现细节，包括草稿弹窗处理、感谢页处理完整流程、地址建议6层兜底策略、弹窗确认3层兜底逻辑，更正TC025实现差异）

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
| `{YYYYMMDD}T{HHmmss}` | 广告标题中的时间戳部分 | `YYYYMMDDTHHmmss` | `20260413T200931` | 发布时取当前本地时间 |
| `{D MMM}` | 进度条节点日期 / 操作截止日期 | `D MMM`（无年份） | `13 Apr` | 页面动态显示，无需断言具体值，可用正则 `\d{1,2} [A-Z][a-z]{2}` |
| `{D MMM YYYY}` | 发货截止日期 / 面单到期日期 | `D MMM YYYY` | `22 Apr 2026` | 页面动态显示，断言格式即可 |
| `{DD-MM-YYYY, HH:MM:SS}` | 支付时间戳 | `DD-MM-YYYY, HH:MM:SS` | `14-04-2026, 11:16:41` | 页面动态显示，断言格式即可 |

---

## 🔑 实测关键发现（与 v1.0 推断的差异）

### ✅ 已确认的业务规则

| 规则 | 推断值 | 实测结果 |
|------|-------|------|
| Buyer Protection 费率 | 商品价格 × 5% + 0.7 | ✅ 确认：£20 × 5% + £0.7 = **£1.70** |
| 自提点配送费（小包裹） | £2.59 | ✅ 确认：**£2.59** |
| 到家配送费（小包裹） | £2.99 | ✅ 确认：**£2.99** |
| 结账页默认配送方式 | 推断配送到家 | ✅ 修正：**默认选中"Deliver to pick-up point"** |
| 配送服务商 | EVRi | ✅ 确认：**EVRi**（原 Hermes） |
| 结账页 URL | 推断 /checkout | ✅ 修正：**/create-order?advertId={advertId}** |
| 广告详情页 Buyer Protection 展示 | 推断在结账页显示 | ✅ 修正：**广告详情页已展示 "Buyer Protection £1.70"** |

### ⚠️ 实测修正内容

1. **自提点搜索交互**：v1.0 未描述完整流程。实测为：
   - 点击 "Choose a pick-up point" → 弹出搜索对话框（含地图）
   - 搜索框提示 "Type address or postcode"
   - 输入地址“24-26 Railway Street”后显示下拉建议（如 "Costcutter Supermarket 24-26 Railway Street, Altrincham WA14 2RE"）
   - 点击建议后展示附近 Evri ParcelShop 列表（默认按距离升序）
   - 点击第一条名为“LONDIS”的结果展开营业时间详情
   - 点击绿色 "**Choose this pick-up point**" 确认选择
   - 弹窗关闭，结账页显示已选自提点信息和 "**Change**" 链接

2. **Nearby 定位逻辑**：初始列表使用卖家广告位置（Great Yarmouth 附近）定位，与 v1.0 中"使用买家默认地址"的推断不同

3. **包裹尺寸选择 UI**：使用自定义下拉组件（非标准 `<select>`），需要先点击再按 **Space 键** 才能展开选项

4. **结账页已有支付方式**：买家测试账号已预绑定 VISA 卡（尾号 1119），无需新增

5. **广告详情页额外信息**：显示 "Delivery from £2.59 | Buyer Protection £1.70"（两个价格均在详情页可见）

---

## 📑 目录

- [模块1：卖家发布广告](#模块1卖家发布广告)
- [模块2：买家浏览与下单（含自提点选择）](#模块2买家浏览与下单含自提点选择)
- [模块3：买家支付](#模块3买家支付)
- [模块3B：下单成功后买卖双方订单页面元素校验](#模块3b下单成功后买卖双方订单页面元素校验)
- [模块4：卖家发货物流](#模块4卖家发货物流)
- [模块5：物流正向流转](#模块5物流正向流转)
- [模块6：买家签收与确认收货](#模块6买家签收与确认收货)

---

## 🔢 测试用例编号说明

### 📋 文档TC编号与脚本TC编号对应关系

本文档采用**业务流程顺序编号**，而测试脚本采用**执行顺序编号**，因此存在以下编号差异：

| 文档TC编号 | 脚本方法名 | 功能说明 | 编号差异原因 |
|-----------|-----------|---------|------------|
| **TC001-TC021** | `test_TC001` ~ `test_TC021` | 发布广告 → 下单 → 支付 → 创建面单 → Webhook物流 | ✅ **编号一致** |
| **TC022 (文档)** | `test_TC022_de_webhook` | DE Webhook（买家取件完成） | ✅ **编号一致** |
| **TC023 (文档)** | `test_TC023_buyer_confirm_receipt` | 买家手动确认收货 | ✅ **编号一致** |
| **Phase 11 - TC022 (文档)** | `test_TC025_buyer_leave_review` | 买家 Leave a review | ⚠️ **编号不同**：文档Phase 11的TC022对应脚本TC025 |
| **Phase 11 - TC023 (文档)** | `test_TC025_seller_leave_review` | 卖家 Leave a review | ⚠️ **编号不同**：文档Phase 11的TC023对应脚本TC025-seller |

### ⚠️ 编号差异原因

1. **文档编号逻辑**：
   - TC001-TC023：按**业务流程顺序**编号（发布→下单→支付→物流→确认收货）
   - Phase 11（TC022/TC023）：单独的评价流程章节，复用了TC022/TC023编号

2. **脚本编号逻辑**：
   - TC001-TC023：按**测试执行顺序**编号
   - TC025：评价流程在确认收货（TC023）之后执行，故编号为TC025

3. **触发方式差异**：
   - **买家评价**：文档与脚本一致，均从**订单详情页**触发
   - **卖家评价**：
     - 📝 文档描述：从**订单列表**点击 `Leave a review` 按钮触发
     - 🤖 脚本实现：从**订单详情页**点击 `Leave a review` 按钮触发
     - ✅ UI支持两种方式：订单列表和订单详情页均可触发评价弹窗

### 📌 快速查找对照表

**按脚本方法名查找文档用例**：

```python
# 脚本方法名 → 文档章节位置
test_TC025_buyer_leave_review      → Phase 11 - TC022（买家评价）
test_TC025_seller_leave_review     → Phase 11 - TC023（卖家评价）
```

**按文档用例查找脚本方法**：

```markdown
- 文档 Phase 11 - TC022（买家评价） → test_TC025_buyer_leave_review
- 文档 Phase 11 - TC023（卖家评价） → test_TC025_seller_leave_review
```

> 💡 **最佳实践**：在自动化脚本中，建议使用**脚本编号（TC025）**作为标准，以保持测试执行顺序的清晰性。文档中的Phase 11编号仅用于业务功能分组。

---

## 模块1：卖家发布广告

### TC001: 发布支持配送广告-完整正向流程（小包裹）

#### 📋 前置条件
- 已登录卖家账号（gtauto5858@outlook.com）
- 站点：https://www.unicorn.gumtree.io/

#### 🎬 执行步骤
1. 点击右上角 "Post an ad" 按钮
2. 选择类目路径：**For Sale → Clothes, Footwear & Accessories → Other**
3. 填写商品标题：`Delivery Store {YYYYMMDD}T{HHmmss} {时区}`
   - **标题格式说明**：每次发布广告标题需唯一，格式为 `Delivery Store` + 当前系统时间（精确到秒）+ 广告所在地邮编区号
   - **示例**：`Delivery Store 20260413T060141 WA14`（其中 WA14 为自提点邮编区号 `WA14 2RE` 的前缀）
   - ⚠️ **注意**：日期与时间之间必须使用字母 `T` 分隔（不可使用连字符 `-`），否则系统会误判为电话号码并报错："Please remove phone number from title"
4. 填写商品价格：`20`（英镑，在 1-250 区间内）
5. 点击图片上传区域，上传至少 1 张商品图片
6. 填写商品描述：`This is a QA test listing for automated testing purposes. Please do not purchase this item.`
7. 在 "Condition" 下拉框选择 `New`
8. 在 "Location" 字段确认已填写地址（默认应有值）
9. 在 "Delivery" 区域，开启 "Enable delivery" 开关
10. 在 "Parcel size" 下拉框：**先点击下拉框，再按 Space 键展开**，选择 `Small`
11. 点击 "Post ad"（或 "Preview ad"）按钮发布

#### ✅ 预期结果
- ✅ **实测**：广告发布成功，页面跳转到广告详情页
- ✅ **实测**：详情页标题与填写内容一致
- ✅ **实测**：右侧显示价格 **£20** 和 "**Buy now**" 按钮
- ✅ **实测**：详情页显示 "Delivery from **£2.59** | Buyer Protection **£1.70**"
- ✅ **实测**：面包屑显示：Home / For Sale / Clothes, Footwear & Accessories / Other / Private
- ✅ **实测**：广告 ID 在 URL 中可见（`/p/other-footwear/{title}/{ad-id}`）

#### 🤖 自动化实现细节

**草稿恢复弹窗处理**（步骤1后）：
- **问题**：点击 "Post an ad" 后可能弹出草稿恢复对话框（"Resume your draft" 或类似）
- **处理策略**：尝试2种按钮文本（`button:has-text('No thanks')` / `button:has-text('Discard')`），点击第一个可见的关闭草稿弹窗
- **定位器**：
  ```python
  for draft_sel in ("button:has-text('No thanks')", "button:has-text('Discard')"):
      loc = page.locator(draft_sel).first
      if loc.is_visible(timeout=2000):
          loc.click(force=True)
          break
  ```
- **容错性**：使用 `timeout=2000` 快速检测，若不存在则跳过（无副作用）

**等待关键元素加载**（步骤2后）：
- **关键点**：选择完分类点击 "Continue" 后，需等待广告创建表单完全加载
- **验证元素**：`ad-title-input`（广告标题输入框，`data-testid="ad-title-input"`）
- **等待策略**：`page.get_by_test_id("ad-title-input").wait_for(state="visible", timeout=30000)`
- **原因**：确保表单 DOM 完全渲染后再填写，避免 "元素未找到" 错误

**发布后跳转处理**（步骤11后）：
- **可能路径**：
  1. **直接跳转广告详情页**：URL 格式 `/p/other-footwear/{title}/{ad-id}`
  2. **跳转感谢页**：URL 格式 `/thankyou/` 或 `my.unicorn.gumtree.io/thankyou/*`
- **等待策略**：`page.wait_for_url(re.compile(r"(/p/|/thankyou/)"), timeout=120000)`（支持两种 URL 模式）
- **感谢页处理完整流程**（若跳转到 `/thankyou/`）：
  
  **策略1：查找 "View your ad" 链接**（优先）
  - 尝试6种选择器兜底：
    1. `a:has-text('View your ad')`
    2. `a:has-text('View ad')`
    3. `a:has-text('View Ad')`
    4. `button:has-text('View your ad')`
    5. `[data-q='view-ad']`
    6. 文本模糊匹配
  - 点击后等待跳转到 `/p/` 广告页
  
  **策略2：通过 /manage/ads 查找广告**（兜底）
  - 从感谢页 URL 提取 `advertId` 参数（正则：`advertId=(\d+)`）
  - 导航到 `/manage/ads` 页面
  - 通过 `a[href*='{advertId}']` 定位广告链接
  - 提取 `href` 属性，拼接完整 URL 后跳转
  
  **隐私弹窗处理**：
  - 发布广告成功后可能随时弹出隐私协议弹窗
  - 连续调用 `_dismiss_overlays()` 两轮，间隔 800ms
  - 清理可能的 Cookie 同意弹窗、隐私通知等遮罩层

**最终验证策略**：
- 记录广告详情页 URL 到类变量 `_ad_url`
- 验证广告标题可见（10秒超时）
- 验证配送费 £2.59 可见（10秒超时）
- 日志记录：`logger.info(f"✓ TC001: 广告已发布 → {page.url}")`

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向（Happy Path）
- **UI自动化**: ✅ 可自动化

---

### TC002: 发布广告-Enable delivery 展示条件校验

#### 📋 前置条件
- 已登录卖家账号
- 进入广告发布页面

#### 🎬 执行步骤
| 场景 | 类目 | 价格 | 预期 Enable delivery 开关 |
|------|------|------|--------------------------|
| 场景A | **非开放类目**（如 Jobs） | £50 | 不可见 |
| 场景B | 开放类目（Clothes Other） | **£0.99**（<1英镑） | 不可见 |
| 场景C | 开放类目（Clothes Other） | **£250.01**（>250英镑） | 不可见 |
| 场景D | 开放类目（Clothes Other） | **£20**（在区间内） | 可见且可操作 |

#### ✅ 预期结果（已全部实测）
- 场景A（非开放类目 Motors/Cars）：进入广告发布表单后 "Enable delivery" 开关**完全不显示** ✅ 实测确认
- 场景B（价格 £0.99 < £1）：
  - "Enable delivery" 开关**仍显示**，但状态为 **"No"** + **disabled（不可操作）**
  - Price 字段下方出现提示：**"Delivery is only available for items between £1 and £250."**
  - Enable delivery 区域显示 **"Item not eligible"** + **"Delivery is not available for items less than £1 or over £250."** + "Learn more" 按钮 ✅ 实测确认
- 场景C（价格 £250.01 > £250）：行为与场景B完全相同 ✅ 实测确认
- 场景D："Enable delivery" 开关**可见且可点击** ✅ 实测确认（TC001 中已验证）

> 💡 **Oracle 修正**：原预期场景A/B/C 开关"不可见"，实测结果为：
> - 场景A（非开放类目）：真的完全不显示
> - 场景B/C（开放类目但价格超范围）：开关**仍显示但 disabled**，并显示详细提示文案

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向/边界值
- **UI自动化**: ✅ 可自动化

---

### TC003: 发布广告-未选择包裹尺寸提交校验

#### 📋 前置条件
- 已登录卖家账号，进入广告发布页面
- 选择开放类目，填写价格 £20

#### 🎬 执行步骤
1. 开启 "Enable delivery" 开关
2. **不选择** Parcel size（保持空值）
3. 点击 "Post ad" 按钮

#### ✅ 预期结果
- 提交被阻止，页面不跳转 ✅ 实测确认（URL 不变）
- Parcel size 字段下方显示错误提示 **"Please select parcel size."** ✅ 实测确认
- 页面底部/顶部同时出现 Toast/Banner **"Almost there, but it looks like you've missed something?"** ✅ 实测确认
- 其他必填字段（Photos/Title/Description/Condition）也会一并显示各自的校验错误 ✅ 实测确认

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向/表单校验
- **UI自动化**: ✅ 可自动化

---

### TC004: My ads 列表-配送标签展示

#### 📋 前置条件
- 已登录卖家账号
- 存在一个**已开启配送**的广告（TC001 创建的广告）

#### 🎬 执行步骤
1. 点击 Menu → Manage my Ads
2. 查看 TC001 创建的广告卡片
3. 查找配送相关标签

#### ✅ 预期结果
- 已开启配送的广告卡片显示 **"Delivery enabled"** 标签 ✅ 实测确认（My Ads 列表中已验证多个广告均显示此标签）
- 未开启配送的广告（如价格 £0.01、£0.50）：广告卡片**不显示** "Delivery enabled" 标签 ✅ 实测确认
- > ⚠️ **Oracle 修正**：原预期"未开启配送的开放类目广告显示 Eligible for delivery"，实测结果为**不显示任何配送相关标签**

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

## 模块2：买家浏览与下单（含自提点选择）

### TC005: 广告详情页-Buy now 按钮展示验证

#### 📋 前置条件
- 已登录**买家账号**（gtauto25858@outlook.com）
- 访问卖家发布的已启用配送广告（TC001 的广告）
- 测试用广告 URL：`https://www.unicorn.gumtree.io/p/other-footwear/qa-test-item/{ad-id}`

#### 🎬 执行步骤
1. 导航到广告详情页 URL
2. 查看右侧区域

#### ✅ 预期结果
- ✅ **实测**：右侧显示价格 **£20** 和绿色 "**Buy now**" 按钮
- ✅ **实测**：显示 "Delivery from **£2.59** | Buyer Protection **£1.70**"
- ✅ **实测**：页面同时显示 "Message" 按钮（私信卖家）
- ✅ **实测**：卖家信息区显示 "Email address verified" 徽标

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC006: 广告详情页-本人广告不显示 Buy now

#### 📋 前置条件
- 以**卖家身份**登录
- 访问自己发布的已启用配送广告

#### 🎬 执行步骤
1. 以卖家账号登录（gtauto5858@outlook.com）
2. 访问自己发布的已启用配送广告（TC001 发布的广告）
3. 检查广告详情页右侧操作按钮区域

#### ✅ 预期结果
- ✅ **实测**：广告标题正确显示
- ✅ **实测**：Buy now 按钮**禁用状态**（`disabled`，按钮可见但不可点击，灰色显示）
  - ⚠️ **Oracle 修正**：原预期"不可见"，实测为**禁用可见**（卖家不能购买自己的广告）
- ✅ **实测**：`Delivery from £2.59` 配送费信息可见
- ✅ **实测**：`Buyer Protection £1.70` 买家保护费信息可见

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

### TC007: 结账页-默认显示"配送到自提点"并完成选择（E2E 核心路径）

#### 📋 前置条件
- 已登录买家账号（gtauto25858@outlook.com）
- 已在 TC005 中确认广告可购买
- 买家账号已绑定支付方式（实测：VISA 尾号 1119）

#### 🎬 执行步骤
1. 在广告详情页点击 "**Buy now**" 按钮
2. 跳转至结账页（URL：`/create-order?advertId={advertId}`）
3. 确认 "**Deliver to pick-up point**" 默认选中
4. 查看订单摘要
5. 点击 "**Choose a pick-up point**" 按钮
6. 弹出搜索对话框（含地图）
7. 在搜索框输入：`24-26 Railway Street`
8. 从下拉建议中点击：`Costcutter Supermarket 24-26 Railway Street, Altrincham WA14 2RE`
9. 搜索结果列表更新，第一条显示 "**LONDIS**" 旁有 "Nearest" 标签
10. 点击第一条结果（LONDIS, 24-26 Railway Street, Altrincham, WA14 2RE）
11. 展开详情页，显示 LONDIS 的营业时间
12. 点击绿色 "**Choose this pick-up point**" 按钮
13. 弹窗关闭，回到结账页

#### ✅ 预期结果
- ✅ **实测**：点击 Buy now 后，URL 跳转至 `/create-order?advertId=1001670514`（实测 ID）
- ✅ **实测**：结账页默认选中 "Deliver to pick-up point"（单选按钮已选中状态）
- ✅ **实测**：另一配送选项 "Home delivery £2.99" 未选中
- ✅ **实测**：订单摘要：Item subtotal **£20.00** / Delivery **£2.59** / Buyer Protection **£1.70** / Total to pay **£24.29**
- ✅ **实测**：点击 "Choose a pick-up point" 后弹出搜索对话框（含地图和 "Type address or postcode" 提示）
- ✅ **实测**：输入地址后自动显示地址建议下拉列表
- ✅ **实测**：选择地址建议后列表更新为附近 Evri 服务点，第一条带 "Nearest" 标签
- ✅ **实测**：点击列表项展开详情，显示店名（LONDIS）、地址、营业时间、距离（6m）
- ✅ **实测**：点击 "Choose this pick-up point" 后弹窗关闭
- ✅ **实测**：结账页 "Pick-up point" 区域更新为：
  - Evri ParcelShop / LONDIS / 24-26 Railway Street, Altrincham, WA14 2RE
  - 右侧显示 "**Change**" 链接

#### 🤖 自动化实现细节

**步骤1：点击 Buy now（实现差异说明）**
- **问题**：广告详情页可能有多个 Buy now 按钮（顶部 + sticky 底栏）
- **脚本实现**：使用 `.nth(1)` 选择第二个（sticky 区域的 Buy now）
  ```python
  page.get_by_role("button", name="Buy now").nth(1).click()
  ```
- **原因**：sticky 区域的按钮更稳定，避免页面滚动导致的超时问题
- **等待策略**：`page.wait_for_url(re.compile(r"/create-order"), timeout=20000)`

**步骤7：输入地址（健壮性处理）**
- **操作序列**：
  1. `addr_input.click()`：确保输入框获得焦点
  2. `addr_input.fill("")`：清空输入框（可能有缓存值）
  3. `page.keyboard.type(self.PICKUP_POINT_SEARCH, delay=80)`：模拟真实打字（delay 80ms，触发地址联想）
  4. 等待 **2500ms**：等待 Google Places API 返回地址建议
- **为什么不用 `fill()`**：直接 `fill()` 可能不触发地址联想的 `input` 事件

**步骤8：选择地址建议（6层兜底策略）**
- **难点**：Google Places 自动完成建议的 DOM 结构不稳定，选择器多样
- **策略1：尝试6种 CSS 选择器**（按优先级）
  1. `.pac-item`（Google Places API 标准）
  2. `.pac-container .pac-item`（带容器前缀）
  3. `.dialog-content li`（对话框内列表项）
  4. `.dialog-content [role='option']`（ARIA 角色）
  5. `.dialog-content [role='listitem']`
  6. `.dialog-content [class*='suggestion']`（类名模糊匹配）
  - 每个选择器使用 `timeout=5000` 尝试，若可见则点击并 break
- **策略2：文字模糊匹配**（兜底1）
  - 若策略1全失败，尝试查找包含以下文本的元素（全局搜索）：
    - "24-26 Railway"
    - "Railway Street"
    - "Altrincham"
  - 点击第一个可见元素（`timeout=2000`）
- **策略3：键盘导航**（兜底2）
  - 若策略1和2全失败，模拟键盘操作：
    - `page.keyboard.press("ArrowDown")`：选中第一条建议
    - 等待 300ms
    - `page.keyboard.press("Enter")`：确认选择
  - 日志警告：`logger.warning("⚠️ 建议选择兜底：ArrowDown + Enter")`
- **等待策略**：选择建议后等待 **4000ms**，等待搜索结果列表刷新

**步骤10：点击 LONDIS（超时保护）**
- **定位器**：`dialog_content.get_by_text(self.PICKUP_POINT_NAME).first`（使用 `.dialog-content` 作用域）
- **等待策略**：`londis.wait_for(state="visible", timeout=20000)`（20秒超时，环境可能较慢）
- **点击后等待**：`page.wait_for_timeout(1500)`（等待详情区域展开动画）

**步骤12：点击 Choose this pick-up point（视口处理）**
- **定位器**：
  ```python
  choose_btn = dialog_content.get_by_role("button", name="Choose this pick-up point")
  ```
- **关键操作**：`choose_btn.scroll_into_view_if_needed()`
  - **原因**：按钮可能在视口外（列表较长），直接点击会失败
  - **等待**：scroll 后等待 **300ms** 让滚动动画完成
- **点击后验证**：等待 `.dialog` 容器消失（`state="hidden", timeout=15000`）
  - **原因**：确保弹窗完全关闭，避免遮罩层干扰后续操作
- **最终清理**：`page.wait_for_timeout(500)` + `_dismiss_overlays()`

**关键等待时间汇总**：
- **2500ms**：输入地址后等待建议加载
- **4000ms**：选择建议后等待列表刷新
- **20000ms**：等待 LONDIS 可见（含 API 查询时间）
- **1500ms**：点击 LONDIS 后等待详情展开
- **15000ms**：等待弹窗关闭（含动画）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向（E2E 核心路径）
- **UI自动化**: ✅ 可自动化

---

### TC009: 结账页-自提点搜索-结果列表展示验证

#### 📋 前置条件
- 已登录买家账号，进入结账页（广告 £50.00），选择 "Deliver to pick-up point" 配送方式

#### 🎬 执行步骤
1. 在 "Pick-up point" 区域点击 "**Change**" 按钮 → 进入自提点选择面板
2. 查看初始 Tab 状态（Nearby / Recently used）
3. 在搜索框输入 `TW91EJ` → 选择地址自动补全建议
4. 查看搜索结果列表详情
5. 点击 "**Recently used**" Tab 验证历史记录

#### ✅ 预期结果（已全部实测）

**自提点选择面板入口区域（精确文案）：**
- ✅ **实测**：面板标题（Tab 标签）：`Nearby`（默认选中）、`Recently used`
- ✅ **实测**：搜索框 placeholder：`Enter your postcode...`
- ✅ **实测**：搜索框可直接交互（非 readonly）
- ✅ **实测**：搜索框右侧有 "📍" 定位图标按钮

**搜索行为（输入 TW91EJ）：**
- ✅ **实测**：输入后自动显示地址建议列表（格式：`地址名称 / 城市 邮编`，如：`Buckingham Palace / London TW91EJ`）
- ✅ **实测**：点击地址建议后，搜索框更新为选中地址
- ✅ **实测**：Nearby 列表立即刷新为该位置附近的自提点列表

**Nearby 搜索结果列表（精确元素，每条记录包含）：**
- ✅ **实测**：类型标签（如：`Evri ParcelShop` 或 `Evri Locker`）
- ✅ **实测**：价格：`£3.49`（统一显示）
- ✅ **实测**：店名（如：`LONDIS`、`McColl's`）
- ✅ **实测**：地址（完整街道+城市+邮编）
- ✅ **实测**：配送时效：`2-4 business days`
- ✅ **实测**：`Opening hours` 链接（点击展开营业时间详情）
- ✅ **实测**：距离（格式：`2.0km`，最近处带 `Nearest` 红色标签）
- ✅ **实测**：搜索结果列表约显示 10 条记录
- ✅ **实测**：最近的记录带 `Nearest` 标签

**Recently used Tab（精确文案）：**
- ✅ **实测**：点击 "Recently used" Tab 切换 → 显示上次选择过的自提点（历史记录）
- ✅ **实测**：记录格式与 Nearby 相同（店名/地址/价格/距离）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向
- **UI自动化**: ✅ 可自动化

---

### TC010: 结账页-费用计算校验 + 自提点确认

#### 📋 前置条件
- 已登录买家账号，进入结账页

#### 🎬 执行步骤（配送到自提点 + 确认自提点）
1. 选择 "Deliver to pick-up point"，搜索并点击一个自提点（如 LONDIS）
2. 在自提点详情面板点击 "**Choose this pick-up point**"
3. 查看右侧订单摘要

#### ✅ 预期结果（全部实测）

**点击自提点展开详情面板（精确文案）：**
- ✅ **实测**：面板顶部：类型+价格（如：`Evri ParcelShop £3.49`）
- ✅ **实测**：店名（如：`LONDIS`）
- ✅ **实测**：地址（如：`24-26 Railway Street, Altrincham, WA14 2RE`）
- ✅ **实测**：完整营业时间：`Mon - Sat 07:00 - 23:00`、`Sun 09:00 - 23:00`（展开显示）
- ✅ **实测**：按钮：`Choose this pick-up point`

**点击 "Choose this pick-up point" 后结账页更新：**
- ✅ **实测**："Pick-up point" 区域显示选中的自提点完整信息
  - 配送类型：`Evri ParcelShop`
  - 价格：`£3.49`
  - 店名：`LONDIS`
  - 地址：`24-26 Railway Street, Altrincham, WA14 2RE`
  - 时效：`At pick-up point in 2-4 business days`
  - "Change" 按钮（可重新选择）

**费用计算（配送到自提点，商品 £50.00）：**
- ✅ **实测**：Item subtotal = **£50.00**
- ✅ **实测**：Delivery = **£3.49**（Evri ParcelShop 自提点）
- ✅ **实测**：Buyer Protection = **£3.20**（计算公式：£50 × 5% + £0.7 = **£3.20** ✅ 验证正确）
- ✅ **实测**：Total = **£56.69**（50.00 + 3.49 + 3.20 = 56.69 ✅ 计算正确）

**费用计算（配送到家，同一 £50 商品）：**
- ✅ **实测**：Item subtotal = **£50.00**
- ✅ **实测**：Delivery = **£6.59**（Home delivery）
- ✅ **实测**：Buyer Protection = **£3.20**
- ✅ **实测**：Total = **£59.79**（50.00 + 6.59 + 3.20 = 59.79 ✅ 计算正确）

> 💡 **Buyer Protection 计算公式验证**：£50 × 5% + £0.7 = £3.20 ✅

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/计算校验
- **UI自动化**: ✅ 可自动化

---

## 模块3：买家支付

### TC011: 使用已保存银行卡支付-E2E 核心路径

#### 📋 前置条件
- 已登录买家账号（测试账号已绑定 VISA 尾号 1119）
- 已在结账页选择好配送到自提点（LONDIS, 24-26 Railway Street）
- 结账页显示 "Confirm & Pay" 按钮

#### 🎬 执行步骤
1. **前置校验**：确认结账页（`/create-order`）自提点仍处于已选中状态
   - ✅ **脚本新增防御**：检查 URL 仍为 `/create-order`
   - ✅ **脚本新增防御**：检查 "Evri ParcelShop / LONDIS" 自提点名称可见
   - ⚠️ **环境问题处理**：若自提点丢失（页面刷新或状态重置），脚本将自动重新选择：
     - 点击自提点搜索输入框，移除 `readonly` 属性
     - 输入 `24-26 Railway Street`
     - 从结果列表选择 LONDIS
     - 点击 "Choose this pick-up point" 确认
2. 在 "Payment method" 区域：
   - 显式点击 **VISA 卡区域**（确保激活选中状态，尾号 1119）
   - 确认卡片已选中（视觉高亮/边框变化）
3. 点击 "**Confirm & Pay**" 按钮
4. 等待支付结果（约 60-120 秒，取决于环境响应速度）

#### ✅ 预期结果

**支付成功后跳转页（/payment-result）：**
- ✅ **实测**：页面 URL 跳转至 `/payment-result`
- ✅ **实测**：页面顶部显示标题：`Thanks for your order, {买家用户名}!`（实测："Thanks for your order, gt2!"）
  - ⚠️ **脚本实现**：使用模糊匹配 `to_contain_text("Thanks for your order")`，未严格校验用户名
- ✅ **实测**：显示成功消息：`Your order was placed successfully`
- ✅ **实测**：显示发货截止提示：`Will be dispatched by` + 日期（格式：`D MMM YYYY`）
- ✅ **实测**：显示订单号区域：`Order No.` 标签 + 8位数字（实测：`13800118`）
- ✅ **实测**：显示购买商品标题（实测：`Delivery Store 20260413T060141 WA14`）
- ✅ **实测**：显示总支付金额（实测：`£13.79`，即 £10.00 + £2.59 + £1.20）
  - ⚠️ **脚本缺失**：未在 /payment-result 页明确校验 `£24.29` 或 `Total` 文案，仅提取订单号
- ✅ **实测**：显示配送方式：`Deliver to pick-up point`
- ✅ **实测**：显示自提点名称：`LONDIS`
- ✅ **实测**：显示支付方式：`VISA` 卡信息（尾号 1119）
  - ⚠️ **脚本缺失**：未在 /payment-result 页明确校验 VISA 文案
- ✅ **实测**：买家可在 "My Orders" 中查看订单（状态：`In progress | Awaiting dispatch`）
- ✅ **实测**：卖家侧 "Sold" 列表中自动出现该订单（状态：`In progress | Awaiting dispatch`）
- 买家收到支付成功邮件通知 ⚠️ 待实测确认

> **📌 本次实测参数**：广告价格 £10.00，Buyer Protection = £10 × 5% + £0.7 = **£1.20**，总计 £13.79

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向（E2E 核心路径）
- **UI自动化**: ✅ 可自动化

---

## 模块3B：下单成功后买卖双方订单页面元素校验

> **前置说明**：TC011 支付成功后，买家和卖家双方均需登录各自账号，分别进入订单列表和订单详情页，逐一校验所有页面元素。

### TC011b: 买家订单列表页（My Orders / Bought）-下单成功后元素校验

#### 📋 前置条件
- 已登录买家账号（gtauto25858@outlook.com）
- TC011 支付操作已成功完成
- 进入：Menu → My Orders → 默认显示 Bought Tab

#### 🎬 执行步骤
1. 点击 Menu → My Orders（买家侧）
2. 默认显示 `Bought` Tab（买家已购订单）
3. 在列表中找到 TC001 对应的订单（标题含 "Delivery Store"）

#### ✅ 预期结果（订单列表页元素全量校验）

**页面级元素：**
- ✅ **实测**：页面 URL：`/manage/orders`
- ✅ **实测**：浏览器 Tab 标题：`Order List | My Gumtree - Gumtree`
- ✅ **实测**：页面区域标题：`My orders`
- ✅ **实测**：内部 Tab 栏包含 `Bought`（选中）和 `Sold` 两个子 Tab
  - ⚠️ **修正**：原推断为 Active/Completed/Cancelled，实测为 **Bought / Sold** 二级分类
- ✅ **实测**：筛选下拉框（Filter）：选项包含 `All`（默认）/ `In progress` / `Completed` / `Cancelled` / `Suspended`

**目标订单卡片元素：**
- ✅ **实测**：订单状态标签（多种，精确文案）：
  - 待发货：`In progress | Awaiting dispatch`
  - 已取消：`Cancelled`
  - ⚠️ **修正**：原推断为 `Awaiting dispatch`，实测含前缀 `In progress | `
- ✅ **实测**：状态标签右侧带三点（...）图标按钮（展开更多操作）
- ✅ **实测**：商品缩略图（可点击，链接到 `/order/{id}?type=bought`）
- ✅ **实测**：商品标题（可点击链接，链接到 `/order/{id}?type=bought`）
- ✅ **实测**：商品单价（可点击链接，如 `£50.00`）
- ✅ **实测**：`View order details` 按钮（可点击进入订单详情）
- ✅ **实测**：订单编号文案格式：`Order number: {8位数字}`（如 `Order number: 13800868`）

**分页导航（精确元素）：**
- ✅ **实测**：每页显示 10 条订单
- ✅ **实测**：底部分页导航：`← 上一页` / `1 2 3 4 ...` / `→ 下一页`
- ✅ **实测**：当前页码高亮显示（格式：`current page, 1`）
- ✅ **实测**：非当前页格式：`View page {n}`

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/UI元素校验
- **UI自动化**: ✅ 可自动化

---

### TC011c: 买家订单详情页-下单成功后全量元素校验

#### 📋 前置条件
- 已登录买家账号（gtauto25858@outlook.com）
- 从订单列表（TC011b）点击 "View order details" 进入对应订单详情页

#### 🎬 执行步骤
1. 点击 Menu → My Orders（URL: `/manage/orders`）
2. 在 Bought Tab 的列表中点击目标订单的 "View order details" 按钮
3. 进入订单详情页，逐一校验页面所有展示元素

#### ✅ 预期结果（订单详情页元素全量校验）

**页面级元素：**
- ✅ **实测**：URL 格式：`/order/{orderId}?type=bought`
- ✅ **实测**：浏览器 Tab 标题：`OrderDetail | My Gumtree - Gumtree`
- ✅ **实测**：`← Back` 返回按钮（文案：`Back`，左侧带箭头图标）

**订单头部区域（精确文案）：**
- ✅ **实测**：区域标题：`Order details`
- ✅ **实测**：订单号文案格式：`Order No. : {8位数字}`（如 `Order No. : 13800868`）
- ✅ **实测**：当前状态（大字）：`Awaiting Dispatch`
- ✅ **实测**：截止发货提示文案：`Will be dispatched by: {D MMM YYYY}`（如 `Will be dispatched by: 22 Apr 2026`）

**进度条区域（精确节点文案）：**
- ✅ **实测**：自提点订单进度条显示 **4 个节点**（非 Home delivery 的 3 节点）：
  - 第1节点：`Paid`（已激活，含日期如 `13 Apr`）
  - 第2节点：`Dispatched`（未激活）
  - 第3节点：`Arrived`（未激活）
  - 第4节点：`Picked up`（未激活）
- > ⚠️ **重要区分**：
  >   - **自提点订单**（Deliver to pick-up point）：4节点（Paid → Dispatched → Arrived → Picked up）
  >   - **到家配送订单**（Home delivery）：3节点（Paid → Dispatched → Delivered）
  >   - 本用例为自提点流程，故为 4 节点

**商品信息区域（精确文案）：**
- ✅ **实测**：区域标题：`Item`
- ✅ **实测**：商品数量徽章：`1`（叠加在缩略图上）
- ✅ **实测**：商品缩略图（可点击，链接到 `/order-snapshot/{id}?type=bought`）
- ✅ **实测**：商品标题（可点击链接，指向订单快照）
- ✅ **实测**：商品价格（可点击链接，如 `£20.00`）
- ✅ **实测**：`View Snapshot` 按钮
- ✅ **实测**：`Message seller` 按钮（区域右侧）

**费用明细区域（精确文案和字段名 - 基于脚本实测£20商品）：**
- ✅ **实测**：区域标题：`Order summary`
- ✅ **实测**：行1：`Item subtotal` + `£20.00`
- ✅ **实测**：行2：`Delivery` + `£2.59`（自提点小包裹配送费）
- ✅ **实测**：行3：`Buyer Protection` + `£1.70`（带 ℹ️ 图标可点击）
- ✅ **实测**：行4：`Total` + `£24.29`（含 VAT 说明文案）

**配送信息区域（精确字段名和格式 - 自提点订单）：**
- ✅ **实测**：区域标题：`Pick-up point`（非 Home delivery 的 "Delivery address"）
- ✅ **实测**：配送方式：`Deliver to pick-up point`
- ✅ **实测**：自提点信息：
  - 类型+价格：`Evri ParcelShop £2.59`
  - 店名：`LONDIS`
  - 地址：`24-26 Railway Street, Altrincham, WA14 2RE`
  - 时效：`At pick-up point in 2-4 business days`

**支付信息区域（精确字段名）：**
- ✅ **实测**：区域标题：`Payment method`
- ✅ **实测**：展示格式：卡片图标 + `VISA ending in 1119`
- ⚠️ **脚本缺失**：支付时间戳校验（文档中提及的 `{DD-MM-YYYY, HH:MM:SS}` 格式）

**底部操作按钮区域（Awaiting Dispatch 状态）：**
- ✅ **实测**：`Message seller` 按钮
- ✅ **实测**：`Contact Customer Service` 按钮
- ✅ **实测**：`Cancel order` 按钮

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/UI元素校验
- **UI自动化**: ✅ 可自动化

---

### TC011c-snap: 买家订单快照页-下单成功后元素校验

#### 📋 前置条件
- 已登录买家账号
- 已进入买家订单详情页（TC011c）

#### 🎬 执行步骤
1. 在订单详情页点击 `View Snapshot` 按钮（或点击商品标题/图片链接）
2. 进入订单快照页
3. 逐一校验页面所有展示元素

#### ✅ 预期结果（订单快照页元素全量校验）

**页面级元素：**
- ✅ **实测**：URL 格式：`/order-snapshot/{orderId}?type=bought`（实测：`/order-snapshot/1380011800000000000002997260?type=bought`）
- ✅ **实测**：`← Back` 返回按钮（点击回到订单详情页）
- ✅ **实测**：页面标题：`[Snapshot]: Delivery Store 20260413T060141 WA14`

**图片区域：**
- ✅ **实测**：`Images` Tab（选中状态）
- ✅ **实测**：图片列表（列表框形式，实测 1 张图片）
- ✅ **实测**：图片翻页指示器：`1 of 1`
- ✅ **实测**：上/下翻页按钮（图片只有 1 张时可禁用）

**商品信息区域：**
- ✅ **实测**：`Description` 区域标题
- ✅ **实测**：描述文本：`Test item for QA automation - pay and ship e2e test. Please ignore this listing.`
- ✅ **实测**：Ad ID：`Ad ID: 1001670624`

**价格及费用区域：**
- ✅ **实测**：商品价格：`£10.00`
- ✅ **实测**：配送费说明：`Delivery from £2.59`
- ✅ **实测**：分隔符：`|`
- ✅ **实测**：买家保护费说明：`Buyer Protection £1.20`

**卖家信息区域：**
- ✅ **实测**：卖家头像（字母缩写形式，实测显示 "a"）
- ✅ **实测**：卖家用户名：`autogt`

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/UI元素校验
- **UI自动化**: ✅ 可自动化

---

### TC011d: 卖家订单列表页（My Orders / Sold）-下单成功后元素校验

#### 📋 前置条件
- 已**切换登录卖家账号**（gtauto5858@outlook.com）
- TC011 买家支付成功后，卖家侧订单自动生成
- 进入：Menu → My Orders → 切换至 `Sold` Tab

#### 🎬 执行步骤
1. 使用卖家账号登录
2. 点击 Menu → My Orders（卖家侧）
3. 默认显示 `Bought` Tab，需手动切换至 `Sold` Tab
4. 在列表中找到 "Delivery Store" 标题订单

#### ✅ 预期结果（卖家订单列表页元素全量校验）

**页面级元素：**
- ✅ **实测**：URL：`/manage/orders?type=sold`
- ✅ **实测**：浏览器 Tab 标题：`Order List | My Gumtree - Gumtree`
- ✅ **实测**：页面区域标题：`My orders`
- ✅ **实测**：内部 Tab 栏：`Bought` / `Sold`（选中状态）
  - ⚠️ **修正**：原推断存在 `Active/Completed/Cancelled`，实测买卖双方共用同一 Tab 结构（Bought / Sold 区分身份）
- ✅ **实测**：筛选下拉框（Filter）：`All`（默认）/ `In progress` / `Completed` / `Cancelled` / `Suspended`

**目标订单卡片元素：**
- ✅ **实测**：订单状态标签：`In progress | Awaiting dispatch`
- ✅ **实测**：右上角三点菜单按钮（展开更多操作）
- ✅ **实测**：商品缩略图（可点击，链接到卖家侧订单详情 `/order/{orderId}?type=sold`）
- ✅ **实测**：商品标题：`Delivery Store 20260413T060141 WA14`（可点击链接）
- ✅ **实测**：商品售价：`£10.00`（可点击链接）
- ✅ **实测**：发货倒计时提示：⏰ 图标 + `7 day(s) left to send`（距发货截止剩余天数）
- ✅ **实测**：`Create Label` 按钮（Awaiting dispatch 状态下在卡片上直接展示）
  - ⚠️ **修正**：原推断按钮文本为 `Ship item`，实测为 `Create Label`
- ✅ **实测**：订单编号格式：`Order number: {ORDER_NO}`（8位数字）

**分页导航：**
- ✅ **实测**：页面底部显示分页导航（实测共 4+ 页，当前在第 1 页）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/UI元素校验
- **UI自动化**: ✅ 可自动化

---

### TC011e: 卖家订单详情页-下单成功后全量元素校验

#### 📋 前置条件
- 已登录卖家账号
- 从卖家订单列表（TC011d）点击商品标题进入对应订单详情页

#### 🎬 执行步骤
1. 在卖家订单列表（Sold Tab）中点击商品标题或图片
2. 进入卖家侧订单详情页
3. 逐一校验页面所有展示元素

#### ✅ 预期结果（卖家订单详情页元素全量校验）

**页面级元素：**
- ✅ **实测**：URL 格式：`/order/{ORDER_ID}?type=sold`
- ✅ **实测**：`← Back` 返回按钮（点击回到卖家订单列表）

**订单头部区域：**
- ✅ **实测**：区域标题：`Order details`
- ✅ **实测**：订单号格式：`Order No. : {ORDER_NO}`（8位数字）
- ✅ **实测**：订单状态：`Awaiting Dispatch`
- ✅ **实测**：发货截止日期：`Dispatch by: 21 Apr 2026`

**进度条区域：**
- ✅ **实测**：4 节点进度条：`Paid`（已激活，含日期 "13 Apr"）→ `Dispatched`（未激活）→ `Arrived`（未激活）→ `Picked up`（未激活）

**商品信息区域（Item）：**
- ✅ **实测**：区域标题：`Item`
- ✅ **实测**：商品数量徽章 `1`（可点击，链接到卖家侧订单快照）
- ✅ **实测**：商品缩略图（可点击，链接到卖家侧订单快照）
- ✅ **实测**：商品标题：`Delivery Store 20260413T060141 WA14`（可点击链接，指向卖家侧订单快照）
- ✅ **实测**：商品售价：`£10.00`（可点击链接，指向卖家侧订单快照）
- ✅ **实测**：`View Snapshot` 按钮（点击跳转至卖家侧广告快照页）
- ✅ **实测**：`Create Label` 按钮（Awaiting Dispatch 状态下在商品信息区域内直接展示）
  - ⚠️ **修正**：原推断按钮名称为 `Ship item`，实测为 `Create Label`

**费用明细区域（Order summary）：**
- ✅ **实测**：区域标题：`Order summary`
- ✅ **实测**：Item subtotal：`£10.00`
- ✅ **实测**：Delivery：`£2.59`
- ✅ **实测**：Buyer Protection：`£1.20`（含 ℹ️ 信息图标）
- ✅ **实测**：Total（含 VAT 说明）：`£13.79`

**配送地址区域（Delivery address）：**
- ✅ **实测**：区域标题：`Delivery address`
- ✅ **实测**：买家姓名：`gt2 auto`
- ✅ **实测**：地址内容：`Address available on delivery label`（面单未创建前，实际地址隐藏）
  - ⚠️ **重要发现**：卖家在面单创建前**无法看到买家收货地址**，地址仅在物流面单上显示

**支付状态区域：**
- ✅ **实测**：图标（支付相关图标）
- ✅ **实测**：区域标题：`Payment status`
- ✅ **实测**：文本：`The buyer has already paid. Once the item is delivered and confirmed by the buyer, we will transfer the funds to your bank account.`

**操作按钮区域：**
- ✅ **实测**：`Message buyer` 按钮
- ✅ **实测**：`Contact Customer Service` 按钮
- ✅ **实测**：`Cancel order` 按钮（Awaiting Dispatch 状态下可见）
  - ⚠️ **修正**：原推断有 `Message buyer/Contact buyer` 按钮，实测为 `Message buyer`

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/UI元素校验
- **UI自动化**: ✅ 可自动化

---

### TC011e-snap: 卖家订单快照页-下单成功后元素校验

#### 📋 前置条件
- 已登录卖家账号
- 已进入卖家订单详情页（TC011e）

#### 🎬 执行步骤
1. 在卖家订单详情页点击 `View Snapshot` 按钮（或点击商品标题/图片/数量徽章链接）
2. 进入卖家侧订单快照页
3. 逐一校验页面所有展示元素

#### ✅ 预期结果（卖家订单快照页元素全量校验）

**页面级元素：**
- ✅ **实测**：URL 格式：`/order-snapshot/{orderId}?type=sold`（实测：`/order-snapshot/1380011800000000000002997260?type=sold`）
- ✅ **实测**：`← Back` 返回按钮（点击回到卖家订单详情页）
- ✅ **实测**：页面标题：`[Snapshot]: Delivery Store 20260413T060141 WA14`

**图片区域：**
- ✅ **实测**：`Images` Tab（选中状态）
- ✅ **实测**：图片列表（列表框形式，实测 1 张图片）
- ✅ **实测**：图片翻页指示器：`1 of 1`
- ✅ **实测**：图片翻页按钮（图片仅 1 张时不可翻）

**商品信息区域：**
- ✅ **实测**：`Description` 区域标题
- ✅ **实测**：描述文本：`Test item for QA automation - pay and ship e2e test. Please ignore this listing.`
- ✅ **实测**：Ad ID：`Ad ID: 1001670624`

**价格及费用区域：**
- ✅ **实测**：商品价格：`£10.00`
- ✅ **实测**：配送费说明：`Delivery from £2.59`
- ✅ **实测**：分隔符：`|`
- ✅ **实测**：买家保护费说明：`Buyer Protection £1.20`

**卖家信息区域：**
- ✅ **实测**：卖家头像（字母缩写，实测显示 "a"）
- ✅ **实测**：卖家用户名：`autogt`

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/UI元素校验
- **UI自动化**: ✅ 可自动化

---

## 模块4：卖家发货物流

### TC018: 卖家创建面单-完整流程（已注册 MangoPay）

#### 📋 前置条件
- 已登录卖家账号（gtauto5858@outlook.com，已完成 MangoPay 卖家注册）
- TC011 买家支付成功，且 TC011d 卖家订单列表已可见该订单（状态：`Awaiting dispatch`）

#### 🎬 执行步骤

**Step 1：在卖家订单详情页点击 Create Label**
1. 从 TC011e 卖家订单详情页点击 `Create Label` 按钮
   - 或从 TC011d 卖家订单列表卡片直接点击 `Create Label` 按钮

**Step 2：查看创建面单信息确认页**
2. 页面跳转至 `/shipping-label/create?orderId={orderId}&source=OrderDetail`
3. 确认 "Send with"、"Return address"、"Recipient address" 各区域信息
4. （可选）点击 "Find a drop-off location" 为卖家选择 Evri 投递点

**Step 3：点击 Continue 确认并生成面单**
5. 点击 `Continue` 按钮（确认条款并触发面单生成）
6. 等待面单生成结果

#### ✅ 预期结果

**创建面单信息确认页（Step 2）：**
- ✅ **实测**：URL：`/shipping-label/create?orderId={orderId}&source=OrderDetail`
- ✅ **实测**：页面一级标题（h1）：`Create label`
- ✅ **实测**：`← Back` 返回按钮
- ✅ **实测**："Send with" 区域（h2），包含：
  - 子标题（h3）：`Evri drop-off point`
  - 说明文本：`paid by buyer`
  - 可点击区域：`Find a drop-off location`（含右箭头图标，用于卖家选择投递点）
- ✅ **实测**："Return address" 区域（h2），包含：
  - `Change` 按钮（修改退件地址）
  - 卖家姓名（h3）：`gt auto`（从卖家个人中心自动读取）
  - 地址：`Swiss House, Bush Road, Great Yarmouth`
  - 邮编：`NR29 4BY`
  - 手机：`07123456789`
- ✅ **实测**："Recipient address" 区域（h2），包含：
  - 买家姓名（h3）：`gt2 auto`
  - 说明文本：`This address is automatically added to the shipping label.`（收件地址不在页面显示，自动写入面单）
- ✅ **实测**：`Continue` 按钮（主要操作按钮）
- ✅ **实测**：条款文本：`By clicking "continue" you acknowledge and accept that your item is subject [Gumtree Terms and Conditions] or carriage. You are also responsible for checking your item can be sent within the UK.`

**面单生成成功页（Step 3 - 实测结果，基于 2026-04-20 MCP 快照）：**
- ✅ **实测**：URL 跳转至 `/shipping-label/generated?orderId={orderId}` 或 `/shipping-label/{orderId}`
- ✅ **实测**：页面一级标题（h1）：`Label Generated`（⚠️ UI已更新，旧版为 "Your label is ready!"）
- ✅ **实测**：提示说明文本：`We sent a QR code and a label to your email address.`（⚠️ UI已更新，旧版为 "Congratulations, your shipping label has been created..."）
- ✅ **实测**：面单有效期文案（动态日期计算）：`This label will be valid until {创建日期+8天}.`
  - 格式示例：`This label will be valid until 28 Apr.`（日期格式：`D MMM.`，含句号）
  - 日期元素为 `<strong>` 标签，独立可定位
  - ⚠️ **自动化注意**：测试脚本需动态计算 `datetime.now() + timedelta(days=8)` 生成预期日期字符串
- ✅ **实测**：`Find a drop-off location` 文本（可点击区域，非标准链接）
- ✅ **实测**：二级标题（h2）：`Evri QR Code`
- ✅ **实测**：**QR 码图片**显示（`<img alt="QR Code">`，通过 alt 属性精准定位，避开隐藏的 tracking 像素图片）
- ✅ **实测**：**Tracking Number 二级标题（h2）**：显示追踪号短码（如 `H06Z5A`，页面仅显示前 6 位）
  - 完整追踪号（如 `H06Z5A0000017876`）需通过 proxy API 获取：
  - API: `GET https://proxy-seller.thirdparty.unicorn.gumtree.io/order/ui/orderDetail?orderId={orderId}`
  - 响应路径: `data.shippingDetail.trackingNumber`
- ✅ **实测**：`Save QR code` 按钮（下载 QR 码图片）
- ✅ **实测**：`Download label` 按钮（下载完整面单 PDF）
- ✅ **实测**：`Find a drop-off location` 链接（外部链接，查找投递点）
- ✅ **实测**：卖家订单详情页状态仍为 `Awaiting Dispatch`（面单已创建，尚未交承运商）
- ✅ **实测**：卖家订单详情页 `Create Label` 按钮 → 变为 `View Label` 按钮（面单已生成标志）
- ✅ **实测**：卖家订单列表卡片 `Create Label` 按钮 → 变为 `View Label` 按钮

**⚠️ 环境错误重试（注意事项）：**
> 若点击 `Continue` 后出现弹窗：
> - 标题：`Label generation failed`
> - 内容：`Calling logistics service failed. Please try again later.`
> - 按钮：`Retry` / `Contact Customer Service` / `Close`
>
> → 点击 `Retry` 重试，最多重试 **5 次**；5 次后仍失败则报告环境问题并停止。

> ✅ **重要**：面单创建成功后必须**记录 Tracking Number（追踪号）**（通过 proxy API 获取完整追踪号），后续物流 webhook 调用（模块5）需要使用此追踪号。

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向（E2E 核心路径）
- **UI自动化**: ✅ 可自动化

---

## 模块5：物流正向流转

> **注意**：以下场景通过调用 **`utils/ship_webhook.py`** 工具类模拟物流商（EVRi）回调状态变更。
>
> **工具类使用方式（Python）：**
> ```python
> from test_cases.PayShip.utils.order_api import get_tracking_number
> from test_cases.PayShip.utils.ship_webhook import ShipWebhook
>
> # 动态获取追踪号（从订单详情页 URL 提取 ORDER_ID）
> tracking_number = get_tracking_number(order_id="{ORDER_ID}", env="unicorn")
>
> webhook = ShipWebhook(env_name="unicorn")
>
> # 调用示例：触发 AC 状态
> response = webhook.trigger(
>     tracking_number=tracking_number,
>     status_code="AC"
> )
>
> # SP 自提点到达（需指定 delivery_method）
> response = webhook.trigger(
>     tracking_number=tracking_number,
>     status_code="SP",
>     delivery_method="STORE"  # 自提商店
> )
>
> # DE 买家取件（自提商店）
> response = webhook.trigger(
>     tracking_number=tracking_number,
>     status_code="DE",
>     delivery_method="STORE"
> )
> ```
>
> **自提订单完整物流流转**：AC → IT → AT → SP → DE
>
> **各状态说明**：
> | Status Code | 触发时机 | 买家订单状态变化 |
> |-------------|----------|-----------------|
> | AC | 承运商揽收包裹 | Awaiting dispatch → **On its way** |
> | IT | 包裹在途中 | On its way（无状态变化，追踪更新）|
> | AT | 包裹派送中 | On its way（追踪更新）|
> | SP | 包裹到达自提点 | On its way → **Arrived** |
> | DE | 买家已取件 | Arrived → **Delivered** |
> | RETURN | 包裹退回 | → **Suspended** |

### TC020: 物流状态-AC（承运商接收）→ 订单"On its way"

#### 📋 前置条件
- TC018 面单已创建（卖家已点击 `Create Label`），订单状态：`Awaiting Dispatch`
- 已登录买家和卖家账号（用于后续页面校验）

#### 🎬 执行步骤
1. 通过 `order_api` 获取追踪号，再调用 ShipWebhook 触发 AC 状态：
   ```python
   from test_cases.PayShip.utils.order_api import get_tracking_number
   from test_cases.PayShip.utils.ship_webhook import ShipWebhook

   # 从卖家订单详情页 URL 提取 ORDER_ID
   tracking_number = get_tracking_number(order_id="{ORDER_ID}", env="unicorn")

   webhook = ShipWebhook(env_name="unicorn")
   response = webhook.trigger(tracking_number=tracking_number, status_code="AC")
   assert response.status_code == 200
   ```
2. 前往卖家订单列表，点击对应订单卡片查看订单详情
3. 返回，切换到买家账号，前往买家订单列表，点击对应订单卡片查看详情

#### ✅ 预期结果

**Webhook 调用：**
- ✅ **实测**：HTTP 响应状态码：`200`
- ✅ **实测**：响应体无错误信息

**卖家订单列表页（AC 后）：**
- ✅ **实测**：订单卡片状态文字：`In progress | On its way`
- ✅ **实测**：`Create Label` 按钮 → 已变为 `Track order` 按钮

**卖家订单详情页（AC 后）：**
- ✅ **实测**：`Order details` 区域状态：`On its way`
- ✅ **实测**：显示预计送达时间：`Estimated delivery: 14 Apr - 16 Apr`（实测值，范围因调用时间浮动）
- ✅ **实测**：进度条激活节点：`Paid (13 Apr)` + `Dispatched (13 Apr)`（已激活）
- ✅ **实测**：`Arrived` 和 `Picked up` 节点**未**激活（灰色）
- ✅ **实测**：商品区域操作按钮：`View Label` → 变为 `Track order` 按钮
- ✅ **实测**：`Cancel order` 按钮**消失**（已发货后不可取消）
- ✅ **实测**：底部操作按钮：`Message buyer` + `Track order` + `Contact Customer Service`

**买家订单列表页（AC 后）：**
- ✅ **实测**：订单卡片状态文字：`In progress | On its way`
- ✅ **实测**：`Track order` 按钮显示

**买家订单详情页（AC 后）：**
- ✅ **实测**：订单状态：`On its way`
- ✅ **实测**：显示预计送达时间：`Estimated delivery: 14 Apr - 16 Apr`
- ✅ **实测**：进度条激活节点：`Paid` + `Dispatched`（两个节点已激活，含日期）
- ✅ **实测**：`Arrived` 和 `Picked up` 节点**未**激活（灰色）
- ✅ **实测**：`Cancel order` 按钮**消失**（已发货后不可取消）
- ✅ **实测**：`Track order` 按钮可见
- ✅ **实测**：底部操作按钮：`Message seller` + `Track order` + `Contact Customer Service`

#### 📊 用例属性
- **优先级**: P0 | **UI自动化**: ✅ 可自动化（结合 ShipWebhook 工具类）

---

### TC020b: 物流状态-IT（在途中）→ 订单追踪更新

#### 📋 前置条件
- TC020 AC Webhook 已触发，订单当前状态：`On its way`
- 已获取 Tracking Number（追踪号）

#### 🎬 执行步骤
1. 调用 ShipWebhook 触发 IT 状态：
```python
# tracking_number 由 TC020 步骤中的 get_tracking_number() 已获取
response = webhook.trigger(tracking_number=tracking_number, status_code="IT")
assert response.status_code == 200
```
2. 刷新买家订单列表页
3. 进入买家订单详情页
4. （可选）切换到卖家账号验证卖家侧订单状态

#### ✅ 预期结果

**买家/卖家订单列表页（IT 后）：**
- ✅ **实测**：订单卡片状态文字：`In progress | On its way`（与 AC 后**一致**，无变化）
- ✅ **实测**：`Track order` 按钮显示

**买家/卖家订单详情页（IT 后）：**
- ✅ **实测**：订单状态保持 `On its way`（IT 不触发页面状态变化）
- ✅ **实测**：进度条节点与 AC 后相同（Paid + Dispatched 激活，Arrived 未激活）
- ⚠️ **推断**：物流轨迹追踪页（Track order 链接）最新记录应更新为 `IT - Collected from ParcelShop`（未实际点击 Track order 链接验证）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/物流状态
- **UI自动化**: ✅ 可自动化

---

### TC020c: 物流状态-AT（派送中）→ 订单追踪更新

#### 📋 前置条件
- TC020b IT Webhook 已触发，订单当前状态：`On its way`
- 已获取 Tracking Number（追踪号）
- ⚠️ **业务规则**：自提点订单流程从 IT 直接跳到 SP，跳过 AT 状态；AT 适用于到家配送的"派件中"场景

#### 🎬 执行步骤
1. 调用 ShipWebhook 触发 AT 状态：
```python
# tracking_number 由 TC020 步骤中的 get_tracking_number() 已获取
response = webhook.trigger(tracking_number=tracking_number, status_code="AT")
assert response.status_code == 200
```
2. 刷新买家订单列表/详情页
3. 切换到卖家账号验证订单状态

#### ✅ 预期结果
- ⚠️ **推断（未实测，自提点订单本次流程跳过 AT）**：订单状态仍为 `On its way`（AT 仅更新追踪记录）
- ⚠️ **推断**：物流轨迹最新记录：`AT - Out For Delivery`

> **注意**：本次实测为自提点订单，实际物流流程从 IT 直接跳过 AT 调用了 SP（送达自提点）。AT 状态适用于到家配送的"派件中"场景。

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/物流状态（仅适用到家配送，自提点流程跳过此状态）
- **UI自动化**: ✅ 可自动化

---

### TC021: 物流状态-SP（送至自提点）→ 订单"Arrived at pick-up point"

#### 📋 前置条件
- 已触发 AC/IT 状态，订单当前状态：`On its way`
- 本次为自提点订单（delivery_method = STORE）

#### 🎬 执行步骤
1. 调用 ShipWebhook 触发 SP 状态：
```python
# tracking_number 由 TC020 步骤中的 get_tracking_number() 已获取
response = webhook.trigger(
    tracking_number=tracking_number,
    status_code="SP",
    delivery_method="STORE"
)
assert response.status_code == 200
```
2. 刷新买家订单列表页，查看订单状态变化
3. 点击订单卡片，进入买家订单详情页，校验进度条和操作按钮
4. 切换到卖家账号，校验卖家侧订单列表和详情页

#### ✅ 预期结果

**Webhook 调用：**
- ✅ **实测**：HTTP 响应状态码：`200`
- ✅ **实测**：event_code: `1440`，event_description: `Received at ParcelShop`

**买家订单列表页（SP 后）：**
- ✅ **实测**：订单卡片状态文字：`In progress | Arrived at pick-up point`
- ✅ **实测**：操作按钮：`Track order`

**买家订单详情页（SP 后）：**
- ✅ **实测**：`Order details` 区域状态：`Arrived at pick-up point`
- ✅ **实测**：进度条激活节点：`Paid` + `Dispatched` + `Arrived (13 Apr)`（三个激活）
- ✅ **实测**：`Picked up` 进度节点**未**激活（灰色）
- ✅ **实测**：自提点信息区域显示更新消息：`Your parcel arrived at your pick-up point on 13 Apr! It's ready for you to collect.`（或类似文字）
  - 自提点名称：`LONDIS`
  - 地址：`24-26 Railway Street, Altrincham, WA14 2RE`
  - 营业时间显示（可展开：Mon-Sun 07:00-23:00，Sun 09:00-23:00）
- ✅ **实测**：底部操作按钮：`Message seller` + `Track order` + `Contact Customer Service`（无 `I'm happy with my item`）

**卖家订单列表页（SP 后）：**
- ✅ **实测**：状态文字：`In progress | Arrived at pick-up point`
- ✅ **实测**：操作按钮：`Track order`

**卖家订单详情页（SP 后）：**
- ⚠️ **推断（切换账号成本，基于买家侧推断）**：状态变为 `Arrived at pick-up point`，进度条同步激活到 `Arrived`

#### 📊 用例属性
- **优先级**: P0 | **UI自动化**: ✅ 可自动化

---

### TC022: 物流状态-DE（买家取件完成）→ 订单"Picked up"

#### 📋 前置条件
- 已触发 SP 状态（TC021），订单当前状态：`Arrived at pick-up point`
- 本次为自提商店取件（delivery_method = STORE）

#### 🎬 执行步骤
1. 调用 ShipWebhook 触发 DE 状态（Delivered / Collected with PIN）：
```python
# tracking_number 由 TC020 步骤中的 get_tracking_number() 已获取
response = webhook.trigger(
    tracking_number=tracking_number,
    status_code="DE",
    delivery_method="STORE"
)
assert response.status_code == 200
```
2. 刷新买家订单列表页，查看订单状态变化为 `Picked up`
3. 点击订单卡片，进入买家订单详情页，校验进度条和新增的 `I'm happy with my item` 按钮
4. 切换到卖家账号，校验卖家侧订单状态

#### ✅ 预期结果

**Webhook 调用：**
- ✅ **实测**：HTTP 响应状态码：`200`
- ✅ **实测**：event_code: `1448`，event_description: `Collected with PIN`

**买家订单列表页（DE 后）：**
- ✅ **实测**：订单卡片状态文字：`In progress | Picked up`
- ✅ **实测**：操作按钮：`Track order`

**买家订单详情页（DE 后）：**
- ✅ **实测**：`Order details` 区域状态：`Picked up`
- ✅ **实测**：显示取件确认截止时间：`Confirm by [日期]`（实测：`Confirm by 15 Apr`，DE 触发后 48 小时）
- ✅ **实测**：进度条激活节点：`Paid` + `Dispatched` + `Arrived` + `Picked up (13 Apr)`（四个激活）
- ✅ **实测**：自提点信息区域消息：`Your parcel has been picked up on 13 Apr!`
- ✅ **实测**：商品区域：出现 **`I'm happy with my item`** 按钮（主操作确认收货）
- ✅ **实测**：底部操作按钮：`Message seller` + `Track order` + `Report an issue`（`Contact Customer Service` 消失，`Report an issue` 出现）

**卖家订单详情页（DE 后）：**
- ⚠️ **推断**：状态显示 `Picked up`，等待买家确认

> **注意**：自提点订单的"Delivered"状态在 UI 中显示为 `Picked up`，而非 `Delivered`。

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/物流状态（E2E 核心路径）
- **UI自动化**: ✅ 可自动化

---

## 模块6：买家签收与确认收货

### TC023: 买家手动确认收货-签收48小时内

#### 📋 前置条件
- 已登录买家账号
- 订单状态：`Picked up`（DE Webhook 已触发），签收时间不超过 48 小时

#### 🎬 执行步骤
1. 进入买家订单详情页（状态：`Picked up`，显示 `Confirm by [日期]`）
2. 点击商品区域的 **`I'm happy with my item`** 按钮
3. 弹出 "Check your item" 确认对话框，点击对话框内的 **`I'm happy with my item`** 按钮确认

#### ✅ 预期结果

**"Check your item" 确认弹窗（步骤 2 后）：**
- ✅ **实测**：弹窗标题：`Check your item`
- ✅ **实测**：说明文字：`If the item matches its description, confirm you're happy with it. Report an issue if it never arrived or it's not what you expected.`
- ✅ **实测**：确认按钮：`I'm happy with my item`（绿色/主操作）
- ✅ **实测**：问题按钮：`Report an issue`（次要操作）
- ✅ **实测**：关闭按钮：`Close`（× 图标）

**确认收货后买家订单详情页（步骤 3 后）：**
- ✅ **实测**：`Order details` 区域状态变更为：**`Order Completed`**
- ✅ **实测**：进度条全部激活：`Paid (13 Apr)` + `Dispatched (13 Apr)` + `Arrived (13 Apr)` + `Picked up (13 Apr)` + **`Completed (13 Apr)`**（五个全部激活）
- ✅ **实测**：商品区域：`I'm happy with my item` → 变为 **`Leave a review`** 按钮
- ✅ **实测**：底部操作按钮：`Message seller` + `Track order` + `Contact Customer Service`
- ✅ **实测**：`Report an issue` 按钮**消失**
- ✅ **实测**：`Confirm by [日期]` 文字**消失**

**确认收货后买家订单列表页（刷新后）：**
- ✅ **实测**：订单卡片状态：`Completed`（或筛选后可见）
- ✅ **实测**：商品区域操作按钮：`Leave a review`（确认收货后出现）
- ✅ **实测**：订单号格式：`Order number: {8位数字}`
- ✅ **实测**：三点菜单（...）内容：
  - `View order details`
  - `Message seller`
  - `Track order`
  - `Contact Customer Service`
  - ⚠️ `Report an issue` **已消失**（确认收货后不可再报问题）

**确认收货后卖家订单列表页（自动同步，实测步骤）：**
- ✅ **实测前置**：切换到卖家账号登录
- ✅ **实测步骤**：导航至 Menu → My Orders → Sold Tab（URL: `/manage/orders?type=sold`）
- ✅ **实测结果**：
  - 订单卡片状态：`Completed`
  - 商品区域操作按钮：`Leave a review`（买家确认收货后卖家侧也出现评价入口）
  - 订单号格式：`Order number: {8位数字}`
  - 三点菜单（...）内容：
    - `View order details`
    - `Message buyer`
    - `Track order`
    - `Contact Customer Service`
    - ⚠️ `Cancel order` **已消失**（订单已完成不可取消）

**确认收货后卖家订单详情页（实测步骤）：**
- ✅ **实测步骤**：导航至 `/order/{ORDER_ID}?type=sold`
- ✅ **实测结果（全量元素校验）**：
  - **订单状态头部**：`Order Completed`
  - **进度条**：5 个节点全部激活
    - `Paid` - 13 Apr
    - `Dispatched` - 13 Apr
    - `Arrived` - 13 Apr
    - `Picked up` - 13 Apr
    - `Completed` - 13 Apr
  - **商品区域**：
    - 商品数量徽章：`1`
    - 商品标题（可点击链接 → 快照）
    - 商品价格（可点击链接 → 快照）
    - `View Snapshot` 按钮
    - **`Leave a review` 按钮**（新增，用于卖家评价买家）
  - **订单摘要**（Order summary）：
    - Item subtotal: £10.00（或对应价格）
    - Delivery: £2.59
    - Buyer Protection: £1.20
    - Total: £13.79
  - **配送地址**：
    - 收件人姓名：`gt2 auto`
    - 地址文本：`Address available on delivery label`（仍隐藏）
  - **支付状态横幅（Payment status）**：
    - 图标 + 消息文本：`The order is complete and £{Item Price} will be transferred to your bank account.`
    - ⚠️ **文案变更**：从 "The buyer has already paid..." 变为 "The order is complete and £... will be transferred..."（确认收货后支付状态消息更新）
  - **底部操作按钮区域**：
    - `Message buyer` 按钮
    - `Track order` 按钮
    - `Contact Customer Service` 按钮
    - ⚠️ `Cancel order` 按钮**已消失**（订单完成后不可取消）

**资金流转（业务规则）：**
- 买卖双方可以互相评价 ✅ **实测确认**（`Leave a review` 按钮存在，点击流程见 TC025）
- 确认收货 24 小时后系统向卖家 payout ⚠️ 待实测确认
- 资金流转：
  - Item Price：买家钱包 → 卖家钱包
  - Ship Price：买家钱包 → Gumtree 运费钱包
  - Buyer Protection Fee：买家钱包 → Gumtree 保护费钱包

#### 🤖 自动化实现细节

**步骤1：触发确认收货（实现差异说明）**
- **脚本实现**：在买家订单**列表**点击 `I'm happy with my item`（line 1395）
  ```python
  page.get_by_role("button", name="I'm happy with my item").first.click()
  ```
- **文档描述**：在买家订单**详情页**点击
- **UI 支持两种方式**：列表和详情页均可触发确认弹窗，脚本选择列表触发（效率更高）

**步骤3：弹窗内确认（3层兜底策略）**
- **难点**：确认按钮需在弹窗容器内精准定位，避免误点页面上的其他同名按钮
- **策略1：尝试3种弹窗容器选择器**（按优先级）
  1. `[data-testid='dialog-content']`（标准 testid）
  2. `.dialog-content`（类名）
  3. `[role='dialog']`（ARIA 角色）
  - 在容器内查找：`dlg.get_by_role("button", name="I'm happy with my item").click()`
- **策略2：兜底方案**（若策略1全失败）
  - 直接点击页面上**最后一个**可见的 `I'm happy with my item` 按钮（`.last`）
  - 假设弹窗按钮在 DOM 中后出现，故用 `.last` 优先匹配弹窗内按钮
  ```python
  page.get_by_role("button", name="I'm happy with my item").last.click()
  ```
- **确认后等待**：`page.wait_for_timeout(4000)`（等待确认 API 完成，异步更新订单状态）
- **容错性**：每个策略使用 `try/except` + `timeout=2000` 快速检测

**验证策略优化（步骤3后）**
- **优先验证详情页**：先导航到 `/order/{ORDER_ID}?type=bought`，验证 `Order Completed` 状态
  - **原因**：详情页状态更可靠，不依赖列表 DOM 刷新时机
- **5节点循环验证**：
  ```python
  for node in ["Paid", "Dispatched", "Arrived", "Picked up", "Completed"]:
      expect(page.get_by_text(node).first).to_be_visible()
  ```
- **使用 `Leave a review` 判断完成状态**：
  - **问题**：直接用 `get_by_text("Completed")` 会匹配到 Filter 下拉框的 "Completed" 选项
  - **解决**：用 `Leave a review` 按钮存在作为订单完成的强信号
  - **验证逻辑**：`expect(page.get_by_role("button", name="Leave a review").first).to_be_visible()`

**三点菜单验证（不稳定实现）**
- **脚本实现**：使用 `.nth(3)` 硬编码点击第4个按钮（假设为三点菜单）
  ```python
  page.get_by_role("button").nth(3).click()
  ```
- **验证项**：`View order details` / `Message seller` / `Track order`
- **容错性**：整个菜单验证用 `try/except` 包裹，失败不影响测试通过
- ⚠️ **脚本不完整**：未明确定位菜单按钮（如 `data-testid="order-menu"`），硬编码索引不可靠

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向（E2E 核心路径）
- **UI自动化**: ✅ 可自动化

---

### TC025: 买家评价卖家-3步评价流程（基于订单详情页触发）

#### 📋 前置条件
- TC023 确认收货已完成，订单状态：`Order Completed`
- 买家尚未对该订单评价卖家
- 已登录买家账号（gtauto25858@outlook.com）

#### 🎬 执行步骤
1. 进入买家订单详情页（状态：`Order Completed`）
2. 点击商品区的 **`Leave a review`** 按钮
3. **Step 1 - 评分**：点击第5颗星（最高评价）
4. 点击 `Continue` 进入 Step 2
5. **Step 2 - 好评标签**：选择 `Item as described`（单选即可，也可多选）
6. 点击 `Continue` 进入 Step 3
7. **Step 3 - 差评标签**：选择 `None of these`
8. 点击 `Continue` 提交评价

#### ✅ 预期结果

**评价弹窗 Step 1（评分选择）：**
- ✅ **实测**：弹窗标题：`How was your experience in this exchange with {卖家昵称}?`
  - 🤖 **脚本实现**：使用 `data-testid="dialog-content"` 限定作用域，避免误选其他 dialog
- ✅ **实测**：显示 5 颗星评分按钮
  - 🤖 **脚本实现**：`get_by_test_id("star-button").nth(4)` 选中第5颗星（索引从0开始）
- ✅ **实测**：选中第5星后显示描述文字：`It was great`
- ✅ **实测**：`Continue` 按钮状态：初始 `disabled` → 选星后 `enabled`
  - 🤖 **脚本实现**：使用 `to_be_enabled()` 断言

**评价弹窗 Step 2（好评标签）：**
- ✅ **实测**：步骤标题：`What went well?`
- ✅ **实测**：显示多选标签：`Friendly` / `Polite` / `Helpful` / `Speedy responder` / `Item as described` / `Quick transaction` / `Showed up on time` / `Fair negotiation` / `None of these`
  - 🤖 **脚本实现**：只选择 `Item as described`（`get_by_role("button", name="Item as described").click()`）
  - ⚠️ **实现差异**：文档原描述选2个标签（Friendly + Item as described），实际脚本只选1个
- ✅ **实测**：`Continue` 按钮初始即为 `enabled`（可跳过不选）

**评价弹窗 Step 3（差评标签）：**
- ✅ **实测**：步骤标题：`What didn't go well?`
- ✅ **实测**：显示多选标签：`Rude` / `Unhelpful` / `Unresponsive` / `Item not as described` / `Cancelled offer` / `Didn't show up` / `Too much haggling` / `None of these`
  - 🤖 **脚本实现**：`get_by_role("button", name="None of these").click()`
- ✅ **实测**：`Continue` 按钮文案变为 `Submit review`（最后一步）

**提交结果（unicorn 环境已知 Bug）：**
- 🐛 **实测**：提交后出现错误弹窗：`There's been an error processing your request` / `Please try again later`
  - ⚠️ **环境问题**：unicorn 环境评价接口异常，非功能缺陷
  - 🤖 **脚本处理**：检测错误文案，点击弹窗内的 `Close` 按钮关闭（`page.get_by_role("button", name="Close").last.click()`）
- 🐛 **实测**：评价提交失败后，`Leave a review` 按钮**仍然显示**（未变更为已评价状态）
- ⚠️ **推断**（正常环境）：提交成功后 `Leave a review` 按钮应消失或变为 `Reviewed`

**订单列表中的评价入口（补充验证）：**
- ✅ **实测**：买家订单列表页（Completed 状态）订单卡片上的三点菜单（`...`）中**无 `Leave a review` 入口**
  - ⚠️ **UI差异**：订单列表卡片的三点菜单不含评价入口，仅在订单详情页商品区显示 `Leave a review` 按钮
  - 🤖 **脚本实现**：点击 `get_by_role("button").nth(3)` 后（硬编码索引），验证菜单内容
  - ⚠️ **脚本不完整**：使用 `try/except` 跳过失败，未严格验证每个菜单项

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向（E2E 评价流程）
- **UI自动化**: ⚠️ 部分可自动化（UI交互可测，API提交受环境限制）

---

## 📊 用例统计

| 模块 | 用例数 | 实测 ✅ | 待实测 ⚠️ | P0 | P1 | P2 |
|------|--------|--------|----------|----|----|-----|
| 模块1：卖家发布广告 | 4 | 1 | 3 | 2 | 2 | 0 |
| 模块2：买家浏览与下单 | 6 | 2 | 4 | 4 | 2 | 0 |
| 模块3：买家支付 | 4 | 1 | 3 | 3 | 1 | 0 |
| **模块3B：买卖双方订单页面元素校验** | **6** | **6** | **0** | **5** | **1** | **0** |
| 模块4：卖家发货物流 | 2 | 2 ✅ | 0 | 2 | 0 | 0 |
| 模块5：物流正向流转 | 6 | 4 ✅（AC/IT/SP/DE）| 2（AT/全流程）| 3 | 3 | 0 |
| 模块6：签收与确认收货 | 3 | 1 ✅（TC023 手动确认收货）| 2（自动确认/评价）| 2 | 1 | 0 |
| **合计** | **41** | **22** | **19** | **23** | **18** | **0** |

> **说明**：v4.0 新增实测覆盖：TC018（面单生成成功页）、TC020（AC/IT/SP/DE Webhook 全流程）、TC023（买家手动确认收货）；本次实测订单 Tracking Number: `H06Z5A0000017864`，Order ID: `1380031800000000000002997260`。
> **v6.0（2026-04-16）更新**：补充实测 `Check your item` 弹窗准确说明文字；新增买家/卖家 Completed 状态 "..." 菜单 CTA 全量实测（View order details / Message seller|buyer / Track order / Contact Customer Service）；确认 Report an issue 在确认收货后消失；本次实测订单 Order ID: `1380196800000000000002997260`，Tracking Number: `H06Z5A0000018068`。

---

## 🔍 实测探索覆盖情况

### ✅ 已实测确认的场景

**第一次探测（卖家发布广告 → 结账页）：**
1. **卖家登录流程**：点击 Login → Continue with email → 输入邮箱密码 → Continue
2. **广告发布 - 类目选择**：For Sale > Clothes, Footwear & Accessories > Other
3. **广告发布 - Parcel size 选择**：需要先点击再按 **Space 键** 展开（自定义下拉组件）
4. **广告发布 - 图片上传**：拖放或点击上传区域，支持 JPG 格式
5. **广告发布 - 标题格式坑**：日期时间之间必须用 T 分隔（如 `20260413T060141`），否则被误判为电话号码
6. **买家登录流程**：与卖家相同
7. **广告详情页**：显示 Buy now、配送费、Buyer Protection、卖家信息
8. **结账页布局**：默认选中 Deliver to pick-up point
9. **费用计算公式**：商品价格 × 5% + £0.7 = Buyer Protection（£10→£1.20，£20→£1.70）✅ 公式正确
10. **自提点搜索完整流程**：输入地址 → 选建议 → 列表展示 → 展开详情 → 确认选择
11. **退出登录流程**：Menu → Logout → 跳转至 my.unicorn.gumtree.io/logout

**第二次探测（支付成功 → 订单页面全量元素 → 创建面单页）：**
12. **支付成功页**（`/payment-result`）：标题 "Thanks for your order, {用户名}!"、订单号、商品标题、总价
13. **买家订单列表**（`/manage/orders`）：Bought/Sold 二级 Tab；订单卡片含状态 "In progress | Awaiting dispatch"、商品标题/价格、"View order details" 按钮、订单号
14. **买家订单详情**（`/order/{id}?type=bought`）：4 节点进度条、费用明细（£10+£2.59+£1.20=£13.79）、自提点地址 LONDIS WA14 2RE、支付方式 VISA 1119
15. **买家订单快照**（`/order-snapshot/{id}?type=bought`）：广告图片+描述+Ad ID+价格+卖家用户名
16. **卖家订单列表 Sold Tab**（`/manage/orders?type=sold`）：订单卡片含状态标签、"Create Label" 按钮（非 "Ship item"）、发货倒计时
17. **卖家订单详情**（`/order/{id}?type=sold`）：收件地址隐藏（"Address available on delivery label"）、Payment status 说明文本、操作按钮（Message buyer / Contact CS / Cancel）
18. **卖家订单快照**（`/order-snapshot/{id}?type=sold`）：与买家侧结构相同，显示卖家自己的信息
19. **创建面单信息确认页**（`/shipping-label/create`）：Send with（Evri/paid by buyer）、Return address（自动读取卖家地址）、Recipient address（隐藏）、Continue 按钮+条款文本
20. **面单生成失败弹窗**：标题 "Label generation failed"，原因 "Calling logistics service failed"（测试环境物流服务异常，非功能缺陷）

**第三次探测（面单生成成功 → Webhook AC/IT/SP/DE → 买家确认收货 → 订单完成）：**
21. **面单生成成功页**（`/shipping-label/{orderId}`）：标题 "Your label is ready!"、QR 码图片、Tracking Number（短码 `74CP2D`）、Save QR code 按钮、Download label 按钮、Find a drop-off location 链接、到期日期提示
22. **Proxy API 获取完整追踪号**：`GET https://proxy-seller.thirdparty.unicorn.gumtree.io/order/ui/orderDetail?orderId={orderId}`，取 `data.shippingDetail.trackingNumber`，实测值：`H06Z5A0000017864`
23. **AC Webhook 后卖家/买家订单状态**：`In progress | On its way`；详情页进度条激活 Paid+Dispatched；`Create Label`→`View Label`→`Track order`；`Cancel order` 消失
24. **IT Webhook 后**：状态无变化（同 AC），`On its way` 保持不变
25. **SP Webhook（STORE）后**：状态变为 `In progress | Arrived at pick-up point`；进度条激活到 `Arrived`；自提点消息 "Your parcel arrived at your pick-up point on 13 Apr!"
26. **DE Webhook（STORE）后**：状态变为 `In progress | Picked up`；进度条激活到 `Picked up`；出现 `I'm happy with my item` 按钮；显示 `Confirm by 15 Apr`；底部出现 `Report an issue` 按钮
27. **"Check your item" 确认弹窗**：标题 `Check your item`，`I'm happy with my item`+`Report an issue`+`Close` 三个按钮
28. **买家确认收货后**：状态变为 `Order Completed`；进度条五个节点全部激活（含 `Completed (13 Apr)`）；商品区域出现 `Leave a review` 按钮；底部 `Report an issue` 消失
29. **Leave a review 评价弹窗（三步流程）**：
    - 第一步：`How was your experience in this exchange with {对方昵称}?` → 5颗星评分按钮（星级描述：1星→5星，选中5星后显示 "It was great"）→ `Continue`（disabled → enabled）
    - 第二步：`What went well?` → 多选标签：Friendly / Polite / Helpful / Speedy responder / Item as described / Quick transaction / Showed up on time / Fair negotiation / None of these → `Continue`（已激活，可跳过不选）
    - 第三步：`What didn't go well?` → 多选标签：Rude / Unhelpful / Unresponsive / Item not as described / Cancelled offer / Didn't show up / Too much haggling / None of these → `Continue`
30. **Leave a review 触发入口**：可从订单列表卡片的 `Leave a review` 按钮触发；也可从订单详情页商品区的 `Leave a review` 按钮触发（两处均实测可触发评价弹窗）
31. **🐛 Bug 发现（评价提交失败）**：买家和卖家提交评价后均收到错误弹窗 `"There's been an error processing your request"` / `"Please try again later"`；提交失败后 `Leave a review` 按钮**未变更为已评价状态**，页面上仍显示 `Leave a review`（unicorn 环境评价接口存在问题）
32. **卖家订单详情（完成后）支付状态消息**：`"The order is complete and £{金额} will be transferred to your bank account."` —— 订单完成后卖家侧支付状态消息由等待确认变更为确认转账通知

### ⚠️ 查缺补漏：原文档需要修正的内容

| 序号 | 原文档描述 | 实测修正 |
|------|------------|---------|
| 1 | 基础URL：https://www.gumtree.com | 测试环境：**https://www.unicorn.gumtree.io/** |
| 2 | 结账页配送默认为配送到家 | 默认选中 **"Deliver to pick-up point"** |
| 3 | 自提点搜索：Nearby / Recently used Tab | 搜索弹窗有 Nearby 和 Recently used Tab，但搜索框需输入地址才能显示指定位置附近的自提点 |
| 4 | 中包裹配送到自提点 £2.99 | 实测为**小包裹** £2.59（广告选择的是小包裹） |
| 5 | 广告详情页 Buyer Protection 展示位置 | 在**广告详情页**（非仅在结账页）就已显示 "Buyer Protection £1.70" |
| 6 | 结账页 URL 未指定 | 确认为 **/create-order?advertId={advertId}** |
| 7 | 买家账号无支付方式描述 | 测试账号已预绑定 **VISA 尾号 1119**，无需首次添加 |
| 8 | 广告标题格式含 `-`（如 `20260413-153022`） | **必须用 `T` 分隔**（如 `20260413T060141`），否则报错 "Please remove phone number from title" |
| 9 | 订单列表 Tab 为 Active/Completed/Cancelled | 实测为 **Bought / Sold** 二级分类，筛选通过 Filter 下拉完成 |
| 10 | 订单状态为 `Awaiting dispatch` | 实测状态文本为 **`In progress \| Awaiting dispatch`** |
| 11 | 卖家订单卡片按钮为 `Ship item` | 实测按钮文本为 **`Create Label`** |
| 12 | 卖家可查看买家收货地址 | 面单创建前**地址隐藏**，卡片显示 "Address available on delivery label" |
| 13 | 自提点订单 Delivered 状态文字 | UI 中不显示 `Delivered`，而是显示 **`Picked up`** |
| 14 | 确认收货按钮文字为 "Confirm received" | 实测按钮文字为 **`I'm happy with my item`**，位于商品区域而非底部操作区 |
| 15 | DE 后 48 小时内可确认收货 | 实测 UI 显示 **`Confirm by [日期]`**（DE 触发后 +48h），卖家端同期等待 |
| 16 | 面单 Tracking Number 直接页面显示 | 页面仅显示短码（如 `74CP2D`），完整追踪号（如 `H06Z5A0000017864`）需通过 proxy API 获取 |
| 17 | 物流状态 IT/AT 后订单状态会变化 | 实测 **IT 和 AT 不改变订单主状态**，仅更新内部物流追踪记录，UI 订单列表/详情状态保持 `On its way` |

---

## 🛠️ 测试工具配置

### Playwright 脚本路径参考
- 卖家广告发布脚本：`test_scripts/seller_post_ad.py`
- 买家购买脚本：`test_scripts/buyer_purchase_pickup.py`

### 物流状态 Webhook 工具类
```
工具类路径: test_cases/PayShip/utils/ship_webhook.py   （v5.0 更新：脚本已移至此路径）
类名: ShipWebhook

初始化参数:
  env_name (str): 环境名称，含 zoidberg/bixi/gaga/unicorn/stage 之一即可

trigger() 参数:
  tracking_number (str): TC018 面单创建后获取的追踪号（必填）
  status_code (str): 物流状态码，取值 AC/IT/AT/SP/DE/RETURN（必填）
  delivery_method (str): 配送方式，SP/DE 时必填，取值 HOME/STORE/LOCKER
  return_reason (str): 退回原因，RETURN 时必填，取值 SPRETURN/ITRETURN

状态码与事件码对照:
  AC   → event_code: 1409 | Customer Sent via ParcelShop
  IT   → event_code: 1410 | Collected from ParcelShop
  AT   → event_code: 1032 | Out For Delivery
  SP+STORE  → event_code: 1440 | Received at ParcelShop
  SP+LOCKER → event_code: 4210 | Received at Locker
  DE+HOME   → event_code: 4238 | This parcel has been delivered
  DE+STORE  → event_code: 1448 | Collected with PIN
  DE+LOCKER → event_code: 1448 | Collected with PIN
  RETURN+SPRETURN → event_code: 4212 | Driver collected expired parcel
  RETURN+ITRETURN → event_code: 1021 | This parcel is currently being processed to be returned to the retailer

自提订单完整流程便捷方法:
  webhook.trigger_full_flow(tracking_number="{追踪号}", delivery_method="STORE")
  # 自动按顺序触发: AC → IT → AT → SP → DE
```

### MangoPay 测试配置
```
卖家注册电话: +33 611111111
验证码: 702100
3DS 测试卡: 4970105181818183（Expiry: 12/28, CVV: 123）
普通测试卡: 4970107111111119（Expiry: 12/28, CVV: 123）
```

---

**文档生成时间**: 2026-04-13  
**文档版本**: v5.2（补充脚本实测细节，规范化为 web-qa-brain skill 标准格式）  
**本次探测订单快照（仅供历史参考，每次测试值不同）**:
> ⚠️ 以下为某次实际探测记录，不可硬编码到测试脚本中。测试脚本应通过 `get_tracking_number(order_id)` 动态获取。

- 广告标题: `Delivery Store {YYYYMMDD}T{HHmmss} TW9`（每次发布动态生成）
- Order ID: 从订单详情页 URL `/order/{ORDER_ID}?type=sold` 提取
- Order No.: 从页面 `Order No. : {8位数字}` 提取
- Tracking Number: 通过 `get_tracking_number(order_id, env="unicorn")` 获取
- 自提点: LONDIS, 24-26 Railway Street, Altrincham, WA14 2RE（固定测试数据）

**Playwright MCP 探测覆盖**:
- ✅ 卖家发布广告（TC001）
- ✅ 买家下单至自提点选择并支付（TC007/TC011）
- ✅ 支付成功页全量元素（TC011）
- ✅ 买家订单列表全量元素（TC011b）
- ✅ 买家订单详情全量元素（TC011c）
- ✅ 买家订单快照全量元素（TC011c-snap）
- ✅ 卖家订单列表（Sold Tab）全量元素（TC011d）
- ✅ 卖家订单详情全量元素（TC011e）
- ✅ 卖家订单快照全量元素（TC011e-snap）
- ✅ 创建面单信息确认页全量元素（TC018）
- ✅ 面单生成成功页全量元素（TC018-generated）
- ✅ 调用 AC Webhook → 卖家/买家订单列表+详情状态验证（TC020-AC）
- ✅ 调用 IT Webhook → 买家/卖家订单列表+详情状态验证（TC020-IT，无 UI 变化）
- ✅ 调用 SP Webhook（STORE）→ 买家/卖家订单列表+详情状态变化（TC020-SP）
- ✅ 调用 DE Webhook（STORE）→ 买家/卖家订单列表+详情状态变化（TC020-DE）
- ✅ 买家点击"I'm happy with my item"→ 弹窗确认 → 订单完成（TC021）
- ✅ 订单完成后买家订单列表+详情状态（TC021-final-buyer）
- ✅ 订单完成后卖家订单列表+详情状态（TC021-final-seller）【v5.0 新增实测】
- ✅ 买家从订单详情点击"Leave a review" → 三步评价弹窗完整流程（TC022-buyer）【v5.0 新增实测】
- ✅ 卖家从订单列表点击"Leave a review" → 三步评价弹窗完整流程（TC022-seller）【v5.0 新增实测】
- 🐛 评价提交后 API 返回错误，"Leave a review"按钮状态未更新（TC022-bug）【v5.0 新增实测发现的缺陷】
- ✅ 实测 "Check your item" 弹窗准确说明文字：`If the item matches its description, confirm you're happy with it. Report an issue if it never arrived or it's not what you expected.`【v6.0 更新】
- ✅ 买家 Completed 状态 "..." 菜单 CTA 全量（View order details / Message seller / Track order / Contact Customer Service；Report an issue 确认消失）【v6.0 新增实测】
- ✅ 卖家 Completed 状态 "..." 菜单 CTA 全量（View order details / Message buyer / Track order / Contact Customer Service）【v6.0 新增实测】

---

## Phase 11 - Leave a Review 评价流程测试用例（v5.0 实测新增）

### TC022 - 买家 Leave a Review（从订单详情页触发）

| 字段 | 内容 |
|------|------|
| **TC ID** | TC022 |
| **功能模块** | 评价功能 - 买家评价卖家 |
| **前置条件** | 买家已完成确认收货（订单状态为 Completed），买家账号已登录 |
| **测试路径** | 买家订单详情页 → 商品区 "Leave a review" 按钮 |
| **自动化可行性** | 🔴 高风险（评价接口在 unicorn 环境报错，需等修复后再自动化） |

**步骤与实测结果**：

| # | 操作步骤 | 实测结果 | 预期结果 |
|---|----------|----------|----------|
| 1 | 买家进入已完成订单详情页（Order Completed 状态） | 商品区显示 `Leave a review` 按钮 ✅ | 存在 `Leave a review` 按钮 |
| 2 | 点击 `Leave a review` | 弹出评价弹窗 Step 1：`"How was your experience in this exchange with {卖家昵称}?"` ✅ | 弹出 5 星评价弹窗 |
| 3 | **Step 1**：点击5颗星（最高评价） | 5星按钮选中（[active]），显示描述文字 `"It was great"`；`Continue` 按钮激活（disabled→enabled）✅ | 选中星级，Continue 可点击 |
| 4 | 点击 `Continue` | 进入 Step 2：`"What went well?"` ✅ | 进入第二步 |
| 5 | **Step 2**：点击好评标签（Friendly, Item as described） | 对应标签按钮选中；`Continue` 可点击 ✅ | 标签多选，Continue 可点击 |
| 6 | 点击 `Continue` | 进入 Step 3：`"What didn't go well?"` ✅ | 进入第三步 |
| 7 | **Step 3**：点击 `None of these` | 按钮选中 ✅ | 标签可选 |
| 8 | 点击 `Continue` 提交 | 🐛 弹出错误提示：`"There's been an error processing your request"` / `"Please try again later"` | 预期：评价成功提交，弹窗关闭，`Leave a review` 按钮变为 `Review submitted` 或消失 |
| 9 | 关闭错误弹窗 | 返回订单详情页，`Leave a review` 按钮**仍然存在**（状态未更新）🐛 | 预期：按钮状态更新为已评价 |
| 10 | 点击 `My Orders` 返回订单列表 | 买家订单列表中本订单状态仍为 `Completed`，按钮仍为 `Leave a review` 🐛 | 预期：按钮更新 |

**🤖 自动化实现细节（脚本中使用的精确定位方式）**：
- **弹窗作用域限定**：所有弹窗内操作使用 `page.get_by_test_id("dialog-content")` 作为父容器，避免定位到页面其他区域同名元素
- **星级按钮精准定位**：`page.get_by_test_id("dialog-content").get_by_test_id("star-button").nth(4)` 定位第5颗星（索引从0开始）
- **星级描述文字**：`page.get_by_test_id("dialog-content").get_by_text("It was great")` 验证5星描述文字（失败不中断）
- **步骤标题验证**：通过 `get_by_role("heading", level=2)` 匹配各步骤标题（"How was your experience...", "What went well?", "What didn't go well?"）
- **标签按钮选择**：通过 `get_by_role("button", name="Item as described")` 或 `name="Friendly"` 精准选择标签
- **Continue 按钮**：`get_by_role("button", name="Continue")` 通用定位，各步骤复用
- **错误处理**：捕获 `TimeoutError`（API 报错导致弹窗不关闭），自动调用 `page.keyboard.press("Escape")` 关闭弹窗

**🐛 缺陷记录**：
- **缺陷描述**：unicorn 测试环境下评价提交 API 返回 500 错误，提示 "There's been an error processing your request"
- **影响范围**：买家和卖家均无法成功提交评价
- **可观察结果**：`Leave a review` 按钮提交失败后状态未更改，页面仍显示 `Leave a review`（应为已评价状态）

---

### TC023 - 卖家 Leave a Review（从订单列表触发）

| 字段 | 内容 |
|------|------|
| **TC ID** | TC023 |
| **功能模块** | 评价功能 - 卖家评价买家 |
| **前置条件** | 买家已完成确认收货（订单状态为 Completed），卖家账号已登录 |
| **测试路径** | 卖家订单列表（Sold Tab）→ Completed 订单卡片 "Leave a review" 按钮 |
| **自动化可行性** | 🔴 高风险（评价接口在 unicorn 环境报错，需等修复后再自动化） |

**步骤与实测结果**：

| # | 操作步骤 | 实测结果 | 预期结果 |
|---|----------|----------|----------|
| 1 | 卖家进入订单列表（Sold Tab），找到 Completed 订单 | 订单卡片状态：`Completed`，按钮：`Leave a review` ✅ | 存在 `Leave a review` 按钮 |
| 2 | 点击订单卡片上的 `Leave a review` 按钮（**注意：弹窗从列表触发，不需要进入详情**）| 弹出评价弹窗 Step 1：`"How was your experience in this exchange with {买家昵称}?"` ✅ | 直接从列表触发弹窗 |
| 3 | **Step 1**：点击5颗星 | 5星选中；`Continue` 激活 ✅ | 同 TC022-Step3 |
| 4 | 点击 `Continue` | 进入 Step 2：`"What went well?"` ✅ | 同 TC022 |
| 5 | **Step 2**：点击好评标签（Friendly）后点 `Continue` | 进入 Step 3 ✅ | 同 TC022 |
| 6 | **Step 3**：点击 `None of these` 后点 `Continue` | 🐛 弹出错误提示：`"There's been an error processing your request"` / `"Please try again later"` | 预期：评价成功提交 |
| 7 | 关闭错误弹窗后检查列表 | 卖家订单列表本订单仍为 `Completed` + `Leave a review`，状态未更新 🐛 | 预期：按钮更新为已评价 |
| 8 | 点击订单进入卖家订单详情 | 详情页可见：`Order Completed`，5节点进度条全亮，`Leave a review` 仍存在，支付状态消息：`"The order is complete and £10.00 will be transferred to your bank account."` ✅ | 详情页状态正确 |

**🤖 自动化实现细节（脚本中使用的定位方式）**：
- **触发入口差异**：脚本实际从**订单详情页**触发 Leave a review，而非订单列表
  - 手动测试：可从订单列表卡片直接触发
  - 自动化脚本：进入订单详情后点击 `Leave a review` 按钮（`page.get_by_role("button", name="Leave a review")`）
- **弹窗定位**：与 TC022 买家评价使用相同的 `data-testid="dialog-content"` 作用域限定
- **标签选择差异**：卖家 Step 2 选择 `Friendly` 标签（`get_by_role("button", name="Friendly")`）
- **其他步骤**：星级、Continue 按钮、错误处理逻辑与 TC022 完全一致
- **最终验证**：检查卖家订单列表 Leave a review 按钮仍存在（因 API 错误导致状态未更新）

**卖家订单详情（Completed 后）全量元素**：

| 区域 | 元素 | 实测值 |
|------|------|--------|
| 页面标题 | 标题文本 | `Order details` |
| 订单号 | Order No. | `Order No. : {ORDER_NO}` |
| 状态标题 | 总状态 | `Order Completed` ✅ |
| 进度条 | 节点1 | `Paid` - 13 Apr ✅ |
| 进度条 | 节点2 | `Dispatched` - 13 Apr ✅ |
| 进度条 | 节点3 | `Arrived` - 13 Apr ✅ |
| 进度条 | 节点4 | `Picked up` - 13 Apr ✅ |
| 进度条 | 节点5 | `Completed` - 13 Apr ✅（全部激活） |
| 商品区 | 商品数量 | 1 |
| 商品区 | 商品名称链接（→快照） | Delivery Store 20260413T200931 TW9 ✅ |
| 商品区 | 价格链接（→快照） | £10.00 ✅ |
| 商品区 | 操作按钮 | `View Snapshot` ✅ |
| 商品区 | 评价按钮 | `Leave a review` ✅（评价提交失败故仍存在） |
| 订单摘要 | Item subtotal | £10.00 |
| 订单摘要 | Delivery | £2.59 |
| 订单摘要 | Buyer Protection | £1.20 |
| 订单摘要 | Total | £13.79 |
| 配送地址 | 收件人 | gt2 auto |
| 配送地址 | 地址文本 | `Address available on delivery label` |
| 支付状态横幅 | 消息文本 | `The order is complete and £10.00 will be transferred to your bank account.` ✅ |
| 底部操作区 | 按钮1 | `Message buyer` ✅ |
| 底部操作区 | 按钮2 | `Track order` ✅ |
| 底部操作区 | 按钮3 | `Contact Customer Service` ✅ |

---

### TC022-后验证：买家订单列表（Leave a review 后）

| 元素 | 实测值 |
|------|--------|
| 订单状态标识 | `Completed` ✅ |
| 订单操作按钮 | `Leave a review`（评价提交失败，未更新）🐛 |
| 订单号 | `Order number: {ORDER_NO}` ✅ |

**买家 Completed 订单卡片 "..." 菜单（实测）：**

| 菜单项 | 实测 |
|--------|------|
| View order details | ✅ |
| Message seller | ✅ |
| Track order | ✅ |
| Contact Customer Service | ✅ |
| Report an issue | ❌ 不存在（确认收货后消失） |
| Cancel order | ❌ 不存在 |

### TC023-后验证：卖家订单列表（Leave a review 后）

| 元素 | 实测值 |
|------|--------|
| Tab 位置 | Sold Tab ✅ |
| 订单状态标识 | `Completed` ✅ |
| 订单操作按钮 | `Leave a review`（评价提交失败，未更新）🐛 |
| 订单号 | `Order number: {ORDER_NO}` ✅ |

**卖家 Completed 订单卡片 "..." 菜单（实测）：**

| 菜单项 | 实测 |
|--------|------|
| View order details | ✅ |
| Message buyer | ✅ |
| Track order | ✅ |
| Contact Customer Service | ✅ |
| Cancel order | ❌ 不存在 |

---

## 📋 附：Webhook 物流状态 UI 变化汇总（实测）

| Webhook 阶段 | 买家订单列表状态 | 买家订单详情状态 | 进度条激活节点 | 买家操作按钮变化 | 卖家订单列表状态 | 卖家订单详情状态 | 卖家操作按钮变化 |
|---|---|---|---|---|---|---|---|
| **下单成功（初始）** | In progress \| Awaiting dispatch | Awaiting Dispatch | Paid (13 Apr) | View order details | In progress \| Awaiting dispatch | Awaiting Dispatch | Create Label |
| **创建面单后** | In progress \| Awaiting dispatch | Awaiting Dispatch | Paid (13 Apr) | View order details | In progress \| Awaiting dispatch | Awaiting Dispatch | View Label（Create Label→View Label） |
| **AC（揽收）** | In progress \| On its way | On its way | Paid + Dispatched (13 Apr) | Track order（Cancel order消失） | In progress \| On its way | On its way | Track order（View Label→Track order） |
| **IT（运输中）** | In progress \| On its way（同AC） | On its way（同AC） | Paid + Dispatched | Track order | In progress \| On its way（同AC） | On its way | Track order |
| **SP（到达自提点）** | In progress \| Arrived at pick-up point | Arrived at pick-up point | Paid + Dispatched + Arrived (13 Apr) | Track order | In progress \| Arrived at pick-up point ✅ | Arrived at pick-up point ✅ | Track order ✅ |
| **DE（签收/取件）** | In progress \| Picked up | Picked up，`Confirm by 15 Apr` | Paid + Dispatched + Arrived + Picked up (13 Apr) | I'm happy with my item（商品区）+ Track order + Report an issue | In progress \| Picked up ✅ | Picked up；支付状态消息：`The parcel is already delivered. Once the item is confirmed by the buyer, we will transfer the funds to your bank account.` ✅ | Track order ✅ |
| **买家确认收货** | Completed | Order Completed | 全部激活+Completed (13 Apr) | Leave a review（商品区）+ Track order + Contact Customer Service | Completed ✅ | Order Completed；支付状态消息：`The order is complete and £10.00 will be transferred to your bank account.` ✅ | Leave a review（商品区）+ Message buyer + Track order + Contact Customer Service ✅ |
| **Leave a review（评价）** | Completed（状态不变） | Order Completed（状态不变），`Leave a review` 按钮仍存在（评价 API 报错） 🐛 | 全部激活（不变） | Leave a review（仍显示，未变为"已评价"状态）🐛 | Completed（状态不变）✅ | Order Completed（状态不变），`Leave a review` 按钮仍存在 🐛 | Leave a review（仍显示）🐛 |
| **ITRETURN（在途退回）** | Suspended 🟡 | Order Suspended；提示卡：`Your order has been suspended` + `Your parcel is being returned to the seller...` | `Paid→Dispatched→Sent back→Suspended🟡`（4步） | `Contact Customer Service`（绿色）；`Track order` 消失 | Suspended 🟡 | Order Suspended；提示卡：`Your order has been suspended` + `The buyer's parcel is on its way back to you...`；Payment status: `Funds is on hold` | `Contact Customer Service`（绿色）；无其他操作按钮 |
| **DE（卖家签收退回包裹，ITRETURN 后）** | Cancelled ⚫ | Order Cancelled；Order cancelled 卡：`This order has been cancelled.` + `Reason: Parcel returned to seller`；Refund to: VISA ending in 1119 | `Paid→Dispatched→Sent back→Suspended🟡→Seller receipt→Cancelled🟡→Refunded✅`（7步完整） | **全部消失**（终态） | Cancelled ⚫ | Order Cancelled（同买家）；Payment status: `The funds have already been refunded to the buyer.`；无 Refund to 区域 | **全部消失**（终态） |

> ✅ 表示已通过实际操作验证（v5.0 新增实测）  
> 🐛 表示发现缺陷：评价提交 API 在 unicorn 环境返回错误 `"There's been an error processing your request"`，`Leave a review` 按钮状态未正确更新为已评价状态（买家和卖家双方均复现）  
> ⚠️ Oracle 修正（TC039）：业务文档预测 DE 后状态为 "Returned to seller"，实测为 **"Order Cancelled"**（系统直接取消并退款）

---

## 📝 文档更新日志

### v5.1 (2026-04-16) - 脚本对齐与编号说明补充

**本次更新内容**：

1. **新增：测试用例编号说明部分** (lines 87-143)
   - 📋 添加完整的文档TC编号与脚本TC编号对应关系表
   - ⚠️ 解释编号差异原因：文档采用业务流程顺序编号，脚本采用执行顺序编号
   - 🔍 提供快速查找对照表（按脚本方法名查找 / 按文档用例查找）
   - 💡 说明触发方式差异：买家评价一致（订单详情页），卖家评价有差异（文档描述列表触发，脚本实现详情页触发）

2. **确认已更新：TC018-generated 面单成功页UI文案** (lines 863-864)
   - ✅ 页面标题：`Your label is ready!` → **`Label Generated`**
   - ✅ 提示文案：旧版"Congratulations..."→ **`We sent a QR code and a label to your email address.`**
   - ✅ 有效期文案：`by [到期日期]` → **`This label will be valid until {创建日期+8}.`**
   - ✅ 新增二级标题：**`Evri QR Code`** (h2)
   - ✅ 精准定位说明：通过 `alt="QR Code"` 避开隐藏tracking图片

3. **确认已更新：TC011 前置校验步骤** (lines 454-466)
   - ✅ 新增步骤1：前置校验（检查URL、自提点可见性）
   - ✅ 环境问题处理：自提点丢失时自动重新选择
   - ✅ 新增步骤2：显式点击VISA卡区域确保选中
   - ✅ 新增步骤4：等待时间说明（60-120秒）

4. **确认已更新：TC023 买卖双方订单完整实测结果** (lines 1172-1229)
   - ✅ 买家订单列表：Leave a review按钮、三点菜单内容、Report an issue消失
   - ✅ 卖家订单列表：完整元素校验（状态、按钮、菜单、Cancel order消失）
   - ✅ 卖家订单详情：全量元素校验（5节点进度条、支付状态消息文案变更、所有按钮状态）

**关键改进**：
- 🎯 **消除编号混淆**：通过新增编号说明部分，明确文档与脚本编号对应关系，避免使用时的困惑
- 📊 **提高文档一致性**：确保文档描述与脚本实现（基于2026-04-20 MCP快照）完全一致
- 🔧 **增强可维护性**：补充脚本新增的健壮性增强措施（前置校验、防御性操作），便于后续维护

**文档版本更新**：
- 更新版本号：v5.0 → **v5.1**
- 更新日期：2026-04-16
- 主要变更：补充脚本对齐说明，消除文档与脚本编号差异的困惑

---

### v5.2 (2026-04-16) - 规范化为 web-qa-brain skill 标准格式

**本次更新目标**：
- 🎯 按照 `@.claude/skills/web-qa-brain/SKILL.md` 的标准格式补充脚本中有但文档缺失的验证点
- 📋 规范所有用例属性格式（从 `P0 | ✅ 可自动化` → 标准三行格式）
- ✅ 将脚本已实测但文档标注为 `⚠️ 待实测确认` 的内容更新为 `✅ 实测`

**详细补充内容**：

1. **TC006 - 卖家视角广告页** (lines 285-302)
   - ⚠️ **Oracle 修正**：原文档"Buy now 按钮不可见"，实测为**禁用状态**（disabled，按钮可见但不可点击）
   - ✅ 补充实测：卖家账号登录步骤、Delivery from £2.59 可见性、Buyer Protection 可见性

2. **TC011 - 支付成功页** (lines 473-490)
   - ✅ 补充实测文案：`Your order was placed successfully`
   - ✅ 补充实测文案：`Will be dispatched by` + 日期
   - ✅ 补充实测文案：`Order No.` 标签 + 8位数字
   - ✅ 补充配送方式：`Deliver to pick-up point`
   - ✅ 补充自提点名称：`LONDIS`
   - ⚠️ **脚本缺失标注**：总金额、VISA卡信息在脚本中未明确校验

3. **TC011c - 买家订单详情** (lines 577-618)
   - ✅ **重要修正**：进度条节点数量从**3节点**（误标为Home delivery）更正为**4节点**（自提点订单）
   - ✅ 更正费用明细：从 £50订单 → **£20订单**（Item subtotal £20.00 + Delivery £2.59 + Buyer Protection £1.70 = Total £24.29）
   - ✅ 更正配送信息区域：从"Delivery address"（到家配送）→ **"Pick-up point"**（自提点订单），包含完整自提点地址和时效说明
   - ⚠️ **脚本缺失标注**：支付时间戳格式（文档有描述但脚本未验证）

4. **TC020 AC Webhook - 买家订单详情** (lines 1009-1016)
   - ✅ 补充验证：`Arrived` 和 `Picked up` 节点**未**激活（灰色）
   - ✅ 补充验证：`Track order` 按钮可见
   - ✅ 明确标注：进度条两个节点已激活，**含日期**

5. **TC020b IT Webhook** (lines 1030-1055)
   - ✅ 新增：前置条件（TC020 AC 已触发，订单状态 `On its way`）
   - ✅ 新增：详细执行步骤（刷新页面、进入详情、切换账号）
   - ✅ 规范化：用例属性从简写格式改为标准三行格式

6. **TC020c AT Webhook** (lines 1058-1084)
   - ✅ 新增：前置条件（TC020b IT 已触发）
   - ✅ 新增：业务规则说明（自提点订单跳过AT状态，AT适用到家配送）
   - ✅ 新增：详细执行步骤
   - ✅ 新增：用例属性（P2 / 正向/物流状态 / ✅ 可自动化）

7. **TC021 SP Webhook** (lines 1092-1107)
   - ✅ 补充：详细执行步骤（刷新列表、进入详情、切换账号验证）

8. **TC022 DE Webhook** (lines 1147-1189)
   - ✅ 补充：详细执行步骤（调用webhook、刷新页面、校验进度条、校验按钮）
   - ✅ 规范化：用例属性从简写格式改为标准三行格式（P0 / 正向/物流状态(E2E核心路径) / ✅ 可自动化）

9. **TC025 - 买家评价卖家** (lines 1295-1367)
   - ✅ **完整替换**：从 `⚠️ 待实测确认` 更新为**完整的3步流程实测结果**
   - ✅ 补充实测：Step 1 评分选择（5星、描述文字 `It was great`、Continue 按钮状态变化）
   - ✅ 补充实测：Step 2 好评标签（9个标签选项、多选逻辑、Continue可跳过）
   - ✅ 补充实测：Step 3 差评标签（8个标签选项、Continue变为Submit review）
   - 🐛 补充实测：unicorn环境API错误（评价提交失败、错误弹窗文案、Leave a review按钮未更新）
   - 🤖 补充自动化实现细节：
     - `data-testid="dialog-content"` 作用域限定
     - `get_by_test_id("star-button").nth(4)` 选中第5颗星
     - `get_by_role("button", name="Friendly")` 标签点击
     - 错误弹窗捕获与处理（`dialog.accept()`）
   - ✅ 补充验证：订单列表三点菜单中**无 `Leave a review` 入口**（仅在详情页商品区显示）
   - ⚠️ 更新用例属性：从 `✅ 可自动化` → `⚠️ 部分可自动化（UI交互可测，API提交受环境限制）`

**格式规范化统计**：
- 📋 前置条件：新增/补充 6 处
- 🎬 执行步骤：详细化 7 处
- ✅ 预期结果：从 `⚠️ 待实测` 更新为 `✅ 实测` 共 15+ 验证点
- 📊 用例属性：规范化格式 5 处（从 `P0 | ✅` 简写 → 标准三行）
- 🤖 自动化实现细节：新增脚本定位器说明（TC025）
- ⚠️ Oracle 修正：标注 3 处（TC006 Buy now状态、TC011c 进度条节点数、TC011c 费用明细）

**关键改进**：
- 📐 **严格遵循 web-qa-brain skill 标准**：所有用例包含完整的 📋 前置条件、🎬 执行步骤、✅ 预期结果、📊 用例属性四部分
- 🔬 **消除推断，增加实测**：将文档中的 `⚠️ 待实测确认` 替换为基于通过脚本的 `✅ 实测` 结果
- 🎯 **提高验证颗粒度**：将"显示配送信息"展开为精确字段（`Deliver to pick-up point` + `LONDIS` + 完整地址）
- 🐛 **标注环境差异**：明确区分功能实现与环境限制（TC025 API错误）
- 🤖 **增强自动化可维护性**：补充关键定位器（`data-testid`、`.nth()`）和错误处理逻辑

**文档版本更新**：
- 更新版本号：v5.1 → **v5.2**
- 更新日期：2026-04-16
- 主要变更：**补充脚本实测细节，规范化为 web-qa-brain skill 标准格式**

---

### v5.3 (2026-04-16) - 补充脚本健壮性实现细节（基于详细对比分析）

**本次更新目标**：
- 🎯 根据 `SCRIPT_VS_DOC_COMPARISON.md` 对比分析报告，补充脚本中的健壮性处理逻辑
- 🔧 添加 "🤖 自动化实现细节" 部分，记录兜底策略、等待时间、容错处理
- ✅ 更正实现差异（触发入口、标签选择数量、错误处理方式）

**详细补充内容**：

1. **TC001 - 发布广告** (新增自动化实现细节)
   - ✅ **草稿恢复弹窗处理**：2种按钮文本兜底（`No thanks` / `Discard`），timeout=2000
   - ✅ **等待表单加载**：`ad-title-input` 可见性验证（timeout=30000），确保表单 DOM 完全渲染
   - ✅ **发布后跳转处理**：支持两种 URL 模式（`/p/` 直接跳转 / `/thankyou/` 感谢页）
   - ✅ **感谢页处理完整流程**（lines 389-428）：
     - 策略1：查找 "View your ad" 链接（6种选择器兜底）
     - 策略2：通过 `/manage/ads` 查找广告（从 URL 提取 advertId）
     - 隐私弹窗处理：连续 dismiss overlays 两轮（间隔800ms）

2. **TC007 - 买家结账选择自提点** (新增自动化实现细节)
   - ✅ **点击 Buy now 实现差异**：使用 `.nth(1)` 选择 sticky 区域按钮（避免滚动超时）
   - ✅ **输入地址健壮性处理**：
     - `addr_input.click()` 确保聚焦
     - `addr_input.fill("")` 清空缓存
     - `keyboard.type(..., delay=80)` 模拟真实打字（触发联想）
     - 等待 **2500ms** 等待 Google Places API
   - ✅ **选择地址建议的6层兜底策略**（lines 551-586）：
     - 策略1：6种 CSS 选择器（`.pac-item` / `.dialog-content li` / `[role='option']` 等）
     - 策略2：文字模糊匹配（"24-26 Railway" / "Railway Street" / "Altrincham"）
     - 策略3：键盘导航（`ArrowDown + Enter`）
   - ✅ **关键等待时间汇总**：
     - 2500ms：输入地址后等待建议
     - 4000ms：选择建议后等待列表刷新
     - 20000ms：等待 LONDIS 可见
     - 1500ms：点击 LONDIS 后等待详情展开
     - 15000ms：等待弹窗关闭
   - ✅ **scroll_into_view_if_needed**：确保 "Choose this pick-up point" 按钮在视口内

3. **TC023 - 买家确认收货** (新增自动化实现细节)
   - ✅ **触发入口实现差异**：脚本从订单**列表**触发（效率更高），文档描述从**详情页**触发，UI 支持两种方式
   - ✅ **弹窗内确认的3层兜底策略**（lines 1410-1429）：
     - 策略1：尝试3种容器选择器（`data-testid='dialog-content'` / `.dialog-content` / `[role='dialog']`）
     - 策略2：兜底方案使用 `.last` 按钮（假设弹窗按钮在 DOM 后出现）
     - 每个策略 timeout=2000 快速检测
   - ✅ **确认后等待**：`page.wait_for_timeout(4000)`（等待异步 API 完成）
   - ✅ **验证策略优化**：
     - 优先验证详情页（不依赖列表刷新）
     - 使用 `Leave a review` 按钮判断完成状态（避免 Filter 下拉框干扰）
     - 5节点循环验证
   - ⚠️ **脚本不完整标注**：三点菜单使用 `.nth(3)` 硬编码 + `try/except` 跳过失败

4. **TC025 - 买家评价卖家** (更正实现差异)
   - 🔧 **Step 2 标签选择数量**：更正为只选 `Item as described`（1个），非 `Friendly` + `Item as described`（2个）
   - 🔧 **错误处理方式**：更正为 `page.get_by_role("button", name="Close").last.click()`，非 `dialog.accept()`
   - ⚠️ **脚本不完整标注**：三点菜单验证使用 `.nth(3)` 硬编码，未严格验证每个菜单项

**格式规范统计**：
- 🤖 新增自动化实现细节：3 个测试用例（TC001 / TC007 / TC023）
- 🔧 更正实现差异：2 处（TC025 标签选择 / 错误处理）
- ⏱️ 记录关键等待时间：TC007 有 5 个关键等待点
- 🎯 记录兜底策略：TC001 有 2 层策略、TC007 有 3 层策略、TC023 有 2 层策略
- ⚠️ 标注脚本不完整：三点菜单验证（`.nth(3)` 硬编码）

**关键改进**：
- 📐 **完整记录健壮性处理**：将脚本中的 `try/except` 兜底逻辑、多选择器尝试策略完整记录到文档
- ⏱️ **明确等待时间**：记录所有关键等待点及其原因（API响应/动画完成/DOM刷新）
- 🔍 **标注实现局限**：明确指出脚本使用硬编码索引、`try/except` 跳过等不够健壮的实现
- 🎯 **消除实现差异**：更正文档中与脚本不一致的描述（标签选择数量、错误处理方式）

**文档版本更新**：
- 更新版本号：v5.2 → **v5.3**
- 更新日期：2026-04-16
- 主要变更：**补充脚本健壮性实现细节（草稿弹窗/感谢页处理/6层地址建议兜底/弹窗确认兜底），更正实现差异**

---

