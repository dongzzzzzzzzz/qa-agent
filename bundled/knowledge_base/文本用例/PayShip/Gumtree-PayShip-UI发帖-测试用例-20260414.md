# Gumtree 支付物流帖子 UI 发帖测试用例

**版本**: 1.0  
**创建日期**: 2026-04-14  
**测试范围**: 账号切换（SessionManager） / UI 页面操作发帖 / 支付物流开关验证 / 价格与物流开关联动 / Manage My Ads 标签验证 / 包裹规格与配送费验证 / 编辑帖子物流状态联动  
**测试环境**: Unicorn（https://www.unicorn.gumtree.io/）  
**测试用例总数**: 27 个（模块一为前置依赖工具类，不计入测试用例）  

---

## 📋 测试环境配置

### 测试账号

| 角色 | 账号 | 密码 | 用途 |
|------|------|------|------|
| 卖家 | gtauto5858@outlook.com | autoGt5858! | 发布帖子、验证 Manage My Ads |
| 买家 | gtauto25858@outlook.com | autoGt5858! | 备用，本模块不涉及 |

### 支持的测试环境

| 环境名称 | 环境代码 | 主站 URL | My 站 URL |
|---------|---------|---------|----------|
| **Zoidberg** | `zoidberg` | https://www.zoidberg.gumtree.io | https://my.zoidberg.gumtree.io |
| **Bixi** | `bixi` | https://www.bixi.gumtree.io | https://my.bixi.gumtree.io |
| **Gaga** | `gaga` | https://www.gaga.gumtree.io | https://my.gaga.gumtree.io |
| **Taro** | `taro` | https://www.taro.gumtree.io | https://my.taro.gumtree.io |
| **Unicorn** | `unicorn` | https://www.unicorn.gumtree.io | https://my.unicorn.gumtree.io |
| **Staging** | `staging` | https://www.staging.gumtree.io | https://my.staging.gumtree.io |
| **Production** | `prod` | https://www.gumtree.com | https://my.gumtree.com |

### 通用配置

```yaml
测试配置:
  浏览器: Chrome/Chromium (Playwright)
  视口尺寸: 1523x800 (桌面端)
  超时设置: 30秒

工具类:
  SessionManager:
    文件: utils/session_manager.py
    用途: 账号状态检测、API 免密登录、storage_state 保存/恢复

发帖入口:
  顶部导航 → "Sell" 按钮 → 类目选择页 (/postad/category)

测试图片:
  Freebies 类目（不支持物流）:
    路径: test_image.jpg
    用途: 模块二发帖上传
  Men's Formal Shoes 类目（支持物流）:
    路径: pic/shoes.png
    规格: 473×1024 PNG
    用途: 模块三、四发帖上传

类目路径（不支持物流）:
  For Sale → Freebies
  URL 路径: for-sale → freebies

类目路径（支持物流）:
  For Sale → Clothes, Footwear & Accessories
    → Men's Shoes & Boots → Men's Formal Shoes
  URL 路径: for-sale → clothes-footwear-accessories
    → mens-shoes-boots → mens-formal-shoes

支付物流开关规则（价格联动）:
  价格 < £1      → 物流开关自动关闭（不可启用）
  £1 ≤ 价格 ≤ £250 → 物流开关可开启（自动开启或允许手动开启）
  价格 > £250    → 物流开关自动关闭（超出配送价格上限）

包裹规格说明（开启物流后必选）:
  Small  → 配送费 £2.59
  Medium → 配送费 £2.99
  Large  → 配送费 £3.49
  规格选择后，VIP 页展示对应配送费（"Delivery from £2.59/£2.99/£3.49"）
  VIP 页同步展示买家保护费（"Buyer Protection"）= 商品价格 × 5% + £0.70（四舍五入）

Manage My Ads 物流标签说明:
  已启用物流              → 帖子卡片显示 "Delivery enabled" 标签
                           （类目支持 + 价格 £1–£250 + 卖家手动开启物流）
  价格在范围内但未开启物流 → 帖子卡片显示 "Eligible for delivery" 标签
                           （类目支持 + 价格 £1–£250 + 卖家手动关闭物流）
  价格超出范围            → 帖子卡片无任何物流标签
                           （价格 < £1 或价格 > £250，即使类目支持物流）
  类目不支持物流          → 帖子卡片无任何物流标签
```

---

## 📖 Application Overview

### 功能描述

Gumtree 的支付物流（Pay & Ship）功能允许卖家在 UI 发帖流程中手动开启在线支付和物流配送开关。系统根据**帖子类目**和**价格区间**两个维度自动控制开关的可用性：仅特定类目（如服装、配件等）支持物流，且价格需在 £1–£250 区间内，超出范围开关自动关闭。

### 业务规则

| 规则 | 说明 |
|------|------|
| 类目限制 | Freebies 等部分类目不支持物流开关，发帖页不显示物流选项 |
| 价格下限 | 价格 < £1 时，物流开关自动关闭且不可手动开启 |
| 价格正常区间 | £1 ≤ 价格 ≤ £250 时，物流开关可开启（可启用在线支付） |
| 价格上限 | 价格 > £250 时，物流开关自动关闭（超出配送价格上限） |
| Manage My Ads 标签 | 开启物流 → "Delivery enabled"；价格在范围内但未开启 → "Eligible for delivery"；价格 < £1 或 > £250 → 无任何物流标签 |
| 包裹规格 | 开启物流后需选择包裹规格（Small / Medium / Large），规格影响 VIP 页展示的配送费金额 |
| 配送费 | 按包裹规格固定收费：**Small = £2.59** / **Medium = £2.99** / **Large = £3.49** |
| 买家保护费 | Buyer Protection Fee = 商品价格 × 5% + £0.70（四舍五入到两位小数）。例：£50 → £3.20，£80 → £4.70 |
| 账号前置 | 所有发帖操作需以卖家账号登录，通过 SessionManager 判断并切换账号 |

### SessionManager 账号切换逻辑

```
1. 检查当前 context 是否已登录 → auth_helper.is_logged_in()
2. 如已登录，检查是否是卖家账号 → auth_helper.is_same_account(SELLER_EMAIL)
3. 若不是卖家账号 → session_manager.api_login_and_save(page, SELLER_EMAIL, SELLER_PASS, env)
   或 auth_helper.logout() → auth_helper.login(SELLER_EMAIL, SELLER_PASS)
4. 若未登录 → session_manager.load_state(browser, SELLER_EMAIL)
   或 session_manager.api_login_and_save(page, SELLER_EMAIL, SELLER_PASS, env)
```

### 页面状态

| 页面 | URL | 描述 |
|------|-----|------|
| 类目选择页 | `/postad/category` | 发帖入口，选择一级类目 |
| 帖子编辑页 | `/postad/{editorId}` | 填写帖子详情，含物流开关 |
| Bumpup 页 | `/postad/{editorId}/bumpup` | 推广选项页（点击 No thanks 跳过） |
| Manage My Ads | `/manage/ads` 或 `my.*/manage/ads` | 验证帖子状态及物流标签 |

---

## 🧪 测试用例

---

### 模块一：前置依赖 — 账号切换工具类（SessionManager）

> ⚠️ **脚本生成说明**：本模块为**前置依赖**，不生成独立测试步骤脚本。  
> 生成测试脚本时，应将以下逻辑封装为**工具类方法**（`conftest.py` fixture 或独立 helper），供后续模块（二、三、四）在 `setup` 阶段调用。

---

#### 工具类接口规范

**接口一：ensure_seller_login(page, session_manager, auth_helper)**  
**说明**: 确保当前浏览器 context 以卖家账号登录，若不是则自动切换  
**封装目标**: `conftest.py` 中的 `seller_page` fixture 或 `PayShipHelper.ensure_seller_login()`

**逻辑描述**:
1. 实例化 `AuthHelper(page, base_url="https://www.unicorn.gumtree.io")`
2. 调用 `auth.is_logged_in()` 检查当前登录状态
3. 若已登录，调用 `auth.is_same_account("gtauto5858@outlook.com")` 检查是否为卖家账号
4. 若已是卖家账号，直接返回，无需切换
5. 若不是卖家账号（或未登录），调用 `session_manager.api_login_and_save(page, "gtauto5858@outlook.com", "autoGt5858!", env="unicorn")` 完成登录

**预期行为**:
- 若当前已是卖家账号：直接返回，无副作用
- 若不是卖家账号或未登录：`api_login_and_save()` 执行后，`is_logged_in()` 和 `is_same_account("gtauto5858@outlook.com")` 均返回 `True`
- SessionManager 通过 API 登录（约 1 秒），无需走登录表单

**备注**:
- storage_state 文件保存至 `temp/session_storage/state_gtauto5858_outlook_com.json`，包含 13 个以上 Cookie

---

**接口二：load_seller_context(browser, session_manager)**  
**说明**: 从已保存的 storage_state 文件直接创建已登录的卖家 BrowserContext  
**封装目标**: `conftest.py` 中的 `seller_context` fixture

**逻辑描述**:
1. 调用 `session_manager.has_state("gtauto5858@outlook.com")` 检查是否有已保存状态
2. 若有，调用 `session_manager.load_state(browser, "gtauto5858@outlook.com")` 创建 context
3. 在 context 中创建 page 并导航到 `https://my.unicorn.gumtree.io/manage/ads` 验证登录有效

**预期行为**:
- `load_state()` 返回非 None 的 BrowserContext
- 导航到 manage/ads 时 URL 不含 `/login`，页面显示 "Hi auto!"
- 整个过程无需任何登录表单操作

---

### 模块二：发布不支持物流的帖子（Freebies 类目）

---

**TC-PSUI-010**  
**标题**: 在 Freebies 类目发帖，验证物流开关不存在  
**优先级**: P0  
**类型**: 功能验证  

**前置条件**:
- 已以卖家账号 `gtauto5858@outlook.com` 登录（通过 TC-PSUI-001 完成）
- 当前位于 `https://www.unicorn.gumtree.io`

**测试步骤**:
1. 点击顶部导航 "Sell" 按钮，进入类目选择页 `/postad/category`
2. 选择一级类目 **"For Sale"**
3. 在子类目列表中选择 **"Freebies"**
4. 进入帖子编辑页（`/postad/{editorId}`）
5. 观察页面中是否存在支付物流开关（"Delivery"、"Pay & Ship"、"Support shipping" 等相关 UI）

**预期结果**:
- 页面不显示任何支付物流相关开关或选项
- 帖子编辑页中没有 "Delivery" / "Pay & Ship" / "Shipping" 选项区域

---

**TC-PSUI-011**  
**标题**: 在 Freebies 类目填写帖子信息并发布，验证无物流标签  
**优先级**: P0  
**类型**: 端到端验证  

**前置条件**:
- 已以卖家账号登录
- 已进入 Freebies 类目编辑页（继续 TC-PSUI-010）

**测试步骤**:
1. （首次发帖时）若出现 **"Please add your location"** 弹窗，输入 postcode `TW9 1EJ`，点击 **"Go"** 按钮关闭弹窗
2. 在帖子编辑页填写以下信息：
   - 标题：`UI Test Freebie Ad [时间戳]`（如 `UI Test Freebie Ad 20260414_001`）
   - 描述：`Test freebie advert, no shipping support`
   - 地区：选择伦敦区域（如 London / Richmond）
3. 上传图片：选择工程根目录下的 `test_image.jpg` 文件上传
   - 观察上传进度/loading 状态
   - 确认图片上传完成后，编辑页中显示图片缩略图（可预览）
4. 确认无物流开关后，点击 **"Post your ad"** / **"Publish"** 按钮发布帖子
5. 若出现 Bumpup 推广页，点击 **"No thanks"** / **"Skip"** 跳过
6. 等待帖子发布成功，记录帖子 VIP URL（若发布后自动跳转到 VIP 页）
7. 导航到 `https://www.unicorn.gumtree.io/manage/ads`（注意：是 www 域名，不是 my 域名）
8. 在帖子列表中找到新发布的帖子（通过标题匹配）
9. 检查帖子卡片内容（物流标签、基本信息）
10. 从帖子卡片中提取完整的 VIP 链接（用于后续 TC-PSUI-012 验证）

**预期结果**:
- 图片上传成功，编辑页中显示图片缩略图（可预览）
- 帖子成功发布
- 在 Manage My Ads 页面：
  - 找到新发布的帖子（标题匹配）
  - 帖子卡片中 **不显示** "Delivery enabled" 标签
  - 帖子卡片中 **不显示** "Eligible for delivery" 标签
  - 帖子卡片显示基本信息：
    - 标题（与发帖时填写的一致）
    - 地区（如 "Richmond, London" 或 "TW9 1EJ"）
    - 发布时间（如 "Posted 1 minute ago" 或具体时间）
    - Ad ID（格式如 "Ad ID: 12345678"）
  - （可选）帖子卡片显示状态标签为 "Live"（或通过卡片样式判断为 Live 状态）
  - 成功提取 VIP 链接（完整 URL，格式如 `https://www.unicorn.gumtree.io/p/[slug]/[adId]`）


---

**TC-PSUI-012**  
**标题**: Freebies 帖子的 VIP 页不展示物流支付组件  
**优先级**: P1  
**类型**: UI 验证  

**前置条件**:
- TC-PSUI-011 已完成，Freebies 帖子已发布

**测试步骤**:
1. 在 Manage My Ads 中点击帖子标题，进入 VIP 页
2. 检查 VIP 页右侧交互卡片区域

**预期结果**:
- VIP 页 **不显示** "Delivery from £X.XX" 文字
- VIP 页 **不显示** "Buyer Protection £X.XX" 文字
- VIP 页 **不显示** "Buy now" 按钮
- 只显示 "Message"、"Favourite"、"Report" 等标准按钮

---

### 模块三：发布支持物流的帖子（Men's Formal Shoes 类目，价格 £50）

---

**TC-PSUI-020**  
**标题**: 在 Men's Formal Shoes 类目发帖，验证物流开关存在且可开启  
**优先级**: P0  
**类型**: 功能验证  

**前置条件**:
- 已以卖家账号登录
- 当前位于 `https://www.unicorn.gumtree.io`

**测试步骤**:
1. 点击顶部导航 "Sell" 按钮，进入类目选择页
2. 依次选择类目路径：
   - **For Sale** → **Clothes, Footwear & Accessories** → **Men's Shoes & Boots** → **Men's Formal Shoes**
3. 进入帖子编辑页
4. 观察页面中是否存在支付物流相关开关

**预期结果**:
- 帖子编辑页中显示物流开关（"Delivery" / "Pay & Ship" / "Support shipping" 等相关 UI 组件）
- 物流开关处于可交互状态（非置灰/禁用）

---

**TC-PSUI-021**  
**标题**: 验证物流开关可以手动开启  
**优先级**: P0  
**类型**: 功能验证  

**前置条件**:
- 已进入 Men's Formal Shoes 类目编辑页（继续 TC-PSUI-020）
- 物流开关存在

**测试步骤**:
1. 找到物流开关（toggle / checkbox）
2. 确认开关初始状态（开启）
3. 若初始为开启状态，点击开关将其关闭
4. 观察开关状态变化
5. 点击开关将其开启，观察开关状态变化

**预期结果**:
- 物流开关可以成功切换为开启状态
- 开启后开关 UI 显示为激活状态（如绿色 toggle、勾选状态）
- 页面可能显示物流费用预估信息

---

**TC-PSUI-022**  
**标题**: 上传图片、填写价格 £50，开启物流，发布帖子，验证 Manage My Ads 物流标签  
**优先级**: P0  
**类型**: 端到端验证  

**前置条件**:
- 已进入 Men's Formal Shoes 类目编辑页
- 物流开关已确认存在

**测试步骤**:
1. （首次发帖到该类目时）若出现 **"Please add your location"** 弹窗，输入 postcode `TW9 1EJ`，点击 **"Go"** 按钮关闭弹窗
2. 上传图片：选择工程中的 `pic/shoes.png` 文件上传
   - 观察上传进度/loading 状态
   - 确认图片上传完成后，编辑页中显示图片缩略图
3. 填写以下信息：

   - 标题：`UI Test Shoes Ad £50 [时间戳]`（如 `UI Test Shoes Ad 50 20260414_002`）
   - 描述：`Test shoes advert with shipping enabled, price £50`
   - 价格：输入 `50`
   - 地区：选择伦敦区域
4. 开启物流开关（若未自动开启）
5. 确认物流开关处于开启状态后，点击 **"Post your ad"** / **"Publish"** 发布帖子
6. 若出现 Bumpup 推广页，点击 **"No thanks"** / **"Skip"** 跳过
7. 等待帖子发布成功
8. 导航到 `https://www.unicorn.gumtree.io/manage/ads`（注意：是 www 域名）
9. 在帖子列表中找到新发布的帖子（通过标题匹配）
10. 检查帖子卡片内容（物流标签、价格、基本信息）
11. 从帖子卡片中提取完整的 VIP 链接（用于后续 TC-PSUI-024 验证）

**预期结果**:
- 图片上传成功，编辑页中显示图片缩略图
- 价格 £50 处于物流支持区间（£1–£250），物流开关可开启
- 物流开关成功开启（UI 显示激活状态）
- 帖子成功发布
- 在 Manage My Ads 页面：
  - 找到新发布的帖子（标题匹配）
  - 帖子卡片 **显示物流标签**：
    - "Delivery enabled" 标签（已激活物流配送）
    - 或包含 "Delivery" / "delivery" 等相关文字
  - 帖子卡片显示价格 **£50**
  - 帖子卡片显示基本信息：
    - 标题、地区、发布时间、Ad ID
  - （可选）帖子卡片显示状态标签为 "Live"
  - 成功提取 VIP 链接（用于后续 VIP 页验证）

---

**TC-PSUI-023**  
**标题**: 价格 £70，手动关闭物流开关后发布帖子，验证 Manage My Ads 显示 "Eligible for delivery" 标签  
**优先级**: P0  
**类型**: 端到端验证  

**前置条件**:
- 已以卖家账号登录
- 已进入 Men's Formal Shoes 类目帖子编辑页
- 物流开关存在且处于可交互状态

**测试步骤**:
1. （首次发帖到该类目时）若出现 **"Please add your location"** 弹窗，输入 postcode `TW9 1EJ`，点击 **"Go"** 按钮关闭弹窗
2. 上传图片：选择工程中的 `pic/shoes.png` 文件上传
   - 观察上传进度/loading 状态
   - 确认图片上传完成后，编辑页中显示图片缩略图
3. 填写以下信息：
   - 标题：`UI Test Shoes Ad £70 No Ship [时间戳]`（如 `UI Test Shoes Ad 70 NoShip 20260414_004`）
   - 描述：`Test shoes advert with shipping manually disabled, price £70`
   - 价格：输入 `70`
   - 地区：选择伦敦区域
4. 确认价格 £70 时物流开关处于可开启状态（£1–£250 区间）
5. **手动点击物流开关，将其关闭**
6. 确认物流开关已处于关闭状态
7. 点击 **"Post your ad"** / **"Publish"** 发布帖子
8. 若出现 Bumpup 推广页，点击 **"No thanks"** / **"Skip"** 跳过
9. 等待帖子发布成功
10. 导航到 `https://www.unicorn.gumtree.io/manage/ads`（注意：是 www 域名）
11. 在帖子列表中找到新发布的帖子（通过标题匹配）
12. 检查帖子卡片内容（物流标签、价格、基本信息）
13. 从帖子卡片中提取完整的 VIP 链接（用于后续验证，如需要）

**预期结果**:
- 图片上传成功，编辑页中显示图片缩略图
- 价格 £70 处于物流支持区间，物流开关可被手动关闭
- 物流开关成功关闭（UI 显示未激活状态）
- 帖子成功发布
- 在 Manage My Ads 页面：
  - 找到新发布的帖子（标题匹配）
  - 帖子卡片显示 **"Eligible for delivery"** 标签
    （即：类目支持物流、价格在支持区间，但卖家未开启物流，系统提示可开启）
  - 帖子卡片 **不显示** "Delivery enabled" 标签（未完成支付物流配置）
  - 帖子卡片显示价格 **£70**
  - 帖子卡片显示基本信息：
    - 标题、地区、发布时间、Ad ID
  - （可选）帖子卡片显示状态标签为 "Live"
  - 成功提取 VIP 链接（用于后续验证）

---

**TC-PSUI-024**  
**标题**: 验证价格 £50 的物流帖子 VIP 页正确展示物流支付组件  
**优先级**: P0  
**类型**: UI 验证  

**前置条件**:
- TC-PSUI-022 已完成，帖子已发布

**测试步骤**:
1. 在 Manage My Ads 点击帖子标题，进入 VIP 页
2. 检查 VIP 页右侧交互卡片区域

**预期结果**:
- VIP 页显示价格 "£50"
- 显示 **"Delivery from £2.59"** 文字（默认 Small 规格配送费）
- 显示 **"Buyer Protection £3.20"**（= £50 × 5% + £0.70 = £3.20）
- 显示 "Buy now" 按钮，可点击
- 页面 datalayer 中 `isDelivery` 为 `true`

---

### 模块四：价格与物流开关联动验证（Men's Formal Shoes 类目）

---

**TC-PSUI-030**  
**标题**: 价格输入小于 £1 时，物流开关自动关闭且不可开启  
**优先级**: P0  
**类型**: 边界值验证  

**前置条件**:
- 已以卖家账号登录
- 已进入 Men's Formal Shoes 类目帖子编辑页
- 物流开关存在

**测试步骤**:
1. 在价格输入框中输入 `0`（或 `0.50`）
2. 点击其他区域，触发价格校验
3. 观察物流开关状态变化

**预期结果**:
- 物流开关自动切换为 **关闭** 状态
- 开关可能变为置灰/禁用状态（不可手动开启）
- 页面可能显示提示信息（如 "Shipping is not available for this price"）

---

**TC-PSUI-031**  
**标题**: 价格输入 £0.50（< £1），尝试手动开启物流开关，验证无法开启  
**优先级**: P1  
**类型**: 边界值验证  

**前置条件**:
- 继续 TC-PSUI-030，价格已输入 £0.50，物流开关已自动关闭

**测试步骤**:
1. 尝试点击物流开关，尝试将其开启
2. 观察开关是否能被成功开启

**预期结果**:
- 开关无法被手动开启（点击无效或开关为禁用状态）
- 物流开关保持 **关闭** 状态

---

**TC-PSUI-032**  
**标题**: 价格从 £0.50 修改为 £50（£1–£249 区间），物流开关自动开启  
**优先级**: P0  
**类型**: 联动验证  

**前置条件**:
- 继续 TC-PSUI-031，价格为 £0.50，物流开关处于关闭状态

**测试步骤**:
1. 清除价格输入框中的 `0.50`
2. 输入价格 `50`
3. 点击其他区域，触发价格校验
4. 观察物流开关状态变化

**预期结果**:
- 物流开关自动切换为 **开启** 状态（或变为可开启状态）
- 开关 UI 显示激活状态

---

**TC-PSUI-033**  
**标题**: 价格从 £50 修改为 £251（> £250），物流开关自动关闭  
**优先级**: P0  
**类型**: 边界值验证  

**前置条件**:
- 继续 TC-PSUI-032，价格为 £50，物流开关处于开启状态

**测试步骤**:
1. 清除价格输入框中的 `50`
2. 输入价格 `251`
3. 点击其他区域，触发价格校验
4. 观察物流开关状态变化

**预期结果**:
- 物流开关自动切换为 **关闭** 状态
- 开关可能变为置灰/禁用状态
- 页面可能显示提示信息（如 "Shipping is not available for items priced over £250"）

---

**TC-PSUI-034**  
**标题**: 价格为 £250（= £250 上限值），验证物流开关可以开启  
**优先级**: P1  
**类型**: 边界值验证  

**前置条件**:
- 已进入 Men's Formal Shoes 类目帖子编辑页

**测试步骤**:
1. 在价格输入框中输入 `250`
2. 点击其他区域，触发价格校验
3. 观察物流开关状态

**预期结果**:
- 物流开关处于可开启状态（非禁用）
- 若未自动开启，可手动将其开启
- 开启后开关 UI 显示激活状态

---

**TC-PSUI-035**  
**标题**: 价格 £251 与 £250 的边界切换，验证开关准确响应  
**优先级**: P1  
**类型**: 边界值验证  

**前置条件**:
- 已进入 Men's Formal Shoes 类目帖子编辑页，价格为 £250，物流开关可开启

**测试步骤**:
1. 将价格从 `250` 修改为 `251`，触发校验，观察开关是否关闭
2. 再将价格从 `251` 修改回 `250`，触发校验，观察开关是否重新可开启

**预期结果**:
- 价格 £251：开关自动关闭
- 价格 £250：开关重新变为可开启状态（或自动开启）
- 边界准确，无误判

---

**TC-PSUI-036**  
**标题**: 使用超出物流限价（£300）发布帖子，验证 Manage My Ads 不显示任何物流标签  
**优先级**: P0  
**类型**: 端到端验证  

**前置条件**:
- 已以卖家账号登录
- 已进入 Men's Formal Shoes 类目帖子编辑页

**测试步骤**:
1. 上传图片：选择工程中的 `pic/shoes.png` 文件上传
2. 填写以下信息：
   - 标题：`UI Test Shoes Ad £300 [时间戳]`（如 `UI Test Shoes Ad 300 20260414_003`）
   - 描述：`Test shoes advert with price exceeding shipping limit`
   - 价格：输入 `300`
   - 地区：选择伦敦区域
3. 确认价格输入 `300` 后，物流开关已自动关闭
4. 不手动开启物流开关（保持关闭）
5. 点击 **"Post your ad"** / **"Publish"** 发布帖子
6. 若出现 Bumpup 推广页，点击 **"No thanks"** / **"Skip"** 跳过
7. 等待帖子发布成功，记录帖子 ID
8. 导航到 `https://my.unicorn.gumtree.io/manage/ads`
9. 在帖子列表中找到新发布的帖子（标题匹配）
10. 检查帖子卡片的物流标签

**预期结果**:
- 帖子成功发布，状态为 "Live"
- Manage My Ads 中帖子卡片 **不显示** 任何物流标签
  （价格 £300 > £250，超出物流价格上限，系统不展示 "Delivery enabled" 也不展示 "Eligible for delivery"）
- 帖子卡片显示价格 £300
- 帖子卡片与普通无物流帖子展示相同（仅显示标题、价格、地区等基本信息）

---

**TC-PSUI-037**  
**标题**: 验证价格 £300 帖子的 VIP 页不展示物流支付组件  
**优先级**: P1  
**类型**: UI 验证  

**前置条件**:
- TC-PSUI-036 已完成，帖子已发布

**测试步骤**:
1. 在 Manage My Ads 点击帖子标题，进入 VIP 页
2. 检查 VIP 页右侧交互卡片区域

**预期结果**:
- VIP 页 **不显示** "Delivery from £X.XX" 文字
- VIP 页 **不显示** "Buyer Protection £X.XX" 文字
- VIP 页 **不显示** "Buy now" 按钮
- 页面 datalayer 中 `isDelivery` 为 `false`

---

### 模块五：包裹规格与 VIP 页配送费验证（Men's Formal Shoes 类目）

---

> **说明**：本模块需分别发布 3 条帖子，各选择不同包裹规格（Small / Medium / Large），验证 VIP 页配送费和买家保护费随规格变化正确展示。
>
> **业务规则**：
> - 配送费（Delivery Fee）按包裹规格固定收费：**Small = £2.59** | **Medium = £2.99** | **Large = £3.49**
> - 买家保护费（Buyer Protection Fee）= 商品价格 × 5% + £0.70，四舍五入到两位小数
>   - 例：商品价格 £50 → 50 × 0.05 + 0.70 = **£3.20**

---

**TC-PSUI-040**  
**标题**: 选择 Small 包裹规格发布帖子，验证 VIP 页配送费与买家保护费正确展示  
**优先级**: P0  
**类型**: 端到端验证  

**前置条件**:
- 已以卖家账号登录
- 已进入 Men's Formal Shoes 类目帖子编辑页
- 物流开关存在

**测试步骤**:
1. （首次发帖到该类目时）若出现 **"Please add your location"** 弹窗，输入 postcode `TW9 1EJ`，点击 **"Go"** 按钮关闭弹窗
2. 上传图片：选择工程中的 `pic/shoes.png` 文件上传
   - 观察上传进度/loading 状态
   - 确认图片上传完成后，编辑页中显示图片缩略图
3. 填写以下信息：
   - 标题：`UI Test Shoes Small Parcel [时间戳]`（如 `UI Test Shoes Small 20260414_005`）
   - 描述：`Test shoes advert with small parcel size`
   - 价格：输入 `50`
   - 地区：选择伦敦区域
4. 开启物流开关（若未自动开启）
5. 在包裹规格选项中选择 **"Small"**
6. 记录页面上显示的配送费预估值（如 "Delivery from £X.XX"）
7. 点击 **"Post your ad"** / **"Publish"** 发布帖子
8. 若出现 Bumpup 推广页，点击 **"No thanks"** / **"Skip"** 跳过
9. 等待帖子发布成功
10. 导航到 `https://www.unicorn.gumtree.io/manage/ads`
11. 在 Manage My Ads 找到新发布的帖子（通过标题匹配），检查物流标签
12. 从帖子卡片中提取完整的 VIP 链接
13. 点击帖子标题进入 VIP 页，检查右侧交互卡片区域

**预期结果**:
- 图片上传成功，编辑页中显示图片缩略图
- 物流开关开启后，页面显示包裹规格选项（Small / Medium / Large）
- 选择 Small 后，发帖页显示对应 Small 规格的配送费预估
- 帖子成功发布
- 在 Manage My Ads 页面：
  - 找到新发布的帖子（标题匹配）
  - 帖子卡片显示 **"Delivery enabled"** 标签
  - 帖子卡片显示价格 **£50**
  - 帖子卡片显示基本信息：标题、地区、发布时间、Ad ID
  - （可选）帖子卡片显示状态标签为 "Live"
  - 成功提取 VIP 链接
- 在 VIP 页：
  - 显示价格 **"£50"**
  - 显示 **"Delivery from £2.59"**（Small 规格固定配送费）
  - 显示 **"Buyer Protection £3.20"**（= £50 × 5% + £0.70 = £3.20，保留两位小数）
  - 显示 **"Buy now"** 按钮，可点击
- 记录实际展示的 Small 规格配送费金额（£2.59），供后续与 Medium/Large 对比

---

**TC-PSUI-041**  
**标题**: 选择 Medium 包裹规格发布帖子，验证 VIP 页配送费高于 Small 规格  
**优先级**: P0  
**类型**: 端到端验证  

**前置条件**:
- 已以卖家账号登录
- 已进入 Men's Formal Shoes 类目帖子编辑页
- 物流开关存在
- TC-PSUI-040 已完成，已记录 Small 规格配送费

**测试步骤**:
1. 上传图片：选择工程中的 `pic/shoes.png` 文件上传
2. 填写以下信息：
   - 标题：`UI Test Shoes Medium Parcel [时间戳]`（如 `UI Test Shoes Medium 20260414_006`）
   - 描述：`Test shoes advert with medium parcel size`
   - 价格：输入 `50`
   - 地区：选择伦敦区域
3. 开启物流开关（若未自动开启）
4. 在包裹规格选项中选择 **"Medium"**
5. 记录页面上显示的配送费预估值
6. 点击 **"Post your ad"** / **"Publish"** 发布帖子
7. 若出现 Bumpup 推广页，点击 **"No thanks"** / **"Skip"** 跳过
8. 等待帖子发布成功，记录帖子 ID
9. 在 Manage My Ads 找到新发布的帖子，点击进入 VIP 页
10. 检查 VIP 页右侧交互卡片区域

**预期结果**:
- 物流开关开启后，包裹规格选项正常显示
- 选择 Medium 后，发帖页显示对应 Medium 规格的配送费预估
- Medium 规格的配送费 **≥** Small 规格配送费（£2.99 ≥ £2.59）
- 帖子成功发布，Manage My Ads 显示 "Delivery enabled" 标签
- VIP 页显示 **"Delivery from £2.99"**（Medium 规格固定配送费）
- VIP 页显示 **"Buyer Protection £3.20"**（= £50 × 5% + £0.70 = £3.20）
- VIP 页显示 **"Buy now"** 按钮
- 记录实际展示的 Medium 规格配送费金额

---

**TC-PSUI-042**  
**标题**: 选择 Large 包裹规格发布帖子，验证 VIP 页配送费高于 Medium 规格  
**优先级**: P0  
**类型**: 端到端验证  

**前置条件**:
- 已以卖家账号登录
- 已进入 Men's Formal Shoes 类目帖子编辑页
- 物流开关存在
- TC-PSUI-041 已完成，已记录 Medium 规格配送费

**测试步骤**:
1. 上传图片：选择工程中的 `pic/shoes.png` 文件上传
2. 填写以下信息：
   - 标题：`UI Test Shoes Large Parcel [时间戳]`（如 `UI Test Shoes Large 20260414_007`）
   - 描述：`Test shoes advert with large parcel size`
   - 价格：输入 `50`
   - 地区：选择伦敦区域
3. 开启物流开关（若未自动开启）
4. 在包裹规格选项中选择 **"Large"**
5. 记录页面上显示的配送费预估值
6. 点击 **"Post your ad"** / **"Publish"** 发布帖子
7. 若出现 Bumpup 推广页，点击 **"No thanks"** / **"Skip"** 跳过
8. 等待帖子发布成功，记录帖子 ID
9. 在 Manage My Ads 找到新发布的帖子，点击进入 VIP 页
10. 检查 VIP 页右侧交互卡片区域

**预期结果**:
- 物流开关开启后，包裹规格选项正常显示
- 选择 Large 后，发帖页显示对应 Large 规格的配送费预估
- Large 规格的配送费 **≥** Medium 规格配送费（£3.49 ≥ £2.99）
- 帖子成功发布，Manage My Ads 显示 "Delivery enabled" 标签
- VIP 页显示 **"Delivery from £3.49"**（Large 规格固定配送费）
- VIP 页显示 **"Buyer Protection £3.20"**（= £50 × 5% + £0.70 = £3.20）
- VIP 页显示 **"Buy now"** 按钮
- 三种规格配送费满足：Small(£2.59) ≤ Medium(£2.99) ≤ Large(£3.49)

---

### 模块六：编辑帖子 — 物流状态联动验证

---

> **说明**：本模块复用前序模块已发布的两条帖子：
> - **帖子 A**：TC-PSUI-036 发布的 £300 帖子（My Ads 无物流标签，编辑页物流开关不可用）
> - **帖子 B**：TC-PSUI-023 发布的 £70 帖子（My Ads 显示 "Eligible for delivery"，编辑页物流开关可用但已关闭）
>
> 验证：编辑页物流开关初始状态与帖子当前状态一致；修改价格后开关随价格规则联动；发布后 My Ads 和 VIP 页物流状态同步更新。

---

**TC-PSUI-050**  
**标题**: 进入 £300 帖子编辑页，验证物流开关状态与帖子当前状态一致（不可用）  
**优先级**: P0  
**类型**: 编辑页状态验证  

**前置条件**:
- TC-PSUI-036 已完成，£300 帖子已发布，My Ads 无物流标签
- 已以卖家账号登录

**测试步骤**:
1. 导航到 `https://my.unicorn.gumtree.io/manage/ads`
2. 找到标题为 `UI Test Shoes Ad £300` 的帖子卡片
3. 点击帖子编辑入口（"Edit" 按钮或"编辑"链接），进入帖子编辑页
4. 在编辑页中观察物流开关状态

**预期结果**:
- 成功进入帖子编辑页（URL 含 `/postad/{editorId}`）
- 编辑页中物流开关处于 **不可用/自动关闭** 状态（与帖子当前状态一致）
- 价格字段显示当前值 `300`
- 不显示可开启的物流选项

---

**TC-PSUI-051**  
**标题**: 编辑 £300 帖子，将价格改为 £80，验证编辑页物流开关变为可用  
**优先级**: P0  
**类型**: 编辑页价格联动验证  

**前置条件**:
- 继续 TC-PSUI-050，已在 £300 帖子编辑页中，物流开关不可用

**测试步骤**:
1. 清除价格输入框中的 `300`
2. 输入价格 `80`
3. 点击其他区域，触发价格校验
4. 观察物流开关状态变化

**预期结果**:
- 价格修改为 £80 后，物流开关 **自动变为可用状态**（£80 处于 £1–£250 支持区间）
- 物流开关可被手动开启（不再置灰/禁用）
- 若系统自动开启开关，UI 显示为激活状态

---

**TC-PSUI-052**  
**标题**: 开启物流后发布编辑后的 £80 帖子，验证 My Ads 和 VIP 页物流状态更新  
**优先级**: P0  
**类型**: 端到端验证  

**前置条件**:
- 继续 TC-PSUI-051，价格已改为 £80，物流开关已变为可用

**测试步骤**:
1. 开启物流开关（若未自动开启）
2. 确认物流开关处于开启状态后，点击 **"Update your ad"** / **"Save"** / **"Publish"** 保存帖子
3. 若出现 Bumpup 推广页，点击 **"No thanks"** / **"Skip"** 跳过
4. 等待帖子更新成功
5. 导航到 `https://www.unicorn.gumtree.io/manage/ads`（注意：是 www 域名）
6. 找到该帖子（通过标题匹配），检查帖子卡片内容
7. 从帖子卡片中提取完整的 VIP 链接
8. 点击帖子标题进入 VIP 页，检查右侧交互卡片区域

**预期结果**:
- 帖子更新成功
- 在 Manage My Ads 页面：
  - 找到更新后的帖子（标题匹配）
  - 帖子卡片显示 **"Delivery enabled"** 标签（由无标签变为有标签）
  - 帖子卡片价格更新为 **£80**
  - 帖子卡片显示基本信息：标题、地区、发布时间、Ad ID
  - （可选）帖子卡片显示状态标签为 "Live"
  - 成功提取 VIP 链接
- 在 VIP 页：
  - 显示价格 **"£80"**
  - 显示 **"Delivery from £2.59"**（编辑后未选规格默认 Small）或与编辑页所选规格匹配的配送费
  - 显示 **"Buyer Protection £4.70"**（= £80 × 5% + £0.70 = £4.70，保留两位小数）
  - 显示 "Buy now" 按钮，可点击
- 物流状态从"无"变为"已开启"，变化生效

---

**TC-PSUI-053**  
**标题**: 进入 £70 帖子编辑页，验证物流开关状态与帖子当前状态一致（可用但已关闭）  
**优先级**: P0  
**类型**: 编辑页状态验证  

**前置条件**:
- TC-PSUI-023 已完成，£70 帖子已发布（物流手动关闭），My Ads 显示 "Eligible for delivery"
- 已以卖家账号登录

**测试步骤**:
1. 导航到 `https://my.unicorn.gumtree.io/manage/ads`
2. 找到标题为 `UI Test Shoes Ad £70 No Ship` 的帖子卡片，确认显示 "Eligible for delivery" 标签
3. 点击帖子编辑入口，进入帖子编辑页
4. 在编辑页中观察物流开关状态

**预期结果**:
- 成功进入帖子编辑页
- 编辑页中物流开关处于 **可用但关闭** 状态（与帖子当前状态一致）
- 价格字段显示当前值 `70`
- 物流开关可被手动开启（非禁用，仅处于关闭态）

---

**TC-PSUI-054**  
**标题**: 编辑 £70 帖子，将价格改为 £370，验证编辑页物流开关变为不可用  
**优先级**: P0  
**类型**: 编辑页价格联动验证  

**前置条件**:
- 继续 TC-PSUI-053，已在 £70 帖子编辑页中，物流开关可用但已关闭

**测试步骤**:
1. 清除价格输入框中的 `70`
2. 输入价格 `370`
3. 点击其他区域，触发价格校验
4. 观察物流开关状态变化

**预期结果**:
- 价格修改为 £370 后，物流开关 **自动变为不可用/关闭** 状态（£370 > £250，超出支持区间）
- 开关变为置灰/禁用状态，无法手动开启
- 页面可能显示提示信息（如 "Shipping is not available for items priced over £250"）

---

**TC-PSUI-055**  
**标题**: 发布编辑后的 £370 帖子，验证 My Ads 和 VIP 页物流标签消失  
**优先级**: P0  
**类型**: 端到端验证  

**前置条件**:
- 继续 TC-PSUI-054，价格已改为 £370，物流开关已变为不可用

**测试步骤**:
1. 确认物流开关处于关闭/不可用状态
2. 点击 **"Update your ad"** / **"Save"** / **"Publish"** 保存帖子
3. 若出现 Bumpup 推广页，点击 **"No thanks"** / **"Skip"** 跳过
4. 等待帖子更新成功
5. 导航到 `https://www.unicorn.gumtree.io/manage/ads`（注意：是 www 域名）
6. 找到该帖子（通过标题匹配），检查帖子卡片内容
7. 从帖子卡片中提取完整的 VIP 链接
8. 点击帖子标题进入 VIP 页，检查右侧交互卡片区域

**预期结果**:
- 帖子更新成功
- 在 Manage My Ads 页面：
  - 找到更新后的帖子（标题匹配）
  - 帖子卡片 **不显示** "Delivery enabled" 标签
  - 帖子卡片 **不显示** "Eligible for delivery" 标签（之前的标签已消失）
  - 帖子卡片价格更新为 **£370**
  - 帖子卡片显示基本信息：标题、地区、发布时间、Ad ID
  - （可选）帖子卡片显示状态标签为 "Live"
  - 成功提取 VIP 链接
- 在 VIP 页：
  - 显示价格 **"£370"**
  - **不显示** "Delivery from £X.XX" 文字
  - **不显示** "Buyer Protection £X.XX" 文字
  - **不显示** "Buy now" 按钮
- 物流状态从 "Eligible for delivery" 变为无，变化生效

---

## 📊 测试总结

### 测试覆盖一览

| 模块 | 用例数 | 核心验证点 |
|------|--------|-----------|
| 模块一：前置依赖（工具类） | — | SessionManager 封装为 fixture/helper，不生成测试脚本 |
| 模块二：Freebies 无物流 | 3 | 不支持物流类目无开关 + 发帖后无物流标签 |
| 模块三：Shoes 有物流（£50 / £70 手动关闭） | 5 | 支持物流类目有开关 + 图片上传 + 发帖后有物流标签 + 手动关闭后显示 Eligible 标签 + VIP 组件 |
| 模块四：价格联动验证 | 8 | 价格 < £1 / £1–£250 / > £250 三段联动 + 边界值 + 超限帖发布后无物流标签 |
| 模块五：包裹规格与配送费 | 3 | Small / Medium / Large 三种规格 + VIP 页配送费递增验证 + 买家保护费展示 |
| 模块六：编辑帖子物流状态联动 | 6 | 编辑页初始状态与帖子一致 + 价格修改触发开关联动 + 发布后 My Ads / VIP 同步更新 |
| **合计（测试用例）** | **27** | 模块一为前置工具类，不纳入用例计数 |

### 关键验证矩阵

| 类目 | 价格 | 物流开关可用 | 物流开关状态 | Manage My Ads 标签 | VIP 物流组件 |
|------|------|------------|------------|-------------------|------------|
| Freebies | 任意 | ❌ 不存在 | N/A | 无标签 | 无 |
| Men's Formal Shoes | £0（< £1） | ✅ 存在 | 自动关闭 | 无标签 | 无 |
| Men's Formal Shoes | £50（£1–£250，开启物流，Small） | ✅ 存在 | 手动/自动开启 | Delivery enabled ✅ | Delivery £2.59 + Buyer Protection £3.20 |
| Men's Formal Shoes | £50（£1–£250，开启物流，Medium） | ✅ 存在 | 手动/自动开启 | Delivery enabled ✅ | Delivery £2.99 + Buyer Protection £3.20 |
| Men's Formal Shoes | £50（£1–£250，开启物流，Large） | ✅ 存在 | 手动/自动开启 | Delivery enabled ✅ | Delivery £3.49 + Buyer Protection £3.20 |
| Men's Formal Shoes | £70（£1–£250，手动关闭） | ✅ 存在 | 手动关闭 | Eligible for delivery | 无 |
| Men's Formal Shoes | £251（> £250） | ✅ 存在 | 自动关闭 | 无标签 | 无 |
| Men's Formal Shoes | £300（> £250） | ✅ 存在 | 自动关闭 | 无标签 | 无 |
| Men's Formal Shoes | £300→£80 编辑后（开启物流） | ✅ 存在 | 编辑后变为开启 | Delivery enabled ✅ | Delivery £2.59 + Buyer Protection £4.70 |
| Men's Formal Shoes | £70→£370 编辑后（超出上限） | ✅ 存在 | 编辑后变为不可用 | 无标签（由 Eligible 变为无） | 无 |

### 测试数据

```yaml
测试图片:
  Freebies 类目: test_image.jpg（工程根目录）
  Men's Formal Shoes 类目: pic/shoes.png（473×1024 px）

测试帖子标题规范:
  无物流: "UI Test Freebie Ad {timestamp}"
  有物流 £50（开启）: "UI Test Shoes Ad 50 {timestamp}"
  有物流 £70（手动关闭）: "UI Test Shoes Ad 70 NoShip {timestamp}"
  超限 £300: "UI Test Shoes Ad 300 {timestamp}"
  包裹 Small: "UI Test Shoes Small {timestamp}"
  包裹 Medium: "UI Test Shoes Medium {timestamp}"
  包裹 Large: "UI Test Shoes Large {timestamp}"

类目 ID（参考）:
  Freebies: freebies（不支持物流）
  Men's Formal Shoes: mens-formal-shoes（支持物流）
```

### 未覆盖场景（待补充）

| 场景 | 优先级 | 说明 |
|------|--------|------|
| 买家账号查看物流帖子 | P1 | 买家视角的 VIP 页 Buy now 流程 |
| 编辑帖子时修改类目触发物流开关变化 | P2 | 从支持物流类目改为不支持类目后开关是否消失 |
| ~~三种规格配送费实际金额的精确值断言~~ | ~~P2~~ | ~~已补充：Small £2.59 / Medium £2.99 / Large £3.49~~ |
| 网络异常时物流开关行为 | P3 | 边界异常场景 |

---

## 📸 临时文件说明

| 说明 | 路径 |
|------|------|
| 卖家账号 storage_state | `temp/session_storage/state_gtauto5858_outlook_com.json` |
| 买家账号 storage_state | `temp/session_storage/state_gtauto25858_outlook_com.json` |
| 测试图片 | `pic/shoes.png`（473×1024 PNG） |
| 探测截图建议目录 | `temp/payship/payship_ui_*.png` |
