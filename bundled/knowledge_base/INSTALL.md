# Gumtree UI Agent 知识库 - 快速开始指南

## 项目简介

本项目是 Gumtree UI 自动化测试 Agent 的知识库,用于存储和管理业务规则、业务流程、业务全景等结构化知识内容,帮助 AI Agent 更好地理解业务逻辑并生成高质量的测试用例。

## 前置要求

- **Node.js**: 版本 20.6 或更高
- **Git**: 用于克隆项目
- **网络**: 需要能访问 GitHub 和 npm

## 快速开始

### 第一步: 从 GitHub 克隆项目

```bash
# 克隆项目到本地
git clone git@github.com:gumtree-tech/gumtree-ui-agent-kb.git

# 进入项目目录
cd gumtree-ui-agent-kb
```

### 第二步: 验证项目结构

```bash
# 查看目录结构
ls -la

# 应该看到以下目录:
# .claude/         - Claude 技能目录
# 业务规则库/      - 存储详细业务规则
# 业务知识图谱/    - 存储业务流程和全景
# 产品全景/        - 存储产品架构和设计
# AGENTS.md        - Agent 技能配置文件
# README.md        - 项目说明
```

### 第三步: 安装 openskills (如果尚未安装)

openskills 是一个通用的 skills 管理工具,用于加载和管理 AI Agent 的技能。

```bash
# 验证 Node.js 版本 (需要 20.6+)
node --version

# 同步已有的 skills 到 AGENTS.md
npx openskills sync -y

# 查看已安装的 skills
npx openskills list
```

**预期输出**:
```
Available Skills:

  knowledge-base-manager    (project)
    This skill transforms scattered test cases and requirements into a 
    structured, AI-ready knowledge base with business process flows, 
    rules, and observation points.

Summary: 1 project, 0 global (1 total)
```

### 第四步: 验证 knowledge-base-manager skill

```bash
# 查看 skill 目录
ls -la .claude/skills/knowledge-base-manager/

# 应该看到:
# SKILL.md           - 技能主文档
# references/        - 参考文档目录
#   ├── architecture-patterns.md     - 架构模式说明
#   ├── content-classification.md    - 内容分类指南
#   ├── document-templates.md        - 文档模板
#   └── quality-standards.md         - 质量标准
```

## 使用 knowledge-base-manager skill

### 场景 1: 归档测试用例到知识库

假设你有一个测试用例文档 `TC_example.md`,想要将它归档到知识库:

**步骤 1: 在 Cursor 中打开测试用例文档**
- 使用 `@` 符号引用文件: `@TC_example.md`

**步骤 2: 向 AI Agent 发送归档请求**
```
在 @gumtree-ui-agent-kb 项目中使用 knowledge-base-manager skill 
总结 @TC_example.md 到知识库
```

**步骤 3: AI Agent 自动执行流程**
1. ✅ 扫描知识库架构(识别为三层架构)
2. ✅ 深度阅读测试用例文档
3. ✅ 提取业务规则和业务流程
4. ✅ 识别模块归属(如: 支付模块、商业表现看板模块等)
5. ✅ 语义去重检测(检查是否有重复内容)
6. ✅ 生成预览(显示将要创建/更新的文档)
7. ⏸️ 等待用户确认
8. ✅ 执行写入操作
9. ✅ 质量验证

**步骤 4: 审查生成的文档**

Agent 会生成以下文档:
- `业务规则库/<模块名>/<功能名>规则.md` - 详细业务规则(6章节结构)
- `业务知识图谱/<模块名>业务域/<流程名>业务流程.md` - 详细业务流程(5章节结构)
- `业务知识图谱/<模块名>业务域/<模块名>业务全景.md` - 业务全景(11章节结构)

### 场景 2: 更新已有的业务规则

当业务规则有变更时:

```
使用 knowledge-base-manager skill 更新:
登录验证码有效期从60秒改为90秒
```

Agent 会:
1. 识别变更范围(用户模块 - 登录规则)
2. 识别影响的文档(规则库、业务全景、业务流程)
3. 生成变更预览
4. 同步更新所有相关文档
5. 验证一致性

### 场景 3: 批量归档多个文档

```
使用 knowledge-base-manager skill 归档以下测试用例:
@TC_payment.md
@TC_search.md
@TC_listing.md
```

Agent 会:
1. 逐个分析每个文档
2. 汇总所有变更到单一预览
3. 统一去重检测
4. 批量写入

## knowledge-base-manager skill 核心能力

### 📋 自动提取业务规则
从测试用例中识别:
- 输入规则(字段、类型、必填、长度、格式)
- 校验规则(格式校验、业务校验)
- 权限规则(角色、权限控制)
- 业务约束(频控、限制、依赖)
- 错误处理(错误码、错误信息、触发条件)

### 🗺️ 生成业务知识图谱
自动构建:
- 完整的业务流程(主流程、异常流程)
- 页面拓扑关系(页面入口矩阵、跳转流程图)
- Mermaid 流程图(业务流程图、状态流转图)
- 详细观测点(✅正向、❌负向、⚠️待确认)

### 🔍 智能语义去重
- 利用 AI 语义理解识别重复内容
- 避免简单文本匹配的误判
- 识别规则冲突并标记

### 🔄 同步更新维护
- 内容变更时自动同步更新规则库和知识图谱
- 保持跨文档一致性
- 自动维护双向链接

### ✅ 质量自动验证
- 检查模板完整性
- 验证链接有效性
- 检查 Mermaid 语法正确性
- 验证数据一致性

## 知识库目录结构说明

```
gumtree-ui-agent-kb/
├── .claude/
│   └── skills/
│       └── knowledge-base-manager/    # 知识库管理技能
│           ├── SKILL.md               # 技能主文档
│           └── references/            # 参考文档
│               ├── architecture-patterns.md
│               ├── content-classification.md
│               ├── document-templates.md
│               └── quality-standards.md
├── 业务规则库/                         # 第一层: 详细业务规则
│   ├── 支付模块/
│   ├── 商业表现看板模块/
│   └── ...
├── 业务知识图谱/                       # 第二层: 业务流程和全景
│   ├── 支付业务域/
│   ├── 商业表现看板业务域/
│   └── ...
├── 产品全景/                           # 第三层: 产品架构和设计
│   ├── 产品架构图.md
│   ├── 技术架构.md
│   └── 业务流程图/
├── AGENTS.md                           # Agent 技能配置
└── README.md                           # 项目说明
```

### 三层架构说明

1. **业务规则库** - 详细规则层
   - 按功能模块组织(如: 支付模块、商业表现看板模块)
   - 存储详细的业务规则、输入规则、校验规则、权限规则等
   - 文档结构: 6章节(功能概述、核心流程、业务规则、错误处理、已知问题、变更历史)

2. **业务知识图谱** - 流程层
   - 按业务域组织(如: 支付业务域、商业表现看板业务域)
   - 存储业务流程、业务全景、Mermaid 流程图、观测点
   - 业务全景文档: 11章节(业务定位、范围、流程全景图、核心流程概览、页面拓扑、数据流转、规则索引、FAQ、指标、已知问题、变更历史)
   - 业务流程文档: 5章节(完整流程图、详细步骤与观测点、流程验证清单、关联文档、变更历史)

3. **产品全景** - 设计层
   - 存储产品架构、技术架构、功能模块清单等顶层设计文档

## 常用命令

### openskills 命令

```bash
# 查看已安装的 skills
npx openskills list

# 读取 skill 内容 (AI Agent 使用)
npx openskills read knowledge-base-manager

# 同步 skills 到 AGENTS.md
npx openskills sync

# 从 Anthropic marketplace 安装更多 skills
npx openskills install anthropics/skills

# 从本地路径安装 skill
npx openskills install ./local-skills/my-skill

# 从 GitHub 仓库安装 skill
npx openskills install your-org/your-skills

# 更新已安装的 skills
npx openskills update

# 删除 skill
npx openskills remove <skill-name>
```

### Git 命令

```bash
# 查看当前分支和状态
git status

# 拉取最新代码
git pull origin main

# 创建新分支
git checkout -b feature/add-new-module

# 提交变更
git add .
git commit -m "docs: add new business rules for XX module"
git push origin feature/add-new-module
```

## 实际案例: 商业表现看板模块

本知识库已包含一个完整的示例 - **商业表现看板模块**,该模块基于 `TC_performance_metrics_phase2.md` (62条测试用例)提取而来。

### 已生成的文档

1. **业务规则库/商业表现看板模块/商业表现看板规则.md** (202行)
   - 10个业务规则组: 权限、时间筛选、核心指标计算、地理位置、表格、导出、空状态、Tooltip、数据一致性、埋点
   - 5种错误处理场景
   - 8个 PRD 差距问题

2. **业务知识图谱/商业表现看板业务域/商业表现看板访问与浏览业务流程.md** (388行)
   - Mermaid 完整流程图
   - 11个详细步骤(含页面位置、操作、观测点、验证方法、关联规则)
   - 25个流程验证点

3. **业务知识图谱/商业表现看板业务域/商业表现看板业务全景.md** (374行)
   - 业务定位和价值
   - 5个核心业务流程概览
   - 页面拓扑关系(入口矩阵、跳转流程图、关系详解)
   - 业务数据流转(状态流转图、用户操作表格、关键数据表格)
   - 10个业务 FAQ

### 查看示例文档

```bash
# 查看业务规则
cat 业务规则库/商业表现看板模块/商业表现看板规则.md

# 查看业务流程
cat 业务知识图谱/商业表现看板业务域/商业表现看板访问与浏览业务流程.md

# 查看业务全景
cat 业务知识图谱/商业表现看板业务域/商业表现看板业务全景.md
```

## AI Agent 使用流程

### 在 Cursor 中使用知识库

1. **打开 Cursor IDE**
2. **打开项目**: File → Open → 选择 `gumtree-ui-agent-kb` 目录
3. **打开测试用例文档**: 在 Cursor 中打开需要归档的测试用例文件
4. **向 AI Agent 发送指令**:

```
在 @gumtree-ui-agent-kb 项目中使用 knowledge-base-manager skill 
总结 @TC_your_test_case.md 到知识库
```

5. **AI Agent 自动执行**:
   - 扫描知识库架构
   - 深度阅读测试用例
   - 提取业务规则和流程
   - 语义去重检测
   - 生成预览
   - 等待确认
   - 执行写入
   - 质量验证

6. **审查生成的文档**: 检查生成的业务规则、业务流程、业务全景文档

### 典型工作流程示例

#### 示例 1: 归档新的测试用例

**场景**: 你有一个新的支付功能测试用例 `TC_new_payment_flow.md`

**操作**:
```
使用 knowledge-base-manager skill 归档 @TC_new_payment_flow.md
```

**Agent 执行**:
1. 识别为支付模块
2. 提取支付规则、支付流程
3. 检查是否与现有的"3DS认证支付规则.md"重复
4. 生成新文档或更新现有文档
5. 同步更新业务知识图谱

#### 示例 2: 更新业务规则

**场景**: 支付超时时间从 30 秒改为 60 秒

**操作**:
```
使用 knowledge-base-manager skill 更新知识库:
支付超时时间从 30 秒改为 60 秒
```

**Agent 执行**:
1. 识别变更范围: 支付模块
2. 定位影响文档:
   - 业务规则库/支付模块/xxx规则.md
   - 业务知识图谱/支付业务域/xxx业务流程.md
   - 业务知识图谱/支付业务域/支付业务全景.md
3. 生成变更预览
4. 同步更新所有文档的相关章节
5. 更新变更历史

#### 示例 3: 查询知识库内容

**场景**: 想了解某个业务规则

**操作**:
```
查看商业表现看板的时间筛选规则
```

**Agent 执行**:
1. 读取 `业务规则库/商业表现看板模块/商业表现看板规则.md`
2. 定位到"3.2 时间筛选规则"章节
3. 展示规则内容

## 文档模板说明

### 业务规则文档模板 (6章节)

```markdown
# [模块名] - [功能名]业务规则

## 1. 功能概述
- 功能描述、用户角色、入口位置、依赖模块

## 2. 核心流程
- 主流程、异常流程

## 3. 业务规则
- 输入规则、校验规则、权限规则、业务约束

## 4. 错误处理
- 错误码、错误信息、触发条件、用户提示

## 5. 已知问题
- 问题描述 + Jira 链接

## 6. 变更历史
- 日期、版本、变更内容、变更人
```

### 业务流程文档模板 (5章节)

```markdown
# [流程名]业务流程

> **业务目标**: 一句话描述

## 1. 完整流程图
- Mermaid 流程图(含判断分支、异常处理)

## 2. 详细步骤与观测点
- 每个步骤含: 页面位置、操作、观测点、验证方法、关联规则

## 3. 流程完整性验证清单
- Checkbox 列表(10-25个验证点)

## 4. 关联文档
- 链接到业务全景和业务规则

## 5. 变更历史
```

### 业务全景文档模板 (11章节)

```markdown
# [模块名]业务域 - 业务全景

## 1. 业务定位
## 2. 业务范围
## 3. 业务流程全景图
## 4. 核心业务流程概览
## 5. 页面拓扑关系
## 6. 业务数据流转
## 7. 关键业务规则索引
## 8. 业务FAQ
## 9. 业务指标(可选)
## 10. 已知问题与风险
## 11. 变更历史
```

## 最佳实践

### ✅ 归档前
- 先扫描架构,确保知识库目录结构正确
- 完整阅读输入文档,不跳过任何细节
- 识别模块归属,确保内容归档到正确的目录

### ✅ 归档时
- 默认同时生成业务规则文档和业务知识图谱
- 使用 AI 语义理解判断重复,而非简单文本匹配
- 生成预览后等待确认再写入
- 严格遵循文档模板,不遗漏章节

### ✅ 归档后
- 质量验证(模板完整性、链接有效性、Mermaid 语法)
- 同步更新规则库和知识图谱
- 维护双向链接

### ❌ 常见错误
- 只更新业务规则库,忘记更新业务知识图谱
- 不遵循模板结构,遗漏章节
- Mermaid 语法错误
- 链接路径错误
- 在业务规则库下创建不必要的中间层目录

## 技术支持

### 问题排查

**问题 1: openskills 命令找不到**
```bash
# 解决: 使用 npx 运行
npx openskills list
```

**问题 2: skill 加载失败**
```bash
# 检查 AGENTS.md 是否正确配置
cat AGENTS.md

# 重新同步
npx openskills sync -y
```

**问题 3: 文档生成不符合预期**
- 检查输入文档是否完整
- 验证知识库目录结构是否正确
- 查看参考模板: `.claude/skills/knowledge-base-manager/references/document-templates.md`

### 获取帮助

- **查看 skill 文档**: `npx openskills read knowledge-base-manager`
- **查看参考文档**: 阅读 `.claude/skills/knowledge-base-manager/references/` 目录下的文档
- **查看示例**: 参考已生成的商业表现看板模块和支付模块文档

## 贡献指南

### 提交代码

1. 创建新分支: `git checkout -b feature/add-new-module`
2. 添加或更新知识库文档
3. 提交变更: `git commit -m "docs: add XX module business rules"`
4. 推送分支: `git push origin feature/add-new-module`
5. 在 GitHub 上创建 Pull Request

### 文档规范

- 所有文档使用 Markdown 格式
- 严格遵循文档模板结构
- Mermaid 流程图必须语法正确
- 链接使用相对路径
- 变更历史必须记录

## 附录

### 相关资源

- **openskills 项目**: https://github.com/numman-ali/openskills
- **Anthropic Skills 文档**: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- **Mermaid 语法**: https://mermaid.js.org/

### 当前知识库统计

- **总模块数**: 2个(支付模块、商业表现看板模块)
- **业务规则文档**: 2个
- **业务流程文档**: 2个
- **业务全景文档**: 1个
- **总行数**: ~1,600行

---

**最后更新**: 2026-03-25
**维护者**: Gumtree QA Team
