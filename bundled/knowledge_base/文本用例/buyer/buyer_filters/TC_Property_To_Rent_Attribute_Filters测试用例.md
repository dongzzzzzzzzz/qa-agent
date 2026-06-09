# Gumtree - Property to Rent属性筛选功能测试用例

> **生成时间**: 2026-05-07  
> **测试范围**: Property to Rent 列表页属性筛选功能  
> **总用例数**: 25条  
> **可自动化**: 18条 (72.0%)  
> **手工测试**: 7条 (28.0%)

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

- [分组一：Rent (pw) 筛选器](#分组一rent-pw-筛选器)
- [分组二：Property type 筛选器](#分组二property-type-筛选器)
- [分组三：Number of bedrooms 筛选器](#分组三number-of-bedrooms-筛选器)
- [分组四：Seller type 筛选器](#分组四seller-type-筛选器)
- [分组五：组合筛选场景](#分组五组合筛选场景)
- [分组六：异常输入与边界场景](#分组六异常输入与边界场景)
- [分组七：浏览器行为与用户体验](#分组七浏览器行为与用户体验)
- [测试统计](#测试统计)

---

## 测试概述

Property to Rent 列表页提供租房筛选功能,帮助租客快速定位目标房源。核心测试点:
- 周租金筛选(Rent pw: Min/Max)
- 房产类型筛选(Property type: Flat/House等)
- 卧室数量筛选(Number of bedrooms: Min/Max)
- 卖家类型筛选(Seller type: Agency/Private)
- 筛选器展开/收起交互
- URL参数正确性
- Clear all 清除功能
- 多筛选器叠加应用

**重要说明**:
1. URL 中必须携带 `gt_gb_exp_ovr=Mul-M:B` 实验参数,用于启用多选筛选器行为
2. 筛选器行为具有双重动态性(同 Watches 页):筛选按钮是否渲染取决于广告数据,选项值也由当前广告决定
3. 每个测试会先检查筛选按钮是否存在,不存在则跳过(skip)而非失败

**目标页面**: `{base_url}/flats-houses/property-to-rent/uk/london?gt_gb_exp_ovr=Mul-M:B`

---

## 分组一:Rent (pw) 筛选器

### TC001: 打开 Rent (pw) 筛选器,验证 Min/Max 输入框和 Search 按钮可见

#### 📋 前置条件
- 已访问 Property to Rent 列表页(含实验参数)
- Cookie 弹窗已关闭
- Rent (pw) 筛选按钮存在

#### 🎬 执行步骤
1. 检查 Rent (pw) 筛选按钮是否存在
2. 点击 Rent (pw) 筛选按钮
3. 验证 Min. 输入框可见
4. 验证 Max. 输入框可见
5. 验证 Search 按钮可见

#### ✅ 预期结果
- Rent (pw) 筛选面板展开
- Min. 和 Max. 输入框均可见且可编辑
- Search 按钮可见且可点击
- 面板内无 Clear all 按钮(Rent 筛选器特征)

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_001

---

### TC002: 输入租金范围 min=100 max=500,点击 Search,URL 包含 min_price 和 max_price 参数

#### 📋 前置条件
- Rent (pw) 筛选按钮存在

#### 🎬 执行步骤
1. 点击 Rent (pw) 筛选按钮展开面板
2. 在 Min. 输入框中输入 `100`
3. 在 Max. 输入框中输入 `500`
4. 点击 Search 按钮提交筛选
5. 等待页面加载完成
6. 验证 URL 包含 `min_price=100` 和 `max_price=500`
7. 验证页面 H1 标题可见

#### ✅ 预期结果
- URL 同时包含 `min_price=100` 和 `max_price=500`
- 房源列表刷新,仅展示周租金在 £100-£500 范围内的房源
- H1 标题可见

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_002

---

### TC003: 仅输入 Min 租金不填 Max,点击 Search,URL 包含 min_price 但不含 max_price

#### 📋 前置条件
- Rent (pw) 筛选按钮存在

#### 🎬 执行步骤
1. 展开 Rent (pw) 面板
2. 在 Min. 输入框中输入 `200`
3. Max. 输入框保持为空
4. 点击 Search 提交筛选
5. 验证 URL 包含 `min_price=200`
6. 验证 URL 不包含 `max_price` 参数

#### ✅ 预期结果
- URL 包含 `min_price=200`
- URL 中不包含 `max_price` 参数
- 房源列表展示周租金 ≥ £200 的所有房源(无上限)

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_003

---

### TC004: Rent (pw) 筛选器展开后,再次点击按钮,面板应收起

#### 📋 前置条件
- Rent (pw) 筛选按钮存在

#### 🎬 执行步骤
1. 点击 Rent (pw) 按钮展开面板
2. 验证 Min. 输入框可见(确认面板已展开)
3. 再次点击 Rent (pw) 按钮
4. 验证 Min. 输入框不可见(确认面板已收起)

#### ✅ 预期结果
- 面板表现为 toggle 开关行为
- 第二次点击后面板完全收起

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 交互测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_004

---

## 分组二:Property type 筛选器

### TC005: 打开 Property type 筛选器,验证面板展开并含操作按钮,记录当前可用选项

#### 📋 前置条件
- Property type 筛选按钮存在(如不存在说明无广告含房产类型属性,测试跳过)

#### 🎬 执行步骤
1. 检查 Property type 筛选按钮是否存在
2. 点击 Property type 筛选按钮展开面板
3. 验证 Clear all 按钮可见
4. 验证 Search 按钮可见
5. 记录当前可用房产类型选项(通常为 Flat/House,以实际为准)

#### ✅ 预期结果
- Property type 筛选面板展开
- Clear all 和 Search 按钮可见
- 面板内展示房产类型选项(数量和内容取决于当前房源数据)

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_005

---

### TC006: 点击第一个可用 Property type 选项,验证 URL 包含 property_type 参数

#### 📋 前置条件
- Property type 筛选按钮存在
- 面板内至少有一个可用房产类型选项

#### 🎬 执行步骤
1. 展开 Property type 面板
2. 动态获取第一个可用房产类型选项(如无选项则跳过)
3. 记录选项的 href 中的 property_type 参数值
4. 点击该房产类型选项
5. 点击 Search 提交筛选
6. 验证 URL path 包含房产类型路径(如 `/property-to-rent/flat/` 或 `/property-to-rent/house/`)
7. 验证 H1 标题可见

#### ✅ 预期结果
- URL path 从 `/property-to-rent/uk/london` 变为 `/property-to-rent/flat/uk/london`(或 house)
- 房源列表刷新,仅展示该房产类型的房源
- H1 标题更新(通常包含房产类型名称)

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_006

---

### TC007: 选中某 Property type 选项后,点击 Clear all,筛选参数从 URL 中清除

#### 📋 前置条件
- 已按 TC006 选中某房产类型并提交筛选
- URL path 包含房产类型路径

#### 🎬 执行步骤
1. 重新展开 Property type 面板
2. 点击 Clear all 按钮
3. 验证 URL path 回到 `/property-to-rent/uk/london`(移除房产类型路径段)
4. 验证房源列表展示所有房产类型

#### ✅ 预期结果
- 房产类型路径段从 URL 中移除
- URL 回到基础路径
- 房源列表恢复展示所有房产类型
- 筛选面板仍保持展开状态

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_007

---

### TC008: Property type 面板各选项的 href 格式校验

#### 📋 前置条件
- Property type 面板已展开
- 面板内有可用选项

#### 🎬 执行步骤
1. 遍历所有可见的 Property type 选项
2. 读取每个选项的 href 属性
3. 验证 href 包含正确的路径格式(如 `/property-to-rent/flat/` 或 `/property-to-rent/house/`)

#### ✅ 预期结果
- 所有 Property type 选项的 href 都包含正确的路径格式
- 路径值符合预期的房产类型

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 数据验证
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_008

---

## 分组三:Number of bedrooms 筛选器

### TC009: 打开 Number of bedrooms 筛选器,验证 Min/Max 下拉按钮和 Search 按钮可见

#### 📋 前置条件
- Number of bedrooms 筛选按钮存在

#### 🎬 执行步骤
1. 检查 Number of bedrooms 筛选按钮是否存在
2. 点击 Number of bedrooms 筛选按钮展开面板
3. 验证 Min 下拉按钮可见(显示 "Any")
4. 验证 Max 下拉按钮可见(显示 "Any")
5. 验证 Search 按钮可见

#### ✅ 预期结果
- Number of bedrooms 筛选面板展开
- Min 和 Max 下拉按钮均可见(默认显示 "Any")
- Search 按钮可见
- 面板内无 Clear all 按钮(与 Rent 筛选器类似)

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_009

---

### TC010: 选择 Min 卧室数量,点击 Search,URL 包含 min_property_number_beds 参数

#### 📋 前置条件
- Number of bedrooms 筛选按钮存在

#### 🎬 执行步骤
1. 展开 Number of bedrooms 面板
2. 点击 Min 下拉按钮(显示 "Any")
3. 选择第一个数字选项(如 1、2、3 等)
4. 点击 Search 提交筛选
5. 验证 URL 包含 `min_property_number_beds=X`(X 为所选数字)
6. 验证房源列表刷新

#### ✅ 预期结果
- URL 包含 `min_property_number_beds=` 参数
- 房源列表刷新,仅展示卧室数量 ≥ 所选值的房源

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_010

---

### TC011: 同时选择 Min 和 Max 卧室数量,URL 同时包含两个 beds 参数

#### 📋 前置条件
- Number of bedrooms 筛选按钮存在

#### 🎬 执行步骤
1. 展开 Number of bedrooms 面板
2. 点击 Min 下拉,选择第一个数字选项(假设为 1)
3. 点击 Max 下拉,选择第二个数字选项(假设为 3)
4. 点击 Search 提交筛选
5. 验证 URL 同时包含 `min_property_number_beds=1` 和 `max_property_number_beds=3`
6. 验证房源列表展示卧室数量在 1-3 之间的房源

#### ✅ 预期结果
- URL 同时包含 Min 和 Max beds 参数
- 房源列表符合卧室数量范围筛选条件

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_011

---

### TC012: Number of bedrooms 面板展开后,再次点击按钮,面板应收起

#### 📋 前置条件
- Number of bedrooms 筛选按钮存在

#### 🎬 执行步骤
1. 点击 Number of bedrooms 按钮展开面板
2. 验证 Min 下拉按钮可见(确认面板已展开)
3. 再次点击 Number of bedrooms 按钮
4. 验证 Min 下拉按钮不可见(确认面板已收起)

#### ✅ 预期结果
- 面板表现为 toggle 开关行为
- 第二次点击后面板完全收起

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 交互测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_012

---

## 分组四:Seller type 筛选器

### TC013: 打开 Seller type 筛选器,验证面板展开并含操作按钮,记录当前可用选项

#### 📋 前置条件
- Seller type 筛选按钮存在

#### 🎬 执行步骤
1. 检查 Seller type 筛选按钮是否存在
2. 点击 Seller type 筛选按钮展开面板
3. 验证 Clear all 按钮可见
4. 验证 Search 按钮可见
5. 记录当前可用卖家类型选项(通常为 Agency/Private)

#### ✅ 预期结果
- Seller type 筛选面板展开
- Clear all 和 Search 按钮可见
- 面板内展示卖家类型选项

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_013

---

### TC014: 若 Agency 选项存在,点击后验证 URL 包含 seller_type=trade

#### 📋 前置条件
- Seller type 面板中 Agency 选项存在

#### 🎬 执行步骤
1. 展开 Seller type 面板
2. 点击 Agency 选项
3. 点击 Search 提交筛选
4. 验证 URL 包含 `seller_type=trade` 参数
5. 验证房源列表仅展示中介房源

#### ✅ 预期结果
- URL 包含 `seller_type=trade` 参数
- 房源列表刷新,仅展示中介发布的房源

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_014

---

### TC015: 若 Private 选项存在,点击后验证 URL 包含 seller_type=private

#### 📋 前置条件
- Seller type 面板中 Private 选项存在

#### 🎬 执行步骤
1. 展开 Seller type 面板
2. 点击 Private 选项
3. 点击 Search 提交筛选
4. 验证 URL 包含 `seller_type=private` 参数
5. 验证房源列表仅展示私人房源

#### ✅ 预期结果
- URL 包含 `seller_type=private` 参数
- 房源列表刷新,仅展示私人房东发布的房源

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_015

---

### TC016: 选中某 Seller type 选项后,点击 Clear all,URL 中 seller_type 参数消失

#### 📋 前置条件
- 已选中某 Seller type 并提交筛选
- URL 包含 `seller_type=` 参数

#### 🎬 执行步骤
1. 重新展开 Seller type 面板
2. 点击 Clear all 按钮
3. 验证 URL 不再包含 `seller_type=` 参数
4. 验证房源列表展示所有卖家类型

#### ✅ 预期结果
- `seller_type=` 参数从 URL 中移除
- 房源列表恢复展示中介和私人房东的房源
- 筛选面板仍保持展开状态

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_016

---

## 分组五:组合筛选场景

### TC017: Property type 和 Seller type 同时应用,URL 同时包含两组筛选参数

#### 📋 前置条件
- Property type 和 Seller type 筛选按钮均存在
- 两个面板内均有可用选项

#### 🎬 执行步骤
1. 展开 Property type 面板,选中第一个选项,点击 Search
2. 展开 Seller type 面板,选中第一个选项,点击 Search
3. 验证 URL 同时包含房产类型路径和 `seller_type=` 参数
4. 验证房源列表同时满足两个筛选条件

#### ✅ 预期结果
- URL 同时包含房产类型路径(如 `/flat/`)和 seller_type 参数
- 房源列表同时满足两个筛选条件
- 两个筛选器可以叠加使用

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_017

---

### TC018: Rent (pw) 筛选 + Property type 同时应用,URL 包含价格参数和 property_type 参数

#### 📋 前置条件
- Rent (pw) 和 Property type 筛选按钮均存在

#### 🎬 执行步骤
1. 展开 Rent (pw) 面板,输入 Min=100 Max=500,点击 Search
2. 展开 Property type 面板,选中第一个选项,点击 Search
3. 验证 URL 同时包含价格参数和房产类型路径
4. 验证房源列表同时满足两个筛选条件

#### ✅ 预期结果
- URL 同时包含 `min_price=100`、`max_price=500` 和房产类型路径
- 房源列表同时满足租金范围和房产类型筛选条件

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_PTR_018

---

## 分组六:异常输入与边界场景

### TC019: Rent输入负数租金,验证系统拒绝或提示错误

#### 📋 前置条件
- Rent (pw) 筛选按钮存在

#### 🎬 执行步骤
1. 展开 Rent (pw) 面板
2. 在 Min. 输入框中输入 `-50`
3. 点击 Search 按钮
4. 观察系统行为

#### ✅ 预期结果
- 系统应阻止提交或清空负数
- 显示友好的错误提示
- 或者将负数转换为0/忽略负号

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ❌ 暂不自动化(需要验证错误处理的合理性)

---

### TC020: Number of bedrooms选择 Min > Max,验证系统行为

#### 📋 前置条件
- Number of bedrooms 筛选按钮存在

#### 🎬 执行步骤
1. 展开 Number of bedrooms 面板
2. Min 下拉选择 `3`
3. Max 下拉选择 `1`
4. 点击 Search 提交
5. 观察系统行为

#### ✅ 预期结果
- 选项A: 系统提示"Min不能大于Max"
- 选项B: 系统返回零结果但不报错
- 选项C: 系统自动交换 Min 和 Max 值
- 应有明确的用户提示

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ❌ 暂不自动化(需要验证错误处理逻辑)

---

### TC021: 缺少实验参数时,验证筛选器功能降级或正常工作

#### 📋 前置条件
- 访问不带 `gt_gb_exp_ovr=Mul-M:B` 参数的 Property to Rent 页面

#### 🎬 执行步骤
1. 直接访问 `{base_url}/flats-houses/property-to-rent/uk/london`(不含实验参数)
2. 观察筛选器按钮是否正常渲染
3. 尝试应用筛选
4. 检查筛选功能是否正常

#### ✅ 预期结果
- 筛选器应有降级方案或正常工作
- 如果依赖实验参数,应有合理的降级行为
- 不应出现页面崩溃或功能完全不可用

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能降级测试
- **UI自动化**: ❌ 暂不自动化(需要验证实验参数的依赖性)

---

### TC022: 极端租金区间导致零结果,验证提示信息和重试机制

#### 📋 前置条件
- Rent (pw) 筛选按钮存在

#### 🎬 执行步骤
1. 展开 Rent (pw) 面板
2. 输入极端租金区间(如 Min=9999 Max=10000)
3. 提交筛选
4. 检查空状态提示
5. 尝试调整租金区间为合理值并重新搜索

#### ✅ 预期结果
- 显示友好的"无匹配房源"提示
- 提示应建议用户调整筛选条件
- 筛选器仍可正常调整
- 调整后能返回匹配结果

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UX测试
- **UI自动化**: ❌ 暂不自动化(需要评估空状态提示的用户友好性)

---

## 分组七:浏览器行为与用户体验

### TC023: 浏览器后退/前进按钮测试,验证筛选状态正确切换

#### 📋 前置条件
- 已依次应用多个筛选条件

#### 🎬 执行步骤
1. 初始状态: 无筛选
2. 应用 Rent 筛选,提交
3. 应用 Property type 筛选,提交
4. 点击后退按钮两次
5. 点击前进按钮一次

#### ✅ 预期结果
- 后退两次: 回到初始无筛选状态
- 前进一次: 恢复 Rent 筛选状态
- 每次切换后 URL 和房源列表应正确对应

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 浏览器兼容性测试
- **UI自动化**: ❌ 暂不自动化(需要验证浏览器历史栈管理)

---

### TC024: 直接输入带实验参数和筛选参数的完整URL,验证状态同步

#### 📋 前置条件
- 无

#### 🎬 执行步骤
1. 在浏览器地址栏输入完整URL:  
   `{base_url}/flats-houses/property-to-rent/flat/uk/london?gt_gb_exp_ovr=Mul-M:B&min_price=200&max_price=500&seller_type=private`
2. 按回车访问
3. 检查页面筛选器状态

#### ✅ 预期结果
- 房源列表正确展示筛选后的结果
- Property type 应显示 Flat 已选中
- Rent (pw) 筛选器应回显 Min=200, Max=500
- Seller type 应显示 Private 已选中

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: URL状态同步测试
- **UI自动化**: ❌ 暂不自动化(需要验证前端与URL的双向绑定)

---

### TC025: 移动端视图下,验证筛选器的响应式布局和触摸交互

#### 📋 前置条件
- 使用移动端设备或浏览器开发者工具切换到移动端视图

#### 🎬 执行步骤
1. 访问 Property to Rent 列表页(含实验参数)
2. 观察筛选器按钮在移动端的布局
3. 尝试展开筛选器面板
4. 尝试应用筛选并提交
5. 检查房源列表在移动端的显示

#### ✅ 预期结果
- 筛选器按钮应有移动端适配布局
- 筛选面板应易于触摸操作
- 下拉选择器(卧室数量)应使用原生移动端控件
- 所有功能在移动端应正常工作

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 响应式测试
- **UI自动化**: ❌ 暂不自动化(需要在真实移动设备上测试触摸交互)

---

## 测试统计

### 按优先级统计

| 优先级 | 用例数量 | 占比 |
|--------|---------|------|
| P0 | 2 | 8.0% |
| P1 | 15 | 60.0% |
| P2 | 8 | 32.0% |
| **总计** | **25** | **100%** |

### 按测试类型统计

| 测试类型 | 用例数量 | 占比 |
|---------|---------|------|
| 功能测试 | 16 | 64.0% |
| 交互测试 | 2 | 8.0% |
| 数据验证 | 1 | 4.0% |
| 边界测试 | 2 | 8.0% |
| 功能降级测试 | 1 | 4.0% |
| UX测试 | 1 | 4.0% |
| 浏览器兼容性测试 | 1 | 4.0% |
| URL状态同步测试 | 1 | 4.0% |
| **总计** | **25** | **100%** |

### 按筛选器分组统计

| 筛选器 | 用例数量 | 包含功能 |
|--------|---------|---------|
| Rent (pw) | 4 | 面板展开、租金区间筛选、单边筛选、面板收起 |
| Property type | 4 | 面板展开、房产类型选择、Clear all 清除、href 格式校验 |
| Number of bedrooms | 4 | 面板展开、Min 选择、Min+Max 选择、面板收起 |
| Seller type | 4 | 面板展开、Agency 筛选、Private 筛选、Clear all 清除 |
| 组合筛选 | 2 | Property type + Seller type、Rent + Property type |
| 异常输入与边界场景 | 4 | 负数输入、Min>Max、实验参数依赖、零结果提示 |
| 浏览器行为与UX | 3 | 后退/前进按钮、URL直接输入、移动端响应式 |
| **总计** | **25** | - |

### 自动化覆盖率

| 项目 | 数量 |
|------|------|
| 总用例数 | 25 |
| 可自动化用例 | 18 |
| 手工测试用例 | 7 |
| 自动化覆盖率 | 72.0% |

**手工测试场景说明**:  
TC019-TC025 为手工测试场景,主要覆盖:
- 异常输入验证和错误提示
- Min > Max 边界条件处理
- 实验参数依赖性和功能降级
- 零结果时的用户体验
- 浏览器后退/前进按钮行为
- URL直接输入时的状态同步
- 移动端响应式布局和触摸交互

这些场景需要人工观察和评估,暂不纳入自动化测试范围。

---

## 附录

### 筛选器 URL 参数一览

| 筛选器 | URL 参数/路径 | 说明 |
|--------|--------------|------|
| Rent (pw) | `min_price=X&max_price=Y` | 文本输入,无 Clear all |
| Property type | URL path: `/property-to-rent/flat/` 或 `/property-to-rent/house/` | 有 Clear all |
| Number of bedrooms | `min_property_number_beds=X&max_property_number_beds=Y` | 下拉选择,无 Clear all |
| Seller type | `seller_type=trade` 或 `seller_type=private` | 有 Clear all |

### 实验参数说明

**重要**: 本测试套件依赖实验参数 `gt_gb_exp_ovr=Mul-M:B`,该参数用于启用多选筛选器行为。

- **完整测试URL**: `{base_url}/flats-houses/property-to-rent/uk/london?gt_gb_exp_ovr=Mul-M:B`
- **作用**: 启用多选筛选器面板和组合筛选功能
- **影响**: 若缺少该参数,筛选器行为可能不一致

### 动态性特征说明

**双重动态性**与 Watches 测试套件一致:

1. **筛选按钮动态渲染**
   - 筛选按钮是否出现取决于当前房源列表数据
   - 若所有房源均未填写某属性,则该筛选按钮不会渲染

2. **筛选选项动态生成**
   - 面板内的具体选项值完全由当前房源数据决定
   - 测试不硬编码任何具体选项名称

3. **Skip 场景**
   - 筛选按钮不存在 → skip(属性在当前环境完全缺失)
   - 筛选按钮存在但面板内无可用选项 → skip(按钮存在但无匹配房源)

### 测试脚本路径

- **自动化脚本**: `bundled/skills/gt_autotest_ui_skill/bundled/gt_autotest_ui_gumtree/test_cases/buyer/test_buyer_property_to_rent_attribute_filters.py`
- **文本用例**: `bundled/knowledge_base/文本用例/buyer_filters/TC_Property_To_Rent_Attribute_Filters测试用例.md`

### 运行命令

```bash
# 基础运行
pytest test_cases/buyer/test_buyer_property_to_rent_attribute_filters.py --env=zoidberg

# 详细模式 + 有头浏览器
pytest test_cases/buyer/test_buyer_property_to_rent_attribute_filters.py --env=zoidberg --probe-headed -v
```
