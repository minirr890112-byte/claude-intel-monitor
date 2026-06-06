"""Model switching recommendations when Claude degradation is detected.

当 claude-intel-monitor 检测到降智后，根据降智程度自动推荐替代模型。
基于 V2EX/CSDN 社区验证的替代方案排名。
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelAlternative:
    """Alternative model recommendation."""
    name: str
    provider: str
    model_id: str
    rating: float               # 0.0-10.0 community rating
    cost_per_1m_tokens: float   # USD per 1M tokens (input + output avg)
    pros: list = field(default_factory=list)
    cons: list = field(default_factory=list)
    setup_env: dict = field(default_factory=dict)  # {ENV_VAR: value}
    best_for: list = field(default_factory=list)   # use cases
    community_notes: str = ""


# ── Alternative model rankings (curated from V2EX/CSDN 2026-06 data) ───

ALTERNATIVES = {
    "claude-opus-4": [
        ModelAlternative(
            name="DeepSeek V3 / R1",
            provider="deepseek",
            model_id="deepseek-chat",
            rating=8.5,
            cost_per_1m_tokens=0.50,
            pros=["推理能力强", "成本极低", "中文优秀", "无降智问题", "开源可自部署"],
            cons=["英文略逊Claude", "工具调用不如Claude", "无Artifacts"],
            setup_env={"DEEPSEEK_API_KEY": "sk-your-key"},
            best_for=["代码生成", "数学推理", "中文内容", "数据分析"],
            community_notes="V2EX 160+回复推荐，中国开发者首选替代。DeepSeek API比OpenAI便宜95%",
        ),
        ModelAlternative(
            name="GPT-4o / GPT-4.1",
            provider="openai",
            model_id="gpt-4o",
            rating=8.0,
            cost_per_1m_tokens=5.00,
            pros=["生态最完善", "函数调用强", "多模态", "速度快"],
            cons=["价格高", "中文偶尔出错", "也有降智传闻"],
            setup_env={"OPENAI_API_KEY": "sk-your-key"},
            best_for=["多模态任务", "复杂工具调用", "企业集成", "函数调用"],
            community_notes="OpenAI近期也有API不稳定报告（V2EX 23+18回复），但整体质量稳定",
        ),
        ModelAlternative(
            name="Gemini 2.5 Pro",
            provider="openai",  # OpenAI-compatible
            model_id="gemini-2.5-pro-exp-03-25",
            rating=7.5,
            cost_per_1m_tokens=1.25,
            pros=["上下文1M tokens", "多模态强", "免费额度", "速度快"],
            cons=["偶尔幻觉", "推理不如Claude", "中文质量参差"],
            setup_env={},
            best_for=["长文档处理", "多模态分析", "探索性任务"],
            community_notes="Gemma4部署V2EX 24回复，Gemini大模型关注度高",
        ),
        ModelAlternative(
            name="Qwen3 / 通义千问",
            provider="openai",
            model_id="qwen-plus",
            rating=7.0,
            cost_per_1m_tokens=0.50,
            pros=["中文第一梯队", "免费额度", "阿里生态", "开源版本"],
            cons=["代码略弱", "英文一般", "复杂推理有时出错"],
            setup_env={"OPENAI_API_KEY": "sk-your-key",
                       "OPENAI_BASE_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
            best_for=["中文写作", "翻译", "文档处理", "国内合规场景"],
            community_notes="国内用户首选合规替代方案，阿里云生态集成好",
        ),
        ModelAlternative(
            name="Claude 多账号轮换",
            provider="anthropic",
            model_id="claude-sonnet-4-20250514",
            rating=6.5,
            cost_per_1m_tokens=3.00,
            pros=["原汁原味Claude", "生态不变", "无需迁移"],
            cons=["降智问题仍存在", "需要多个付费账号", "管理成本高"],
            setup_env={"ANTHROPIC_API_KEY": "sk-ant-key1,sk-ant-key2"},
            best_for=["不愿迁移的用户", "团队共享账号", "短期过渡"],
            community_notes="V2EX Codex多账号管理18回复，多账号轮换是新兴解法",
        ),
    ],
    "claude-sonnet-4": [
        # Same alternatives but with different recommendation ordering
        ModelAlternative(
            name="DeepSeek V3 / R1",
            provider="deepseek",
            model_id="deepseek-chat",
            rating=9.0,
            cost_per_1m_tokens=0.50,
            pros=["性价比极高", "推理接近Claude Sonnet", "完全无降智"],
            cons=["英文输出风格不同", "工具调用需适配"],
            setup_env={"DEEPSEEK_API_KEY": "sk-your-key"},
            best_for=["代码生成", "数据推理", "成本敏感"],
            community_notes="与Claude Sonnet对标的最佳替代品，V2EX社区强烈推荐",
        ),
        ModelAlternative(
            name="GPT-4o",
            provider="openai",
            model_id="gpt-4o",
            rating=7.5,
            cost_per_1m_tokens=5.00,
            pros=["同等能力水平", "生态无缝", "多模态"],
            cons=["贵10倍", "偶尔降智", "生态绑定"],
            setup_env={"OPENAI_API_KEY": "sk-your-key"},
            best_for=["多模态", "企业应用", "复杂工具调用"],
            community_notes="功能最接近但价格差距大",
        ),
        ModelAlternative(
            name="Gemini 2.5 Flash",
            provider="openai",
            model_id="gemini-2.5-flash",
            rating=7.0,
            cost_per_1m_tokens=0.15,
            pros=["超低价格", "超快速度", "长期免费额度"],
            cons=["推理深度一般", "不适合复杂代码"],
            setup_env={},
            best_for=["高频简单任务", "批量处理", "原型验证"],
            community_notes="高频调用的性价比之选",
        ),
    ],
}

# Default alternatives for any Claude variant
DEFAULT_ALTERNATIVES = ALTERNATIVES.get("claude-sonnet-4", [])


@dataclass
class SwitchRecommendation:
    """Complete switching recommendation."""
    reason: str
    urgency: str  # "low", "medium", "high", "critical"
    alternatives: list  # list of ModelAlternative ranked
    keep_zenmux: bool     # whether ZenMux can mitigate instead
    migration_cost: str   # "low", "medium", "high"
    summary: str


def recommend(degradation_score: float, quality_score: float,
              current_model: str = "claude-sonnet-4",
              reasoning_steps_avg: float = 5.0,
              response_length_ratio: float = 1.0) -> SwitchRecommendation:
    """Generate switching recommendation based on degradation metrics.

    Args:
        degradation_score: 0.0-1.0 degradation severity (from evaluator)
        quality_score: 0.0-1.0 quality score (from quality analyzer)
        current_model: Current model identifier
        reasoning_steps_avg: Average reasoning steps per response
        response_length_ratio: Current / baseline response length ratio

    Returns:
        SwitchRecommendation with ranked alternatives.
    """
    # Determine urgency
    if degradation_score > 0.15 or quality_score < 0.3:
        urgency = "critical"
        reason = f"严重降智：质量评分 {quality_score:.2f}，推理步数 {reasoning_steps_avg:.1f}步"
        keep_zenmux = False
    elif degradation_score > 0.10 or quality_score < 0.5:
        urgency = "high"
        reason = f"显著降智：质量评分 {quality_score:.2f}，建议切换"
        keep_zenmux = True  # Still worth trying ZenMux first
    elif degradation_score > 0.05 or quality_score < 0.65:
        urgency = "medium"
        reason = f"轻微降智：质量评分 {quality_score:.2f}，可继续观察"
        keep_zenmux = True
    else:
        urgency = "low"
        reason = f"质量正常：{quality_score:.2f}，无需切换"
        keep_zenmux = True

    # Select alternatives
    alternatives = ALTERNATIVES.get(current_model, DEFAULT_ALTERNATIVES)

    # Filter by urgency
    if urgency == "critical":
        # Only recommend top 2 most reliable
        alternatives = [a for a in alternatives if a.rating >= 7.5][:2]
    elif urgency == "high":
        alternatives = [a for a in alternatives if a.rating >= 7.0][:3]
    else:
        alternatives = alternatives[:3]

    # Migration cost estimate
    if all(a.provider == "anthropic" for a in alternatives):
        migration_cost = "low"
    elif any(a.provider == "deepseek" for a in alternatives):
        migration_cost = "medium"  # Need API key + code changes
    else:
        migration_cost = "medium"

    # Build summary
    top = alternatives[0] if alternatives else None
    if urgency in ("critical", "high") and top:
        summary = (
            f"建议切换至 {top.name} ({top.provider})。"
            f"社区评分 {top.rating}/10，成本 ${top.cost_per_1m_tokens}/1M tokens。"
            f"{top.community_notes}"
        )
    elif urgency == "medium":
        summary = (
            f"暂不建议切换，可先启用 ZenMux 绕行。"
            f"如持续恶化，首选 {top.name if top else 'DeepSeek'}。"
        )
    else:
        summary = "当前模型质量正常，无需切换。"

    return SwitchRecommendation(
        reason=reason,
        urgency=urgency,
        alternatives=alternatives,
        keep_zenmux=keep_zenmux,
        migration_cost=migration_cost,
        summary=summary,
    )


def print_alternatives_table(alternatives: list) -> str:
    """Format alternatives as a simple table.

    Returns:
        Multi-line formatted table.
    """
    if not alternatives:
        return "无可用替代方案"

    lines = []
    lines.append("┌──────┬──────────────────┬──────────┬──────────────┬──────────────┐")
    lines.append("│ 排名 │ 模型             │ 评分     │ 成本/1M tokens│ 最佳场景     │")
    lines.append("├──────┼──────────────────┼──────────┼──────────────┼──────────────┤")
    for i, alt in enumerate(alternatives, 1):
        name = alt.name[:16].ljust(16)
        rating = f"{alt.rating:.1f}/10".ljust(8)
        cost = f"${alt.cost_per_1m_tokens:.2f}".ljust(12)
        best = alt.best_for[0][:12].ljust(12) if alt.best_for else "通用".ljust(12)
        lines.append(f"│  {i}   │ {name}│ {rating}│ {cost}│ {best}│")
    lines.append("└──────┴──────────────────┴──────────┴──────────────┴──────────────┘")

    for i, alt in enumerate(alternatives, 1):
        lines.append(f"\n  {i}. {alt.name} ({alt.provider})")
        lines.append(f"     优点: {', '.join(alt.pros[:3])}")
        lines.append(f"     缺点: {', '.join(alt.cons[:2])}")
        if alt.setup_env:
            env_vars = ' '.join(f'{k}={v}' for k, v in alt.setup_env.items())
            lines.append(f"     配置: {env_vars}")

    return "\n".join(lines)


def print_quick_switch(current_model: str, to_model: str, to_provider: str) -> str:
    """Generate quick-switch instructions for one specific model.

    Returns:
        Shell commands to execute.
    """
    alt = None
    for alts in ALTERNATIVES.values():
        for a in alts:
            if a.name == to_model or a.model_id == to_model:
                alt = a
                break

    if not alt:
        alt = ModelAlternative(
            name=to_model, provider=to_provider, model_id=to_model,
            rating=7.0, cost_per_1m_tokens=1.0,
            setup_env={f"{to_provider.upper()}_API_KEY": "sk-your-key"},
        )

    lines = []
    lines.append(f"# 从 {current_model} 切换到 {alt.name}")
    lines.append("")
    for env_var, default_val in alt.setup_env.items():
        lines.append(f"export {env_var}={default_val}")
    lines.append(f"# 然后正常使用你的 Claude 客户端即可")

    return "\n".join(lines)
