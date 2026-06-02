"""Product-facing copy for PRD gate issues (used by render_prd_gate_notice)."""

from __future__ import annotations

import os
import re

# Strip internal QA refs from fallback text
_INTERNAL_REF = re.compile(
    r"\b(?:SC|O|ASM|GATE|RT)-[0-9]{2,3}\b|"
    r"overlap[<>=][0-9.]+|"
    r"fail-safe|precheck|figma-snapshot|delivery_coverage\.\S+|"
    r"workspace/inputs/\S+"
)


def _clean(text: str) -> str:
    t = _INTERNAL_REF.sub("", text or "")
    t = re.sub(r"\s{2,}", " ", t)
    t = re.sub(r"[；;]\s*[；;]+", "；", t)
    return t.strip(" ；;")


def _bullets_from_suggestion(suggestion: str) -> str:
    s = _clean(suggestion)
    if not s:
        return "（待产品补充具体改法）"
    parts = re.split(r"[；;。]\s*", s)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) <= 1:
        return s
    return "\n".join(f"- {p}" for p in parts)


# Fallback when gatekeeper did not write product_copy (keyed by GATE id)
_FALLBACK_BY_ID: dict[str, dict[str, str]] = {
    "GATE-001": {
        "title": "设计稿链接不可用",
        "problem": (
            "当前提供的 Figma 链接是占位地址，打不开真实设计稿。"
            "Requirement 3 规定了价格后缀的字体、间距、大小写，但没有稿面就无法核对 Feed 卡片上 pm/pw 的实际样式。"
        ),
        "action": (
            "- 提供可打开的 Figma 链接（最好带 node-id，定位到首页 Feed 卡片）\n"
            "- 稿面需覆盖：租赁价（带 pm/pw）、出售价（无后缀）、A/B 实验两种样式\n"
            "- 更新链接后通知 QA 重新跑 prd-analyze"
        ),
    },
    "GATE-002": {
        "title": "租赁频率缺失时，价格怎么显示？",
        "problem": (
            "PRD 只写了：**如果** listing 有租赁频率（月租/周租），Feed 就在价格后加 pm 或 pw。\n\n"
            "但没有写：如果频率字段**缺失、为空、或后端漏传**，用户会看到什么？\n"
            "- 只显示 `£1,800`？\n"
            "- 还是前端随便猜一个 pm/pw？\n\n"
            "开发不知道该怎么实现，测试也不知道怎样才算验收通过。"
        ),
        "action": (
            "- 在 Requirement 1 和 Feed API 章节写清楚：频率为空时 API 的 type 默认值是什么\n"
            "- 说明 BFF/客户端的兜底展示规则（显示纯金额 / 隐藏 / 与 PDP 对齐等）\n"
            "- 是否需要监控或告警\n"
            "- 给一条可 Mock 的 JSON 示例"
        ),
    },
    "GATE-003": {
        "title": "月租/周租两套字段对不上，听谁的？",
        "problem": (
            "PRD 里有两套说法：\n"
            "- 产品侧：Monthly（月租）/ Weekly（周租）\n"
            "- 接口侧：`PER_MONTH` / `PER_WEEK`\n\n"
            "但没有写它们如何一一对应；也没有写**数据冲突**怎么办——"
            "例如业务标记为周租，接口却返回月租类型，界面该显示 pw 还是 pm？"
            "缺少规则时，最容易出现**静默显示错误**（用户看到的后缀是错的，但没人发现）。"
        ),
        "action": (
            "- 补充映射表：Monthly ↔ PER_MONTH，Weekly ↔ PER_WEEK\n"
            "- 定义冲突时的优先级（以哪个字段为准）\n"
            "- 冲突时是回退为无后缀、还是报错/打点\n"
            "- 给一个反例（错误数据组合）及期望 UI"
        ),
    },
    "GATE-004": {
        "title": "Feed 接口文档不够细，开发和测试绑不住",
        "problem": (
            "PRD 描述了「首页 Feed 会返回 price 对象」，也给了 JSON 截图，但缺少：\n"
            "- 具体是哪个 HTTP 接口\n"
            "- 完整 JSON 结构（字段路径是否 `advert.price.type`）\n"
            "- 异常/未知 type 时的响应\n\n"
            "开发和自动化测试无法绑定到唯一、可 Mock 的接口定义。"
        ),
        "action": (
            "- 补充 OpenAPI 或完整示例 JSON\n"
            "- 明确 `advert.price.amount`、`advert.price.type` 字段路径\n"
            "- 给出五类 type（SPECIFIED_AMOUNT、FREE、PER_MONTH、PER_WEEK、FREE_QUOTA）各一条样例\n"
            "- 说明遇到未知 type 时的回退逻辑"
        ),
    },
    "GATE-005": {
        "title": "A/B 实验文案和功能规则前后不一致",
        "problem": (
            "同一份 PRD 里写了两种格式：\n"
            "- **Requirement 3**（V1.1）：`£1,200pm` —— 价格和 pm/pw **之间无空格**\n"
            "- **A/B Testing Plan**：`£X pm / £X pw` —— **有空格**\n\n"
            "验收时无法同时满足两条规则。应以哪一条为准，PRD 没有定稿。"
        ),
        "action": (
            "- 统一 A/B 实验组文案为无空格：`£Xpm` / `£Xpw`（与 Requirement 3 一致）\n"
            "- 或者修订 Requirement 3，明确实验组是否允许空格，并更新正反示例"
        ),
    },
    "GATE-006": {
        "title": "API 默认 type 和租赁 type 两条规则互相打架",
        "problem": (
            "PRD 同时存在两条规则，对**同一条租赁 listing** 可能都适用：\n"
            "1. 通用规则：`amount > 0` 时 type = `SPECIFIED_AMOUNT`（只显示金额，不带 pm/pw）\n"
            "2. 租赁规则：租赁 listing 要用 `PER_MONTH` 或 `PER_WEEK`（要带 pm/pw）\n\n"
            "一条 £1,800 的月租房，API 到底该返回哪种 type？BFF 按哪条规则渲染？契约层面目前说不通。"
        ),
        "action": (
            "- 修订默认规则：**出售** → `SPECIFIED_AMOUNT`；**租赁且 amount>0** → 必须 `PER_MONTH` / `PER_WEEK`\n"
            "- 说明迁移期老数据如何兼容"
        ),
    },
    "GATE-007": {
        "title": "「Feed 与 PDP 100% 一致」和 A/B 对照组互相矛盾",
        "problem": (
            "PRD 目标要求：Feed 和 PDP 的租期单位 **100% 一致**。\n\n"
            "但 A/B 实验设计是：\n"
            "- **对照组**：Feed 仍是老的 `£X`（无 pm/pw 后缀）\n"
            "- **PDP**：已经有 `£1,800pm` 等后缀\n\n"
            "对照组用户永远会看到 Feed 无后缀、PDP 有后缀——实验期间**不可能**满足 100% 一致性。"
            "两个目标无法同时作为验收标准。"
        ),
        "action": (
            "- 明确实验期是否**暂时不考核** Feed/PDP 一致性\n"
            "- 或调整实验设计（例如对照组 PDP 也同步隐藏后缀）\n"
            "- 定稿分流比例、开关字段、成功指标的计算方式"
        ),
    },
    "GATE-008": {
        "title": "出售房如果接口误返回租期类型，界面怎么办？",
        "problem": (
            "PRD 写清楚了：**出售房**不追加 pm/pw 后缀（Requirement 2）。\n\n"
            "但没有写：如果后端**搞错了**，给一条出售房返回了 `PER_WEEK` 或 `PER_MONTH`，"
            "前端要不要显示 pw/pm？\n"
            "- 若「看到租期 type 就加后缀」→ 出售房可能错误显示成 `£250,000pw`\n"
            "- 若「出售房一律忽略租期 type」→ 更安全"
        ),
        "action": (
            "- 明确规定：for-sale listing **忽略**租期 type，或 API **强制**返回 `SPECIFIED_AMOUNT`\n"
            "- 增加负向验收说明：出售房 + 误返 PER_WEEK → 界面仍**无** pw 后缀"
        ),
    },
    "GATE-009": {
        "title": "月租/周租但金额是 0，界面显示什么？",
        "problem": (
            "PRD 分别写了：\n"
            "- `amount = 0` → type 为 `FREE`，显示 free\n"
            "- `PER_MONTH` → 显示 xxxpm\n"
            "- `FREE_QUOTA` → 显示 free quota\n\n"
            "但没有写这种**组合**：type = `PER_MONTH` 或 `PER_WEEK`，同时 amount = **0**——"
            "是显示 `0pm`、`free`，还是别的？实现时各端可能各猜各的。"
        ),
        "action": (
            "- 补充 PER_MONTH / PER_WEEK 与 amount（0 / >0）的组合矩阵\n"
            "- 每种组合写明期望 UI\n"
            "- 非法组合是禁止下发，还是统一映射为 free"
        ),
    },
}


def get_product_copy(issue: dict) -> dict[str, str]:
    """Return {title, problem, action} for product-facing notice."""
    pc = issue.get("product_copy") or {}
    if pc.get("title") and pc.get("problem") and pc.get("action"):
        return {
            "title": pc["title"].strip(),
            "problem": pc["problem"].strip(),
            "action": pc["action"].strip(),
        }

    issue_id = issue.get("id", "")
    if os.environ.get("QA_AGENT_USE_LEGACY_PRODUCT_COPY") == "1" and issue_id in _FALLBACK_BY_ID:
        return dict(_FALLBACK_BY_ID[issue_id])

    # Generic fallback: strip jargon, format suggestion as bullets
    title = _clean(issue.get("description", ""))[:48]
    if len(title) >= 48:
        title += "…"
    return {
        "title": title or "待补充标题",
        "problem": _clean(issue.get("description", "")) or "（无说明）",
        "action": _bullets_from_suggestion(issue.get("suggestion", "")),
    }


def product_summary(issues: list[dict]) -> str:
    """One-paragraph intro for product readers."""
    blockers = [i for i in issues if i.get("severity") == "blocker"]
    majors = [i for i in issues if i.get("severity") == "major"]
    themes: list[str] = []
    ids = {i.get("id") for i in issues}
    if any(x in ids for x in ("GATE-005", "GATE-006", "GATE-007")):
        themes.append("PRD 内部有多处规则前后矛盾（如 A/B 文案、API 默认 type、Feed/PDP 一致性）")
    if any(x in ids for x in ("GATE-002", "GATE-003", "GATE-008", "GATE-009")):
        themes.append("租赁价格的边界场景和字段映射尚未写全")
    if "GATE-001" in ids:
        themes.append("Figma 设计稿尚不可用")
    if "GATE-004" in ids:
        themes.append("Feed 接口文档不够细")
    theme_text = "；".join(themes) if themes else "PRD 或设计稿尚有未闭合项"
    parts = [f"共 **{len(issues)}** 项待处理"]
    if blockers:
        parts.append(f"，其中 **{len(blockers)}** 项为必须修订的规则冲突或缺失")
    if majors:
        parts.append(f"，**{len(majors)}** 项为设计稿与接口细节补充")
    return f"{theme_text}。{''.join(parts)}。请按下方清单逐条修订后重新提测。"
