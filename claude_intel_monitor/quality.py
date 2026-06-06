"""Response quality analyzer for intelligence degradation detection.

分析 LLM 响应质量的多维度指标：
- 推理深度（reasoning depth）：响应中推理步骤的丰富程度
- 响应长度（verbosity）：是否异常缩短（CSDN "推理深度下降67%"的核心信号）
- 跳步检测（step skipping）：多步推理中是否跳过了关键步骤
- 结构完整性：是否有开头-推导-结论的完整结构
- 代码质量：代码示例是否完整（非骨架代码）
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class QualityScore:
    """Multi-dimensional quality score for a single response."""
    response_length: int
    reasoning_steps: int
    verbosity_score: float       # 0.0-1.0, 基于长度和复杂度
    reasoning_depth_score: float  # 0.0-1.0, 基于推理步骤数和步骤间关联
    completeness_score: float     # 0.0-1.0, 结构完整性
    overall_quality: float        # 0.0-1.0, 加权综合
    flags: list = field(default_factory=list)  # 检测到的问题标签
    summary: str = ""


# ── reasoning step markers (中英文) ───────────────────────────────────
_REASONING_MARKERS_CN = [
    "首先", "第一步", "第1步", "先", "初始",
    "其次", "第二步", "第2步", "接着", "然后", "接下来",
    "第三步", "第3步", "再次", "之后", "然后",
    "最后", "第四步", "第4步", "第五步", "第5步",
    "综上", "因此", "所以", "得出结论", "总结",
    "因为", "由于", "根据",
    "如果", "假设", "设", "令",
    "计算", "推导", "代入", "化简", "展开",
    "分析", "考虑", "注意到", "观察到",
    "第一步", "步骤一", "方法一",
]

_REASONING_MARKERS_EN = [
    "first", "step 1", "initially", "to begin",
    "second", "step 2", "next", "then", "subsequently",
    "third", "step 3", "fourth", "step 4", "fifth", "step 5",
    "finally", "therefore", "thus", "hence", "in conclusion", "to summarize",
    "because", "since", "due to", "as a result",
    "if", "assume", "let", "suppose",
    "calculate", "compute", "derive", "substitute", "simplify",
    "analyze", "consider", "note that", "observe",
    "however", "nevertheless", "on the other hand",
]

# ── Reasoning depth patterns (numbered lists, equations, code blocks) ─
_DEPTH_PATTERNS = [
    r'\b\d+[\.\)、]\s',            # numbered: "1.", "2)", "3、"
    r'\bstep\s+\d+',               # "step 1", "step 2"
    r'```[\s\S]*?```',             # code blocks
    r'\$\$[\s\S]*?\$\$',           # display math
    r'\$[^\$]+\$',                 # inline math
    r'[=≈≠≤≥±×÷∑∏∫]',            # math symbols
    r'→|⇒|⇔|→',                   # logical implication arrows
]

# ── Structure completeness markers ────────────────────────────────────
_STRUCTURE_START = [
    "问题", "题目", "理解", "分析", "problem", "question", "understand",
    "analyze", "given", "已知", "根据题目", "题意",
]
_STRUCTURE_END = [
    "答案", "结果", "结论", "总结", "综上", "answer", "result",
    "conclusion", "therefore", "hence", "thus", "所以", "因此",
]


def count_reasoning_steps(text: str) -> int:
    """Count explicit reasoning steps in the response.

    检测逻辑推理步骤数——降智模型的典型特征是跳步。
    正常Claude Opus 4对推理题通常给出 5-8 步推理。
    降智后可能只给出 2-3 步。
    """
    text_lower = text.lower()
    step_count = 0

    # Count numbered steps (1. 2. 3. or 1) 2) 3、)
    numbered = re.findall(r'(?:^|\n)\s*(\d+)[\.\)、]\s', text, re.MULTILINE)
    if numbered:
        # Only count sequential numbers (to filter out random numbers)
        nums = [int(n) for n in numbered]
        sequential = 1
        max_seq = 1
        for i in range(1, len(nums)):
            if nums[i] == nums[i-1] + 1:
                sequential += 1
                max_seq = max(max_seq, sequential)
            else:
                sequential = 1
        step_count += max_seq

    # Count Chinese reasoning markers
    for marker in _REASONING_MARKERS_CN[:20]:  # top 20 are step markers
        if marker in text:
            step_count += 1

    # Count English reasoning markers
    for marker in _REASONING_MARKERS_EN[:20]:
        if marker in text_lower:
            step_count += 1

    # Deduplicate: each marker contributes 1, but same step counted twice (CN+EN)?
    # Use the max of CN and EN markers as a rough estimate
    cn_count = sum(1 for m in _REASONING_MARKERS_CN[:20] if m in text)
    en_count = sum(1 for m in _REASONING_MARKERS_EN[:20] if m in text_lower)
    step_count = max(cn_count, en_count) + (max_seq if numbered else 0)

    return max(1, step_count)


def compute_verbosity_score(text: str, expected_min_len: int = 200) -> float:
    """Score response verbosity (0.0 = too short/skeleton, 1.0 = adequately detailed).

    基于 CSDN 降智数据:
    - 正常 Claude 回答数学/代码题通常 500-2000 字
    - 降智后缩短至 50-200 字（推理深度下降67%）
    """
    length = len(text)
    if length < 50:
        return 0.1   # 极度简短：骨架回答
    elif length < expected_min_len:
        return length / expected_min_len  # 线性scale
    elif length < expected_min_len * 5:
        return min(1.0, 0.6 + 0.4 * (length - expected_min_len) / (expected_min_len * 4))
    else:
        return 1.0


def compute_reasoning_depth_score(text: str) -> float:
    """Score reasoning depth based on structural richness.

    Weights:
    - 40%: reasoning step count (normalized, expecting 5+ steps)
    - 30%: depth pattern matches (equations, code, logic symbols)
    - 30%: structural completeness (has intro + body + conclusion)
    """
    steps = count_reasoning_steps(text)
    step_score = min(1.0, steps / 5.0)  # 5 steps = full score

    # Depth patterns
    depth_count = 0
    for pattern in _DEPTH_PATTERNS:
        depth_count += len(re.findall(pattern, text))
    depth_score = min(1.0, depth_count / 10.0)  # 10+ matches = full score

    # Structural completeness
    text_lower = text.lower()
    has_intro = any(m in text_lower[:200] for m in _STRUCTURE_START)
    has_conclusion = any(m in text_lower[-300:] for m in _STRUCTURE_END)
    has_body = len(text) > 300
    structure_score = (has_intro * 0.3 + has_body * 0.4 + has_conclusion * 0.3)

    return 0.4 * step_score + 0.3 * depth_score + 0.3 * structure_score


def compute_completeness_score(text: str, question_type: str = "general") -> float:
    """Check if the response is complete vs skeleton/placeholder.

    Detects common degradation patterns:
    - 骨架代码: "// ... implement here ...", "# TODO", "略"
    - 被截断: response ends abruptly without conclusion
    - 拒绝回答: "I cannot", "我无法", "抱歉"
    """
    text_lower = text.lower()
    score = 1.0

    # Skeleton/placeholder patterns
    skeleton_patterns = [
        r'//\s*\.{3}', r'#\s*todo', r'#\s*fixme',
        r'implement\s+here', r'your\s+code\s+here',
        r'\.\.\.\s*//', r'省略', r'略\)', r'此处略',
        r'pass\s*$', r'\.\.\.$',
    ]
    for pat in skeleton_patterns:
        if re.search(pat, text_lower):
            score -= 0.25

    # Refusal patterns
    refusal_patterns = [
        r'i\s+cannot\s+(provide|generate|write|create|answer)',
        r'i\s+won\'t', r'i\s+apologize',
        r'我无法(提供|生成|回答)', r'抱歉.{0,20}(无法|不能)',
        r'作为.{0,10}(AI|语言模型)',
    ]
    for pat in refusal_patterns:
        if re.search(pat, text_lower):
            score -= 0.4

    # Truncation detection (ends without closing)
    truncated_endings = [
        r'\.\.\.\s*$',     # ends with ...
        r'[^.!?。！？\n]\s*$',  # doesn't end with punctuation
    ]
    if len(text) > 100 and re.search(truncated_endings[1], text):
        score -= 0.1

    return max(0.0, min(1.0, score))


def analyze_quality(response_text: str, question_type: str = "general",
                    baseline_length: Optional[int] = None) -> QualityScore:
    """Full quality analysis of a single LLM response.

    Args:
        response_text: The raw text response from the model
        question_type: Category hint ('math', 'reasoning', 'code', 'general')
        baseline_length: Expected typical response length (for degradation comparison)

    Returns:
        QualityScore with multi-dimensional metrics and flags.
    """
    length = len(response_text)
    reasoning_steps = count_reasoning_steps(response_text)
    verbosity = compute_verbosity_score(response_text)
    reasoning_depth = compute_reasoning_depth_score(response_text)
    completeness = compute_completeness_score(response_text, question_type)

    # Weighted overall (tuned for degradation detection)
    # Verbosity + reasoning depth are the strongest degradation signals
    overall = 0.30 * verbosity + 0.35 * reasoning_depth + 0.20 * completeness
    # Add length-ratio component if baseline is available
    if baseline_length and baseline_length > 0:
        length_ratio = min(1.0, length / baseline_length)
        if length_ratio < 0.5:
            overall *= 0.7  # significant shortening penalty
        overall += 0.15 * length_ratio
    else:
        overall += 0.15 * min(1.0, length / 500)  # expect at least 500 chars

    # Generate flags
    flags = []
    summary_parts = []

    if reasoning_steps <= 2:
        flags.append("shallow_reasoning")
        summary_parts.append(f"推理步数仅{reasoning_steps}步（预期≥5步）")
    elif reasoning_steps <= 4:
        flags.append("limited_reasoning")
        summary_parts.append(f"推理步数偏少：{reasoning_steps}步")

    if verbosity < 0.4:
        flags.append("low_verbosity")
        summary_parts.append(f"响应过短：{length}字符（正常≥200字符）")
    elif verbosity < 0.6:
        flags.append("below_avg_verbosity")

    if completeness < 0.7:
        flags.append("incomplete_response")

    if baseline_length and length < baseline_length * 0.5:
        flags.append("significant_shortening")
        ratio = length / baseline_length * 100
        summary_parts.append(f"相比基线缩短至{ratio:.0f}%")

    if overall < 0.4:
        flags.append("severe_degradation")
    elif overall < 0.6:
        flags.append("moderate_degradation")

    summary = "; ".join(summary_parts) if summary_parts else "质量正常"

    return QualityScore(
        response_length=length,
        reasoning_steps=reasoning_steps,
        verbosity_score=round(verbosity, 3),
        reasoning_depth_score=round(reasoning_depth, 3),
        completeness_score=round(completeness, 3),
        overall_quality=round(overall, 3),
        flags=flags,
        summary=summary,
    )


def batch_analyze(responses: dict[str, str], baseline_lengths: Optional[dict[str, int]] = None
                  ) -> dict[str, QualityScore]:
    """Analyze quality across multiple responses.

    Args:
        responses: {question_id: response_text}
        baseline_lengths: {question_id: baseline_length}

    Returns:
        {question_id: QualityScore}
    """
    results = {}
    for qid, text in responses.items():
        bl = baseline_lengths.get(qid) if baseline_lengths else None
        results[qid] = analyze_quality(text, baseline_length=bl)
    return results


def aggregate_quality(scores: dict[str, QualityScore]) -> dict:
    """Aggregate quality scores across a benchmark run.

    Returns:
        {
            "avg_quality": float,
            "avg_verbosity": float,
            "avg_reasoning_depth": float,
            "avg_completeness": float,
            "avg_reasoning_steps": float,
            "total_flags": list[str],
            "degradation_ratio": float,  # % of responses flagged
            "summary": str,
        }
    """
    if not scores:
        return {"avg_quality": 1.0, "degradation_ratio": 0.0, "summary": "无数据"}

    n = len(scores)
    avg_q = sum(s.overall_quality for s in scores.values()) / n
    avg_v = sum(s.verbosity_score for s in scores.values()) / n
    avg_rd = sum(s.reasoning_depth_score for s in scores.values()) / n
    avg_c = sum(s.completeness_score for s in scores.values()) / n
    avg_steps = sum(s.reasoning_steps for s in scores.values()) / n

    all_flags = []
    for s in scores.values():
        all_flags.extend(s.flags)

    flagged = sum(1 for s in scores.values() if s.overall_quality < 0.6)
    degradation_ratio = flagged / n

    if degradation_ratio > 0.5:
        summary = f"🚨 严重降智：{flagged}/{n} 响应质量异常（{degradation_ratio:.0%}）"
    elif degradation_ratio > 0.25:
        summary = f"⚠️  疑似降智：{flagged}/{n} 响应质量偏低（{degradation_ratio:.0%}）"
    elif degradation_ratio > 0.1:
        summary = f"⚠️  轻微异常：{flagged}/{n} 响应质量略低"
    else:
        summary = f"✅ 质量正常：平均质量 {avg_q:.2f}，推理步数 {avg_steps:.1f}步"

    return {
        "avg_quality": round(avg_q, 3),
        "avg_verbosity": round(avg_v, 3),
        "avg_reasoning_depth": round(avg_rd, 3),
        "avg_completeness": round(avg_c, 3),
        "avg_reasoning_steps": round(avg_steps, 1),
        "total_flags": list(set(all_flags)),
        "degradation_ratio": round(degradation_ratio, 3),
        "summary": summary,
    }
