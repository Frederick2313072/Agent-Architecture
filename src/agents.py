"""
AutoGen Agent 系统
实现对话驱动的多Agent协作架构
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Callable
import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import json
import logging
from .config import config
from .observability import traced_agent_operation, log_conversation
from .safety import output_validator, AgentOutput

logger = logging.getLogger(__name__)

class TrackedAssistantAgent(AssistantAgent):
    """带追踪功能的 AssistantAgent"""
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.conversation_history = []
    
    @traced_agent_operation("agent_generate_reply")
    def generate_reply(self, *args, **kwargs):
        """重写生成回复方法，添加追踪和验证"""
        
        # 处理参数 - 兼容不同的调用方式
        messages = None
        sender = None
        
        # 解析位置参数
        if len(args) >= 1:
            messages = args[0]
        if len(args) >= 2:
            sender = args[1]
        
        # 从关键字参数中获取
        if 'messages' in kwargs:
            messages = kwargs['messages']
        if 'sender' in kwargs:
            sender = kwargs['sender']
        
        # 记录输入
        try:
            if messages:
                if isinstance(messages, list) and messages:
                    last_message = messages[-1].get("content", "") if isinstance(messages[-1], dict) else str(messages[-1])
                else:
                    last_message = str(messages)
                
                log_conversation(
                    self.name,
                    f"收到消息: {last_message[:100]}...",
                    "user"
                )
        except Exception as e:
            logger.warning(f"记录输入消息时出错: {e}")
        
        # 调用父类方法生成回复
        try:
            # 使用原始参数调用父类方法
            reply = super().generate_reply(*args, **kwargs)
        except Exception as e:
            logger.error(f"调用父类generate_reply时出错: {e}")
            logger.error(f"参数: args={args}, kwargs={kwargs}")
            # 返回一个默认回复而不是抛出异常
            return "抱歉，我在处理您的请求时遇到了技术问题。"
        
        # 记录输出
        try:
            log_conversation(
                self.name,
                str(reply),
                "assistant",
                {"sender": sender.name if sender and hasattr(sender, 'name') else "unknown"}
            )
        except Exception as e:
            logger.warning(f"记录输出消息时出错: {e}")
        
        # 存储对话历史
        try:
            self.conversation_history.append({
                "role": "assistant",
                "content": str(reply),
                "timestamp": time.time()
            })
        except Exception as e:
            logger.warning(f"无法记录对话历史: {e}")
        
        return reply

class EnhancedGroupChatManager(GroupChatManager):
    """增强的群聊管理器，集成安全验证"""
    
    def __init__(self, groupchat: GroupChat, **kwargs):
        super().__init__(groupchat, **kwargs)
        self.round_count = 0
        self.validation_enabled = True
    
    @traced_agent_operation("group_chat_coordination")
    def run_chat(self, *args, **kwargs):
        """重写群聊执行方法，添加协调追踪"""
        
        self.round_count += 1
        log_conversation(
            "GroupChatManager",
            f"开始第 {self.round_count} 轮群聊协调",
            "system"
        )
        
        result = super().run_chat(*args, **kwargs)
        
        log_conversation(
            "GroupChatManager",
            f"第 {self.round_count} 轮群聊完成",
            "system"
        )
        
        return result

class MarketAnalysisTeam:
    """市场分析团队 - 展示 AutoGen 对话驱动架构"""
    
    def __init__(self):
        self.llm_config = self._build_llm_config()
        self.agents = {}
        self.group_chat = None
        self.manager = None
        self._setup_agents()
        self._setup_group_chat()
    
    def _build_llm_config(self) -> Dict[str, Any]:
        """构建 LLM 配置"""
        return {
            "config_list": [
                {
                    "model": config.llm.default_model,
                    "api_key": config.llm.openai_api_key,
                }
            ],
            "timeout": config.llm.request_timeout,
            "temperature": 0.1,
        }
    
    @traced_agent_operation("setup_agents")
    def _setup_agents(self):
        """设置专门化的 Agent"""
        
        # 1. 市场研究员 - 负责收集和分析市场数据
        self.agents["researcher"] = TrackedAssistantAgent(
            name="MarketResearcher",
            system_message="""你是一位专业的市场研究员，具有以下职责：

🔍 **核心能力：**
- 深度市场调研和数据分析
- 行业趋势识别和竞争对手分析  
- 消费者行为洞察

📊 **工作风格：**
- 数据驱动，客观理性
- 善于发现隐藏的市场机会
- 能够将复杂数据转化为清晰洞察

⚡ **协作模式：**
- 在讨论开始时主动提供市场背景
- 为其他团队成员提供数据支撑
- 质疑不准确的市场假设

请始终提供具体的数据和来源，避免泛泛而谈。""",
            llm_config=self.llm_config,
        )
        
        # 2. 战略分析师 - 负责战略规划和风险评估
        self.agents["analyst"] = TrackedAssistantAgent(
            name="StrategyAnalyst", 
            system_message="""你是一位资深的战略分析师，具有以下专长：

🎯 **核心能力：**
- 战略规划和商业模式设计
- 风险评估和机会分析
- 竞争策略制定

🧠 **分析框架：**
- SWOT、波特五力模型
- 价值链分析
- 情景规划和敏感性分析

🤝 **协作风格：**
- 基于研究员的数据提出战略建议
- 挑战假设，提出替代方案
- 关注实施可行性

请使用结构化的分析框架，提供可执行的战略建议。""",
            llm_config=self.llm_config,
        )
        
        # 3. 商业写作专家 - 负责整合信息并撰写报告
        self.agents["writer"] = TrackedAssistantAgent(
            name="BusinessWriter",
            system_message="""你是一位专业的商业写作专家，擅长：

✍️ **写作专长：**
- 将复杂分析转化为清晰的商业文档
- 创建引人注目的执行摘要
- 调整内容以适应不同的目标受众

📝 **文档标准：**
- 逻辑清晰，结构合理
- 关键点突出，易于理解
- 包含具体的行动建议

🎨 **协作角色：**
- 在讨论末期综合各方观点
- 确保最终输出的一致性和质量
- 根据反馈迭代改进

请确保最终输出为结构化的、可操作的商业文档。""",
            llm_config=self.llm_config,
        )
        
        # 4. 用户代理 - 代表用户参与对话
        self.agents["user_proxy"] = UserProxyAgent(
            name="ProjectManager",
            system_message="""你是项目经理，负责：
- 引导团队讨论方向
- 确保项目按时完成
- 协调团队成员的工作

你会在必要时介入对话，但主要让团队成员自主协作。""",
            human_input_mode="NEVER",  # 自动化执行
            max_consecutive_auto_reply=1,
            code_execution_config=False,
        )
    
    @traced_agent_operation("setup_group_chat")
    def _setup_group_chat(self):
        """设置群聊"""
        agent_list = list(self.agents.values())
        
        self.group_chat = GroupChat(
            agents=agent_list,
            messages=[],
            max_round=config.agent.max_round,
            speaker_selection_method="round_robin",  # 轮询模式确保每个Agent都参与
        )
        
        self.manager = EnhancedGroupChatManager(
            groupchat=self.group_chat,
            llm_config=self.llm_config,
        )
    
    @traced_agent_operation("market_analysis_workflow")
    async def analyze_market(self, query: str) -> Optional[AgentOutput]:
        """执行市场分析工作流"""
        
        log_conversation(
            "MarketAnalysisTeam",
            f"启动市场分析任务: {query}",
            "system"
        )
        
        try:
            # 构建初始提示，明确任务和协作期望
            initial_prompt = f"""
🎯 **市场分析任务**

**问题:** {query}

**团队协作流程:**
1. **MarketResearcher**: 首先提供相关的市场数据、趋势和竞争环境分析
2. **StrategyAnalyst**: 基于研究结果进行战略分析，识别机会和风险
3. **BusinessWriter**: 综合前两位的观点，撰写结构化的分析报告

**最终输出要求:**
- 执行摘要 (关键发现)
- 市场环境分析
- 战略建议
- 风险评估
- 下一步行动计划

请开始协作！
"""
            
            # 启动群聊
            result = self.agents["user_proxy"].initiate_chat(
                self.manager,
                message=initial_prompt,
                max_turns=config.agent.max_round
            )
            
            # 提取最后一个助手的回复作为最终结果
            final_message = ""
            try:
                if hasattr(result, 'chat_history') and result.chat_history:
                    final_message = result.chat_history[-1].get("content", "")
                elif isinstance(result, str):
                    final_message = result
                elif isinstance(result, dict) and "content" in result:
                    final_message = result["content"]
                
                if not final_message:
                    # 从群聊消息中获取最后的回复
                    if self.group_chat.messages:
                        last_msg = self.group_chat.messages[-1]
                        if isinstance(last_msg, dict):
                            final_message = last_msg.get("content", "")
                        else:
                            final_message = str(last_msg)
            except Exception as e:
                logger.error(f"提取最终消息时出错: {e}")
                final_message = "系统生成了回复，但提取时出现问题"
            
            # 验证和后处理输出
            if final_message:
                validated_output = await output_validator.validate_with_correction(
                    final_message,
                    "MarketAnalysisTeam",
                    correction_callback=self._correction_callback
                )
                return validated_output
            else:
                logger.error("群聊没有产生有效的最终结果")
                return None
                
        except Exception as e:
            logger.error(f"市场分析执行失败: {e}")
            return None
    
    async def _correction_callback(self, invalid_output: str, error_reason: str) -> str:
        """自修复回调函数"""
        correction_prompt = f"""
❌ **输出需要修正**

**错误原因:** {error_reason}

**当前输出:** {invalid_output[:500]}...

**修正要求:**
请BusinessWriter重新整理输出，确保：
1. 格式清晰，结构合理
2. 内容安全，符合商业标准
3. 包含具体的数据和建议

请提供修正后的版本：
"""
        
        try:
            # 让写作专家进行修正
            # 需要将prompt包装为消息格式
            messages = [{"role": "user", "content": correction_prompt}]
            corrected = self.agents["writer"].generate_reply(
                messages=messages,
                sender=None
            )
            return str(corrected) if corrected else invalid_output
        except Exception as e:
            logger.error(f"自修复失败: {e}")
            return invalid_output
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """获取对话摘要"""
        summary = {
            "total_rounds": self.manager.round_count if self.manager else 0,
            "participants": list(self.agents.keys()),
            "message_count": len(self.group_chat.messages) if self.group_chat else 0,
            "agent_contributions": {}
        }
        
        # 统计每个Agent的贡献
        for agent_name, agent in self.agents.items():
            if hasattr(agent, 'conversation_history'):
                summary["agent_contributions"][agent_name] = len(agent.conversation_history)
        
        return summary

# 工厂函数
def create_market_analysis_team() -> MarketAnalysisTeam:
    """创建市场分析团队实例"""
    team = MarketAnalysisTeam()
    log_conversation(
        "TeamFactory",
        "市场分析团队创建完成",
        "system"
    )
    return team 