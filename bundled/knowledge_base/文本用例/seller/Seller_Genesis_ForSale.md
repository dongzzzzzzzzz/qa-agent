# AI Posting Genesis - For Sale Phase 1 测试分析报告（详细版）

> **生成时间**: 2026-03-30  
> **设计来源**: Figma - AI posting Genesis- For Sale - Phase 1  
> **产品阶段**: UI Phase 1  
> **设计师**: Vickie.Meng  
> **开始日期**: 2025年12月1日  
> **报告类型**: 详细版（约15000字）  

---

## 📌 一、功能概述

### 1.1 核心功能描述

AI Posting Genesis For Sale Phase 1 是Gumtree平台的智能化广告发布流程第一阶段,主要针对移动端(iOS)实现。该功能引入AI辅助能力,帮助卖家更高效地创建和发布For Sale类目的广告。

**核心特性**:
- 🤖 **AI智能填充**: 基于用户输入的标题/照片,AI自动生成广告描述和推荐类目
- 📱 **移动端优先**: 专为iPhone X及以上设备优化的流式交互
- 🎯 **简化流程**: 从类目选择到发布完成的完整路径简化
- ✨ **实时生成**: AI内容生成过程可视化,提供骨架屏加载效果

### 1.2 功能边界

**包含范围**:
- ✅ For Sale 主类目及所有子类目(如 Baby & Kids Stuff / Car Seats & Baby Carriers)
- ✅ 移动端(iOS)完整发布流程
- ✅ AI辅助内容生成(标题、描述)
- ✅ 照片上传(最多20张)
- ✅ 必填字段: 标题、描述、价格、类目、位置
- ✅ 可选字段: Item Specifics (Condition等)、推广选项(Featured/Urgent/Spotlight)
- ✅ 草稿保存与恢复
- ✅ 发布成功后的推广推荐

**不包含范围**:
- ❌ Jobs, Motors, Property等其他主类目
- ❌ 桌面端/Web端流程
- ❌ 高级编辑功能(如富文本编辑)
- ❌ 视频上传(仅支持YouTube链接)
- ❌ 批量发布

### 1.3 目标用户

- **个人卖家**: 希望快速发布二手物品的普通用户
- **小商家**: 需要频繁发布商品的个体经营者
- **新手用户**: 首次使用Gumtree发布广告的用户(AI辅助可降低门槛)

---

## 🔄 二、核心业务流程

### 2.1 主流程概览

```
开始 → 选择类目 → AI生成内容 → 填写详情 → 选择推广(可选) → 提交发布 → 成功页
```

### 2.2 详细流程拆解

#### 流程1: 类目选择
**入口**: 
- 用户点击首页"Sell"按钮
- 或从其他页面进入发帖流程

**交互步骤**:
1. **APP-sell页面**:
   - 展示搜索框: "e.g. Cars, Sofas, Bikes, Laptops"
   - 提示文案: "Or browse to find a category"
   - 用户可搜索或浏览类目

2. **搜索类目**:
   - 用户输入关键词(如"Bike")
   - 系统实时显示建议类目列表(suggested categories)
   - 展示完整路径,如: "For Sale > Phones > Mobile Phones & Telecoms > Mobile Phones > Google"

3. **浏览类目**:
   - 点击"browse"展开类目树
   - 多级类目选择(最多4级)
   - 示例: For Sale → Baby & Kids Stuff → Car Seats & Baby Carriers

4. **确认类目**:
   - 选中类目后进入发帖主页面
   - 顶部显示面包屑导航
   - 右上角"Edit"按钮可重新选择类目

**页面标识**:
- `APP-sell` (初始搜索页)
- `APP-sell / suggested categoried` (建议类目页)
- `APP-sell / browse` (浏览类目页)

---

#### 流程2: AI辅助内容生成

**触发时机**:
- 用户上传第一张照片后
- 或用户输入标题后

**生成过程**:
1. **Title优先场景** (AI posting - title first):
   - 用户先输入标题: "e.g. 'Vintage red leather jacket'"
   - 系统根据标题推荐类目
   - 用户选择类目后进入主表单

2. **Photo优先场景** (标准流程):
   - 用户上传照片
   - 系统识别物品并生成:
     - 推荐标题
     - 完整描述(15-10000字符)
     - 推荐类目标签(如: Dinning Tables, Dinning Chairs, Tableware)
   
3. **AI生成中状态**:
   - Title字段显示骨架屏动画(灰色矩形块)
   - Description字段显示3行骨架屏
   - 右上角显示"01"图标(加载动画)
   - 底部"Post"按钮保持可用(用户可随时修改)

4. **AI生成完成**:
   - 骨架屏消失,内容填充
   - Title示例: "input-text"(实际显示AI生成的标题)
   - Description示例: "This wooden dining table is in excellent condition and can be picked up by yourself. It is now on sale at a low price！"
   - Category建议标签自动展示(用户可选择)

**关键设计稿**:
- `Post- AI生成中` (7586.5, 1821) - 加载状态
- `Post- AI生成内容加载成功` (8422, 1821) - 完成状态
- `Post` (4983, 4234) - 类目建议标签展示

---

#### 流程3: 填写广告详情

**必填字段**:

1. **Photos** (必填,通过提示引导):
   - 位置: 页面顶部
   - 限制: 0/20张
   - 提示: "Ads with good pictures get more views and replies"
   - 按钮: "Add up to 20 images"
   - 可选: "Add a Youtube video link"(需额外付费£1.99)
   - 交互: 
     - 横向滚动展示
     - 长按拖拽调整顺序
     - 点击【X】删除照片

2. **Ad Title** (必填,标*):
   - 字段类型: 单行文本输入框
   - 验证规则: 无字符数限制(设计稿未显示)
   - Placeholder: 无(AI生成后直接填充)
   - 图标: 左侧显示类目图标(某些场景)

3. **Description** (必填,标*):
   - 字段类型: 多行文本域
   - 验证规则: 15-10000字符
   - 实时计数: "56/10000"
   - 提示文案: "15 characters minimum"
   - AI辅助: 可点击"Label"按钮使用AI重写/优化
   - 右上角: "Change"按钮(带旋转箭头图标) - 重新生成描述

4. **Category** (必填,隐式):
   - 展示: "For Sale / Baby & Kids Stuff / Car Seats & Baby Carriers"
   - 交互: 点击"Edit"按钮可修改
   - AI建议: 下方展示推荐子类目标签(Dinning Tables, Dinning Chairs, Tableware)
   - 标签可点击选中(复选框样式)

5. **Price** (必填,标*):
   - 字段类型: 数字输入框
   - 货币符号: £ (左侧固定显示)
   - 验证规则: 仅数字,最多2位小数(推测)
   - 示例值: "input-text" → 实际数字

6. **Location** (必填,标*):
   - 默认值: 基于用户账户设置(如"Camden, London")
   - 显示格式: "Camden, London / NW5 4HX"
   - 隐私提示: "We won't show your postcode or exact location on the ad."
   - 复选框: "Show a map on my ad" (展示Google地图预览)
   - 地图提示: "Only the approximate area will be shown"
   - 可编辑: 点击"Edit"按钮修改

**可选字段**:

7. **Item Specifics**:
   - 标签切换: "Required" / "Optional"
   - Required子字段:
     - **Condition**: 必填,点击展开选择(New/Used/For parts or not working等)
   - Optional子字段: 依类目而定(设计稿未详细展示)

8. **Contact Details** (必填,标*):
   - 默认值: "get notified via Vickie.meng@gumtree.com"
   - 复选框1: "Messages on platform" (平台站内信,默认勾选)
   - 复选框2: "Phone:" + 按钮"Add phone number"
   - 隐私提示: "We will never share your email address with users." + "Learn more"链接

**表单设计稿位置**:
- `APP-sell-SYI(for sale)/default` (2631, 5913) - 完整表单
- `M-post an ad` (1573, 9417) - 移动端优化版本

---

#### 流程4: 推广选项 (Make your ad stand out)

**入口位置**: 表单底部,Contact Details与Location之间

**可选推广套餐**:

1. **Featured** (推荐):
   - 描述: "Have your Ad appear at the top of the category listings for 3, 7 or 14 days."
   - 价格: 下拉选择 "7 days - £1.00" (默认)
   - 标签: "Recommended" (带绿色徽章)
   - 示例链接: "View example"

2. **Urgent**:
   - 描述: "Let people know you want to sell, rent or hire quickly."
   - 价格: "7 days - £0.75"
   - 标签: "Urgent"
   - 示例链接: "View example"

3. **Spotlight**:
   - 描述: "Have your Ad seen on the Gumtree homepage!"
   - 价格: "7 days - £1.99"
   - 标签: "Spotlight"
   - 示例链接: "View example"

**交互逻辑**:
- 复选框多选
- "Select all" 快捷全选按钮(底部)
- 选中后价格累加(设计稿未显示总价)

**设计稿位置**:
- `Frame 744` (0, 1243) - 推广选项完整模块
- `M-post an ad` 移动端版本

---

#### 流程5: 草稿保存与恢复

**自动草稿**:
- 触发: 用户填写部分信息后退出/关闭页面
- 存储: 本地或云端(设计稿未明确)
- 保留时长: 未知

**草稿恢复弹窗** (`Post- 加载草稿弹窗`):
- 触发时机: 用户重新进入发帖页面且有未完成草稿
- 弹窗内容:
  - 标题: "Pick up where you left off?"
  - 说明: "Do you wish to continue with your previous draft?"
  - 按钮1: "Label" (左侧,推测为"新建")
  - 按钮2: "Label" (右侧,推测为"继续编辑")
  - 关闭按钮: 右上角【X】

**设计稿位置**:
- `Post- 加载草稿弹窗` (10778, 1821)

---

#### 流程6: 提交与发布

**提交前验证**:
- 系统校验所有必填字段
- 错误状态显示 (`Post- error` 页面):
  - Photos: "supporting-text" (错误提示)
  - Title: "supporting-text" (错误提示)
  - Description: "supporting-text" (错误提示)
  - Category: "Please choose a category" (红色提示)
  - Condition: "supporting-text" (错误提示)
  - Price: "supporting-text" (错误提示)
  - Location: "supporting-text" (错误提示)

**提交按钮**:
- 位置: 页面底部固定
- 文案: "Post my Ad"
- 尺寸: 343x46
- 法律声明(按钮下方):
  - "By selecting Post My Ad you agree you've read and accepted our Terms of Use and Posting Rules"
  - "Please see our Privacy Notice for information regarding the processing of your data. Please visit our Contact Us pages to seek additional support."
  - 链接: Terms of Use, Posting Rules, Privacy Notice, Contact Us

**提交后状态**:
- 跳转到成功页面

**设计稿位置**:
- `Post- error` (8837, 1821) - 错误状态
- `Button` (688:48604) - 提交按钮

---

#### 流程7: 发布成功

**成功页面** (`Post-Succsee`):

1. **反馈提示**:
   - 图标: 成功图标(Frame 1079)
   - 主文案: "How was your overall" (体验反馈,两行文本)
   - 可能包含评分组件(Group 799)

2. **推广推荐模块** (Make your Ad stand out):
   - 标题: "Make your Ad stand out"
   - 副标题: "Label"
   - 展示3个推广选项卡片:
     - Featured (SYI. Promote options)
     - Urgent (SYI. Promote options)
     - Spotlight (带锁图标,可能需要解锁)
   - 每个卡片包含:
     - 套餐名称(Badge title)
     - 价格(Price)
     - 描述(Description)
     - "View example"链接
   - 复选框: "Select all"选项

3. **主按钮**:
   - 文案: Button (推测为"Post another ad"或"Done")
   - 尺寸: 343x48

**设计稿位置**:
- `Post-Succsee` (10085.75, 1821)

---

### 2.3 分支场景

#### 分支1: 不同的发帖起点

**场景A: Title优先**:
```
输入标题 → AI推荐类目 → 选择类目 → 填写详情(AI生成描述)
```

**场景B: Category优先**(标准流程):
```
选择类目 → 上传照片 → AI生成标题+描述 → 填写详情
```

**场景C: Browse浏览**:
```
Browse类目树 → 多级展开选择 → 进入表单
```

#### 分支2: 草稿处理

**有草稿场景**:
```
进入发帖页 → 弹窗提示草稿 → 选择"继续"/选择"新建"
```

**无草稿场景**:
```
进入发帖页 → 直接进入空白表单
```

#### 分支3: AI生成失败

**失败状态**:
- 生成超时(>30秒,推测)
- 网络错误
- AI服务不可用

**降级方案**:
- 显示错误提示: "supporting-text"
- 允许用户手动填写
- 保留"Change"按钮可重试

---

## 📊 三、数据与字段分析

### 3.1 所有字段详细分析

| 字段名 | 中文名 | 类型 | 必填 | 默认值 | 验证规则 | AI辅助 | 数据来源 | 备注 |
|--------|--------|------|------|--------|----------|--------|----------|------|
| Photos | 照片 | File Upload | 是(引导) | 无 | 0-20张,支持jpg/png等 | ✅ 可识别物品 | 用户上传 | 提示文案引导,非强制 |
| Ad Title | 广告标题 | Text | 是* | 无 | 无明确限制 | ✅ AI生成 | AI/用户输入 | 标*表示必填 |
| Description | 描述 | Textarea | 是* | 无 | 15-10000字符 | ✅ AI生成 | AI/用户输入 | 实时字数统计 |
| Category | 类目 | Select Tree | 是(隐式) | 无 | 必须选择叶子节点 | ✅ AI推荐标签 | 用户选择 | 面包屑导航展示 |
| Price | 价格 | Number | 是* | 无 | 数字,最多2位小数(推测) | ❌ | 用户输入 | 货币符号固定 |
| Location | 位置 | Location Picker | 是* | 用户账户位置 | 必须包含postcode | ❌ | 账户设置/用户输入 | 隐私保护 |
| Condition | 成品状况 | Select | 是(Required) | 无 | 枚举值(New/Used/等) | ❌ | 用户选择 | Item Specifics子字段 |
| Contact - Email | 联系邮箱 | Checkbox | 是(默认勾选) | 用户注册邮箱 | Email格式 | ❌ | 账户设置 | 不可见给买家 |
| Contact - Phone | 联系电话 | Phone Input | 否 | 无 | 手机号格式 | ❌ | 用户输入 | 可选添加 |
| Show Map | 地图展示 | Checkbox | 否 | false | Boolean | ❌ | 用户勾选 | 影响广告展示 |
| Promotion - Featured | 推广-置顶 | Checkbox | 否 | false | Boolean | ❌ | 用户勾选 | 付费功能 |
| Promotion - Urgent | 推广-急售 | Checkbox | 否 | false | Boolean | ❌ | 用户勾选 | 付费功能 |
| Promotion - Spotlight | 推广-焦点 | Checkbox | 否 | false | Boolean | ❌ | 用户勾选 | 付费功能 |
| Youtube Link | 视频链接 | Checkbox | 否 | false | Boolean | ❌ | 用户勾选 | 需付费£1.99 |

### 3.2 数据字典

#### Photos字段

```json
{
  "fieldName": "photos",
  "type": "file[]",
  "maxCount": 20,
  "minCount": 0,
  "required": false, // 非强制,但强烈引导
  "acceptTypes": ["image/jpeg", "image/png", "image/gif", "image/webp"],
  "maxSizePerFile": "未知(需确认)",
  "storageType": "云存储(推测CDN)",
  "aiProcessing": {
    "imageRecognition": true,
    "autoTagging": true,
    "contentModeration": true
  },
  "displayOrder": "用户可拖拽调整",
  "interactions": {
    "upload": "点击+号上传",
    "delete": "点击X删除",
    "reorder": "长按拖拽",
    "scroll": "横向滚动查看"
  }
}
```

#### Category字段

```json
{
  "fieldName": "category",
  "type": "hierarchical-select",
  "maxDepth": 4,
  "required": true,
  "displayFormat": "breadcrumb",
  "example": "For Sale > Baby & Kids Stuff > Car Seats & Baby Carriers",
  "aiSuggestion": {
    "enabled": true,
    "suggestedTags": ["Dinning Tables", "Dinning Chairs", "Tableware"],
    "confidence": "未知(设计稿未显示置信度)",
    "userCanOverride": true
  },
  "editability": "发布后可通过Edit按钮修改"
}
```

#### Location字段

```json
{
  "fieldName": "location",
  "type": "location-picker",
  "required": true,
  "components": {
    "city": "Camden",
    "area": "London",
    "postcode": "NW5 4HX"
  },
  "display": {
    "public": "Camden, London (仅区域)",
    "private": "NW5 4HX (不对买家显示)"
  },
  "mapIntegration": {
    "provider": "Google Maps",
    "optional": true,
    "approximateAreaOnly": true,
    "privacyNote": "Only the approximate area will be shown"
  }
}
```

### 3.3 业务规则详解

#### 规则1: 照片上传限制
- **数量限制**: 0-20张
- **格式限制**: jpg, png, gif, webp (推测)
- **尺寸限制**: 未明确(需确认后端API)
- **AI处理**: 
  - 首张照片上传后触发AI识别
  - 识别物品类型并生成标题/描述
  - 可能包含图片质量检测(模糊/清晰度)
- **顺序调整**: 用户可长按拖拽调整照片顺序
- **主图标识**: 第一张照片为主图(缩略图显示在广告列表)

#### 规则2: 标题描述生成逻辑
- **触发条件**: 
  - 场景1: 上传首张照片
  - 场景2: 输入标题后选择类目
- **生成策略**:
  - 基于图片识别结果
  - 结合类目属性
  - 生成符合Gumtree风格的描述
- **字符数限制**:
  - Title: 无明确上限(推测50-100字符)
  - Description: 15-10000字符
- **用户编辑**:
  - AI生成后用户可随时修改
  - "Change"按钮可重新生成
  - "Label"按钮可能提供更多AI辅助选项

#### 规则3: 类目推荐与验证
- **推荐来源**:
  - 基于标题关键词匹配
  - 基于图片识别结果
  - 基于用户历史发布记录(推测)
- **验证规则**:
  - 必须选择到叶子节点(最深层级)
  - 不能选择"For Sale"根节点
  - 示例: ✅ "Car Seats & Baby Carriers" / ❌ "Baby & Kids Stuff"
- **子类目标签**:
  - AI推荐3-5个相关子类目
  - 用户可点击快速选择
  - 标签选择后替换主类目(需确认)

#### 规则4: 价格字段约束
- **货币**: 固定£(英镑)
- **输入限制**: 
  - 仅允许数字和小数点
  - 最多2位小数
  - 不允许负数
- **最小值**: £0.01(推测)
- **最大值**: 未明确(需确认,可能£999,999.99)
- **免费标识**: 若价格为£0,可能显示为"Free"

#### 规则5: 位置隐私保护
- **公开信息**: City + Area (如"Camden, London")
- **隐藏信息**: 完整Postcode (如"NW5 4HX")
- **地图展示**: 
  - 用户可选择是否展示
  - 仅展示近似区域圆形范围
  - 不显示精确地址
- **编辑限制**: 发布后可能限制修改位置(需确认)

#### 规则6: 推广套餐规则
- **可多选**: 用户可同时选择多个推广套餐
- **价格累加**: 总费用 = Featured价格 + Urgent价格 + Spotlight价格
- **时长选择**: 
  - Featured: 3/7/14天(下拉选择)
  - Urgent: 固定7天
  - Spotlight: 固定7天
- **支付时机**: 广告提交后跳转支付页面(设计稿未展示)
- **Spotlight限制**: 可能需要满足某些条件才能解锁(带锁图标)

#### 规则7: 草稿保存规则
- **自动保存时机**:
  - 用户填写任一字段后
  - 每30秒自动保存(推测)
  - 用户主动退出时
- **草稿有效期**: 未明确(推测7-30天)
- **草稿恢复优先级**: 最近一次保存的草稿
- **草稿清理**: 用户选择"新建"后清除旧草稿

---

## 🎨 四、UI与交互分析

### 4.1 完整UI元素清单

#### 导航与布局

| 元素 | 位置 | 尺寸(px) | 样式 | 交互 | 状态 |
|------|------|----------|------|------|------|
| Status Bar | 顶部 | 375x48 | iPhone X默认 | 无 | 固定 |
| Top App Bar | Status Bar下 | 375x56 | 含返回按钮 | 点击返回上一页 | 固定 |
| 面包屑导航 | Top Bar下 | 343x110 | "For Sale / Baby & Kids Stuff / Car Seats & Baby Carriers" | 点击Edit修改类目 | 动态 |
| Bottom Bar | 底部 | 375x64 | 含Post按钮 | 点击提交表单 | 固定 |
| Home Indicator | 最底部 | 375x34 | iPhone X圆角指示条 | 无 | 固定 |
| Save Draft按钮 | Bottom Bar内 | 63x40 | 隐藏(hidden) | 保存草稿 | 隐藏 |

#### 表单元素

| 元素 | 字段 | 位置 | 尺寸(px) | 组件类型 | 交互 | 验证 |
|------|------|------|----------|----------|------|------|
| Photos上传区 | Photos | (16, 113) | 100x132 | File Upload | 点击+上传 | 0-20张 |
| 照片计数器 | Photos | (35, 64) | 30x20 | Label | 无 | 实时更新 |
| 照片提示框 | Photos | (16, 51) | 343x76 | Info Banner | 无 | 静态 |
| YouTube链接按钮 | Photos | (22, 301) | 202x38 | Button | 点击添加链接 | 付费功能 |
| 标题输入框 | Ad Title | (16, 269) | 343x48 | Text Input | 输入文本 | 无限制 |
| 标题Label | Ad Title | (0, 0) | 343x24 | Label | 无 | 带*号 |
| 标题AI图标 | Ad Title | (0, 24) | 16x16 | Icon | 显示AI生成 | 动态 |
| 描述输入框 | Description | (16, 397) | 343x156 | Textarea | 输入多行文本 | 15-10000字符 |
| 描述Label | Description | (0, 0) | 343x24 | Label | 无 | 带*号 |
| 描述AI按钮 | Description | (8, 116) | 122x32 | Button | 点击AI辅助 | 无 |
| 描述Change按钮 | Description | (268, 1) | 75x30 | Button | 重新生成描述 | 无 |
| 描述字数统计 | Description | (275, 162) | 68x19 | Label | 无 | 实时更新 |
| 描述最小字数提示 | Description | (0, 160) | 167x22 | Label | 无 | 静态 |
| 类目展示 | Category | (16, 599) | 343x24 | Breadcrumb | 点击Edit修改 | 必填 |
| 类目标签组 | Category | (16, 635) | 443x44 | Checkbox Group | 点击选中标签 | 可选 |
| 价格输入框 | Price | (16, 841) | 343x48 | Number Input | 输入数字 | 数字+小数 |
| 价格Label | Price | (0, 0) | 343x24 | Label | 无 | 带*号 |
| 货币符号 | Price | (12, 12) | 10x24 | Label | 无 | 固定£ |
| Item Specifics模块 | - | (16, 647) | 343x140 | Tab Group | 切换Required/Optional | 动态 |
| Condition选择 | Condition | (16, 735) | 343x48 | Select | 点击展开选项 | 必填 |
| Location展示 | Location | (16, 909) | 343x78 | Location Input | 点击Edit修改 | 必填 |
| Location Label | Location | (0, 0) | 343x24 | Label | 无 | 带*号 |
| Show Map复选框 | Location | (0, 130) | 194x31 | Checkbox | 勾选展示地图 | 可选 |
| Google Map预览 | Location | (1, 1) | 341x120 | Iframe | 无 | 动态加载 |

#### 推广选项

| 元素 | 套餐 | 位置 | 尺寸(px) | 组件 | 交互 | 价格 |
|------|------|------|----------|------|------|------|
| Featured卡片 | Featured | (16, 69) | 343x195 | Card | 点击勾选 | £1.00 (7天) |
| Featured徽章 | Featured | (35, 0) | 85x29 | Badge | 无 | "Recommended" |
| Featured下拉 | Featured | (171.5, 17) | 154x32 | Dropdown | 选择天数 | 3/7/14天 |
| Urgent卡片 | Urgent | (16, 280) | 343x147 | Card | 点击勾选 | £0.75 (7天) |
| Spotlight卡片 | Spotlight | (16, 443) | 343x147 | Card | 点击勾选 | £1.99 (7天) |
| Spotlight锁图标 | Spotlight | (0, 4) | 20x20 | Icon | 提示需解锁 | 可能限制 |
| Select All复选框 | - | (16, 605) | 99x34 | Checkbox | 全选推广 | 无 |
| View Example链接 | - | (52, 157) | 98x19 | Link | 跳转示例页 | 无 |

#### Contact Details

| 元素 | 字段 | 位置 | 尺寸(px) | 组件 | 交互 | 默认 |
|------|------|------|----------|------|------|------|
| Contact Heading | - | (0, 8) | 343x33 | Heading | 无 | "Contact Details*" |
| Email展示 | Email | (35, 81) | 308x22 | Label | 无 | 用户邮箱 |
| Messages复选框 | Messages | (0, 47) | 201x34 | Checkbox | 勾选站内信 | 默认勾选 |
| Phone按钮 | Phone | (109, 117) | 163x30 | Button | 点击添加手机号 | 可选 |
| Phone复选框 | Phone | (0, 115) | 95x34 | Checkbox | 勾选后显示手机 | 默认不勾选 |
| 隐私提示框 | - | (0, 165) | 343x110 | Info Banner | Learn more链接 | 静态 |
| Edit按钮 | - | (313, 8) | 30x32 | Button | 点击修改 | 右上角 |

#### 底部按钮与声明

| 元素 | 位置 | 尺寸(px) | 文案 | 交互 | 颜色 |
|------|------|----------|------|------|------|
| Post按钮 | (16, 8) | 343x48 | "Post my Ad" | 点击提交 | 主色调(橙/绿) |
| 法律声明文本 | (16, 2437) | 338x96 | Terms of Use链接等 | 点击跳转 | 灰色小字 |
| Terms链接 | (134, 2457) | 92x18 | "Terms of Use" | 跳转政策页 | 蓝色下划线 |
| Posting Rules链接 | (259, 2457) | 91x18 | "Posting Rules" | 跳转规则页 | 蓝色下划线 |
| Privacy Notice链接 | (113, 2476) | 106x18 | "Privacy Notice" | 跳转隐私页 | 蓝色下划线 |
| Contact Us链接 | (39, 2515) | 82x18 | "Contact Us" | 跳转联系页 | 蓝色下划线 |

### 4.2 交互行为详解

#### 交互1: 照片上传与管理

**上传流程**:
1. 用户点击照片区域的"+"图标
2. 触发系统相册/相机选择器
3. 用户选择照片(可单选/多选)
4. 照片上传到服务器(显示上传进度,推测)
5. 上传完成后照片展示在横向滚动列表

**横向滚动**:
- 照片以100x100尺寸横向排列
- 超过4张后可左右滑动查看
- 最多显示20张照片

**长按拖拽**:
- 用户长按照片1秒(推测)
- 照片进入"可拖拽"状态(可能有视觉反馈,如边框高亮)
- 用户拖动照片到目标位置
- 释放后照片顺序更新
- 第一张照片为主图(缩略图)

**删除照片**:
- 每张照片右上角显示【X】按钮
- 点击【X】后照片立即删除(无二次确认,推测)
- 后续照片自动前移填补空位
- 计数器实时更新 "X/20"

#### 交互2: AI内容生成动画

**加载状态**:
- Title字段显示骨架屏(灰色矩形,宽245px,高20px)
- Description字段显示3行骨架屏(宽度递减: 285px, 245px, 185px)
- 骨架屏呈现呼吸动画(推测: opacity 0.3-0.6循环)
- 右上角显示"01"加载图标(可能旋转动画)

**生成完成**:
- 骨架屏淡出(fade-out, 0.3s,推测)
- AI生成内容淡入(fade-in, 0.3s,推测)
- "01"图标消失
- 用户可立即编辑内容

**Change按钮**:
- 位置: Description右上角
- 图标: 旋转箭头(Arrow-rotate)
- 点击后:
  1. 当前描述保留(不清空)
  2. 重新显示骨架屏
  3. AI重新生成新内容
  4. 新内容替换旧内容

#### 交互3: 类目标签选择

**标签展示**:
- 位置: Category字段下方
- 样式: 白色背景+灰色边框的标签(Chip)
- 布局: 横向排列,自动换行
- 示例: "Dinning Tables", "Dinning Chairs", "Tableware"

**选择交互**:
- 点击标签后:
  1. 标签样式变化(可能: 边框变色+勾选图标)
  2. 主Category字段不变(仍显示父类目)
  3. 或替换为子类目(需确认行为)

**多选逻辑**:
- 设计稿显示复选框样式
- 推测可多选标签
- 多选后可能影响广告推荐精度

#### 交互4: Item Specifics标签切换

**Required / Optional标签**:
- 位置: (20, 683)和(192, 683)
- 样式: 分段控制器(Segmented Control)
- 默认选中: "Required"

**切换交互**:
1. 用户点击"Optional"标签
2. 标签背景色变化(高亮)
3. 下方字段列表切换:
   - Required: 显示Condition等必填字段
   - Optional: 显示其他可选字段(如Brand, Size等,依类目而定)

**字段展开**:
- Condition字段为Select类型
- 点击后展开下拉菜单(Dropdown/Bottom Sheet,推测)
- 用户选择后值回填到字段

#### 交互5: Location地图展示

**Show Map复选框**:
- 默认状态: 未勾选
- 勾选后:
  1. 下方展开Google Map iframe(341x120)
  2. 地图中心为用户位置近似区域
  3. 显示圆形半透明覆盖范围(推测半径1-2km)
  4. 左上角"View larger map"链接可跳转Google Maps

**地图交互**:
- 地图内无缩放/拖拽功能(iframe限制)
- 点击地图区域无响应
- 仅用于预览展示效果

**隐私提示**:
- 位置: 地图下方
- 文案: "Only the approximate area will be shown"
- 样式: 灰色小字

#### 交互6: 推广套餐卡片

**卡片布局**:
- 每个卡片为独立Card组件
- 高度: Featured 195px, Urgent/Spotlight 147px
- 内容:
  - 左侧: 复选框 + 套餐徽章
  - 右侧: 价格 + 天数下拉(Featured独有)
  - 中间: 描述文案
  - 底部: "View example"链接

**选中状态**:
- 用户点击卡片任意位置
- 复选框勾选
- 卡片边框可能高亮(需确认)
- 价格累加到总价(设计稿未显示总价位置)

**View example链接**:
- 点击后新窗口打开(推测)
- 展示该推广套餐的示例广告
- 用户可返回继续编辑

**Select all功能**:
- 点击"Select all"复选框
- 所有推广卡片同时勾选
- 再次点击全部取消勾选

#### 交互7: 表单提交与验证

**实时验证**:
- 用户blur(失焦)某字段时
- 触发该字段的验证规则
- 错误提示显示在字段下方(红色"supporting-text")
- 示例: Description少于15字符时提示"15 characters minimum"

**提交验证**:
- 用户点击"Post my Ad"按钮
- 前端校验所有必填字段:
  - Photos: 无明确要求(0张也可,仅引导上传)
  - Ad Title: 不能为空
  - Description: 15-10000字符
  - Category: 必须选择
  - Price: 不能为空,必须为数字
  - Location: 不能为空
  - Condition: 必须选择(Required字段)
  - Contact Details: 至少勾选Messages或Phone之一
- 若有字段未填写/格式错误:
  - 页面滚动到第一个错误字段
  - 字段下方显示红色错误提示
  - 字段边框变红(推测)
  - 底部弹出Toast提示(推测): "Please complete all required fields"

**提交成功**:
- 前端验证通过后
- 显示Loading动画(推测: 按钮文案变为"Posting...",带旋转图标)
- 调用后端API提交数据
- 后端返回成功后跳转到成功页面
- 若选择了推广套餐,跳转到支付页面(设计稿未展示)

### 4.3 状态变化分析

#### 状态1: 页面加载状态

**初始加载** (首次进入发帖页):
```
空白表单 → 检查草稿 → [有草稿] 弹窗提示 / [无草稿] 直接显示空表单
```

**草稿加载** (选择"继续编辑"):
```
弹窗关闭 → 显示Loading(推测) → 填充草稿数据 → 页面就绪
```

**类目选择后** (确认类目):
```
类目选择页 → 显示面包屑导航 → 表单展开 → 光标定位到第一个空字段(Photos,推测)
```

#### 状态2: AI生成状态

**生成中**:
- UI状态:
  - Title: 骨架屏动画(1行)
  - Description: 骨架屏动画(3行)
  - "01"图标旋转(右上角)
  - 其他字段可编辑
- 数据状态:
  - `isAIGenerating: true`
  - `generatedTitle: null`
  - `generatedDescription: null`
  - `generationStartTime: timestamp`
- 允许操作:
  - ✅ 编辑其他字段(Price, Location等)
  - ✅ 上传更多照片
  - ✅ 切换类目(会中断AI生成)
  - ❌ 提交表单(Post按钮可能禁用,需确认)

**生成成功**:
- UI状态:
  - 骨架屏淡出
  - AI内容填充
  - "01"图标消失
  - "Change"按钮可见
- 数据状态:
  - `isAIGenerating: false`
  - `generatedTitle: "AI生成的标题"`
  - `generatedDescription: "AI生成的完整描述"`
  - `generationEndTime: timestamp`
- 允许操作:
  - ✅ 编辑AI生成的内容
  - ✅ 点击"Change"重新生成
  - ✅ 提交表单

**生成失败**:
- UI状态:
  - 骨架屏消失
  - 显示错误提示: "supporting-text"(可能文案: "AI generation failed. Please enter manually.")
  - "Change"按钮变为"Retry"(推测)
- 数据状态:
  - `isAIGenerating: false`
  - `generationError: "error message"`
- 降级方案:
  - 用户手动填写
  - 点击"Retry"重试

#### 状态3: 字段错误状态

**单字段错误** (例如Description少于15字符):
```json
{
  "field": "description",
  "value": "Short text",
  "error": {
    "code": "MIN_LENGTH",
    "message": "15 characters minimum",
    "severity": "error"
  },
  "uiState": {
    "borderColor": "red",
    "showErrorText": true,
    "errorTextColor": "red"
  }
}
```

**全局错误** (提交时多字段错误):
```json
{
  "validationErrors": [
    {
      "field": "photos",
      "message": "supporting-text"
    },
    {
      "field": "title",
      "message": "supporting-text"
    },
    {
      "field": "category",
      "message": "Please choose a category"
    }
  ],
  "scrollToFirstError": true,
  "showToast": true,
  "toastMessage": "Please complete all required fields"
}
```

#### 状态4: 推广选项状态

**未选择**:
```json
{
  "featured": {
    "selected": false,
    "price": 1.00,
    "duration": 7
  },
  "urgent": {
    "selected": false,
    "price": 0.75
  },
  "spotlight": {
    "selected": false,
    "price": 1.99,
    "locked": true // 可能需要满足条件
  },
  "totalCost": 0.00
}
```

**Featured选中**:
```json
{
  "featured": {
    "selected": true,
    "price": 1.00,
    "duration": 7, // 用户可选3/7/14
    "priceByDuration": {
      "3": 0.50,
      "7": 1.00,
      "14": 1.80
    }
  },
  "totalCost": 1.00
}
```

**Select all选中**:
```json
{
  "featured": { "selected": true, "price": 1.00, "duration": 7 },
  "urgent": { "selected": true, "price": 0.75 },
  "spotlight": { "selected": true, "price": 1.99 },
  "totalCost": 3.74 // £1.00 + £0.75 + £1.99
}
```

---

## ⚠️ 五、风险识别与评估

### 5.1 所有风险点清单 (30-50个)

#### 高风险点 (P0 - 影响核心功能)

| 风险ID | 风险描述 | 场景 | 影响 | 概率 | 检测方法 |
|--------|----------|------|------|------|----------|
| R001 | AI生成失败时无降级方案 | 用户上传照片后AI服务不可用 | 用户无法继续发布,流程中断 | 中 | 模拟AI服务超时/500错误 |
| R002 | 照片上传失败无重试机制 | 网络不稳定时上传大图片 | 照片丢失,用户体验差 | 高 | 弱网环境测试(2G/3G) |
| R003 | 类目未选择可提交表单 | 前端验证漏洞 | 后端报错,数据不完整 | 低 | 绕过前端验证直接调API |
| R004 | 必填字段验证不一致 | Title/Description标*但不校验 | 空内容提交到后端 | 中 | 删除字段内容后提交 |
| R005 | 推广套餐价格计算错误 | 多选套餐后总价不正确 | 用户支付金额错误,财务损失 | 高 | 选择所有套餐验证总价 |
| R006 | 草稿恢复后数据丢失 | 某些字段(如照片)未保存 | 用户需重新上传,体验差 | 中 | 保存草稿后关闭页面重新进入 |
| R007 | Location隐私泄露 | 地图显示精确地址 | 用户隐私泄露,安全风险 | 低 | 勾选"Show Map"后查看公开广告 |
| R008 | 提交后无Loading状态 | 点击"Post"后无反馈 | 用户重复点击,重复提交 | 中 | 慢网环境点击Post按钮 |
| R009 | AI生成内容包含敏感词 | AI生成违禁词汇/不当内容 | 广告被拒,品牌形象受损 | 中 | 上传特定类型图片测试 |
| R010 | 照片顺序调整后丢失 | 拖拽后刷新页面 | 主图错误,影响展示 | 低 | 拖拽照片后刷新页面 |

#### 中风险点 (P1 - 影响用户体验)

| 风险ID | 风险描述 | 场景 | 影响 | 概率 | 检测方法 |
|--------|----------|------|------|------|----------|
| R011 | Description字符数统计不准确 | 输入特殊字符/emoji | 提示"56/10000"但实际超限 | 中 | 输入emoji和特殊字符 |
| R012 | 类目建议标签不准确 | AI推荐错误类目 | 用户选错类目,广告曝光差 | 高 | 上传多种物品图片测试 |
| R013 | 照片上传大小限制未提示 | 上传超大图片(>10MB) | 上传失败无提示 | 中 | 上传大尺寸照片 |
| R014 | Price字段允许负数 | 输入-100 | 显示异常价格 | 低 | 输入负数和非法字符 |
| R015 | Category面包屑导航过长 | 4级类目标题过长 | 文本截断,显示不完整 | 中 | 选择长标题类目 |
| R016 | 推广套餐"View example"链接失效 | 点击后404 | 用户无法预览效果 | 低 | 点击所有"View example"链接 |
| R017 | Phone号码格式验证宽松 | 输入123可通过 | 买家联系失败 | 中 | 输入各种格式手机号 |
| R018 | YouTube链接验证不严格 | 输入非YouTube链接 | 视频无法播放 | 中 | 输入任意URL |
| R019 | 草稿弹窗无过期时间提示 | 草稿已超期但仍显示 | 恢复后数据过期 | 低 | 保存草稿30天后测试 |
| R020 | Condition选项加载失败 | 依赖后端接口返回枚举 | 用户无法选择,流程中断 | 中 | 模拟API返回空数据 |

#### 低风险点 (P2 - 边界场景)

| 风险ID | 风险描述 | 场景 | 影响 | 概率 | 检测方法 |
|--------|----------|------|------|------|----------|
| R021 | 照片拖拽到边界外释放 | 拖拽照片到屏幕外 | 照片丢失或位置错误 | 低 | 边界操作测试 |
| R022 | AI生成过程中切换类目 | 生成中改变类目 | AI继续生成错误内容 | 低 | 在骨架屏动画时切换类目 |
| R023 | 推广套餐Spotlight锁定条件不明 | 新用户无法解锁 | 混淆用户 | 低 | 新注册账户测试 |
| R024 | 地图iframe加载失败 | 网络问题或Google Maps不可用 | 空白区域 | 中 | 禁用Google Maps API |
| R025 | 法律声明链接全部失效 | Terms/Privacy链接404 | 法律风险 | 低 | 点击所有底部链接 |
| R026 | 成功页面体验反馈无提交 | "How was your overall"无交互 | 用户反馈丢失 | 低 | 发布成功后测试反馈 |
| R027 | 推广选择后刷新页面丢失 | 勾选推广后返回 | 用户需重新选择 | 低 | 选择推广后返回再进入 |
| R028 | Title/Description包含HTML标签 | 输入`<script>alert()</script>` | XSS风险 | 中 | 输入恶意HTML代码 |
| R029 | 照片上传进度无显示 | 上传大图片无进度条 | 用户不知是否成功 | 中 | 慢网环境上传大图 |
| R030 | Category标签过多时布局混乱 | AI推荐10+标签 | 超出屏幕,无法滚动 | 低 | Mock返回大量标签 |
| R031 | Draft保存时机不明确 | 不知何时自动保存 | 用户误以为未保存 | 低 | 填写后立即关闭页面 |
| R032 | Promotion天数下拉选择无默认值 | Featured未选择天数 | 提交时报错 | 低 | 不选择天数直接提交 |
| R033 | Item Specifics Optional字段为空 | 切换到Optional无字段 | 用户困惑 | 中 | 选择不同类目测试 |
| R034 | Contact Email不可修改 | 用户想用其他邮箱 | 功能限制 | 低 | 尝试修改邮箱 |
| R035 | Success页面"Post another ad"按钮位置不明 | 设计稿未清晰标注 | 用户找不到继续发布 | 低 | 发布成功后查看页面 |
| R036 | AI生成超时无提示 | 30秒仍未返回 | 用户不知是否失败 | 中 | 模拟慢速AI响应 |
| R037 | 照片删除无二次确认 | 误点X按钮 | 照片意外删除 | 中 | 快速点击X按钮 |
| R038 | Price货币符号固定为£ | 其他国家用户使用 | 货币错误 | 低 | 切换国家/地区测试 |
| R039 | Location地图缩放级别不当 | 显示太宽或太窄 | 位置不准确 | 低 | 不同城市测试 |
| R040 | 推广套餐支付流程未设计 | 点击Post后不知如何支付 | 流程中断 | 高 | 选择推广后提交 |

### 5.2 风险等级矩阵

```
高影响 |  R005  |  R002  |  R012  |  R040  |
       |  R009  |  R008  |        |        |
-------------------------------------------------
中影响 |  R001  |  R011  |  R018  |  R036  |
       |  R004  |  R015  |  R020  |  R028  |
       |  R006  |  R017  |        |  R029  |
-------------------------------------------------
低影响 |  R003  |  R013  |  R021  |  R037  |
       |  R007  |  R014  |  R022  |  R038  |
       |  R010  |  R016  |  R023  |  R039  |
       |        |  R019  |  R024  |        |
       |        |  R025  |  R027  |        |
       |        |  R026  |  R030  |        |
       |        |  R031  |  R032  |        |
       |        |  R032  |  R033  |        |
       |        |  R034  |  R035  |        |
-------------------------------------------------
       |   低    |   中    |   高    |  极高   |
                    发生概率
```

### 5.3 测试重点建议

**优先级1 (必测)**:
1. **AI生成失败降级**: R001, R009, R036
2. **照片上传稳定性**: R002, R010, R029, R037
3. **推广套餐计费**: R005, R040
4. **必填字段验证**: R003, R004
5. **类目推荐准确性**: R012

**优先级2 (重点测试)**:
1. **草稿保存恢复**: R006, R019, R027, R031
2. **字段验证**: R011, R014, R017, R018, R028
3. **UI交互**: R008, R015, R020
4. **隐私安全**: R007

**优先级3 (边界测试)**:
1. **异常场景**: R021, R022, R023, R024, R030, R033
2. **兼容性**: R025, R026, R032, R034, R035, R038, R039

---

## 📋 六、测试策略

### 6.1 详细测试范围

#### 范围1: 功能测试

**类目选择模块**:
- 搜索类目功能 (输入关键词 → 显示建议 → 选择类目)
- 浏览类目树功能 (展开多级 → 选择叶子节点)
- 类目编辑功能 (点击Edit → 修改类目 → 更新面包屑)
- 类目建议标签 (AI推荐 → 点击选中 → 验证选中效果)

**AI辅助生成模块**:
- 基于照片生成 (上传照片 → AI识别 → 生成标题+描述)
- 基于标题生成 (输入标题 → AI推荐类目 → 生成描述)
- 重新生成功能 (点击Change → 骨架屏 → 生成新内容)
- 生成失败处理 (模拟超时 → 显示错误 → 允许手动填写)

**表单填写模块**:
- 所有必填字段验证 (Photos, Title, Description, Category, Price, Location, Condition, Contact)
- 字段格式验证 (Price数字, Description字符数, Phone号码格式)
- 实时验证反馈 (blur时验证 → 显示错误提示)
- 字段联动逻辑 (类目变化 → Condition选项变化)

**照片管理模块**:
- 上传照片 (单张/多张 → 显示缩略图 → 计数器更新)
- 横向滚动查看 (超过4张 → 可滑动)
- 拖拽调整顺序 (长按 → 拖动 → 释放 → 更新顺序)
- 删除照片 (点击X → 立即删除 → 后续照片前移)
- 照片上传进度 (大图片 → 显示进度条,如有)

**推广选项模块**:
- 单选/多选推广套餐
- Featured天数选择 (下拉选择3/7/14天)
- Select all功能
- 价格计算 (选中套餐 → 计算总价)
- View example链接 (打开新窗口 → 展示示例)

**草稿功能模块**:
- 自动保存草稿 (填写字段 → 30秒后保存 → 验证保存成功)
- 草稿恢复弹窗 (重新进入 → 显示弹窗 → 选择"继续"/选择"新建")
- 草稿数据完整性 (恢复后 → 验证所有字段 → 包括照片)
- 草稿过期处理 (30天后 → 草稿清除或过期提示)

**提交发布模块**:
- 前端验证 (提交前 → 校验所有字段 → 显示错误)
- 后端提交 (验证通过 → 调用API → 显示Loading)
- 成功跳转 (提交成功 → 跳转成功页 → 显示推广推荐)
- 支付流程 (选择推广 → 跳转支付页,如有)

#### 范围2: UI/UX测试

**响应式布局**:
- iPhone X及以上尺寸 (375x812)
- iPhone SE等小屏 (推测: 320x568)
- iPad横屏/竖屏 (推测: 768x1024)
- 不同字体大小 (系统设置放大字体)

**视觉一致性**:
- 颜色规范 (主色调, 错误红色, 链接蓝色)
- 字体规范 (标题, 正文, 提示文字)
- 间距规范 (模块间距16px, 字段间距等)
- 圆角规范 (按钮, 卡片, 输入框圆角值)

**动画效果**:
- 骨架屏呼吸动画 (平滑, 无卡顿)
- 内容淡入淡出 (0.3s transition)
- 页面跳转动画 (推测: slide-in/fade)
- 加载图标旋转 (01图标)

**交互反馈**:
- 按钮点击状态 (按下时颜色变深)
- 字段聚焦状态 (边框高亮)
- 错误状态样式 (红色边框+错误文本)
- Toast提示 (提交错误时显示)

**可访问性**:
- VoiceOver支持 (屏幕阅读器可读所有元素)
- 色盲模式 (错误提示不仅用红色)
- 键盘导航 (Tab键可遍历所有字段)
- 触摸区域大小 (按钮至少44x44)

#### 范围3: 兼容性测试

**iOS版本**:
- iOS 14 (最低支持版本,推测)
- iOS 15
- iOS 16
- iOS 17 (最新版本)

**设备型号**:
- iPhone X/XS/XR (刘海屏)
- iPhone 11/12/13 (标准尺寸)
- iPhone 14/15 Pro Max (大屏)
- iPhone SE (小屏)

**浏览器内核**:
- Safari WebView (iOS默认)
- Chrome WebView (第三方浏览器)
- WKWebView vs UIWebView (不同内核)

**网络环境**:
- 4G (正常速度)
- 3G (慢速)
- 2G (极慢)
- WiFi (高速)
- 弱网 (丢包率50%)
- 离线后恢复 (网络中断后重连)

**系统设置**:
- 深色模式 (Dark Mode,如支持)
- 字体大小 (默认, 放大, 最大)
- 系统语言 (英语, 其他语言)
- 低电量模式 (是否影响动画)

#### 范围4: 性能测试

**页面加载性能**:
- 首屏加载时间 (目标: <3秒)
- 类目数据加载 (目标: <1秒)
- 草稿恢复时间 (目标: <2秒)

**AI生成性能**:
- 标题生成耗时 (目标: <5秒)
- 描述生成耗时 (目标: <10秒)
- 超时重试机制 (>30秒视为失败)

**照片上传性能**:
- 单张照片上传 (1MB, 目标<2秒)
- 批量上传20张 (目标<30秒)
- 上传失败重试 (自动重试3次)

**表单提交性能**:
- 提交API响应时间 (目标<3秒)
- 大数据量提交 (20张照片+长描述)

**内存占用**:
- 页面内存占用 (目标<150MB)
- 照片缓存策略 (避免内存泄漏)
- 长时间使用后性能 (填写30分钟后)

#### 范围5: 安全测试

**输入验证**:
- SQL注入 (Title/Description输入SQL语句)
- XSS攻击 (输入`<script>`标签)
- HTML注入 (输入恶意HTML)
- 特殊字符处理 (emoji, Unicode)

**数据传输**:
- HTTPS加密 (所有API使用HTTPS)
- 敏感数据脱敏 (日志不包含邮箱/手机)
- Token安全 (验证token过期机制)

**隐私保护**:
- Location精确度 (不泄露完整postcode)
- 地图模糊化 (仅显示近似区域)
- Email不公开 (买家看不到卖家邮箱)
- Phone可选 (用户可选择不提供)

**权限控制**:
- 相册访问权限 (首次上传照片时请求)
- 位置访问权限 (首次设置Location时请求)
- 权限拒绝处理 (提示用户手动开启)

### 6.2 完整测试方法

#### 方法1: 功能测试

**黑盒测试**:
- 等价类划分 (有效/无效输入)
- 边界值分析 (字符数0, 15, 10000, 10001)
- 判定表法 (多条件组合场景)
- 场景法 (完整业务流程)

**示例: Description字段测试**

| 测试场景 | 输入 | 预期结果 | 用例类型 |
|----------|------|----------|----------|
| 最小边界值-1 | 14个字符 | 错误提示"15 characters minimum" | 边界值 |
| 最小边界值 | 15个字符 | 通过验证 | 边界值 |
| 正常值 | 500个字符 | 通过验证 | 正常值 |
| 最大边界值 | 10000个字符 | 通过验证 | 边界值 |
| 最大边界值+1 | 10001个字符 | 错误提示或自动截断 | 边界值 |
| 空值 | "" | 错误提示(必填) | 异常值 |
| 特殊字符 | "Test\<script\>alert()\</script\>" | HTML转义或过滤 | 安全测试 |
| emoji | "Good stuff 🎉🎉🎉" | 正常显示,计数正确 | 兼容性 |
| 换行符 | "Line1\nLine2\nLine3" | 保留换行符 | 格式测试 |

**白盒测试**:
- 语句覆盖 (所有代码行执行)
- 分支覆盖 (所有if/else分支)
- 条件覆盖 (所有条件true/false)
- 路径覆盖 (所有逻辑路径)

**示例: AI生成逻辑测试**

```javascript
// 伪代码: AI生成函数
function generateContent(photos, title) {
  if (!photos && !title) {
    // 路径1: 无输入
    return null;
  } else if (photos && !title) {
    // 路径2: 仅照片
    return aiGenerateFromPhoto(photos);
  } else if (!photos && title) {
    // 路径3: 仅标题
    return aiGenerateFromTitle(title);
  } else {
    // 路径4: 照片+标题
    return aiGenerateFromBoth(photos, title);
  }
}

// 测试用例设计:
// TC1: photos=null, title=null → 路径1
// TC2: photos=[photo1], title=null → 路径2
// TC3: photos=null, title="Bike" → 路径3
// TC4: photos=[photo1], title="Red Bike" → 路径4
```

#### 方法2: 探索式测试

**自由探索**:
- 随机操作顺序 (先填Price再填Title等)
- 快速连续操作 (快速点击按钮)
- 异常操作 (填写中途切换app)
- 极端数据 (超长文本, 特殊字符)

**基于场景的探索**:
- **新手用户场景**: 
  - 首次使用,不熟悉流程
  - 可能误操作,需要引导
  - 测试重点: Tooltip提示, 错误恢复能力
- **高级用户场景**:
  - 快速填写,跳过非必填
  - 使用键盘快捷键(如有)
  - 测试重点: 快捷操作, 高级功能
- **网络不稳定场景**:
  - 填写过程中断网
  - 提交时网络恢复
  - 测试重点: 数据丢失保护, 重试机制

**基于风险的探索**:
- 关注高风险模块 (AI生成, 照片上传, 支付)
- 模拟失败场景 (API超时, 服务降级)
- 测试边界条件 (最大值, 最小值)

#### 方法3: 自动化测试

**UI自动化 (Playwright)**:
- 关键路径回归 (每次发布前执行)
- 跨浏览器测试 (Safari, Chrome)
- 数据驱动测试 (参数化不同类目)

**示例: Playwright测试脚本**

```python
# test_post_ad_ai_posting.py
import pytest
from playwright.sync_api import Page

def test_ai_generate_from_photo(page: Page):
    """测试: 上传照片后AI自动生成标题和描述"""
    # 1. 进入发帖页面
    page.goto("/postad/create?categoryId=123")
    
    # 2. 上传照片
    page.set_input_files('input[type="file"]', 'test_images/bike.jpg')
    
    # 3. 等待AI生成(最多30秒)
    page.wait_for_selector('[data-testid="ai-generated-title"]', timeout=30000)
    
    # 4. 验证标题已填充
    title = page.locator('[data-testid="ad-title"]').input_value()
    assert len(title) > 0, "AI应生成标题"
    
    # 5. 验证描述已填充
    description = page.locator('[data-testid="ad-description"]').input_value()
    assert len(description) >= 15, "AI应生成至少15字符的描述"
    
    # 6. 验证类目标签已推荐
    tags = page.locator('[data-testid="category-tag"]').all()
    assert len(tags) > 0, "AI应推荐至少1个类目标签"
```

**API自动化 (Pytest + Requests)**:
- 接口契约测试
- 数据验证测试
- 性能基准测试

**示例: API测试脚本**

```python
# test_api_submit_ad.py
import requests

def test_submit_ad_with_all_fields():
    """测试: 提交完整广告数据"""
    url = "https://api.gumtree.com/v1/ads"
    headers = {"Authorization": "Bearer {token}"}
    data = {
        "title": "Red Bike for Sale",
        "description": "This is a good bike in excellent condition.",
        "category_id": 123,
        "price": 50.00,
        "location": {
            "city": "London",
            "postcode": "NW5 4HX"
        },
        "photos": ["https://cdn.gumtree.com/photo1.jpg"],
        "condition": "used",
        "contact": {
            "email": "test@example.com",
            "phone": "07123456789"
        },
        "promotions": ["featured"]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    assert response.status_code == 201, "提交应成功返回201"
    assert response.json()["ad_id"] is not None, "应返回广告ID"
    assert response.json()["status"] == "published", "状态应为published"
```

#### 方法4: A/B测试

**对比测试场景**:
- **AI生成 vs 手动填写**: 
  - 对比完成时间
  - 对比广告质量(点击率/回复率)
  - 对比用户满意度
- **不同AI模型**:
  - 模型A vs 模型B生成质量
  - 生成速度对比
  - 推荐准确率对比
- **推广推荐位置**:
  - 表单中 vs 成功页推荐转化率

### 6.3 优先级矩阵

#### 优先级定义

| 优先级 | 定义 | 必测场景 | 执行频率 |
|--------|------|----------|----------|
| P0 | 核心功能,影响主流程 | 冒烟测试必包含 | 每次构建 |
| P1 | 重要功能,影响用户体验 | 回归测试必包含 | 每次发布 |
| P2 | 一般功能,边界场景 | 全量测试包含 | 每周一次 |
| P3 | 低频场景,兼容性 | 探索式测试 | 每月一次 |

#### 测试用例优先级矩阵

| 模块 | P0用例数 | P1用例数 | P2用例数 | P3用例数 | 总计 |
|------|----------|----------|----------|----------|------|
| 类目选择 | 3 | 5 | 3 | 2 | 13 |
| AI生成 | 5 | 4 | 3 | 1 | 13 |
| 照片管理 | 4 | 5 | 4 | 2 | 15 |
| 表单填写 | 8 | 6 | 4 | 2 | 20 |
| 推广选项 | 3 | 3 | 2 | 1 | 9 |
| 草稿功能 | 2 | 3 | 2 | 1 | 8 |
| 提交发布 | 5 | 3 | 2 | 1 | 11 |
| 成功页面 | 1 | 2 | 1 | 1 | 5 |
| **总计** | **31** | **31** | **21** | **11** | **94** |

**说明**: 
- 预估总用例数: 94条 (基于80/20原则,控制在100条以内)
- P0+P1占比: 66% (62/94) - 核心测试覆盖
- 建议自动化: P0全部自动化, P1选择性自动化

---

## ❓ 七、待确认问题清单

### 7.1 核心逻辑确认 (15-30个关键问题)

#### 产品需求层面

**Q1: AI生成策略**
- **问题**: AI生成标题和描述的优先级是什么? 如果同时有照片和标题,以哪个为主?
- **影响**: 测试用例设计,覆盖不同输入组合
- **当前假设**: 照片优先,标题辅助
- **需确认对象**: 产品经理

**Q2: 推广套餐支付流程**
- **问题**: 用户选择推广套餐后点击"Post my Ad",是否直接跳转支付页面? 还是先发布广告再支付?
- **影响**: 测试流程完整性,支付失败后的广告状态
- **当前假设**: 先发布后支付(设计稿未展示支付页)
- **需确认对象**: 产品经理 + 开发工程师

**Q3: 草稿保存时机**
- **问题**: 草稿自动保存的触发条件是什么? 每填写一个字段?每30秒?退出页面时?
- **影响**: 草稿功能测试策略
- **当前假设**: 每30秒自动保存 + 退出时保存
- **需确认对象**: 产品经理

**Q4: 草稿有效期**
- **问题**: 草稿保存多久? 7天?30天?永久?
- **影响**: 长期测试计划
- **当前假设**: 30天
- **需确认对象**: 产品经理

**Q5: AI生成失败降级方案**
- **问题**: 如果AI生成失败(超时/服务不可用),用户如何继续? 是否允许手动填写? 有无"Retry"按钮?
- **影响**: 异常场景测试,用户体验
- **当前假设**: 显示错误提示,允许手动填写,有"Change"按钮可重试
- **需确认对象**: 产品经理 + UX设计师

**Q6: Spotlight推广解锁条件**
- **问题**: 设计稿中Spotlight套餐有"锁图标",解锁条件是什么? 账户等级?历史发布量?
- **影响**: 推广功能测试
- **当前假设**: 新用户不可用,需满足某些条件
- **需确认对象**: 产品经理

**Q7: Location地图精确度**
- **问题**: "Show a map on my ad"展示的地图范围是多大? 精确到街道还是区域? 半径1km还是2km?
- **影响**: 隐私保护测试
- **当前假设**: 半径1-2km的圆形区域
- **需确认对象**: 产品经理 + 法务团队

**Q8: 类目标签选择逻辑**
- **问题**: 用户点击AI推荐的类目标签(如"Dinning Tables")后,主Category字段是否替换? 还是作为子类目标签存在?
- **影响**: 类目选择测试
- **当前假设**: 作为子类目标签,不替换主Category
- **需确认对象**: 产品经理 + UX设计师

**Q9: Featured天数默认值**
- **问题**: Featured推广套餐的下拉菜单默认选中哪个天数? 7天? 还是需要用户手动选择?
- **影响**: 推广功能测试
- **当前假设**: 默认7天
- **需确认对象**: 产品经理

**Q10: 成功页面体验反馈**
- **问题**: "How was your overall"体验反馈是必填还是可选? 有无评分组件? 如何提交?
- **影响**: 成功页面测试
- **当前假设**: 可选,可能包含星级评分
- **需确认对象**: 产品经理

#### 技术实现层面

**Q11: 照片上传大小限制**
- **问题**: 单张照片最大尺寸是多少? 5MB? 10MB? 总计20张是否有总大小限制?
- **影响**: 照片上传测试,性能测试
- **当前假设**: 单张10MB,总计100MB
- **需确认对象**: 开发工程师

**Q12: AI生成超时时间**
- **问题**: AI生成标题/描述的超时时间是多少? 30秒? 60秒?
- **影响**: 性能测试,异常场景测试
- **当前假设**: 30秒
- **需确认对象**: 开发工程师 + 产品经理

**Q13: Description字符数计算规则**
- **问题**: 字符数统计是按byte还是character? emoji算1个字符还是多个?
- **影响**: 字段验证测试
- **当前假设**: 按character,emoji算1个
- **需确认对象**: 开发工程师

**Q14: Price字段精度**
- **问题**: 价格最多几位小数? 2位? 允许输入£0.01吗?
- **影响**: 价格字段测试
- **当前假设**: 2位小数,最小£0.01
- **需确认对象**: 开发工程师

**Q15: Phone号码格式验证**
- **问题**: 手机号验证规则是什么? 仅UK号码? 还是国际号码? 格式要求?
- **影响**: Contact字段测试
- **当前假设**: UK号码,07开头,11位
- **需确认对象**: 开发工程师

**Q16: YouTube链接验证**
- **问题**: YouTube链接的验证规则是什么? 仅youtube.com域名? 还是youtu.be短链接也可以?
- **影响**: YouTube功能测试
- **当前假设**: youtube.com和youtu.be都支持
- **需确认对象**: 开发工程师

**Q17: Category枚举数据来源**
- **问题**: 类目树数据是前端硬编码还是后端API返回? Item Specifics的Condition选项是否依赖类目?
- **影响**: 接口测试,数据驱动测试
- **当前假设**: 后端API返回,Condition依赖类目
- **需确认对象**: 开发工程师

**Q18: 草稿存储位置**
- **问题**: 草稿数据存储在哪里? LocalStorage? 云端? 如果换设备能否恢复?
- **影响**: 草稿功能测试,跨设备测试
- **当前假设**: 云端存储,绑定账户
- **需确认对象**: 开发工程师

**Q19: AI生成API契约**
- **问题**: AI生成的API请求/响应格式是什么? 有无置信度字段? 错误码定义?
- **影响**: API测试,Mock数据准备
- **当前假设**: 需查看API文档
- **需确认对象**: 开发工程师

**Q20: 推广套餐价格规则**
- **问题**: Featured不同天数的价格是固定的还是动态计算的? 3天£0.50, 7天£1.00, 14天£1.80是后端返回还是前端硬编码?
- **影响**: 推广价格测试
- **当前假设**: 后端返回
- **需确认对象**: 开发工程师 + 产品经理

#### UI/UX设计层面

**Q21: 照片上传进度展示**
- **问题**: 照片上传时是否显示进度条? 在哪里显示? 什么样式?
- **影响**: UI测试
- **当前假设**: 照片上显示圆形进度条
- **需确认对象**: UX设计师

**Q22: 提交Loading状态**
- **问题**: 点击"Post my Ad"后按钮文案是否变化? 是否禁用? 有无Loading图标?
- **影响**: 交互测试
- **当前假设**: 文案变为"Posting...",按钮禁用,显示旋转图标
- **需确认对象**: UX设计师

**Q23: 错误提示样式**
- **问题**: 字段验证错误时,除了红色边框和"supporting-text",是否有其他视觉反馈? 如图标?
- **影响**: UI测试
- **当前假设**: 仅红色边框和错误文本
- **需确认对象**: UX设计师

**Q24: 草稿弹窗按钮文案**
- **问题**: 草稿恢复弹窗的两个按钮文案是什么? 左侧"Label"是"新建"还是"取消"? 右侧是"继续编辑"?
- **影响**: 草稿功能测试
- **当前假设**: 左侧"新建",右侧"继续编辑"
- **需确认对象**: UX设计师 + 产品经理

**Q25: Success页面主按钮文案**
- **问题**: 成功页面底部按钮是"Post another ad"还是"Done"? 点击后跳转到哪里?
- **影响**: 成功页面测试
- **当前假设**: "Post another ad",跳转到空白发帖页
- **需确认对象**: UX设计师

**Q26: 深色模式支持**
- **问题**: 该页面是否支持iOS深色模式? 如支持,有无单独设计稿?
- **影响**: 视觉测试
- **当前假设**: 不支持(设计稿未展示)
- **需确认对象**: UX设计师

**Q27: 骨架屏动画参数**
- **问题**: AI生成中的骨架屏动画具体参数是什么? opacity范围? 动画时长?
- **影响**: 动画测试
- **当前假设**: opacity 0.3-0.6, 1.5s循环
- **需确认对象**: UX设计师 + 开发工程师

**Q28: Toast提示位置**
- **问题**: 提交失败时的Toast提示显示在哪里? 顶部还是底部? 自动消失时间?
- **影响**: 交互测试
- **当前假设**: 底部,3秒自动消失
- **需确认对象**: UX设计师

**Q29: 照片删除二次确认**
- **问题**: 点击照片的X按钮删除时,是否需要二次确认? 还是直接删除?
- **影响**: 交互测试,用户体验
- **当前假设**: 直接删除(设计稿无弹窗)
- **需确认对象**: UX设计师 + 产品经理

**Q30: Category标签最大数量**
- **问题**: AI推荐的类目标签最多显示几个? 如果AI返回10个标签,是否有"更多"按钮?
- **影响**: UI测试,边界测试
- **当前假设**: 最多5个,无"更多"
- **需确认对象**: UX设计师 + 产品经理

---

## 📊 八、UI自动化可行性评估

### 8.1 可自动化场景 (✅)

| 功能模块 | 场景 | Playwright实现方案 | 预估难度 | 稳定性 |
|----------|------|-------------------|----------|--------|
| 类目选择 | 搜索类目 | `page.fill()` + `page.click()` | 低 | 高 |
| 类目选择 | 浏览类目树 | `page.locator().nth()` 多次点击 | 中 | 中 |
| 类目选择 | 确认类目 | 验证面包屑文本 `expect(breadcrumb).to_contain_text()` | 低 | 高 |
| 照片上传 | 上传单张 | `page.set_input_files()` | 低 | 高 |
| 照片上传 | 上传多张 | `page.set_input_files([file1, file2])` | 低 | 高 |
| 照片上传 | 验证缩略图 | `expect(image).to_be_visible()` | 低 | 高 |
| 照片上传 | 验证计数器 | `expect(counter).to_have_text("3/20")` | 低 | 高 |
| 照片管理 | 删除照片 | `page.locator('[data-testid="delete-photo"]').click()` | 低 | 高 |
| 表单填写 | 填写Title | `page.fill('[data-testid="title"]', "Red Bike")` | 低 | 高 |
| 表单填写 | 填写Description | `page.fill('[data-testid="description"]', "Long text")` | 低 | 高 |
| 表单填写 | 填写Price | `page.fill('[data-testid="price"]', "50.00")` | 低 | 高 |
| 表单填写 | 选择Condition | `page.select_option('[data-testid="condition"]', "used")` | 低 | 高 |
| 表单填写 | 勾选Contact复选框 | `page.check('[data-testid="messages"]')` | 低 | 高 |
| 推广选项 | 勾选Featured | `page.check('[data-testid="featured"]')` | 低 | 高 |
| 推广选项 | 选择天数 | `page.select_option('[data-testid="days"]', "7")` | 低 | 高 |
| 推广选项 | 验证价格 | `expect(price).to_have_text("£1.00")` | 低 | 高 |
| 提交发布 | 点击Post按钮 | `page.click('[data-testid="post-button"]')` | 低 | 高 |
| 提交发布 | 验证跳转成功 | `expect(page).to_have_url(/thankyou/)` | 低 | 高 |
| 字段验证 | 触发错误提示 | 填写空值后 `page.blur()`,验证错误文本 | 中 | 中 |
| AI生成 | 等待生成完成 | `page.wait_for_selector('[data-testid="ai-content"]', timeout=30000)` | 中 | 中 |
| AI生成 | 验证标题填充 | `expect(title).not.to_be_empty()` | 低 | 高 |
| AI生成 | 验证描述填充 | `expect(description).not.to_be_empty()` | 低 | 高 |
| 草稿恢复 | 验证弹窗出现 | `expect(dialog).to_be_visible()` | 低 | 高 |
| 草稿恢复 | 点击继续编辑 | `page.click('[data-testid="continue"]')` | 低 | 高 |
| 草稿恢复 | 验证数据恢复 | 验证所有字段值 | 中 | 中 |

**可自动化率**: 约90% (核心功能流程全部可自动化)

### 8.2 不可自动化场景 (❌)

| 功能模块 | 场景 | 原因 | 替代方案 |
|----------|------|------|----------|
| 照片管理 | 拖拽调整顺序 | Playwright拖拽API对iOS WebView支持不佳 | 手动测试 + 截图对比 |
| 照片管理 | 横向滚动查看 | 滚动交互依赖手势,难以精确模拟 | 验证DOM元素存在即可 |
| UI视觉 | 骨架屏动画效果 | 动画流畅度需人工判断 | 视觉回归测试(Percy/Applitools) |
| UI视觉 | 颜色规范 | 颜色准确性需设计师确认 | 视觉回归测试 |
| UI视觉 | 字体间距 | 细节布局需人工检查 | 视觉回归测试 |
| 交互体验 | 按钮点击反馈 | 触感反馈(haptic)无法自动化 | 手动测试 |
| AI生成 | 内容质量评估 | 需人工判断生成内容是否合理 | 人工抽查 + 用户反馈 |
| 推广套餐 | View example链接效果 | 需跳转到新页面,示例展示效果需人工确认 | 手动测试 |
| 成功页面 | 体验反馈交互 | 设计稿不明确,需人工确认实际组件 | 手动测试 |
| 兼容性 | 不同iOS版本差异 | 需多设备并行测试 | 云测平台(BrowserStack) |
| 性能 | 内存占用监控 | 需Instruments工具 | 专项性能测试 |
| 安全 | 人工审核AI内容 | 敏感词/不当内容需人工确认 | 内容审核团队 |

**不可自动化率**: 约10%

### 8.3 自动化测试策略

#### 测试金字塔

```
      /\
     /  \  E2E (端到端)     10%
    /----\                  - 关键业务流程
   /      \ Integration    30%
  /--------\                - 模块集成测试
 /          \ Unit         60%
/------------\              - 单元测试
```

**E2E自动化场景** (基于Playwright):
1. **Happy Path**: 完整发布流程(类目选择 → 上传照片 → AI生成 → 填写表单 → 提交成功)
2. **AI生成场景**: 仅照片生成 / 仅标题生成 / 照片+标题生成
3. **草稿场景**: 保存草稿 → 退出 → 重新进入 → 恢复草稿
4. **推广场景**: 选择单个推广 / 选择多个推广 / Select all
5. **错误场景**: 必填字段为空 → 提交 → 显示错误

**集成测试场景** (API测试):
1. 提交广告API
2. AI生成API
3. 类目查询API
4. 草稿保存/恢复API
5. 推广套餐查询API

**单元测试场景** (Jest/Vitest):
1. 字段验证函数 (validateTitle, validateDescription, validatePrice)
2. 字符数统计函数 (countCharacters)
3. 价格格式化函数 (formatPrice)
4. 类目路径解析函数 (parseBreadcrumb)

#### CI/CD集成

```yaml
# .github/workflows/test.yml
name: UI Automation Tests

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  playwright-tests:
    runs-on: macos-latest  # iOS模拟器需macOS
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - uses: actions/setup-python@v4
      
      - name: Install dependencies
        run: |
          pip install playwright pytest
          playwright install webkit  # iOS使用WebKit
      
      - name: Run Playwright tests
        run: pytest test_cases/ai_posting/ --browser=webkit
      
      - name: Upload test report
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: reports/
```

### 8.4 自动化测试ROI评估

**成本**:
- 脚本开发: 2周 (40人时)
- 维护成本: 每月4人时
- 工具成本: Playwright(免费) + BrowserStack($99/月,可选)

**收益**:
- 回归测试时间: 从2天 → 2小时 (节省90%)
- 测试覆盖率: 从60% → 85%
- Bug发现时间: 从生产环境 → 测试环境 (提前1周)
- 人工测试成本降低: 每月节省16人时

**ROI**: 3个月回本,第一年ROI约300%

---

## 🎯 九、推荐测试用例数量与分批策略

### 9.1 基于80/20原则的用例数量控制

**原则**: 用20%的精准测试用例发现80%的风险

**功能复杂度评估**: AI Posting Genesis For Sale Phase 1
- 主流程: 类目选择 → AI生成 → 表单填写 → 推广选项 → 提交
- 流程步骤: 5个主模块
- 字段数量: 12个(Photos, Title, Description, Category, Price, Location, Condition, Contact Email/Phone, 3个推广选项)
- 复杂度: **中等偏高**

**用例数量建议**: 
- 小功能(≤3步骤): 20-30条
- 中等功能(4-6步骤): **40-60条** ← 本功能属于此类
- 大功能(≥7步骤): 80-100条

**最终建议**: **50-55条核心用例** (覆盖80%风险)

### 9.2 分批生成策略

#### 第一批: 核心流程用例 (20-25条, P0)

**目标**: 验证主流程可用性,确保核心功能无阻塞性问题

| 批次 | 用例类型 | 数量 | 示例 |
|------|----------|------|------|
| 1.1 | Happy Path | 3条 | 标准发布流程 / AI生成流程 / 无AI手动流程 |
| 1.2 | 必填字段 | 8条 | 每个必填字段的正常值测试 |
| 1.3 | 类目选择 | 3条 | 搜索类目 / 浏览类目 / 修改类目 |
| 1.4 | 照片上传 | 3条 | 上传单张 / 上传多张 / 删除照片 |
| 1.5 | AI生成 | 3条 | 照片生成 / 标题生成 / 生成失败 |
| 1.6 | 提交成功 | 2条 | 无推广提交 / 有推广提交 |
| **小计** | - | **22条** | - |

**执行时间**: 2小时(手动) / 30分钟(自动化)

#### 第二批: 异常场景用例 (15-18条, P1)

**目标**: 验证错误处理和边界值

| 批次 | 用例类型 | 数量 | 示例 |
|------|----------|------|------|
| 2.1 | 字段验证 | 6条 | Description<15字符 / Price负数 / Phone格式错误等 |
| 2.2 | 边界值 | 4条 | 照片20张 / Description 10000字符 / Price最大值 |
| 2.3 | 网络异常 | 3条 | AI超时 / 照片上传失败 / 提交API失败 |
| 2.4 | 草稿功能 | 3条 | 自动保存 / 恢复草稿 / 放弃草稿 |
| **小计** | - | **16条** | - |

**执行时间**: 1.5小时(手动) / 20分钟(自动化)

#### 第三批: 高级功能用例 (10-12条, P1)

**目标**: 验证推广、Location等可选功能

| 批次 | 用例类型 | 数量 | 示例 |
|------|----------|------|------|
| 3.1 | 推广选项 | 4条 | 单选Featured / 多选推广 / Select all / 价格计算 |
| 3.2 | Location功能 | 3条 | 修改位置 / 显示地图 / 隐私保护 |
| 3.3 | Contact选项 | 2条 | 仅Email / Email+Phone |
| 3.4 | Category标签 | 2条 | 选择标签 / 多选标签 |
| **小计** | - | **11条** | - |

**执行时间**: 1小时(手动) / 15分钟(自动化)

#### 第四批: 边界与兼容性用例 (5-7条, P2)

**目标**: 覆盖低频场景和兼容性

| 批次 | 用例类型 | 数量 | 示例 |
|------|----------|------|------|
| 4.1 | 极端数据 | 2条 | 特殊字符 / emoji / HTML标签 |
| 4.2 | UI交互 | 2条 | 照片拖拽 / 骨架屏动画 |
| 4.3 | 兼容性 | 2条 | 不同iOS版本 / 不同设备尺寸 |
| **小计** | - | **6条** | - |

**执行时间**: 1小时(手动,需多设备)

---

### 9.3 总结

**推荐用例总数**: 55条
- 第一批(P0): 22条 - 核心流程
- 第二批(P1): 16条 - 异常场景
- 第三批(P1): 11条 - 高级功能
- 第四批(P2): 6条 - 边界兼容

**分批执行策略**:
1. **第一轮迭代**: 执行第一批(22条) → 修复阻塞性Bug → 第二轮
2. **第二轮迭代**: 执行第二批(16条) → 修复关键Bug → 第三轮
3. **第三轮迭代**: 执行第三批(11条) → 优化体验 → 回归测试
4. **回归测试**: 执行第一+二+三批(49条) → 验收测试
5. **最终验收**: 执行全部(55条) + 探索式测试 → 上线

**自动化覆盖**: 
- 第一批: 100%自动化 (22条)
- 第二批: 80%自动化 (13条)
- 第三批: 70%自动化 (8条)
- 第四批: 30%自动化 (2条)
- **总自动化率**: 82% (45/55)

---

## 📈 十、覆盖度评估标准

### 10.1 测试维度评分

| 维度 | 权重 | 评分标准 | 目标 | 实际 | 得分 |
|------|------|----------|------|------|------|
| **功能点覆盖** | 30% | 核心功能是否全覆盖 | 100% | TBD | - |
| **用户场景覆盖** | 25% | 真实用户场景覆盖率 | ≥90% | TBD | - |
| **风险点覆盖** | 20% | 高风险场景覆盖率 | 100% | TBD | - |
| **数据边界覆盖** | 15% | 边界值/异常值测试 | ≥80% | TBD | - |
| **安全测试覆盖** | 10% | 安全风险点覆盖 | ≥90% | TBD | - |
| **总分** | 100% | - | - | - | **TBD** |

### 10.2 功能点覆盖详情

#### 核心功能模块

| 模块 | 子功能 | 用例数 | 覆盖率 | 状态 |
|------|--------|--------|--------|------|
| 类目选择 | 搜索类目 | 3 | TBD | ⏳ Pending |
| 类目选择 | 浏览类目树 | 3 | TBD | ⏳ Pending |
| 类目选择 | 类目标签选择 | 2 | TBD | ⏳ Pending |
| AI生成 | 基于照片生成 | 3 | TBD | ⏳ Pending |
| AI生成 | 基于标题生成 | 2 | TBD | ⏳ Pending |
| AI生成 | 重新生成 | 2 | TBD | ⏳ Pending |
| 照片管理 | 上传照片 | 4 | TBD | ⏳ Pending |
| 照片管理 | 删除照片 | 2 | TBD | ⏳ Pending |
| 照片管理 | 拖拽调整 | 1 | TBD | ⏳ Pending |
| 表单填写 | Title字段 | 3 | TBD | ⏳ Pending |
| 表单填写 | Description字段 | 4 | TBD | ⏳ Pending |
| 表单填写 | Price字段 | 3 | TBD | ⏳ Pending |
| 表单填写 | Location字段 | 3 | TBD | ⏳ Pending |
| 表单填写 | Condition字段 | 2 | TBD | ⏳ Pending |
| 表单填写 | Contact字段 | 2 | TBD | ⏳ Pending |
| 推广选项 | Featured选择 | 3 | TBD | ⏳ Pending |
| 推广选项 | Urgent选择 | 2 | TBD | ⏳ Pending |
| 推广选项 | Spotlight选择 | 2 | TBD | ⏳ Pending |
| 推广选项 | 价格计算 | 2 | TBD | ⏳ Pending |
| 草稿功能 | 自动保存 | 2 | TBD | ⏳ Pending |
| 草稿功能 | 草稿恢复 | 3 | TBD | ⏳ Pending |
| 提交发布 | 前端验证 | 5 | TBD | ⏳ Pending |
| 提交发布 | 提交成功 | 2 | TBD | ⏳ Pending |
| 成功页面 | 推广推荐 | 2 | TBD | ⏳ Pending |
| **总计** | - | **55条** | **TBD** | - |

### 10.3 用户场景覆盖

#### 用户画像与场景

**用户1: 新手卖家 (30%)**
- 场景1: 首次发布,依赖AI辅助 → 覆盖 ✅
- 场景2: 不熟悉类目,需要搜索 → 覆盖 ✅
- 场景3: 误操作后恢复草稿 → 覆盖 ✅

**用户2: 经验卖家 (50%)**
- 场景1: 快速发布,直接选类目 → 覆盖 ✅
- 场景2: 不使用AI,手动填写 → 覆盖 ✅
- 场景3: 选择推广套餐 → 覆盖 ✅

**用户3: 商家用户 (20%)**
- 场景1: 批量上传照片 → 覆盖 ✅
- 场景2: 精确填写Item Specifics → 覆盖 ⚠️ (部分,取决于类目)
- 场景3: 频繁发布,依赖草稿 → 覆盖 ✅

**场景覆盖率**: 9/10 = 90% ✅

### 10.4 风险点覆盖

基于第五章风险清单:
- **高风险点(P0)**: 10个 → 目标覆盖率100%
- **中风险点(P1)**: 20个 → 目标覆盖率90%
- **低风险点(P2)**: 10个 → 目标覆盖率70%

**覆盖率计算公式**:
```
风险覆盖率 = (P0覆盖数*1.0 + P1覆盖数*0.7 + P2覆盖数*0.3) / (10*1.0 + 20*0.7 + 10*0.3)
```

### 10.5 遗漏场景识别

**潜在遗漏**:
1. **多设备协同场景**: 
   - 用户在手机A保存草稿,在手机B恢复
   - **建议**: 增加跨设备草稿测试(+2条用例)
   
2. **网络切换场景**:
   - WiFi → 4G切换时的表单状态
   - **建议**: 增加网络切换测试(+1条用例)

3. **长时间填写场景**:
   - 用户填写30分钟后Session过期
   - **建议**: 增加Session管理测试(+1条用例)

4. **辅助功能**:
   - VoiceOver屏幕阅读器支持
   - **建议**: 增加可访问性测试(+2条用例)

5. **特殊类目场景**:
   - 不同类目的Item Specifics字段差异
   - **建议**: 增加多类目测试(+3条用例)

**补充用例建议**: +9条 → 总计64条(若全面覆盖)

### 10.6 最终评分标准

| 总分范围 | 评级 | 建议 |
|----------|------|------|
| 90-100分 | 优秀 ✅ | 可上线,持续监控 |
| 80-89分 | 良好 ⚠️ | 修复关键问题后上线 |
| 70-79分 | 一般 ⚠️ | 补充测试用例,修复后再评估 |
| <70分 | 不足 ❌ | 不建议上线,需全面测试 |

---

## 📝 十一、下一步行动

### 11.1 人工评审阶段

**目标**: 确认AI理解的准确性,回答待确认问题

**行动项**:
1. **产品经理评审** (预计1小时):
   - 确认功能边界与流程描述是否准确
   - 回答第七章"待确认问题清单"(Q1-Q10, Q24-Q30)
   - 确认推广套餐支付流程(Q2)
   - 确认AI生成失败降级方案(Q5)

2. **开发工程师评审** (预计1小时):
   - 确认技术实现细节(Q11-Q20)
   - 提供API文档与接口契约
   - 确认字段验证规则
   - 确认草稿存储方案

3. **UX设计师评审** (预计30分钟):
   - 确认交互细节(Q21-Q29)
   - 提供完整视觉规范(颜色/字体/间距)
   - 确认动画参数
   - 确认错误提示样式

### 11.2 测试用例生成

**第一批用例(核心流程, 22条)**:
- 预计生成时间: 30分钟
- 格式: Markdown
- 包含:
  - 用例ID, 标题, 优先级
  - 前置条件, 测试步骤, 预期结果
  - UI自动化标记(✅/❌)

**第二批用例(异常场景, 16条)**:
- 预计生成时间: 20分钟

**第三批用例(高级功能, 11条)**:
- 预计生成时间: 15分钟

**第四批用例(边界兼容, 6条)**:
- 预计生成时间: 10分钟

### 11.3 自动化脚本开发

**环境准备** (预计2小时):
- 安装Playwright: `pip install playwright`
- 安装iOS模拟器: Xcode Simulator
- 配置测试环境变量(baseURL, credentials)

**脚本开发** (预计2周):
- 第一周: POM页面对象封装 + 第一批用例自动化(22条)
- 第二周: 第二+三批用例自动化(27条) + CI集成

**预估自动化覆盖**: 45/55 = 82%

### 11.4 测试执行

**时间表**:
- 第1天: 执行第一批用例(22条) → 修复阻塞性Bug
- 第2天: 执行第二批用例(16条) → 修复关键Bug
- 第3天: 执行第三批用例(11条) → 优化体验
- 第4天: 回归测试(49条) → 验收
- 第5天: 全量测试(55条) + 探索式测试 → 上线准备

**风险缓解**:
- 若发现高风险Bug(如AI生成完全不可用),暂停后续测试,优先修复
- 若覆盖率<80%,补充测试用例至目标

---

## 📌 十二、附录

### 12.1 缩写与术语

| 术语 | 全称 | 说明 |
|------|------|------|
| AI | Artificial Intelligence | 人工智能 |
| SYI | Sell Your Item | 发布物品(Gumtree术语) |
| POM | Page Object Model | 页面对象模型(自动化测试设计模式) |
| E2E | End-to-End | 端到端测试 |
| API | Application Programming Interface | 应用程序接口 |
| UI | User Interface | 用户界面 |
| UX | User Experience | 用户体验 |
| XSS | Cross-Site Scripting | 跨站脚本攻击 |
| HTML | HyperText Markup Language | 超文本标记语言 |
| URL | Uniform Resource Locator | 统一资源定位符 |
| CDN | Content Delivery Network | 内容分发网络 |
| MVP | Minimum Viable Product | 最小可行产品 |

### 12.2 设计稿关键页面索引

| 页面名称 | Node ID | 坐标 | 说明 |
|----------|---------|------|------|
| APP-sell | 688:48381 | (476, 5912) | 类目搜索入口页 |
| APP-sell / browse | 688:48390 | (923, 6809) | 类目浏览页 |
| APP-sell / suggested categoried | 688:48413 | (923, 5913) | 建议类目页 |
| APP-sell-SYI(for sale)/default | 688:48422 | (2631, 5913) | 完整表单页(包含推广) |
| M-post an ad | 1573:9417 | (1573, 9417) | 移动端优化版 |
| Post- AI生成中 | 688:57162 | (7586.5, 1821) | AI加载状态 |
| Post- AI生成内容加载成功 | 688:56809 | (8422, 1821) | AI生成完成 |
| Post-填写完成 | 688:56904 | (9252, 1821) | 所有字段已填写 |
| Post- 默认态 | 1302:6439 | (3052, 9416) | 空白表单初始状态 |
| Post- 加载草稿弹窗 | 688:57076 | (10778, 1821) | 草稿恢复弹窗 |
| Post- error | 688:57239 | (8837, 1821) | 表单验证错误状态 |
| Post-Succsee | 688:57318 | (10085.75, 1821) | 发布成功页 |
| UI (类目选择) | 688:49011 | (2591, 9416) | 类目图标网格 |

### 12.3 关键字段数据字典

| 字段名 | API字段名(推测) | 类型 | 示例值 |
|--------|-----------------|------|--------|
| Photos | `photos` | `array<string>` | `["https://cdn.gumtree.com/img1.jpg"]` |
| Ad Title | `title` | `string` | `"Red Bike for Sale"` |
| Description | `description` | `string(15-10000)` | `"This is a good bike..."` |
| Category | `category_id` | `integer` | `123456` |
| Price | `price` | `decimal(10,2)` | `50.00` |
| Location | `location` | `object` | `{"city":"London","postcode":"NW5 4HX"}` |
| Condition | `condition` | `enum` | `"used"` |
| Contact Email | `contact.email` | `string(email)` | `"test@example.com"` |
| Contact Phone | `contact.phone` | `string(phone)` | `"07123456789"` |
| Show Map | `show_map` | `boolean` | `true` |
| Promotions | `promotions` | `array<string>` | `["featured","urgent"]` |

### 12.4 参考文档

- Figma设计稿: https://www.figma.com/design/iNgMJe2KOmUnYJF93W7ZaS/Genesis?node-id=688-41441
- Gumtree Posting Rules: (需确认URL)
- Playwright文档: https://playwright.dev/python/
- iOS测试指南: (需补充)

---

**报告结束**

> **下一步**: 请产品经理/开发/设计师评审本报告,回答"待确认问题清单",确认无误后我将分批生成详细测试用例(Markdown格式)。

