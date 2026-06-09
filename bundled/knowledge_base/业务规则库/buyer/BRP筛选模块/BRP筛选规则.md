# Buyer - BRP 筛选业务规则

## 1. 功能概述
- **功能描述**：买家在 BRP（Browse Results Page，浏览结果页）点击 Filter chip 进入多属性筛选页，通过类目/价格/品种/颜色/规格等多维度组合筛选缩小搜索范围，查看符合条件的广告列表
- **用户角色**：访客和已登录买家均可使用筛选功能（无需登录）
- **入口位置**：首页类目入口 → BRP 页顶部 Filter chip
- **依赖模块**：首页业务域（类目入口）、BRP 页面、多选子页面

## 2. 核心流程

### 2.1 主流程
1. 点击首页类目入口进入 BRP（浏览结果页），结果数量文字可见
2. 点击 BRP 顶部「Filter」按钮，进入筛选页（Filters 标题可见）
3. 在筛选页设置各属性维度（类目/价格/多选属性/单选属性）
4. 底部「Show Results」按钮始终可见，可点击查看筛选结果
5. 点击 Show Results 返回 BRP，Filter 按钮显示激活状态「Filter (n)」
6. 有广告时显示广告列表；0 结果时显示 Save search 按钮

### 2.2 异常流程
- **筛选结果为 0**：BRP 显示「Save search」按钮；iOS 可能同时展示「相似广告」推荐
- **属性不存在（平台差异）**：iOS / Android 的属性集可能不同，找不到的属性跳过，不影响整体流程
- **多选超出上限**：Mobile Phones Model 最多勾选 10 个，超出后其余项置灰

## 3. 业务规则

### 3.1 输入规则
| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| Category | String | 否 | 类目下钻路径，如 Pets for Sale → Dogs |
| Price Min | Number | 否 | 价格下限（如 10），与 Max 独立设置 |
| Price Max | Number | 否 | 价格上限（如 2000），与 Min 独立设置 |
| 多选属性（含□） | Array | 否 | Dog Breed / Sex / Model / Storage / Condition / Colour 等 |
| 单选属性（无□） | String | 否 | Vaccinated / Neutered / Deflead / Microchipped / KC Registered / Health checked 等，选 yes |

### 3.2 校验规则
- **Show Results 按钮**：始终处于 enabled 状态，无论是否选择了筛选条件
- **Price Min/Max 校验**：Price min > Price max 时前端显示校验提示，但仍允许跳转 SRP（已实测确认）
- **多选数量策略**：
  - 有 CheckBox（□）的属性：总选项 < 5 时全选；否则选 5 个
  - 无 CheckBox（单选列表）：直接点击 yes
- **Model 多选上限**：Apple iPhone Model 最多勾选 10 个，超出后其余项置灰不可选
- **筛选激活标记**：点击 Show Results 后，BRP Filter 按钮显示「Filter (n)」，n > 0

### 3.3 权限规则
- 筛选功能无需登录，访客和已登录用户均可使用
- BRP 筛选页无底部导航栏，不可通过 Tab 直接跳回首页（需逐层 go_back）

### 3.4 业务约束
- **页面层级**：首页 → BRP → Filter 筛选页 → 多选子页面（最多4层）
- **iOS 特殊行为**：BRP 页面的 tab bar 在 iOS 中 visible=false（全屏浏览），必须用 `element_to_be_clickable` 判断 home.tab 是否可点
- **回首页导航策略**：
  - BRP 页：tab bar 可见（Android）/ 需 clickable 判断（iOS）→ 直接点 Home tab
  - Filter 筛选页：无 tab bar → go_back() → 再点 Home tab
  - 多选子页面：go_back() → Filter 页 → go_back() → Home tab
- **单选属性自动返回**：单选属性（无□）选中 yes 后页面自动返回 Filter 页；若未自动返回则手动 go_back()
- **0 结果处理**：iOS 可能展示相似广告推荐，不强断言无广告图片；仅断言「Save search」按钮可见

### 3.5 Dogs 类目专属规则
| 属性 | 类型 | 操作 |
|-----|------|------|
| Category | 下钻 | Pets → Pets for Sale → Dogs |
| Price | 区间 | Min=10 / Max=2000 |
| Dog Breed | 多选（□） | 不足5项全选，否则选5个 |
| Sex | 多选（□，3项） | 全选（3项不足5项，全选） |
| Vaccinated | 单选（无□） | 选 yes |
| Neutered or Spayed | 单选（无□） | 选 yes |
| Deflead | 单选（无□） | 选 yes |
| Microchipped | 单选（无□） | 选 yes |
| KC Registered | 单选（无□） | 选 yes |
| Health checked by a vet | 单选（无□） | 选 yes |

### 3.6 Mobile Phones 类目专属规则
| 属性 | 类型 | 操作 |
|-----|------|------|
| Category | 下钻 | Mobile Phones → Apple iPhone |
| Model | 多选（□，上限10） | 滚动全选（超出10项后置灰） |
| Storage Capacity | 多选（□） | 不足5项全选，否则选5项 |
| Condition | 多选（□，4项） | 全选（4项不足5项） |
| Colour | 多选（□） | 不足5项全选，否则选5项 |

## 4. 错误处理
| 错误码 | 错误信息 | 触发条件 | 用户提示 |
|-------|---------|---------|---------|
| - | Price 校验提示 | Min > Max | 显示校验提示文案，但仍允许提交 |
| - | 0 结果页 | 筛选条件过严导致无匹配广告 | 显示「Save search」按钮 |
| - | 属性不可选（置灰） | Model 多选超出 10 个上限 | 超出选项自动置灰 |
| - | 属性行找不到 | iOS/Android 平台属性集不同 | 跳过该属性，继续流程 |

## 5. 已知问题
- **TC022（Dogs）**：Keyword 特殊字符搜索行为：自动化脚本 selector 错误，产品行为待人工验证
- **iOS 属性集差异**：部分单选属性（Vaccinated 等）在 iOS 平台上可能不存在，需分平台维护
- **Filter 页滚动**：单选属性（需下滑查找）依赖滚动找到属性行，动态内容高度可能导致滚动范围不确定

## 6. 变更历史
| 日期 | 版本 | 变更内容 | 变更人 |
|-----|------|---------|--------|
| 2026-04-17 | v1.0 | 初始版本，基于 buyer-筛选功能-Dogs与MobilePhones.md（2条用例）归档 | Arin Yang |
