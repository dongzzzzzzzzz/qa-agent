# Gumtree - Computing & IT Jobs属性筛选功能测试用例

> **生成时间**: 2026-05-07  
> **测试范围**: Computing & IT Jobs 列表页属性筛选功能  
> **总用例数**: 27条  
> **可自动化**: 20条 (74.1%)  
> **手工测试**: 7条 (25.9%)

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

- [分组一：Contract type 筛选器](#分组一contract-type-筛选器)
- [分组二：Recruiter Type 筛选器](#分组二recruiter-type-筛选器)
- [分组三：Hours 筛选器](#分组三hours-筛选器)
- [分组四：Salary 筛选器](#分组四salary-筛选器)
- [分组五：多筛选器组合场景](#分组五多筛选器组合场景)
- [分组六：异常输入与边界场景](#分组六异常输入与边界场景)
- [分组七：浏览器行为与用户体验](#分组七浏览器行为与用户体验)
- [测试统计](#测试统计)

---

## 测试概述

Computing & IT Jobs 列表页提供职位筛选功能,帮助求职者快速定位目标岗位。核心测试点:
- 合同类型筛选(Contract type: Contract/Permanent)
- 招聘方类型筛选(Recruiter Type: Agency/Direct Employer)
- 工时类型筛选(Hours: Full Time/Part Time)
- 薪资范围筛选(Salary: Min/Max)
- 筛选器展开/收起交互
- Tag 标签清除功能
- 全局 Clear All 按钮
- URL参数正确性
- 多筛选器叠加应用

**筛选器设计差异**:
- **Contract type / Recruiter Type / Hours**: 下拉选项型,需先选中选项再点击 Search,面板内有 Clear all + Search 按钮
- **Salary**: 范围输入型,Min./Max. 输入框,面板内仅有 Search 按钮(无 Clear all)

**目标页面**: `{base_url}/jobs/computing-it-jobs/uk/london`

---

## 分组一:Contract type 筛选器

### TC001: Contract type 面板展开,验证 Contract/Permanent 选项及 Clear all / Search 按钮

#### 📋 前置条件
- 已访问 Computing & IT Jobs 列表页
- Cookie 弹窗已关闭
- Contract type 筛选按钮存在

#### 🎬 执行步骤
1. 检查 Contract type 筛选按钮是否存在
2. 点击 Contract type 按钮展开面板
3. 验证 Contract 选项可见(文本含 Contract)
4. 验证 Permanent 选项可见(文本含 Permanent)
5. 验证 Clear all 按钮可见
6. 验证 Search 按钮可见

#### ✅ 预期结果
- Contract type 筛选面板展开
- Contract 和 Permanent 选项均可见
- Clear all 和 Search 按钮均可见

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_001

---

### TC002: 选择 Contract 选项并 Search,URL 包含 job_contract_type=contract,H1 更新

#### 📋 前置条件
- Contract type 筛选按钮存在

#### 🎬 执行步骤
1. 点击 Contract type 按钮展开面板
2. 点击 Contract 选项(选中复选框)
3. 点击 Search 提交筛选
4. 等待页面加载完成
5. 验证 URL 包含 `job_contract_type=contract`
6. 验证 H1 标题包含 Contract 文案
7. 验证筛选 Tag 出现

#### ✅ 预期结果
- URL 包含 `job_contract_type=contract` 参数
- H1 标题更新包含 Contract
- 页面顶部出现筛选 Tag(可点击 × 清除)
- 职位列表刷新,仅展示合同制职位

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_002

---

### TC003: 选择 Permanent 选项并 Search,URL 包含 permanent 路径或参数

#### 📋 前置条件
- Contract type 筛选按钮存在

#### 🎬 执行步骤
1. 点击 Contract type 按钮展开面板
2. 点击 Permanent 选项
3. 点击 Search 提交筛选
4. 等待页面加载完成
5. 验证 URL 包含 permanent(路径段或参数)

#### ✅ 预期结果
- URL 包含 permanent(可能是路径 `/permanent/` 或参数)
- 职位列表刷新,仅展示全职/永久制职位

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_003

---

### TC004: Contract type 面板内点击 Clear all,已选选项被取消(URL 未变化)

#### 📋 前置条件
- Contract type 筛选按钮存在

#### 🎬 执行步骤
1. 展开 Contract type 面板
2. 点击 Contract 选项使其被选中
3. 点击面板内 Clear all(不点 Search)
4. 验证 URL 未含 job_contract_type 参数(筛选未提交)
5. 验证 Clear all 按钮仍可点击(面板保持展开状态)

#### ✅ 预期结果
- 点击 Clear all 后选项被取消选中
- URL 未发生变化(筛选未提交到服务器)
- 筛选面板仍保持展开状态

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 交互测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_004

---

### TC005: Contract 筛选生效后,点击 Tag × 图标,job_contract_type 参数从 URL 移除

#### 📋 前置条件
- 已按 TC002 选中 Contract 并提交筛选
- URL 包含 `job_contract_type=contract`
- 页面顶部出现筛选 Tag

#### 🎬 执行步骤
1. 定位页面顶部的 Contract 筛选 Tag
2. 点击 Tag 右侧的 × 图标
3. 等待页面刷新
4. 验证 URL 不再包含 `job_contract_type=contract`
5. 验证 H1 标题恢复为默认文案
6. 验证筛选 Tag 消失

#### ✅ 预期结果
- 点击 Tag × 后 URL 立即变化
- `job_contract_type=contract` 参数从 URL 移除
- 职位列表恢复展示所有合同类型
- H1 标题恢复为 "Computing & IT Jobs"

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_005

---

## 分组二:Recruiter Type 筛选器

### TC006: Recruiter Type 面板展开,验证 Recruiter 选项及 Clear all / Search 按钮

#### 📋 前置条件
- Recruiter Type 筛选按钮存在

#### 🎬 执行步骤
1. 检查 Recruiter Type 筛选按钮是否存在
2. 点击 Recruiter Type 按钮展开面板
3. 验证 Recruiter 选项可见(通常为 Agency/Direct Employer)
4. 验证 Clear all 按钮可见
5. 验证 Search 按钮可见

#### ✅ 预期结果
- Recruiter Type 筛选面板展开
- 招聘方类型选项可见(数量和内容取决于当前职位数据)
- Clear all 和 Search 按钮均可见

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_006

---

### TC007: 选择 Recruiter 选项并 Search,URL 包含 recruiter_type=agency

#### 📋 前置条件
- Recruiter Type 筛选按钮存在
- 面板内有可用选项

#### 🎬 执行步骤
1. 展开 Recruiter Type 面板
2. 点击第一个可用招聘方选项(通常为 Agency)
3. 点击 Search 提交筛选
4. 等待页面加载
5. 验证 URL 包含 `recruiter_type=agency`(或其他对应值)
6. 验证职位列表刷新

#### ✅ 预期结果
- URL 包含 `recruiter_type=` 参数
- 职位列表刷新,仅展示对应招聘方类型的职位

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_007

---

### TC008: Recruiter 筛选生效后,点击全局 Clear All,recruiter_type 参数消失

#### 📋 前置条件
- 已按 TC007 选中某招聘方类型并提交筛选
- URL 包含 `recruiter_type=` 参数

#### 🎬 执行步骤
1. 定位页面上的全局 Clear All 按钮(通常在筛选区域)
2. 点击 Clear All 按钮
3. 等待页面刷新
4. 验证 URL 不再包含 `recruiter_type=` 参数
5. 验证所有筛选 Tag 消失

#### ✅ 预期结果
- 点击全局 Clear All 后所有筛选清除
- `recruiter_type=` 参数从 URL 移除
- 职位列表恢复展示所有招聘方类型

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_008

---

## 分组三:Hours 筛选器

### TC009: Hours 面板展开,验证 Part Time 选项及 Clear all / Search 按钮

#### 📋 前置条件
- Hours 筛选按钮存在

#### 🎬 执行步骤
1. 检查 Hours 筛选按钮是否存在
2. 点击 Hours 按钮展开面板
3. 验证工时选项可见(通常为 Full Time/Part Time)
4. 验证 Clear all 按钮可见
5. 验证 Search 按钮可见

#### ✅ 预期结果
- Hours 筛选面板展开
- 工时类型选项可见
- Clear all 和 Search 按钮均可见

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_009

---

### TC010: 选择 Part Time 选项并 Search,URL 包含 job_hours=part_time,标题含 Part Time

#### 📋 前置条件
- Hours 筛选按钮存在
- Part Time 选项存在

#### 🎬 执行步骤
1. 展开 Hours 面板
2. 点击 Part Time 选项
3. 点击 Search 提交筛选
4. 等待页面加载
5. 验证 URL 包含 `job_hours=part_time`
6. 验证 H1 标题包含 Part Time 文案

#### ✅ 预期结果
- URL 包含 `job_hours=part_time` 参数
- H1 标题更新(通常包含 "Part Time")
- 职位列表刷新,仅展示兼职职位

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_010

---

### TC011: Part Time 筛选生效后,点击 Tag × 图标,job_hours 参数从 URL 移除

#### 📋 前置条件
- 已按 TC010 选中 Part Time 并提交筛选
- URL 包含 `job_hours=part_time`

#### 🎬 执行步骤
1. 定位页面顶部的 Part Time 筛选 Tag
2. 点击 Tag 右侧的 × 图标
3. 等待页面刷新
4. 验证 URL 不再包含 `job_hours=part_time`
5. 验证职位列表恢复展示所有工时类型

#### ✅ 预期结果
- `job_hours=part_time` 参数从 URL 移除
- 职位列表恢复展示全职和兼职职位

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_011

---

## 分组四:Salary 筛选器

### TC012: Salary 面板展开,验证 Min./Max. 输入框可见且仅有 Search 按钮(无 Clear all)

#### 📋 前置条件
- 已访问 Computing & IT Jobs 列表页
- Salary 筛选按钮存在

#### 🎬 执行步骤
1. 检查 Salary 筛选按钮是否存在
2. 点击 Salary 按钮展开面板
3. 验证 Min. 输入框可见
4. 验证 Max. 输入框可见
5. 验证 Search 按钮可见
6. 验证面板内无 Clear all 按钮(Salary 筛选器特征)

#### ✅ 预期结果
- Salary 筛选面板展开
- Min. 和 Max. 输入框均可见且可编辑
- Search 按钮可见
- 面板内无 Clear all 按钮(与其他筛选器不同)

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_012

---

### TC013: 输入 Min.=30000 Max.=60000 点击 Search,URL 同时含 min_salary 和 max_salary

#### 📋 前置条件
- Salary 筛选按钮存在

#### 🎬 执行步骤
1. 展开 Salary 面板
2. 在 Min. 输入框中输入 `30000`
3. 在 Max. 输入框中输入 `60000`
4. 点击 Search 提交筛选
5. 等待页面加载
6. 验证 URL 包含 `min_salary=30000` 和 `max_salary=60000`
7. 验证职位列表刷新

#### ✅ 预期结果
- URL 同时包含 `min_salary=30000` 和 `max_salary=60000`
- 职位列表刷新,仅展示薪资在 £30,000-£60,000 范围内的职位

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_013

---

### TC014: 仅输入 Min.=40000 点击 Search,URL 含 min_salary=40000 不含 max_salary

#### 📋 前置条件
- Salary 筛选按钮存在

#### 🎬 执行步骤
1. 展开 Salary 面板
2. 在 Min. 输入框中输入 `40000`
3. Max. 输入框保持为空
4. 点击 Search 提交筛选
5. 验证 URL 包含 `min_salary=40000`
6. 验证 URL 不包含 `max_salary` 参数

#### ✅ 预期结果
- URL 包含 `min_salary=40000`
- URL 中不包含 `max_salary` 参数
- 职位列表展示薪资 ≥ £40,000 的所有职位(无上限)

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_014

---

### TC015: 仅输入 Max.=50000 点击 Search,URL 含 max_salary=50000 不含 min_salary

#### 📋 前置条件
- Salary 筛选按钮存在

#### 🎬 执行步骤
1. 展开 Salary 面板
2. Min. 输入框保持为空
3. 在 Max. 输入框中输入 `50000`
4. 点击 Search 提交筛选
5. 验证 URL 包含 `max_salary=50000`
6. 验证 URL 不包含 `min_salary` 参数

#### ✅ 预期结果
- URL 包含 `max_salary=50000`
- URL 中不包含 `min_salary` 参数
- 职位列表展示薪资 ≤ £50,000 的所有职位(无下限)

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_015

---

### TC016: Salary Min+Max 均生效后,点击 From Tag × 移除,min_salary 参数消失

#### 📋 前置条件
- 已按 TC013 设置薪资范围并提交筛选
- URL 包含 `min_salary=30000` 和 `max_salary=60000`
- 页面顶部出现 "From £30,000" 和 "To £60,000" 两个 Tag

#### 🎬 执行步骤
1. 定位 "From £30,000" Tag
2. 点击该 Tag 右侧的 × 图标
3. 等待页面刷新
4. 验证 URL 不再包含 `min_salary=30000`
5. 验证 URL 仍包含 `max_salary=60000`
6. 验证 "From" Tag 消失,"To" Tag 仍存在

#### ✅ 预期结果
- `min_salary=30000` 参数从 URL 移除
- `max_salary=60000` 参数仍保留
- 职位列表展示薪资 ≤ £60,000 的所有职位(无下限)

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_016

---

### TC017: Salary 面板 Min./Max. 均为空直接点击 Search,URL 无薪资参数新增

#### 📋 前置条件
- Salary 筛选按钮存在

#### 🎬 执行步骤
1. 展开 Salary 面板
2. Min. 和 Max. 输入框均保持为空
3. 点击 Search 按钮
4. 验证 URL 不包含 `min_salary` 或 `max_salary` 参数
5. 验证职位列表未发生变化

#### ✅ 预期结果
- URL 未新增薪资参数
- 职位列表展示所有薪资范围的职位
- 无筛选 Tag 出现

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_017

---

### TC018: Salary 设置范围 Min=30000 Max=60000 零结果,页面显示空状态文案

#### 📋 前置条件
- Salary 筛选按钮存在

#### 🎬 执行步骤
1. 展开 Salary 面板
2. 输入一个预期会导致零结果的薪资范围(如 Min=30000 Max=60000)
3. 点击 Search 提交筛选
4. 验证页面显示空状态提示文案(如 "No results found")
5. 验证 URL 包含薪资参数

#### ✅ 预期结果
- 页面显示空状态提示
- URL 包含正确的薪资参数
- 无职位卡片展示

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_018

---

## 分组五:多筛选器组合场景

### TC019: Contract type=Contract 与 Salary Min.=200 叠加,URL 同时含两组参数

#### 📋 前置条件
- Contract type 和 Salary 筛选按钮均存在

#### 🎬 执行步骤
1. 展开 Contract type 面板,选中 Contract,点击 Search
2. 展开 Salary 面板,输入 Min.=200,点击 Search
3. 验证 URL 同时包含 `job_contract_type=contract` 和 `min_salary=200`
4. 验证职位列表同时满足两个筛选条件

#### ✅ 预期结果
- URL 同时包含合同类型和薪资参数
- 职位列表展示合同制且薪资 ≥ £200 的职位
- 两个筛选 Tag 均出现在页面顶部

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_019

---

### TC020: 多筛选器激活时,点击全局 Clear All,所有筛选参数清除,4 个筛选按钮恢复显示

#### 📋 前置条件
- 已应用多个筛选条件(如 Contract type、Hours、Salary)
- URL 包含多个筛选参数
- 页面顶部出现多个筛选 Tag

#### 🎬 执行步骤
1. 定位页面上的全局 Clear All 按钮
2. 点击 Clear All 按钮
3. 等待页面刷新
4. 验证 URL 不再包含任何筛选参数
5. 验证所有筛选 Tag 消失
6. 验证 4 个筛选按钮(Contract type、Recruiter Type、Hours、Salary)均恢复显示
7. 验证职位列表展示所有职位

#### ✅ 预期结果
- 所有筛选参数从 URL 中移除
- 所有筛选 Tag 消失
- 4 个筛选按钮恢复初始状态
- 职位列表恢复展示所有职位

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **Case ID**: GUMTREE_BUYER_JOBS_IT_020

---

## 分组六:异常输入与边界场景

### TC021: Salary输入非数字字符,验证输入框过滤机制

#### 📋 前置条件
- Salary 筛选按钮存在

#### 🎬 执行步骤
1. 展开 Salary 面板
2. 尝试在 Min. 输入框中输入字母和特殊字符: `abc`, `£`, `30k`
3. 观察输入框是否接受这些字符
4. 如果接受,点击 Search 后观察系统行为

#### ✅ 预期结果
- 理想情况: 输入框仅接受纯数字(客户端验证)
- 或者: 后端验证时拒绝非法输入并提示明确错误
- 系统应处理用户可能输入的常见格式(如 `30k` 转为 `30000`)

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 边界测试
- **UI自动化**: ❌ 暂不自动化(需要人工观察输入框实时反馈和错误提示)

---

### TC022: 同时打开多个筛选器面板,验证布局不冲突

#### 📋 前置条件
- 所有筛选器按钮存在

#### 🎬 执行步骤
1. 依次展开 Contract type、Recruiter Type、Hours、Salary 面板(不关闭前一个)
2. 观察多个面板是否重叠或错位
3. 尝试在不同面板中进行操作

#### ✅ 预期结果
- 如果设计为互斥: 展开新面板时前一个应自动关闭
- 如果设计为可同时展开: 面板应有合理布局,不重叠或错位
- 页面滚动条应能正常工作
- 所有面板内的交互元素应可点击

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UI/UX测试
- **UI自动化**: ❌ 暂不自动化(需要人工评估多面板展开时的视觉效果)

---

### TC023: 零结果情况下,验证筛选器仍可调整且提示信息友好

#### 📋 前置条件
- 已应用某组筛选导致零结果

#### 🎬 执行步骤
1. 应用极端筛选条件(如 Salary Min=999999)导致零结果
2. 检查页面显示的空状态提示
3. 尝试调整筛选器(如降低 Salary Min)
4. 检查筛选器是否仍可正常使用

#### ✅ 预期结果
- 显示友好的"无匹配职位"提示
- 提示应建议用户调整筛选条件
- 所有筛选器按钮仍可点击和调整
- 调整后提交,系统应返回新的匹配结果

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UX测试
- **UI自动化**: ❌ 暂不自动化(需要评估空状态提示的用户友好性)

---

### TC024: Tag标签过多时,验证页面布局和滚动行为

#### 📋 前置条件
- 已应用多个筛选条件(4个以上)

#### 🎬 执行步骤
1. 依次应用 Contract type、Recruiter Type、Hours、Salary Min、Salary Max 筛选
2. 观察页面顶部 Tag 标签区域的布局
3. 检查 Tag 是否换行或横向滚动
4. 尝试点击每个 Tag 的 × 图标清除

#### ✅ 预期结果
- Tag 区域应有合理布局(换行或横向滚动)
- 所有 Tag 均可见且可操作
- Tag 不应遮挡其他重要内容
- 点击 × 图标应能准确清除对应筛选

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: UI测试
- **UI自动化**: ❌ 暂不自动化(需要人工评估多Tag布局的视觉效果)

---

## 分组七:浏览器行为与用户体验

### TC025: 刷新页面后,验证所有筛选器状态和 Tag 标签正确恢复

#### 📋 前置条件
- 已应用多个筛选条件

#### 🎬 执行步骤
1. 应用 Contract type、Hours、Salary 筛选
2. 按 F5 刷新页面
3. 等待页面重新加载
4. 检查 URL、职位列表、Tag 标签、筛选器面板状态

#### ✅ 预期结果
- URL 参数保持不变
- 职位列表仍展示筛选后的结果
- 所有 Tag 标签重新渲染显示
- 如果展开筛选器面板,应回显之前的选中状态

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 状态持久化测试
- **UI自动化**: ❌ 暂不自动化(需要验证页面刷新后的完整状态恢复)

---

### TC026: 使用键盘 Tab 键导航完成完整筛选流程

#### 📋 前置条件
- 页面已加载完成

#### 🎬 执行步骤
1. 按 Tab 键导航到 Contract type 按钮,按 Enter 展开
2. 继续 Tab 导航到 Contract 选项,按 Space 选中
3. Tab 到 Search 按钮,按 Enter 提交
4. 观察筛选是否成功应用

#### ✅ 预期结果
- 所有交互元素可通过 Tab 键访问
- 焦点顺序符合逻辑
- 按钮可通过 Enter/Space 激活
- 完整筛选流程无需鼠标即可完成

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 无障碍测试
- **UI自动化**: ❌ 暂不自动化(需要验证键盘导航的流畅性)

---

### TC027: 移动端视图下,验证筛选器的触摸交互和响应式布局

#### 📋 前置条件
- 使用移动端设备或浏览器开发者工具切换到移动端视图

#### 🎬 执行步骤
1. 访问 Computing & IT Jobs 列表页
2. 观察筛选器按钮在移动端的布局
3. 尝试点击展开筛选器面板
4. 尝试应用筛选并提交
5. 检查 Tag 标签在移动端的显示

#### ✅ 预期结果
- 筛选器按钮在移动端应有适配布局
- 筛选面板应易于触摸操作
- 所有功能在移动端应正常工作
- Tag 标签应合理换行,不应横向溢出

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 响应式测试
- **UI自动化**: ❌ 暂不自动化(需要在真实移动设备上测试触摸交互)

---

## 测试统计

### 按优先级统计

| 优先级 | 用例数量 | 占比 |
|--------|---------|------|
| P0 | 6 | 22.2% |
| P1 | 14 | 51.9% |
| P2 | 7 | 25.9% |
| **总计** | **27** | **100%** |

### 按测试类型统计

| 测试类型 | 用例数量 | 占比 |
|---------|---------|------|
| 功能测试 | 17 | 63.0% |
| 交互测试 | 1 | 3.7% |
| 边界测试 | 3 | 11.1% |
| UI/UX测试 | 3 | 11.1% |
| 状态持久化测试 | 1 | 3.7% |
| 无障碍测试 | 1 | 3.7% |
| 响应式测试 | 1 | 3.7% |
| **总计** | **27** | **100%** |

### 按筛选器分组统计

| 筛选器 | 用例数量 | 包含功能 |
|--------|---------|---------|
| Contract type | 5 | 面板展开、Contract 选择、Permanent 选择、Clear all、Tag 清除 |
| Recruiter Type | 3 | 面板展开、Recruiter 选择、全局 Clear All |
| Hours | 3 | 面板展开、Part Time 选择、Tag 清除 |
| Salary | 7 | 面板展开、Min+Max 设置、单边设置、Tag 清除、空输入、零结果 |
| 多筛选组合 | 2 | 两筛选器叠加、全局 Clear All |
| 异常输入与边界场景 | 4 | 非数字输入、多面板展开、零结果提示、多Tag布局 |
| 浏览器行为与UX | 3 | 页面刷新、键盘导航、移动端响应式 |
| **总计** | **27** | - |

### 自动化覆盖率

| 项目 | 数量 |
|------|------|
| 总用例数 | 27 |
| 可自动化用例 | 20 |
| 手工测试用例 | 7 |
| 自动化覆盖率 | 74.1% |

**手工测试场景说明**:  
TC021-TC027 为手工测试场景,主要覆盖:
- 异常输入验证和错误提示准确性
- 多面板展开时的视觉布局
- 零结果时的用户体验和提示友好性
- 多Tag标签的布局和滚动行为
- 页面刷新后的完整状态恢复
- 键盘导航和无障碍性
- 移动端响应式布局和触摸交互

这些场景需要人工观察和评估,暂不纳入自动化测试范围。

---

## 附录

### 筛选器 URL 参数一览

| 筛选器 | URL 参数/路径 | 说明 |
|--------|--------------|------|
| Contract type | `job_contract_type=contract` 或 `/permanent/` 路径 | 有 Clear all |
| Recruiter Type | `recruiter_type=agency` | 有 Clear all |
| Hours | `job_hours=part_time` | 有 Clear all |
| Salary | `min_salary=X` 和/或 `max_salary=Y` | 无 Clear all(通过 Tag × 清除) |

### 筛选器设计特征

1. **选项型筛选器**(Contract type、Recruiter Type、Hours):
   - 需先选中选项再点击 Search
   - 面板内有 Clear all + Search 按钮
   - 支持 Tag × 图标清除

2. **输入型筛选器**(Salary):
   - Min./Max. 文本输入框
   - 面板内仅有 Search 按钮(无 Clear all)
   - 支持 Tag × 图标清除(From/To 分别清除)

3. **全局 Clear All**:
   - 清除所有已应用筛选
   - 所有筛选按钮恢复初始状态

### 测试脚本路径

- **自动化脚本**: `bundled/skills/gt_autotest_ui_skill/bundled/gt_autotest_ui_gumtree/test_cases/buyer/test_buyer_jobs_it_attribute_filters.py`
- **文本用例**: `bundled/knowledge_base/文本用例/buyer_filters/TC_Jobs_IT_Attribute_Filters测试用例.md`

### 运行命令

```bash
# 基础运行
pytest test_cases/buyer/test_buyer_jobs_it_attribute_filters.py --env=zoidberg

# 详细模式
pytest test_cases/buyer/test_buyer_jobs_it_attribute_filters.py --env=zoidberg -v
```
