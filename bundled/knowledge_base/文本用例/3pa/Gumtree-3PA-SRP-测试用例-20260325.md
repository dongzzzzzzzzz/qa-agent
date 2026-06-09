# Gumtree SRP 页面第三方广告位测试用例

**版本**: 1.2  
**创建日期**: 2026-03-25  
**更新日期**: 2026-05-11  
**测试范围**: SRP (Search Results Page) 第三方广告位（3PA - Third Party Ads）  
**多环境支持**: ✅ 支持  
**测试用例总数**: 45 个（新增模块 15: Google AFS 文本广告验证，共 5 个用例）

> ⚠️ **重要更新 (2026-05-11)**：Bing 搜索广告已完全下线，所有 `bing-*` 相关的 DOM 元素已从页面移除。原 Bing 广告位被 `afscontainer1-fallback`（Gumtree 自有推广横幅）替代。相关用例已更新预期结果。

---

## 📋 测试环境配置

### 支持的测试环境

本测试用例支持以下所有 Gumtree 环境：

| 环境名称 | 环境代码 | 测试URL | 用途 |
|---------|---------|---------|------|
| **Production** | `prod` | https://www.gumtree.com/search?search_category=all&q=ps5 | 生产环境 |
| **Staging** | `staging` | https://www.staging.gumtree.io/search?search_category=all&q=ps5 | 预发布环境 |
| **Zoidberg** | `zoidberg` | https://www.zoidberg.gumtree.io/search?search_category=all&q=ps5 | 测试环境1 |
| **Bixi** | `bixi` | https://www.bixi.gumtree.io/search?search_category=all&q=ps5 | 测试环境2 |
| **Gaga** | `gaga` | https://www.gaga.gumtree.io/search?search_category=all&q=ps5 | 测试环境3 |
| **Unicorn** | `unicorn` | https://www.unicorn.gumtree.io/search?search_category=all&q=ps5 | 测试环境4 |
| **Taro** | `taro` | https://www.taro.gumtree.io/search?search_category=all&q=ps5 | 测试环境5 |

### 环境变量配置

```bash
# 方式1: 使用环境变量
export GUMTREE_ENV=staging
pytest test_cases/3pa/test_3pa_SRP.py -v

# 方式2: 使用命令行参数
pytest test_cases/3pa/test_3pa_SRP.py -v --env=staging

# 方式3: 使用 pytest.ini 配置
# 在 pytest.ini 中添加: env = staging

# 默认环境（未指定时）: prod
```

### 通用配置

```yaml
测试配置:
  浏览器: Chrome/Chromium (Playwright)
  视口尺寸: 1523x800 (桌面端)
  超时设置: 30秒
  无头模式: 可选（默认有头）
  页面类型: SRP (Search Results Page - 搜索结果页)
  
广告位信息:
  浮动广告位:
    id: floatingFooter-container
    别名: floating
    类型: 浮动页脚广告
    标准尺寸: 可变（通常页面底部浮动）
  
  顶部横幅广告:
    id: tBanner-container
    别名: top
    类型: 横幅广告
    标准尺寸: 728x90 (Leaderboard)
  
  中间广告位1:
    id: integratedMpu-container
    别名: middle1
    类型: 嵌入式广告
    标准尺寸: 728x90
    特殊说明: 包含第三方广告脚本(srvb1.com)
  
  中间广告位2:
    id: integratedListing-container
    别名: middle2
    类型: 嵌入式广告
    标准尺寸: 728x90
  
  Bing 搜索广告（已下线）:
    状态: ❌ 已于 2026 年下线，DOM 中不再存在
    原顶部位置 id: bing-top-slot-wrapper（已移除）
    原底部位置 id: bing-bottom-slot-wrapper（已移除）
    替代方案: afscontainer1-fallback（Gumtree 自有推广横幅）
  
  右侧广告位:
    右侧顶部广告1:
      id: rSkyT-container
      别名: topRight
      类型: 侧边栏广告
      标准尺寸: 300x250/600 (Medium Rectangle / Half Page)
    右侧顶部广告2:
      id: rSkyT2-container
      别名: topRight2
      类型: 侧边栏广告
      标准尺寸: 300x250/600
    右侧底部广告1:
      id: rSkyB-container
      别名: bottomRight
      类型: 侧边栏广告
      标准尺寸: 300x250/600
    右侧底部广告2:
      id: rSkyB2-container
      别名: bottomRight2
      类型: 侧边栏广告
      标准尺寸: 300x250/600
  
  Google AFS 文本广告:
    id: afscontainer1
    类型: Google AdSense for Search 文本广告
    状态: 隐藏（按需激活）
    广告平台: syndicatedsearch.goog
  
  其他广告位:
    - floatingFooter-container (浮动页脚广告)
    - pixel-container (追踪像素)
```

### 环境切换示例

```python
# conftest.py 中的环境配置
import os

def get_base_url(env: str = None) -> str:
    """根据环境变量返回对应的 SRP URL"""
    env = env or os.getenv('GUMTREE_ENV', 'prod')
    
    base_urls = {
        'prod': 'https://www.gumtree.com',
        'staging': 'https://www.staging.gumtree.io',
        'zoidberg': 'https://www.zoidberg.gumtree.io',
        'bixi': 'https://www.bixi.gumtree.io',
        'gaga': 'https://www.gaga.gumtree.io',
        'unicorn': 'https://www.unicorn.gumtree.io',
        'taro': 'https://www.taro.gumtree.io',
    }
    
    base = base_urls.get(env, base_urls['prod'])
    return f"{base}/search?search_category=all&q=ps5&search_location=United%20Kingdom"
```

### 测试执行示例

```bash
# 在生产环境执行
pytest test_cases/3pa/test_3pa_SRP.py -v

# 在 Staging 环境执行
pytest test_cases/3pa/test_3pa_SRP.py -v --env=staging

# 执行特定测试用例
pytest test_cases/3pa/test_3pa_SRP.py::TestGumtree3PASRP::test_all_ad_slots_enumeration -v

# 生成 HTML 报告
pytest test_cases/3pa/test_3pa_SRP.py -v --html=reports/3pa_srp_report.html
```

---

## 📊 Application Overview

### 功能定位
SRP (Search Results Page) 是 Gumtree 的搜索结果页面，展示用户搜索关键词（如 "ps5"）后的匹配广告列表。该页面包含多个第三方广告位以及列表区内自有推广（`afscontainer1-fallback`），是网站主要收入来源之一。（历史 Bing 搜索广告已下线。）

### 页面特点
- 显示 2,175 条 PS5 相关广告
- 包含左侧筛选侧边栏（价格、条件、卖家类型、位置、分类）
- 中间为搜索结果列表展示区域
- 列表区内含自有推广横幅（`afscontainer1-fallback`）；Google AFS 容器 `afscontainer1` 存在但通常为隐藏态
- 右侧为第三方展示广告位区域
- 支持排序和保存搜索

### 广告位业务规则
1. **~~Bing 搜索广告~~（已下线）**：Bing 广告所有 DOM 元素（`bing-top-slot-wrapper`、`bing-bottom-slot-wrapper` 等）已从页面完全移除
2. **afscontainer1-fallback（自有推广横幅）**：替代原 Bing 广告位，显示 Gumtree 自有推广内容（"One place for all your Ads — Post an Ad for nearly anything"），链接指向 `/postad/category?utm_source=bing3pa`
3. **Google AFS 文本广告**：afscontainer1 仍存在但隐藏（display: none），包含 iframe 结构
4. **广告位预留机制**：所有标准广告位容器在页面加载时创建
5. **分层布局**：
   - 顶部横幅广告（tBanner）：位于面包屑导航下方
   - 自有推广横幅（afscontainer1-fallback）：位于搜索结果列表中
   - 右侧广告位（rSkyT/rSkyT2/rSkyB/rSkyB2）：位于页面右侧
   - 中间嵌入式广告（integratedMpu/integratedListing）：插入在结果列表之间
   - 浮动广告（floatingFooter）：页面底部浮动
6. **异步加载**：第三方广告通过异步脚本加载
7. **Google AFS 特性**：
   - 使用独立的 text-ads-slot 容器类
   - 包含 master-a-1 和 master-1 iframe
   - 默认隐藏

### 广告位状态枚举
- **已投放已加载**：广告位有尺寸且内容展示正常
- **已预留未投放**：广告位存在但尺寸为 0
- **自有推广横幅已加载**：afscontainer1-fallback 显示 Gumtree 自有推广内容
- **Google AFS 待激活**：AFS 容器存在但隐藏（display: none）
- **加载失败**：广告脚本加载失败，容器为空
- **被屏蔽**：广告拦截器阻止广告加载
- **~~Bing 广告已加载~~**：已下线，不再适用

---

## 🧪 测试用例

### 模块 1: 浮动广告位 (floatingFooter-container / floating)

#### TC-SRP-3PA-001: 浮动广告位容器存在性验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 浏览器无广告拦截插件

**测试步骤**:
1. 访问 SRP 页面 (搜索 "ps5")
2. 等待页面加载完成
3. 检查 DOM 中是否存在 `id="floatingFooter-container"` 的元素

**预期结果**: ✅ 实测
- 元素存在于 DOM 中
- 元素具有 class `ad-slot`
- 元素包含属性 `data-display-ad="true"`

**实际结果**: 
```javascript
{
  "id": "floatingFooter-container",
  "exists": true,
  "visible": true,
  "position": { "width": 0, "height": 0 },
  "childrenCount": 1
}
```

**测试数据**: 无  
**备注**: 浮动广告位预留但当前未使用

---

#### TC-SRP-3PA-002: 浮动广告位展示位置验证
**优先级**: P2  
**UI自动化**: ⚠️ 部分可自动化（需广告投放后验证）  
**前置条件**: 
- TC-SRP-3PA-001 通过
- 浮动广告有投放

**测试步骤**:
1. 访问 SRP 页面
2. 滚动到页面底部
3. 检查浮动广告的位置特性

**预期结果**: ⚠️ 推断
- 广告位固定在页面底部（position: fixed）
- 不随页面滚动而移动
- 横跨整个页面宽度
- 可能有关闭按钮

**实际结果**: 
当前未投放

**测试数据**: 无  
**备注**: 浮动广告通常用于特殊营销活动

---

### 模块 2: 顶部横幅广告位 (tBanner-container / top)

#### TC-SRP-3PA-003: 顶部横幅广告位容器存在性验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 浏览器无广告拦截插件

**测试步骤**:
1. 访问 SRP 页面
2. 等待页面加载完成
3. 检查 DOM 中是否存在 `id="tBanner-container"` 的元素

**预期结果**: ✅ 实测
- 元素存在于 DOM 中
- 元素具有 class `ad-slot`
- 元素包含属性 `data-display-ad="true"`
- 元素包含一个子元素 `<div id="tBanner"></div>`

**实际结果**: 
```javascript
{
  "id": "tBanner-container",
  "exists": true,
  "visible": true,
  "position": { "x": 610.5, "y": 122, "width": 0, "height": 90 },
  "childrenCount": 1
}
```

**测试数据**: 无  
**备注**: 容器已预留，高度为 90px，但宽度为 0（当前未投放）

---

#### TC-SRP-3PA-004: 顶部横幅广告位位置验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-SRP-3PA-003 通过

**测试步骤**:
1. 访问 SRP 页面
2. 获取 `tBanner-container` 的 `getBoundingClientRect()` 信息
3. 验证位置坐标

**预期结果**: ✅ 实测
- 广告位位于页面顶部区域（导航栏下方）
- top 坐标约为 122px
- 高度预留 90px（标准 Leaderboard 高度）

**实际结果**: 
```javascript
{
  "top": 122,
  "left": 610.5,
  "width": 0,
  "height": 90
}
```

**测试数据**: 无  
**备注**: 位置正确，当前未投放

---

### 模块 3: 中间广告位1 (integratedMpu-container / middle1)

#### TC-SRP-3PA-005: 中间广告位1容器存在性验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 检查 DOM 中是否存在 `id="integratedMpu-container"` 的元素

**预期结果**: ✅ 实测
- 元素存在于 DOM 中
- 元素具有 class `ad-slot`
- 元素包含属性 `data-display-ad="true"`

**实际结果**: 
```javascript
{
  "id": "integratedMpu-container",
  "exists": true,
  "visible": true,
  "childrenCount": 2,
  "position": { "x": 390.5, "y": 3055, "width": 728, "height": 0 }
}
```

**测试数据**: 无  
**备注**: 嵌入在搜索结果列表中间，包含第三方广告脚本

---

#### TC-SRP-3PA-006: 中间广告位1广告脚本验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-SRP-3PA-005 通过

**测试步骤**:
1. 访问 SRP 页面
2. 检查 integratedMpu-container 的子元素
3. 验证是否包含广告脚本标签

**预期结果**: ✅ 实测
- 包含 2 个子元素
- 第一个子元素为 `<script>` 标签
- script src 指向第三方广告服务器（srvb1.com）

**实际结果**: 
```html
<div id="integratedMpu-container" class="ad-slot">
  <script data-moa-script="true" src="//srvb1.com/o.js?uid=5a1f69e5ccdad7794d13a92f" type="text/javascript"></script>
  <div id="integratedMpu"></div>
</div>
```

**测试数据**: 无  
**备注**: 使用第三方广告平台（srvb1.com），包含唯一 UID

---

### 模块 4: 中间广告位2 (integratedListing-container / middle2)

#### TC-SRP-3PA-007: 中间广告位2容器存在性验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 检查 DOM 中是否存在 `id="integratedListing-container"` 的元素

**预期结果**: ✅ 实测
- 元素存在于 DOM 中
- 元素具有 class `ad-slot`
- 元素包含属性 `data-display-ad="true"`

**实际结果**: 
```javascript
{
  "id": "integratedListing-container",
  "exists": true,
  "visible": true,
  "childrenCount": 1,
  "position": { "x": 390.5, "y": 5107, "width": 728, "height": 0 }
}
```

**测试数据**: 无  
**备注**: 位于 middle1 下方约 2052px 处

---

#### TC-SRP-3PA-008: 中间广告位2位置验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-SRP-3PA-007 通过

**测试步骤**:
1. 访问 SRP 页面
2. 验证广告位位置

**预期结果**: ✅ 实测
- left 坐标与 middle1 相同（390.5px）
- top 坐标约为 5107px（位于列表下半部分）
- width 为 728px

**实际结果**: 
```javascript
{
  "x": 390.5,
  "y": 5107,
  "width": 728,
  "height": 0
}
```

**测试数据**: 无  
**备注**: 与 middle1 垂直间隔约 2052px

---

### 模块 5: ~~Bing 搜索广告~~ → 自有推广横幅 (afscontainer1-fallback)

> **说明**：Bing 搜索广告已完全下线，页面不再包含任何 `bing-*` DOM。原区域由 Gumtree 自有推广横幅 `afscontainer1-fallback` 承接（文案含 “One place for all your Ads — Post an Ad for nearly anything”，落地页 `/postad/category?utm_source=bing3pa`）。

#### TC-SRP-3PA-009: ~~Bing~~ `bing-*` 相关 DOM 不应存在验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 检查以下典型 Bing 相关 id 是否均**不存在**于 DOM：`bing-top-slot-wrapper`、`bing-bottom-slot-wrapper`、`bing-top-container`、`bing-bottom-container`、`bing-top`、`bing-bottom`、`bing-top-attribution`、`bing-bottom-attribution`、`bing-top-fallback`、`bing-bottom-fallback`（及历史 `bing-text-ad-*` 单元）

**预期结果**: ✅ 实测
- 上述所有 `bing-*` 容器与关键子结构**均不存在**（`exists: false`）
- DOM 查询无匹配节点

**实际结果**: 
```javascript
{
  "bingSelectors": [
    "#bing-top-slot-wrapper",
    "#bing-bottom-slot-wrapper",
    "#bing-top-container",
    "#bing-bottom-container",
    "#bing-top",
    "#bing-bottom",
    "#bing-top-attribution",
    "#bing-bottom-attribution",
    "#bing-top-fallback",
    "#bing-bottom-fallback"
  ],
  "allExist": false,
  "note": "Bing 3PA DOM 已全部移除（2026-05）"
}
```

**测试数据**: 无  
**备注**: Bing 下线后此项为回归守门用例；若任一所列 id 再次出现需排查误发布。

---

#### TC-SRP-3PA-010: afscontainer1-fallback 自有推广横幅内容与链接验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 检查 DOM 中是否存在 `id="afscontainer1-fallback"`（或等价自有推广横幅根节点）
3. 校验计算样式：`display` 为 `block`
4. 校验 `getBoundingClientRect()` 尺寸约为 **736×200** px（宽高允许极小浮动）
5. 校验可见文案包含 **「One place for all your Ads」**（或以页面实际文案为准，保留 “Post an Ad for nearly anything” 语义）
6. 校验主行动链接 `href` 包含 **`/postad/category?utm_source=bing3pa`**

**预期结果**: ✅ 实测
- 元素存在且可见（`display: block`）
- 尺寸约为 736×200px
- 文案与上述自有推广语义一致
- CTA 链接指向 `/postad/category?utm_source=bing3pa`

**实际结果**: 
```javascript
{
  "id": "afscontainer1-fallback",
  "exists": true,
  "visible": true,
  "display": "block",
  "position": { "width": 736, "height": 200 },
  "textContains": "One place for all your Ads",
  "ctaHrefContains": "/postad/category?utm_source=bing3pa"
}
```

**测试数据**: 无  
**备注**: 此为原 Bing 位的站内推广替代形态；不与 Google AFS `afscontainer1`（仍 `display:none`）混淆。

---

#### TC-SRP-3PA-011: afscontainer1-fallback 位置与尺寸验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-SRP-3PA-010 通过

**测试步骤**:
1. 访问 SRP 页面
2. 获取 `afscontainer1-fallback` 的 `getBoundingClientRect()`（及如有父级则在主内容列内对齐关系）
3. 验证位于**搜索结果列表主内容区**内、与列表流一致；尺寸 **736×200** px

**预期结果**: ✅ 实测
- 元素可见且 `display: block`
- **width × height ≈ 736 × 200** px
- 水平方向与主结果列对齐（具体 `x` 随布局 token 浮动，以设计为准）

**实际结果**: 
```javascript
{
  "afscontainer1-fallback": {
    "display": "block",
    "position": { "width": 736, "height": 200 }
  }
}
```

**测试数据**: 无  
**备注**: 取代原 `bing-top` 区域在列表顶部的「文本推广」占位；不再验证 Bing 容器坐标。

---

#### TC-SRP-3PA-012: ~~废弃~~ Bing 底部广告位容器存在性验证
**状态**: 🗑️ **废弃**（Bing 已下线，用例不再执行）  
**优先级**: —  
**前置条件**: 已作废

**测试步骤**: （历史）验证 `bing-bottom-slot-wrapper` 等 — **不适用**

**预期结果**: 废弃  
**实际结果**: Bing DOM 已移除；请使用 TC-SRP-3PA-009 / TC-SRP-3PA-010 / TC-SRP-3PA-011 覆盖当前行为。

**测试数据**: 无  
**备注**: 保留编号仅作文档追溯。

---

#### TC-SRP-3PA-013: ~~废弃~~ Bing 底部广告内容验证
**状态**: 🗑️ **废弃**（Bing 已下线）  
**优先级**: —  
**前置条件**: 已作废

**测试步骤**: （历史）验证 `bing-bottom` 内广告单元 — **不适用**

**预期结果**: 废弃  
**实际结果**: —

**测试数据**: 无  
**备注**: 保留编号仅作文档追溯。

---

#### TC-SRP-3PA-014: ~~废弃~~ Bing 广告 fallback 机制验证（bing-top/bottom-fallback）
**状态**: 🗑️ **废弃**（Bing DOM 不存在，旧 fallback 链路失效）  
**优先级**: —  
**前置条件**: 已作废

**测试步骤**: （历史）检查 `bing-top-fallback`、`bing-bottom-fallback` — **不适用**

**预期结果**: 废弃  
**实际结果**: 当前列表区推广由 `afscontainer1-fallback` 承担；不再有 Bing fallback。

**测试数据**: 无  
**备注**: 保留编号仅作文档追溯。

---

#### TC-SRP-3PA-015: ~~废弃~~ Bing 广告归属标识验证
**状态**: 🗑️ **废弃**（Bing 已下线）  
**优先级**: —  
**前置条件**: 已作废

**测试步骤**: （历史）检查 `bing-*-attribution` — **不适用**

**预期结果**: 废弃  
**实际结果**: —

**测试数据**: 无  
**备注**: 保留编号仅作文档追溯。

---

### 模块 6: 右侧广告位验证

#### TC-SRP-3PA-016: 右侧顶部广告位1容器存在性验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 检查 DOM 中是否存在 `id="rSkyT-container"` 的元素
3. 验证容器属性

**预期结果**: ✅ 实测
- 元素存在于 DOM 中
- 元素具有 class `ad-slot`
- 元素包含属性 `data-display-ad="true"`
- 容器宽度为 300px

**实际结果**: 
```javascript
{
  "id": "rSkyT-container",
  "exists": true,
  "visible": true,
  "position": { "x": 1167, "y": 122, "width": 300, "height": 0 },
  "hasDataAttr": true,
  "childrenCount": 1
}
```

**测试数据**: 无  
**备注**: 右侧顶部广告位1预留但当前未投放

---

#### TC-SRP-3PA-017: 右侧顶部广告位1位置验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-SRP-3PA-016 通过

**测试步骤**:
1. 访问 SRP 页面
2. 获取 rSkyT-container 的位置坐标
3. 验证位置合理性

**预期结果**: ✅ 实测
- 位于页面右侧（left 约 1167px）
- 与页面顶部导航对齐（top 约 122px）
- 宽度为 300px

**实际结果**: 
```javascript
{
  "rSkyT-container": {
    "position": { "x": 1167, "y": 122 },
    "size": { "width": 300, "height": 0 }
  }
}
```

**测试数据**: 无  
**备注**: 位置符合预期，位于页面右侧顶部

---

#### TC-SRP-3PA-018: 右侧顶部广告位2容器存在性验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 检查 DOM 中是否存在 `id="rSkyT2-container"` 的元素
3. 验证容器属性

**预期结果**: ✅ 实测
- 元素存在于 DOM 中
- 元素具有 class `ad-slot`
- 位于 rSkyT-container 下方

**实际结果**: 
```javascript
{
  "id": "rSkyT2-container",
  "exists": true,
  "visible": true,
  "position": { "x": 1167, "y": 146, "width": 300, "height": 0 },
  "hasDataAttr": true,
  "childrenCount": 1
}
```

**测试数据**: 无  
**备注**: 右侧顶部广告位2预留但当前未投放，与 rSkyT 间距 24px

---

#### TC-SRP-3PA-019: 右侧底部广告位1容器存在性验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 滚动到页面中下部
3. 检查 DOM 中是否存在 `id="rSkyB-container"` 的元素

**预期结果**: ✅ 实测
- 元素存在于 DOM 中
- 元素具有 class `ad-slot`
- 位于页面右侧中下部

**实际结果**: 
```javascript
{
  "id": "rSkyB-container",
  "exists": true,
  "visible": true,
  "position": { "x": 1167, "y": 3940, "width": 300, "height": 0 },
  "hasDataAttr": true,
  "childrenCount": 1
}
```

**测试数据**: 无  
**备注**: 右侧底部广告位1预留但当前未投放

---

#### TC-SRP-3PA-020: 右侧底部广告位2容器存在性验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 滚动到页面中下部
3. 检查 DOM 中是否存在 `id="rSkyB2-container"` 的元素

**预期结果**: ✅ 实测
- 元素存在于 DOM 中
- 元素具有 class `ad-slot`
- 位于 rSkyB-container 下方

**实际结果**: 
```javascript
{
  "id": "rSkyB2-container",
  "exists": true,
  "visible": true,
  "position": { "x": 1167, "y": 3964, "width": 300, "height": 0 },
  "hasDataAttr": true,
  "childrenCount": 1
}
```

**测试数据**: 无  
**备注**: 右侧底部广告位2预留但当前未投放，与 rSkyB 间距 24px

---

#### TC-SRP-3PA-021: 右侧广告位垂直对齐验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-SRP-3PA-016~020 通过

**测试步骤**:
1. 访问 SRP 页面
2. 获取所有右侧广告位的坐标
3. 验证它们的左对齐和间距

**预期结果**: ✅ 实测
- 所有右侧广告位 left 坐标相同（1167px）
- rSkyT 和 rSkyT2 垂直间距约 24px
- rSkyB 和 rSkyB2 垂直间距约 24px
- 所有右侧广告位 width 为 300px

**实际结果**: 
```javascript
{
  "alignment": "perfect",
  "leftPosition": 1167,  // 统一左对齐
  "width": 300,  // 统一宽度
  "gaps": {
    "rSkyT-rSkyT2": 24,
    "rSkyB-rSkyB2": 24
  }
}
```

**测试数据**: 无  
**备注**: 右侧广告位完美垂直对齐，间距统一

---

### 模块 7: 所有广告位统计验证

#### TC-SRP-3PA-018: 所有广告位容器枚举验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 查询所有 class 包含 `ad-slot` 的元素
3. 列出所有广告位 ID
4. 确认不再存在 Bing 专有广告位 DOM（已由 TC-SRP-3PA-009 覆盖时可引用）

**预期结果**: ✅ 实测
- 标准广告位容器（.ad-slot）：**9 个**
- **总计：9** 个标准广告位区域（Bing 已下线，`bing-*` 容器不计入）
- 自有推广横幅 `afscontainer1-fallback` 通常**非** `.ad-slot`，单独用 TC-SRP-3PA-010 验证

**实际结果**: 
```javascript
{
  "standardAdSlots": [
    "floatingFooter-container",
    "tBanner-container",
    "integratedMpu-container",
    "integratedListing-container",
    "rSkyT-container",
    "rSkyT2-container",
    "rSkyB-container",
    "rSkyB2-container",
    "pixel-container"
  ],
  "standardCount": 9,
  "totalAdSlotContainers": 9
}
```

**测试数据**: 无  
**备注**: Bing 搜索广告已移除；枚举以 `.ad-slot` 为准

---

#### TC-SRP-3PA-019: 广告位数据属性验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 查询所有 `.ad-slot` 元素
3. 检查每个元素的 `data-display-ad` 属性

**预期结果**: ✅ 实测
- 所有标准广告位容器均包含 `data-display-ad="true"` 属性

**实际结果**: 
所有 9 个标准广告位均包含 `data-display-ad="true"`

**测试数据**: 
```javascript
document.querySelectorAll('.ad-slot[data-display-ad="true"]').length === 9
```

**备注**: 自有推广 `afscontainer1-fallback` 与 Google AFS `afscontainer1` 等非 `.ad-slot` 文本位需单独断言

---

#### TC-SRP-3PA-020: 广告位 ID 唯一性验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 获取所有标准广告位容器 ID（`.ad-slot` 根节点）
3. 检查是否有重复 ID；如有其它推广/AFS 根节点一并纳入 uniqueness 检查（视实现而定）

**预期结果**: ✅ 实测
- 所有 `.ad-slot` 容器 ID 唯一
- 不存在重复容器 ID

**实际结果**: 
```javascript
// 9 个标准 .ad-slot 容器 ID 全部唯一；Bing 相关 DOM 已不存在
```

**测试数据**: 无  
**备注**: 历史性 Bing 文案单元 id 不复用 issue 已不再适用当前 DOM

---

### 模块 8: 广告位真实加载验证

#### TC-SRP-3PA-021: ~~废弃~~ Bing 顶部广告真实加载验证
**状态**: 🗑️ **废弃**（Bing 已从页面移除，无 Bing 顶层容器可断言「真实加载」）  
**优先级**: —  
**前置条件**: 已作废

**测试步骤**: （历史）等待 Bing 顶部广告加载 — **不适用**

**预期结果**: 废弃  
**实际结果**: Bing `bing-*` 不存在；请以 TC-SRP-3PA-009、`afscontainer1-fallback`（TC-SRP-3PA-010）替代。

**测试数据**: 无  
**备注**: 与同编号「右侧广告位」用例并行存在于不同模块时注意区分自动化关键字。

---

#### TC-SRP-3PA-022: ~~废弃~~ Bing 底部广告真实加载验证
**状态**: 🗑️ **废弃**（Bing 已从页面移除）  
**优先级**: —  
**前置条件**: 已作废

**测试步骤**: （历史）滚动到底部验证 Bing bottom — **不适用**

**预期结果**: 废弃  
**实际结果**: —

**测试数据**: 无  
**备注**: 保留编号仅作文档追溯。

---

#### TC-SRP-3PA-023: 中间广告位1脚本加载验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-SRP-3PA-005 通过

**测试步骤**:
1. 访问 SRP 页面
2. 滚动到中间广告位区域
3. 检查 middle1 是否包含广告脚本
4. 验证脚本是否开始加载

**预期结果**: ✅ 实测
- 包含第三方广告脚本（srvb1.com）
- script 标签存在且 src 正确
- 脚本为异步加载

**实际结果**: 
```javascript
{
  "integratedMpu-container": {
    "hasScript": true,
    "scriptSrc": "//srvb1.com/o.js?uid=5a1f69e5ccdad7794d13a92f",
    "scriptLoaded": true,
    "contentHeight": 0  // 脚本已加载但未渲染
  }
}
```

**测试数据**: 无  
**备注**: middle1 是唯一包含第三方广告脚本的标准广告位

---

#### TC-SRP-3PA-024: 所有标准广告位加载状态统计
**优先级**: P1  
**UI自动化**: ⚠️ 部分可自动化（广告投放状态不可控，脚本配合 pytest.skip 处理未投放场景）  
**前置条件**: 
- 访问 SRP 页面
- 滚动整个页面

**测试步骤**:
1. 访问 SRP 页面
2. 滚动整个页面（从顶部到底部）
3. 等待所有广告位有机会加载（10-15秒）
4. 统计所有标准广告位（.ad-slot）的加载状态

**预期结果**: ✅ 实测
- 总广告位数：9 个（标准 `.ad-slot`）
- 有脚本/内容：1 个（middle1）
- 实际加载（尺寸 > 0）：依投放而定（历史探测多为 0）
- **Bing 不再单独统计**（已下线）

**实际结果**: 
```javascript
{
  "standardAdSlots": {
    "total": 9,
    "hasContent": 1,
    "loaded": 0,
    "loadRate": "0%"
  },
  "bingAdSlots": {
    "note": "deprecated — DOM removed"
  }
}
```

**测试数据**: 无  
**备注**: 列表区可见推广以 `afscontainer1-fallback`（自有）为主，见模块 5

---

### 模块 9: 广告位布局和层级验证

#### TC-SRP-3PA-025: ~~废弃~~ Bing 广告优先级验证
**状态**: 🗑️ **废弃**（Bing 已下线，「相对有机结果的优先级」概念不再适用）  
**优先级**: —  
**前置条件**: 已作废

**测试步骤**: （历史）比对 `bing-top` 与首条自然结果 y 坐标 — **不适用**

**预期结果**: 废弃  
**实际结果**: 无 Bing 容器；列表顶区推广见 `afscontainer1-fallback`（TC-SRP-3PA-010/011）。

**测试数据**: 无  
**备注**: 保留编号仅作文档追溯。

---

#### TC-SRP-3PA-026: 广告位垂直顺序验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 获取所有主要广告位的 y 坐标
3. 验证垂直顺序

**预期结果**: ✅ 实测
- 从上到下顺序（**不含**已移除的 `bing-top` / `bing-bottom`）：
  1. tBanner (y: 122)
  2. afscontainer1-fallback（自有推广横幅，位于列表主列；典型 **736×200**，具体 y 随首屏与列表布局浮动）
  3. integratedMpu (y: 3055)
  4. rSkyB (y: 3939)
  5. integratedListing (y: 5107)
  6. pixel (y: 7708)

**实际结果**: 
```javascript
[
  { "id": "tBanner", "y": 122 },
  { "id": "afscontainer1-fallback", "approxSize": "736x200" },
  { "id": "integratedMpu", "y": 3055 },
  { "id": "rSkyB", "y": 3939 },
  { "id": "integratedListing", "y": 5107 },
  { "id": "pixel", "y": 7708 }
]
```

**测试数据**: 无  
**备注**: 历史 `bing-bottom` 槽位已删除；纵向关系以当前 DOM 实测为准。

---

### 模块 10: 广告位性能和加载验证

#### TC-SRP-3PA-027: 广告位不阻塞主内容加载验证
**优先级**: P0  
**UI自动化**: ⚠️ 部分可自动化（需 Performance API 或 Lighthouse 配合）  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 记录 DOMContentLoaded 事件时间
3. 记录搜索结果列表展示时间
4. 检查广告脚本是否异步加载

**预期结果**: ⚠️ 推断
- 搜索结果在 2 秒内展示完成
- 站内推广与三方脚本为异步或非阻塞装配，不应阻塞列表首屏可读
- 标准广告脚本为异步加载（async 或 defer）
- 广告加载失败不影响搜索结果展示

**实际结果**: 
需要使用 Performance API 或 Lighthouse 进行实测

**测试数据**: 无  
**备注**: Bing 已不再参与首屏链路；可关注标准 `.ad-slot` 脚本及自有横幅对 LCP/FCP 的影响

---

#### TC-SRP-3PA-028: 广告位控制台错误验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面
- 打开浏览器开发者工具

**测试步骤**:
1. 打开浏览器控制台
2. 访问 SRP 页面
3. 检查控制台是否有广告相关错误

**预期结果**: ✅ 实测
- 页面可能存在广告脚本加载失败的错误
- 错误为网络请求失败（如 CORS、ERR_FAILED）
- 错误不影响页面核心功能（搜索、浏览结果）

**实际结果**: 
```
Console Errors Detected:
- Access to fetch at 'https://fast.nexx360.io/...' blocked by CORS
- Failed to load resource: net::ERR_FAILED (广告脚本)
- 5 errors, 1 warnings 总计
```

**测试数据**: 无  
**备注**: 广告和第三方脚本错误属于正常现象

---

### 模块 11: 响应式设计验证

#### TC-SRP-3PA-029: 移动端广告位布局验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 调整视口宽度至移动端尺寸（如 375px）

**测试步骤**:
1. 设置视口宽度为 375px（iPhone SE）
2. 访问 SRP 页面
3. 检查广告位的展示状态

**预期结果**: ⚠️ 推断
- 自有推广横幅 / 列表区占位随断点缩放或重排（以设计为准）
- 顶部横幅广告调整或隐藏
- 右侧广告位全部隐藏
- 中间广告位调整宽度

**实际结果**: 
需要在移动端视口下测试

**测试数据**: 
```
视口尺寸: 375x667 (iPhone SE)
```

**备注**: Bing 文本广告已下线；移动端关注 `afscontainer1-fallback` 与标准广告位表现

---

#### TC-SRP-3PA-030: 平板端广告位布局验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 调整视口宽度至平板尺寸（如 768px）

**测试步骤**:
1. 设置视口宽度为 768px（iPad）
2. 访问 SRP 页面
3. 检查广告位布局

**预期结果**: ⚠️ 推断
- 自有推广与普通广告容器随断点保持合理展示（或无投放时的预留态）
- 顶部横幅广告展示
- 右侧广告位可能隐藏
- 中间广告位保持展示

**实际结果**: 
需要在平板视口下测试

**测试数据**: 
```
视口尺寸: 768x1024 (iPad)
```

**备注**: 平板端布局介于桌面和移动端之间

---

### 模块 12: ~~Bing 广告特殊验证~~（已不适用）

#### TC-SRP-3PA-031: ~~废弃~~ Bing 广告单元交互性验证
**状态**: 🗑️ **废弃**（Bing 文本广告已从页面移除）  
**优先级**: —  
**前置条件**: 已作废

**测试步骤**: （历史）检查 Bing 广告单元交互 — **不适用**

**预期结果**: 废弃  
**实际结果**: 无 Bing DOM；站内推广横幅交互见 TC-SRP-3PA-010。

**测试数据**: 无  
**备注**: 保留编号仅作文档追溯。

---

#### TC-SRP-3PA-032: ~~废弃~~ Bing 广告文本内容验证
**状态**: 🗑️ **废弃**  
**优先级**: —  
**前置条件**: 已作废

**测试步骤**: （历史）提取 Bing 广告文案 — **不适用**

**预期结果**: 废弃  
**实际结果**: —

**测试数据**: 无  
**备注**: 保留编号仅作文档追溯。

---

#### TC-SRP-3PA-033: ~~废弃~~ Bing 广告数量动态性验证
**状态**: 🗑️ **废弃**  
**优先级**: —  
**前置条件**: 已作废

**测试步骤**: （历史）多关键词统计 Bing 单元数 — **不适用**

**预期结果**: 废弃  
**实际结果**: —

**测试数据**: 无  

**备注**: 保留编号仅作文档追溯。

---

### 模块 13: 广告拦截场景验证

#### TC-SRP-3PA-034: 广告拦截器启用时页面验证
**优先级**: P1  
**UI自动化**: 🔴 不可自动化（需安装浏览器广告拦截插件）  
**前置条件**: 
- 浏览器安装 AdBlock 或 uBlock Origin
- 启用广告拦截器

**测试步骤**:
1. 启用广告拦截器
2. 访问 SRP 页面
3. 检查页面布局和功能

**预期结果**: ⚠️ 推断
- 标准广告位容器可能被拦截器影响（移除脚本或占位）
- 搜索结果正常展示
- 筛选、排序等核心功能正常
- 自有推广 `afscontainer1-fallback` 是否被拦（依规则）需单独观察

**实际结果**: 
需要安装广告拦截插件测试

**测试数据**: 无  
**备注**: Bing 已无第三方文本广告链路；关注点转向标准 `.ad-slot` 与站内推广。

---

#### TC-SRP-3PA-035: ~~废弃~~ Bing 广告被屏蔽后的 fallback 验证
**状态**: 🗑️ **废弃**（Bing DOM 不存在；历史 `bing-*-fallback` 不再适用）  
**优先级**: —  
**前置条件**: 已作废

**测试步骤**: （历史）广告拦下查看 `bing-*-fallback` — **不适用**

**预期结果**: 废弃  
**实际结果**: 当前无 Bing fallback；请以 TC-SRP-3PA-034 及对 `afscontainer1-fallback` 的兼容性探索替代。

**测试数据**: 无  
**备注**: 保留编号仅作文档追溯。

---

### 模块 14: 特殊场景验证

#### TC-SRP-3PA-036: 无搜索结果时广告位验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 使用无结果的搜索关键词（如 "asdfjkl123xyz"）

**测试步骤**:
1. 访问 SRP 页面，搜索无结果的关键词
2. 检查广告位展示状态
3. 特别关注列表区内自有推广 `afscontainer1-fallback`（是否仍展示、是否占位异常）

**预期结果**: ⚠️ 推断
- 标准广告位容器仍然存在
- 站内推广或无结果状态下的文案/链接行为符合产品预期
- ~~Bing fallback~~ **不适用**

**实际结果**: 
需要使用无结果关键词测试

**测试数据**: 
```
搜索关键词: asdfjkl123xyz (无结果)
```

**备注**: 无搜索结果可能影响广告投放

---

#### TC-SRP-3PA-037: 搜索结果数量少时广告位验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 使用结果数量少的搜索关键词（< 10 条）

**测试步骤**:
1. 访问 SRP 页面，搜索结果少的关键词
2. 检查所有广告位是否仍然展示
3. 特别关注中间和底部广告位

**预期结果**: ⚠️ 推断
- 所有广告位容器仍然存在
- 列表底部的中间广告位／推广区域布局可能压缩或上移（结果太少时）
- 中间广告位可能不展示（结果太少）

**实际结果**: 
需要使用小众关键词测试

**测试数据**: 无  
**备注**: 结果数量影响中间广告位的展示

---

#### TC-SRP-3PA-038: 不同搜索类别广告位验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问不同类别的 SRP 页面

**测试步骤**:
1. 访问不同类别的 SRP（如 For Sale, Motors, Property）
2. 检查广告位配置是否相同
3. 对比差异

**预期结果**: ⚠️ 推断
- 广告位容器结构基本相同
- 自有推广/AFS 相关容器策略可能因类目不同而有差异（以实际为准）
- 可能有类别特定的广告位

**实际结果**: 
需要测试多个类别

**测试数据**: 
```
类别: For Sale, Motors, Property, Jobs, etc.
```

**备注**: 不同类别可能有不同的广告策略

---

#### TC-SRP-3PA-039: 地理位置对广告位的影响验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 更改搜索位置参数

**测试步骤**:
1. 访问 SRP 页面，使用不同的 search_location 参数
2. 检查广告位及列表区自有推广／第三方投放表现是否变化
3. 对比差异

**预期结果**: ⚠️ 推断
- 广告位结构保持一致
- 投放内容与自有推广文案可能根据地理位置变化
- 标准广告位投放可能受地域影响

**实际结果**: 
需要测试不同地理位置

**测试数据**: 
```
location: United Kingdom, London, Manchester, etc.
```

**备注**: 地理位置影响广告内容和投放

---

#### TC-SRP-3PA-040: 页面刷新后广告位一致性验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 记录所有广告位状态及自有推广／第三方投放可见性
3. 刷新页面（F5）
4. 再次记录广告位状态
5. 对比差异

**预期结果**: ⚠️ 推断
- 广告位容器结构保持一致
- 第三方投放素材可能轮换；自有推广文案通常稳定（除非运营调整）
- 标准广告位投放状态可能变化

**实际结果**: 
需要多次刷新测试

**测试数据**: 无  
**备注**: Bing 已不再提供动态文本单元；仍可观察标准广告脚本与站内推广是否稳定

---

### 模块 15: Google AFS 文本广告验证

#### TC-SRP-3PA-041: Google AFS 容器存在性验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 检查 DOM 中是否存在 `id="afscontainer1"` 的元素
3. 验证容器类名和属性

**预期结果**: ✅ 实测
- 元素存在于 DOM 中
- 元素具有 class `text-ads-slot`
- 包含 Google AFS iframe 结构

**实际结果**: 
```javascript
{
  "id": "afscontainer1",
  "exists": true,
  "className": "text-ads-slot",
  "visible": false,  // display: none
  "hasIframe": true,
  "iframeNames": ["master-a-1", "master-1"]
}
```

**测试数据**: 无  
**备注**: Google AFS 容器存在但隐藏，等待激活条件

---

#### TC-SRP-3PA-042: Google AFS iframe 结构验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-SRP-3PA-041 通过

**测试步骤**:
1. 访问 SRP 页面
2. 检查 afscontainer1 内的 iframe 元素
3. 验证 iframe 属性

**预期结果**: ✅ 实测
- 包含 iframe 元素
- iframe name 为 "master-a-1"
- iframe src 指向 `syndicatedsearch.goog/afs/ads`
- 关联的 master-1 iframe 存在

**实际结果**: 
```javascript
{
  "afscontainer1": {
    "iframes": [
      {
        "name": "master-a-1",
        "src": "https://syndicatedsearch.goog/afs/ads/i/iframe.html",
        "visible": false
      },
      {
        "name": "master-1",
        "src": "https://syndicatedsearch.goog/afs/ads?sjk=...",
        "visible": false
      }
    ]
  }
}
```

**测试数据**: 无  
**备注**: Google AFS 使用主从 iframe 结构（master-a-1 和 master-1）

---

#### TC-SRP-3PA-043: Google AFS 激活条件推断
**优先级**: P2  
**UI自动化**: ⚠️ 部分可自动化（激活条件不明确，仅可验证当前状态）  
**前置条件**: 
- TC-SRP-3PA-041 通过

**测试步骤**:
1. 访问 SRP 页面
2. 检查 afscontainer1 的可见性状态
3. 推断激活条件

**预期结果**: ⚠️ 推断
- 默认状态：隐藏（display: none）
- **不再**推断「Bing 失败后备」或与 Bing **互斥**（Bing 已下线）；激活更可能取决于产品/A-B、受众、关键字、地域等运行时策略
- 列表区站内推广主要由 `afscontainer1-fallback` 承担，与隐藏态 AFS **概念上独立**（一为站内 CTA，一为 Google AFS）

**实际结果**: 
```javascript
{
  "afscontainer1": {
    "visible": false
  },
  "bingAdsVisible": false,
  "fallbackPromoVisible": true
}
```

**测试数据**: 无  
**备注**: `fallbackPromoVisible` 指 `afscontainer1-fallback` 自有横幅（见模块 5）；具体键名实现可调整

---

#### TC-SRP-3PA-044: Google AFS 与 ~~Bing 广告~~ 历史互斥关系说明（已不适用）
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 SRP 页面

**测试步骤**:
1. 访问 SRP 页面
2. 检查 `afscontainer1`（Google AFS）可见性
3. 确认页面**不存在** Bing 文本广告 DOM（`bingAdsVisible` 恒为 false）
4. 记录 `afscontainer1-fallback`（自有推广）可见性供对照

**预期结果**: ⚠️ 推断 / 文档化
- **「与 Bing 互斥」** 的产品假设已随 Bing 下线而**失效**；当前只需断言：**无 Bing**、AFS 默认隐藏、自有推广可单独展示
- 若未来 AFS 激活，与 `afscontainer1-fallback` 是否同屏需按新 PRD 单独定义

**实际结果**: 
```javascript
{
  "bingAdsVisible": false,
  "afsVisible": false,
  "promoFallbackVisible": true
}
```

**测试数据**: 无  
**备注**: 历史对比：曾记录 `bingAdsVisible: true` 与 AFS 隐藏；现 Bing 已移除，`bingAdsVisible` 应为 **false**。

---

#### TC-SRP-3PA-045: Google AFS 广告平台标识验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-SRP-3PA-041 通过

**测试步骤**:
1. 访问 SRP 页面
2. 检查 afscontainer1 的数据属性和标识
3. 验证广告平台来源

**预期结果**: ⚠️ 推断
- 容器 class 为 "text-ads-slot"
- iframe src 包含 "syndicatedsearch.goog"
- 与标准 ad-slot 类不同（文本广告 vs 展示广告）
- 可能包含 Google AdSense 归属标识

**实际结果**: 
```javascript
{
  "afscontainer1": {
    "className": "text-ads-slot",
    "iframeSrc": "https://syndicatedsearch.goog/afs/ads/i/iframe.html",
    "platform": "Google AdSense for Search"
  }
}
```

**测试数据**: 无  
**备注**: AFS 使用独立的容器类，与标准展示广告区分

---

## 📸 测试截图

### 截图清单

1. **01_gumtree_srp_full.png**
   - 完整 SRP 页面截图（全页面滚动截图）
   - 包含：顶部导航、列表区自有推广横幅（`afscontainer1-fallback`）、搜索结果、筛选侧边栏、所有广告位、页脚

2. **02_gumtree_srp_viewport.png**
   - 视口截图
   - 清晰显示列表区自有推广与搜索结果列表
   - 包含 Cookie 隐私弹窗

---

## 📝 测试总结

### 已验证功能（实测 ✅）

1. **~~Bing 搜索广告~~ → 自有推广横幅 `afscontainer1-fallback`（Bing 已废弃）**：
   - ✅ **无**任何 `bing-*` DOM（TC-SRP-3PA-009）
   - ✅ 自有推广横幅存在、可见（`display: block`）、约 **736×200** px
   - ✅ 文案包含 “One place for all your Ads”；CTA 指向 `/postad/category?utm_source=bing3pa`
   - 🗑️ 历史 Bing top/bottom、fallback、归因等用例均已**废弃**（仅作文档追溯）

2. **标准广告位容器**：
   - ✅ 所有 **9** 个标准 `.ad-slot` 容器均存在
   - ✅ 右侧广告位 4 个（rSkyT/rSkyT2/rSkyB/rSkyB2）完美垂直对齐
   - ✅ 中间广告位 1（middle1）包含第三方广告脚本（srvb1.com）
   - ✅ 其他标准广告位预留但未投放

3. **Google AFS 文本广告**：
   - ✅ `afscontainer1` 容器存在但隐藏（`display: none`）
   - ✅ 包含 Google AFS iframe 结构（master-a-1, master-1）
   - ✅ 使用独立的 `text-ads-slot` 容器类
   - ✅ ~~与 Bing 互斥~~：**Bing 已下线**；当前以「AFS 默认隐藏 + 自有推广按需展示」的实测组合为准（参见模块 15 TC-043/044）

4. **布局和数据属性**：
   - ✅ 右侧广告位完美垂直对齐（left: 1166.5px，间距 24px）
   - ✅ 标准广告位容器 ID 唯一（`.ad-slot` 级别）
   - ✅ 所有标准广告位包含 `data-display-ad="true"` 属性

5. **广告位垂直顺序**：
   - ✅ 自上而下（当前 DOM）：**tBanner → afscontainer1-fallback → middle1 → rSkyB → middle2 → pixel**（已无 `bing-top` / `bing-bottom`）

### 待验证功能（推断 ⚠️）

1. **标准广告位投放**：
   - ⚠️ 顶部横幅、右侧广告位当前未投放
   - ⚠️ 需要在广告投放时段重新测试

2. **响应式布局**：
   - ⚠️ 移动端和平板端广告位与自有推广的断点行为

3. **广告拦截场景**：
   - ⚠️ 拦截器对标准 `.ad-slot` 与站内推广 `afscontainer1-fallback` 的差异影响

4. **特殊场景**：
   - ⚠️ 无搜索结果时的广告展示
   - ⚠️ 不同类别和地理位置的影响

5. **Google AFS 激活场景**：
   - ⚠️ Google AFS 何时激活（**不再**以「Bing 失败后备」为前提）
   - ⚠️ AFS 与未来列表区推广的并存规则（若有 PRD）
   - ⚠️ AFS 激活后的展示效果

### 关键发现

1. **~~Bing 搜索广告曾是 SRP 核心第三方文本链路，现已下线~~**：
   - 已由 **Gumtree 自有推广横幅**承接原视觉/列表区占位部分的职责
   - 收入与度量口径需切换为「站内推广 + 投放 + Google AFS 可能激活」等新组合

2. **标准广告位作为补充**：
   - 当前投放率低（仅 middle1 有脚本）
   - 预留机制完善
   - 布局合理，不影响用户体验

3. **广告位总数和配置（`.ad-slot` 枚举）**：
   - **9** 个标准广告位（无 Bing wrapper）
   - 另有非 `.ad-slot`：`afscontainer1`（Google AFS，常隐藏）、`afscontainer1-fallback`（自有推广，常显示）
   - 展示广告（标准 ad-slot）与文本/Google AFS/站内推广分列管理

4. **Google AFS**：
   - 容器仍存在且默认隐藏
   - **不再**与 Bing 构成互斥假设；需在真实激活流量下重新定义验收

### 风险识别

1. **文本广告链路变更**：第三方 Bing 收入已关停，需跟进「自有推广 / AFS / 标准投放」的替代指标与 SLA
2. **Google AFS 激活条件仍不明确**：`afscontainer1` 隐藏时机与受众策略需产品与数据侧对齐
3. **标准广告位投放不稳定**：大部分标准广告位未投放
4. **~~历史~~ Bing DOM 漂移**：存量自动化若仍断言 `bing-*` 将导致全红；应改为 TC-009「不应存在」+ fallback 断言
5. **性能**：首屏与列表区仍以多方脚本并行加载为主，需在无 Bing DOM 前提下重测 baseline
6. **~~文本平台双轨 Bing/AFS~~**：已简化为 Google AFS + 站内自有推广等产品组合

### 自动化建议

1. **可自动化场景**：
   - **回归**：断言所有关键 `bing-*` **不存在**
   - 自有推广：`afscontainer1-fallback` 可见性、尺寸（736×200）、文案、`utm_source=bing3pa` 链接
   - Google AFS 容器与 iframe 结构
   - 模块 15 中 **`bingAdsVisible: false`** 与 **AFS 隐藏**快照
   - 标准广告位容器与右侧对齐枚举

2. **难以自动化场景**：
   - 自有推广/投放素材合规与文案审美
   - Google AFS 激活条件触发
   - 广告点击与外跳归因
   - 三方投放素材的动态轮换（非自有横幅）

3. **推荐测试策略**：
   - 将 **P0 守门**设为：`bing-*` 不存在 + `afscontainer1-fallback` 正常展示 + 标准 9 slot 枚举
   - 监控 Google AFS 是否在特定流量下激活
   - 定期检查标准容器完整性及数据属性
   - 校验列表区纵向顺序中含 **fallback**，且 **无任何** Bing 占位

---

## 🔗 相关文档

- [IAB 标准广告尺寸](https://www.iab.com/newadportfolio/)
- [Gumtree 广告政策](https://www.gumtree.com/info/life/advertise-with-us/)
- [Bing Ads 文档](https://about.ads.microsoft.com/)（**历史**：SRP 已不再加载 Bing 3PA；链接保留供背景阅读）
- [Google AdSense for Search 文档](https://support.google.com/adsense/answer/17960)
- [Playwright 测试文档](https://playwright.dev/python/)

---

**编写人**: Web QA Brain (AI)  
**最后更新**: 2026-05-11  
**版本历史**:
- v1.2 (2026-05-11): Bing 搜索广告已下线，更新所有 Bing 相关用例预期结果，新增 `afscontainer1-fallback` 自有推广横幅验证；`.ad-slot` 总计修正为 9；若干用例标为废弃
- v1.1 (2026-03-25): **新增模块 15：Google AFS 文本广告验证**，包含 5 个用例（TC-SRP-3PA-041~045），验证 Google AdSense for Search 容器、iframe 结构、激活条件、与 Bing 广告互斥性；更新右侧广告位详细信息
- v1.0 (2026-03-25): 初始版本，基于 SRP 页面探测生成，包含 Bing 搜索广告验证