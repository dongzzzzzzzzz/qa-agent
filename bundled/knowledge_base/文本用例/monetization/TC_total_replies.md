# Manage My Ads - Remaining Credit Allowance 模块测试用例

> **生成时间**: 2026-03-13
> **设计来源**: Figma - Dashboard / Desktop-web My ads（Phase 1）
> **Figma Node**: 639:6878（统计区 Remaining Credit Allowance 列）、639:9228（展开明细面板）
> **测试范围**: Remaining Credit Allowance 统计卡片及悬浮明细面板
> **总用例数**: 12 条
> **可自动化**: 9 条 (75%)
> **⚠️ 权限说明**: Remaining Credit Allowance 模块（含明细面板）仅 **Pro 账号**可见，普通账号该统计区不存在

> **变更说明（2026-03-13）**：
> - 模块文案由 "Total Replies" 更名为 **"Remaining Credit Allowance"**
> - 明细面板触发方式由"点击 ⓘ 图标"改为**鼠标悬浮**整个模块
> - 统计区由 3 列（Live Ads / Ad views / Total Replies）调整为 4 列（Live Ads / Search Impressions / Unique Replies / Remaining Credit Allowance）
> - 数据刷新提示文案由 `"We update the data every morning at 8 a.m."` 改为 `"We refresh the data daily"`
> - 普通账号行为变更：不显示任何统计卡片（而非仅隐藏 ⓘ 图标）

---

## 测试环境配置

### Pro 账号（用于 TC001~TC010）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | uk | Gumtree 英国站 |
| 基础URL | https://www.zoidberg.gumtree.io | Zoidberg 测试环境 |
| 页面路径 | /manage/ads | Manage My Ads 页面 |
| 角色 | seller_pro | Pro 卖家账号 |
| 账号名称 | dc_seller_pro_uk | 用于 session 命名 |
| 测试账号 | loroxon693@dnsclick.com | Pro 账号登录邮箱 |
| 测试密码 | Gumtree123! | 登录密码 |

### 普通账号（用于 TC011~TC012）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | uk | Gumtree 英国站 |
| 基础URL | https://www.zoidberg.gumtree.io | Zoidberg 测试环境 |
| 页面路径 | /manage/ads | Manage My Ads 页面 |
| 角色 | seller_normal | 普通卖家账号 |
| 账号名称 | dc_seller_normal_uk | 用于 session 命名 |
| 测试账号 | normal-user@gumtree.com | 普通账号登录邮箱 |
| 测试密码 | Gumtree123! | 登录密码 |

**前置说明**：TC001~TC010 均使用 Pro 账号登录，且账号名下存在至少一条有余额数据的广告。

---

## 📑 目录

**Pro 账号用例（loroxon693@dnsclick.com）**
- [TC001 Remaining Credit Allowance 标签文字正确展示](#tc001-remaining-credit-allowance-标签文字正确展示)
- [TC002 统计区四列标签全部正确展示](#tc002-统计区四列标签全部正确展示)
- [TC003 悬浮模块展开明细面板](#tc003-悬浮模块展开明细面板)
- [TC004 明细面板内容正确性验证](#tc004-明细面板内容正确性验证)
- [TC005 明细面板总值为非负整数且与统计区一致](#tc005-明细面板总值为非负整数且与统计区一致)
- [TC006 鼠标移开后明细面板消失](#tc006-鼠标移开后明细面板消失)
- [TC007 数据刷新提示信息展示](#tc007-数据刷新提示信息展示)
- [TC008 Credit Allowance 为零时的展示（Skip）](#tc008-credit-allowance-为零时的展示skip)
- [TC009 四列统计卡片等宽布局验证](#tc009-四列统计卡片等宽布局验证)
- [TC010 页面刷新后统计数据保持一致](#tc010-页面刷新后统计数据保持一致)

**普通账号用例（normal-user@gumtree.com）**
- [TC011 普通账号无 Remaining Credit Allowance 统计模块](#tc011-普通账号无-remaining-credit-allowance-统计模块)
- [TC012 普通账号无 Pro 专属统计区](#tc012-普通账号无-pro-专属统计区)

---

## 测试用例

### TC001: Remaining Credit Allowance 标签文字正确展示

#### 📋 前置条件
- 使用 **Pro 账号** 登录（loroxon693@dnsclick.com / Gumtree123!）
- 进入 Manage My Ads 页面（`https://www.zoidberg.gumtree.io/manage/ads`）

#### 🎬 执行步骤
1. 导航至 Manage My Ads 页面
2. 定位统计区 "Remaining Credit Allowance" 卡片
3. 观察标签文字是否正确展示

#### ✅ 预期结果
- "Remaining Credit Allowance" 标签文字可见
- 标签内容精确包含 "Remaining Credit Allowance"

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化状态**: ✅ 已实现并通过

---

### TC002: 统计区四列标签全部正确展示

#### 📋 前置条件
- 使用 **Pro 账号** 登录（loroxon693@dnsclick.com / Gumtree123!），进入 Manage My Ads 页面

#### 🎬 执行步骤
1. 定位统计区四列
2. 逐一检查每列标签是否可见

#### ✅ 预期结果
统计区按以下顺序展示四列标签，全部可见：

| 列序 | 标签文字 |
|------|---------|
| 1 | Live Ads |
| 2 | Search Impressions |
| 3 | Unique Replies |
| 4 | Remaining Credit Allowance |

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI测试
- **UI自动化**: ✅ 可自动化
- **自动化状态**: ✅ 已实现并通过

---

### TC003: 悬浮模块展开明细面板

#### 📋 前置条件
- 使用 **Pro 账号** 登录（loroxon693@dnsclick.com / Gumtree123!），进入 Manage My Ads 页面
- 明细面板默认处于**收起**状态

#### 🎬 执行步骤
1. 确认 "Remaining Credit Allowance" 模块可见
2. 将鼠标悬浮（hover）在该模块上

#### ✅ 预期结果
- 悬浮后，明细面板展开
- 面板包含 credit 余额明细内容（含描述文字 "The balance shows"）
- 触发方式为**鼠标悬浮**，无需点击

> ⚠️ **与 Figma 设计差异**：Figma 设计为点击 ⓘ 图标触发，实际实现改为悬浮整个模块触发，ⓘ 图标已移除。

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化状态**: ✅ 已实现并通过

---

### TC004: 明细面板内容正确性验证

#### 📋 前置条件
- 使用 **Pro 账号** 登录（loroxon693@dnsclick.com / Gumtree123!）
- 已悬浮 Remaining Credit Allowance 模块，明细面板已展开（参考 TC003）

#### 🎬 执行步骤
1. 观察展开的明细面板内容

#### ✅ 预期结果
- 面板顶部显示描述文字，包含 **"The balance shows"**
- 面板包含至少一行广告类型数据（广告类型名称 + 对应余额数值）
- 数据行格式：左侧为广告类型名称，右侧为余额数值

> **注意**：面板内容为动态 credit 分配明细，具体行数和内容因账号而异（实测账号有 28 行数据）。

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化状态**: ✅ 已实现并通过

---

### TC005: 明细面板总值为非负整数且与统计区一致

#### 📋 前置条件
- 使用 **Pro 账号** 登录（loroxon693@dnsclick.com / Gumtree123!）

#### 🎬 执行步骤
1. 读取统计区 "Remaining Credit Allowance" 显示的数值
2. 验证数值格式合法性
3. 悬浮展开明细面板
4. 在面板中核对相同数值是否展示

#### ✅ 预期结果
- 统计区数值为**非负整数**（≥ 0），不出现负数、小数、"-"、"N/A" 等异常格式
- 面板中包含与统计区相同的数值（数值一致性）
- 各细分广告类型的余额数值与总余额**无严格数学关系**（可大于或小于，属正常业务逻辑）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 数据格式验证
- **UI自动化**: ✅ 可自动化
- **自动化状态**: ✅ 已实现并通过

---

### TC006: 鼠标移开后明细面板消失

#### 📋 前置条件
- 使用 **Pro 账号** 登录（loroxon693@dnsclick.com / Gumtree123!）
- 明细面板已展开（参考 TC003）

#### 🎬 执行步骤
1. 确认明细面板处于展开状态
2. 将鼠标移至页面其他安全区域（远离面板）

#### ✅ 预期结果
- 明细面板关闭/消失
- 页面恢复正常状态，不影响其他元素
- 不触发任何意外导航（如跳转到首页）

> ⚠️ **与 Figma 设计差异**：Figma 设计为点击外部区域关闭，实际实现为鼠标移开后自动关闭。关闭操作使用 `Escape` 键或 `page.mouse.move()` 至安全坐标，**禁止点击**（防止误触链接导航）。

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 交互测试
- **UI自动化**: ✅ 可自动化
- **自动化状态**: ✅ 已实现并通过

---

### TC007: 数据刷新提示信息展示

#### 📋 前置条件
- 使用 **Pro 账号** 登录（loroxon693@dnsclick.com / Gumtree123!），进入 Manage My Ads 页面

#### 🎬 执行步骤
1. 定位统计数据区域底部的提示信息
2. 查看提示文字内容

#### ✅ 预期结果
- 显示数据刷新提示文字，包含关键词 **"refresh"**
- 实际文案：`"We refresh the data daily"`
- 提示信息在统计区下方可见

> ⚠️ **与 Figma 设计差异**：原设计文案为 `"We update the data every morning at 8 a.m., but sometimes it may be delayed."`，实际文案已简化为 `"We refresh the data daily"`，且无 ⓘ 信息图标前缀。

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI测试
- **UI自动化**: ✅ 可自动化
- **自动化状态**: ✅ 已实现并通过

---

### TC008: Credit Allowance 为零时的展示（Skip）

#### 📋 前置条件
- 使用 **Pro 账号** 登录（loroxon693@dnsclick.com / Gumtree123!）
- 且该账号**余额为零**（需专用零额度测试账号）

#### 🎬 执行步骤
1. 进入 Manage My Ads 页面
2. 查看 "Remaining Credit Allowance" 卡片数值
3. 悬浮展开面板，查看细分广告类型余额

#### ✅ 预期结果
- 统计区显示数字 `"0"`（而非空白、"-" 或报错）
- 悬浮后面板正常展开，各广告类型余额均显示 `0`
- 页面无报错、无崩溃

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 边界值测试
- **UI自动化**: ✅ 可自动化
- **自动化状态**: ⏭ **已跳过**（Skip）——需要专用零额度 Pro 测试账号，待提供后执行

---

### TC009: 四列统计卡片等宽布局验证

#### 📋 前置条件
- 使用 **Pro 账号** 登录（loroxon693@dnsclick.com / Gumtree123!），进入 Manage My Ads 页面

#### 🎬 执行步骤
1. 在标准宽度浏览器下访问 Manage My Ads 页面
2. 观察统计区四列（Live Ads / Search Impressions / Unique Replies / Remaining Credit Allowance）的宽度分配

#### ✅ 预期结果
- 四列等宽均分显示
- 各列之间有视觉分隔
- 布局整齐，无错位或溢出

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UI布局测试
- **UI自动化**: ❌ 不可自动化（需人工视觉判断像素布局）

---

### TC010: 页面刷新后统计数据保持一致

#### 📋 前置条件
- 使用 **Pro 账号** 登录（loroxon693@dnsclick.com / Gumtree123!），进入 Manage My Ads 页面

#### 🎬 执行步骤
1. 记录页面上 "Remaining Credit Allowance" 显示的数值（设为 N）
2. 刷新浏览器（F5 / Cmd+R）
3. 页面重新加载后，再次查看 "Remaining Credit Allowance" 数值

#### ✅ 预期结果
- 刷新后数值与刷新前相同（= N）
- 不出现数据闪烁或短暂显示错误值的情况
- 页面加载期间统计区有适当的 loading 状态（骨架屏或 spinner）

> ⚠️ **注意**：若在数据更新时间点前后刷新，数据可能因数据源更新而变化，属正常现象。

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 稳定性测试
- **UI自动化**: ❌ 不可自动化（依赖数据一致性，受数据更新时机影响）

---

### TC011: 普通账号无 Remaining Credit Allowance 统计模块

#### 📋 前置条件
- 使用**普通账号**登录（normal-user@gumtree.com / Gumtree123!）
- 进入 Manage My Ads 页面

#### 🎬 执行步骤
1. 进入 Manage My Ads 页面
2. 在页面中查找 "Remaining Credit Allowance" 标签
3. 查找明细面板描述文字 "The balance shows"

#### ✅ 预期结果
- **"Remaining Credit Allowance" 标签不可见**（普通账号无此模块）
- 明细面板描述文字 "The balance shows" 不在页面中
- 普通账号 Manage My Ads 页面为简化布局：仅显示广告列表，无任何统计卡片区域

> **实测行为**：普通账号与 Pro 账号使用**完全不同的页面布局**。普通账号页面无任何统计卡片区（无 Live Ads、Search Impressions、Unique Replies、Remaining Credit Allowance），仅展示基本的广告管理列表。

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 权限测试
- **UI自动化**: ✅ 可自动化
- **自动化状态**: ✅ 已实现并通过

---

### TC012: 普通账号无 Pro 专属统计区

#### 📋 前置条件
- 使用**普通账号**登录（normal-user@gumtree.com / Gumtree123!）
- 进入 Manage My Ads 页面

#### 🎬 执行步骤
1. 在页面中分别查找 "Search Impressions" 和 "Remaining Credit Allowance" 标签
2. 验证这两个 Pro 专属统计标签均不可见

#### ✅ 预期结果
- **"Search Impressions" 不可见**（Pro 专属统计列）
- **"Remaining Credit Allowance" 不可见**（Pro 专属 credit 模块）
- 页面无权限相关报错或异常样式

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 权限测试
- **UI自动化**: ✅ 可自动化
- **自动化状态**: ✅ 已实现并通过

---

## 测试统计

### 用例概览
- **总用例数**: 12 条
- **可自动化**: 9 条 (75%)
- **不可自动化**: 2 条 (17%)
- **已实现并通过**: 9 条（含 1 条 Skip）

### 账号分组

| 账号类型 | 邮箱 | 密码 | 用例 |
|---------|------|------|------|
| Pro 账号 | loroxon693@dnsclick.com | Gumtree123! | TC001~TC010 |
| 普通账号 | normal-user@gumtree.com | Gumtree123! | TC011~TC012 |

### 按优先级分布

| 优先级 | 总数 | 可自动化 | 自动化率 | 执行状态 |
|--------|------|---------|---------|---------|
| P0 | 4 | 4 | 100% | ✅ 全部通过 |
| P1 | 6 | 5 | 83% | ✅ 通过 4 / ⏭ Skip 1 |
| P2 | 2 | 0 | 0% | 待人工执行 |

### 覆盖维度

| 测试维度 | 覆盖情况 |
|---------|---------|
| 标签展示（Pro） | ✅ TC001 |
| 统计区四列完整性 | ✅ TC002 |
| 悬浮展开交互 | ✅ TC003 |
| 面板内容正确性 | ✅ TC004 |
| 数值格式与一致性 | ✅ TC005 |
| 鼠标移开关闭面板 | ✅ TC006 |
| 数据刷新提示 | ✅ TC007 |
| 边界值（0值） | ⏭ TC008（Skip，需专用账号） |
| 布局验证 | ✅ TC009（人工） |
| 刷新稳定性 | ✅ TC010（人工） |
| 权限控制（普通账号无统计模块） | ✅ TC011、TC012 |

### ✅ 已确认事项

1. **细分数值与总数关系**：各广告类型 credit 余额与 "Remaining Credit Allowance" 总值**无严格数学关系**，可大于或小于总值，属正常业务逻辑。
2. **面板触发方式**：已确认为**鼠标悬浮**整个模块（非点击 ⓘ 图标），ⓘ 图标已从 UI 中移除。
3. **数据刷新提示文案**：已确认为 `"We refresh the data daily"`。
4. **普通账号行为**：普通账号 `/manage/ads` 页面**完全不显示**统计卡片区，与 Pro 账号使用不同的页面布局。

### ⚠️ 待确认 / 待办事项

1. **TC008 专用账号**：需提供一个余额为零的 Pro 测试账号，以执行零边界值测试。
2. **数据刷新时区**：`"We refresh the data daily"` 以哪个时区为准？是否根据用户时区动态显示？
