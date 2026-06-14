# 🧠 Claude Intel Monitor

> **检测 Claude / GPT / DeepSeek 是否偷偷变笨**  
> Detect intelligence degradation in AI models with standardized benchmarks + response quality analysis

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green)]()
[![GitHub stars](https://img.shields.io/github/stars/minirr890112-byte/claude-intel-monitor?style=social)](https://github.com/minirr890112-byte/claude-intel-monitor)

## v1.1.0 新增 🆕

- **响应质量分析** (`quality`): 检测 thinking 跳步、推理深度、代码完整性，0-1 综合评分
- **ZenMux 智能绕行** (`zenmux`): Docker Compose 一键部署，主端点降智时自动切换备用模型
- **模型切换推荐** (`switch`): 按场景+预算推荐最佳替代模型，含评分/成本/社区评价
- **质量感知告警**: benchmark 自动检测响应质量 < 30% 触发 🚨 严重告警

## 为什么需要这个工具？

2025-2026年，中文开发者社区反复报道 AI 模型"降智"现象：
- 代码补全变简单，跳过关键逻辑
- 推理时跳步、结论先行  
- 数学能力下降，频繁出现幻觉
- 回复变得敷衍、模板化

Anthropic 和 OpenAI 不会主动报告退化。**claude-intel-monitor** 是独立第三方的量化检测工具。

## 快速开始

```bash
# 安装
pip install git+https://github.com/minirr890112-byte/claude-intel-monitor.git

# 基准测试
claude-intel-monitor test --model claude-sonnet-4 --provider anthropic

# 响应质量分析
claude-intel-monitor quality -f response.txt -c code

# ZenMux 智能路由
claude-intel-monitor zenmux

# 模型切换推荐
claude-intel-monitor switch -s degraded

# 历史趋势
claude-intel-monitor history

# 持续监控
claude-intel-monitor watch --model claude-sonnet-4 --provider anthropic --interval 6h
```

## 命令行一览

| 命令 | 说明 | v1.1 新增 |
|------|------|:---:|
| `test` | 运行基准测试（30题 Math/Reasoning/Code） | — |
| `baseline` | 设定基线用于后续对比 | — |
| `history` | 查看历史趋势 | — |
| `watch` | 持续监控（定时自动测试） | — |
| `quality` | 响应质量分析（thinking跳步/深度/完整性）| ✅ |
| `zenmux` | ZenMux 状态检测 + 配置指南 | ✅ |
| `switch` | 模型切换推荐（按场景+预算） | ✅ |

## 基准测试题

30 道题，覆盖 3 个维度：

| 维度 | 题数 | 权重 | 检测目标 |
|------|------|------|----------|
| Math | 10 | 1.0x | 数学推理能力，幻觉倾向 |
| Reasoning | 10 | 1.2x | 逻辑推理，安全意识降低 |
| Code | 10 | 1.3x | 代码质量，架构能力退化 |

所有题目是中文的，专门针对中文社区报告的降智模式设计。

## 检测原理 (v1.1)

```
                    ┌─────────────┐
题目 → API请求 → 模型回答 → Lambda校验 → 加权评分 → 对比基线
                    │                            │
                    ▼                            ▼
              质量分析器                  质量感知告警
          (thinking/深度/代码)         (< 30% → 🚨)
```

**v1.1 双层检测**: 传统 benchmark（正确与否）+ 响应质量分析（如何回答），全方位捕捉降智信号。

## 响应质量分析

`quality` 命令提供 4 维质量评分：

```
🔬 响应质量分析         85.0%

📊 质量维度
┌──────────┬────────┬──────────┐
│ 维度     │ 得分   │ 说明     │
├──────────┼────────┼──────────┤
│ 冗长度   │ 78.0%  │ 内容充实 │
│ 推理深度 │ 92.0%  │ 推理充分 │
│ 完整性   │ 85.0%  │ 回答完整 │
│ 推理步数 │ 12     │ 丰富     │
└──────────┴────────┴──────────┘
```

同时检测 thinking 跳步（中英文推理标记）、代码截断/省略、模板化回复等降智信号。

## 支持的大模型

| Provider | 环境变量 | 模型示例 |
|----------|----------|----------|
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet-4-20250514 |
| OpenAI | `OPENAI_API_KEY` | gpt-4o, gpt-4.1 |
| DeepSeek | `DEEPSEEK_API_KEY` | deepseek-chat |

> 🏆 **Featured Baseline**: DeepSeek scored **91.1% (27/30)** as the first live test baseline.

## ZenMux 智能路由 (v1.1 新增)

自动检测降智 + 无缝切换备用模型：

```bash
claude-intel-monitor zenmux   # 一键检测+生成配置

# 推荐架构:
# Anthropic (主) → OpenRouter Claude (备用1) → DeepSeek V3 (备用2)
```

`zenmux` 命令检测系统安装状态、扫描现有配置、生成 Docker Compose 一键部署指南。

## 模型切换引擎 (v1.1 新增)

当检测到降智时，智能推荐替代方案：

```bash
claude-intel-monitor switch                  # 降智替代推荐
claude-intel-monitor switch -s cost -b 2.0   # 预算限制推荐
claude-intel-monitor switch -s all            # 全部替代方案
```

内置 5 个替代模型及其评分/成本/社区评价：
- DeepSeek V3 (8.5/10, $0.50/百万token)
- GPT-4o (8.2/10, $5.00/百万token)
- Gemini Pro (7.8/10, $2.50/百万token)
- Claude Sonnet 4 (9.0/10, $8.00/百万token) — 保底回退
- Mistral Large (6.5/10, $1.50/百万token)

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
🔬 质量检测: avg=78.5% | 推理深度=82.0% | thinking跳步=2/30
```

## 使用场景

### 场景 1: 检测模型退化

```bash
claude-intel-monitor baseline --model claude-sonnet-4 --provider anthropic
# ... 一周后 ...
claude-intel-monitor test --model claude-sonnet-4 --provider anthropic
```

### 场景 2: 对比多个供应商

```bash
claude-intel-monitor test --model claude-sonnet-4 --provider anthropic
claude-intel-monitor test --model gpt-4o --provider openai
claude-intel-monitor test --model deepseek-chat --provider deepseek
claude-intel-monitor history  # 对比趋势
```

### 场景 3: CI/CD 持续监控

```bash
claude-intel-monitor watch --model claude-sonnet-4 --provider anthropic --interval 6h &
# 或 cron: 0 9 * * * claude-intel-monitor test --model claude-sonnet-4 >> ~/intel-monitor.log
```

### 场景 4: 降智时自动切换 (v1.1)

```bash
# 1. 部署 ZenMux
claude-intel-monitor zenmux  # 复制 Docker Compose 配置

# 2. 运行 benchmark 检测
claude-intel-monitor test --model claude-sonnet-4

# 3. 质量 < 30% → 查看替代方案
claude-intel-monitor switch -s degraded

# 4. 一键切换
export LLM_PROVIDER=deepseek  # 或通过 ZenMux 自动路由
```

## 项目动机

这个工具从 **HermesMade** 项目的真实痛点数据中诞生。2026 年 4-6 月的中文开发者社区扫描中，"Claude/GPT 降智" 是 Top 1 最热话题（30+ 篇 CSDN 文章爆发，推理深度下降 67%）。我们不想只抱怨，决定做一个可量化的工具。

## Also available on ClawHub

[ClawHub](https://clawhub.ai) is an AI-native package registry. You can install and run `claude-intel-monitor` directly from ClawHub:

```bash
claw install claude-intel-monitor
```

All features, benchmarks, and providers work identically.

## 🌐 生态系统

| Tool | Description |
|---|---|
| [cursor-doctor](https://github.com/minirr890112-byte/cursor-doctor) | Cursor IDE 诊断修复工具 |
| [model-watch](https://github.com/minirr890112-byte/model-watch) | 轻量级模型退化监控 |
| [api-cost-compare](https://github.com/minirr890112-byte/api-cost-compare) | LLM API 价格对比 |
| [openai-ban-tracker](https://github.com/minirr890112-byte/openai-ban-tracker) | OpenAI封号风险检测 |

## 许可证

MIT
