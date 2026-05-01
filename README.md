# 🧠 Claude Intel Monitor

> **检测 Claude / GPT / DeepSeek 是否偷偷变笨**  
> Detect intelligence degradation in AI models with standardized benchmarks

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green)]()

## 为什么需要这个工具？

2025-2026年，中文开发者社区反复报道 Claude/GPT 存在"降智"现象：
- 代码补全变简单，跳过关键逻辑
- 推理时跳步、结论先行
- 数学能力下降，频繁出现幻觉
- 回复变得敷衍、模板化

Anthropic 和 OpenAI 不会主动报告退化。**claude-intel-monitor** 是独立第三方的量化检测工具。

## 快速开始

```bash
# 安装
pip install claude-intel-monitor

# 测试某个模型（需要 API key）
claude-intel-monitor test --model claude-sonnet-4 --provider anthropic

# 自测模式（无需 API）
claude-intel-monitor test --self

# 查看历史趋势
claude-intel-monitor history

# 设置基线（用于后续检测退化）
claude-intel-monitor baseline --model claude-sonnet-4

# 持续监控
claude-intel-monitor watch --model claude-sonnet-4 --provider anthropic --interval 6h
```

## 基准测试题

30 道题，覆盖 3 个维度：

| 维度 | 题数 | 权重 | 检测目标 |
|------|------|------|----------|
| Math | 10 | 1.0x | 数学推理能力，幻觉倾向 |
| Reasoning | 10 | 1.2x | 逻辑推理，安全意识降低 |
| Code | 10 | 1.3x | 代码质量，架构能力退化 |

所有题目是中文的，专门针对中文社区报告的降智模式设计。

## 检测原理

```
题目 → API请求 → 模型回答 → Lambda校验 → 加权评分 → 对比基线
```

- 每个题目有独立的 `check` 函数验证答案
- 不使用 AI 评分（避免偏见）
- 历史数据存储在 SQLite（`~/.claude-intel-monitor/history.db`）
- 退化阈值：5% 警告，10% 严重告警

## 支持的大模型

| Provider | 环境变量 | 模型示例 |
|----------|----------|----------|
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet-4-20250514 |
| OpenAI | `OPENAI_API_KEY` | gpt-4o, gpt-4.1 |
| DeepSeek | `DEEPSEEK_API_KEY` | deepseek-chat |

## 输出示例

```
🧠 Testing claude-sonnet-4 via anthropic — 30 questions

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃      82.3%  ██████████████░░░░░░  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📊 分类得分
┌──────────┬────────┬────────┬────────┬───────────┐
│ 类别     │ 通过率 │ 加权分 │ 状态   │ vs 基线   │
├──────────┼────────┼────────┼────────┼───────────┤
│ math     │ 8/10   │ 80.0%  │ ✅     │ -2.1%    │
│ reasoning│ 9/10   │ 90.0%  │ 🟢     │ +1.5%    │
│ code     │ 7/10   │ 70.0%  │ ⚠️     │ -6.2%    │
└──────────┴────────┴────────┴────────┴───────────┘

⚠️ code: 轻微下降 6.2% (current=70.0%, baseline=76.2%)
```

## 项目动机

这个工具从 **HermesMade** 项目的真实痛点数据中诞生。在 2026 年 4 月的中国开发者社区扫描中，"Claude/GPT 降智" 是 Top 3 最热话题。我们不想只抱怨，决定做一个可量化的工具。

## 许可证

MIT
