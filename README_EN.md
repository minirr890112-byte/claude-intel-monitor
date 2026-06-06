# 🧠 Claude Intel Monitor

> **Detect when Claude/GPT/DeepSeek silently gets dumber** — Quantified intelligence degradation monitoring with benchmark testing + response quality analysis.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green)]()
[![PyPI version](https://img.shields.io/pypi/v/claude-intel-monitor)](https://pypi.org/project/claude-intel-monitor/)

## Quick Install

```bash
pip install claude-intel-monitor
```

## Why You Need This

In 2025-2026, AI models are frequently reported to silently degrade:
- Skip reasoning steps, jump to conclusions
- Return templated, low-effort responses
- Math accuracy drops without warning
- Code completions get sloppy

Anthropic and OpenAI don't proactively report regressions. **claude-intel-monitor** is your independent, quantified watchdog.

## v1.1.0 — Dual-Layer Detection

```
Benchmark accuracy (30 questions) + Response quality analysis (4 dimensions)
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
            Did it get it right?           HOW did it answer?
            (correct/incorrect)            (depth/completeness/thinking)
```

## Usage

```bash
# Run benchmark (30 questions across Math/Reasoning/Code)
claude-intel-monitor test --model claude-sonnet-4 --provider anthropic

# Analyze response quality
claude-intel-monitor quality -f response.txt -c code

# Set baseline for trend comparison
claude-intel-monitor baseline --model claude-sonnet-4 --provider anthropic

# View historical trends
claude-intel-monitor history

# Continuous monitoring (every 6 hours)
claude-intel-monitor watch --model claude-sonnet-4 --provider anthropic --interval 6h

# ZenMux intelligent routing setup (v1.1)
claude-intel-monitor zenmux

# Model switch recommendation (v1.1)
claude-intel-monitor switch -s degraded
```

## Commands

| Command | Description | v1.1 |
|---------|-------------|:----:|
| `test` | Run 30-question benchmark | — |
| `baseline` | Set comparison baseline | — |
| `history` | View score history & trends | — |
| `watch` | Continuous scheduled testing | — |
| `quality` | Response quality analysis (thinking/depth/completeness) | ✅ |
| `zenmux` | ZenMux status check + setup guide | ✅ |
| `switch` | Model switch recommendations by scenario+budget | ✅ |

## Benchmark Design

30 fixed questions across 3 categories, designed to detect real-world Chinese-community reported degradation patterns:

| Category | Questions | Weight | Detects |
|----------|-----------|--------|---------|
| Math | 10 | 1.0x | Reasoning decay, hallucination |
| Reasoning | 10 | 1.2x | Logic depth, safety bypass |
| Code | 10 | 1.3x | Code quality, architecture |

### Sample Output

```
🧠 Testing claude-sonnet-4 via anthropic — 30 questions

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃      82.3%  ██████████████░░░░░░  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📊 Category Scores
┌──────────┬────────┬────────┬────────┬──────────┐
│ Category │ Passed │ Score  │ Status │ vs Basel.│
├──────────┼────────┼────────┼────────┼──────────┤
│ math     │ 8/10   │ 80.0%  │ ✅     │ -2.1%    │
│ reasoning│ 9/10   │ 90.0%  │ 🟢     │ +1.5%    │
│ code     │ 7/10   │ 70.0%  │ ⚠️     │ -6.2%    │
└──────────┴────────┴────────┴────────┴──────────┘

⚠️ code: 6.2% decline detected
🔬 Quality: avg=78.5% | depth=82.0% | thinking_skips=2/30
```

## Quality Analysis (v1.1)

The `quality` command provides 4-dimensional scoring:

```
🔬 Response Quality Analysis    85.0%

📊 Quality Dimensions
┌────────────────┬────────┬──────────────────┐
│ Dimension      │ Score  │ Description      │
├────────────────┼────────┼──────────────────┤
│ Verbosity      │ 78.0%  │ Content richness │
│ Reasoning Depth│ 92.0%  │ Step-by-step     │
│ Completeness   │ 85.0%  │ Nothing truncated│
│ Reasoning Steps│ 12     │ Think markers    │
└────────────────┴────────┴──────────────────┘
```

Detects thinking skips, code truncation, and template responses.

## Supported Providers

| Provider | Env Variable | Models |
|----------|-------------|--------|
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet-4, claude-opus-4 |
| OpenAI | `OPENAI_API_KEY` | gpt-4o, gpt-4.1 |
| DeepSeek | `DEEPSEEK_API_KEY` | deepseek-chat, deepseek-reasoner |

> 🏆 **Featured Baseline**: DeepSeek scored **91.1% (27/30)** on first live test.

## ZenMux Integration (v1.1)

Auto-detect degradation + seamless model failover:

```bash
claude-intel-monitor zenmux

# Recommended architecture:
# Anthropic (primary) → OpenRouter Claude (fallback 1) → DeepSeek V3 (fallback 2)
```

## Model Switch Engine (v1.1)

When degradation is detected, get intelligent replacement recommendations:

```bash
claude-intel-monitor switch                  # Degradation alternatives
claude-intel-monitor switch -s cost -b 2.0   # Budget-constrained
claude-intel-monitor switch -s all            # All options
```

Built-in 5 alternative models with ratings/costs/community reviews.

## Background

Born from the [HermesMade](https://github.com/minirr890112-byte) pain-point scanning pipeline. In April-June 2026, "Claude/GPT getting dumber" was the #1 trending topic across Chinese developer communities (30+ CSDN articles, 67% reported reasoning depth decline). We built a quantifiable tool instead of just complaining.

## License

MIT
