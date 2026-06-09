# Gumtree - Watches属性筛选功能测试用例

> **生成时间**: 2026-05-07  
> **测试范围**: Watches 列表页属性筛选功能  
> **总用例数**: 28条  
> **可自动化**: 20条 (71.4%)  
> **手工测试**: 8条 (28.6%)

---

## 测试环境配置(必填)

**请从 `config.yaml` 中选择环境和账号配置**

| 字段 | 值 | 说明 |
|------|-----|------|
| 环境 | zoidberg | 从 `config.yaml` 的 `environment` 和 `urls` 中选择 |
| 基础URL | https://www.zoidberg.gumtree.io | 根据所选环境自动获取 |
| 测试账号类型 | test_account | 从 `config.yaml` 中选择 |
| 测试账号 | runnan.jiao@gumtree.com | 根据所选账号类型自动获取 |
| 测试密码 | Gumtree123! | 根据所选账号类型自动获取 |
| Session命名 | zoidberg_test_account | 格式：{环境}_{账号类型} |

**配置文件路径**: `bundled/skills/gt_autotest_ui_skill/bundled/gt_autotest_ui_gumtree/config/config.yaml`

---

## 📑 目录

- [分组一：Price 筛选器](#分组一price-筛选器)
- [分组二：Condition 筛选器](#分组二condition-筛选器)
- [分组三：Brand 筛选器](#分组三brand-筛选器)
- [分组四：Colour 筛选器](#分组四colour-筛选器)
- [分组五：Seller type 筛选器](#分组五seller-type-筛选器)
- [分组六：组合筛选场景](#分组六组合筛选场景)
- [分组七：异常输入与边界场景](#分组七异常输入与边界场景)
- [分组八：浏览器行为与用户体验](#分组八浏览器行为与用户体验)
- [测试统计](#测试统计)

---

## 测试概述

Watches 列表页提供多维度属性筛选功能,帮助买家快速定位目标商品。核心测试点:
- 价格区间筛选(Price)
- 商品状况筛选(Condition: New/Used)
- 品牌筛选(Brand)
- 颜色筛选(Colour)
- 卖家类型筛选(Seller type: Private/Business)
- 多筛选器组合应用
- 筛选器互斥关闭行为
- URL参数/路径正确性
- Clear all 清除功能

**重要说明(双重动态性)**:
1. 筛选按钮是否渲染取决于当前广告列表中是否有广告填写了对应属性
2. 筛选面板内的选项值由当前广告决定,不硬编码具体选项名
3. 每个测试会先检查筛选按钮是否存在,不存在则跳过(skip)而非失败

**目标页面**: `{base_url}/for-sale/clothing/watches/uk/london`

---

## 分组一:Price 筛选器

### TC001: 打开 Price 筛选器,验证 Min/Max 输入框和 Search 按钮可见

#### 📋 前置条件
- 已访问 Watches 列表页
- Cookie 弹窗已关闭

#### 🎬 执行步骤
1. 检查 Price 筛选按钮是否存在
2. 点击 Price 筛选按钮
3. 验证 Min. 输入框可见
4. 验证 Max. 输入框可见
5. 验证 Search 按钮可见

#### ✅ 预期结果
- Price 筛选面板展开
- Min. 和 Max. 输入框均可见且可编辑
- Search 按钮可见且可点击

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_001

---

### TC002: 输入价格范围 min=10 max=100,点击 Search,URL 包含 min_price 和 max_price 参数

#### 📋 前置条件
- 已访问 Watches 列表页
- Price 筛选按钮存在

#### 🎬 执行步骤
1. 点击 Price 筛选按钮展开面板
2. 在 Min. 输入框中输入 `10`
3. 在 Max. 输入框中输入 `100`
4. 点击 Search 按钮提交筛选
5. 等待页面加载完成
6. 验证 URL 包含 `min_price=10` 和 `max_price=100`
7. 验证页面 H1 标题可见

#### ✅ 预期结果
- URL 同时包含 `min_price=10` 和 `max_price=100`
- 广告列表刷新,仅展示价格在 £10-£100 范围内的商品
- H1 标题可见

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_002

---

### TC003: 仅输入 Min 价格不填 Max,点击 Search,URL 包含 min_price 但不含 max_price

#### 📋 前置条件
- 已访问 Watches 列表页

#### 🎬 执行步骤
1. 展开 Price 面板
2. 在 Min. 输入框中输入 `50`
3. Max. 输入框保持为空
4. 点击 Search 提交筛选
5. 验证 URL 包含 `min_price=50`
6. 验证 URL 不包含 `max_price` 参数

#### ✅ 预期结果
- URL 包含 `min_price=50`
- URL 中不包含 `max_price` 参数
- 广告列表展示价格 ≥ £50 的所有商品(无上限)

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_003

---

### TC004: Price 筛选器展开后,再次点击 Price 按钮,面板应收起

#### 📋 前置条件
- 已访问 Watches 列表页

#### 🎬 执行步骤
1. 点击 Price 按钮展开面板
2. 验证 Min. 输入框可见(确认面板已展开)
3. 再次点击 Price 按钮
4. 验证 Min. 输入框不可见(确认面板已收起)

#### ✅ 预期结果
- 面板表现为 toggle 开关行为
- 第二次点击后面板完全收起

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 交互测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_004

---

## 分组二:Condition 筛选器

### TC005: 打开 Condition 筛选器,验证面板展开并含操作按钮,记录当前可用选项

#### 📋 前置条件
- Condition 筛选按钮存在(如不存在说明无广告含该属性,测试跳过)

#### 🎬 执行步骤
1. 检查 Condition 筛选按钮是否存在
2. 点击 Condition 筛选按钮展开面板
3. 验证 Clear all 按钮可见
4. 验证 Search 按钮可见
5. 记录当前可用选项(动态,通常为 New/Used)

#### ✅ 预期结果
- Condition 筛选面板展开
- Clear all 和 Search 按钮可见
- 面板内展示条件选项(数量和内容取决于当前广告数据)

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_005

---

### TC006: 点击第一个可用 Condition 选项,验证 URL 包含 common_for_sale_condition 参数

#### 📋 前置条件
- Condition 筛选按钮存在
- 面板内至少有一个可用选项

#### 🎬 执行步骤
1. 展开 Condition 面板
2. 动态获取第一个可用选项(如无选项则跳过)
3. 记录选项的 href 中的条件值
4. 点击该选项(选中复选框)
5. 点击 Search 提交筛选
6. 验证 URL 包含 `common_for_sale_condition=` 参数
7. 验证 H1 标题可见

#### ✅ 预期结果
- URL 包含 `common_for_sale_condition=` 参数(值如 new/used)
- 广告列表刷新,仅展示该条件的商品
- H1 标题可见

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_006

---

### TC007: 选中某 Condition 选项后,点击 Clear all,筛选参数从 URL 中清除

#### 📋 前置条件
- 已按 TC006 选中某条件并提交筛选
- URL 包含 `common_for_sale_condition=` 参数

#### 🎬 执行步骤
1. 重新展开 Condition 面板
2. 点击 Clear all 按钮
3. 验证 URL 不再包含 `common_for_sale_condition=` 参数
4. 验证广告列表展示所有条件的商品

#### ✅ 预期结果
- `common_for_sale_condition=` 参数从 URL 中移除
- 广告列表恢复展示所有条件
- 筛选面板仍保持展开状态

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_007

---

### TC008: Condition 面板各选项的 href 格式校验

#### 📋 前置条件
- Condition 面板已展开
- 面板内有可用选项

#### 🎬 执行步骤
1. 遍历所有可见的 Condition 选项
2. 读取每个选项的 href 属性
3. 验证 href 包含 `common_for_sale_condition=` 参数

#### ✅ 预期结果
- 所有 Condition 选项的 href 都包含正确的参数格式
- 参数值符合预期(如 new、used 等)

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 数据验证
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_008

---

## 分组三:Brand 筛选器

### TC009: 打开 Brand 筛选器,验证面板展开并含操作按钮,记录当前可用品牌

#### 📋 前置条件
- Brand 筛选按钮存在(如不存在说明无广告含品牌属性,测试跳过)

#### 🎬 执行步骤
1. 检查 Brand 筛选按钮是否存在
2. 点击 Brand 筛选按钮展开面板
3. 验证 Clear all 按钮可见
4. 验证 Search 按钮可见
5. 记录当前可用品牌选项(动态)

#### ✅ 预期结果
- Brand 筛选面板展开
- Clear all 和 Search 按钮可见
- 面板内展示品牌选项(数量和内容取决于当前广告数据)

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_009

---

### TC010: 点击第一个可用 Brand 选项,验证 URL 包含 fashion_brand 参数

#### 📋 前置条件
- Brand 筛选按钮存在
- 面板内至少有一个可用品牌选项

#### 🎬 执行步骤
1. 展开 Brand 面板
2. 动态获取第一个可用品牌选项
3. 记录选项的 href 中的品牌值
4. 点击该品牌选项
5. 点击 Search 提交筛选
6. 验证 URL 包含 `fashion_brand=` 参数
7. 验证 H1 标题可见

#### ✅ 预期结果
- URL 包含 `fashion_brand=` 参数
- 广告列表刷新,仅展示该品牌的商品
- H1 标题更新(可能包含品牌名)

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_010

---

### TC011: Brand 筛选器展开时,切换到 Condition 筛选器,Brand 面板自动收起

#### 📋 前置条件
- Brand 和 Condition 筛选按钮均存在

#### 🎬 执行步骤
1. 点击 Brand 按钮展开面板
2. 验证 Brand 面板可见
3. 点击 Condition 按钮
4. 验证 Condition 面板展开
5. 验证 Brand 面板已自动收起(互斥行为)

#### ✅ 预期结果
- 同一时刻只能有一个筛选面板展开
- 切换筛选器时,之前展开的面板自动收起

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 交互测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_011

---

## 分组四:Colour 筛选器

### TC012: 打开 Colour 筛选器,验证面板展开并含操作按钮,记录当前可用颜色选项

#### 📋 前置条件
- Colour 筛选按钮存在(如不存在说明无广告含颜色属性,测试跳过)

#### 🎬 执行步骤
1. 检查 Colour 筛选按钮是否存在
2. 点击 Colour 筛选按钮展开面板
3. 验证 Clear all 按钮可见
4. 验证 Search 按钮可见
5. 记录当前可用颜色选项(动态)

#### ✅ 预期结果
- Colour 筛选面板展开
- Clear all 和 Search 按钮可见
- 面板内展示颜色选项(数量和内容取决于当前广告数据)

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_012

---

### TC013: 点击第一个可用 Colour 选项,验证 URL 包含 common_for_sale_colour 参数

#### 📋 前置条件
- Colour 筛选按钮存在
- 面板内至少有一个可用颜色选项

#### 🎬 执行步骤
1. 展开 Colour 面板
2. 动态获取第一个可用颜色选项
3. 记录选项的 href 中的颜色值
4. 点击该颜色选项
5. 点击 Search 提交筛选
6. 验证 URL 包含 `common_for_sale_colour=` 参数
7. 验证 H1 标题可见

#### ✅ 预期结果
- URL 包含 `common_for_sale_colour=` 参数
- 广告列表刷新,仅展示该颜色的商品
- H1 标题可见

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_013

---

### TC014: Colour 面板各选项的 href 格式校验

#### 📋 前置条件
- Colour 面板已展开
- 面板内有可用选项

#### 🎬 执行步骤
1. 遍历所有可见的 Colour 选项
2. 读取每个选项的 href 属性
3. 验证 href 包含 `common_for_sale_colour=` 参数

#### ✅ 预期结果
- 所有 Colour 选项的 href 都包含正确的参数格式
- 参数值符合预期的颜色编码

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 数据验证
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_014

---

## 分组五:Seller type 筛选器

### TC015: 打开 Seller type 筛选器,验证面板展开并含操作按钮,记录当前可用选项

#### 📋 前置条件
- Seller type 筛选按钮存在

#### 🎬 执行步骤
1. 检查 Seller type 筛选按钮是否存在
2. 点击 Seller type 筛选按钮展开面板
3. 验证 Clear all 按钮可见
4. 验证 Search 按钮可见
5. 记录当前可用选项(通常为 Private/Business)

#### ✅ 预期结果
- Seller type 筛选面板展开
- Clear all 和 Search 按钮可见
- 面板内展示卖家类型选项

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_015

---

### TC016: 若 Private 选项存在,点击后验证 URL path 包含 /private/

#### 📋 前置条件
- Seller type 面板中 Private 选项存在

#### 🎬 执行步骤
1. 展开 Seller type 面板
2. 点击 Private 选项
3. 点击 Search 提交筛选
4. 验证 URL path 包含 `/private/` 路径段

#### ✅ 预期结果
- URL 从 `/watches/uk/london` 变为 `/watches/private/uk/london`
- 广告列表仅展示私人卖家的商品

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_016

---

### TC017: 若 Private 选项存在,点击后验证 URL 包含 seller_type=private

#### 📋 前置条件
- Seller type 面板中 Private 选项存在

#### 🎬 执行步骤
1. 展开 Seller type 面板
2. 点击 Private 选项
3. 点击 Search 提交筛选
4. 验证 URL 包含 `seller_type=private` 参数

#### ✅ 预期结果
- URL 包含 `seller_type=private` 参数(或使用路径模式)
- 筛选结果符合预期

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_017

---

### TC018: 若 Business 选项存在,点击后验证 URL path 包含 /trade/

#### 📋 前置条件
- Seller type 面板中 Business 选项存在

#### 🎬 执行步骤
1. 展开 Seller type 面板
2. 点击 Business 选项
3. 点击 Search 提交筛选
4. 验证 URL path 包含 `/trade/` 路径段

#### ✅ 预期结果
- URL 从 `/watches/uk/london` 变为 `/watches/trade/uk/london`
- 广告列表仅展示商家卖家的商品

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_018

---

### TC019: 选中某 Seller type 选项后,点击 Clear all,URL 中 seller type 路径消失

#### 📋 前置条件
- 已选中某 Seller type 并提交筛选
- URL path 包含 seller type 路径段(如 /private/ 或 /trade/)

#### 🎬 执行步骤
1. 重新展开 Seller type 面板
2. 点击 Clear all 按钮
3. 验证 URL path 不再包含 seller type 路径段
4. 验证广告列表展示所有卖家类型

#### ✅ 预期结果
- URL 回到基础路径(移除 /private/ 或 /trade/)
- 广告列表恢复展示所有卖家类型
- 筛选面板仍保持展开状态

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_019

---

## 分组六:组合筛选场景

### TC020: 同时应用 Condition 和 Seller type 两个筛选,验证两个参数均生效

#### 📋 前置条件
- Condition 和 Seller type 筛选按钮均存在
- 两个面板内均有可用选项

#### 🎬 执行步骤
1. 展开 Condition 面板,选中第一个选项,点击 Search
2. 展开 Seller type 面板,选中第一个选项,点击 Search
3. 验证 URL 同时包含两个筛选参数
4. 验证广告列表同时满足两个筛选条件

#### ✅ 预期结果
- URL 同时包含 `common_for_sale_condition=` 和 seller type 相关参数
- 广告列表同时满足两个筛选条件
- 两个筛选器可以叠加使用

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_FILTER_020

---

## 分组七:异常输入与边界场景

### TC021: Price 输入超大数值(如99999999),验证系统处理能力

#### 📋 前置条件
- Price 筛选按钮存在

#### 🎬 执行步骤
1. 展开 Price 面板
2. 在 Max. 输入框中输入超大数值 `99999999`
3. 点击 Search 按钮
4. 观察系统响应

#### ✅ 预期结果
- 系统应正常处理(返回零结果或所有结果)
- 不应出现系统错误或页面崩溃
- 如有上限限制,应提示用户"价格不能超过X"

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ❌ 暂不自动化(需要验证系统对极端值的处理能力)

---

### TC022: 多个筛选器快速连续切换,验证系统稳定性

#### 📋 前置条件
- 所有筛选按钮存在

#### 🎬 执行步骤
1. 快速依次展开 Price、Condition、Brand、Colour、Seller type 筛选器(不关闭前一个)
2. 观察页面渲染情况
3. 尝试在不同筛选器面板中快速点击选项
4. 观察是否出现面板叠加、错位或其他UI问题

#### ✅ 预期结果
- 所有筛选器面板应正确展开/收起(互斥或叠加根据设计而定)
- 页面不应出现布局错乱
- 点击选项时不应出现延迟或无响应
- 不应出现JavaScript错误

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 性能/并发测试
- **UI自动化**: ❌ 暂不自动化(需要人工观察UI渲染和交互流畅度)

---

### TC023: 同时应用所有筛选器,验证URL参数正确性和结果准确性

#### 📋 前置条件
- 所有筛选器按钮存在且有可用选项

#### 🎬 执行步骤
1. 依次应用 Price(Min=10 Max=100)、Condition(New)、Brand(第一个)、Colour(第一个)、Seller type(Private)
2. 提交每个筛选后,检查URL
3. 检查最终广告列表

#### ✅ 预期结果
- URL 包含所有筛选参数,格式正确
- 广告列表同时满足所有筛选条件
- 页面顶部应显示多个筛选 Tag
- 筛选器面板应正确回显已选状态

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 集成测试
- **UI自动化**: ❌ 暂不自动化(需要验证复杂组合下的数据准确性)

---

### TC024: Seller type筛选后点击广告进入详情页,返回时筛选状态保持

#### 📋 前置条件
- 已应用 Seller type 筛选(如 Private)

#### 🎬 执行步骤
1. 应用 Seller type=Private 筛选
2. 点击列表中的某个广告,进入广告详情页
3. 点击浏览器后退按钮,返回列表页
4. 检查筛选器状态

#### ✅ 预期结果
- 返回列表页后,Seller type 筛选仍生效
- URL 中 `seller_type=private` 参数仍存在
- 广告列表仍展示筛选后的结果
- 筛选 Tag 仍然显示

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 导航测试
- **UI自动化**: ❌ 暂不自动化(需要验证跨页面导航后的状态保持)

---

## 分组八:浏览器行为与用户体验

### TC025: 使用浏览器前进按钮,验证筛选状态正确前进

#### 📋 前置条件
- 已按TC018完成后退操作

#### 🎬 执行步骤
1. 从初始状态依次应用 Condition、Brand 筛选
2. 点击两次后退按钮,回到初始状态
3. 点击一次前进按钮
4. 再次点击前进按钮

#### ✅ 预期结果
- 第一次前进: 恢复 Condition 筛选
- 第二次前进: 恢复 Condition + Brand 筛选
- 每次前进后 URL 和广告列表应与之前一致

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 浏览器兼容性测试
- **UI自动化**: ❌ 暂不自动化(需要验证浏览器历史栈管理)

---

### TC026: 移动端视图下筛选器的响应式布局和交互

#### 📋 前置条件
- 使用移动端设备或浏览器开发者工具切换到移动端视图(如 iPhone 12)

#### 🎬 执行步骤
1. 访问 Watches 列表页
2. 观察筛选器按钮的布局(是否收起为汉堡菜单或保持可见)
3. 尝试展开筛选器面板,观察面板是否覆盖全屏或以抽屉形式展开
4. 尝试应用筛选并提交
5. 检查移动端下的交互流畅度

#### ✅ 预期结果
- 筛选器在移动端应有适配的布局(不应横向溢出或错位)
- 筛选面板应易于操作(按钮足够大,间距合理)
- 所有功能在移动端应正常工作
- 页面滚动和交互应流畅

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 响应式测试
- **UI自动化**: ❌ 暂不自动化(需要在真实设备上测试触摸交互)

---

### TC027: 筛选器面板展开时滚动页面,验证面板位置锁定或跟随

#### 📋 前置条件
- Price 筛选器已展开

#### 🎬 执行步骤
1. 展开 Price 筛选器面板
2. 向下滚动页面
3. 观察 Price 筛选器面板的行为

#### ✅ 预期结果
- 选项A: 面板保持在视口可见区域(sticky定位)
- 选项B: 面板跟随滚动(相对定位)
- 选项C: 滚动时面板自动关闭
- 无论哪种方案,都应有良好的用户体验,不应出现面板丢失或错位

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UX测试
- **UI自动化**: ❌ 暂不自动化(需要人工评估滚动交互的用户体验)

---

### TC028: 清除所有筛选器后,验证页面性能和加载时间

#### 📋 前置条件
- 已应用多个筛选条件

#### 🎬 执行步骤
1. 应用 5 个筛选器(Price、Condition、Brand、Colour、Seller type)
2. 点击页面上的全局 Clear All 或逐个清除筛选 Tag
3. 使用浏览器开发者工具测量页面加载时间
4. 观察广告列表恢复速度

#### ✅ 预期结果
- 清除筛选后页面应在 2 秒内完成加载(含广告列表刷新)
- 不应出现明显的白屏或卡顿
- 广告列表应平滑过渡到全量展示

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 性能测试
- **UI自动化**: ❌ 暂不自动化(需要人工测量和评估页面性能)

---

## 测试统计

### 按优先级统计

| 优先级 | 用例数量 | 占比 |
|--------|---------|------|
| P0 | 1 | 3.6% |
| P1 | 18 | 64.3% |
| P2 | 9 | 32.1% |
| **总计** | **28** | **100%** |

### 按测试类型统计

| 测试类型 | 用例数量 | 占比 |
|---------|---------|------|
| 功能测试 | 16 | 57.1% |
| 交互测试 | 2 | 7.1% |
| 数据验证 | 2 | 7.1% |
| 边界测试 | 1 | 3.6% |
| 性能/并发测试 | 2 | 7.1% |
| 集成测试 | 1 | 3.6% |
| 导航测试 | 1 | 3.6% |
| 浏览器兼容性测试 | 1 | 3.6% |
| 响应式测试 | 1 | 3.6% |
| UX测试 | 1 | 3.6% |
| **总计** | **28** | **100%** |

### 按筛选器分组统计

| 筛选器 | 用例数量 | 包含功能 |
|--------|---------|---------|
| Price | 4 | 面板展开、价格区间筛选、单边筛选、面板收起 |
| Condition | 4 | 面板展开、选项选择、Clear all 清除、href 格式校验 |
| Brand | 3 | 面板展开、品牌选择、面板互斥关闭 |
| Colour | 3 | 面板展开、颜色选择、href 格式校验 |
| Seller type | 5 | 面板展开、Private 筛选、Business 筛选、Clear all 清除(路径+参数) |
| 组合筛选 | 1 | 多筛选器同时应用 |
| 异常输入与边界场景 | 4 | 超大数值、快速切换、全筛选器组合、跨页面状态保持 |
| 浏览器行为与UX | 4 | 前进按钮、移动端响应式、滚动交互、性能测试 |
| **总计** | **28** | - |

### 自动化覆盖率

| 项目 | 数量 |
|------|------|
| 总用例数 | 28 |
| 可自动化用例 | 20 |
| 手工测试用例 | 8 |
| 自动化覆盖率 | 71.4% |

**手工测试场景说明**:  
TC021-TC028 为手工测试场景,主要覆盖:
- 异常输入和边界值验证
- 多筛选器快速切换的并发稳定性
- 复杂组合筛选的数据准确性
- 跨页面导航后的状态保持
- 浏览器前进/后退按钮行为
- 移动端响应式布局和触摸交互
- 滚动交互的用户体验
- 页面性能和加载时间

这些场景需要人工观察和判断,暂不纳入自动化测试范围。

---

## 附录

### 筛选器 URL 参数一览

| 筛选器 | URL 参数/路径 | 说明 |
|--------|--------------|------|
| Price | `min_price=X&max_price=Y` | 文本输入,无 Clear all |
| Condition | `common_for_sale_condition=new/used` | 有 Clear all |
| Brand | `fashion_brand=X` | 有 Clear all |
| Colour | `common_for_sale_colour=X` | 有 Clear all |
| Seller type | `/private/` 或 `/trade/` 路径 + `seller_type=` 参数 | 有 Clear all,支持路径和参数两种模式 |

### 动态性特征说明

**双重动态性**是本测试套件的核心特征:

1. **筛选按钮动态渲染**
   - 筛选按钮是否出现取决于当前广告列表数据
   - 若所有广告均未填写某属性,则该筛选按钮不会渲染

2. **筛选选项动态生成**
   - 面板内的具体选项值完全由当前广告数据决定
   - 测试不硬编码任何具体选项名称

3. **Skip 场景**
   - 筛选按钮不存在 → skip(属性在当前环境完全缺失)
   - 筛选按钮存在但面板内无可用选项 → skip(按钮存在但无匹配广告)

### 测试脚本路径

- **自动化脚本**: `bundled/skills/gt_autotest_ui_skill/bundled/gt_autotest_ui_gumtree/test_cases/buyer/test_buyer_watches_attribute_filters.py`
- **文本用例**: `bundled/knowledge_base/文本用例/buyer_filters/TC_Watches_Attribute_Filters测试用例.md`

### 运行命令

```bash
# 基础运行
pytest test_cases/buyer/test_buyer_watches_attribute_filters.py --env=zoidberg

# 详细模式 + 有头浏览器
pytest test_cases/buyer/test_buyer_watches_attribute_filters.py --env=zoidberg --probe-headed -v
```
