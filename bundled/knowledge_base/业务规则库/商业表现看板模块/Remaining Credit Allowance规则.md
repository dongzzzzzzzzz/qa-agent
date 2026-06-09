# 商业表现看板模块 - Remaining Credit Allowance 业务规则

## 1. 功能概述
- **功能描述**: Remaining Credit Allowance 是 Manage My Ads 页面统计卡片区中面向 Pro Account 卖家展示的 credit 余额汇总模块，提供账号当前剩余广告投放 credit 总量，并支持悬浮查看各广告类型的 credit 余额明细面板
- **用户角色**: 仅 Pro Account 卖家可见；普通账号（Normal Account）不显示任何统计卡片区（与 Pro 页面使用完全不同的布局）
- **入口位置**: Manage My Ads 页面（`/manage/ads`）顶部统计卡片区第四列
- **依赖模块**:
  - 用户认证模块（Pro 账号权限验证）
  - Credit 管理模块（Remaining Credit Allowance 数据源）
  - 广告管理模块（统计卡片区其他列数据来源）

## 2. 核心流程

### 2.1 主流程
1. Pro Account 卖家登录并进入 `/manage/ads` 页面
2. 页面顶部统计卡片区展示四列：Live Ads / Search Impressions / Unique Replies / Remaining Credit Allowance
3. 卖家将鼠标悬浮（hover）在 Remaining Credit Allowance 模块上
4. 系统展开 credit 余额明细面板，显示各广告类型的余额明细
5. 卖家查看细分余额后，将鼠标移至其他区域
6. 明细面板自动收起

### 2.2 异常流程
- **普通账号访问**：普通账号 Manage My Ads 页面不显示任何统计卡片区，整体布局与 Pro 账号不同，无 Remaining Credit Allowance 模块
- **余额为零**：统计区显示数字 `0`（非空白、非"-"），悬浮后面板正常展开，各广告类型余额均显示 `0`（需专用零额度 Pro 账号验证）
- **面板误触导航**：关闭面板时禁止点击操作，应使用 `Escape` 键或将鼠标移至安全坐标，防止误触链接导致页面跳转

## 3. 业务规则

### 3.1 输入规则（统计区数据展示）
| 字段 | 类型 | 必填 | 格式 | 默认值 | 说明 |
|-----|------|-----|------|--------|------|
| remaining_credit_allowance | Integer | 是 | 非负整数（≥ 0） | - | 账号当前剩余 credit 总量，不允许负数、小数、"-"、"N/A" |
| credit_details | Array | 是 | 广告类型名称 + 余额数值 | - | 各广告类型的 credit 余额明细，行数因账号而异 |

### 3.2 校验规则
- 统计区数值必须为**非负整数**（≥ 0），不允许出现负数、小数、"-"、"N/A" 等异常格式
- 明细面板中各细分广告类型余额数值与 Remaining Credit Allowance 总值**无严格数学关系**（细分值可大于或小于总值），属正常业务逻辑
- 明细面板顶部描述文字必须包含 **"The balance shows"**
- 数据刷新提示文案为 **`"We refresh the data daily"`**（非原 Figma 设计文案 `"We update the data every morning at 8 a.m."`）

### 3.3 权限规则
| 规则项 | 规则内容 |
|-------|---------|
| 模块可见性 | Remaining Credit Allowance 统计卡片及明细面板仅 Pro Account 可见 |
| 普通账号页面布局 | 普通账号 Manage My Ads 页面完全不显示统计卡片区（无 Live Ads、Search Impressions、Unique Replies、Remaining Credit Allowance 四列） |
| 访问拦截 | 普通账号无法触发 Remaining Credit Allowance 相关 UI 元素 |

### 3.4 业务约束
- **统计区四列固定顺序**：Live Ads → Search Impressions → Unique Replies → Remaining Credit Allowance，列序不可变
- **四列等宽布局**：统计卡片区四列等宽均分显示，各列之间有视觉分隔（需人工视觉验证）
- **悬浮触发方式**：明细面板通过鼠标悬浮整个 Remaining Credit Allowance 模块触发，无需点击；与原 Figma 设计（点击 ⓘ 图标触发）存在实现差异，ⓘ 图标已从 UI 中移除
- **面板关闭方式**：鼠标移开后明细面板自动收起；操作时禁止使用点击关闭（防止误触链接），应使用 `Escape` 键或移动鼠标至安全坐标
- **数据刷新频率**：数据每天刷新一次，非实时数据
- **数据一致性**：页面刷新后，Remaining Credit Allowance 数值应保持一致（数据源更新时间点前后刷新除外）

### 3.5 设计实现差异（与 Figma 的已确认差异）
| 差异项 | Figma 设计 | 实际实现 |
|-------|-----------|---------|
| 面板触发方式 | 点击 ⓘ 图标 | 鼠标悬浮整个模块，ⓘ 图标已移除 |
| 面板关闭方式 | 点击外部区域关闭 | 鼠标移开后自动关闭 |
| 数据刷新提示文案 | `"We update the data every morning at 8 a.m., but sometimes it may be delayed."` | `"We refresh the data daily"` |
| 统计区列数 | 3 列（Live Ads / Ad views / Total Replies） | 4 列（Live Ads / Search Impressions / Unique Replies / Remaining Credit Allowance） |
| 模块名称 | Total Replies | Remaining Credit Allowance |
| 普通账号行为 | 仅隐藏 ⓘ 图标 | 完全不显示任何统计卡片 |

## 4. 错误处理
| 错误场景 | 错误信息 | 触发条件 | 用户提示 |
|---------|---------|---------|---------|
| 普通账号访问 | 无权限 | 普通账号进入 `/manage/ads` | 不显示统计卡片区（整体页面布局不同），无报错提示 |
| 余额为零 | - | Pro 账号余额归零 | 统计区显示 `0`，明细面板正常展开显示各广告类型余额均为 `0` |
| 面板误触导航 | - | 关闭面板操作不当时点击链接 | 不应发生，通过使用 `Escape` 键或安全坐标移动预防 |

## 5. 已知问题
- **TC008 专用账号待提供**：余额为零的边界值测试（TC008）需要专用零额度 Pro 测试账号，当前已跳过（Skip），待账号提供后执行
- **数据刷新时区待确认**：`"We refresh the data daily"` 以哪个时区为准？是否根据用户时区动态显示？

## 6. 变更历史
| 日期 | 版本 | 变更内容 | 变更人 |
|-----|------|---------|--------|
| 2026-04-15 | v1.0 | 基于 TC_total_replies.md（12条测试用例）提取初始业务规则；涵盖权限规则、悬浮交互规则、数据格式规则、设计实现差异等 | AI Agent |
