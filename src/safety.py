"""
安全与验证模块
实现内容安全检查、输出验证和自修复机制
"""

import openai
import asyncio
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, ValidationError
from enum import Enum
import logging
from .config import config
from .observability import traced_agent_operation, log_conversation

logger = logging.getLogger(__name__)

class ModerationResult(BaseModel):
    """内容审核结果"""
    flagged: bool
    categories: Dict[str, bool]
    category_scores: Dict[str, float]
    reason: Optional[str] = None

class ValidationStatus(str, Enum):
    """验证状态"""
    VALID = "valid"
    INVALID = "invalid"
    RETRY_NEEDED = "retry_needed"
    BLOCKED = "blocked"

class AgentOutput(BaseModel):
    """标准化的 Agent 输出格式"""
    content: str = Field(description="主要内容")
    agent_name: str = Field(description="生成内容的 Agent 名称")
    confidence: float = Field(ge=0.0, le=1.0, description="内容可信度评分")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="附加元数据")
    sources: List[str] = Field(default_factory=list, description="信息来源")

class SafetyManager:
    """安全管理器"""
    
    def __init__(self):
        self.moderation_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """初始化外部服务客户端"""
        if config.llm.openai_api_key:
            self.moderation_client = openai.OpenAI(api_key=config.llm.openai_api_key)
    
    @traced_agent_operation("content_moderation")
    async def moderate_content(self, content: str) -> ModerationResult:
        """使用 OpenAI Moderation API 检查内容安全性"""
        if not config.security.enable_content_moderation or not self.moderation_client:
            return ModerationResult(
                flagged=False,
                categories={},
                category_scores={}
            )
        
        try:
            response = self.moderation_client.moderations.create(input=content)
            result = response.results[0]
            
            # 检查是否超过阈值
            flagged = result.flagged
            max_score = max(result.category_scores.model_dump().values()) if result.category_scores else 0
            
            if max_score > config.security.moderation_threshold:
                flagged = True
            
            # 找出触发的类别
            reason = None
            if flagged:
                triggered_categories = [
                    category for category, flagged_status in result.categories.model_dump().items()
                    if flagged_status or result.category_scores.model_dump().get(category, 0) > config.security.moderation_threshold
                ]
                reason = f"触发类别: {', '.join(triggered_categories)}"
            
            return ModerationResult(
                flagged=flagged,
                categories=result.categories.model_dump(),
                category_scores=result.category_scores.model_dump(),
                reason=reason
            )
        
        except Exception as e:
            logger.error(f"内容审核失败: {e}")
            # 在审核服务不可用时，采用保守策略
            return ModerationResult(
                flagged=False,
                categories={},
                category_scores={},
                reason=f"审核服务异常: {str(e)}"
            )
    
    @traced_agent_operation("output_validation")
    def validate_agent_output(self, raw_output: str, agent_name: str) -> tuple[ValidationStatus, Optional[AgentOutput]]:
        """验证 Agent 输出格式和内容"""
        try:
            # 尝试解析为结构化格式
            if self._is_json_like(raw_output):
                return self._validate_json_output(raw_output, agent_name)
            else:
                return self._validate_text_output(raw_output, agent_name)
        
        except Exception as e:
            logger.error(f"输出验证异常: {e}")
            return ValidationStatus.INVALID, None
    
    def _is_json_like(self, content: str) -> bool:
        """简单检查内容是否类似 JSON"""
        stripped = content.strip()
        return stripped.startswith('{') and stripped.endswith('}')
    
    def _validate_json_output(self, content: str, agent_name: str) -> tuple[ValidationStatus, Optional[AgentOutput]]:
        """验证 JSON 格式的输出"""
        try:
            import json
            data = json.loads(content)
            
            # 尝试构建 AgentOutput
            output = AgentOutput(
                content=data.get('content', content),
                agent_name=agent_name,
                confidence=data.get('confidence', 0.8),
                metadata=data.get('metadata', {}),
                sources=data.get('sources', [])
            )
            return ValidationStatus.VALID, output
        
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning(f"JSON 输出验证失败: {e}")
            return ValidationStatus.RETRY_NEEDED, None
    
    def _validate_text_output(self, content: str, agent_name: str) -> tuple[ValidationStatus, Optional[AgentOutput]]:
        """验证文本格式的输出"""
        # 基本长度检查
        if len(content.strip()) < 10:
            return ValidationStatus.INVALID, None
        
        # 基本质量检查
        confidence = self._assess_content_quality(content)
        
        output = AgentOutput(
            content=content.strip(),
            agent_name=agent_name,
            confidence=confidence,
            metadata={"format": "text", "length": len(content)},
            sources=[]
        )
        
        return ValidationStatus.VALID, output
    
    def _assess_content_quality(self, content: str) -> float:
        """简单的内容质量评估"""
        score = 0.5  # 基础分
        
        # 长度合理性
        if 50 <= len(content) <= 2000:
            score += 0.2
        
        # 包含标点符号
        if any(punct in content for punct in '。！？.,!?'):
            score += 0.1
        
        # 避免重复内容
        words = content.split()
        if len(set(words)) / len(words) > 0.7:  # 词汇多样性
            score += 0.2
        
        return min(score, 1.0)

class OutputValidator:
    """输出验证器 - 实现自修复循环"""
    
    def __init__(self, safety_manager: SafetyManager):
        self.safety_manager = safety_manager
    
    @traced_agent_operation("self_correction_loop")
    async def validate_with_correction(self, 
                                     raw_output: str, 
                                     agent_name: str,
                                     correction_callback=None) -> Optional[AgentOutput]:
        """带自修复的验证循环"""
        
        for attempt in range(config.security.max_retry_attempts):
            log_conversation(
                "Validator", 
                f"正在验证 {agent_name} 的输出 (尝试 {attempt + 1}/{config.security.max_retry_attempts})",
                "system"
            )
            
            # 1. 内容安全检查
            moderation_result = await self.safety_manager.moderate_content(raw_output)
            if moderation_result.flagged:
                logger.warning(f"内容被标记为不安全: {moderation_result.reason}")
                if attempt == config.security.max_retry_attempts - 1:
                    return None  # 最后一次尝试仍然不安全，放弃
                
                # 请求修正
                if correction_callback:
                    raw_output = await correction_callback(
                        raw_output, 
                        f"内容安全检查失败: {moderation_result.reason}"
                    )
                    continue
                else:
                    return None
            
            # 2. 格式和质量验证
            status, validated_output = self.safety_manager.validate_agent_output(raw_output, agent_name)
            
            if status == ValidationStatus.VALID:
                log_conversation(
                    "Validator", 
                    f"✅ {agent_name} 输出验证通过",
                    "system"
                )
                return validated_output
            
            elif status == ValidationStatus.RETRY_NEEDED:
                logger.warning(f"输出格式需要修正 (尝试 {attempt + 1})")
                if correction_callback and attempt < config.security.max_retry_attempts - 1:
                    raw_output = await correction_callback(
                        raw_output, 
                        "输出格式不符合要求，请重新生成结构化内容"
                    )
                    continue
            
            # 验证失败
            if attempt == config.security.max_retry_attempts - 1:
                logger.error(f"❌ {agent_name} 输出验证最终失败")
                return None
        
        return None

# 全局实例
safety_manager = SafetyManager()
output_validator = OutputValidator(safety_manager) 