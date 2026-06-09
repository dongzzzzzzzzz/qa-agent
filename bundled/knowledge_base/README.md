# Gumtree UI Agent 知识库

用于 UI 自动化测试 Agent 场景的知识库项目,提供结构化的业务规则、业务流程和业务全景文档,帮助 AI Agent 更好地理解业务逻辑。

## 快速开始

```bash
# 1. 克隆项目
git clone git@github.com:gumtree-tech/gumtree-ui-agent-kb.git
cd gumtree-ui-agent-kb

# 2. 验证 Node.js (需要 20.6+)
node --version

# 3. 同步 skills
npx openskills sync -y

# 4. 查看已安装的 skills
npx openskills list
```

详细安装和使用说明请查看 [INSTALL.md](./INSTALL.md)

## 目录结构

### 📋 产品全景

- **产品架构图.md** - 系统整体架构图
- **技术架构.md** - 技术栈和架构设计
- **核心业务流程总览.md** - 核心业务流程概述
- **功能模块清单.md** - 所有功能模块列表
- **用户角色与权限体系.md** - 用户角色定义
- **业务流程图/** - 各业务流程图文件

### 🗺️ 业务知识图谱

按业务域组织的详细业务知识:

- **支付业务域/** - 支付相关业务流程和全景
- **商业表现看板业务域/** - 商业表现看板相关业务流程和全景
- **认证业务域/** - 认证相关业务流程和全景（GBG 身份验证、Google Review）

### 📚 业务规则库

按模块组织的具体业务规则:

- **支付模块/** - 支付相关规则
- **商业表现看板模块/** - 商业表现看板相关规则
- **认证模块/** - 认证相关规则（GBG 身份验证、Google Review）

## 安装 Skills（如果未找到）

[https://github.com/numman-ali/openskills](https://github.com/numman-ali/openskills)

[https://igit.58corp.com/intl_qa/knowledge_base](https://igit.58corp.com/intl_qa/knowledge_base)



### knowledge-base-manager

将非结构化的测试用例和需求文档转化为结构化知识库,自动提取业务规则、生成业务流程、构建 Mermaid 流程图。

**使用方法**:

```bash
# 在 Cursor 中向 AI Agent 发送指令
使用 knowledge-base-manager skill 归档 @your_test_case.md
```

详细使用说明请查看 [INSTALL.md](./INSTALL.md)

---

**维护者**: Gumtree QA Team  
**最后更新**: 2026-04-15