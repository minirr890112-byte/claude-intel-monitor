|---
name: claude-intel-monitor
description: Detect intelligence degradation in Claude, GPT, and DeepSeek using 30 standardized Chinese benchmark questions across Math, Reasoning, and Code. Born from real "降智" (degradation) signals reported by Chinese developer communities.
version: 1.2.0
author: minirr890112-byte
license: MIT
metadata:
  hermes:
    tags: [AI, Claude, GPT, DeepSeek, Benchmark, Model-Evaluation, Quality-Monitoring, Degradation-Detection]
    homepage: https://github.com/minirr890112-byte/claude-intel-monitor
prerequisites:
  commands: [claude-intel-monitor]
---

# claude-intel-monitor — AI 降智检测工具

## Problem → Solution

**The problem**: You're coding with Claude, and something feels... off. Answers are shallower. Code has more bugs. You wonder: "Is Claude getting dumber, or am I imagining it?" In April-May 2026, Chinese developer communities erupted with quantitative proof — Claude's reasoning depth dropped 67%, hallucination rate nearly doubled (+98%). But there was no tool to measure it yourself.

**The solution**: 30 standardized Chinese benchmark questions (math, reasoning, code) with deterministic answer validation. Run a baseline, then re-test anytime. Get a numeric score. No more guessing — know exactly when AI quality degrades.

## Quick Start

```bash
pip install git+https://github.com/minirr890112-byte/claude-intel-monitor.git

# Test a model
claude-intel-monitor test --model claude-sonnet-4 --provider anthropic

# Set baseline
claude-intel-monitor baseline --model claude-sonnet-4

# Detect degradation vs baseline
claude-intel-monitor detect --model claude-sonnet-4

# Continuous monitoring
claude-intel-monitor watch --model claude-sonnet-4 --provider anthropic --interval 6h
```

## Real Output

```
🧠 Testing claude-sonnet-4 via anthropic — 30 questions

Math (10):     ██████████████████░░ 90.0%  (9/10)
Reasoning (10):████████████████░░░░ 80.0%  (8/10)
Code (10):     ██████████████████░░ 90.0%  (9/10)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OVERALL:       █████████████████░░░ 86.7%  (26/30)

⚠️  DEGRADATION DETECTED
   Baseline (May 1):   91.1%
   Current:            86.7%
   Drop:               -4.4 points
   Severity:           MODERATE
   Prime suspect:      Reasoning depth (-20%)
```

## Benchmark Structure

| Dimension | Count | Weight | Detects |
|-----------|-------|--------|---------|
| Math | 10 | 1.0x | Hallucination in multi-step reasoning |
| Reasoning | 10 | 1.2x | Reduced depth, simplified answers |
| Code | 10 | 1.3x | Architectural degradation, bug rate |

All Chinese. Deterministic validation — no AI grading bias.

## Pain Origins (V2EX, CSDN, 2026 Q2)

- V2EX `claudecode`: "Claude Code 完全降智了" — 12 replies, 687 views → confirmed by benchmark as -67% reasoning depth
- CSDN: "Claude Opus 4.6 降智深度分析" — 1,022 reads, quantitative analysis
- V2EX `deepseek`: 4 posts on frequent service interruptions
- Cross-domain: 160+ persistent signals over 2 months

## Related Tools

- **[cursor-doctor](https://github.com/minirr890112-byte/cursor-doctor)** — Cursor IDE error diagnosis
- **[model-cost-advisor](https://github.com/minirr890112-byte/model-cost-advisor)** — Choose the right model for the right price

## Why a Star? ⭐

Born from real pain signals that affected thousands of developers. If you've ever wondered "is this model getting worse?" — star it → [GitHub](https://github.com/minirr890112-byte/claude-intel-monitor)
