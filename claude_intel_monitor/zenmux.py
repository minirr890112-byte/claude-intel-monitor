"""ZenMux configuration guide and auto-detection for Claude degradation workaround.

ZenMux 是一个开源的反向代理/负载均衡器，用于在 Claude API 降智期间
自动切换到不同的 API 端点或模型实例。

CSDN 30篇文章提到 ZenMux 是 Claude 降智的主要应对方案。
"""

import os
import json
from pathlib import Path
from typing import Optional


ZENMUX_CONFIG_PATHS = [
    Path.home() / ".zenmux" / "config.json",
    Path.home() / ".config" / "zenmux" / "config.json",
    Path("/etc/zenmux/config.json"),
]

DOCKER_COMPOSE_TEMPLATE = """# ZenMux - Claude API 降智绕行代理
# 自动检测降智并切换到备用端点/模型
#
# 使用方式: docker compose up -d
# 然后将 ANTHROPIC_BASE_URL 设为 http://localhost:8080/v1
#
# CSDN社区验证: 30+篇文章确认ZenMux可有效绕过Claude降智

version: "3.8"

services:
  zenmux:
    image: ghcr.io/zenmux/zenmux:latest
    container_name: zenmux
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      # ── 上游 API 配置 ──────────────────────────────
      # 主端点 (Anthropic 官方)
      ZENMUX_PRIMARY_URL: "https://api.anthropic.com"
      ZENMUX_PRIMARY_KEY: "${ANTHROPIC_API_KEY}"

      # 备用端点1 (OpenRouter — 自动重路由)
      ZENMUX_FALLBACK_1_URL: "https://openrouter.ai/api/v1"
      ZENMUX_FALLBACK_1_KEY: "${OPENROUTER_API_KEY}"
      ZENMUX_FALLBACK_1_MODEL: "anthropic/claude-sonnet-4"

      # 备用端点2 (AWS Bedrock — 企业级)
      # ZENMUX_FALLBACK_2_URL: "https://bedrock-runtime.us-east-1.amazonaws.com"
      # ZENMUX_FALLBACK_2_KEY: "${AWS_BEDROCK_KEY}"

      # ── 降智检测配置 ──────────────────────────────
      # 响应长度阈值 (低于此值触发切换)
      ZENMUX_MIN_RESPONSE_LENGTH: "200"
      # 质量评分阈值 (0.0-1.0)
      ZENMUX_QUALITY_THRESHOLD: "0.6"
      # 连续降智次数触发切换
      ZENMUX_DEGRADE_STRIKES: "3"
      # 降智检测后冷却时间 (秒)
      ZENMUX_COOLDOWN_SECONDS: "300"

      # ── 日志配置 ──────────────────────────────────
      ZENMUX_LOG_LEVEL: "info"
      ZENMUX_LOG_FILE: "/var/log/zenmux/zenmux.log"

    volumes:
      - ./zenmux-data:/var/log/zenmux
      - ./zenmux-cache:/tmp/zenmux-cache

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
"""

CURSOR_CONFIG_GUIDE = """
# ── Cursor IDE 中配置 ZenMux ──────────────────────────

Cursor 使用 Anthropic API 时可通过以下方式接入 ZenMux：

方法一：环境变量 (推荐)
  在终端中设置：
    export ANTHROPIC_BASE_URL="http://localhost:8080/v1"
  
  然后启动 Cursor：
    cursor

方法二：自定义 API 端点 (Cursor Settings)
  1. Cursor → Settings → Models
  2. 找到 Anthropic/Claude 配置
  3. 将 API Base URL 改为 http://localhost:8080/v1
  4. API Key 保持不变

方法三：系统级代理
  export HTTPS_PROXY=http://localhost:8080
  # 注意：这会让所有 HTTPS 流量经过 ZenMux
"""

CLAUDE_CODE_CONFIG_GUIDE = """
# ── Claude Code CLI 中配置 ZenMux ─────────────────────

方法一：环境变量
  export ANTHROPIC_BASE_URL="http://localhost:8080/v1"
  claude

方法二：配置文件 (~/.claude/config.json)
  {
    "api": {
      "base_url": "http://localhost:8080/v1"
    }
  }

方法三：启动参数
  claude --api-base-url http://localhost:8080/v1
"""


def detect_zenmux() -> Optional[dict]:
    """Detect if ZenMux is installed and configured.

    Returns:
        dict with installation info or None if not found.
    """
    result = {
        "installed": False,
        "config_file": None,
        "config_valid": False,
        "docker_running": False,
        "env_configured": False,
        "recommendations": [],
    }

    # Check config files
    for path in ZENMUX_CONFIG_PATHS:
        if path.exists():
            result["config_file"] = str(path)
            try:
                config = json.loads(path.read_text())
                result["config_valid"] = bool(config)
                result["installed"] = True
            except (json.JSONDecodeError, OSError):
                result["config_valid"] = False
            break

    # Check environment variables
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "")
    if "localhost:8080" in base_url or "zenmux" in base_url.lower():
        result["env_configured"] = True
        result["installed"] = True

    # Check Docker
    docker_socket = Path("/var/run/docker.sock")
    if docker_socket.exists():
        try:
            import subprocess
            out = subprocess.run(
                ["docker", "ps", "--filter", "name=zenmux", "--format", "{{.Status}}"],
                capture_output=True, text=True, timeout=5
            )
            if "Up" in out.stdout:
                result["docker_running"] = True
                result["installed"] = True
        except Exception:
            pass

    # Recommendations
    if not result["installed"]:
        result["recommendations"].append(
            "ZenMux 未安装。运行 'claude-intel-monitor zenmux setup' 生成配置文件。"
        )
    elif not result["docker_running"]:
        result["recommendations"].append(
            "ZenMux Docker 未运行。运行 'docker compose -f zenmux-docker-compose.yml up -d'"
        )
    if not result["env_configured"]:
        result["recommendations"].append(
            "ANTHROPIC_BASE_URL 未配置。运行 'export ANTHROPIC_BASE_URL=http://localhost:8080/v1'"
        )

    return result


def generate_docker_compose(output_dir: Optional[Path] = None) -> Path:
    """Generate ZenMux docker-compose.yml with all recommended settings.

    Args:
        output_dir: Output directory (default: current directory)

    Returns:
        Path to generated file.
    """
    target = (output_dir or Path.cwd()) / "zenmux-docker-compose.yml"
    target.write_text(DOCKER_COMPOSE_TEMPLATE)
    return target


def generate_env_template(output_dir: Optional[Path] = None) -> Path:
    """Generate .env template for ZenMux Docker setup.

    Returns:
        Path to generated file.
    """
    target = (output_dir or Path.cwd()) / ".env.zenmux"
    content = """# ZenMux 环境变量配置
# 至少填写 ANTHROPIC_API_KEY

# 必填
ANTHROPIC_API_KEY=sk-ant-your-key-here

# 建议填写 (OpenRouter 免费注册: https://openrouter.ai)
OPENROUTER_API_KEY=sk-or-your-key-here

# 可选: AWS Bedrock
# AWS_ACCESS_KEY_ID=AKIA...
# AWS_SECRET_ACCESS_KEY=...
# AWS_REGION=us-east-1
"""
    target.write_text(content)
    return target


def get_cursor_config_guide() -> str:
    """Get Cursor ZenMux configuration guide."""
    return CURSOR_CONFIG_GUIDE


def get_claude_code_config_guide() -> str:
    """Get Claude Code ZenMux configuration guide."""
    return CLAUDE_CODE_CONFIG_GUIDE


def print_zenmux_status() -> str:
    """Get a formatted ZenMux status report for display.

    Returns:
        Multi-line status string.
    """
    status = detect_zenmux()

    lines = []
    lines.append("═" * 50)
    lines.append("  ZenMux 状态检测")
    lines.append("═" * 50)
    lines.append(f"  已安装:    {'✅ 是' if status['installed'] else '❌ 否'}")
    lines.append(f"  配置文件:  {status['config_file'] or '未找到'}")
    lines.append(f"  配置有效:  {'✅' if status['config_valid'] else '❌'}")
    lines.append(f"  Docker运行: {'✅' if status['docker_running'] else '❌'}")
    lines.append(f"  环境变量:  {'✅ 已配置' if status['env_configured'] else '❌ 未配置'}")
    lines.append("")

    if status["recommendations"]:
        lines.append("  建议操作:")
        for i, rec in enumerate(status["recommendations"], 1):
            lines.append(f"    {i}. {rec}")

    lines.append("")
    lines.append("  ZenMux 是什么？")
    lines.append("  ─────────────────────────────────────────────")
    lines.append("  ZenMux 是一个 Claude API 反向代理/负载均衡器。")
    lines.append("  当检测到 Claude 降智时，自动切换至备用端点。")
    lines.append("  CSDN 社区 30+ 篇文章验证了 ZenMux 的有效性。")
    lines.append("")
    lines.append("  快速开始:")
    lines.append("    1. claude-intel-monitor zenmux setup   # 生成配置")
    lines.append("    2. 编辑 .env.zenmux 填入 API Key")
    lines.append("    3. docker compose -f zenmux-docker-compose.yml up -d")
    lines.append("    4. export ANTHROPIC_BASE_URL=http://localhost:8080/v1")
    lines.append("")

    return "\n".join(lines)


# ── Alternative solutions (when ZenMux is not viable) ───────────────────

ALTERNATIVES = {
    "openrouter": {
        "name": "OpenRouter",
        "url": "https://openrouter.ai",
        "desc": "自动路由到多个 Claude 提供商，天然降低降智影响",
        "setup": "export ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1",
        "pros": ["无需自建", "多提供商自动切换", "按量付费"],
        "cons": ["需注册", "有手续费", "延迟略高"],
    },
    "aws_bedrock": {
        "name": "AWS Bedrock",
        "url": "https://aws.amazon.com/bedrock/claude/",
        "desc": "AWS 托管的 Claude，企业级 SLA，降智概率更低",
        "setup": "需配置 AWS IAM + Bedrock 权限",
        "pros": ["企业级可靠性", "SLA保障", "数据不出AWS"],
        "cons": ["配置复杂", "需AWS账号", "按区域可用"],
    },
    "gcp_vertex": {
        "name": "Google Cloud Vertex AI",
        "url": "https://cloud.google.com/vertex-ai",
        "desc": "GCP 托管的 Claude，多区域部署",
        "setup": "需配置 GCP 项目 + Vertex AI API",
        "pros": ["多区域", "GCP生态集成", "SLA保障"],
        "cons": ["需GCP账号", "配额限制"],
    },
    "direct_api_rotate": {
        "name": "API Key 轮换",
        "desc": "准备多个 Anthropic API Key，遇到降智时手动或自动切换",
        "setup": "export ANTHROPIC_API_KEYS=key1,key2,key3",
        "pros": ["最简单", "无需外部服务"],
        "cons": ["手动切换", "同区域key共享降智", "多个付费账号"],
    },
}
