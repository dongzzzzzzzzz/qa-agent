# Gumtree Pay & Ship - VIP 广告详情页测试用例

> **生成时间**: 2026-04-27  
> **测试方式**: Playwright 自动化脚本 + 手工测试  
> **测试账号**: 买家 gtauto25858@outlook.com  
> **测试站点**: https://www.unicorn.gumtree.io/  
> **页面范围**: VIP 广告详情页 (`/p/`)  
> **文档版本**: v1.0

---

## 🔧 测试环境配置

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | uk | 英国站 |
| 测试环境基础URL | https://www.unicorn.gumtree.io/ | ⚠️ **注意：是 unicorn 测试环境，非 www.gumtree.com** |
| 买家账号 | gtauto25858@outlook.com | 登录邮箱 |
| 买家密码 | autoGt5858! | 登录密码 |
| 卖家账号 | gtauto5858@outlook.com | 用于验证卖家信息 |
| 测试商品价格 | £20.00 | 小包裹配送广告 |

### 📌 测试数据占位符

| 占位符 | 含义 | 格式 | 示例 |
|--------|------|------|------|
| `{advertId}` | 广告 ID | 纯数字字符串 | `1001673677` |
| `{AD_TITLE}` | 广告标题 | 字符串 | `Ship Ad UI-Auto Autotest 20260424_153933` |
| `{ITEM_PRICE}` | 商品价格 | £xx.xx | `£20.00` |
| `{DELIVERY_FEE}` | 配送费 | £x.xx | `£2.59` |
| `{BP_FEE}` | 买家保护费 | £x.xx | `£1.70` |
| `{VIP_URL}` | VIP 页面 URL | 完整 URL | `https://www.unicorn.gumtree.io/p-item/1001673677` |

---

## 📑 目录

- [模块1：页面加载与导航](#模块1页面加载与导航)
- [模块2：商品图片区域](#模块2商品图片区域)
- [模块3：商品信息与价格](#模块3商品信息与价格)
- [模块4：卖家信息](#模块4卖家信息)
- [模块5：Message 私信按钮](#模块5message-私信按钮)
- [模块6：安全提示](#模块6安全提示)
- [模块7：商品描述与属性](#模块7商品描述与属性)
- [模块8：推荐区域](#模块8推荐区域)
- [模块9：浮动窗口](#模块9浮动窗口)
- [模块10：页面跳转与交互](#模块10页面跳转与交互)

---

## 模块1：页面加载与导航

### TC-VIP-001: VIP 页面加载-URL 和基础元素验证

#### 📋 前置条件
- 已登录买家账号（gtauto25858@outlook.com）
- 从搜索结果页或广告列表点击进入 VIP 页
- 广告已启用配送功能

#### 🎬 执行步骤
1. 通过搜索或直接访问进入 VIP 页面
2. 验证页面 URL 格式
3. 验证页面加载完成

#### ✅ 预期结果

**URL 验证：**
- ✅ URL 格式：`/p/{category}/{title}/{advertId}` 或 `/p-item/{advertId}`
- ✅ URL 包含广告 ID（纯数字）
- ✅ 页面状态码：200（正常加载）

**页面加载验证：**
- ✅ 页面标题（document.title）包含广告标题
- ✅ 无 JavaScript 错误（Console 无红色错误）
- ✅ 主要内容区域加载完成（非空白页）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/基础验证
- **UI自动化**: ✅ 已自动化（Phase 2 隐式验证）

---

### TC-VIP-002: 面包屑导航验证

#### 📋 前置条件
- 已进入 VIP 页面
- 广告属于特定类目（如：For Sale > Clothes > Men's Accessories > Backpacks）

#### 🎬 执行步骤
1. 查看页面顶部面包屑导航区域
2. 验证面包屑路径完整性
3. 点击面包屑链接验证跳转

#### ✅ 预期结果

**面包屑路径：**
- ✅ 起始节点：`Home` 或 `Gumtree`
- ✅ 二级节点：`For Sale`
- ✅ 三级节点：主类目（如 `Clothes, Footwear & Accessories`）
- ✅ 四级节点：子类目（如 `Men's Accessories`）
- ✅ 末级节点：最终类目（如 `Backpacks`）

**交互验证：**
- ✅ 每个节点都是可点击链接（除末级节点可能为纯文本）
- ✅ 点击任一节点跳转至对应类目页
- ✅ 节点之间有分隔符（如 `>` 或 `/`）

**面包屑格式示例：**
```
Home > For Sale > Clothes, Footwear & Accessories > Men's Accessories > Backpacks
```

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/导航验证
- **UI自动化**: ✅ 已自动化（Phase 2 - 1.1）

---

### TC-VIP-003: 返回搜索结果功能

#### 📋 前置条件
- 从搜索结果页进入 VIP 页
- 浏览器支持历史记录

#### 🎬 执行步骤
1. 从搜索结果页点击广告进入 VIP 页
2. 点击浏览器返回按钮
3. 验证是否返回搜索结果页

#### ✅ 预期结果

**返回功能：**
- ✅ 点击浏览器返回按钮后返回搜索结果页
- ✅ 搜索结果页保持之前的搜索关键词和结果
- ✅ 滚动位置大致保持（可选，取决于实现）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/用户体验
- **UI自动化**: ⚠️ 待自动化

---

## 模块2：商品图片区域

### TC-VIP-004: 图片展示区-基础元素验证

#### 📋 前置条件
- 已进入 VIP 页面
- 广告包含至少 1 张商品图片

#### 🎬 执行步骤
1. 查看页面左侧或中央的图片展示区域
2. 验证图片展示和控制元素

#### ✅ 预期结果

**图片展示区域：**
- ✅ 主图片显示（大尺寸预览图）
- ✅ 图片清晰可见，无加载失败图标
- ✅ 图片比例合适，无严重变形

**图片控制元素：**
- ✅ `Images` 标签/Tab（选中状态）
- ✅ `Map` 标签/Tab（未选中状态）
- ✅ 图片计数器：`1 of 1` 或 `1 of n`（显示当前图片/总图片数）
- ✅ 左右翻页箭头（< 和 >）：如有多张图片则显示
- ✅ 放大镜图标/按钮（用于全屏查看）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/UI 元素
- **UI自动化**: ✅ 已自动化（Phase 2 - 3.1-3.5）

---

### TC-VIP-005: 图片浏览-多图翻页功能

#### 📋 前置条件
- 广告包含多张图片（≥ 2 张）
- 已进入 VIP 页面

#### 🎬 执行步骤
1. 在图片展示区域找到翻页箭头
2. 点击右箭头 `>` 翻页至下一张
3. 点击左箭头 `<` 翻页至上一张
4. 观察图片计数器变化

#### ✅ 预期结果

**翻页功能：**
- ✅ 点击右箭头后主图切换至下一张
- ✅ 图片计数器更新（如 `1 of 3` → `2 of 3`）
- ✅ 点击左箭头后主图切换至上一张
- ✅ 翻页有平滑过渡动画（可选）

**边界处理：**
- ✅ 在第一张图片时，左箭头禁用或隐藏
- ✅ 在最后一张图片时，右箭头禁用或隐藏
- ✅ 或支持循环翻页（最后一张 → 第一张）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/交互
- **UI自动化**: ⚠️ 待自动化

---

### TC-VIP-006: 图片放大查看功能

#### 📋 前置条件
- 已进入 VIP 页面
- 图片展示区域有放大镜图标

#### 🎬 执行步骤
1. 点击放大镜图标或主图片
2. 查看全屏图片展示
3. 在全屏模式下翻页（如有多张图片）
4. 关闭全屏模式

#### ✅ 预期结果

**全屏模式：**
- ✅ 点击放大镜后进入全屏模式（或大图弹窗）
- ✅ 图片居中显示，背景半透明遮罩
- ✅ 图片尺寸适配屏幕，可缩放（可选）
- ✅ 显示关闭按钮（X 或 Close）
- ✅ 支持键盘 ESC 关闭
- ✅ 点击背景区域关闭（可选）

**全屏模式下翻页：**
- ✅ 如有多张图片，显示左右箭头
- ✅ 翻页功能正常，图片切换流畅
- ✅ 显示图片计数器

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/交互
- **UI自动化**: ⚠️ 待自动化

---

### TC-VIP-007: 图片与地图切换

#### 📋 前置条件
- 已进入 VIP 页面
- 广告包含地理位置信息

#### 🎬 执行步骤
1. 点击 `Map` 标签/Tab
2. 验证地图显示
3. 点击 `Images` 标签返回图片展示

#### ✅ 预期结果

**地图显示：**
- ✅ 点击 `Map` 后图片区域切换为地图（如 Google Maps）
- ✅ 地图标记显示广告位置（大致区域，非精确地址）
- ✅ 地图支持缩放、拖拽交互

**切换功能：**
- ✅ `Map` 标签高亮（选中状态）
- ✅ 点击 `Images` 标签返回图片展示
- ✅ 切换流畅，无卡顿

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/Tab 切换
- **UI自动化**: ⚠️ 待自动化

---

## 模块3：商品信息与价格

### TC-VIP-008: 商品标题与位置信息

#### 📋 前置条件
- 已进入 VIP 页面
- 广告包含标题和位置信息

#### 🎬 执行步骤
1. 查看页面顶部或中央区域
2. 验证商品标题和位置信息展示

#### ✅ 预期结果

**商品标题：**
- ✅ 标题完整显示（与发布时一致）
- ✅ 标题为 h1 或突出显示（大字号、加粗）
- ✅ 标题无截断（或截断后可展开）

**位置信息：**
- ✅ 显示发布位置：`Richmond, London` 或类似格式
- ✅ 位置信息靠近标题显示（通常在标题下方）
- ✅ 位置可能包含图标（📍 或类似）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/信息展示
- **UI自动化**: ✅ 已自动化（Phase 2 - 2.1-2.2）

---

### TC-VIP-009: 商品价格与购买按钮（支持配送广告）

#### 📋 前置条件
- 已登录买家账号
- 广告已启用配送功能
- 商品价格：£20.00

#### 🎬 执行步骤
1. 查看页面右侧价格区域
2. 验证价格、配送费、买家保护费展示
3. 验证 Buy now 按钮存在

#### ✅ 预期结果

**价格信息：**
- ✅ 商品价格显示：`£20` 或 `£20.00`（大字号、突出显示）
- ✅ 配送费信息：`Delivery from £2.59`
- ✅ 买家保护费：`Buyer Protection £1.70`
- ✅ 价格格式统一，带 £ 符号

**购买按钮：**
- ✅ 绿色 `Buy now` 按钮（主操作按钮）
- ✅ 按钮位置：价格下方或右侧固定区域
- ✅ 按钮状态：启用（非禁用/灰色）
- ✅ 按钮文字清晰：`Buy now` 或 `Buy it now`

**其他按钮（与 Buy now 并列）：**
- ✅ `Message` 按钮（私信卖家）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/核心功能
- **UI自动化**: ✅ 已自动化（Phase 2 - 4.1-4.4）

---

### TC-VIP-010: 商品价格-不支持配送广告

#### 📋 前置条件
- 广告未启用配送功能（纯面交广告）
- 已进入 VIP 页面

#### 🎬 执行步骤
1. 查看价格区域
2. 验证是否显示配送相关信息

#### ✅ 预期结果

**价格信息：**
- ✅ 商品价格正常显示
- ✅ **不显示** `Delivery from` 配送费信息
- ✅ **不显示** `Buyer Protection` 信息
- ✅ **不显示** `Buy now` 按钮

**其他按钮：**
- ✅ 显示 `Message` 按钮（主要交互方式）
- ✅ 可能显示 `Call` 按钮（如卖家提供电话）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/不同广告类型
- **UI自动化**: ⚠️ 待自动化

---

### TC-VIP-011: 价格显示-免费广告

#### 📋 前置条件
- 广告价格为 £0 或标记为免费
- 已进入 VIP 页面

#### 🎬 执行步骤
1. 查看价格区域
2. 验证免费标识展示

#### ✅ 预期结果

**免费标识：**
- ✅ 显示 `Free` 或 `£0` 或 `FREE` 标识
- ✅ 免费标识位置：价格区域（可能用特殊颜色突出）
- ✅ 如支持配送，仍显示配送费和 Buy now 按钮

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界/特殊价格
- **UI自动化**: ⚠️ 待自动化

---

## 模块4：卖家信息

### TC-VIP-012: 卖家基础信息展示

#### 📋 前置条件
- 已进入 VIP 页面
- 卖家账号：GT Auto（gtauto5858@outlook.com）

#### 🎬 执行步骤
1. 查看卖家信息区域（通常在价格区域下方或右侧）
2. 验证卖家信息完整性

#### ✅ 预期结果

**卖家信息区域：**
- ✅ 卖家头像/图标（默认头像或自定义头像）
- ✅ 卖家名称：`GT Auto` 或类似显示名
- ✅ 卖家统计信息：
  - `Posting for X years/months/days`（注册时长）
  - `X Ads in a year`（年度发帖数）
- ✅ 邮箱验证徽章：`Email address verified`（绿色勾选图标）

**卖家信息格式示例：**
```
[头像]
GT Auto
Posting for 2 years
50 Ads in a year
✓ Email address verified
```

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/信息展示
- **UI自动化**: ✅ 已自动化（Phase 2 - 5.1-5.4）

---

### TC-VIP-013: 卖家信息-点击查看卖家主页

#### 📋 前置条件
- 已进入 VIP 页面
- 卖家名称为可点击链接

#### 🎬 执行步骤
1. 点击卖家名称或头像
2. 验证是否跳转至卖家主页

#### ✅ 预期结果

**卖家主页跳转：**
- ✅ 点击卖家名称后跳转至卖家主页
- ✅ 卖家主页 URL 格式：`/profile/{sellerId}` 或类似
- ✅ 卖家主页显示该卖家的所有在售广告
- ✅ 卖家主页显示卖家评价/反馈（如有）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/跳转
- **UI自动化**: ⚠️ 待自动化

---

### TC-VIP-014: 卖家验证徽章-未验证状态

#### 📋 前置条件
- 使用未验证邮箱的卖家账号发布广告
- 已进入该广告 VIP 页面

#### 🎬 执行步骤
1. 查看卖家信息区域
2. 验证邮箱验证徽章状态

#### ✅ 预期结果

**未验证状态：**
- ✅ **不显示** `Email address verified` 徽章
- ✅ 或显示 `Email not verified`（警告样式）
- ✅ 其他卖家信息正常显示

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 负向/未验证
- **UI自动化**: ⚠️ 待自动化

---

## 模块5：Message 私信按钮

### TC-VIP-015: Message 按钮-基础展示

#### 📋 前置条件
- 已登录买家账号
- 已进入 VIP 页面

#### 🎬 执行步骤
1. 查看页面互动按钮区域（通常在卖家信息下方或价格区域）
2. 验证 Message 按钮存在

#### ✅ 预期结果

**Message 按钮：**
- ✅ `Message` 按钮存在（私信卖家功能）
- ✅ 按钮文字清晰：`Message` 或 `Message seller`
- ✅ 按钮样式：突出显示（如绿色或主色调）或边框按钮
- ✅ 按钮位置：价格区域附近或卖家信息下方

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/UI 元素
- **UI自动化**: ✅ 已自动化（Phase 2 - 6.1）

---

### TC-VIP-016: Message 按钮-发送私信

#### 📋 前置条件
- 已登录买家账号（gtauto25858@outlook.com）
- 已进入 VIP 页面
- 买家与卖家非同一账号
- 广告状态为 LIVE

#### 🎬 执行步骤
1. 在 VIP 页面找到 `Message` 按钮（通常在价格区域附近或卖家信息下方）
2. 点击 `Message` 按钮
3. 等待页面跳转至会话详情页
4. 验证会话详情页 URL 和页面元素
5. 在消息输入框中输入测试消息内容（如："Hello, is this item still available?"）
6. 点击发送按钮
7. 验证消息发送成功

#### ✅ 预期结果

**Message 按钮点击：**
- ✅ 按钮可点击（非禁用状态）
- ✅ 点击后触发导航或弹窗

**页面跳转验证：**
- ✅ 跳转到会话详情页（Conversation page）
- ✅ URL 包含 `/post-message/` 或 `/conversation/` 路径
- ✅ URL 包含广告 ID 参数：`postId={advertId}` 或 `adId={advertId}`
- ✅ 页面加载完成（无错误）

**会话详情页元素验证：**
- ✅ 页面顶部包含商品信息卡片：
  - 商品缩略图
  - 商品标题（与 VIP 页一致）
  - 商品价格（与 VIP 页一致）
- ✅ 卖家信息显示：
  - 卖家名称
  - 卖家头像（如有）
- ✅ 消息输入框存在且可编辑
- ✅ 发送按钮存在且初始状态为禁用（未输入内容时）

**消息发送验证：**
- ✅ 在输入框输入消息后，发送按钮变为可点击状态
- ✅ 点击发送按钮后：
  - 消息成功发送（无错误提示）
  - 消息显示在对话历史中
  - 消息内容与输入一致
  - 消息发送时间显示（如："Just now" 或具体时间）
- ✅ 发送后输入框自动清空
- ✅ 可以继续发送新消息

**异常情况处理：**
- ✅ 如果会话已存在，直接打开已有会话（不创建新会话）
- ✅ 网络错误时显示友好的错误提示

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/私信功能
- **UI自动化**: ⚠️ 待自动化（Phase 3 规划中）

#### 🔧 自动化参考代码

```python
# 1. 点击 Message 按钮
message_button = page.locator("button:has-text('Message')").first
message_button.click()

# 2. 等待跳转到会话详情页
page.wait_for_url("**/post-message/**", timeout=10000)
conversation_url = page.url

# 3. 验证 URL 包含广告 ID
assert f"postId={advert_id}" in conversation_url or f"adId={advert_id}" in conversation_url

# 4. 验证商品信息卡片
product_card = page.locator("[class*='product-card'], [class*='ad-card']")
assert product_card.is_visible()
assert ad_title in product_card.text_content()

# 5. 验证消息输入框和发送按钮
message_input = page.locator("textarea[placeholder*='message'], input[placeholder*='message']")
send_button = page.locator("button:has-text('Send'), button[type='submit']")

assert message_input.is_visible()
assert send_button.is_visible()
assert not send_button.is_enabled()  # 初始状态应为禁用

# 6. 输入测试消息
test_message = "Hello, is this item still available?"
message_input.fill(test_message)
page.wait_for_timeout(500)

# 7. 验证发送按钮变为可用
assert send_button.is_enabled()

# 8. 点击发送按钮
send_button.click()
page.wait_for_timeout(2000)

# 9. 验证消息显示在对话历史中
conversation_history = page.locator("[class*='message-list'], [class*='conversation']")
assert test_message in conversation_history.text_content()

# 10. 验证输入框已清空
assert message_input.input_value() == ""

# 11. 截图保存
page.screenshot(path="conversation_page_after_send.png")
```

#### 📝 测试数据

| 字段 | 值 | 说明 |
|------|-----|------|
| 测试消息1 | "Hello, is this item still available?" | 常见询问 |
| 测试消息2 | "Can you deliver to London?" | 配送相关询问 |
| 测试消息3 | "What's the condition of the item?" | 商品状态询问 |

#### ⚠️ 注意事项

1. **会话重复性**：如果买家之前已经给该卖家发过消息，点击 Message 会打开已有会话，而不是创建新会话
2. **消息长度限制**：消息输入框可能有字符数限制（通常为 1000-5000 字符）
3. **发送频率限制**：连续发送消息可能有频率限制，避免被识别为垃圾消息
4. **登录状态**：如果会话期间登录过期，发送消息可能失败或跳转到登录页
5. **测试数据清理**：测试后建议删除测试会话（如果平台支持）或使用明确标识的测试消息

---

## 模块6：安全提示

### TC-VIP-020: 安全提示区域-Stay Safe

#### 📋 前置条件
- 已进入 VIP 页面

#### 🎬 执行步骤
1. 滚动页面至安全提示区域
2. 验证安全提示内容
3. 点击翻页按钮查看更多提示（如有）

#### ✅ 预期结果

**Stay Safe 区域：**
- ✅ 区域标题：`Stay Safe` 或 `Safety tips`
- ✅ 安全提示文字：
  - `Only access Gumtree from gumtree.com`
  - 或其他安全建议文字
- ✅ `Read all safety tips` 链接（跳转至帮助页面）

**安全提示翻页：**
- ✅ 如有多条提示，显示翻页器（如 `1 of 3`）
- ✅ 左右箭头或点按钮切换提示
- ✅ 翻页器不与图片计数器冲突（位置区分）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/安全提示
- **UI自动化**: ✅ 已自动化（Phase 2 - 7.1-7.6）

---

## 模块7：商品描述与属性

### TC-VIP-021: Description 商品描述区域

#### 📋 前置条件
- 已进入 VIP 页面
- 广告包含商品描述

#### 🎬 执行步骤
1. 滚动至 Description 区域
2. 验证描述内容完整展示
3. 验证发布时间和 Ad ID

#### ✅ 预期结果

**Description 区域：**
- ✅ 区域标题：`Description`
- ✅ 商品描述文字完整展示（与发布时一致）
- ✅ 描述支持换行和段落格式
- ✅ 描述可能包含 Emoji（如发布时使用）

**元信息：**
- ✅ 发布时间：`Posted` + 时间（如 `Posted 2 hours ago`）
- ✅ Ad ID：`Ad ID: {advertId}`（纯数字）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/信息展示
- **UI自动化**: ✅ 已自动化（Phase 2 - 8.1-8.4）

---

### TC-VIP-022: Details 商品属性区域

#### 📋 前置条件
- 已进入 VIP 页面
- 广告包含商品属性（如 Condition、Colour、Brand、Material）

#### 🎬 执行步骤
1. 滚动至 Details 区域
2. 验证属性字段展示
3. 验证 "Sell one like this" 按钮

#### ✅ 预期结果

**Details 区域：**
- ✅ 区域标题：`Details`
- ✅ 商品属性字段：
  - `Condition`：New / Used / etc.
  - `Colour`：颜色值
  - `Brand`：品牌名称
  - `Material`：材质
  - 其他自定义属性

**Sell one like this 按钮：**
- ✅ 按钮文字：`Sell one like this`
- ✅ 点击后跳转至发布页面，自动填充部分字段（类目、属性）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/属性展示
- **UI自动化**: ✅ 已自动化（Phase 2 - 9.1-9.6）

---

### TC-VIP-023: Description 长文本-展开收起

#### 📋 前置条件
- 广告描述超过 300 字符（或其他截断阈值）
- 已进入 VIP 页面

#### 🎬 执行步骤
1. 查看 Description 区域
2. 验证是否默认截断显示
3. 点击 "Read more" 或展开按钮
4. 点击 "Show less" 或收起按钮

#### ✅ 预期结果

**长文本处理：**
- ✅ 描述超过阈值时，默认显示部分内容 + `...`
- ✅ 显示 `Read more` 或 `Show more` 按钮
- ✅ 点击后展开完整描述
- ✅ 展开后显示 `Show less` 按钮（可选）
- ✅ 点击 Show less 后恢复截断状态

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/长文本
- **UI自动化**: ⚠️ 待自动化

---

## 模块8：推荐区域

### TC-VIP-024: "You may also like" 推荐区域

#### 📋 前置条件
- 已进入 VIP 页面
- 系统有推荐算法数据

#### 🎬 执行步骤
1. 滚动至 "You may also like" 推荐区域
2. 验证推荐广告卡片展示
3. 点击推荐广告验证跳转

#### ✅ 预期结果

**推荐区域：**
- ✅ 区域标题：`You may also like...` 或 `Similar ads`
- ✅ 显示多个推荐广告卡片（通常 4-6 个）
- ✅ 每个卡片包含：
  - 商品缩略图
  - 商品标题
  - 价格
  - 位置信息（可选）
- ✅ `See more` 链接（跳转至更多推荐或搜索结果）

**推荐卡片交互：**
- ✅ 点击卡片后跳转至对应广告 VIP 页
- ✅ 左右滚动箭头（如卡片较多）
- ✅ 或横向滚动条（移动端常见）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/推荐功能
- **UI自动化**: ✅ 已自动化（Phase 2 - 10.1-10.4）

---

## 模块9：浮动窗口

### TC-VIP-026: 浮动窗口-滚动触发展示

#### 📋 前置条件
- 已登录买家账号
- 已进入支持配送的广告 VIP 页面
- 浏览器窗口高度正常（非全屏超高窗口）

#### 🎬 执行步骤
1. 页面加载完成后，位于顶部
2. 滚动页面至底部（触发浮动窗口）
3. 观察页面顶部是否出现浮动窗口

#### ✅ 预期结果

**浮动窗口展示：**
- ✅ 滚动至底部时，页面顶部出现浮动窗口（Sticky footer / Fixed bar）
- ✅ 浮动窗口固定在页面顶部或底部（position: fixed/sticky）
- ✅ 浮动窗口覆盖在内容之上（z-index 较高）

**浮动窗口内容：**
- ✅ 商品价格：`£20` 或 `£20.00`
- ✅ 配送费信息：`Delivery from £2.59` 或 `£2.59`
- ✅ 买家保护费：`Buyer Protection £1.70` 或 `£1.70`
- ✅ 绿色 `Buy now` 按钮

**浮动窗口样式：**
- ✅ 背景色：白色或浅色（与页面背景区分）
- ✅ 可能有阴影效果（box-shadow）
- ✅ 高度适中，不遮挡过多内容

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向/交互功能
- **UI自动化**: ✅ 已自动化（Phase 2 - 12.1-12.5）

---

### TC-VIP-027: 浮动窗口-滚动回顶部消失

#### 📋 前置条件
- 浮动窗口已触发展示
- 页面位于底部

#### 🎬 执行步骤
1. 从页面底部滚动回顶部
2. 观察浮动窗口是否消失

#### ✅ 预期结果

**浮动窗口消失：**
- ✅ 滚动回顶部后，浮动窗口自动隐藏
- ✅ 或浮动窗口始终显示（取决于产品设计）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向/交互
- **UI自动化**: ⚠️ 待自动化

---

### TC-VIP-028: 浮动窗口-响应式布局

#### 📋 前置条件
- 已触发浮动窗口展示
- 测试不同屏幕尺寸

#### 🎬 执行步骤
1. 在桌面浏览器查看浮动窗口
2. 调整浏览器窗口至移动端尺寸
3. 验证浮动窗口适配

#### ✅ 预期结果

**桌面布局：**
- ✅ 浮动窗口横向排列：价格 | 配送费 | 保护费 | Buy now
- ✅ 宽度适配页面，居中或左对齐

**移动端布局：**
- ✅ 浮动窗口紧凑排列，可能部分信息折叠
- ✅ Buy now 按钮突出显示
- ✅ 价格信息缩略展示（如只显示总价）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI/响应式
- **UI自动化**: ⚠️ 待自动化

---

## 模块10：页面跳转与交互

### TC-VIP-029: Buy now 按钮-跳转结账页（主按钮）

#### 📋 前置条件
- 已登录买家账号
- 已进入支持配送的广告 VIP 页面

#### 🎬 执行步骤
1. 找到页面右侧的 `Buy now` 按钮（主按钮，非浮动窗口）
2. 点击按钮
3. 等待页面跳转

#### ✅ 预期结果

**跳转验证：**
- ✅ 点击后页面跳转至结账页
- ✅ 结账页 URL 格式：`/create-order?advertId={advertId}` 或 `/checkout?advertId={advertId}`
- ✅ advertId 参数与当前广告 ID 一致
- ✅ 结账页正常加载，显示商品信息

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向（E2E 核心路径）
- **UI自动化**: ✅ 已自动化（Phase 3）

---

### TC-VIP-030: 浮动窗口 Buy now 按钮-跳转结账页

#### 📋 前置条件
- 已登录买家账号（gtauto25858@outlook.com）
- 已进入支持配送的广告 VIP 页面
- 浮动窗口已触发展示（滚动到页面底部）

#### 🎬 执行步骤

1. **滚动到页面底部**
   - 使用鼠标滚轮或键盘向下滚动
   - 确保页面滚动至最底部
   - 观察浮动窗口出现

2. **定位浮动窗口 Buy now 按钮**
   - 在页面顶部或底部的浮动窗口（Fixed bar）中
   - 定位 `Buy now` 按钮（通常为主色调按钮）
   - 确认按钮处于可用状态（非禁用）

3. **点击浮动窗口中的 Buy now 按钮**
   - 点击浮动窗口中的 `Buy now` 按钮（**区别于页面右侧的主 Buy now 按钮**）
   - 等待页面响应

4. **等待页面跳转**
   - 观察浏览器地址栏变化
   - 等待新页面加载完成（3-5 秒）

5. **验证结账页 URL**
   - 检查 URL 是否包含 `/create-order?advertId=` 或 `/checkout`
   - 验证 `advertId` 参数是否与当前广告 ID 一致

6. **验证结账页面内容**
   - 确认页面标题为"Checkout" 或 "Create Order"
   - 确认显示正确的商品信息（标题、价格、图片）
   - 确认显示配送选项（Home delivery / Collection）

#### ✅ 预期结果

**按钮状态验证：**
- ✅ 浮动窗口中的 Buy now 按钮可见
- ✅ 按钮处于可用状态（非禁用，可点击）
- ✅ 按钮文本为 `Buy now`
- ✅ 按钮样式为主色调（Primary button）

**页面跳转验证：**
- ✅ 点击按钮后，**页面 URL 发生变化**
- ✅ 跳转目标：结账页面（`/create-order` 或 `/checkout`）
- ✅ URL 参数：包含 `advertId=XXXXXXXX`（当前广告 ID）

**结账页内容验证：**
- ✅ 页面标题：`Checkout` 或 `Create Order`
- ✅ 商品信息卡片：
  - 商品标题与 VIP 页一致
  - 商品价格与 VIP 页一致
  - 商品图片显示正常
- ✅ 配送选项：
  - 显示 `Home delivery` 选项
  - 显示 `Collection` 选项
  - 默认选中 `Collection`（或根据产品设计）
- ✅ 价格摘要：
  - Item price: £X.XX
  - Delivery fee: £X.XX（如选择 Home delivery）
  - Buyer Protection: £X.XX
  - Total: £X.XX

**验证点（共 3 项）：**
1. ✅ **URL 跳转验证**：点击后 URL 改变，与原 VIP 页 URL 不同
2. ✅ **跳转到结账页**：新 URL 包含 `create-order` 或 `checkout` 关键字
3. ✅ **advertId 参数验证**：URL 中的 `advertId` 与当前广告 ID 一致

#### 🤖 Playwright 自动化参考

```python
# ─── 浮动窗口 Buy now 按钮跳转验证 ─────────────────────────────────────

# 1. 滚动到底部，触发浮动窗口
page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
page.wait_for_timeout(1500)  # 等待浮动窗口出现

# 2. 获取当前 VIP 页面 URL（跳转前）
original_url = page.url
print(f"[跳转前] VIP 页面 URL: {original_url}")

# 3. 定位并点击浮动窗口中的 Buy now 按钮
# 方式1: 使用 .last 获取最后一个（通常浮动窗口在页面底部）
sticky_buy_btn = page.locator("button:has-text('Buy now')").last

# 方式2: 使用 JavaScript 定位（备用方案）
if not sticky_buy_btn.is_visible():
    page.evaluate("""
        const btns = Array.from(document.querySelectorAll('button'));
        const stickyBtn = btns.find(btn => 
            btn.textContent.includes('Buy now') && 
            getComputedStyle(btn.closest('div')).position === 'fixed'
        );
        if (stickyBtn) stickyBtn.click();
    """)
else:
    sticky_buy_btn.click()

# 4. 等待页面跳转
page.wait_for_timeout(2000)
new_url = page.url
print(f"[跳转后] 结账页面 URL: {new_url}")

# 5. 验证点 1: URL 跳转验证
assert new_url != original_url, "❌ 点击后 URL 未改变"
print("✅ URL 跳转验证通过")

# 6. 验证点 2: 跳转到结账页
assert "create-order" in new_url or "checkout" in new_url, \
    f"❌ 未跳转至结账页，当前 URL: {new_url}"
print("✅ 跳转到结账页验证通过")

# 7. 验证点 3: advertId 参数验证
import re
advert_id_match = re.search(r"advertId=(\d+)", new_url)
assert advert_id_match, "❌ URL 中未找到 advertId 参数"
assert advert_id_match.group(1) == expected_advert_id, \
    f"❌ advertId 不匹配: 期望={expected_advert_id}, 实际={advert_id_match.group(1)}"
print(f"✅ advertId 参数验证通过: {advert_id_match.group(1)}")

# 8. （可选）验证结账页内容
page.wait_for_selector("h1, h2", timeout=5000)
page_content = page.content()
assert expected_title in page_content, "❌ 结账页未显示商品标题"
assert f"£{expected_price}" in page_content, "❌ 结账页未显示商品价格"
print("✅ 结账页内容验证通过")
```

#### 📝 测试数据

| 字段 | 测试数据 | 说明 |
|------|---------|------|
| **广告 ID** | `1001673931` | 测试广告的唯一标识 |
| **商品标题** | `Ship Ad UI-Auto Autotest...` | 自动创建的测试广告 |
| **商品价格** | `£50.00` | 固定价格（small 包裹） |
| **VIP 页 URL** | `/p/mens-backpacks/ship-ad.../1001673931` | 跳转前 URL |
| **结账页 URL** | `/create-order?advertId=1001673931` | 跳转后 URL |
| **浮动窗口触发** | 滚动至底部 | 触发浮动窗口的条件 |

#### ⚠️ 注意事项

1. **浮动窗口定位：**
   - 浮动窗口通常使用 `position: fixed` 或 `position: sticky`
   - 可能位于页面顶部或底部，根据设计而定
   - 使用 `.last` 获取最后一个 Buy now 按钮（更可靠）

2. **区分两个 Buy now 按钮：**
   - **主 Buy now 按钮**：页面右侧价格区域中的按钮（始终可见）
   - **浮动窗口 Buy now 按钮**：滚动后出现的浮动窗口中的按钮
   - 本用例测试的是**浮动窗口中的按钮**

3. **跳转等待时间：**
   - 点击后需等待 2-3 秒让页面完全跳转
   - 不要在 URL 变化前就开始验证
   - 使用 `page.wait_for_timeout()` 或 `page.wait_for_url()`

4. **URL 参数验证：**
   - 使用正则表达式 `r"advertId=(\d+)"` 提取 advertId
   - 确保提取到的 advertId 与当前广告 ID 一致

5. **错误处理：**
   - 如果浮动窗口未出现，检查是否滚动到底部
   - 如果按钮点击无响应，尝试使用 JavaScript 强制点击
   - 如果 URL 未变化，检查是否有 Cookie 弹窗遮挡

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向（交互验证）
- **UI自动化**: ✅ 已自动化（test_payship_vip_page.py - 模块 9: 浮动窗口 Buy now 按钮跳转）

---

### TC-VIP-031: 未登录状态-Buy now 跳转登录页

#### 📋 前置条件
- 用户未登录
- 已进入支持配送的广告 VIP 页面

#### 🎬 执行步骤
1. 点击 `Buy now` 按钮
2. 观察页面行为

#### ✅ 预期结果

**未登录跳转：**
- ✅ 点击 Buy now 后跳转至登录页 `/signin`
- ✅ 或弹出登录弹窗
- ✅ 登录成功后自动返回结账页（保留 advertId 参数）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 异常/未登录
- **UI自动化**: ⚠️ 待自动化

---

### TC-VIP-032: 卖家查看自己的广告-Buy now 隐藏

#### 📋 前置条件
- 使用卖家账号登录（发布广告的账号）
- 访问自己发布的广告 VIP 页

#### 🎬 执行步骤
1. 卖家登录后访问自己的广告
2. 查看价格区域
3. 验证 Buy now 按钮是否显示

#### ✅ 预期结果

**卖家视图：**
- ✅ **不显示** `Buy now` 按钮（卖家不能购买自己的商品）
- ✅ 价格、配送费、买家保护费仍正常显示
- ✅ Message 按钮隐藏（不能给自己发消息）
- ✅ 可能显示 `Edit` 或 `Manage ad` 按钮（卖家管理功能）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向/权限验证
- **UI自动化**: ⚠️ 待自动化

---

## 📊 用例统计

| 模块 | 用例数 | 自动化 ✅ | 待自动化 ⚠️ | P0 | P1 | P2 |
|------|--------|----------|------------|----|----|-----|
| 模块1：页面加载与导航 | 3 | 1 | 2 | 1 | 1 | 1 |
| 模块2：商品图片区域 | 4 | 1 | 3 | 1 | 2 | 1 |
| 模块3：商品信息与价格 | 4 | 1 | 3 | 1 | 1 | 2 |
| 模块4：卖家信息 | 3 | 1 | 2 | 1 | 0 | 2 |
| 模块5：Message 私信按钮 | 2 | 1 | 1 | 1 | 1 | 0 |
| 模块6：安全提示 | 1 | 1 | 0 | 0 | 1 | 0 |
| 模块7：商品描述与属性 | 3 | 2 | 1 | 1 | 1 | 1 |
| 模块8：推荐区域 | 1 | 1 | 0 | 0 | 1 | 0 |
| 模块9：浮动窗口 | 3 | 1 | 2 | 1 | 1 | 1 |
| 模块10：页面跳转与交互 | 4 | 2 | 2 | 3 | 1 | 0 |
| **合计** | **28** | **12** | **16** | **10** | **10** | **8** |

---

## 🛠️ 自动化实现参考

### 相关脚本文件
```
Phase 2 脚本（VIP 页面全量验证）:
test_cases/payship/homeDelivery_happyPath/phase2_buyer_vip.py

验证项统计（Pay & Ship 相关）:
- 搜索结果页: 8 项
- VIP 页面: 35 项（仅 Pay & Ship 核心功能）
- 浮动窗口: 5 项
- 浮动窗口跳转: 3 项
- 总计: 51 项
```

### 核心验证逻辑

#### VIP 页面元素验证（TC-VIP-008、TC-VIP-009）
```python
page_text = page.text_content("body")

# 验证标题和位置
assert title in page_text, f"❌ VIP 页未找到帖子标题: {title}"
assert "Richmond, London" in page_text, "❌ 未找到地点信息"

# 验证价格和配送费
price_number = price.replace("£", "").rstrip("0").rstrip(".")
assert f"£{price_number}" in page_text, f"❌ 商品价格不存在"

delivery_match = re.search(r"Delivery from £([\d.]+)", page_text)
assert delivery_match, "❌ 'Delivery from £x.xx' 不存在"

bp_match = re.search(r"Buyer [Pp]rotection £([\d.]+)", page_text)
assert bp_match, "❌ 'Buyer Protection £x.xx' 不存在"

# 验证 Buy now 按钮
buy_now = page.locator("button:has-text('Buy now'), a:has-text('Buy now')")
assert buy_now.count() > 0, "❌ 'Buy now' 按钮不存在"
```

#### 浮动窗口验证（TC-VIP-026）
```python
# 滚动到底部触发浮动窗口
page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
page.wait_for_timeout(1500)

# 检查浮动窗口是否出现
sticky_footer = page.locator(
    "[class*='sticky'], [class*='fixed'], [class*='floating'],"
    "[style*='position: fixed'], [style*='position: sticky']"
).filter(has_text="Buy now")

if sticky_footer.count() > 0:
    # 验证浮动窗口内容
    sticky_text = sticky_footer.text_content()
    assert "£20" in sticky_text, "❌ 浮动窗口未显示价格"
    assert "2.59" in sticky_text, "❌ 浮动窗口未显示配送费"
    assert "1.70" in sticky_text, "❌ 浮动窗口未显示买家保护费"
```

#### 浮动窗口跳转验证（TC-VIP-030）
```python
# 点击浮动窗口中的 Buy now 按钮
sticky_buy_btn = page.locator(
    "[class*='sticky'] button:has-text('Buy now'),"
    "[class*='fixed'] button:has-text('Buy now')"
).first

current_url = page.url
sticky_buy_btn.click()
page.wait_for_load_state("domcontentloaded", timeout=10000)
new_url = page.url

# 验证跳转
assert new_url != current_url, "❌ URL 未改变"
assert ("create-order" in new_url or "checkout" in new_url), "❌ 未跳转到结账页"

# 验证 advertId 参数
advert_id_match = re.search(r"advertId=(\d+)", new_url)
assert advert_id_match.group(1) == advert_id, "❌ advertId 不匹配"
```

---

## 📝 附录

### VIP 页面元素定位器参考

```python
# 面包屑导航
breadcrumb = page.locator("[class*='breadcrumb'], nav[aria-label='Breadcrumb']")

# 商品标题
title = page.locator("h1")

# 商品图片
main_image = page.locator("[class*='gallery'] img, [class*='carousel'] img").first
image_counter = page.locator("text=/\\d+ of \\d+/")
next_arrow = page.locator("button[aria-label*='ext'], [class*='arrow-right']")
prev_arrow = page.locator("button[aria-label*='rev'], [class*='arrow-left']")

# 价格区域
price = page.locator("[class*='price'], [data-testid='price']")
delivery_fee = page.locator("text=/Delivery from £[\\d.]+/")
buyer_protection = page.locator("text=/Buyer Protection £[\\d.]+/")
buy_now_button = page.locator("button:has-text('Buy now'), a:has-text('Buy now')")

# 卖家信息
seller_name = page.locator("[class*='seller-name'], [data-testid='seller-name']")
seller_verified = page.locator("text='Email address verified'")

# Message 按钮
message_button = page.locator("button:has-text('Message'), a:has-text('Message')")

# 描述区域
description = page.locator("[class*='description'], [data-testid='description']")
ad_id = page.locator("text=/Ad ID:?\\s*\\d+/")

# 属性区域
details = page.locator("[class*='details'], [data-testid='details']")

# 浮动窗口
sticky_footer = page.locator(
    "[class*='sticky'], [class*='fixed'], [style*='position: fixed']"
).filter(has_text="Buy now")
```

### VIP 页面验证点清单（51 项）

#### 搜索结果页验证（8 项）
- [ ] S.1 帖子图片缩略图
- [ ] S.2 图片计数角标
- [ ] S.3 帖子标题匹配
- [ ] S.4 收藏按钮存在
- [ ] S.5 描述片段匹配
- [ ] S.6 地点信息匹配
- [ ] S.7 价格匹配
- [ ] S.8 "Delivery available" 标签

#### VIP 页面验证（35 项）

**一、面包屑导航（1 项）**
- [ ] 1.1 面包屑路径完整

**二、帖子标题与位置（2 项）**
- [ ] 2.1 帖子标题
- [ ] 2.2 帖子地点

**三、图片展示区（5 项）**
- [ ] 3.1 "Images" 标签
- [ ] 3.2 "Map" 标签
- [ ] 3.3 左右翻页箭头
- [ ] 3.4 图片计数器
- [ ] 3.5 放大镜图标

**四、价格与购买区（4 项）**
- [ ] 4.1 商品价格
- [ ] 4.2 配送费
- [ ] 4.3 买家保护费
- [ ] 4.4 "Buy now" 按钮

**五、卖家信息区（4 项）**
- [ ] 5.1 卖家头像
- [ ] 5.2 卖家名称
- [ ] 5.3 卖家统计
- [ ] 5.4 邮箱验证徽章

**六、Message 按钮区（1 项）**
- [ ] 6.1 "Message" 按钮

**七、安全提示区（4 项）**
- [ ] 7.3 "Stay Safe" 区域
- [ ] 7.4 安全提示文字
- [ ] 7.5 "Read all safety tips" 链接
- [ ] 7.6 安全提示翻页

**八、Description 帖子描述区（4 项）**
- [ ] 8.1 "Description" 标题
- [ ] 8.2 帖子描述内容
- [ ] 8.3 发布时间
- [ ] 8.4 帖子 Ad ID

**九、Details 帖子属性区（6 项）**
- [ ] 9.1 "Details" 标题
- [ ] 9.2 "Sell one like this" 按钮
- [ ] 9.3 Condition 属性
- [ ] 9.4 Colour 属性
- [ ] 9.5 Brand 属性
- [ ] 9.6 Material 属性

**十、推荐区（4 项）**
- [ ] 10.1 "You may also like..." 标题
- [ ] 10.2 "See more" 链接
- [ ] 10.3 推荐帖子卡片
- [ ] 10.4 左右滚动箭头

#### 浮动窗口验证（5 项）
- [ ] 12.1 浮动窗口存在
- [ ] 12.2 浮动窗口中的商品价格
- [ ] 12.3 浮动窗口中的配送费
- [ ] 12.4 浮动窗口中的买家保护费
- [ ] 12.5 浮动窗口中的 Buy now 按钮

#### 浮动窗口跳转验证（3 项）
- [ ] 13.1 浮动窗口 Buy now 按钮点击
- [ ] 13.2 URL 跳转到结账页
- [ ] 13.3 结账页 advertId 参数验证

---

**文档生成时间**: 2026-04-27  
**文档版本**: v1.0  
**关联文档**: `TC_PayShip_HomeDelivery_HappyPath.md`  
**关联脚本**: `test_cases/payship/homeDelivery_happyPath/phase2_buyer_vip.py`
