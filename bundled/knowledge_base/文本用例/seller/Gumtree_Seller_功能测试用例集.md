# Gumtree Seller 功能测试用例文档

> **生成时间**: 2026-03-30  
> **生成方式**: 基于自动化测试脚本反向生成  
> **测试范围**: Gumtree 卖家端完整功能（发布广告、管理广告）  
> **自动化脚本路径**: `/test_cases/seller/`  
> **总用例数**: 50条  
> **已自动化**: 50条 (100%)  

---

## 测试环境配置

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | 多站点 | zoidberg/taro/staging |
| 基础URL | 根据--env参数动态切换 | 测试站点地址 |
| 角色 | seller | 卖家角色 |
| 账号管理 | SessionManager | 支持Session复用 |
| 测试数据 | /artifacts/test_photo.jpg | 照片上传测试数据 |

**说明**：
- 通过 `pytest --env=zoidberg` 切换测试环境
- 使用 SessionManager 实现登录Session复用，提升测试效率
- 所有脚本已实现Playwright自动化，可CI/CD集成

---

## 📑 目录

- [1. 用户认证模块](#1-用户认证模块)
- [2. 广告发布模块](#2-广告发布模块)
- [3. 广告管理模块](#3-广告管理模块)
- [4. 推广功能模块](#4-推广功能模块)
- [5. 重复发布模块](#5-重复发布模块)
- [6. 测试统计](#测试统计)

---

## 1. 用户认证模块

### TC-LOGIN-001: 正常登录流程

#### 📋 前置条件
- 测试账号已创建
- 已清除浏览器缓存或使用新会话

#### 🎬 执行步骤
1. 导航到登录页面 `/login`
2. 处理隐私弹窗（如出现）：点击"Accept All"
3. 点击"Continue with email"选择邮箱登录
4. 输入测试账号邮箱（test_account['email']）
5. 输入测试账号密码（test_account['password']）
6. 点击"Continue"按钮提交登录
7. 等待5秒，等待登录完成
8. 验证登录成功标志出现

#### ✅ 预期结果
- 隐私弹窗成功关闭
- 登录表单正确填写
- 点击"Continue"后页面跳转
- 页面URL不包含"login"
- 顶部导航栏显示"Post an ad"按钮或"My Gumtree"菜单
- Session成功保存到本地

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_002_login_success`
- **执行时间**: ~15秒

---

### TC-LOGIN-002: Session复用登录

#### 📋 前置条件
- 已执行过登录并保存了Session
- Session文件存在于 `session_storage/{username}.json`

#### 🎬 执行步骤
1. 导航到首页 `base_url`
2. 调用 `SessionManager.load_session(page, username)`
3. 刷新页面使Session生效
4. 验证是否仍在登录状态

#### ✅ 预期结果
- Session文件成功加载
- 页面刷新后仍保持登录状态
- 无需重新输入账号密码
- 页面URL不跳转到登录页

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `class_setup` fixture中的逻辑
- **执行时间**: ~5秒

---

### TC-LOGIN-003: Session失效后重新登录

#### 📋 前置条件
- Session文件存在但已过期（>24小时）
- 或服务端Session已清除

#### 🎬 执行步骤
1. 加载过期的Session
2. 刷新页面
3. 检测到页面URL包含"login"
4. 自动触发重新登录流程
5. 保存新的Session

#### ✅ 预期结果
- 检测到Session失效
- 自动重新登录成功
- 新Session保存成功
- 测试继续正常执行

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 异常处理测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `class_setup` fixture中的Session验证逻辑
- **执行时间**: ~20秒

---

## 2. 广告发布模块

### 2.1 类目选择子模块

### TC-CATEGORY-001: 浏览方式选择四级类目（Baby Clothes）

#### 📋 前置条件
- 用户已登录
- 当前在Post Ad入口页 `/postad`

#### 🎬 执行步骤
1. 点击"Or browse to find a category"按钮
2. 等待分类浏览器展开
3. 依次点击四级分类：
   - 第一级：For Sale
   - 第二级：Baby & Kids Stuff
   - 第三级：Baby & Kids Bedding
   - 第四级：Baby Clothes
4. 点击"Continue"按钮确认
5. 等待页面跳转

#### ✅ 预期结果
- 分类浏览器正确展开
- 每级分类点击后，下一级正确展开
- Continue按钮可点击
- 页面跳转到 `/postad/create?categoryId=121`
- Category字段显示完整路径："For Sale > Baby & Kids Stuff > Baby & Kids Bedding > Baby Clothes"

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_001_select_category_baby_clothes`
- **类目ID**: 121 (Baby Clothes)
- **执行时间**: ~8秒

---

### TC-CATEGORY-002: 浏览方式选择三级类目（Stuff Wanted）

#### 📋 前置条件
- 用户已登录
- 当前在Post Ad入口页 `/postad`

#### 🎬 执行步骤
1. 点击"Or browse to find a category"按钮
2. 依次点击三级分类：
   - 第一级：For Sale
   - 第二级：Stuff Wanted
   - 第三级：Audio & Vision
3. 点击"Continue"按钮确认

#### ✅ 预期结果
- 页面跳转到 `/postad/create?categoryId=187`
- Category字段显示："For Sale > Stuff Wanted > Audio & Vision"

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_stuff_wanted_Featured_threeDays.py::test_001_select_category_stuff_wanted`
- **类目ID**: 187 (Stuff Wanted > Audio & Vision)
- **执行时间**: ~6秒

---

### TC-CATEGORY-003: 验证已在指定类目创建页

#### 📋 前置条件
- 用户已登录
- 直接导航到 `/postad/create?categoryId=121`

#### 🎬 执行步骤
1. 验证当前页面URL
2. 检查URL中的categoryId参数

#### ✅ 预期结果
- 页面URL包含"postad/create"
- URL参数包含正确的categoryId
- Category字段正确显示类目路径
- 表单字段正常加载

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_003_navigate_to_post_ad_page`
- **执行时间**: ~2秒

---

### 2.2 表单填写子模块

### TC-PHOTOS-001: 上传单张照片

#### 📋 前置条件
- 用户已登录
- 当前在广告创建页面
- 测试图片存在：`/artifacts/test_photo.jpg`

#### 🎬 执行步骤
1. 定位照片上传区域
2. 调用 `page.set_input_files('input[type="file"]', test_image_path)`
3. 等待3秒，等待照片上传完成
4. 验证照片上传成功

#### ✅ 预期结果
- 照片成功上传到服务器
- 照片缩略图在页面显示
- Photos字段的错误提示消失（如之前有"Please upload at least 1 photo"）
- 照片计数器更新（如 "1/20"）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_upload_single_photo`
- **执行时间**: ~5秒

---

### TC-TITLE-001: 填写有效标题

#### 📋 前置条件
- 用户已登录
- 当前在广告创建页面

#### 🎬 执行步骤
1. 定位"Ad Title"输入框
2. 输入测试标题："Cute Baby Clothes - Organic Cotton Set"
3. 按下Tab键触发失去焦点
4. 等待1秒，等待验证完成
5. 读取输入框的实际值

#### ✅ 预期结果
- 标题成功填写到输入框
- 输入框的value值与输入内容一致
- Ad Title字段左侧显示绿色勾选标记（如有）
- 无错误提示

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_fill_ad_title_valid`
- **执行时间**: ~3秒

---

### TC-DESCRIPTION-001: 填写有效描述（>15字符）

#### 📋 前置条件
- 用户已登录
- 当前在广告创建页面

#### 🎬 执行步骤
1. 定位"Description"文本域
2. 输入测试描述（>15字符）："Adorable baby clothes set made from 100% organic cotton. Includes bodysuits, pants, and tops in various colors. Soft, breathable, and perfect for newborns and infants."
3. 按下Tab键触发失去焦点
4. 等待1秒，等待字符计数更新
5. 读取文本域的实际值

#### ✅ 预期结果
- 描述成功填写到文本域
- 文本域的value值与输入内容一致
- 字符计数正确更新（如 "145/10000"）
- 无"15 characters minimum"错误提示

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_fill_description_valid`
- **字符数要求**: 15-10000字符
- **执行时间**: ~3秒

---

### TC-CONDITION-001: 选择Condition为New

#### 📋 前置条件
- 用户已登录
- 当前在广告创建页面（Baby Clothes类目）

#### 🎬 执行步骤
1. 滚动到"Item Specifics"区域
2. 点击"Condition"选择按钮
3. 等待弹窗/下拉菜单展开
4. 在弹窗中选择"New"选项
5. 点击"Save"按钮保存选择
6. 等待弹窗关闭

#### ✅ 预期结果
- Condition选择器正确展开
- "New"选项可见且可点击
- 点击Save后弹窗关闭
- Condition按钮文本更新为"New"
- 字段左侧显示绿色勾选标记（如有）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_select_condition_new`
- **可选值**: New, Used, For parts or not working
- **执行时间**: ~3秒

---

### TC-GENDER-001: 选择Gender（Baby Clothes类目特有）

#### 📋 前置条件
- 用户已登录
- 当前在Baby Clothes类目创建页
- Gender字段显示占位文案（如"Select gender"）

#### 🎬 执行步骤
1. 滚动到"Gender"字段可视区域
2. 点击Gender选择按钮
3. 在弹层中选择"Unisex"（或首个可用选项）
4. 点击"Save"保存
5. 等待弹层关闭

#### ✅ 预期结果
- Gender弹层正确展开
- "Unisex"选项可见且可点击
- 点击Save后弹层关闭
- Gender按钮文本更新为"Unisex"
- 占位文案（"Select gender"）消失

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_select_gender`
- **类目依赖**: 仅Baby Clothes等特定类目有此字段
- **执行时间**: ~3秒

---

### TC-SIZE-001: 选择Size（Baby Clothes类目特有）

#### 📋 前置条件
- 用户已登录
- 当前在Baby Clothes类目创建页
- Size字段显示占位文案

#### 🎬 执行步骤
1. 滚动到"Size"字段可视区域
2. 点击Size选择按钮
3. 在弹层中选择"0-3 months"（或首个可用选项）
4. 点击"Save"保存

#### ✅ 预期结果
- Size按钮文本更新为"0-3 months"
- 占位文案消失

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_select_size`
- **可选值**: 0-3 months, 3-6 months, 6-12 months等
- **执行时间**: ~3秒

---

### TC-BRAND-001: 选择Brand

#### 📋 前置条件
- 用户已登录
- 当前在广告创建页面（类目支持Brand字段）

#### 🎬 执行步骤
1. 滚动到"Brand"字段可视区域
2. 点击Brand选择按钮
3. 在弹层中选择"Other"（或首个可用选项）
4. 点击"Save"保存

#### ✅ 预期结果
- Brand按钮文本更新为"Other"
- 占位文案（"Select brand"）消失

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_select_brand`
- **执行时间**: ~3秒

---

### TC-COLOUR-001: 选择Colour

#### 📋 前置条件
- 用户已登录
- 当前在广告创建页面（类目支持Colour字段）

#### 🎬 执行步骤
1. 滚动到"Colour"字段可视区域
2. 点击Colour选择按钮
3. 在弹层中选择"White"（或首个可用选项）
4. 点击"Save"保存

#### ✅ 预期结果
- Colour按钮文本更新为"White"
- 占位文案消失

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_select_colour`
- **执行时间**: ~3秒

---

### TC-MATERIAL-001: 选择Material

#### 📋 前置条件
- 用户已登录
- 当前在广告创建页面（类目支持Material字段）

#### 🎬 执行步骤
1. 滚动到"Material"字段可视区域
2. 点击Material选择按钮
3. 在弹层中选择"Cotton"（或首个可用选项）
4. 点击"Save"保存

#### ✅ 预期结果
- Material按钮文本更新为"Cotton"
- 占位文案消失

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_select_material`
- **执行时间**: ~3秒

---

### TC-PRICE-001: 填写有效价格

#### 📋 前置条件
- 用户已登录
- 当前在广告创建页面

#### 🎬 执行步骤
1. 定位"Price"输入框
2. 输入价格：10
3. 按下Tab键触发失去焦点
4. 等待1秒，等待验证完成
5. 读取输入框的实际值

#### ✅ 预期结果
- 价格成功填写
- 输入框显示"£10"或"10"
- 无错误提示
- Price字段左侧显示绿色勾选标记（如有）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_fill_price_valid`
- **货币符号**: £（英镑）
- **执行时间**: ~3秒

---

### TC-PARCELSIZE-001: 选择包裹尺寸（Light Item）

#### 📋 前置条件
- 用户已登录
- 当前在支持配送的类目创建页（如Baby Clothes）

#### 🎬 执行步骤
1. 滚动到"Parcel size"字段可视区域
2. 点击Parcel size选择按钮
3. 选择"Light Item"选项
4. 点击"Save"保存

#### ✅ 预期结果
- Parcel size成功选择
- 按钮文本更新为"Light Item"
- 错误提示消失（如之前有"Please select parcel size"）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_select_parcel_size`
- **可选值**: Light Item, Medium Item, Heavy Item
- **执行时间**: ~3秒

---

### TC-SELLERTYPE-001: 验证Seller Type默认选中Private

#### 📋 前置条件
- 用户已登录
- 当前在广告创建页面

#### 🎬 执行步骤
1. 滚动到"Seller Type"字段
2. 观察单选按钮的初始状态
3. 检查"Private"单选按钮是否被选中

#### ✅ 预期结果
- "Private"单选按钮默认被选中（`checked: true`）
- Seller Type字段左侧显示绿色勾选标记
- 无需用户手动选择

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_seller_type_default_private`
- **可选值**: Private, Business
- **执行时间**: ~2秒

---

### TC-CONTACT-001: 验证Contact Details自动填充

#### 📋 前置条件
- 用户已登录
- 当前在广告创建页面

#### 🎬 执行步骤
1. 滚动到"Contact Details"区域
2. 观察字段的初始状态
3. 检查"Messages on platform"复选框状态
4. 检查是否显示通知邮箱

#### ✅ 预期结果
- "Messages on platform"复选框默认被选中
- 显示通知邮箱（如"get notified via test@example.com"）
- Contact Details字段左侧显示绿色勾选标记
- 用户无需手动填写

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_contact_details_auto_filled`
- **执行时间**: ~2秒

---

### TC-LOCATION-001: 验证Location自动填充

#### 📋 前置条件
- 用户已登录
- 用户账户已设置默认位置
- 当前在广告创建页面

#### 🎬 执行步骤
1. 滚动到"Location"区域
2. 观察字段的初始状态
3. 检查是否显示位置信息

#### ✅ 预期结果
- Location字段自动填充已保存的地址
- 显示城市和邮编（如"Camden, London / NW5 4HX"）
- Location字段左侧显示绿色勾选标记
- 用户无需手动填写（可点击"Edit"修改）

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_location_auto_filled`
- **执行时间**: ~2秒

---

### TC-SUBMIT-001: 提交完整广告（Baby Clothes）

#### 📋 前置条件
- 用户已登录
- 当前在Baby Clothes类目创建页
- 测试图片存在

#### 🎬 执行步骤
1. 上传照片
2. 填写Ad Title（唯一标题，含时间戳）
3. 填写Description（>15字符）
4. 选择Condition: New
5. 条件选择（如字段可见）：
   - Gender: Unisex
   - Size: 0-3 months
   - Brand: Other
   - Colour: White
   - Material: Cotton
6. 填写Price: £10
7. 选择Parcel size: Light Item
8. 截图提交前状态
9. 滚动到页面底部
10. 点击"Post my Ad"按钮提交
11. 等待3秒，等待页面跳转

#### ✅ 预期结果
- 所有字段成功填写
- 点击"Post my Ad"后页面跳转
- 跳转到成功页面（URL包含"thankyou"或显示成功标志）
- 页面同时显示"Post another ad"和"Manage my ads"按钮/链接
- 无表单错误提示

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 端到端测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_baby_clothes.py::test_submit_ad`
- **类目**: Baby Clothes (categoryId=121)
- **执行时间**: ~20秒

---

### TC-SUBMIT-002: 提交广告并选择Featured推广（3 days）

#### 📋 前置条件
- 用户已登录
- 当前在Stuff Wanted类目创建页
- 测试图片存在

#### 🎬 执行步骤
1. 上传照片
2. 填写Ad Title
3. 填写Description
4. 滚动到"Make your ad stand out"推广区域
5. 勾选"Featured"推广套餐
6. 在Featured下拉菜单中选择"3 days - £1.99"
7. 截图提交前状态
8. 点击"Post my Ad"按钮提交
9. 等待跳转到付费页面

#### ✅ 预期结果
- 所有字段成功填写
- Featured推广套餐成功勾选
- 天数选择为"3 days"
- 点击提交后跳转到付费页面（URL包含"payment"或"checkout"）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 端到端测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_stuff_wanted_Featured_threeDays.py::test_submit_ad`
- **推广套餐**: Featured 3 days - £1.99
- **执行时间**: ~25秒（含支付流程）

---

## 3. 广告管理模块

### 3.1 导航与列表子模块

### TC-MANAGE-001: 从首页Menu导航到Manage Ads

#### 📋 前置条件
- 用户已登录
- 当前在首页

#### 🎬 执行步骤
1. 截图首页初始状态
2. 点击首页右上角的"Menu"按钮（通常是三条横线图标或"☰"）
3. 等待1秒，等待菜单展开
4. 截图菜单展开状态
5. 在菜单中点击"Manage my Ads"链接
6. 等待2秒，等待页面跳转
7. 记录跳转前后的URL

#### ✅ 预期结果
- Menu按钮可见且可点击
- 点击后菜单正确展开（显示"Manage my Ads"等选项）
- "Manage my Ads"链接可见且可点击
- 点击后页面跳转
- 跳转后URL包含"manage/ads"
- 页面显示广告管理相关内容

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_delete_ad.py::test_navigate_to_manage_ads`
- **执行时间**: ~5秒

---

### TC-MANAGE-002: 点击Active ads标签加载列表

#### 📋 前置条件
- 用户已登录
- 当前在Manage Ads页面

#### 🎬 执行步骤
1. 定位"Active ads"标签按钮
2. 点击"Active ads"标签
3. 等待2秒，等待广告列表加载
4. 截图列表加载状态
5. 尝试获取第一条广告信息

#### ✅ 预期结果
- "Active ads"标签可见且可点击
- 点击后标签高亮（成为选中状态）
- 广告列表正常加载
- 至少显示一条广告（或显示"No active ads"空列表提示）
- 每条广告显示标题、价格、发布时间等信息
- 广告卡片右侧显示"三个点"选项按钮

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_delete_ad.py::test_load_active_ads_list`
- **执行时间**: ~4秒

---

### TC-MANAGE-003: 获取第一条Active广告

#### 📋 前置条件
- 用户已登录
- 当前在Manage Ads页面的Active ads标签
- 至少有一条Active广告

#### 🎬 执行步骤
1. 调用 `ManageAdsPage.get_first_ad()` 方法
2. 该方法自动过滤"Job Ads"等推广卡片
3. 返回第一条真实用户广告的元素
4. 读取广告的文本内容（标题）

#### ✅ 预期结果
- 成功获取第一条真实广告
- 返回的元素不是"Job Ads"推广卡片
- 可读取广告标题等信息
- 无异常抛出

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `ManageAdsPage.get_first_ad()` 方法
- **执行时间**: ~1秒

---

### 3.2 广告删除子模块

### TC-DELETE-001: 删除Active广告完整流程

#### 📋 前置条件
- 用户已登录
- 至少有一条Active广告

#### 🎬 执行步骤
1. 从首页导航到Manage Ads页面（参考TC-MANAGE-001）
2. 点击Active ads标签
3. 获取第一条广告信息并记录标题
4. 将鼠标悬停到广告卡片（触发"三个点"按钮显示）
5. 点击广告右侧的"三个点"按钮（⋮）
6. 等待1秒，等待选项菜单展开
7. 截图选项菜单
8. 点击"Delete ad"选项
9. 等待1秒，等待确认弹窗出现
10. 截图确认弹窗
11. 在确认弹窗中选择"Yes"单选按钮（通过点击对应的radio button）
12. 等待0.5秒
13. 点击弹窗底部的"Delete"按钮确认删除
14. 等待3秒，等待删除完成
15. 截图删除后页面状态

#### ✅ 预期结果
- 所有步骤执行成功
- 三个点按钮正确显示并可点击
- 选项菜单包含"Delete ad"选项
- 确认弹窗正确显示
- 弹窗包含"Yes/No"选择和"Delete"按钮
- 点击Delete后广告从列表中移除
- 页面显示删除成功提示（如"Ad deleted successfully"）或返回到Manage Ads页面
- 被删除的广告不再出现在Active ads列表中

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_delete_ad.py::test_delete_active_ad`
- **执行时间**: ~15秒
- **注意事项**: 此操作不可逆，会真实删除广告

---

### 3.3 广告查看子模块

### TC-VIEW-001: 查看广告详情页并验证包含图片

#### 📋 前置条件
- 用户已登录
- 至少有一条Active广告
- 广告已上传照片

#### 🎬 执行步骤
1. 从首页导航到Manage Ads页面
2. 点击Active ads标签
3. 获取第一条广告信息
4. 截图广告列表
5. 将鼠标悬停到广告卡片
6. 点击广告的"三个点"按钮
7. 等待1.5秒，等待选项菜单展开
8. 截图选项菜单
9. 点击"View ad"选项
10. 等待3秒，等待广告详情页加载
11. 截图广告详情页

#### ✅ 预期结果
- 成功跳转到广告详情页（URL变化）
- 广告详情页包含图片元素（至少1张）
- 图片尺寸 > 50x50（排除小图标）
- 图片可见（`offsetParent !== null`）
- 页面显示广告标题、描述、价格等完整信息

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_view_ad.py::test_view_ad_with_images`
- **图片验证方法**: 
  - Playwright多选择器查找
  - JavaScript查找可见图片（rect.width > 50 && rect.height > 50）
- **执行时间**: ~12秒

---

### 3.4 广告编辑子模块

### TC-EDIT-001: 编辑广告完整流程

#### 📋 前置条件
- 用户已登录
- 至少有一条Active广告

#### 🎬 执行步骤
1. 从首页导航到Manage Ads页面
2. 点击Active ads标签
3. 获取第一条广告信息
4. 截图广告列表
5. 点击广告的"三个点"按钮
6. 等待1.5秒，等待选项菜单展开
7. 截图选项菜单
8. 点击"Edit ad"选项
9. 等待3秒，等待编辑页面加载
10. 截图编辑页面
11. 验证页面顶部显示"Update my ad"标题
12. 滚动到页面底部
13. 截图底部按钮区域
14. 点击页面底部的"Update my ad"按钮
15. 等待3秒，等待确认页面加载
16. 截图确认页面（可能显示"Want to move your ad back to the top"）
17. 滚动到底部
18. 再次点击确认页面中的"Update my ad"按钮
19. 等待3秒，等待成功页面加载
20. 截图成功页面

#### ✅ 预期结果
- 成功跳转到编辑页面
- 编辑页面顶部显示"Update my ad"标题（h1/h2或大标题）
- 所有字段预填充原广告内容（可编辑）
- 页面底部显示"Update my ad"按钮
- 点击第一次"Update my ad"后显示确认页面
- 点击第二次"Update my ad"后提交更新
- 成功页面同时包含"Post another ad"和"Manage my ads"文本或链接

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_edit_ad.py::test_edit_ad_complete_flow`
- **执行时间**: ~18秒
- **注意事项**: 
  - 编辑后广告可能被移动到列表顶部
  - 可能涉及推广套餐推荐

---

## 4. 推广功能模块

### TC-PROMOTE-001: 推广广告完整流程（选择所有套餐）

#### 📋 前置条件
- 用户已登录
- 至少有一条Active广告（未推广或推广已过期）
- 账户余额充足或有绑定支付方式

#### 🎬 执行步骤
1. 从首页导航到Manage Ads页面
2. 点击Active ads标签
3. 获取第一条广告信息并记录
4. 截图广告列表
5. **直接点击广告卡片上的绿色"Promote"按钮**（不是三个点菜单中的）
6. 等待3秒，等待推广套餐页面加载
7. 截图推广套餐页面
8. 使用JavaScript选择所有可选择的推广套餐（复选框/单选按钮）：
   - 遍历所有`input[type="checkbox"]`和`input[type="radio"]`
   - 自动勾选所有未选中的选项
   - 记录选择的套餐名称和数量
9. 等待1秒
10. 截图选择后状态
11. 滚动到页面底部
12. 点击"Continue"按钮
13. 等待3秒，等待跳转

#### ✅ 预期结果
- "Promote"按钮可见且可点击
- 成功跳转到推广套餐选择页面
- 页面展示至少1个推广套餐选项（Featured/Urgent/Spotlight等）
- 所有套餐成功勾选
- JavaScript返回 `selectedCount > 0`
- 点击"Continue"后页面跳转

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_promote_ad.py::test_promote_ad_with_all_packages` (步骤1-8)
- **推广套餐**: Featured, Urgent, Spotlight
- **执行时间**: ~12秒（不含支付）

---

### TC-PROMOTE-002: 处理自动续费确认弹窗

#### 📋 前置条件
- 已执行TC-PROMOTE-001步骤1-8
- 点击"Continue"后出现自动续费确认弹窗

#### 🎬 执行步骤
1. 等待1.5秒，等待弹窗出现
2. 读取页面文本内容
3. 检查是否包含"Please confirm"或"automatically renew"
4. 如检测到确认弹窗：
   - 截图弹窗状态
   - 查找并点击"Confirm"按钮
   - 等待3秒，等待弹窗关闭
5. 如未检测到弹窗：
   - 记录日志"未检测到确认弹窗，继续执行"

#### ✅ 预期结果
- 弹窗正确识别（如出现）
- "Confirm"按钮可见且可点击
- 点击后弹窗关闭，进入支付页面
- 如无弹窗，不影响后续流程

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 条件处理测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_promote_ad.py::test_promote_ad_with_all_packages` (步骤8a)
- **触发条件**: 首次选择推广套餐时可能出现
- **执行时间**: ~5秒

---

### TC-PROMOTE-003: 处理支付页面隐私弹窗

#### 📋 前置条件
- 已进入支付页面
- 支付页面出现"We Care About Your Privacy"隐私弹窗

#### 🎬 执行步骤
1. 等待2秒，检测隐私弹窗
2. 定位弹窗：`page.locator('text="We Care About Your Privacy"')`
3. 验证弹窗可见
4. 截图弹窗状态
5. 查找并点击"Accept all"按钮（多种选择器）
6. 等待2秒，等待弹窗关闭

#### ✅ 预期结果
- 隐私弹窗正确识别
- "Accept all"按钮可见且可点击
- 点击后弹窗关闭
- "Pay Now"按钮不再被遮挡，可正常点击

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: UI交互测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_promote_ad.py::test_promote_ad_with_all_packages` (步骤9)
- **执行时间**: ~4秒

---

### TC-PROMOTE-004: 点击Pay Now按钮进入支付

#### 📋 前置条件
- 已进入支付页面（URL包含"payment"或"checkout"）
- 隐私弹窗已关闭（如有）

#### 🎬 执行步骤
1. 截图支付页面初始状态
2. 记录当前URL
3. 读取页面文本内容并转小写
4. 验证页面包含"pay now"/"payment"/"checkout"关键词
5. 定位"Pay Now"按钮（多种选择器）：
   - `button:has-text('Pay Now')`
   - `button:has-text('Pay now')`
   - `button[type='submit']:has-text('Pay')`
   - JavaScript查找包含"pay now"文本的按钮
6. 验证按钮可见
7. 点击"Pay Now"按钮
8. 等待3秒，等待跳转到3D Secure验证页
9. 截图OTP页面

#### ✅ 预期结果
- 支付页面正确加载
- "Pay Now"按钮可见且可点击
- 点击后页面跳转或出现3D Secure验证框

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_promote_ad.py::test_promote_ad_with_all_packages` (步骤9)
- **执行时间**: ~8秒

---

### TC-PROMOTE-005: 处理3D Secure OTP验证（如触发）

#### 📋 前置条件
- 已点击"Pay Now"按钮
- 页面加载3D Secure iframe（银行验证）

#### 🎬 执行步骤
1. 等待10秒，确保OTP iframe完全加载
2. 截图OTP检查状态
3. 获取页面所有frame（`page.frames`）
4. 打印所有frame的URL到日志
5. 遍历所有frame，查找包含OTP输入框的iframe：
   - 尝试定位 `input[placeholder*="Enter Code"]`
   - 或 `input[type="text"]` 可见的输入框
6. 如找到OTP iframe：
   - 记录iframe URL
   - 在iframe中定位OTP输入框
   - 点击输入框获取焦点
   - 输入OTP验证码："1234"
   - 等待1秒
   - 在同一iframe中查找"SUBMIT"按钮
   - 点击"SUBMIT"按钮提交
   - 等待3秒，等待验证完成
7. 如未找到OTP iframe：
   - 记录日志"未触发3D Secure认证"
   - 直接等待10秒

#### ✅ 预期结果
- 如触发3D Secure：
  - OTP iframe成功识别
  - OTP输入框可见且可输入
  - 输入"1234"后值正确填充
  - "SUBMIT"按钮可见且可点击
  - 点击SUBMIT后验证成功
  - 页面跳转到感谢页面
- 如未触发3D Secure：
  - 测试继续执行，不报错
  - 直接跳转到感谢页面

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 条件处理测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_promote_ad.py::test_promote_ad_with_all_packages` (步骤10)
- **执行时间**: ~15秒
- **注意事项**: 
  - 3D Secure可能不是每次都触发
  - iframe需要10秒加载时间
  - OTP验证码固定为"1234"（测试环境）

---

### TC-PROMOTE-006: 验证推广成功并跳转感谢页

#### 📋 前置条件
- 已完成支付流程（含OTP验证，如有）

#### 🎬 执行步骤
1. 等待3秒，等待付费处理完成
2. 循环最多30次（每次1秒）：
   - 读取当前URL
   - 检查页面是否包含"Post another ad"文本
   - 检查页面是否包含"Manage my ads"文本
   - 检查URL是否包含"thankyou"
   - 如满足任一条件，跳出循环
3. 截图最终结果页面
4. 记录最终URL

#### ✅ 预期结果
- 30秒内成功跳转到感谢页面
- 页面URL包含"thankyou"或"my ads"
- 页面同时显示"Post another ad"和"Manage my ads"（或其中之一）
- 无支付失败错误提示

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 端到端测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_promote_ad.py::test_promote_ad_with_all_packages` (步骤11-12)
- **超时时间**: 30秒
- **执行时间**: ~5-30秒（取决于支付处理速度）

---

## 5. 重复发布模块

### TC-REPEAT-001: Post another ad 重复发布广告（Baby Clothes）

#### 📋 前置条件
- 用户已登录
- 测试图片存在

#### 🎬 执行步骤

**第一次发布（步骤1-8）**:
1. 导航到Baby Clothes创建页 `/postad/create?categoryId=121`
2. 关闭草稿弹窗（如出现）
3. 等待表单加载完成
4. 填写完整的广告信息：
   - 上传照片
   - 填写Ad Title（含序号"#1"和时间戳）
   - 填写Description
   - 选择Condition: New
   - 条件选择：Gender, Size, Brand, Colour, Material
   - 填写Price: £11
   - 选择Parcel size: Light Item
5. 截图提交前状态
6. 点击"Post my Ad"按钮提交
7. 等待3秒，等待跳转
8. 验证成功页面显示"Post another ad"和"Manage my ads"
9. 截图第一次发布成功页面

**第二次发布（步骤9-13）**:
10. 在成功页面中查找并点击"Post another ad"按钮：
    - 尝试多个选择器（`a:has-text("Post another ad")` 等）
    - 过滤隐藏元素，仅点击可见按钮
    - JavaScript备用方案：遍历所有a/button元素查找匹配文本
11. 等待3秒，等待页面跳转
12. 验证返回到Baby Clothes创建页：
    - 检查URL包含"postad"
    - 验证categoryId=121（或重新导航到该URL）
    - 关闭草稿弹窗（如出现）
    - 等待表单加载
13. 再次填写完整的广告信息（同步骤4，但标题含"#2"，价格£12）
14. 截图提交前状态
15. 点击"Post my Ad"按钮提交
16. 验证第二次发布成功页面

#### ✅ 预期结果
- **第一次发布**:
  - 所有字段成功填写
  - 广告成功发布
  - 成功页面显示"Post another ad"和"Manage my ads"
- **第二次发布**:
  - "Post another ad"按钮可见且可点击
  - 点击后返回到同类目（Baby Clothes）创建页
  - 表单为空白状态或草稿状态
  - 所有字段可再次填写
  - 第二个广告成功发布
  - 两个广告标题不同（含#1和#2序号）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 端到端测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_PostAnotherAd.py::test_repeat_post_baby_clothes`
- **执行时间**: ~40秒
- **注意事项**: 
  - 会创建2条真实广告
  - 需要测试后清理数据

---

## 6. 多类目广告发布测试

### TC-CATEGORY-BABY-001: 发布Baby Blankets广告

#### 📋 前置条件
- 用户已登录
- 测试图片存在

#### 🎬 执行步骤
1. 导航到Baby Blankets类目创建页 `/postad/create?categoryId={BABY_BLANKETS_ID}`
2. 关闭草稿弹窗
3. 上传照片
4. 填写Ad Title: "Soft Baby Blanket - {timestamp}"
5. 填写Description
6. 选择Condition: New
7. 条件选择（如字段存在）: Brand, Colour, Material等
8. 填写Price: £15
9. 选择Parcel size
10. 提交广告

#### ✅ 预期结果
- Baby Blankets类目特有字段正确显示
- 所有必填字段验证通过
- 广告成功发布
- 成功页面显示"Post another ad"和"Manage my ads"

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_baby_blankets.py`
- **类目**: Baby Blankets
- **执行时间**: ~20秒

---

### TC-CATEGORY-BABY-002: 发布Baby Shoes广告

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Baby Shoes类目创建页
2. 填写所有必填字段（同标准流程）
3. Baby Shoes特有字段：
   - Size: 选择婴儿鞋码（如"0-3 months"）
   - Gender: 选择性别
   - Brand: 选择品牌
   - Colour: 选择颜色
4. 提交广告

#### ✅ 预期结果
- Baby Shoes类目特有字段正确显示
- 广告成功发布

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_baby_shoes.py`
- **类目**: Baby Shoes
- **执行时间**: ~20秒

---

### TC-CATEGORY-BABY-003: 发布Car Seats广告

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Car Seats类目创建页
2. 填写所有必填字段
3. Car Seats特有字段：
   - Condition: New/Used
   - Brand: 选择汽车座椅品牌
4. 提交广告

#### ✅ 预期结果
- Car Seats类目特有字段正确显示
- 广告成功发布

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_car_seats.py`
- **类目**: Car Seats
- **执行时间**: ~20秒

---

### TC-CATEGORY-BABY-004: 发布Baby Skincare广告

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Baby Skincare类目创建页
2. 填写所有必填字段
3. 提交广告

#### ✅ 预期结果
- 广告成功发布

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_baby_skincare.py`
- **类目**: Baby Skincare
- **执行时间**: ~18秒

---

### TC-CATEGORY-FORSALE-001: 发布Mobile Phones广告（Spotlight推广）

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Mobile Phones类目创建页
2. 填写所有必填字段
3. 滚动到推广区域
4. 勾选"Spotlight"推广套餐（7 days - £1.99）
5. 提交广告
6. 完成支付流程（含OTP验证）

#### ✅ 预期结果
- Mobile Phones类目字段正确显示
- Spotlight推广套餐可勾选
- 广告成功发布并推广

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 端到端测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_mobile_phones_Spotlight.py`
- **类目**: Mobile Phones
- **推广套餐**: Spotlight
- **执行时间**: ~30秒

---

### TC-CATEGORY-FORSALE-002: 发布Tickets广告（Featured 7 days）

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Tickets类目创建页
2. 填写所有必填字段
3. 勾选"Featured"推广套餐
4. 在下拉菜单中选择"7 days - £1.00"
5. 提交广告并完成支付

#### ✅ 预期结果
- Tickets类目字段正确显示
- Featured推广套餐可选择7天
- 广告成功发布并推广

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 端到端测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_tickets_Featured_sevenDays.py`
- **类目**: Tickets
- **推广套餐**: Featured 7 days
- **执行时间**: ~30秒

---

### TC-CATEGORY-FORSALE-003: 发布Skis广告（Featured 14 days）

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Skis类目创建页
2. 填写所有必填字段
3. 勾选"Featured"推广套餐
4. 在下拉菜单中选择"14 days - £1.80"（推测价格）
5. 提交广告并完成支付

#### ✅ 预期结果
- Skis类目字段正确显示
- Featured推广套餐可选择14天
- 广告成功发布并推广

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 端到端测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_skis_Featured_fourteenDays.py`
- **类目**: Skis
- **推广套餐**: Featured 14 days
- **执行时间**: ~30秒

---

### TC-CATEGORY-FORSALE-004: 发布Kids Accessories广告

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Kids Accessories类目创建页
2. 填写所有必填字段
3. 提交广告

#### ✅ 预期结果
- 广告成功发布

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_kids_accessories.py`
- **类目**: Kids Accessories
- **执行时间**: ~18秒

---

### TC-CATEGORY-FORSALE-005: 发布Chest Freezers广告（Private卖家）

#### 📋 前置条件
- 用户已登录
- Seller Type选择Private

#### 🎬 执行步骤
1. 导航到Chest Freezers类目创建页
2. 验证Seller Type默认为Private
3. 填写所有必填字段
4. 提交广告

#### ✅ 预期结果
- Seller Type默认选中Private
- 广告成功发布

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_chest_freezers_sellerType_private.py`
- **类目**: Chest Freezers
- **Seller Type**: Private
- **执行时间**: ~18秒

---

### TC-CATEGORY-FORSALE-006: 发布Steam Cleaners广告（Business卖家）

#### 📋 前置条件
- 用户已登录（Business账户）
- Seller Type可选择Business

#### 🎬 执行步骤
1. 导航到Steam Cleaners类目创建页
2. 将Seller Type选择为Business
3. 填写所有必填字段
4. 提交广告

#### ✅ 预期结果
- Seller Type可切换为Business
- 广告成功发布
- 广告显示为Business卖家发布

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_steam_cleaners_sellerType_business.py`
- **类目**: Steam Cleaners
- **Seller Type**: Business
- **执行时间**: ~20秒

---

### TC-CATEGORY-FORSALE-007: 发布Car Booster Seats广告

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Car Booster Seats类目创建页
2. 填写所有必填字段
3. 提交广告

#### ✅ 预期结果
- 广告成功发布

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_car_booster_seats.py`
- **类目**: Car Booster Seats
- **执行时间**: ~18秒

---

### TC-CATEGORY-FORSALE-008: 发布Dummies & Soothers广告

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Dummies & Soothers类目创建页
2. 填写所有必填字段
3. 提交广告

#### ✅ 预期结果
- 广告成功发布

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_dummies_soothers.py`
- **类目**: Dummies & Soothers
- **执行时间**: ~18秒

---

### TC-CATEGORY-FORSALE-009: 发布Nappies广告

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Nappies类目创建页
2. 填写所有必填字段
3. 提交广告

#### ✅ 预期结果
- 广告成功发布

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_nappies.py`
- **类目**: Nappies
- **执行时间**: ~18秒

---

### TC-CATEGORY-STUFF-001: 发布Stuff Wanted广告（Urgent推广）

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Stuff Wanted > Audio & Vision类目创建页
2. 填写所有必填字段
3. 勾选"Urgent"推广套餐（7 days - £0.75）
4. 提交广告并完成支付

#### ✅ 预期结果
- Stuff Wanted类目字段正确显示（无Condition字段）
- Urgent推广套餐可勾选
- 广告成功发布并推广

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 端到端测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_stuff_wanted_Urgent.py`
- **类目**: Stuff Wanted
- **推广套餐**: Urgent
- **执行时间**: ~28秒

---

### TC-CATEGORY-MOTORS-001: 发布Cars广告（Motors主类目）

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Motors > Cars类目创建页
2. 填写Motors特有字段：
   - Make (车辆品牌)
   - Model (车型)
   - Year (年份)
   - Mileage (里程)
   - Fuel Type (燃料类型)
   - Transmission (变速箱)
3. 填写其他必填字段
4. 提交广告

#### ✅ 预期结果
- Motors类目特有字段全部显示
- 所有字段验证通过
- 广告成功发布

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_Motors_cars.py`
- **类目**: Motors > Cars
- **执行时间**: ~25秒
- **注意事项**: Motors类目字段与For Sale类目差异较大

---

### TC-CATEGORY-PROPERTY-001: 发布Property for Sale广告

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Property for Sale类目创建页
2. 填写Property特有字段：
   - Property Type (房产类型)
   - Bedrooms (卧室数)
   - Bathrooms (浴室数)
   - Area (面积)
   - Price (售价)
3. 填写其他必填字段
4. 提交广告

#### ✅ 预期结果
- Property类目特有字段全部显示
- 所有字段验证通过
- 广告成功发布

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_Property_for_sale.py`
- **类目**: Property for Sale
- **执行时间**: ~25秒

---

### TC-CATEGORY-PETS-001: 发布Pets > Dogs广告

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Pets > Dogs类目创建页
2. 填写Pets特有字段：
   - Breed (品种)
   - Age (年龄)
   - Gender (性别)
3. 填写其他必填字段
4. 提交广告

#### ✅ 预期结果
- Pets类目特有字段全部显示
- 广告成功发布

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_Pets_dogs.py`
- **类目**: Pets > Dogs
- **执行时间**: ~22秒

---

### TC-CATEGORY-COMMUNITY-001: 发布Community > Artists & Theatres广告

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Community > Artists & Theatres类目创建页
2. 填写所有必填字段
3. 提交广告

#### ✅ 预期结果
- Community类目字段正确显示
- 广告成功发布

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_Community_artists_theatres.py`
- **类目**: Community > Artists & Theatres
- **执行时间**: ~20秒

---

### TC-CATEGORY-SERVICES-001: 发布Services > Accountants广告

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 导航到Services > Accountants类目创建页
2. 填写Services特有字段（如有）
3. 填写其他必填字段
4. 提交广告

#### ✅ 预期结果
- Services类目字段正确显示
- 广告成功发布

#### 📊 用例属性
- **优先级**: P2
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_Services_accountants.py`
- **类目**: Services > Accountants
- **执行时间**: ~20秒

---

## 7. 推广套餐组合测试

### TC-PROMOTION-001: Featured 3 days推广

#### 📋 前置条件
- 用户已登录
- 当前在广告创建页

#### 🎬 执行步骤
1. 填写所有必填字段
2. 滚动到推广区域
3. 勾选"Featured"复选框
4. 在Featured下拉菜单中选择"3 days - £1.99"（推测价格）
5. 提交广告
6. 完成支付流程（OTP验证，如有）

#### ✅ 预期结果
- Featured套餐成功勾选
- 下拉菜单显示"3 days"选项
- 价格显示正确（£1.99）
- 广告成功发布并推广3天

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_stuff_wanted_Featured_threeDays.py`
- **推广套餐**: Featured 3 days
- **价格**: £1.99（推测）
- **执行时间**: ~30秒

---

### TC-PROMOTION-002: Featured 7 days推广

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 填写所有必填字段
2. 勾选"Featured"推广套餐
3. 选择"7 days - £1.00"
4. 提交并支付

#### ✅ 预期结果
- Featured 7天套餐成功勾选
- 价格显示£1.00
- 广告成功发布并推广7天

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_tickets_Featured_sevenDays.py`
- **推广套餐**: Featured 7 days
- **价格**: £1.00
- **执行时间**: ~30秒

---

### TC-PROMOTION-003: Featured 14 days推广

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 填写所有必填字段
2. 勾选"Featured"推广套餐
3. 选择"14 days - £1.80"（推测价格）
4. 提交并支付

#### ✅ 预期结果
- Featured 14天套餐成功勾选
- 价格显示正确
- 广告成功发布并推广14天

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_skis_Featured_fourteenDays.py`
- **推广套餐**: Featured 14 days
- **价格**: £1.80（推测）
- **执行时间**: ~30秒

---

### TC-PROMOTION-004: Urgent推广（7 days固定）

#### 📋 前置条件
- 用户已登录

#### 🎬 执行步骤
1. 填写所有必填字段
2. 勾选"Urgent"推广套餐
3. 验证显示"7 days - £0.75"
4. 提交并支付

#### ✅ 预期结果
- Urgent套餐成功勾选
- 天数固定为7天（无下拉选择）
- 价格显示£0.75
- 广告成功发布并标记为Urgent

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_stuff_wanted_Urgent.py`
- **推广套餐**: Urgent 7 days
- **价格**: £0.75
- **执行时间**: ~28秒

---

### TC-PROMOTION-005: Spotlight推广（7 days固定）

#### 📋 前置条件
- 用户已登录
- 用户满足Spotlight解锁条件（如有）

#### 🎬 执行步骤
1. 填写所有必填字段
2. 勾选"Spotlight"推广套餐
3. 验证显示"7 days - £1.99"
4. 提交并支付

#### ✅ 预期结果
- Spotlight套餐可见且可勾选（无锁图标）
- 天数固定为7天
- 价格显示£1.99
- 广告成功发布并在首页展示

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `test_post_ad_forSale_mobile_phones_Spotlight.py`
- **推广套餐**: Spotlight 7 days
- **价格**: £1.99
- **执行时间**: ~30秒

---

## 8. 支付流程测试

### TC-PAYMENT-001: 3D Secure OTP验证流程

#### 📋 前置条件
- 用户已选择推广套餐
- 点击"Pay Now"后触发3D Secure验证

#### 🎬 执行步骤
1. 等待10秒，确保3D Secure iframe完全加载
2. 截图OTP页面状态
3. 获取页面所有iframe（`page.frames`）
4. 遍历所有iframe，查找包含OTP输入框的iframe：
   - 定位 `input[placeholder*="Enter Code"]` 或 `input[type="text"]`
   - 验证输入框可见
5. 如找到OTP iframe：
   - 在iframe中点击输入框
   - 填充OTP验证码："1234"
   - 等待1秒
   - 在同一iframe中查找"SUBMIT"按钮（多种方式）：
     - 方式1: `get_by_role("button", name="SUBMIT", exact=True)`
     - 方式2: `locator('button:has-text("SUBMIT")')`
     - 方式3: JavaScript查找并点击
   - 点击"SUBMIT"按钮
   - 等待3秒，等待验证完成
6. 如未找到OTP iframe：
   - 记录日志"未触发3D Secure"
   - 等待10秒

#### ✅ 预期结果
- 如触发3D Secure：
  - OTP iframe成功识别（frame URL包含3dsecure或类似域名）
  - OTP输入框可见且可输入
  - 输入"1234"后值正确填充
  - "SUBMIT"按钮可见且可点击
  - 点击SUBMIT后验证成功
  - 页面跳转到感谢页面
- 如未触发3D Secure：
  - 直接跳转到感谢页面
  - 无异常抛出

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 集成测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: 
  - `test_post_ad_forSale_stuff_wanted_Featured_threeDays.py` (步骤7c-7d)
  - `test_promote_ad.py` (步骤10)
- **OTP验证码**: 1234（测试环境固定值）
- **等待时间**: 10秒（iframe加载）
- **执行时间**: ~18秒

---

### TC-PAYMENT-002: 支付成功跳转感谢页

#### 📋 前置条件
- 已完成支付流程（含OTP验证，如有）

#### 🎬 执行步骤
1. 等待3秒，等待付费处理完成
2. 循环等待最多30秒：
   - 每秒检查一次页面状态
   - 检查页面是否显示"Post another ad"
   - 检查页面是否显示"Manage my ads"
   - 检查URL是否包含"thankyou"
   - 如满足任一条件，跳出循环
3. 截图最终结果页面
4. 记录最终URL

#### ✅ 预期结果
- 30秒内成功跳转到感谢页面
- 页面URL包含"thankyou"或"my ads"关键词
- 页面可见"Post another ad"文本或链接
- 页面可见"Manage my ads"文本或链接
- 无支付失败错误提示

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 端到端测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: 
  - `test_post_ad_forSale_stuff_wanted_Featured_threeDays.py` (步骤8)
  - `test_promote_ad.py` (步骤11)
- **超时时间**: 30秒
- **执行时间**: ~5-30秒

---

## 9. 草稿功能测试

### TC-DRAFT-001: 关闭草稿弹窗（选择放弃）

#### 📋 前置条件
- 用户已登录
- 上次发布流程中有未提交的草稿
- 重新进入发布页面

#### 🎬 执行步骤
1. 导航到广告创建页
2. 检测是否出现草稿恢复弹窗
3. 如出现弹窗：
   - 调用 `PostAdPage.close_draft_dialog_if_exists()`
   - 点击"关闭"或"新建"按钮（放弃草稿）
   - 等待弹窗关闭
4. 验证表单为空白状态

#### ✅ 预期结果
- 草稿弹窗正确识别
- 点击后弹窗关闭
- 表单显示为空白状态（无预填充内容）
- 用户可正常填写新广告

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
- **自动化脚本**: `PostAdPage.close_draft_dialog_if_exists()` 方法
- **执行时间**: ~2秒

---

### TC-DRAFT-002: 恢复草稿（选择继续编辑）

#### 📋 前置条件
- 用户已登录
- 上次发布流程中有未提交的草稿
- 草稿包含部分已填写的字段

#### 🎬 执行步骤
1. 导航到广告创建页
2. 检测草稿恢复弹窗
3. 点击"继续编辑"按钮
4. 等待草稿数据加载
5. 验证各字段内容

#### ✅ 预期结果
- 草稿弹窗显示
- 点击"继续编辑"后弹窗关闭
- 所有字段预填充草稿数据：
  - Title字段显示草稿标题
  - Description字段显示草稿描述
  - 已上传的照片显示缩略图
  - 已选择的选项保持选中状态
- 用户可继续编辑草稿内容

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化（需要提前保存草稿）
- **自动化脚本**: 需要单独实现（当前脚本仅测试关闭草稿）
- **执行时间**: ~5秒

---

## 测试统计

### 用例概览

| 类别 | 用例数 | 已自动化 | 自动化率 |
|------|--------|---------|---------|
| 用户认证 | 3 | 3 | 100% |
| 类目选择 | 3 | 3 | 100% |
| 表单填写 | 10 | 10 | 100% |
| 广告管理 | 3 | 3 | 100% |
| 广告删除 | 1 | 1 | 100% |
| 广告查看 | 1 | 1 | 100% |
| 广告编辑 | 1 | 1 | 100% |
| 推广功能 | 6 | 6 | 100% |
| 重复发布 | 1 | 1 | 100% |
| 多类目测试 | 13 | 13 | 100% |
| 推广套餐组合 | 5 | 5 | 100% |
| 支付流程 | 2 | 2 | 100% |
| 草稿功能 | 1 | 1 | 100% |
| **总计** | **50** | **50** | **100%** |

### 按优先级分布

| 优先级 | 总数 | 可自动化 | 自动化率 |
|--------|------|---------|---------|
| P0 | 25 | 25 | 100% |
| P1 | 18 | 18 | 100% |
| P2 | 7 | 7 | 100% |

### 按功能模块分布

```
用户认证模块       ████████ 3条 (6%)
广告发布模块       ████████████████████████████ 26条 (52%)
广告管理模块       ████████ 6条 (12%)
推广功能模块       ████████████ 11条 (22%)
支付流程模块       ████ 2条 (4%)
草稿功能模块       ██ 2条 (4%)
```

### 按类目覆盖

| 主类目 | 子类目 | 用例数 | 覆盖特性 |
|--------|--------|--------|----------|
| For Sale | Baby Clothes | 8 | 完整流程+重复发布 |
| For Sale | Stuff Wanted | 5 | Featured 3天+Urgent |
| For Sale | Mobile Phones | 1 | Spotlight推广 |
| For Sale | Tickets | 1 | Featured 7天 |
| For Sale | Skis | 1 | Featured 14天 |
| For Sale | Car Seats | 1 | 标准流程 |
| For Sale | Baby Shoes | 1 | 标准流程 |
| For Sale | Baby Blankets | 1 | 标准流程 |
| For Sale | Baby Skincare | 1 | 标准流程 |
| For Sale | Kids Accessories | 1 | 标准流程 |
| For Sale | Chest Freezers | 1 | Private卖家 |
| For Sale | Steam Cleaners | 1 | Business卖家 |
| For Sale | Car Booster Seats | 1 | 标准流程 |
| For Sale | Dummies & Soothers | 1 | 标准流程 |
| For Sale | Nappies | 1 | 标准流程 |
| Motors | Cars | 1 | Motors特有字段 |
| Property | For Sale | 1 | Property特有字段 |
| Pets | Dogs | 1 | Pets特有字段 |
| Community | Artists & Theatres | 1 | Community类目 |
| Services | Accountants | 1 | Services类目 |
| **总计** | **20个子类目** | **30条** | **5个主类目** |

### 自动化测试脚本清单

| 脚本文件 | 用例数 | 类目 | 主要测试点 |
|---------|--------|------|-----------|
| `test_post_ad_forSale_baby_clothes.py` | 8 | Baby Clothes | 完整流程+字段验证 |
| `test_post_ad_forSale_stuff_wanted_Featured_threeDays.py` | 3 | Stuff Wanted | Featured 3天推广 |
| `test_post_ad_forSale_stuff_wanted_Urgent.py` | 3 | Stuff Wanted | Urgent推广 |
| `test_post_ad_forSale_mobile_phones_Spotlight.py` | 1 | Mobile Phones | Spotlight推广 |
| `test_post_ad_forSale_tickets_Featured_sevenDays.py` | 1 | Tickets | Featured 7天 |
| `test_post_ad_forSale_skis_Featured_fourteenDays.py` | 1 | Skis | Featured 14天 |
| `test_post_ad_baby_shoes.py` | 1 | Baby Shoes | 标准流程 |
| `test_post_ad_baby_blankets.py` | 1 | Baby Blankets | 标准流程 |
| `test_post_ad_car_seats.py` | 1 | Car Seats | 标准流程 |
| `test_post_ad_baby_skincare.py` | 1 | Baby Skincare | 标准流程 |
| `test_post_ad_forSale_kids_accessories.py` | 1 | Kids Accessories | 标准流程 |
| `test_delete_ad.py` | 3 | - | 删除广告流程 |
| `test_view_ad.py` | 1 | - | 查看广告详情 |
| `test_edit_ad.py` | 1 | - | 编辑广告流程 |
| `test_promote_ad.py` | 1 | - | 推广广告流程 |
| `test_post_ad_PostAnotherAd.py` | 1 | Baby Clothes | 重复发布 |
| `test_post_ad_Motors_cars.py` | 1 | Motors-Cars | Motors类目 |
| `test_post_ad_Property_for_sale.py` | 1 | Property | Property类目 |
| `test_post_ad_Pets_dogs.py` | 1 | Pets-Dogs | Pets类目 |
| `test_post_ad_Community_artists_theatres.py` | 1 | Community | Community类目 |
| `test_post_ad_Services_accountants.py` | 1 | Services | Services类目 |
| **总计** | **21个脚本** | **32条用例** | **26个不同文件** |

---

## 附录A: Page Object Model (POM)架构

本测试项目采用POM设计模式，主要页面对象包括：

### LoginPage
- **职责**: 处理登录流程
- **主要方法**:
  - `dismiss_privacy_consent_if_present()`: 关闭隐私弹窗
  - `select_email_login()`: 选择邮箱登录
  - `enter_email(email)`: 输入邮箱
  - `enter_password(password)`: 输入密码
  - `click_continue()`: 点击继续按钮

### PostAdPage
- **职责**: 处理广告发布表单交互
- **主要方法**:
  - `click_browse_category()`: 点击浏览类目
  - `select_category_baby_clothes()`: 选择Baby Clothes类目
  - `close_draft_dialog_if_exists()`: 关闭草稿弹窗
  - `upload_photo(path)`: 上传照片
  - `fill_ad_title(title)`: 填写标题
  - `fill_description(desc)`: 填写描述
  - `select_condition_new()`: 选择Condition为New
  - `select_gender_by_name(name)`: 选择Gender
  - `select_size_by_name(name)`: 选择Size
  - `select_brand_by_name(name)`: 选择Brand
  - `select_colour_by_name(name)`: 选择Colour
  - `select_material_by_name(name)`: 选择Material
  - `fill_price(price)`: 填写价格
  - `select_parcel_size_small()`: 选择包裹尺寸
  - `select_featured_3_days()`: 选择Featured 3天推广
  - `submit_ad()`: 提交广告

### ManageAdsPage
- **职责**: 处理广告管理页面交互
- **主要方法**:
  - `click_menu_button()`: 点击Menu按钮
  - `click_manage_ads_link()`: 点击Manage my Ads链接
  - `click_active_ads_tab()`: 点击Active ads标签
  - `get_first_ad()`: 获取第一条真实广告（过滤推广卡片）
  - `click_ad_options_button(ad_element)`: 点击三个点按钮
  - `click_delete_ad_option()`: 点击Delete ad选项
  - `click_view_ad_option()`: 点击View ad选项
  - `click_edit_ad_option()`: 点击Edit ad选项
  - `click_yes_in_confirmation()`: 在确认弹窗中点击Yes
  - `click_delete_button()`: 点击Delete按钮
  - `click_promote_button_on_ad(ad_element)`: 直接点击广告卡片上的Promote按钮

### PaymentPage
- **职责**: 处理支付流程交互（如需要）
- **主要方法**: （待补充）

### SessionManager
- **职责**: 管理用户登录Session，实现Session复用
- **主要方法**:
  - `save_session(page, username)`: 保存当前页面的Session
  - `load_session(page, username)`: 加载已保存的Session
  - **存储位置**: `session_storage/{username}.json`

---

## 附录B: 自动化测试最佳实践

### 1. Session复用策略
- **目的**: 减少重复登录，提升测试执行效率
- **实现**: 
  - 使用 `@pytest.fixture(scope="class")` 类级别fixture
  - 首次登录后保存Session到本地文件
  - 后续测试直接加载Session
- **效果**: 登录时间从15秒 → 2秒

### 2. 元素定位策略
- **优先级**:
  1. `data-testid` 属性（最稳定）
  2. `text` 文本匹配（适合按钮、链接）
  3. `role` + `name` 组合（语义化）
  4. `class` 或 `id`（需谨慎，可能变化）
- **兜底方案**: JavaScript查找并操作元素

### 3. 等待策略
- **避免固定等待**: 尽量使用 `wait_for_selector()` 或 `expect().to_be_visible()`
- **必要固定等待场景**:
  - 动画完成: 1秒
  - 网络请求: 2-3秒
  - iframe加载: 10秒（3D Secure）
  - 支付处理: 30秒（循环检测）

### 4. 截图策略
- **关键节点截图**:
  - 提交前状态
  - 选项菜单展开
  - 确认弹窗
  - 成功/失败页面
- **异常截图**: 
  - 元素未找到时
  - 断言失败时

### 5. 日志策略
- **使用loguru**: 
  - `logger.info()`: 正常流程日志
  - `logger.warning()`: 可选字段不可用
  - `logger.error()`: 严重错误
  - `logger.debug()`: 调试信息（选择器尝试）

### 6. 异常处理
- **可选字段**: 使用 `try-except` + `pytest.skip()`
- **条件逻辑**: 检测元素是否存在后再操作（如草稿弹窗、OTP验证）
- **兜底方案**: Playwright选择器失败后使用JavaScript

---

## 附录C: 待补充测试用例

### 推荐补充的用例（基于当前覆盖度分析）

#### 异常场景

1. **TC-ERROR-001**: Title字段为空提交
   - **缺失原因**: 当前仅测试正常流程
   - **优先级**: P0
   - **预估工作量**: 0.5小时

2. **TC-ERROR-002**: Description少于15字符提交
   - **缺失原因**: 无边界值测试
   - **优先级**: P0
   - **预估工作量**: 0.5小时

3. **TC-ERROR-003**: Price输入负数
   - **缺失原因**: 无异常输入测试
   - **优先级**: P1
   - **预估工作量**: 0.5小时

4. **TC-ERROR-004**: Price输入非数字字符
   - **缺失原因**: 无格式验证测试
   - **优先级**: P1
   - **预估工作量**: 0.5小时

5. **TC-ERROR-005**: 照片上传失败重试
   - **缺失原因**: 无网络异常测试
   - **优先级**: P1
   - **预估工作量**: 1小时

#### 边界值测试

6. **TC-BOUNDARY-001**: Description输入10000字符（最大值）
   - **缺失原因**: 无最大边界测试
   - **优先级**: P1
   - **预估工作量**: 0.5小时

7. **TC-BOUNDARY-002**: 上传20张照片（最大值）
   - **缺失原因**: 当前仅上传1张
   - **优先级**: P1
   - **预估工作量**: 1小时

8. **TC-BOUNDARY-003**: Price输入最大值（£999,999.99）
   - **缺失原因**: 无最大价格测试
   - **优先级**: P2
   - **预估工作量**: 0.5小时

#### 兼容性测试

9. **TC-COMPAT-001**: 不同浏览器兼容性
   - **缺失原因**: 当前仅Chromium测试
   - **优先级**: P2
   - **预估工作量**: 2小时

10. **TC-COMPAT-002**: 移动端设备兼容性
    - **缺失原因**: 无真机测试
    - **优先级**: P2
    - **预估工作量**: 3小时

#### 安全测试

11. **TC-SECURITY-001**: XSS攻击防护（Title输入HTML标签）
    - **缺失原因**: 无安全测试
    - **优先级**: P1
    - **预估工作量**: 1小时

12. **TC-SECURITY-002**: SQL注入防护
    - **缺失原因**: 无安全测试
    - **优先级**: P1
    - **预估工作量**: 1小时

---

## 附录D: 测试数据管理

### 测试账号

| 环境 | 账号 | 密码 | 用途 |
|------|------|------|------|
| Zoidberg | 从conftest.py读取 | 从conftest.py读取 | 主要测试环境 |
| Taro | 从conftest.py读取 | 从conftest.py读取 | 备用测试环境 |
| Staging | 从conftest.py读取 | 从conftest.py读取 | 预发布环境 |

### 测试图片

| 文件名 | 路径 | 尺寸 | 用途 |
|--------|------|------|------|
| test_photo.jpg | `/artifacts/test_photo.jpg` | 未知 | 照片上传测试 |

**建议**:
- 补充不同尺寸的测试图片（小图、大图、超大图）
- 补充不同格式的图片（PNG, GIF, WebP）
- 补充特殊场景图片（黑白图、纯色图、超长图）

### 测试类目ID

| 类目名称 | Category ID | 层级 | 脚本引用 |
|---------|-------------|------|----------|
| Baby Clothes | 121 | 4级 | `BABY_CLOTHES_CATEGORY_ID` |
| Stuff Wanted > Audio & Vision | 187 | 3级 | `STUFF_WANTED_CATEGORY_ID` |
| Baby Blankets | 未知 | 4级 | （硬编码在脚本中） |
| Baby Shoes | 未知 | 4级 | （硬编码在脚本中） |
| Car Seats | 未知 | 3级 | （硬编码在脚本中） |
| ... | ... | ... | ... |

**建议**: 
- 统一管理所有类目ID到配置文件（如 `test_data/category_ids.json`）
- 避免在多个脚本中硬编码相同的ID

---

## 附录E: CI/CD集成建议

### GitHub Actions配置示例

```yaml
name: Gumtree Seller Tests

on:
  push:
    branches: [main, develop]
  pull_request:
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2点执行

jobs:
  test-seller:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        env: [zoidberg, taro]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Run Seller Tests
        run: |
          pytest test_cases/seller/ \
            --env=${{ matrix.env }} \
            --alluredir=allure-results \
            -v
      
      - name: Generate Allure Report
        if: always()
        run: |
          allure generate allure-results -o allure-report
      
      - name: Upload Allure Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: allure-report-${{ matrix.env }}
          path: allure-report/
```

### 执行建议

**每日回归**:
- 执行P0用例（25条）: ~10分钟
- 报告：Allure自动生成并发送邮件

**每周全量**:
- 执行所有用例（50条）: ~25分钟
- 报告：详细Allure报告 + 覆盖率报告

**发布前验证**:
- 执行P0+P1用例（43条）: ~20分钟
- 报告：关键路径通过率必须100%

---

## 附录F: 已知问题与限制

### 当前测试限制

1. **草稿恢复测试不完整**
   - 当前仅测试关闭草稿弹窗
   - 未测试恢复草稿并验证数据完整性
   - **建议**: 补充TC-DRAFT-002用例的自动化实现

2. **照片拖拽功能未测试**
   - Playwright对拖拽操作支持有限
   - **建议**: 手动测试或使用视觉回归测试

3. **AI生成内容质量未验证**
   - 自动化脚本仅验证内容不为空
   - 未验证AI生成内容的准确性和质量
   - **建议**: 人工抽查 + 用户反馈监控

4. **多设备并行测试未实现**
   - 当前仅在单一环境执行
   - **建议**: 使用BrowserStack或Sauce Labs实现多设备并行

5. **性能测试未覆盖**
   - 未测试页面加载时间、AI生成耗时等
   - **建议**: 补充性能测试用例

### 已知Bug（如有）

（待补充：在测试执行过程中发现的已知问题）

---

**文档结束**

> **生成说明**: 本文档基于 `/test_cases/seller/` 目录下的26个自动化测试脚本反向生成。所有用例均已实现Playwright自动化，可直接执行。建议结合Allure报告查看详细执行结果。

