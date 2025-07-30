"""
可观测性模块
集成 OpenTelemetry 和 Arize Phoenix 实现全方位追踪
"""

import logging
import phoenix as px
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.anthropic import AnthropicInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from typing import Dict, Any, Optional
import functools
import time
from .config import config

# 设置日志
logging.basicConfig(level=getattr(logging, config.agent.log_level))
logger = logging.getLogger(__name__)

class ObservabilityManager:
    """可观测性管理器"""
    
    def __init__(self):
        self.tracer = None
        self.phoenix_session = None
        self._initialized = False
    
    def initialize(self) -> None:
        """初始化可观测性系统"""
        if self._initialized:
            return
            
        try:
            # 1. 启动 Phoenix 本地服务器
            self._start_phoenix()
            
            # 2. 配置 OpenTelemetry
            self._setup_opentelemetry()
            
            # 3. 启用自动化 instrumentation
            self._enable_auto_instrumentation()
            
            self._initialized = True
            logger.info("✅ 可观测性系统初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 可观测性系统初始化失败: {e}")
            raise
    
    def _start_phoenix(self) -> None:
        """启动 Phoenix 可视化界面"""
        if not config.observability.enable_tracing:
            return
            
        try:
            # 设置环境变量（新的推荐方式）
            import os
            os.environ["PHOENIX_PORT"] = str(config.observability.phoenix_port)
            os.environ["PHOENIX_HOST"] = "localhost"
            
            # 启动 Phoenix 会话（使用新的无参数方式）
            self.phoenix_session = px.launch_app()
            logger.info(f"🚀 Phoenix UI 已启动: http://localhost:{config.observability.phoenix_port}")
        except Exception as e:
            logger.warning(f"Phoenix 启动失败，将使用备用追踪: {e}")
    
    def _setup_opentelemetry(self) -> None:
        """配置 OpenTelemetry 追踪"""
        # 创建资源标识
        resource = Resource.create({
            ResourceAttributes.SERVICE_NAME: "autogen-agent-workflow",
            ResourceAttributes.SERVICE_VERSION: "1.0.0",
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT: "development"
        })
        
        # 配置 Tracer Provider
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)
        
        # 尝试配置 OTLP 导出器，带端口冲突处理
        otlp_exporter = self._create_otlp_exporter()
        if otlp_exporter:
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor)
            logger.info("✅ OTLP 导出器配置成功")
        else:
            logger.warning("⚠️ OTLP 导出器配置失败，仅使用本地追踪")
        
        # 获取 tracer
        self.tracer = trace.get_tracer(__name__)
    
    def _create_otlp_exporter(self) -> Optional[OTLPSpanExporter]:
        """创建 OTLP 导出器，处理端口冲突"""
        if not config.observability.enable_tracing:
            return None
            
        # 尝试主端口
        try:
            exporter = OTLPSpanExporter(endpoint=config.observability.otel_endpoint)
            logger.info(f"✅ OTLP 导出器已连接: {config.observability.otel_endpoint}")
            return exporter
        except Exception as e:
            logger.warning(f"⚠️ 主 OTLP 端点连接失败: {e}")
            
            # 尝试备用端口
            if config.observability.enable_grpc_fallback:
                try:
                    fallback_endpoint = f"http://localhost:{config.observability.otel_fallback_port}"
                    exporter = OTLPSpanExporter(endpoint=fallback_endpoint)
                    logger.info(f"✅ OTLP 导出器已连接备用端口: {fallback_endpoint}")
                    return exporter
                except Exception as e2:
                    logger.warning(f"⚠️ 备用 OTLP 端点连接失败: {e2}")
            
            # 所有端口都失败，返回 None
            logger.warning("❌ 所有 OTLP 端点都不可用，禁用 GRPC 导出")
            return None
    
    def _enable_auto_instrumentation(self) -> None:
        """启用自动化 instrumentation"""
        try:
            # OpenInference OpenAI 自动追踪 - 默认捕获所有内容
            OpenAIInstrumentor().instrument()
            logger.info("✅ OpenInference OpenAI instrumentation 已启用")
        except Exception as e:
            logger.warning(f"OpenInference OpenAI instrumentation 启用失败: {e}")
        
        try:
            # OpenInference Anthropic 自动追踪（如果可用）
            AnthropicInstrumentor().instrument()
            logger.info("✅ OpenInference Anthropic instrumentation 已启用")
        except Exception as e:
            logger.warning(f"OpenInference Anthropic instrumentation 启用失败: {e}")
    
    def trace_agent_operation(self, operation_name: str):
        """装饰器：追踪 Agent 操作"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self._initialized or not self.tracer:
                    return func(*args, **kwargs)
                
                with self.tracer.start_as_current_span(operation_name) as span:
                    start_time = time.time()
                    
                    # 记录输入参数
                    span.set_attribute("agent.operation", operation_name)
                    span.set_attribute("agent.args_count", len(args))
                    span.set_attribute("agent.kwargs_count", len(kwargs))
                    
                    # 尝试记录详细的输入信息（安全处理）
                    try:
                        # 对于特定的agent操作，记录更详细的信息
                        if operation_name == "agent_generate_reply":
                            if args and len(args) > 0:
                                # 尝试从args中提取messages
                                if hasattr(args[0], '__dict__'):
                                    span.set_attribute("agent.self_class", args[0].__class__.__name__)
                                if len(args) > 1:
                                    messages = args[1] if isinstance(args[1], list) else str(args[1])[:500]
                                    span.set_attribute("input.messages", str(messages)[:1000])
                            
                            # 记录kwargs中的信息
                            if "messages" in kwargs:
                                span.set_attribute("input.messages", str(kwargs["messages"])[:1000])
                            if "sender" in kwargs:
                                span.set_attribute("input.sender", str(kwargs.get("sender", ""))[:200])
                        
                        elif operation_name == "content_moderation":
                            if args and len(args) > 1:
                                content = str(args[1])[:500]  # 限制长度
                                span.set_attribute("input.content", content)
                        
                        elif operation_name == "output_validation":
                            if args and len(args) > 1:
                                output = str(args[1])[:500]
                                span.set_attribute("input.raw_output", output)
                    
                    except Exception as attr_e:
                        span.set_attribute("agent.input_capture_error", str(attr_e))
                    
                    try:
                        result = func(*args, **kwargs)
                        
                        # 记录成功状态和输出
                        span.set_attribute("agent.status", "success")
                        duration = time.time() - start_time
                        span.set_attribute("agent.duration_seconds", duration)
                        
                        # 尝试记录输出信息
                        try:
                            if result is not None:
                                result_str = str(result)[:1000]  # 限制长度
                                span.set_attribute("output.result", result_str)
                                span.set_attribute("output.type", type(result).__name__)
                        except Exception as output_e:
                            span.set_attribute("agent.output_capture_error", str(output_e))
                        
                        return result
                    
                    except Exception as e:
                        # 记录错误信息
                        span.set_attribute("agent.status", "error")
                        span.set_attribute("agent.error_type", type(e).__name__)
                        span.set_attribute("agent.error_message", str(e))
                        span.record_exception(e)
                        raise
            
            return wrapper
        return decorator
    
    def log_agent_conversation(self, 
                             agent_name: str, 
                             message: str, 
                             role: str = "assistant",
                             metadata: Optional[Dict[str, Any]] = None) -> None:
        """记录 Agent 对话"""
        if not self._initialized or not self.tracer:
            return
        
        with self.tracer.start_as_current_span("agent_conversation") as span:
            span.set_attribute("agent.name", agent_name)
            span.set_attribute("agent.role", role)
            span.set_attribute("agent.message_length", len(message))
            
            if metadata:
                for key, value in metadata.items():
                    span.set_attribute(f"agent.meta.{key}", str(value))
            
            # 在生产环境中，可能需要对敏感内容进行脱敏
            logger.info(f"[{agent_name}] {role}: {message[:200]}...")
    
    def create_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """创建自定义 span"""
        if not self._initialized or not self.tracer:
            return None
        
        span = self.tracer.start_span(name)
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        return span

# 全局可观测性管理器实例
observability = ObservabilityManager()

def traced_agent_operation(operation_name: str):
    """快捷装饰器：追踪 Agent 操作"""
    return observability.trace_agent_operation(operation_name)

def log_conversation(agent_name: str, message: str, role: str = "assistant", **metadata):
    """快捷函数：记录对话"""
    observability.log_agent_conversation(agent_name, message, role, metadata) 