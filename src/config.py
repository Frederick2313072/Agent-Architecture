"""
配置管理模块
处理环境变量、API密钥和系统设置
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 加载环境变量
# 首先尝试加载.env文件，如果不存在也不报错
load_dotenv(override=False)  # 不覆盖已存在的环境变量

class LLMConfig(BaseModel):
    """LLM 配置"""
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    default_model: str = Field(default="gpt-4o")
    backup_model: str = Field(default="claude-3-haiku-20240307")
    request_timeout: int = Field(default=300)

class SecurityConfig(BaseModel):
    """安全配置"""
    enable_content_moderation: bool = Field(default=True)
    moderation_threshold: float = Field(default=0.7)
    max_retry_attempts: int = Field(default=3)

class ObservabilityConfig(BaseModel):
    """可观测性配置"""
    phoenix_port: int = Field(default=6006)
    otel_endpoint: str = Field(default="http://localhost:4317")
    otel_fallback_port: int = Field(default=4318)
    enable_tracing: bool = Field(default=True)
    enable_grpc_fallback: bool = Field(default=True)
    
    def __init__(self, **data):
        super().__init__(**data)
        # 支持标准 OTEL 环境变量
        if hasattr(os, 'environ') and 'OTEL_EXPORTER_OTLP_ENDPOINT' in os.environ:
            self.otel_endpoint = os.environ['OTEL_EXPORTER_OTLP_ENDPOINT']

class AgentConfig(BaseModel):
    """Agent 系统配置"""
    max_round: int = Field(default=10)
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

class AppConfig(BaseModel):
    """应用总配置"""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)

# 全局配置实例
config = AppConfig()

def validate_config() -> bool:
    """验证配置完整性"""
    if not config.llm.openai_api_key:
        raise ValueError("OPENAI_API_KEY 未设置")
    return True 