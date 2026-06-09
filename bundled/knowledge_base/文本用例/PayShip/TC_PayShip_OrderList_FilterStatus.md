# TC_PayShip_OrderList_FilterStatus — 订单列表状态筛选

> 探测日期：2026-05-11  
> 探测方式：Playwright MCP 实测  
> 探测状态：✅ 全部实测完成

---

## 测试环境配置

```
站点：gaga（https://gaga.gumtree.io）
买家账号：gtauto25858@outlook.com / autoGt5858!
卖家账号：gtauto5858@outlook.com / autoGt5858!
目标页面：/manage/orders?type=bought（买家）/ /manage/orders?type=sold（卖家）
```

---

## Application Overview

**功能定位**：订单列表页支持按状态筛选，帮助用户快速定位特定阶段的订单。

**筛选下拉选项（两端相同）**：All / In progress / Completed / Cancelled / Suspended

**页面状态**：
- 有数据态：列表展示订单卡片，每张卡片显示订单状态标签
- 空状态：筛选结果为空时显示"No orders yet"图标+文案
- 分页态：订单数量超过10条时显示分页导航

**URL 参数规律**：
- 切换筛选后 URL 自动更新，格式为 `?type=bought&filter=inprogress`
- filter 参数取值：`all` / `inprogress` / `completed` / `cancelled` / `suspended`

---

## 业务规则（筛选逻辑）

| 筛选项 | 应召回的订单状态 | 不允许出现的状态 |
|--------|----------------|----------------|
| All | 全部状态（不过滤） | — |
| In progress | Awaiting dispatch、On its way、Delivered、Arrived at pick-up point、Picked up | 其他任何状态 |
| Completed | Completed | 其他任何状态 |
| Suspended | Suspended | 其他任何状态 |
| Cancelled | Cancelled、Closed | 其他任何状态 |

> 注：测试环境不一定存在所有状态的订单，筛选结果为空也是合法的。

---

## 模块一：买家侧 Bought 订单列表筛选

**账号**：gtauto25858@outlook.com  
**页面**：`/manage/orders?type=bought`

### TC-BUY-F01：All 筛选

- **前置**：买家已登录，进入 Bought 列表，筛选器选择 All
- **操作**：查看列表显示的订单状态标签
- **预期**：同时包含多种状态的订单（无过滤）
- **✅ 实测结果**：页面第1页包含以下状态：
  - `Completed`（订单 13752918）
  - `In progress | Awaiting dispatch`（订单 13752868、13752368）
  - `Cancelled`（订单 13752668、13752618、13752568、13752518、13752468、13752418、13752218）
- **实测结论**：✅ All 筛选正确召回全部状态订单，无异常状态出现

---

### TC-BUY-F02：In progress 筛选

- **前置**：买家已登录，进入 Bought 列表
- **操作**：下拉框选择"In progress"，URL 变为 `?type=bought&filter=inprogress`
- **预期**：仅显示 Awaiting dispatch / On its way / Delivered / Arrived at pick-up point / Picked up 状态订单，不允许出现其他状态
- **✅ 实测结果**：
  - 召回状态（去重）：`In progress | Awaiting dispatch`
  - 无分页（当前数据量不超过1页）
  - 未出现 Completed、Cancelled 等非预期状态
- **实测结论**：✅ In progress 筛选正确，仅召回 Awaiting dispatch 状态订单

---

### TC-BUY-F03：Completed 筛选

- **前置**：买家已登录，进入 Bought 列表
- **操作**：下拉框选择"Completed"，URL 变为 `?type=bought&filter=completed`
- **预期**：仅显示 Completed 状态订单（或空列表）
- **✅ 实测结果**：
  - 召回状态（去重）：`Completed`
  - 未出现其他状态
- **实测结论**：✅ Completed 筛选正确，仅召回 Completed 状态订单

---

### TC-BUY-F04：Cancelled 筛选

- **前置**：买家已登录，进入 Bought 列表
- **操作**：下拉框选择"Cancelled"，URL 变为 `?type=bought&filter=cancelled`
- **预期**：仅显示 Cancelled 和/或 Closed 状态订单，不允许出现其他状态
- **✅ 实测结果**：
  - 召回状态（去重）：`Cancelled`
  - 未出现 Closed（测试环境无此状态，符合预期）
  - 未出现 Completed、In progress 等非预期状态
- **实测结论**：✅ Cancelled 筛选正确，仅召回 Cancelled 状态订单

---

### TC-BUY-F05：Suspended 筛选

- **前置**：买家已登录，进入 Bought 列表
- **操作**：下拉框选择"Suspended"，URL 变为 `?type=bought&filter=suspended`
- **预期**：仅显示 Suspended 状态订单（测试环境可能为空）
- **✅ 实测结果**：
  - 页面显示"No orders yet"空状态
  - 未出现其他状态订单
- **实测结论**：✅ Suspended 筛选正确，测试环境无 Suspended 订单，空列表符合预期

---

## 模块二：卖家侧 Sold 订单列表筛选

**账号**：gtauto5858@outlook.com  
**页面**：`/manage/orders?type=sold`

### TC-SEL-F01：All 筛选

- **前置**：卖家已登录，进入 Sold 列表，筛选器选择 All
- **操作**：查看列表显示的订单状态标签
- **预期**：同时包含多种状态的订单（无过滤）
- **✅ 实测结果**：第1页包含：
  - `Completed`（订单 13752918）
  - `In progress | Awaiting dispatch`（订单 13752868、13752368）
  - `Cancelled`（13752668、13752618、13752568、13752518、13752468、13752418、13752218 等）
  - 总计多页（至少4页以上）
- **实测结论**：✅ All 筛选正确召回全部状态订单

---

### TC-SEL-F02：In progress 筛选

- **前置**：卖家已登录，进入 Sold 列表
- **操作**：下拉框选择"In progress"，URL 变为 `?type=sold&filter=inprogress`
- **预期**：仅显示进行中状态（Awaiting dispatch 等）订单
- **✅ 实测结果**：
  - 召回状态（去重）：`In progress | Awaiting dispatch`
  - 无分页（当前数据量不超过1页）
  - 未出现 Completed、Cancelled 等非预期状态
- **实测结论**：✅ In progress 筛选正确，仅召回 Awaiting dispatch 状态订单

---

### TC-SEL-F03：Completed 筛选

- **前置**：卖家已登录，进入 Sold 列表
- **操作**：下拉框选择"Completed"，URL 变为 `?type=sold&filter=completed`
- **预期**：仅显示 Completed 状态订单（或空列表）
- **✅ 实测结果**：
  - 召回状态（去重）：`Completed`
  - 未出现其他状态
- **实测结论**：✅ Completed 筛选正确，仅召回 Completed 状态订单

---

### TC-SEL-F04：Cancelled 筛选

- **前置**：卖家已登录，进入 Sold 列表
- **操作**：下拉框选择"Cancelled"，URL 变为 `?type=sold&filter=cancelled`
- **预期**：仅显示 Cancelled 和/或 Closed 状态订单
- **✅ 实测结果（第1页+第2页）**：
  - 召回状态（去重）：`Cancelled`
  - 未出现 Closed（测试环境无此状态，符合预期）
  - 未出现 Completed、In progress 等非预期状态
- **实测结论**：✅ Cancelled 筛选正确，仅召回 Cancelled 状态订单

---

### TC-SEL-F05：Suspended 筛选

- **前置**：卖家已登录，进入 Sold 列表
- **操作**：下拉框选择"Suspended"，URL 变为 `?type=sold&filter=suspended`
- **预期**：仅显示 Suspended 状态订单（测试环境可能为空）
- **✅ 实测结果**：
  - 页面显示"No orders yet"空状态
  - 未出现其他状态订单
- **实测结论**：✅ Suspended 筛选正确，测试环境无 Suspended 订单，空列表符合预期

---

## 汇总结论

| 筛选项 | 买家 Bought | 卖家 Sold | 结果 |
|--------|-----------|----------|------|
| All | 含 Completed、In progress、Cancelled | 含 Completed、In progress、Cancelled | ✅ 通过 |
| In progress | 仅 In progress \| Awaiting dispatch | 仅 In progress \| Awaiting dispatch | ✅ 通过 |
| Completed | 仅 Completed | 仅 Completed | ✅ 通过 |
| Cancelled | 仅 Cancelled（无 Closed，符合预期） | 仅 Cancelled（无 Closed，符合预期） | ✅ 通过 |
| Suspended | 空列表（无此状态订单，符合预期） | 空列表（无此状态订单，符合预期） | ✅ 通过 |

**整体结论**：✅ 买家和卖家订单列表的5个状态筛选项全部行为符合预期，无 Bug。

---

## 附：UI 交互细节（实测确认）

1. **URL 联动**：切换筛选后 URL 自动更新（filter 参数），支持分享/书签
2. **状态标签格式**：进行中订单显示为 "In progress | Awaiting dispatch"，包含大类和子状态
3. **空状态**：无匹配订单时显示图标 + "No orders yet" + 说明文案，买家和卖家文案略有差异
   - 买家空状态文案：`Once you've bought something, your orders will show up here`
   - 卖家空状态文案：`Once you've sold something, your orders will show up here`
4. **分页**：All/Cancelled 筛选下有多页，筛选后当前页重置为第1页
