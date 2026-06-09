# Gumtree BRP 页面第三方广告位测试用例

**版本**: 1.5  
**创建日期**: 2026-03-25  
**更新日期**: 2026-05-11  
**测试范围**: BRP (Browse Results Page) 第三方广告位（3PA - Third Party Ads）  
**多环境支持**: ✅ 支持  
**测试用例总数**: 52 个（新增模块 16: Google AFS 文本广告验证，共 5 个用例）

⚠️ **重要更新 (2026-05-11)**：Bing 搜索广告已完全下线，所有 `bing-*` 相关的 DOM 元素已从页面移除。原 Bing 广告位被 `afscontainer1-fallback`（Gumtree 自有推广横幅）替代。相关用例已更新预期结果。

---

## 📋 测试环境配置

### 支持的测试环境

本测试用例支持以下所有 Gumtree 环境：

| 环境名称 | 环境代码 | 测试URL | 用途 |
|---------|---------|---------|------|
| **Production** | `prod` | https://www.gumtree.com/for-sale | 生产环境 |
| **Staging** | `staging` | https://www.staging.gumtree.io/for-sale | 预发布环境 |
| **Zoidberg** | `zoidberg` | https://www.zoidberg.gumtree.io/for-sale | 测试环境1 |
| **Bixi** | `bixi` | https://www.bixi.gumtree.io/for-sale | 测试环境2 |
| **Gaga** | `gaga` | https://www.gaga.gumtree.io/for-sale | 测试环境3 |
| **Unicorn** | `unicorn` | https://www.unicorn.gumtree.io/for-sale | 测试环境4 |
| **Taro** | `taro` | https://www.taro.gumtree.io/for-sale | 测试环境5 |

### 环境变量配置

```bash
# 方式1: 使用环境变量
export GUMTREE_ENV=staging
pytest test_cases/3pa/test_3pa_BRP.py -v

# 方式2: 使用命令行参数
pytest test_cases/3pa/test_3pa_BRP.py -v --env=staging

# 方式3: 使用 pytest.ini 配置
# 在 pytest.ini 中添加: env = staging

# 默认环境（未指定时）: prod (https://www.gumtree.com/for-sale)
```

### 通用配置

```yaml
测试配置:
  浏览器: Chrome/Chromium (Playwright)
  视口尺寸: 1523x800 (桌面端)
  超时设置: 30秒
  无头模式: 可选（默认有头）
  页面类型: BRP (Browse Results Page - 浏览结果页)
### 通用配置

```yaml
测试配置:
  浏览器: Chrome/Chromium (Playwright)
  视口尺寸: 1523x800 (桌面端)
  超时设置: 30秒
  无头模式: 可选（默认有头）
  页面类型: BRP (Browse Results Page - 浏览结果页)
  
广告位信息:
  顶部横幅广告:
    id: tBanner-container
    别名: top
    类型: 横幅广告
    标准尺寸: 728x90 (Leaderboard)
  
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
  
  中间广告位1:
    id: integratedMpu-container
    别名: middle1
    类型: 嵌入式广告
    标准尺寸: 728x90
  
  中间广告位2:
    id: integratedListing-container
    别名: middle2
    类型: 嵌入式广告
    标准尺寸: 728x90
  
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
  
  # 以下 Bing 配置已下线（2026-05-11），仅作历史记录
  Bing 顶部/底部搜索广告:
    状态: 已废弃 — 页面不再渲染任何 bing-* DOM
    说明: 原 bing-top-slot-wrapper / bing-bottom-slot-wrapper 及相关子节点已移除
  
  Google AFS 文本广告 (afscontainer1):
    id: afscontainer1
    类型: Google AdSense for Search 文本广告
    状态: 隐藏（display: none；按需可能激活）
    广告平台: syndicatedsearch.goog
  
  Gumtree 自有推广横幅 (afscontainer1-fallback):
    id: afscontainer1-fallback
    类型: 替代原 Bing 文本广告位的自有横幅
    状态: 可见（display: block）
    典型尺寸: 约 736x200px
    文案示例: "One place for all your Ads — Post an Ad for nearly anything"
    链接: /postad/category?utm_source=bing3pa
  
  其他广告位:
    - floatingFooter-container (浮动页脚广告)
    - pixel-container (追踪像素)
```

### 环境切换示例

```python
# conftest.py 中的环境配置
import os

def get_base_url(env: str = None) -> str:
    """根据环境变量返回对应的 BRP URL"""
    env = env or os.getenv('GUMTREE_ENV', 'prod')
    
    urls = {
        'prod': 'https://www.gumtree.com/for-sale',
        'staging': 'https://www.staging.gumtree.io/for-sale',
        'zoidberg': 'https://www.zoidberg.gumtree.io/for-sale',
        'bixi': 'https://www.bixi.gumtree.io/for-sale',
        'gaga': 'https://www.gaga.gumtree.io/for-sale',
        'unicorn': 'https://www.unicorn.gumtree.io/for-sale',
        'taro': 'https://www.taro.gumtree.io/for-sale',
    }
    
    return urls.get(env, urls['prod'])
```

### 测试执行示例

```bash
# 在生产环境执行
pytest test_cases/3pa/test_3pa_BRP.py -v

# 在 Staging 环境执行
pytest test_cases/3pa/test_3pa_BRP.py -v --env=staging

# 在 Zoidberg 环境执行
pytest test_cases/3pa/test_3pa_BRP.py -v --env=zoidberg

# 执行特定测试用例
pytest test_cases/3pa/test_3pa_BRP.py::test_top_banner_exists -v

# 生成 HTML 报告
pytest test_cases/3pa/test_3pa_BRP.py -v --html=reports/3pa_brp_report.html
```

---

## 📊 Application Overview

### 功能定位
BRP (Browse Results Page) 是 Gumtree 的浏览结果页面，展示 "For Sale" 分类下的所有待售商品广告列表。该页面包含多个第三方广告位，是网站主要收入来源之一。

### 页面特点
- 显示 1,395,801 条待售广告
- 包含左侧筛选侧边栏（价格、条件、卖家类型、位置、分类）
- 中间为广告列表展示区域
- 右侧为第三方广告位区域
- 支持排序和保存搜索

### 广告位业务规则
1. **广告位预留机制**：所有标准广告位容器在页面加载时创建，即使未投放也保持存在
2. **~~Bing 搜索广告优先加载~~（已废弃，2026-05-11）**：原 Bing 文本广告已完全下线，不再加载；原区域由 `afscontainer1-fallback` 自有推广横幅承接
3. **分层布局**：
   - 文本广告/自有推广区：原 Bing 顶部位现由 `afscontainer1-fallback` 展示（`afscontainer1` 本体仍存在于 DOM 但隐藏）
   - 顶部横幅广告（tBanner）：位于面包屑导航下方
   - 右侧顶部广告（rSkyT/rSkyT2）：位于页面右侧顶部区域
   - 中间嵌入式广告（integratedMpu/integratedListing）：插入在列表项之间
   - 右侧底部广告（rSkyB/rSkyB2）：位于页面右侧底部区域
4. **异步加载**：第三方广告通过异步脚本加载，不阻塞主内容
5. **响应式设计**：桌面端展示所有广告位，移动端可能调整布局
6. **数据标记**：所有标准广告位包含 `data-display-ad="true"` 属性
7. **~~Bing 广告特性~~（已废弃，2026-05-11）**：历史行为；当前页面无 `bing-*` DOM。替代为 **afscontainer1-fallback**：Gumtree 自有推广横幅，链向发帖分类页（`utm_source=bing3pa`）

### 广告位状态枚举
- **已投放已加载**：广告位有尺寸（如 300x250），内容展示正常
- **已预留未投放**：广告位存在但尺寸为 0 或高度为 0
- **~~Bing 广告已加载~~（已废弃）**：Bing 搜索广告已下线；验证时预期为无 `bing-*` 元素
- **加载失败**：广告脚本加载失败，容器为空
- **被屏蔽**：广告拦截器阻止广告加载

---

## 🧪 测试用例

### 模块 1: 顶部横幅广告位 (tBanner-container / top)

#### TC-BRP-3PA-001: 顶部横幅广告位容器存在性验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 浏览器无广告拦截插件
- 网络连接正常

**测试步骤**:
1. 访问 `https://www.gumtree.com/for-sale`
2. 等待页面加载完成（DOM Ready）
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

#### TC-BRP-3PA-002: 顶部横幅广告位位置验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-BRP-3PA-001 通过

**测试步骤**:
1. 访问 BRP 页面
2. 获取 `tBanner-container` 的 `getBoundingClientRect()` 信息
3. 验证位置坐标

**预期结果**: ✅ 实测
- 广告位位于页面顶部区域（导航栏下方）
- top 坐标约为 122px
- 位于页面中央水平位置
- 高度预留 90px（标准 Leaderboard 高度）

**实际结果**: 
```javascript
{
  "top": 122,
  "left": 610.5,
  "width": 0,
  "height": 90,
  "right": 610.5,
  "bottom": 212
}
```

**测试数据**: 视口宽度 1523px  
**备注**: 位置正确，当前未投放（宽度为0）

---

#### TC-BRP-3PA-003: 顶部横幅广告位标准尺寸验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 广告位有投放

**测试步骤**:
1. 访问 BRP 页面
2. 获取广告位容器的 width 和 height
3. 验证尺寸是否符合标准

**预期结果**: ⚠️ 推断（当前未投放）
- width: 728px（标准 Leaderboard 宽度）
- height: 90px（标准 Leaderboard 高度）
- 符合 IAB 标准广告尺寸

**实际结果**: 
- width: 0px (未投放)
- height: 90px (已预留高度)

**测试数据**: 无  
**备注**: 需要在广告投放时段重新验证宽度

---

### 模块 2: 右侧顶部广告位 (rSkyT-container / topRight)

#### TC-BRP-3PA-004: 右侧顶部广告位1容器存在性验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 浏览器视口宽度 > 1024px（桌面端）

**测试步骤**:
1. 访问 BRP 页面
2. 检查 DOM 中是否存在 `id="rSkyT-container"` 的元素

**预期结果**: ✅ 实测
- 元素存在于 DOM 中
- 元素具有 class `ad-slot`
- 元素包含属性 `data-display-ad="true"`

**实际结果**: 
```javascript
{
  "id": "rSkyT-container",
  "exists": true,
  "visible": true,
  "childrenCount": 1,
  "position": { "x": 1166.5, "y": 122, "width": 300, "height": 0 }
}
```

**测试数据**: 无  
**备注**: 容器预留，宽度 300px，当前未投放（高度为 0）

---

#### TC-BRP-3PA-005: 右侧顶部广告位1位置验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-BRP-3PA-004 通过

**测试步骤**:
1. 访问 BRP 页面
2. 获取广告位坐标信息
3. 验证位置是否在页面右侧

**预期结果**: ✅ 实测
- left 坐标约为 1166.5px（页面右侧）
- top 坐标约为 122px（与顶部横幅同高）
- width 固定为 300px（标准侧边栏广告宽度）

**实际结果**: 
```javascript
{
  "x": 1166.5,
  "y": 122,
  "width": 300,
  "height": 0
}
```

**测试数据**: 无  
**备注**: 位置正确，宽度已预留，待广告投放后高度会变化

---

#### TC-BRP-3PA-006: 右侧顶部广告位1标准尺寸验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 广告位有投放

**测试步骤**:
1. 访问 BRP 页面
2. 等待广告加载
3. 获取广告位尺寸

**预期结果**: ⚠️ 推断
- width: 300px（固定）
- height: 250px、600px 或 1050px（常见高度：Medium Rectangle、Half Page、Portrait）
- 符合 IAB 标准广告尺寸

**实际结果**: 
当前未投放，高度为 0

**测试数据**: 无  
**备注**: 300px 宽度已确认，需要在广告投放时验证高度

---

### 模块 3: 右侧顶部广告位2 (rSkyT2-container / topRight2)

#### TC-BRP-3PA-007: 右侧顶部广告位2容器存在性验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 浏览器视口宽度 > 1024px

**测试步骤**:
1. 访问 BRP 页面
2. 检查 DOM 中是否存在 `id="rSkyT2-container"` 的元素

**预期结果**: ✅ 实测
- 元素存在于 DOM 中
- 元素具有 class `ad-slot`
- 元素包含属性 `data-display-ad="true"`

**实际结果**: 
```javascript
{
  "id": "rSkyT2-container",
  "exists": true,
  "visible": true,
  "childrenCount": 1,
  "position": { "x": 1166.5, "y": 146, "width": 300, "height": 0 }
}
```

**测试数据**: 无  
**备注**: 容器预留，位于 rSkyT 下方 24px 处

---

#### TC-BRP-3PA-008: 右侧顶部广告位2位置验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-BRP-3PA-007 通过

**测试步骤**:
1. 访问 BRP 页面
2. 验证广告位与 rSkyT 的位置关系

**预期结果**: ✅ 实测
- left 坐标与 rSkyT 相同（1166.5px）
- top 坐标略低于 rSkyT（146px vs 122px，相差 24px）
- width 固定为 300px

**实际结果**: 
```javascript
{
  "x": 1166.5,
  "y": 146,
  "width": 300,
  "height": 0
}
```

**测试数据**: 无  
**备注**: 与 rSkyT 垂直排列，间距 24px

---

### 模块 4: 中间广告位1 (integratedMpu-container / middle1)

#### TC-BRP-3PA-009: 中间广告位1容器存在性验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 BRP 页面

**测试步骤**:
1. 访问 BRP 页面
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
  "position": { "x": 390.5, "y": 3021.5, "width": 728, "height": 0 }
}
```

**测试数据**: 无  
**备注**: 嵌入在列表项中间，宽度 728px，包含广告脚本标签

---

#### TC-BRP-3PA-010: 中间广告位1位置验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-BRP-3PA-009 通过

**测试步骤**:
1. 访问 BRP 页面
2. 滚动到中间广告位位置
3. 验证位置坐标

**预期结果**: ✅ 实测
- left 坐标约为 390.5px（主内容区域左侧）
- top 坐标约为 3021.5px（列表中间位置）
- width 为 728px（标准横幅广告宽度）

**实际结果**: 
```javascript
{
  "x": 390.5,
  "y": 3021.5,
  "width": 728,
  "height": 0
}
```

**测试数据**: 无  
**备注**: 嵌入在列表项之间，不影响列表布局

---

#### TC-BRP-3PA-011: 中间广告位1广告脚本验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-BRP-3PA-009 通过

**测试步骤**:
1. 访问 BRP 页面
2. 检查 integratedMpu-container 的子元素
3. 验证是否包含广告脚本标签

**预期结果**: ✅ 实测
- 包含 2 个子元素
- 第一个子元素为 `<script>` 标签
- script src 指向第三方广告服务器（如 srvb1.com）

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

### 模块 5: 中间广告位2 (integratedListing-container / middle2)

#### TC-BRP-3PA-012: 中间广告位2容器存在性验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 BRP 页面

**测试步骤**:
1. 访问 BRP 页面
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
  "position": { "x": 390.5, "y": 5073.5, "width": 728, "height": 0 }
}
```

**测试数据**: 无  
**备注**: 位于 middle1 下方约 2052px 处

---

#### TC-BRP-3PA-013: 中间广告位2位置验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-BRP-3PA-012 通过

**测试步骤**:
1. 访问 BRP 页面
2. 滚动到广告位位置
3. 验证位置坐标

**预期结果**: ✅ 实测
- left 坐标与 middle1 相同（390.5px）
- top 坐标约为 5073.5px（位于列表下半部分）
- width 为 728px

**实际结果**: 
```javascript
{
  "x": 390.5,
  "y": 5073.5,
  "width": 728,
  "height": 0
}
```

**测试数据**: 无  
**备注**: 与 middle1 垂直间隔约 2052px

---

### 模块 6: 右侧底部广告位1 (rSkyB-container / bottomRight)

#### TC-BRP-3PA-014: 右侧底部广告位1容器存在性验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 浏览器视口宽度 > 1024px

**测试步骤**:
1. 访问 BRP 页面
2. 检查 DOM 中是否存在 `id="rSkyB-container"` 的元素

**预期结果**: ✅ 实测
- 元素存在于 DOM 中
- 元素具有 class `ad-slot`
- 元素包含属性 `data-display-ad="true"`

**实际结果**: 
```javascript
{
  "id": "rSkyB-container",
  "exists": true,
  "visible": true,
  "childrenCount": 1,
  "position": { "x": 1166.5, "y": 4078.75, "width": 300, "height": 0 }
}
```

**测试数据**: 无  
**备注**: 容器预留，位于页面右侧底部区域

---

#### TC-BRP-3PA-015: 右侧底部广告位1位置验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-BRP-3PA-014 通过

**测试步骤**:
1. 访问 BRP 页面
2. 滚动到页面底部区域
3. 验证广告位位置

**预期结果**: ✅ 实测
- left 坐标与右侧顶部广告位相同（1166.5px）
- top 坐标约为 4078.75px（页面下半部分）
- width 为 300px

**实际结果**: 
```javascript
{
  "x": 1166.5,
  "y": 4078.75,
  "width": 300,
  "height": 0
}
```

**测试数据**: 无  
**备注**: 与顶部右侧广告位垂直对齐

---

### 模块 7: 右侧底部广告位2 (rSkyB2-container / bottomRight2)

#### TC-BRP-3PA-016: 右侧底部广告位2容器存在性验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 浏览器视口宽度 > 1024px

**测试步骤**:
1. 访问 BRP 页面
2. 检查 DOM 中是否存在 `id="rSkyB2-container"` 的元素

**预期结果**: ✅ 实测
- 元素存在于 DOM 中
- 元素具有 class `ad-slot`
- 元素包含属性 `data-display-ad="true"`

**实际结果**: 
```javascript
{
  "id": "rSkyB2-container",
  "exists": true,
  "visible": true,
  "childrenCount": 1,
  "position": { "x": 1166.5, "y": 4102.75, "width": 300, "height": 0 }
}
```

**测试数据**: 无  
**备注**: 容器预留，位于 rSkyB 下方 24px 处

---

#### TC-BRP-3PA-017: 右侧底部广告位2位置验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-BRP-3PA-016 通过

**测试步骤**:
1. 访问 BRP 页面
2. 验证广告位与 rSkyB 的位置关系

**预期结果**: ✅ 实测
- left 坐标与 rSkyB 相同（1166.5px）
- top 坐标略低于 rSkyB（4102.75px vs 4078.75px，相差 24px）
- width 为 300px

**实际结果**: 
```javascript
{
  "x": 1166.5,
  "y": 4102.75,
  "width": 300,
  "height": 0
}
```

**测试数据**: 无  
**备注**: 与 rSkyB 垂直排列，间距 24px

---

### 模块 8: 其他广告位验证

#### TC-BRP-3PA-018: 所有广告位容器枚举验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 BRP 页面

**测试步骤**:
1. 访问 BRP 页面
2. 查询所有 class 包含 `ad-slot` 的元素
3. 列出所有广告位 ID

**预期结果**: ✅ 实测
- 至少包含以下 7 个主要广告位：
  1. `tBanner-container` (top)
  2. `rSkyT-container` (topRight)
  3. `rSkyT2-container` (topRight2)
  4. `integratedMpu-container` (middle1)
  5. `integratedListing-container` (middle2)
  6. `rSkyB-container` (bottomRight)
  7. `rSkyB2-container` (bottomRight2)
- 额外包含：
  8. `floatingFooter-container`
  9. `pixel-container`

**实际结果**: 
```javascript
[
  { "id": "tBanner-container", "alias": "top" },
  { "id": "rSkyT-container", "alias": "topRight" },
  { "id": "rSkyT2-container", "alias": "topRight2" },
  { "id": "integratedMpu-container", "alias": "middle1" },
  { "id": "integratedListing-container", "alias": "middle2" },
  { "id": "rSkyB-container", "alias": "bottomRight" },
  { "id": "rSkyB2-container", "alias": "bottomRight2" },
  { "id": "floatingFooter-container" },
  { "id": "pixel-container" }
]
```

**测试数据**: 无  
**备注**: 共 9 个广告位容器，所有容器均包含 data-display-ad="true" 标记

---

#### TC-BRP-3PA-019: floatingFooter-container 浮动页脚广告验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 BRP 页面

**测试步骤**:
1. 访问 BRP 页面
2. 检查 `floatingFooter-container` 元素
3. 验证其状态

**预期结果**: ✅ 实测
- 容器存在
- 尺寸为 0x0（当前未使用）
- 可能作为浮动广告或特殊活动时启用

**实际结果**: 
```javascript
{
  "id": "floatingFooter-container",
  "position": { "width": 0, "height": 0 },
  "visible": true
}
```

**测试数据**: 无  
**备注**: 浮动页脚广告位，当前未启用

---

#### TC-BRP-3PA-020: pixel-container 追踪像素验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 BRP 页面

**测试步骤**:
1. 访问 BRP 页面
2. 检查 `pixel-container` 元素
3. 验证其位置

**预期结果**: ✅ 实测
- 容器存在
- 尺寸为 0x0（不占用可视空间）
- 位于页面底部（y 坐标很大）
- 用于嵌入追踪像素

**实际结果**: 
```javascript
{
  "id": "pixel-container",
  "position": { "x": 0, "y": 7987.5, "width": 0, "height": 0 },
  "visible": true
}
```

**测试数据**: 无  
**备注**: 追踪像素容器，位于页面底部，不影响布局

---

### 模块 9: 广告位数据属性验证

#### TC-BRP-3PA-021: 广告位 data-display-ad 属性验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 BRP 页面

**测试步骤**:
1. 访问 BRP 页面
2. 查询所有 `.ad-slot` 元素
3. 检查每个元素的 `data-display-ad` 属性

**预期结果**: ✅ 实测
- 所有广告位容器均包含 `data-display-ad="true"` 属性
- 该属性用于标识广告位，便于广告脚本查找和注入

**实际结果**: 
所有 9 个广告位均包含 `data-display-ad="true"`

**测试数据**: 
```javascript
document.querySelectorAll('.ad-slot[data-display-ad="true"]').length === 9
```

**备注**: 统一的数据属性便于广告SDK识别和管理

---

#### TC-BRP-3PA-022: 广告位 ID 唯一性验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 BRP 页面

**测试步骤**:
1. 访问 BRP 页面
2. 获取所有广告位 ID
3. 检查是否有重复 ID

**预期结果**: ✅ 实测
- 所有广告位 ID 唯一
- 不存在重复 ID

**实际结果**: 
```javascript
[
  "tBanner-container",
  "integratedMpu-container",
  "integratedListing-container",
  "rSkyT-container",
  "rSkyT2-container",
  "rSkyB-container",
  "rSkyB2-container",
  "floatingFooter-container",
  "pixel-container"
]
// 所有 ID 唯一，无重复
```

**测试数据**: 无  
**备注**: ID 唯一性是 DOM 标准要求

---

### 模块 10: 广告位布局关系验证

#### TC-BRP-3PA-023: 右侧广告位垂直排列验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 BRP 页面

**测试步骤**:
1. 访问 BRP 页面
2. 获取所有右侧广告位的坐标
3. 验证它们的左对齐和垂直间距

**预期结果**: ✅ 实测
- 所有右侧广告位 left 坐标相同（1166.5px）
- rSkyT 和 rSkyT2 垂直间距约 24px
- rSkyB 和 rSkyB2 垂直间距约 24px
- 所有右侧广告位 width 为 300px

**实际结果**: 
```javascript
[
  { "id": "rSkyT", "x": 1166.5, "y": 122, "width": 300 },
  { "id": "rSkyT2", "x": 1166.5, "y": 146, "width": 300 },  // 间距 24px
  { "id": "rSkyB", "x": 1166.5, "y": 4078.75, "width": 300 },
  { "id": "rSkyB2", "x": 1166.5, "y": 4102.75, "width": 300 }  // 间距 24px
]
```

**测试数据**: 无  
**备注**: 右侧广告位完美垂直对齐，间距统一

---

#### TC-BRP-3PA-024: 中间广告位水平对齐验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 BRP 页面

**测试步骤**:
1. 访问 BRP 页面
2. 获取中间广告位的坐标
3. 验证它们的左对齐

**预期结果**: ✅ 实测
- middle1 和 middle2 的 left 坐标相同（390.5px）
- 两者 width 均为 728px
- 垂直间距约 2052px

**实际结果**: 
```javascript
[
  { "id": "integratedMpu", "x": 390.5, "y": 3021.5, "width": 728 },
  { "id": "integratedListing", "x": 390.5, "y": 5073.5, "width": 728 }
]
// 间距：5073.5 - 3021.5 = 2052px
```

**测试数据**: 无  
**备注**: 中间广告位嵌入在列表项之间，保持左对齐

---

### 模块 11: 广告位加载性能验证

#### TC-BRP-3PA-025: 广告位不阻塞主内容加载验证
**优先级**: P0  
**UI自动化**: ⚠️ 部分可自动化（需 Performance API 或 Lighthouse 配合）  
**前置条件**: 
- 访问 BRP 页面
- 监控网络请求和页面加载时间

**测试步骤**:
1. 访问 BRP 页面
2. 记录 DOMContentLoaded 事件时间
3. 记录页面主要内容展示时间
4. 检查广告脚本是否异步加载

**预期结果**: ⚠️ 推断
- 主内容（列表项）在 2 秒内展示完成
- 广告脚本为异步加载（async 或 defer）
- 广告加载失败不影响列表展示

**实际结果**: 
需要使用 Performance API 或 Lighthouse 进行实测

**测试数据**: 无  
**备注**: 性能测试需要专门工具（如 Lighthouse、WebPageTest）

---

#### TC-BRP-3PA-026: 广告位控制台错误验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 BRP 页面
- 打开浏览器开发者工具

**测试步骤**:
1. 打开浏览器控制台
2. 访问 BRP 页面
3. 检查控制台是否有广告相关错误
4. 验证错误是否影响页面功能

**预期结果**: ✅ 实测
- 页面可能存在广告脚本加载失败的错误
- 错误为网络请求失败（如 CORS、ERR_FAILED）
- 错误不影响页面核心功能（筛选、浏览列表、排序）

**实际结果**: 
```
Console Errors Detected:
- Access to fetch at 'https://fast.nexx360.io/...' blocked by CORS
- Failed to load resource: net::ERR_FAILED (广告脚本)
- 7 errors, 2 warnings 总计
```

**测试数据**: 无  
**备注**: 广告和第三方脚本错误属于正常现象，不影响主功能

---

### 模块 12: 响应式设计验证

#### TC-BRP-3PA-027: 移动端广告位布局验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 调整视口宽度至移动端尺寸（如 375px）

**测试步骤**:
1. 设置视口宽度为 375px（iPhone SE）
2. 访问 BRP 页面
3. 检查广告位的展示状态

**预期结果**: ⚠️ 推断
- 顶部横幅广告可能调整尺寸（320x50 或隐藏）
- 右侧广告位全部隐藏或移至列表底部
- 中间广告位调整宽度适配移动端
- 可能展示移动端专用广告位

**实际结果**: 
需要在移动端视口下测试

**测试数据**: 
```
视口尺寸: 375x667 (iPhone SE)
```

**备注**: 响应式广告需要在实际设备或模拟器中测试

---

#### TC-BRP-3PA-028: 平板端广告位布局验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 调整视口宽度至平板尺寸（如 768px）

**测试步骤**:
1. 设置视口宽度为 768px（iPad）
2. 访问 BRP 页面
3. 检查广告位布局

**预期结果**: ⚠️ 推断
- 顶部横幅广告展示，尺寸可能调整
- 右侧广告位可能隐藏或调整位置
- 中间广告位保持展示
- 布局保持良好可用性

**实际结果**: 
需要在平板视口下测试

**测试数据**: 
```
视口尺寸: 768x1024 (iPad)
```

**备注**: 不同屏幕尺寸的广告布局可能不同

---

### 模块 13: 广告拦截器场景验证

#### TC-BRP-3PA-029: 广告拦截器启用时页面验证
**优先级**: P1  
**UI自动化**: 🔴 不可自动化（需安装浏览器广告拦截插件）  
**前置条件**: 
- 浏览器安装 AdBlock 或 uBlock Origin
- 启用广告拦截器

**测试步骤**:
1. 启用广告拦截器
2. 访问 BRP 页面
3. 检查页面布局和功能

**预期结果**: ⚠️ 推断
- 广告位容器可能被移除或隐藏
- 列表正常展示，不出现大片空白
- 筛选、排序等核心功能正常
- 右侧区域收缩或隐藏

**实际结果**: 
需要安装广告拦截插件测试

**测试数据**: 无  
**备注**: 网站应对广告被屏蔽的场景做防御性设计

---

#### TC-BRP-3PA-030: 广告位被屏蔽后的控制台信息
**优先级**: P2  
**UI自动化**: 🔴 不可自动化（需安装浏览器广告拦截插件）  
**前置条件**: 
- 启用广告拦截器

**测试步骤**:
1. 启用广告拦截器
2. 打开浏览器控制台
3. 访问 BRP 页面
4. 检查控制台信息

**预期结果**: ⚠️ 推断
- 控制台可能显示广告脚本被阻止的信息
- 不出现页面崩溃或 JavaScript 错误
- 网站可能检测到广告被屏蔽并记录日志

**实际结果**: 
需要使用广告拦截器测试

**测试数据**: 无  
**备注**: 部分网站会检测广告拦截器并提示用户

---

### 模块 14: 广告位真实加载验证

#### TC-BRP-3PA-031: 顶部横幅广告内容加载验证 (top)
**优先级**: P0  
**UI自动化**: ⚠️ 部分可自动化（广告投放状态不可控，脚本配合 pytest.skip 处理未投放场景）  
**前置条件**: 
- TC-BRP-3PA-001 通过（容器存在）
- Cookie 隐私协议已接受

**测试步骤**:
1. 访问 BRP 页面 `${BASE_URL}/for-sale`
2. 接受 Cookie 隐私协议（如有弹窗）
3. 等待 3-5 秒让广告加载
4. 检查 `tBanner-container` 内是否有内容：
   ```javascript
   const container = document.getElementById('tBanner-container');
   const hasContent = container.children.length > 0 && 
                      (container.innerHTML.trim().length > 100 ||
                       container.querySelector('iframe, script, img, div[id^="google"]'));
   ```
5. 验证广告位状态

**预期结果**: ✅ 实测 / ⚠️ 推断
- 广告位内有内容（非空容器）
- 包含以下至少一种：
  - iframe 元素（第三方广告）
  - script 标签（异步加载脚本）
  - img 标签（图片广告）
  - 带特定 ID 的 div（如 `google_ads_iframe_*`）
- 容器高度 > 0px（已投放）
- 内容 HTML 长度 > 100 字符

**实际结果**: 
```javascript
{
  "hasContent": false,  // 当前未投放
  "containerHeight": 90,  // 预留高度
  "childrenCount": 1,
  "innerHTML": "<div id=\"tBanner\"></div>",  // 仅空子容器
  "hasIframe": false,
  "hasScript": false
}
```

**测试数据**: 无  
**备注**: 
- 当前测试时广告未投放（高度 90px 但宽度为 0）
- 需要在广告投放时段重新测试
- 验证逻辑适用于任何第三方广告平台

---

#### TC-BRP-3PA-032: 顶部横幅广告 iframe 加载验证
**优先级**: P1  
**UI自动化**: ⚠️ 部分可自动化（广告投放状态不可控，脚本配合 pytest.skip 处理未投放场景）  
**前置条件**: 
- TC-BRP-3PA-031 通过（有内容）
- 广告已投放

**测试步骤**:
1. 访问 BRP 页面
2. 等待广告加载（最多 10 秒）
3. 检查 iframe 元素：
   ```javascript
   const iframe = document.querySelector('#tBanner-container iframe');
   if (iframe) {
     return {
       exists: true,
       src: iframe.src,
       width: iframe.offsetWidth,
       height: iframe.offsetHeight,
       visible: iframe.offsetWidth > 0 && iframe.offsetHeight > 0,
       id: iframe.id,
       name: iframe.name
     };
   }
   ```

**预期结果**: ⚠️ 推断（需广告投放）
- iframe 元素存在
- iframe 尺寸正常：
  - width ≈ 728px（标准 Leaderboard 宽度）
  - height ≈ 90px（标准 Leaderboard 高度）
- iframe 处于可见状态（visible: true）
- iframe 有 name 或 id 属性（可能包含广告位路径信息）

**实际结果**: 
当前未投放，无 iframe

**测试数据**: 无  
**备注**: 
- Google Ads iframe 的 src 可能为空字符串（动态加载特性）
- 验证逻辑：只要 iframe 可见且有尺寸即认为加载成功
- iframe name 可能包含广告位路径，如 `google_ads_iframe_/5144/desktop/brp/top_0`

---

#### TC-BRP-3PA-033: 右侧顶部广告位内容加载验证 (topRight/topRight2)
**优先级**: P0  
**UI自动化**: ⚠️ 部分可自动化（广告投放状态不可控，脚本配合 pytest.skip 处理未投放场景）  
**前置条件**: 
- TC-BRP-3PA-004 和 TC-BRP-3PA-007 通过（容器存在）

**测试步骤**:
1. 访问 BRP 页面
2. 等待广告加载
3. 检查右侧顶部两个广告位的内容：
   ```javascript
   const checkRightAd = (containerId) => {
     const container = document.getElementById(containerId);
     return {
       hasContent: container.innerHTML.trim().length > 50,
       hasIframe: !!container.querySelector('iframe'),
       height: container.offsetHeight,
       width: container.offsetWidth,
       childrenCount: container.children.length
     };
   };
   
   return {
     rSkyT: checkRightAd('rSkyT-container'),
     rSkyT2: checkRightAd('rSkyT2-container')
   };
   ```

**预期结果**: ⚠️ 推断（需广告投放）
- 至少有一个右侧广告位有内容
- 有内容的广告位：
  - 高度 > 0（常见：250px、600px）
  - 宽度 = 300px（固定）
  - 包含 iframe 或其他广告内容
- 如果两个广告位都投放，高度可能不同（不同广告尺寸）

**实际结果**: 
```javascript
{
  "rSkyT": {
    "hasContent": false,
    "hasIframe": false,
    "height": 0,
    "width": 300,
    "childrenCount": 1
  },
  "rSkyT2": {
    "hasContent": false,
    "hasIframe": false,
    "height": 0,
    "width": 300,
    "childrenCount": 1
  }
}
```

**测试数据**: 无  
**备注**: 
- 当前两个广告位都未投放（高度为 0）
- 侧边栏广告通常在列表内容加载后再加载
- 可能存在懒加载机制（滚动到可视区域才加载）

---

#### TC-BRP-3PA-034: 中间广告位内容加载验证 (middle1/middle2)
**优先级**: P0  
**UI自动化**: ⚠️ 部分可自动化（广告投放状态不可控，脚本配合 pytest.skip 处理未投放场景）  
**前置条件**: 
- TC-BRP-3PA-009 和 TC-BRP-3PA-012 通过（容器存在）

**测试步骤**:
1. 访问 BRP 页面
2. 滚动到中间广告位区域（确保进入视口）
3. 等待广告加载（懒加载）
4. 检查中间广告位内容：
   ```javascript
   const checkMiddleAd = (containerId) => {
     const container = document.getElementById(containerId);
     return {
       hasContent: container.innerHTML.trim().length > 100,
       hasIframe: !!container.querySelector('iframe'),
       hasScript: !!container.querySelector('script'),
       height: container.offsetHeight,
       width: container.offsetWidth,
       scriptSrc: container.querySelector('script')?.src || null,
       childrenCount: container.children.length
     };
   };
   
   return {
     middle1: checkMiddleAd('integratedMpu-container'),
     middle2: checkMiddleAd('integratedListing-container')
   };
   ```

**预期结果**: ✅ 实测（middle1 有脚本）/ ⚠️ 推断
- **middle1 (integratedMpu-container)**：
  - ✅ 包含第三方广告脚本（srvb1.com）
  - ✅ 有 2 个子元素（script + div）
  - ⚠️ 高度 > 0（等待脚本加载后）
  - 宽度 = 728px
- **middle2 (integratedListing-container)**：
  - ⚠️ 有内容加载（需验证）
  - 高度 > 0
  - 宽度 = 728px

**实际结果**: 
```javascript
{
  "middle1": {
    "hasContent": true,  // ✅ 有脚本标签
    "hasIframe": false,
    "hasScript": true,   // ✅ 第三方脚本
    "height": 0,         // 脚本尚未执行完成
    "width": 728,
    "scriptSrc": "//srvb1.com/o.js?uid=5a1f69e5ccdad7794d13a92f",
    "childrenCount": 2
  },
  "middle2": {
    "hasContent": false,
    "hasIframe": false,
    "hasScript": false,
    "height": 0,
    "width": 728,
    "childrenCount": 1
  }
}
```

**测试数据**: 无  
**备注**: 
- middle1 是唯一包含第三方广告脚本的广告位
- 使用 srvb1.com 广告平台（非 Google Ads）
- 脚本异步加载，可能需要额外等待时间
- 中间广告位通常有懒加载机制（IntersectionObserver）

---

#### TC-BRP-3PA-035: 右侧底部广告位内容加载验证 (bottomRight/bottomRight2)
**优先级**: P1  
**UI自动化**: ⚠️ 部分可自动化（广告投放状态不可控，脚本配合 pytest.skip 处理未投放场景）  
**前置条件**: 
- TC-BRP-3PA-014 和 TC-BRP-3PA-016 通过（容器存在）

**测试步骤**:
1. 访问 BRP 页面
2. 滚动到页面底部区域（右侧底部广告位）
3. 等待广告加载
4. 检查右侧底部两个广告位的内容

**预期结果**: ⚠️ 推断（需广告投放）
- 与右侧顶部广告位验证逻辑相同
- 至少有一个底部广告位有内容
- 有内容的广告位：
  - 高度 > 0
  - 宽度 = 300px
  - 包含 iframe 或其他广告内容

**实际结果**: 
```javascript
{
  "rSkyB": {
    "hasContent": false,
    "hasIframe": false,
    "height": 0,
    "width": 300
  },
  "rSkyB2": {
    "hasContent": false,
    "hasIframe": false,
    "height": 0,
    "width": 300
  }
}
```

**测试数据**: 无  
**备注**: 
- 底部广告位通常在用户滚动到页面下半部分时才加载（懒加载）
- 投放率可能低于顶部广告位
- 需要模拟用户滚动行为触发懒加载

---

#### TC-BRP-3PA-036: 广告位内容尺寸验证
**优先级**: P1  
**UI自动化**: ⚠️ 部分可自动化（广告投放状态不可控，脚本配合 pytest.skip 处理未投放场景）  
**前置条件**: 
- 任一广告位有内容加载（iframe 或其他）

**测试步骤**:
1. 访问 BRP 页面
2. 等待广告加载
3. 对于每个有内容的广告位，获取容器尺寸和内容尺寸
4. 验证尺寸关系：
   ```javascript
   const validateAdSize = (containerId) => {
     const container = document.getElementById(containerId);
     const iframe = container.querySelector('iframe');
     
     if (!iframe) return { valid: false, reason: 'No iframe' };
     
     const containerRect = container.getBoundingClientRect();
     const iframeRect = iframe.getBoundingClientRect();
     
     return {
       valid: iframeRect.width <= containerRect.width + 10 &&
              iframeRect.height <= containerRect.height + 10,
       container: { w: containerRect.width, h: containerRect.height },
       iframe: { w: iframeRect.width, h: iframeRect.height },
       overflow: {
         width: iframeRect.width - containerRect.width,
         height: iframeRect.height - containerRect.height
       }
     };
   };
   ```

**预期结果**: ⚠️ 推断
- 如果是 iframe：尺寸接近容器尺寸（允许±10px误差）
- 符合标准广告尺寸：
  - 顶部横幅：728x90
  - 右侧广告：300x250、300x600
  - 中间广告：728x90
- iframe 内容不超出容器范围：
  - `iframe_width <= container_width + 10`
  - `iframe_height <= container_height + 10`
- 最小尺寸验证：
  - width > 100px
  - height > 50px

**实际结果**: 
当前所有广告位未投放，无 iframe 可验证

**测试数据**: 无  
**备注**: 
- 允许 iframe 稍小于容器（居中或靠边对齐）
- 不允许超出容器（避免布局破坏）
- 某些广告可能使用响应式尺寸

---

#### TC-BRP-3PA-037: 广告位懒加载验证
**优先级**: P1  
**UI自动化**: ⚠️ 部分可自动化（广告投放状态不可控，脚本配合 pytest.skip 处理未投放场景）  
**前置条件**: 
- 访问 BRP 页面

**测试步骤**:
1. 访问 BRP 页面
2. **不滚动页面**，检查初始视口内广告位加载状态
3. 记录初始加载的广告位
4. **滚动到页面中间**，检查中间广告位加载状态
5. **滚动到页面底部**，检查底部广告位加载状态
6. 分析懒加载行为

**预期结果**: ⚠️ 推断
- **初始视口**（不滚动）：
  - 顶部横幅广告（top）：立即加载
  - 右侧顶部广告（topRight/topRight2）：立即加载
  - 中间广告位（middle1/middle2）：不加载（不在视口内）
  - 右侧底部广告（bottomRight/bottomRight2）：不加载（不在视口内）
- **滚动到中间**：
  - 中间广告位开始加载
  - 使用 IntersectionObserver 触发
- **滚动到底部**：
  - 右侧底部广告位开始加载

**实际结果**: 
需要使用 Playwright 模拟滚动行为进行实测

**测试数据**: 
```javascript
// 滚动到指定位置
await page.evaluate(() => window.scrollTo(0, 3000));  // 中间位置
await page.waitForTimeout(2000);  // 等待懒加载
```

**备注**: 
- 懒加载优化页面性能，减少初始加载时间
- 典型实现：IntersectionObserver API
- 触发条件：广告位进入视口 50-100% 时开始加载
- 验证重点：确保用户看到的区域广告已加载

---

#### TC-BRP-3PA-038: 所有广告位加载状态统计验证
**优先级**: P1  
**UI自动化**: ⚠️ 部分可自动化（广告投放状态不可控，脚本配合 pytest.skip 处理未投放场景）  
**前置条件**: 
- 访问 BRP 页面
- 完成所有滚动操作（确保所有广告位进入视口）

**测试步骤**:
1. 访问 BRP 页面
2. 滚动整个页面（从顶部到底部）
3. 等待所有广告位有机会加载（10-15秒）
4. 统计所有 9 个广告位的加载状态：
   ```javascript
   const adSlots = [
     'tBanner-container',
     'rSkyT-container',
     'rSkyT2-container',
     'integratedMpu-container',
     'integratedListing-container',
     'rSkyB-container',
     'rSkyB2-container',
     'floatingFooter-container',
     'pixel-container'
   ];
   
   const stats = adSlots.map(id => {
     const container = document.getElementById(id);
     return {
       id: id,
       exists: !!container,
       hasContent: container?.innerHTML.trim().length > 50,
       hasIframe: !!container?.querySelector('iframe'),
       hasScript: !!container?.querySelector('script'),
       height: container?.offsetHeight || 0,
       width: container?.offsetWidth || 0,
       loaded: (container?.offsetHeight > 0 && container?.offsetWidth > 0)
     };
   });
   
   return {
     total: adSlots.length,
     loaded: stats.filter(s => s.loaded).length,
     hasContent: stats.filter(s => s.hasContent).length,
     hasIframe: stats.filter(s => s.hasIframe).length,
     details: stats
   };
   ```

**预期结果**: ⚠️ 推断
- 总广告位数：9 个
- 至少有内容（script/iframe）：≥ 1 个
- 实际加载（尺寸 > 0）：1-5 个（取决于投放策略）
- 典型加载率：20-50%
- middle1 必定有脚本标签（srvb1.com）

**实际结果**: 
```javascript
{
  "total": 9,
  "loaded": 0,           // 无广告位加载完成（高度为0）
  "hasContent": 1,       // 仅 middle1 有脚本标签
  "hasIframe": 0,
  "details": [
    { "id": "tBanner-container", "loaded": false, "height": 90, "width": 0 },
    { "id": "rSkyT-container", "loaded": false, "height": 0, "width": 300 },
    { "id": "rSkyT2-container", "loaded": false, "height": 0, "width": 300 },
    { "id": "integratedMpu-container", "loaded": false, "hasScript": true, "height": 0, "width": 728 },
    { "id": "integratedListing-container", "loaded": false, "height": 0, "width": 728 },
    { "id": "rSkyB-container", "loaded": false, "height": 0, "width": 300 },
    { "id": "rSkyB2-container", "loaded": false, "height": 0, "width": 300 },
    { "id": "floatingFooter-container", "loaded": false, "height": 0, "width": 0 },
    { "id": "pixel-container", "loaded": false, "height": 0, "width": 0 }
  ]
}
```

**测试数据**: 无  
**备注**: 
- 当前测试时段广告投放率为 0%（仅有脚本标签，未实际渲染）
- 需要在不同时段、不同地域重新测试
- 广告加载率受多种因素影响：
  - 时段（工作日 vs 周末）
  - 地域（不同国家/地区）
  - 用户特征（Cookie、浏览历史）
  - 广告预算和库存
- 统计数据可用于监控广告系统健康度

---

### 模块 15: Bing 搜索广告验证（历史模块名保留；Bing 已下线，见文首说明）

#### TC-BRP-3PA-039: ~~Bing 顶部广告位容器~~ → 页面无 `bing-*` DOM 验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 BRP 页面

**测试步骤**:
1. 访问 BRP 页面
2. 检查 DOM：下列 **历史 Bing** 容器/子节点均 **不应存在**：`bing-top-slot-wrapper`、`bing-bottom-slot-wrapper` 以及任意 ID/class 前缀为 `bing-` 的节点（示例：`bing-top-container`、`bing-top`、`bing-bottom`、`bing-top-fallback`、`bing-bottom-fallback`、`bing-text-ad-1` 等）

**预期结果**: ✅ 实测（2026-05-11）
- **所有上述 `bing-*` 元素 `exists`: false**

**实际结果**: 
```javascript
{
  "bing-top-slot-wrapper": { "exists": false },
  "bing-bottom-slot-wrapper": { "exists": false },
  "bingSelectorsFound": [],  // 页面级查询无匹配
  "note": "Bing 搜索广告 DOM 已从 BRP 完全移除"
}
```

**测试数据**: 无  
**备注**: 替代展示见 TC-040、`afscontainer1-fallback`

---

#### TC-BRP-3PA-040: ~~Bing 顶部广告内容~~ → `afscontainer1-fallback` 自有推广横幅存在与内容验证
**优先级**: P0  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-BRP-3PA-039 通过（无 `bing-*`）

**测试步骤**:
1. 访问 BRP 页面
2. 检查 DOM 中是否存在 `id="afscontainer1-fallback"`（或等价锚点）
3. 断言可见性：`display` 含 `block`（或等价：元素在视口中可见）、尺寸约 **736×200px**（允许小幅浮动）
4. 文本内容包含 **"One place for all your Ads"**（或完整标语含 `Post an Ad for nearly anything`）
5. 验证推广链：存在指向 `/postad/category?utm_source=bing3pa` 的链接（完整 URL 或 path+query）

**预期结果**: ✅ 实测（2026-05-11）
- `afscontainer1-fallback` 存在且 **visible: true**
- 尺寸约 736×200px
- 文案与链接符合自有推广规格

**实际结果**: 
```javascript
{
  "id": "afscontainer1-fallback",
  "exists": true,
  "visible": true,
  "display": "block",
  "position": { "width": 736, "height": 200 },
  "textContains": "One place for all your Ads — Post an Ad for nearly anything",
  "ctaHrefContains": "/postad/category?utm_source=bing3pa"
}
```

**测试数据**: 无  
**备注**: 同期 `afscontainer1`（Google AFS）仍存在但 **display: none**，见模块 16

---

#### TC-BRP-3PA-041: ~~Bing 顶部广告位置和尺寸~~ → `afscontainer1-fallback` 位置与尺寸验证
**优先级**: P1  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-BRP-3PA-040 通过

**测试步骤**:
1. 访问 BRP 页面
2. 获取 `afscontainer1-fallback` 的 `getBoundingClientRect`（或 Playwright bounding box）
3. 验证位于主内容/列表顶部附近（与原 Bing 顶部位同一业务区域），宽高约 **736×200px**

**预期结果**: ✅ 实测（2026-05-11）
- 元素可见，`display: block`
- 宽度约 736px，高度约 200px（允许 ±10% 浮动，以环境为准）

**实际结果**: 
```javascript
{
  "afscontainer1-fallback": {
    "visible": true,
    "display": "block",
    "position": { "x": "<与主列表左缘对齐或在主列内>", "y": "<列表顶部区域>", "width": 736, "height": 200 }
  },
  "afscontainer1": {
    "exists": true,
    "visible": false,
    "display": "none"
  }
}
```

**测试数据**: 无  
**备注**: 精确 `x/y` 随布局微调，以与首屏列表关系合理为准

---

#### TC-BRP-3PA-042: Bing 底部广告位容器存在性验证 **[废弃]**
**状态**: 🚫 **废弃** — Bing 底部槽位已从页面移除；不得再预期 `bing-bottom-slot-wrapper` 存在。底部区域验证改为标准列表/页脚与其它 3PA 位，不包含 Bing。

**历史说明**: 本用例曾验证底部 Bing 容器；2026-05-11 起 **不适用**。

---

#### TC-BRP-3PA-043: Bing 底部广告内容验证 **[废弃]**
**状态**: 🚫 **废弃** — 无 `bing-bottom` / `bing-text-ad-1` 等节点；不适用。

---

#### TC-BRP-3PA-044: Bing 广告 fallback 机制验证 **[废弃]**
**状态**: 🚫 **废弃** — `bing-*-fallback` DOM 已不存在。文本位备用展示由 **`afscontainer1-fallback`**（自有横幅）承接，验证见 TC-040。

---

#### TC-BRP-3PA-045: Bing 广告位置优先级验证 **[废弃]**
**状态**: 🚫 **废弃** — Bing 广告已下线；列表与 `afscontainer1-fallback` 的相对位置见 TC-041。

---

#### TC-BRP-3PA-046: Bing 广告单元交互性验证 **[废弃]**
**状态**: 🚫 **废弃** — 无 Bing 文本广告单元；`afscontainer1-fallback` 内 CTA 链接触发规则可单独立项（不计入本历史用例）。

---

#### TC-BRP-3PA-047: Bing 广告整体统计验证 **[废弃]**
**状态**: 🚫 **废弃** — Bing 广告位数量、单元数统计不再适用；当前以「零 `bing-*` + 单一 `afscontainer1-fallback` 可见」为基线。

---

### 模块 16: Google AFS 文本广告验证

#### TC-BRP-3PA-048: Google AFS 容器存在性验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 BRP 页面

**测试步骤**:
1. 访问 BRP 页面
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
  "iframeCount": 2
}
```

**测试数据**: 无  
**备注**: Google AFS 容器存在但隐藏，等待激活条件；列表上方同期可见 **自有推广** 见 `afscontainer1-fallback`（TC-BRP-3PA-040）

---

#### TC-BRP-3PA-049: Google AFS iframe 结构验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-BRP-3PA-048 通过

**测试步骤**:
1. 访问 BRP 页面
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

#### TC-BRP-3PA-050: Google AFS 激活条件推断
**优先级**: P2  
**UI自动化**: ⚠️ 部分可自动化（激活条件不明确，仅可验证当前状态）  
**前置条件**: 
- TC-BRP-3PA-048 通过

**测试步骤**:
1. 访问 BRP 页面
2. 检查 afscontainer1 的可见性状态
3. 推断激活条件

**预期结果**: ⚠️ 推断
- 默认状态：隐藏（display: none）
- 可能激活条件：
  - 特定浏览类别
  - 特定地理位置
  - A/B 测试场景
- ~~与 Bing 广告互斥~~（Bing 搜索广告已下线，2026-05-11；不再适用二选一逻辑）

**实际结果**: 
```javascript
{
  "afscontainer1": {
    "visible": false,
    "display": "none"
  },
  "afscontainer1-fallback": {
    "visible": true,
    "display": "block"
  }
}
```

**测试数据**: 无  
**备注**: Bing 已移除；当前主列表上方可见文本区为 **自有推广** `afscontainer1-fallback`，Google AFS 容器仍隐藏

---

#### TC-BRP-3PA-051: Google AFS 与文本广告位状态验证（Bing 已下线）
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- 访问 BRP 页面

**测试步骤**:
1. 访问 BRP 页面
2. 同时检查 `afscontainer1`、页面内是否仍存在 Bing 相关可见区域、以及 `afscontainer1-fallback` 可见性
3. 验证：无 Bing 第三方文本广告；AFS 默认隐藏；自有推广横幅可独立展示

**预期结果**: ✅ 实测（2026-05-11）
- **无** `bing-*` 广告位展示（`bingAdsVisible`: false）
- `afscontainer1` 保持隐藏时，可与 **可见的** `afscontainer1-fallback` 同时存在于页面（二者职能不同：AFS vs 自有推广）

**实际结果**: 
```javascript
{
  "bingAdsVisible": false,
  "bingDomPresent": false,
  "afsVisible": false,
  "afsFallbackVisible": true,
  "bothAfsAndFallbackVisible": false  // afscontainer1 与 fallback 一般不同时为 display:block 展示 AFS 内容；fallback 为推广横幅
}
```

**测试数据**: 无  
**备注**: 原「与 Bing 互斥」语义随 Bing 下线作废；现行基线为无 Bing、AFS 隐、fallback 横幅显

---

#### TC-BRP-3PA-052: Google AFS 广告平台标识验证
**优先级**: P2  
**UI自动化**: ✅ 可自动化  
**前置条件**: 
- TC-BRP-3PA-048 通过

**测试步骤**:
1. 访问 BRP 页面
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

1. **01_gumtree_brp_full.png**
   - 完整 BRP 页面截图（全页面滚动截图）
   - 包含：顶部导航、筛选侧边栏、广告位、列表项、页脚

2. **02_gumtree_brp_viewport.png**
   - 视口截图
   - 清晰显示顶部横幅广告位的灰色占位区域
   - 包含 Cookie 隐私弹窗和筛选侧边栏

3. **03_brp_bing_top_ad.png** ⭐ **（历史截图，已过时）**
   - 曾用于记录 **Bing 顶部搜索广告**；**2026-05-11 起 Bing 已从 BRP 移除**，该截图不再代表当前线上布局
   - 当前同比区域请采集 **`afscontainer1-fallback`** 自有推广横幅（示例文案："One place for all your Ads — Post an Ad for nearly anything"）

---

## 📝 测试总结

### 已验证功能（实测 ✅）

1. **Bing 搜索广告（已下线 / 历史）**：
   - 🚫 **Bing 顶部/底部及全部 `bing-*` DOM 已移除**（2026-05-11）
   - ✅ **替代**：`afscontainer1-fallback` 自有推广横幅可见（约 736×200px，`display: block`），文案含 "One place for all your Ads"
   - 🚫 原 Bing fallback / 双槽统计等结论 **不再适用**

2. **标准广告位容器**：
   - ✅ 所有 9 个标准广告位容器均存在于 DOM 中
   - ✅ 顶部横幅广告位位置正确，高度预留 90px（当前未投放）
   - ✅ 广告脚本集成：middle1 包含第三方广告脚本标签

3. **Google AFS 文本广告**：
   - ✅ afscontainer1 容器存在但隐藏（display: none）
   - ✅ 包含 Google AFS iframe 结构（master-a-1, master-1）
   - ✅ 使用独立的 text-ads-slot 容器类
   - ✅ ~~与 Bing 广告互斥~~ → **Bing 已下线**；当前为 AFS 隐、**`afscontainer1-fallback` 推广横幅显**

4. **布局和数据属性**：
   - ✅ 右侧广告位布局：4 个右侧广告位完美垂直对齐，宽度 300px
   - ✅ 中间广告位布局：2 个中间广告位水平对齐，宽度 728px
   - ✅ 数据属性标记：所有标准广告位包含 `data-display-ad="true"` 属性
   - ✅ ID 唯一性：所有广告位 ID 唯一，无冲突

5. **其他**：
   - ✅ 控制台错误：存在广告相关错误，但不影响主功能

### 待验证功能（推断 ⚠️）
1. **标准广告位投放状态**：当前大部分标准广告位未投放（高度为 0），需在广告投放时段测试
2. **广告位实际尺寸**：需要在标准广告位投放后验证实际高度
3. **移动端响应式布局**：需要调整视口或使用真实设备测试
4. **广告拦截器场景**：
   - ⚠️ 需要安装插件并测试
   - ⚠️ 广告拦截器对 **`afscontainer1-fallback` / AFS iframe** 的影响（Bing 已不存在）
5. **页面加载性能**：需要使用 Lighthouse 等工具测量
6. **~~Bing 广告动态性~~（已下线）**：
   - 不再适用
7. **Google AFS 激活场景**：
   - ⚠️ Google AFS 何时激活（条件仍不明确）
   - ⚠️ ~~AFS 与 Bing 的切换逻辑~~ → **Bing 已移除**；关注 AFS 与自有推广/A-B 测试关系
   - ⚠️ AFS 激活后的展示效果

### 风险识别
1. **~~Bing 广告依赖性~~ → 已移除**：原 Bing 收入位已下线；需关注 **`afscontainer1-fallback` 与 AFS** 对体验与收入的影响
2. **Google AFS 激活条件不明确**：AFS 容器存在但隐藏，激活逻辑未知
3. **标准广告位投放不稳定**：BRP 页面标准广告可能因时段、地域、预算等原因不投放
4. **第三方依赖**：使用 srvb1.com 等第三方广告平台，可能因网络或服务故障失败
5. **浏览器兼容性**：不同浏览器的广告展示可能有差异
6. **性能影响**：9 个标准广告位 + **自有推广横幅** + 1 个 AFS 容器可能影响页面加载速度
7. **用户体验**：过多广告可能影响列表浏览体验
8. **~~Bing 广告 ID 重复~~**：已不适用（无 Bing DOM）
9. **文本广告与推广位**：仅余 **Google AFS（隐）** 与 **`afscontainer1-fallback`（显）**，需厘清后续产品策略与监控指标

### 广告位配置总结

#### 按别名分类
```yaml
top (tBanner):
  位置: 顶部中央
  尺寸: 728x90 (Leaderboard)
  状态: 预留未投放

topRight (rSkyT):
  位置: 右侧顶部
  尺寸: 300x?
  状态: 预留未投放

topRight2 (rSkyT2):
  位置: 右侧顶部2（rSkyT下方24px）
  尺寸: 300x?
  状态: 预留未投放

middle1 (integratedMpu):
  位置: 列表中间 (y=3021.5px)
  尺寸: 728x?
  状态: 包含广告脚本

middle2 (integratedListing):
  位置: 列表下半部 (y=5073.5px)
  尺寸: 728x?
  状态: 预留未投放

bottomRight (rSkyB):
  位置: 右侧底部
  尺寸: 300x?
  状态: 预留未投放

bottomRight2 (rSkyB2):
  位置: 右侧底部2（rSkyB下方24px）
  尺寸: 300x?
  状态: 预留未投放

bing-top (bing-top-slot-wrapper):
  状态: **已下线**（2026-05-11，DOM 不再存在）

bing-bottom (bing-bottom-slot-wrapper):
  状态: **已下线**（2026-05-11，DOM 不再存在）

afscontainer1-fallback:
  位置: 原 Bing 顶部位业务区域 / 主列列表上方
  尺寸: 约 736x200px（实测）
  类型: Gumtree 自有推广横幅
  状态: 可见（display: block）

afscontainer1 (Google AFS):
  位置: 隐藏（待激活）
  类型: Google AdSense for Search 文本广告
  状态: 隐藏（display: none）；**不再表述为「Bing 备用」**（Bing 已移除）
  平台: syndicatedsearch.goog
```

### 自动化建议
1. **可自动化场景**：
   - ~~Bing 广告容器~~ → **断言无 `bing-*` 节点**（TC-BRP-3PA-039）
   - **`afscontainer1-fallback` 存在、可见、文案与 CTA 链接**（TC-BRP-3PA-040/041）
   - Google AFS 容器存在性检查（TC-BRP-3PA-048）
   - Google AFS iframe 结构验证（TC-BRP-3PA-049）
   - **Google AFS 与页面文本位状态**（TC-BRP-3PA-051，无 Bing）
   - 标准广告位容器存在性检查（所有 TC-BRP-3PA-001/004/007等）
   - 广告位位置和尺寸验证（TC-BRP-3PA-002/005/008等）
   - 数据属性验证（TC-BRP-3PA-021/022）
   - 布局关系验证（TC-BRP-3PA-023/024）
   - 响应式布局验证（TC-BRP-3PA-027/028）

2. **难以自动化场景**：
   - ~~Bing 广告内容审核~~ → 自有推广横幅合规与本地化可人工抽检
   - Google AFS 激活条件触发（激活逻辑不明确，难以自动化测试）
   - 广告内容审核（需人工判断合规性）
   - 广告点击行为（可能触发计费）
   - 广告投放策略（依赖外部系统）
   - 广告内容质量评估
   - ~~Bing 广告内容动态变化~~ → 不适用

3. **推荐测试策略**：
   - **监控「无 Bing + fallback 横幅稳定展示」**
   - 定期检查标准广告位容器完整性（冒烟测试）
   - ~~验证 Bing 广告位置优先级~~ → 验证 **`afscontainer1-fallback`** 相对列表位置
   - 使用 mock 广告服务器或测试广告账号
   - 监控控制台错误，但不作为失败条件
   - 在多种视口尺寸下测试响应式布局
   - 验证广告位不影响核心功能（列表展示、筛选、排序）
   - ~~监控 Bing fallback~~ → 关注 **fallback 横幅与 AFS** 切换/并存策略变更

---

## 🔗 相关文档

- [IAB 标准广告尺寸](https://www.iab.com/newadportfolio/)
- [Gumtree 广告政策](https://www.gumtree.com/info/life/advertise-with-us/)
- [Bing Ads 文档](https://about.ads.microsoft.com/)（历史参考：BRP 曾集成 Bing 搜索广告文本位，已于 2026-05-11 移除）
- [Google AdSense for Search 文档](https://support.google.com/adsense/answer/17960)
- [Playwright 测试文档](https://playwright.dev/python/)

---

**编写人**: Web QA Brain (AI)  
**最后更新**: 2026-05-11  
**版本历史**:
- v1.5 (2026-05-11): Bing 搜索广告已下线，更新模块 15 所有 Bing 相关用例预期结果，新增 afscontainer1-fallback 自有推广横幅验证
- v1.4 (2026-03-25): **新增模块 16：Google AFS 文本广告验证**，包含 5 个用例（TC-BRP-3PA-048~052），验证 Google AdSense for Search 容器、iframe 结构、激活条件；（当时曾推断）与 Bing 文本广告互斥——**Bing 已于 v1.5 下线，该互斥关系不再适用**
- v1.3 (2026-03-25): **新增模块 15：Bing 搜索广告验证**，包含 9 个用例（TC-BRP-3PA-039~047），验证 Bing 顶部/底部广告位、内容、位置、fallback、交互性、统计
- v1.2 (2026-03-25): **新增模块 14：广告位真实加载验证**，包含 8 个用例（TC-BRP-3PA-031~038），验证广告位是否真实加载广告内容（iframe/script/尺寸/懒加载/统计）
- v1.1 (2026-03-25): 新增多环境支持配置，添加环境切换示例代码
- v1.0 (2026-03-25): 初始版本，基于 BRP 页面探测生成