# Changelog

## v1.1.0 (2026-06-06) — 质量分析与智能绕行

### 新增

- **`quality.py`** — 响应质量分析器，提供 4 维质量评分（冗长度/推理深度/完整性/推理步数）
  - `QualityScore` 数据类：0.0-1.0 综合评分
  - 中英文推理标记检测（各 12+ 标记）
  - Thinking 跳步检测、代码完整性检测、模板化回复检测
  - `aggregate_quality()` 批量聚合质量分数

- **`zenmux.py`** — ZenMux 智能路由模块
  - 4 个系统配置路径自动检测
  - Docker Compose 模板（Anthropic 主 + OpenRouter/DeepSeek 备用）
  - `check_zenmux_installed()` / `detect_current_config()` / `generate_setup_guide()`
  - 中英文配置指南

- **`switch_guide.py`** — 模型切换推荐引擎
  - `ModelAlternative` 数据类（含评分/成本/优劣/社区评价）
  - 5 个替代模型：DeepSeek V3 / GPT-4o / Gemini Pro / Sonnet 4 / Mistral Large
  - 3 个推荐场景：`claude-opus-4` / `cloud-degraded` / `two-tier`
  - `pick_best()` 按场景+预算智能推荐

- **CLI 新命令**
  - `quality` — 分析响应文本质量（`-t` 文本 / `-f` 文件 / `-c` 分类）
  - `zenmux` — 检查 ZenMux 安装状态 + 生成配置指南
  - `switch` — 模型切换推荐（`-s degraded/cost/quality/all` + `-b` 预算）

### 改进

- **`evaluator.py`** 集成质量分析
  - `QuestionResult` 新增 `quality_score` 字段
  - `BenchmarkReport` 新增 `quality_scores` / `avg_quality` / `thinking_skip_count`
  - `evaluate_response()` 自动调用质量分析
  - `compute_scores()` 质量感知告警（avg_quality < 30% → 🚨）

- 版本号: 0.1.0 → 1.1.0

### 数据来源

- CSDN 30 篇 Claude 降智文章爆发（2026-06-06 扫描）
- 推理深度下降 67%，thinking 跳步成为核心痛点
- 社区呼声：需要"降智→检测→绕行"完整链路

---

## v0.1.0 (2026-05-XX) — 初始版本

- 30 道固定基准测试题（Math/Reasoning/Code 各 10 题）
- 3 个 Provider：Anthropic / OpenAI / DeepSeek
- SQLite 历史数据库 + 基线对比
- CLI 命令：`test` / `baseline` / `history` / `watch`
- DeepSeek 基线: 91.1% (27/30)
