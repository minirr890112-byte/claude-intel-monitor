---
name: claude-intel-monitor
description: Detect when Claude/GPT/DeepSeek gets dumber. 30 benchmark questions (Math/Reasoning/Code), response quality analysis, ZenMux smart routing, model switch recommendations. Track intelligence degradation over time.
version: 1.2.0
author: minirr890112-byte
license: MIT
metadata:
  hermes:
    tags: [AI, Monitoring, Benchmark, Claude, GPT, DeepSeek, Intelligence, Degradation]
    homepage: https://github.com/minirr890112-byte/claude-intel-monitor
---

# Claude Intel Monitor

## Problem → Solution

**The problem**: You're coding with Claude and suddenly it feels... off. Code completions are simpler. Reasoning skips steps. Math answers are wrong. You wonder: "Did they nerf the model?" Anthropic and OpenAI don't announce degradations. You're left guessing if it's you or them.

**The solution**: Standardized 30-question benchmark across Math, Reasoning, and Code. Run it daily, track scores over time. When scores drop >10%, you get an alert. Response quality analysis detects thinking-skipping. ZenMux routes to backup models when your primary degrades.

## Quick Start

```bash
pip install git+https://github.com/minirr890112-byte/claude-intel-monitor.git

claude-intel-monitor test --model claude-sonnet-4 --provider anthropic
claude-intel-monitor watch --model claude-sonnet-4 --interval 6h
claude-intel-monitor quality -f response.txt -c code
claude-intel-monitor history
claude-intel-monitor zenmux
claude-intel-monitor switch -s degraded
```

## Real Output

```
$ claude-intel-monitor test --model claude-sonnet-4

🧠 Claude Intel Monitor v1.1.0
Model: claude-sonnet-4 (anthropic)
────────────────────────────────────
Math:      8/10 (80%) ████████░░
Reasoning: 7/10 (70%) ███████░░░
Code:      9/10 (90%) █████████░
────────────────────────────────────
Total:     24/30 (80%)
Status: ✅ Normal (within 5% of baseline)

$ claude-intel-monitor quality -f response.txt
Response Quality: 0.62/1.00 ⚠️
├─ Thinking depth:   0.45  ⚠️ Shallow
├─ Code completeness: 0.85  ✅
└─ Hallucination:    0.55  ⚠️ Suspect
```

## Commands

| Command | Description | v1.1 |
|---------|-------------|:----:|
| `test` | Run 30-question benchmark | — |
| `watch` | Continuous monitoring at interval | — |
| `quality` | Response quality analysis | ✅ |
| `zenmux` | Smart routing to backup models | ✅ |
| `switch` | Model switch recommendations | ✅ |
| `history` | Score trend over time | — |

---
⭐ **Star this repo if you've felt the model get dumber**: [github.com/minirr890112-byte/claude-intel-monitor](https://github.com/minirr890112-byte/claude-intel-monitor)
