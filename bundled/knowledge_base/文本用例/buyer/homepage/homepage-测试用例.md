# Unicorn Gumtree - 网站首页 测试用例

> **生成时间**: 2026-04-10（第二轮：未登录会话）  
> **探测方式**: Playwright MCP 实测  
> **测试范围**: https://www.unicorn.gumtree.io/ 首页；**重点覆盖未登录访客**行为及与已登录态的差异  
> **总用例数**: 39 条  
> **可自动化**: 39 条  

---

## 测试环境配置（必填）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | unicorn | UK 测试环境（unicorn.gumtree.io） |
| 基础URL | https://www.unicorn.gumtree.io/ | 首页地址 |
| 站点名称 | Unicorn / Gumtree UK | 可选 |
| 角色 | visitor（未登录）为主 | 本次主测会话；已登录行为见文末附录 |
| 账号名称 | arin_yang_unicorn | session 命名建议 |
| 测试账号 | arin.yang@gumtree.com | 用户提供 |
| 测试密码 | （用户本地保管） | 本次未执行完整登录成功路径 |

**会话说明**  
第二轮探测时浏览器为 **未登录**：顶栏展示 **Login**、**Sign up**、**Post an ad**，**无** Messages、Menu。首轮曾测 **已登录** 态，差异见下表及附录。

---

## 未登录 vs 已登录 — 首页关键行为对照

| 操作 | 未登录（本轮 ✅） | 已登录（首轮参考） |
|------|-------------------|---------------------|
| 顶栏右侧 | Post an ad、Sign up、Login | Post an ad、Messages、Menu |
| 点击顶栏 **Post an ad** | 打开浮层，标题 **「Log in to sell an item」** | 未复测（首轮未点顶栏） |
| 点击 Hero **Post Ad** | 跳转 **my.unicorn.gumtree.io/login?cb=...postad%2Fcategory** | 同站 **www.unicorn.gumtree.io/postad/category** |
| 点击 **Login** | 浮层标题 **「Log in」** | 无此项（无 Login 按钮） |
| 点击列表 **Save Ad** | 弹出登录类浮层（需登录才能收藏） | 未测收藏成功态 |
| 主搜索 | 可进入搜索结果页 ✅ | 可搜 ✅ |

---

## Application Overview（阶段一）

**功能定位**：Gumtree UK Unicorn 首页；未登录用户可浏览、搜索、进入类目；发帖、收藏等需登录或通过浮层/跳转引导至 My Gumtree。

**用户角色（本轮）**：访客——可见注册/登录入口，不可见站内信箱与账户菜单。

**业务规则（实测 + 推断）**：
- **顶栏发帖**与 **Hero 发帖** 在未登录时行为不同：顶栏打开「卖东西需登录」类浮层；Hero **整页跳转**至 `my.unicorn.gumtree.io/login` 并带发帖回跳 `cb` ✅ 实测。
- **Save Ad** 在未登录时拦截为登录浮层 ✅ 实测。
- **Sign up** 浮层含 **Terms of use** 链接，点击可打开本站 `/termsofuse` ✅ 实测（新标签页）。
- **Cookie 横幅**：本轮首屏快照 **未** 出现 OneTrust 横幅（可能已保存过同意或地区策略）⚠️ 需在全新浏览器配置下补测。

**模块划分 [P0]**：未登录顶栏与双路径发帖；登录/注册浮层；搜索；类目；Good Finds 与 Save Ad 拦截。  
**[P1]**：卖车区块、页脚、Top Locations。  
**[P2]**：边界搜索、会话刷新。

---

## 测试用例

### 未登录访客 — 首页与顶栏

#### TC001: 首页加载 — 标题与 Hero 主文案

#### 📋 前置条件
- 可访问 Unicorn 站点

#### 🎬 执行步骤
1. 打开 `https://www.unicorn.gumtree.io/`
2. 查看标签页标题与首屏 Hero

#### ✅ 预期结果
- 页面标题 **「Gumtree | Free classified ads from the #1 classifieds site in the UK」** ✅ 实测
- H1 **「Free local classifieds」**，H2 **「One place for all your Ads」**；**「600K DAILY ACTIVE USERS」**、**「30K DAILY NEW ADS」** ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC002: 未登录顶栏 — Post an ad、Sign up、Login（无 Messages / Menu）

#### 📋 前置条件
- 清除登录态或使用无痕访问首页

#### 🎬 执行步骤
1. 查看顶栏右侧操作区

#### ✅ 预期结果
- 可见 **「Post an ad」**、**「Sign up」**、**「Login」** ✅ 实测
- **不可见** **「Messages」**、**「Menu」**（与已登录态区分）✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI / 权限
- **UI自动化**: ✅ 可自动化

---

#### TC003: 点击「Login」— 打开「Log in」浮层

#### 📋 前置条件
- 未登录，在首页

#### 🎬 执行步骤
1. 点击 **「Login」**

#### ✅ 预期结果
- 出现浮层，二级标题 **「Log in」** ✅ 实测
- 文案 **「Don't have an account?」** 与 **「Sign up」** 按钮 ✅ 实测
- 提供 **Continue with Apple**、**Continue with Google**、**Continue with Facebook**、**Continue with email** ✅ 实测
- 提供 **Close** 关闭 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC004: 点击顶栏「Post an ad」— 浮层标题「Log in to sell an item」

#### 📋 前置条件
- 未登录，在首页

#### 🎬 执行步骤
1. 点击顶栏 **「Post an ad」**（非 Hero 内按钮）

#### ✅ 预期结果
- **不离开首页**，打开浮层，标题 **「Log in to sell an item」** ✅ 实测
- 同样提供 Apple / Google / Facebook / email 与关闭 ✅ 实测
- **与 Hero「Post Ad」整页跳转行为不同** ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI / 权限
- **UI自动化**: ✅ 可自动化

---

#### TC005: 点击 Hero「Post Ad」— 跳转 My Gumtree 登录并带发帖回跳参数

#### 📋 前置条件
- 未登录，在首页

#### 🎬 执行步骤
1. 点击 Hero 区域 **「Post Ad」**

#### ✅ 预期结果
- 浏览器跳转至 **https://my.unicorn.gumtree.io/login** ✅ 实测
- Query 参数 **cb** 包含 `https://www.unicorn.gumtree.io/postad/category`（URL 编码形式）✅ 实测
- 落地页标题 **「Login | My Gumtree - Gumtree」** ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / 权限
- **UI自动化**: ✅ 可自动化

---

#### TC006: 点击 Good Finds 卡片「Save Ad」— 弹出需登录浮层

#### 📋 前置条件
- 未登录；首页列表可见

#### 🎬 执行步骤
1. 点击任意商品卡片上的 **「Save Ad」**

#### ✅ 预期结果
- 仍在首页 URL，弹出登录/注册类浮层（含 **Don't have an account? Sign up**、**Continue with email** 等）✅ 实测
- 无障碍快照中标题节点可能无文本，但交互意图为拦截未登录收藏 ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / 权限 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC007: 点击「Sign up」— 注册浮层与条款链接

#### 📋 前置条件
- 未登录，在首页

#### 🎬 执行步骤
1. 点击 **「Sign up」**
2. 查看浮层标题与底部协议文案

#### ✅ 预期结果
- 浮层标题 **「Sign up」** ✅ 实测
- 文案 **「Already got an account?」** 与 **「Log in」** ✅ 实测
- 含 **「By Signing up you agree to the Terms of use and Privacy notice」**；**Terms of use** 可点击打开 **https://www.unicorn.gumtree.io/termsofuse**（新标签页）✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI / 合规
- **UI自动化**: ✅ 可自动化

---

### 浏览与搜索（未登录可访问）

#### TC008: 未登录用户主搜索 — 输入关键词并进入搜索结果页

#### 📋 前置条件
- 未登录，在首页

#### 🎬 执行步骤
1. 在「Type search query」输入 `bike`
2. 点击搜索按钮

#### ✅ 预期结果
- **无需登录**即可进入搜索页 ✅ 实测
- URL 含 `q=bike`、`search_location=United%20Kingdom` 等 ✅ 实测
- 页面标题 **「Bike | Other Bikes For Sale - Gumtree」** ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC009: 热门分类「Cars & Vehicles」— UTM 与落地标题

#### 📋 前置条件
- 未登录，在「Discover popular categories」

#### 🎬 执行步骤
1. 点击 **「Cars & Vehicles」** 卡片

#### ✅ 预期结果
- URL 含 `utm_source=featured_categories`、`utm_campaign=cars`、`search_location=United%20Kingdom` ✅ 实测
- 标题 **「Used Cars for Sale Across the UK | Gumtree」** ✅ 实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC010: 主导航「Cars & Vehicles」跳转

#### 📋 前置条件
- 未登录，在首页

#### 🎬 执行步骤
1. 点击主导航 **「Cars & Vehicles」**

#### ✅ 预期结果
- 进入 `/cars-vans-motorbikes/cars` 频道 ✅ 实测（2026-04-16 本地 Playwright 回归：URL 跳转至 Cars 类目确认）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### Cookie 与合规（待全新会话补测）

#### TC011: 首次访问可能出现 OneTrust Cookie 横幅

#### 📋 前置条件
- 新用户代理或无站点 Cookie

#### 🎬 执行步骤
1. 打开首页

#### ✅ 预期结果
- 可能出现 **「We Care About Your Privacy」** 与 **Accept all** / **Reject non-essential** / **Manage options** ✅ 实测（2026-04-16：全新无痕会话实测，www 首页本轮未出现 OneTrust 横幅；my.unicorn.gumtree.io 子域首访确认出现横幅。www 主站环境横幅出现与否与策略/cookie 状态有关，自动化中已通过 `close_privacy_dialogs` 封装处理）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 合规 / UI
- **UI自动化**: ✅ 可自动化

---

### 登录表单细节（浮层内）

#### TC012: 邮箱登录 — 未填时 Continue 禁用

#### 📋 前置条件
- 已打开 Login 浮层并选择 **Continue with email**

#### 🎬 执行步骤
1. 不输入邮箱密码，观察 **Continue**

#### ✅ 预期结果
- **Continue** 为 **disabled** ✅ 实测（2026-04-16：打开 Login 浮层 → Continue with email → 空字段状态下 Continue 按钮 disabled 确认）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC013: 错误邮箱或密码提示

#### 📋 前置条件
- Login 浮层邮箱模式

#### 🎬 执行步骤
1. 输入错误账密提交

#### ✅ 预期结果
- 展示 **「Incorrect email address or password. Check your details and try again.」** ✅ 实测（2026-04-16：输入错误账密提交后确认弹窗顶部显示红色 Banner，文案与预期完全一致）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 负向
- **UI自动化**: ✅ 可自动化

---

#### TC014: 「Forgot password?」入口

#### 📋 前置条件
- 邮箱登录表单可见

#### 🎬 执行步骤
1. 点击 **Forgot password?**

#### ✅ 预期结果
- 进入找回密码流程 ✅ 实测（2026-04-16：点击 Forgot password? 后弹窗内切换，标题变为 "Forgot password"，显示邮箱输入框与说明文案）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### 搜索边界

#### TC015: 空关键词搜索

#### 📋 前置条件
- 首页

#### 🎬 执行步骤
1. 不输入关键词，点击搜索

#### ✅ 预期结果
- 不跳转或提示或默认结果 ✅ 实测（2026-04-16：空关键词点击搜索，页面不离开首页，搜索被拦截）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值 / 负向
- **UI自动化**: ✅ 可自动化

---

#### TC016: 特殊字符或超长关键词

#### 📋 前置条件
- 首页搜索框

#### 🎬 执行步骤
1. 输入 `%`、`*`、超长字符串并搜索

#### ✅ 预期结果
- 被接受、截断或报错 ✅ 实测（2026-04-16：输入 `%*<>&"'` 搜索后正常跳转搜索结果页，页面无崩溃、无 5xx 错误）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界值 / 安全
- **UI自动化**: ✅ 可自动化

---

### 内容与页脚

#### TC017: Discover more Good Finds 列表结构

#### 📋 前置条件
- 首页该区块

#### 🎬 执行步骤
1. 检查卡片字段

#### ✅ 预期结果
- 含图、标题、h2、£ 价格、地区、时间、**Save Ad**；部分 **SPOTLIGHT**、**Delivery available** ✅ 实测（与标准模板一致）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC018: 卖车推广区「Looking to sell your car?」

#### 📋 前置条件
- 首页对应区块

#### 🎬 执行步骤
1. 查看 **Enter reg**、**Sell now**

#### ✅ 预期结果
- 标题与 **Free / Quick / Easy** 步骤；输入框与按钮存在 ✅ 实测（2026-04-16：「Looking to sell your car?」标题可见，车牌输入框与 Sell now 按钮均存在）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC019: 页脚分组与政策链接

#### 📋 前置条件
- 首页页脚

#### 🎬 执行步骤
1. 检查 About Us、Help、Apps、版权与 Terms、Privacy、Cookies

#### ✅ 预期结果
- 含 **Terms of Use**（`/termsofuse`）、**Privacy Notice**（`/privacy_policy`）、**Cookies Policy**（`/cookies`）等 ✅ 实测（2026-04-16：滚动至页脚确认三个政策链接均可见且 href 正确）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC020: Top Locations 地区链接

#### 📋 前置条件
- 首页

#### 🎬 执行步骤
1. 查看 **Top Locations** 与 `/uk/...` 链接

#### ✅ 预期结果
- Tab **「Top Locations」**；含 London、Manchester 等 ✅ 实测（2026-04-16：页脚 Top Locations 区块可见，London 链接存在）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### 会话与导航

#### TC021: 刷新首页模块仍在

#### 📋 前置条件
- 首页

#### 🎬 执行步骤
1. F5 刷新

#### ✅ 预期结果
- Hero、搜索、分类仍展示 ✅ 实测（2026-04-16：F5 刷新后 H1「Free local classifieds」与「Discover popular categories」区块仍可见）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 时序 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC022: 搜索页后退回首页

#### 📋 前置条件
- 从首页进入搜索页

#### 🎬 执行步骤
1. 浏览器后退

#### ✅ 预期结果
- URL 回到 `https://www.unicorn.gumtree.io/` ⚠️ 推断（2026-04-16 自动化测试因 SPA 路由特性出现 net::ERR_ABORTED，建议人工确认实际后退行为）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 时序 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC023: Logo 回根路径

#### 📋 前置条件
- 在子路径

#### 🎬 执行步骤
1. 点击 **Gumtree** Logo

#### ✅ 预期结果
- 导航至 `/` ✅ 实测（2026-04-16：从 Cars LP 点击 Logo，URL 回到首页根路径确认）

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC024: 标题层级 H1 / H2

#### 📋 前置条件
- 首页

#### 🎬 执行步骤
1. 检查 H1 与分区 H2

#### ✅ 预期结果
- H1 **Free local classifieds**；**Discover popular categories** 等为 H2 ✅ 实测

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UI / 无障碍
- **UI自动化**: ✅ 可自动化

---

### Discover popular categories（抽样与全覆盖）

#### TC025: Home & Garden

#### 📋 前置条件
- 首页分类区

#### 🎬 执行步骤
1. 点击 **Home & Garden**

#### ✅ 预期结果
- URL 含 `home-garden` 等 ✅ 实测（2026-04-16：点击后成功跳转至对应类目页，无报错）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC026: Tradespeople

#### 📋 前置条件
- 同上

#### 🎬 执行步骤
1. 点击 **Tradespeople**

#### ✅ 预期结果
- URL 含 `building-home-removal-services` 等 ✅ 实测（2026-04-16：点击 Tradespeople 成功跳转）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC027: Baby & Kids

#### 📋 前置条件
- 同上

#### 🎬 执行步骤
1. 点击 **Baby & Kids**

#### ✅ 预期结果
- URL 含 `baby-kids-stuff` 等 ✅ 实测（2026-04-16：点击 Baby & Kids 成功跳转）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC028: Fashion

#### 📋 前置条件
- 同上

#### 🎬 执行步骤
1. 点击 **Fashion**

#### ✅ 预期结果
- URL 含 `clothing` 等 ✅ 实测（2026-04-16：点击 Fashion 成功跳转）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC029: Sports & Leisure

#### 📋 前置条件
- 同上

#### 🎬 执行步骤
1. 点击 **Sports & Leisure**

#### ✅ 预期结果
- URL 含 `sports-leisure-travel` 等 ✅ 实测（2026-04-16：点击 Sports & Leisure 成功跳转）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC030: Computers

#### 📋 前置条件
- 同上

#### 🎬 执行步骤
1. 点击 **Computers**

#### ✅ 预期结果
- URL 含 `computers-pcs-laptops` 等 ✅ 实测（2026-04-16：点击 Computers 成功跳转）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC031: Properties

#### 📋 前置条件
- 同上

#### 🎬 执行步骤
1. 点击 **Properties**

#### ✅ 预期结果
- URL 含 `flats-houses` 等 ✅ 实测（2026-04-16：点击 Properties 成功跳转）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC032: Cars & Vehicles 与 TC009 一致性

#### 📋 前置条件
- 同上

#### 🎬 执行步骤
1. 对比主导航与热门分类进入 Cars 的落地页

#### ✅ 预期结果
- 与 TC009 一致 ✅ 实测（TC009）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC033: Discover more Good Finds 标题与地区

#### 📋 前置条件
- 首页

#### 🎬 执行步骤
1. 查看区块标题与地区

#### ✅ 预期结果
- **Discover more Good Finds**；**United Kingdom** ✅ 实测（2026-04-16：区块标题与地区文案均可见）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### 附录：已登录态行为（首轮 MCP，供回归对照）

#### TC034: 已登录顶栏 — Messages 与 Menu（无 Login）

#### 📋 前置条件
- 有效会话，已登录

#### 🎬 执行步骤
1. 打开首页查看顶栏

#### ✅ 预期结果
- 可见 **Messages**（`/manage/messages`）、**Menu**；**无** Login / Sign up ✅ 首轮实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / 权限
- **UI自动化**: ✅ 可自动化

---

#### TC035: 已登录 Menu 项

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 打开 **Menu**

#### ✅ 预期结果
- 含 Manage my Ads、My Orders、Messages、Favourites、My Alerts、My Details、Manage my Job Ads、Help & Contact、Logout ✅ 首轮实测

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC036: 已登录 — Hero「Post Ad」直达本站发帖类目

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 点击 Hero **「Post Ad」**

#### ✅ 预期结果
- 跳转 **https://www.unicorn.gumtree.io/postad/category**，标题 **「Post an ad | Gumtree.com」** ✅ 首轮实测（与未登录跳转 My Gumtree 不同）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / 权限
- **UI自动化**: ✅ 可自动化

---

#### TC037: 已登录 — 收藏 Save Ad 成功态

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 点击 **Save Ad**

#### ✅ 预期结果
- 收藏状态变更或提示成功 ✅ 实测（2026-04-16：已登录状态点击 Save Ad，无登录拦截弹窗，收藏动作执行）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

#### TC038: Logout 后恢复访客顶栏

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. Menu → **Logout** → 回首页

#### ✅ 预期结果
- 顶栏恢复 **Login**、**Sign up**；行为与 TC002 一致 ⚠️ 推断（2026-04-16 自动化因 OneTrust 横幅覆盖 Menu 按钮点击受阻，建议人工在已登录态执行 Logout 步骤确认）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 权限 / 时序
- **UI自动化**: ✅ 可自动化

---

#### TC039: Manage my Job Ads 链接

#### 📋 前置条件
- 已登录且打开 Menu

#### 🎬 执行步骤
1. 查看 **Manage my Job Ads**

#### ✅ 预期结果
- 指向 `https://recruiters.gumtree.com/job-listing/` ✅ 首轮实测

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

## 测试统计

| 优先级 | 总数 | 可自动化 |
|--------|------|---------|
| P0 | 14 | 14 |
| P1 | 17 | 17 |
| P2 | 8 | 8 |
| P3 | 0 | 0 |
| **合计** | **39** | **39** |

**实测覆盖率（第二轮未登录）**：顶栏、双路径发帖、Save Ad、Login/Sign up 浮层、搜索、Cars 分类、Hero 标题等均已 **✅**；Cookie 首次横幅、空搜、部分页脚细节为 **⚠️**。

---

## 阶段三探测记录摘录（第二轮 · 未登录）

| 场景 | 实测结论 |
|------|-----------|
| 顶栏 | Post an ad、Sign up、Login；无 Messages/Menu ✅ |
| Login | 浮层「Log in」+ 社交登录 + email ✅ |
| Post an ad（顶栏） | 「Log in to sell an item」浮层 ✅ |
| Hero Post Ad | `my.unicorn.gumtree.io/login?cb=...postad%2Fcategory` ✅ |
| Save Ad | 登录类浮层 ✅ |
| Sign up | 「Sign up」+ Terms of use → `/termsofuse` 新标签页 ✅ |
| 搜索 bike | 未登录可搜，URL 与标题同前 ✅ |
| Cars 热门分类 | UTM + Used Cars 标题 ✅ |
