# Gumtree 消息中心（Messages）测试用例文档

> **生成时间**: 2026-04-15
> **文档依据**: `test_cases/messages/` 目录下已实现的自动化脚本（实际代码梳理）
> **测试环境**: unicorn.gumtree.io（Staging）
> **总用例数**: 60 条（含子用例）
> **测试框架**: Playwright Python + pytest + Allure

---

## 测试账号配置

| 字段 | 值 |
|------|-----|
| 站点 | UK Staging (unicorn) |
| 基础 URL | https://www.unicorn.gumtree.io |
| Buyer 账号 | liulingfeng.100@gmail.com |
| Seller 账号 | liulingfeng.20@gmail.com |
| 公共密码 | Dameinv_10# |

---

## 模块索引

| 模块 | 测试文件 | 用例 |
|------|----------|------|
| [一、核心流程 - Buyer 视角](#一核心流程---buyer-视角) | `test_messages_core.py` | TC001, TC002, TC003, TC039 |
| [二、核心流程 - Seller 视角](#二核心流程---seller-视角) | `test_messages_core.py` | TC004-TC015 |
| [三、消息发送功能](#三消息发送功能) | `test_messages_core.py` | TC005, TC006, TC007, TC038, TC043, TC045 |
| [四、媒体上传](#四媒体上传) | `test_messages_core.py` | TC041a-f, TC042a-c |
| [五、评价提示](#五评价提示) | `test_messages_core.py` | TC044 |
| [六、双方视角](#六双方视角) | `test_messages_core.py` | TC035, TC036 |
| [七、未读消息](#七未读消息) | `test_messages_unread.py` | TC008b-d, TC008f, TC008g |
| [八、分页功能](#八分页功能) | `test_pagination_list_scroll.py`, `test_pagination_simple.py` | TC011, TC011b-d |
| [九、More Options 菜单](#九more-options-菜单) | `test_messages_more_options.py` | TC016-TC023 |
| [十、Delete Conversation](#十delete-conversation) | `test_messages_more_options.py` | TC017, TC018, TC018b |
| [十一、Block 用户](#十一block-用户) | `test_messages_more_options.py` | TC019, TC020, TC040 |
| [十二、Report 用户](#十二report-用户) | `test_messages_more_options.py` | TC021, TC021b, TC022, TC023 |
| [十三、Make an Offer](#十三make-an-offer) | `test_messages_make_offer.py` | TC024, TC024b, TC025, TC025b, TC026, TC027, TC027b, TC028, TC028b, TC044-Offer |
| [十四、权限与认证](#十四权限与认证) | `test_messages_core.py` | TC002, TC013 |

---

## 一、核心流程 - Buyer 视角

**测试类**: `TestBuyerComprehensiveWorkflow`  
**文件**: `test_messages_core.py`  
**优化**: 一次登录串行执行 TC001 + TC003 + TC039

---

### TC001: Buyer 从广告详情页发起新会话

| 项目 | 内容 |
|------|------|
| **优先级** | P0 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC001` |
| **测试类** | `TestBuyerComprehensiveWorkflow` |

**前置条件**
- Buyer 登录（liulingfeng.100@gmail.com）
- Seller 有可用的活跃广告（通过 `_ensure_seller_ad_exists()` 确保）

**测试步骤**
1. Buyer 登录，调用 `_ensure_seller_ad_exists()` 获取 Seller 广告 URL
2. 访问广告详情页（VIP 页）
3. 调用 `AdDetailPage.send_listing_message()` 发送消息
4. 验证跳转到消息中心（`AdDetailPage.expect_navigated_to_messages_thread()`）

**预期结果**
- 发送成功后页面跳转至 `/manage/messages`
- 会话出现在 Buyer 的消息列表顶部

**注意**
- 若广告 URL 包含 `adRemoved=true` 则跳过（`pytest.skip`）

---

### TC003: 重复联系同一广告应跳转到已有会话

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC003` |

**前置条件**
- Buyer 已通过 TC001 建立了一条会话

**测试步骤**
1. 再次访问同一广告详情页
2. 点击 Message 按钮（`get_by_role("button", name="Message")`）
3. 验证跳转到消息中心

**预期结果**
- 不创建新会话
- URL 包含 `/manage/messages`

---

### TC039: Buyer 只能看到自己的会话（数据隔离）

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC039` |

**测试步骤**
1. Buyer 打开消息中心 `/manage/messages`
2. 调用 `inbox.expect_conversation_list_visible()`
3. 统计会话条数

**预期结果**
- 会话列表可见
- Buyer 看到的均为自己参与的会话（数量有限，符合隔离预期）

---

## 二、核心流程 - Seller 视角

**测试类**: `TestSellerComprehensiveWorkflow`  
**文件**: `test_messages_core.py`  
**优化**: 一次 Seller 登录串行执行 TC004~TC045 全部 Seller 视角测试点

---

### TC004: Seller 查看会话列表

| 项目 | 内容 |
|------|------|
| **优先级** | P0 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC004` |

**测试步骤**
1. Seller 登录
2. 打开 `/manage/messages`
3. 调用 `inbox.expect_conversation_list_visible()`

**预期结果**
- 会话列表正常显示

---

### TC008: 会话列表可见性验证

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC008` |

**测试步骤**
1. Seller 登录后调用 `inbox.expect_conversation_list_visible()`

**预期结果**
- 会话列表可见

---

### TC009: AD DELETED 角标检测

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC009` |

**测试步骤**
1. 在会话列表中查找 `"AD DELETED"` 文本元素

**预期结果**
- 若广告已删除，角标存在且可见（软断言，不强制失败）

---

### TC010: AD EXPIRED 角标检测

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC010` |

**测试步骤**
1. 在会话列表中查找 `"AD EXPIRED"` 文本元素

**预期结果**
- 若广告已过期，角标存在且可见（软断言）

---

### TC011: 切换到另一个会话

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC011` |

**前置条件**
- 账号至少有 2 条会话

**测试步骤**
1. 获取所有 `a[href*='conversationId']` 元素
2. 点击第二个会话

**预期结果**
- 成功切换到第二个会话（若会话数不足则警告）

---

### TC012: 刷新页面后会话持久化

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC012` |

**测试步骤**
1. 当前在消息中心某个会话页面
2. 调用 `page.reload()`
3. 验证 URL 仍包含 `/manage/messages`

**预期结果**
- 刷新后仍停留在消息中心
- 会话数据未丢失

---

### TC014: 广告信息卡显示

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC014` |

**测试步骤**
1. 打开一个会话
2. 查找广告信息卡（`[data-testid='ad-card']` 或含 `£` 的元素）

**预期结果**
- 广告信息卡在会话面板中可见（软断言）

---

### TC015: 广告信息卡点击跳转

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC015` |

**测试步骤**
1. 找到广告信息卡并点击
2. 验证页面 URL 包含 `/p/`（广告详情页）
3. 返回消息中心

**预期结果**
- 成功跳转到广告详情页（软断言）

---

## 三、消息发送功能

### TC005: Seller 发送回复消息

| 项目 | 内容 |
|------|------|
| **优先级** | P0 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC005` |

**测试步骤**
1. Seller 打开与 Buyer 的会话
2. 调用 `inbox.type_reply(reply)` 输入消息
3. 调用 `inbox.click_send()`
4. 调用 `inbox.expect_chat_contains(reply)`

**预期结果**
- 消息发送成功并在聊天区域显示

---

### TC006: 空输入框时发送按钮为 disabled

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC006` |

**测试步骤**
1. 确保输入框为空（无内容）
2. 调用 `inbox.expect_send_disabled()`

**预期结果**
- 发送按钮处于 disabled 状态

---

### TC007: 发送普通文本消息

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC007` |

**测试步骤**
1. 输入消息文本（含时间戳确保唯一）
2. 点击 Send
3. 验证消息出现在聊天区

**预期结果**
- 消息成功发送并显示

---

### TC038: Enter 键发送消息

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC038` |

**测试步骤**
1. 在输入框中输入消息
2. 调用 `page.keyboard.press("Enter")`
3. 验证消息出现在聊天区

**预期结果**
- Enter 键触发发送，消息成功显示

---

### TC043: 发送超长消息（1000 字符）

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC043` |

**测试步骤**
1. 构造 1000 字符的消息（`"A" * 1000`）
2. 发送
3. 验证消息区域包含 `"AAAA"`

**预期结果**
- 长消息成功发送（或被系统截断，均软断言）

---

### TC045: 纯空白消息不能发送

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC045` |

**测试步骤**
1. 在输入框中填入纯空格 `"   "`
2. 检查 Send 按钮是否 enabled

**预期结果**
- 发送按钮应为 disabled（软断言，若非 disabled 则警告）

---

## 四、媒体上传

所有媒体上传用例在 `TestSellerComprehensiveWorkflow` 内串行执行。  
测试图片路径：`test_data/images/test_image_Nmb.jpg`  
测试视频路径：`test_data/videos/test_video_N.mp4`

---

### TC041: 单张图片上传

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC041` |

**测试步骤**
1. 查找图片上传按钮（`[data-testid='image-upload']` 或 `input[type='file'][accept*='image']`）
2. 使用 `page.expect_file_chooser()` 选择 1MB 测试图片
3. 等待上传完成，点击 Send

**预期结果**
- 图片上传后发送按钮变为 enabled
- 点击 Send 后发送成功（软断言）

---

### TC041b: 图片 + 文字同时发送

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC041b` |

**测试步骤**
1. 上传一张图片
2. 在 `message-field` 文本框中输入文字
3. 点击 Send

**预期结果**
- 图片 + 文字混合消息发送成功（软断言）

---

### TC041c: 超大图片上传（> 10MB）

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC041c` |
| **测试数据** | `test_data/images/large_image_15mb.jpg` |

**测试步骤**
1. 上传 15MB 图片
2. 等待 5s 后检查是否出现错误提示（`file.*too.*large` 等）

**预期结果**
- 显示文件过大错误提示，**或**系统压缩后允许发送（两种均记录，软断言）

---

### TC041d: 逐个批量上传多张图片（3 张）

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC041d` |

**测试步骤**
1. 依次上传 3 张图片（每次调用 file chooser）
2. 等待缩略图出现（`img[src*='blob:']` 等）
3. 点击 Send

**预期结果**
- 3 张图片累积后发送按钮 enabled
- 发送成功（若按钮未 enabled 则截图并警告）

---

### TC041e: 一次性批量上传 5 张图片

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC041e` |
| **测试数据** | 需要 `test_data/images/test_image_1.jpg` ~ `test_image_5.jpg` |

**测试步骤**
1. 检查 input 是否有 `multiple` 属性
2. 通过 `file_chooser.set_files([5个路径])` 一次选择 5 张图片
3. 等待 8s 后检查发送按钮状态

**预期结果**
- 5 张图片批量上传成功（发送按钮 enabled），软断言

---

### TC041f: 上传 10 张图片验证最多 5 张限制

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC041f` |
| **测试数据** | 需要 `test_data/images/test_image_1.jpg` ~ `test_image_10.jpg` |

**测试步骤**
1. 监听 `dialog` 事件捕获 JavaScript alert
2. 一次性选择 10 张图片上传
3. 检查是否弹出 "最多5张" 提示 **或** 缩略图数 ≤ 5

**预期结果**
- 系统弹出 alert 提示限制（alert 消息包含 "5" 和 "image"），**或** 缩略图数量被限制在 ≤ 5 张

---

### TC042: 单个视频上传

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC042` |
| **测试数据** | `test_data/videos/test_video_2.mp4`（或 `test_video_5mb.mp4`） |

**测试步骤**
1. 找到视频上传 input（`input[type='file'][accept*='video']`）
2. 上传视频文件
3. 等待 5s 后点击 Send

**预期结果**
- 视频上传后发送成功（系统限制 5MB，软断言）

---

### TC042b: 多个视频上传

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC042b` |
| **测试数据** | `test_data/videos/test_video_1.mp4`, `test_video_2.mp4`, `test_video_3.mp4` |

**测试步骤**
1. 选择 2-3 个视频文件同时上传
2. 等待 10s

**预期结果**
- 多视频发送成功（软断言）

---

### TC042c: 视频 + 文字同时发送

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC042c` |
| **测试数据** | `test_data/videos/test_video_5mb.mp4` |

**测试步骤**
1. 上传视频
2. 在 `message-field` 中输入文字
3. 点击 Send

**预期结果**
- 视频 + 文字混合消息发送成功（软断言）

---

## 五、评价提示

### TC044: 发送 5 条消息后验证评价提示

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC044` |

**测试步骤**
1. 在同一会话中连续发送 5 条消息
2. 等待 3s 后检查是否出现评价提示弹窗（`Rate experience if you've bought`）
3. 若出现，验证 "Haven't bought" 和 "Leave a review" 按钮可见
4. 点击 "Haven't bought" 关闭提示

**预期结果**
- 若在买家视角且满足条件，评价提示弹窗出现
- Seller 视角通常不触发（软断言，记录日志）

---

## 六、双方视角

**测试类**: `TestDualPerspective`  
**文件**: `test_messages_core.py`

---

### TC035: Seller 立即看到 Buyer 发送的新会话

| 项目 | 内容 |
|------|------|
| **优先级** | P0 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC035` |

**测试步骤**
1. **Buyer 登录** → 访问广告详情页 → 发送消息（`AdDetailPage.send_listing_message()`）
2. 清空 cookies，**Seller 登录**
3. 打开消息中心
4. 验证会话列表可见，并统计会话数量

**预期结果**
- Seller 能在消息列表中看到来自 Buyer 的会话

---

### TC036: 点击联系人名称跳转到个人资料页

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC036` |

**测试步骤**
1. Seller 登录，打开会话
2. 点击联系人名称链接
3. 验证 URL 包含 `/profile/` 或 `/user/`

**预期结果**
- 成功跳转到对方个人资料页（软断言）

---

## 七、未读消息

**文件**: `test_messages_unread.py`

---

### TC008b: 顶部统计信息验证（X Conversations, Y unread）

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC008b` |
| **测试类** | `TestUnreadMessagesComprehensiveWorkflow` + `TestUnreadStatistics`（独立） |

**测试步骤**
1. 登录（Seller 综合工作流中 / Buyer 独立测试中）
2. 打开消息中心
3. 检查页面是否显示 `\d+ Conversation` 格式的文本
4. 若有未读：验证列表头未读数 = 顶栏 Messages 徽章未读数（`_parse_messages_header_unread()` vs `_parse_global_nav_messages_unread()`）

**预期结果**
- 页面顶部显示会话总数
- 若有未读，两处数字一致（`assert header_u == nav_u`）

---

### TC008c: 阅读消息后未读计数实时更新

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC008c` |

**前置条件**
- 有未读消息的会话存在

**测试步骤**
1. 记录点击前的列表头未读数 `initial_unread_count`
2. 点击含未读徽章的会话
3. 等待 2s 后重新读取未读数

**预期结果**
- 更新后未读数 `< initial_unread_count`（软断言）

---

### TC008d: 首条广告消息未读计数不变（场景 A）

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC008d` |
| **测试类** | `TestUnreadCountRealTimeUpdate` |

**测试步骤**
1. **Seller 登录** → 记录当前未读（列表头 `h0`，顶栏 `n0`）
2. **Buyer 登录** → 调用 `_buyer_send_three_messages_on_ad(page, ad_first)` 向 Seller 的第一条广告发 3 条消息
3. **Seller 重新登录** → 打开消息中心 → 读取新未读（`ha`, `na`）
4. 断言 `ha == h0` 且 `na == n0`（首位会话不增加未读）

**预期结果**
- 对同一首位会话连续发消息，Seller 侧总未读保持不变
- 列表头与顶栏未读一致

> **注意**: 场景 B（两帖各再发3条后未读增加）已注释，待产品确认后恢复。

---

### TC008f: 绿色未读徽章样式验证

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC008f` |

**前置条件**
- 有未读消息（未读数 > 0）

**测试步骤**
1. 找到未读徽章元素（通过 `[class*='badge']` 或纯数字文本）
2. 用 JS 获取 `backgroundColor` 和 `borderRadius`

**预期结果**
- `backgroundColor` 包含绿色值（`rgb(92, 241, 0)` 类似，含 "92" 或 "241"）
- `borderRadius >= 10px`（圆形徽章）

---

### TC008g: 未读徽章位置验证

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC008g` |

**测试步骤**
1. 找到未读徽章元素
2. 验证徽章文本为纯数字（`badge_text.isdigit()`）
3. 通过 `ancestor::*[contains(@href, 'conversationId')]` 定位到徽章所属的会话容器

**预期结果**
- 徽章为纯数字
- 徽章位于对应会话行内（软断言）

---

## 八、分页功能

### TC011b/c/d: 左侧列表独立滚动分页

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC011b` / `TC011c` / `TC011d` |
| **测试类** | `TestPaginationListScroll` |
| **文件** | `test_pagination_list_scroll.py` |

**业务说明**
- 左侧会话列表是**独立滚动容器**
- 第一页默认最多显示 30 个会话
- 只有滚动左侧列表容器才会触发懒加载翻页

**TC011b 测试步骤**
1. Seller 登录，打开消息中心
2. 调用 `inbox.get_visible_conversation_count()` 和 `inbox.get_conversation_count_from_header()`
3. 断言 `first_page_count <= 30`
4. 断言标题数字与可见数一致（允许误差 ≤ 2）

**TC011c 测试步骤**
1. 调用 `inbox.scroll_conversation_list_container(scroll_to_bottom=True)` 最多 5 轮
2. 每轮等待 3s 后检查会话数是否增加
3. 若增加：验证标题数字也同步增加，且与可见数一致
4. 若未增加：验证标题数字保持不变（已全部加载）
5. 调用 `assert_inbox_unread_consistency(page)` 验证未读数一致性

**TC011d 测试步骤**
1. 调用 `inbox.scroll_conversation_list_container(scroll_to_bottom=False)` 回顶
2. 验证第一个会话仍然可见

**预期结果**
- TC011b：第一页 ≤ 30 条，标题与实际一致
- TC011c：滚动后有新会话加载（若超过30条），标题同步更新；未读数三端一致
- TC011d：滚动回顶后首条可见

---

### 分页 - 浏览器滚动不触发列表翻页

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **测试类** | `TestPaginationSimple` |
| **文件** | `test_pagination_simple.py` |

**业务说明**
- 浏览器整体页面滚动（`window.scrollTo`）**不会**触发会话列表翻页

**测试步骤**
1. 记录初始会话数和标题数字
2. 执行 `page.evaluate("window.scrollTo(0, document.body.scrollHeight)")`
3. 验证会话数和标题数字均未变化
4. 重复滚动到顶 → 底，再次验证

**预期结果**
- 浏览器滚动前后会话数保持不变（`assert after_scroll_visible == first_page_visible`）

---

## 九、More Options 菜单

**测试类**: `TestMoreOptionsComprehensiveWorkflow`  
**文件**: `test_messages_more_options.py`  
**优化**: 一次 Seller 登录串行执行 TC016 + TC019 + TC021 + TC022 + TC023

---

### TC016: More Options 菜单展开与选项验证

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC016` |

**测试步骤**
1. Seller 打开一个会话
2. 点击 More options 按钮（`get_by_role("button", name="More options")`）
3. 验证菜单包含：`Delete conversation`、`Block`、`Report` 三个选项

**预期结果**
- 菜单展开，三个选项均可见

---

## 十、Delete Conversation

### TC017: Delete Conversation - 点击 Cancel 取消删除

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC017` |
| **测试类** | `TestDeleteConversation` |

**测试步骤**
1. Seller 打开会话 → More options → Delete conversation
2. 在确认弹窗中点击 **Cancel**
3. 验证会话仍在列表中（`get_by_role("link").filter(has_text=target_name)`）

**预期结果**
- 取消后会话仍保留，`expect(conv_link).to_be_visible()`

---

### TC018 + TC018b: Delete Conversation - 确认删除及单边删除验证

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC018` / `TC018b` |
| **测试类** | `TestDeleteConversation` |

**测试步骤**
1. **数据准备**：Seller 调用 `_create_test_ad()` 创建测试广告；Buyer 发消息建立会话
2. **Seller 侧删除**：More options → Delete conversation → 确认删除（点击 **Delete**）
3. **TC018**：Seller 重新打开消息中心，通过 JS 获取所有 conversationId，断言被删除的 ID 不在列表中
4. **TC018b**：切换到 Buyer，验证 Buyer 的会话列表仍存在（单边删除）

**预期结果**
- TC018：Seller 侧会话消失（`assert conversation_id not in remaining_ids`）
- TC018b：Buyer 侧会话仍存在（`assert len(buyer_names) > 0`）

---

## 十一、Block 用户

### TC019: Block 弹窗内容验证

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC019` |

**测试步骤**
1. More options → Block
2. 验证弹窗（`[data-testid='dialog-content']`）包含 **Block** 和 **Cancel** 按钮
3. 点击 Cancel 关闭

**预期结果**
- Block 弹窗中 Block 和 Cancel 按钮均可见

---

### TC020: Block 用户 - 取消不执行操作

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC020` |
| **测试类** | `TestBlockUser` |

**测试步骤**
1. More options → Block → 点击 **Cancel**
2. 验证会话链接仍然可见（用户未被拉黑）

**预期结果**
- 取消后输入框仍可用，会话未受影响

---

### TC040: 被拉黑用户发消息前端正常但不送达

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC040` |
| **测试类** | `TestBlockedUserMessage` |

**测试步骤**
1. 动态获取 Seller 和 Buyer 的用户 ID（通过 JS 从页面读取）
2. **Seller 通过 API 拉黑 Buyer**：`POST /bff-api/message-centre/users/block`
3. **Buyer 登录** → 打开与 Seller 的会话 → 发送消息
4. Buyer 侧验证消息显示发送成功（`inbox.expect_chat_contains(test_message)`）
5. **Seller 登录** → 验证消息中心页面 body 中**不包含**被拉黑用户的消息内容
6. **清理**：Seller 通过 API 取消拉黑（`POST /bff-api/message-centre/users/unblock`）

**预期结果**
- Buyer 侧显示发送成功
- Seller 侧未收到被拉黑用户的消息（`assert test_message not in page_text`）

---

## 十二、Report 用户

### TC021: Report 弹窗包含 8 个举报原因（首次举报）

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC021` |
| **测试类** | `TestReportUser` |

**测试步骤**
1. More options → Report
2. 检查是否是 "Conversation reported" 状态（已举报过则跳过）
3. 验证 8 个举报原因存在：
   - Fraud/Scam、Abuse/Harassment、Adult/Inappropriate、Phishing Attempt
   - Spam、Policy Violation、No Reply、No show

**预期结果**
- 首次举报：弹窗中至少 6 个举报原因可见（`assert len(visible_reasons) >= 6`）
- 已举报：弹窗显示 "Conversation reported"（`pytest.skip`）

---

### TC021b: 重复举报显示 "Conversation reported" 确认信息

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC021b` |

**测试步骤**
1. More options → Report（已举报过的会话）
2. 验证弹窗显示 "Conversation reported" 标题
3. 验证弹窗内容包含 "reported"

**预期结果**
- 重复举报弹窗正确显示已举报确认信息

---

### TC022: Report - 未选原因直接提交（已知缺陷 BUG-001）

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC022` `@pytest.mark.known_bug` |

**测试步骤**
1. 打开 Report 弹窗
2. 不选择任何原因
3. 检查 Submit 按钮是否为 disabled

**预期结果**
- **期望**：Submit 按钮为 disabled（未选原因不可提交）
- **实际/已知缺陷 BUG-001**：Submit 按钮可能处于 enabled 状态（软断言，仅记录警告）

---

### TC023: Report - 选择原因提交成功

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC023` |

**测试步骤（首次举报路径）**
1. 打开 Report 弹窗
2. 点击 "Spam" 原因按钮
3. 点击 Submit
4. 验证确认弹窗标题 `"Thanks. The conversation has been reported to Gumtree"`
5. 验证正文 `"Your feedback helps us build a safer community for buyers and sellers."`
6. 点击 Close 关闭

**测试步骤（已举报路径）**
1. 打开 Report 弹窗
2. 验证 "Conversation reported" 弹窗内容
3. 验证 `"Your conversation has been submitted to Gumtree for review."`
4. 点击 Cancel 关闭

**预期结果**
- 首次举报路径：提交成功，确认弹窗内容完整，弹窗可关闭
- 已举报路径：正确显示已举报状态

---

## 十三、Make an Offer

**文件**: `test_messages_make_offer.py`

---

### TC024: Make offer 按钮在广告详情页显示

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC024` |
| **测试类** | `TestMakeOfferAdDetail` |

**前置条件**
- For Sale 类目的活跃广告存在（`_ensure_seller_ad_exists()`）

**测试步骤**
1. Buyer 登录
2. 访问广告详情页
3. 查找 `Contact Seller` 或 `Message` 按钮（For Sale 类目）
4. 查找 `Make offer` 按钮

**预期结果**
- Contact Seller / Message 按钮可见
- Make offer 按钮可见（`expect(make_offer_btn).to_be_visible(timeout=5000)`）

---

### TC024b: 正向条件下 Make an Offer 入口可见

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC024b` |
| **测试类** | `TestMakeOfferAdDetail` |

**前置条件**
- Seller 的 For Sale 类目广告（Baby Skincare）：标题关键词 `"Test Ad FOR-SALE Baby Skincare"`
- 非 Pro Buyer 账号

**测试步骤**
1. Seller 登录，调用 `_create_test_ad()` 查找/创建 For Sale 广告
2. Buyer 登录，访问该广告
3. 验证 Make an Offer 入口可见

**预期结果**
- `expect(make_offer_btn).to_be_visible(timeout=5000)` 通过

---

### TC025b: Seller 查看自己的广告不显示 Make offer

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC025b` |
| **测试类** | `TestMakeOfferBusinessRules` |

**测试步骤**
1. Seller 登录，访问自己的 For Sale 广告
2. 检查 Make offer 按钮是否可见

**预期结果**
- `expect(make_offer_btn).not_to_be_visible(timeout=3000)` 通过（卖家看自己广告不显示）

---

### TC025: 消息中心会话中 Make offer 并提交成功

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC025` |
| **测试类** | `TestMakeOfferInConversation` |

**测试步骤**
1. Buyer 登录，点击广告的 Message 按钮进入消息中心（建立会话）
2. 在会话中找到 Make offer 按钮并点击（JS click）
3. 选择 10% off 折扣选项
4. 点击 `Offer £X` 提交按钮
5. 验证会话中出现议价金额（`text=/£[0-9]+\.[0-9]+/`）

**预期结果**
- 议价消息发送成功，会话中显示 `£XX.XX` 格式的金额

---

### TC026 + TC027 + TC027b: Make offer 表单验证（合并）

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC026` / `TC027` / `TC027b` |
| **测试类** | `TestMakeOfferInConversation` |

**TC026 测试步骤**
1. 点击 Make offer 按钮
2. 验证出价表单内联展开（`text=/10% off/i` 可见）

**TC027 测试步骤**
1. 若有自定义金额输入框：清空输入框
2. 尝试点击 Submit（不选折扣不输金额）
3. 验证是否有验证提示（软断言）

**TC027b 测试步骤**
1. 获取广告原价
2. 输入超过原价的金额（原价 + 10）
3. 点击 Submit
4. 验证是否出现超价验证提示（软断言）

**预期结果**
- TC026：表单内联展开，`10% off` 选项可见
- TC027：空值时有验证提示或按钮被禁用（软断言）
- TC027b：超价时有验证提示（软断言）

---

### TC044-Offer: Make an Offer 成功后创建/导航到会话

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC044`（Make offer 模块中） |
| **测试类** | `TestMakeOfferConversationCreation` |

**测试步骤**
1. Buyer 登录，记录消息中心初始会话数
2. 访问广告详情页，点击 Make offer → 选 10% off → 提交
3. 验证跳转到消息中心（URL 含 `/manage/messages`）
4. 验证会话中显示 `£XX.XX` 金额
5. 记录新会话数（与初始对比）

**预期结果**
- 提交后跳转到消息中心
- 议价消息可见
- 若创建新会话则会话数增加（软断言）

---

### TC028: AD DELETED 状态会话仍可发送消息

| 项目 | 内容 |
|------|------|
| **优先级** | P1 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC028` |
| **测试类** | `TestMakeOfferAdStatus` |

**前置条件**
- 存在 AD DELETED 状态的会话

**测试步骤**
1. Buyer 登录，打开消息中心
2. 找到带 "AD DELETED" 标记的会话并点击
3. 发送消息（`inbox.type_reply()` + `inbox.click_send()`）
4. 验证消息显示（`inbox.expect_chat_contains(message)`）

**预期结果**
- AD DELETED 状态的会话仍能正常发送消息

---

### TC028b: AD DELETED/EXPIRED/SOLD 状态广告信息卡显示

| 项目 | 内容 |
|------|------|
| **优先级** | P2 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC028b` |

**测试步骤**
1. 找到 AD DELETED / AD EXPIRED / SOLD 状态的会话并打开
2. 验证聊天面板中广告信息卡可见（`[data-q='ad-card']` 或图片元素）

**预期结果**
- 广告信息卡在特殊状态下仍正常显示（软断言）

---

## 十四、权限与认证

**测试类**: `TestGuestAndUnauthenticated`  
**文件**: `test_messages_core.py`

---

### TC002: 未登录 Buyer 点击联系按钮触发登录

| 项目 | 内容 |
|------|------|
| **优先级** | P0 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC002` |

**测试步骤**
1. 清空 cookies 确保未登录
2. 打开广告详情页
3. 点击 Send Message / Contact Seller 按钮
4. 检查：URL 含 `auth`/`login`，或 `[data-q='email-login']` 可见，或 "Continue with email" 可见，或 Login 按钮可见

**预期结果**
- 任一条件满足即视为触发登录流程（软断言）

---

### TC013: 未认证用户访问消息中心重定向到登录

| 项目 | 内容 |
|------|------|
| **优先级** | P0 |
| **标记** | `@pytest.mark.case_id_GUMTREE_MSG_TC013` |

**测试步骤**
1. 清空 cookies 确保未登录
2. 直接访问 `/manage/messages`
3. 检查：URL 含 `login`/`auth`，或跳转至首页，或 Login 按钮可见

**预期结果**
- URL 重定向或显示登录入口（软断言）

---

## 附录：用例状态汇总

| TC ID | 功能描述 | 优先级 | 测试文件 | 断言类型 |
|-------|----------|--------|----------|----------|
| TC001 | Buyer 发起新会话 | P0 | core | 硬断言 |
| TC002 | 未登录触发登录 | P0 | core | 软断言 |
| TC003 | 重复联系跳到已有会话 | P1 | core | 软断言 |
| TC004 | Seller 查看会话列表 | P0 | core | 硬断言 |
| TC005 | Seller 发送回复 | P0 | core | 硬断言 |
| TC006 | 空输入框 Send 禁用 | P1 | core | 硬断言 |
| TC007 | 发送普通消息 | P1 | core | 硬断言 |
| TC008 | 会话列表可见 | P1 | core | 硬断言 |
| TC008b | 顶部统计信息 | P1 | unread | 硬断言 |
| TC008c | 阅读后未读计数更新 | P1 | unread | 软断言 |
| TC008d | 首位会话未读不变 | P1 | unread | 硬断言 |
| TC008f | 绿色未读徽章样式 | P2 | unread | 软断言 |
| TC008g | 未读徽章位置 | P2 | unread | 软断言 |
| TC009 | AD DELETED 角标 | P2 | core | 软断言 |
| TC010 | AD EXPIRED 角标 | P2 | core | 软断言 |
| TC011 | 切换会话 | P1 | core | 软断言 |
| TC011b | 首页最多30个会话 | P2 | pagination | 硬断言 |
| TC011c | 滚动加载更多会话 | P2 | pagination | 硬断言 |
| TC011d | 滚动回顶部 | P2 | pagination | 硬断言 |
| TC012 | 刷新后会话持久化 | P1 | core | 硬断言 |
| TC013 | 未认证重定向 | P0 | core | 软断言 |
| TC014 | 广告信息卡显示 | P1 | core | 软断言 |
| TC015 | 广告信息卡点击跳转 | P1 | core | 软断言 |
| TC016 | More Options 菜单展开 | P1 | more_options | 硬断言 |
| TC017 | Delete - Cancel 取消 | P1 | more_options | 硬断言 |
| TC018 | Delete - 确认删除 | P1 | more_options | 硬断言 |
| TC018b | Delete - 单边删除验证 | P1 | more_options | 硬断言 |
| TC019 | Block 弹窗内容 | P1 | more_options | 硬断言 |
| TC020 | Block - Cancel 取消 | P2 | more_options | 硬断言 |
| TC021 | Report - 8个举报原因 | P1 | more_options | 硬断言 |
| TC021b | Report - 重复举报确认 | P2 | more_options | 硬断言 |
| TC022 | Report - 空值提交(已知BUG) | P2 | more_options | 软断言 |
| TC023 | Report - 选原因提交成功 | P1 | more_options | 硬断言 |
| TC024 | Make offer 按钮显示 | P1 | make_offer | 硬断言 |
| TC024b | 正向条件 Make offer 可见 | P1 | make_offer | 硬断言 |
| TC025 | 会话中 Make offer 成功 | P1 | make_offer | 硬断言 |
| TC025b | Seller 自己广告无 Make offer | P2 | make_offer | 硬断言 |
| TC026 | Make offer 表单内联展开 | P1 | make_offer | 硬断言 |
| TC027 | Make offer 空值验证 | P1 | make_offer | 软断言 |
| TC027b | Make offer 超价验证 | P1 | make_offer | 软断言 |
| TC028 | AD DELETED 仍可发消息 | P1 | make_offer | 硬断言 |
| TC028b | AD DELETED 广告卡显示 | P2 | make_offer | 软断言 |
| TC035 | Seller 立即看到新会话 | P0 | core | 软断言 |
| TC036 | 点击联系人跳转资料页 | P2 | core | 软断言 |
| TC038 | Enter 键发送消息 | P1 | core | 硬断言 |
| TC039 | 数据隔离验证 | P1 | core | 软断言 |
| TC040 | 被拉黑用户消息不送达 | P1 | more_options | 硬断言 |
| TC041 | 单张图片上传 | P1 | core | 软断言 |
| TC041b | 图片+文字发送 | P1 | core | 软断言 |
| TC041c | 超大图片上传 | P2 | core | 软断言 |
| TC041d | 逐个批量上传3张图片 | P1 | core | 软断言 |
| TC041e | 一次性批量上传5张图片 | P1 | core | 软断言 |
| TC041f | 上传10张验证5张限制 | P2 | core | 软断言 |
| TC042 | 单个视频上传 | P1 | core | 软断言 |
| TC042b | 多个视频上传 | P2 | core | 软断言 |
| TC042c | 视频+文字发送 | P2 | core | 软断言 |
| TC043 | 长消息(1000字符)发送 | P2 | core | 软断言 |
| TC044 | 5条消息触发评价提示 | P2 | core | 软断言 |
| TC044-Offer | Make offer 后创建会话 | P1 | make_offer | 软断言 |
| TC045 | 纯空白消息不能发送 | P1 | core | 软断言 |
| 分页-浏览器 | 浏览器滚动不触发翻页 | P1 | pagination | 硬断言 |

---

## 附录：执行命令参考

```bash
# 运行所有消息中心测试
pytest test_cases/messages/ -v --alluredir=reports/allure-results

# 运行快速综合工作流（推荐日常使用）
pytest test_cases/messages/ -k "Comprehensive" -v

# 按模块运行
pytest test_cases/messages/test_messages_core.py -v
pytest test_cases/messages/test_messages_more_options.py -v
pytest test_cases/messages/test_messages_make_offer.py -v
pytest test_cases/messages/test_messages_unread.py -v
pytest test_cases/messages/test_pagination_list_scroll.py -v
pytest test_cases/messages/test_pagination_simple.py -v

# 按优先级运行
pytest test_cases/messages/ -m p0 -v
pytest test_cases/messages/ -m p1 -v

# 通过全模块入口运行
pytest test_cases/messages/test_messages_all_modules.py -v
```

---

## 附录：已知缺陷

| Bug ID | 描述 | 相关用例 | 状态 |
|--------|------|----------|------|
| BUG-001 | Report 表单未选择原因时 Submit 按钮未被禁用，可直接提交 | TC022 | 已知，测试标记 `@pytest.mark.known_bug` |
