# AutoGen Agent Workflow Demo

> 📋 **完整实验报告请查看**: [`agent-architecture.md`](./agent- architecture.md)

> 🤖 **对话驱动的生产级多Agent协作系统**  
> 基于AutoGen框架，集成OpenTelemetry可观测性和多层安全机制

## ✨ 核心特性

- 🎯 **对话驱动架构**：通过结构化对话实现多Agent协作
- 📊 **全方位可观测性**：OpenTelemetry + Phoenix追踪每个Agent交互
- 🛡️ **多层安全防护**：内容审核、输出验证、自修复机制
- ⚡ **生产级设计**：配置管理、错误处理、性能监控

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd autogen-workflow

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

**方法1：使用 .env 文件（推荐）**

```bash
# 1. 复制环境配置模板文件
cp env_template.txt .env

# 2. 编辑 .env 文件，填入您的实际API密钥
nano .env  # 或使用您喜欢的编辑器

# 3. 修改以下必需配置：
# OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# 4. 其他配置项有默认值，可选修改：
# DEFAULT_MODEL=gpt-4o
# ENABLE_CONTENT_MODERATION=true
# PHOENIX_PORT=6006
```

**方法2：使用环境变量**

```bash
# 设置环境变量
export OPENAI_API_KEY="your_openai_api_key_here"

# 可选：Anthropic API（用于备用模型）
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
```

### 3. 运行演示

```bash
# 第一步：检查.env配置
python scripts/check_env.py

# 第二步：测试基础AutoGen功能
python tests/simple_test.py

# 第三步：Agent专项调试（如果上一步有问题）
python tests/debug_agent.py

# 第四步：完整系统检查
python main.py run-demo --check-config "测试查询"

# 如果配置正确，运行基础市场分析演示
python main.py run-demo "分析中国电动汽车市场的发展趋势和投资机会"

# 批量处理演示
python main.py batch-demo config/sample_queries.json --output-file results.json
```

> 💡 **提示**: 如果遇到API密钥问题，运行 `python scripts/check_env.py` 检查配置

**完整的快速开始流程**：
```bash
# 1. 配置环境
cp config/env_template.txt .env && nano .env

# 2. 检查配置
python scripts/check_env.py

# 3. 基础功能测试
python tests/simple_test.py

# 4. Agent专项调试（如果遇到问题）
python tests/debug_agent.py

# 5. Phoenix UI 诊断（如果无法访问可观测性界面）
python scripts/check_phoenix.py

# 6. 运行完整演示
python main.py run-demo "分析中国电动汽车市场发展趋势"
```

## 📁 项目结构

```
原型验证/
├── src/                           # 核心源代码
│   ├── __init__.py               # 包初始化文件
│   ├── config.py                 # 配置管理
│   ├── observability.py         # 可观测性（OpenTelemetry + Phoenix）
│   ├── safety.py                 # 安全机制（内容审核、输出验证）
│   ├── agents.py                 # AutoGen Agent实现
│   └── demo.py                   # 演示入口
├── tests/                        # 测试套件
│   ├── __init__.py               # 测试包初始化
│   ├── test_openinference.py     # OpenInference追踪测试
│   ├── test_grpc_fallback.py     # GRPC端口冲突测试
│   ├── test_demo.py              # 演示功能测试
│   ├── debug_agent.py            # Agent调试工具
│   └── simple_test.py            # 简单功能测试
├── scripts/                      # 工具脚本
│   ├── check_env.py              # 环境检查工具
│   ├── check_phoenix.py          # Phoenix UI诊断
│   ├── start_phoenix.py          # Phoenix独立启动器
│   └── complete_tracing_guide.py # 完整追踪指南
├── docs/                         # 项目文档
│   ├── Agent_Workflow_实验报告.md  # 完整实验报告
│   ├── TRACING_TUTORIAL.md       # 追踪教程
│   └── FIXING_INPUT_OUTPUT_DISPLAY.md # 故障排查
├── data/                         # 数据文件
│   └── Dataset*.csv             # Phoenix导出的追踪数据
├── config/                       # 配置模板
│   ├── env_template.txt          # 环境变量模板
│   └── sample_queries.json       # 示例查询
├── main.py                       # 主入口文件
├── setup.py                      # 项目安装配置
├── requirements.txt              # Python依赖
└── README.md                     # 项目说明
```

### 🚀 运行方式

```bash
# 方式1：直接运行主入口（推荐）
python main.py run-demo "您的查询"

# 方式2：模块化运行
python -m src.demo run-demo "您的查询"

# 方式3：安装后使用（开发环境）
pip install -e .
agent-workflow run-demo "您的查询"

# 方式4：运行特定脚本
python scripts/check_env.py              # 环境检查
python scripts/start_phoenix.py          # 启动Phoenix UI
python tests/test_openinference.py       # 测试追踪功能
```

## 📖 使用指南

### 环境配置详解

**.env 文件配置**

```bash
# 1. 创建配置文件
cp config/env_template.txt .env

# 2. 编辑配置（使用您喜欢的编辑器）
nano .env   # 或 vim .env 或 code .env

# 3. 验证配置（两种方式）
python scripts/check_env.py                   # 快速检查工具
# 或
python main.py run-demo --check-config "验证" # 完整系统检查
```

**必需配置项**
- `OPENAI_API_KEY`: OpenAI API密钥（必需）

**可选配置项**
- `DEFAULT_MODEL`: 默认LLM模型（默认: gpt-4o）
- `ENABLE_CONTENT_MODERATION`: 是否启用内容审核（默认: true）
- `PHOENIX_PORT`: Phoenix UI端口（默认: 6006）

### 基础使用

```python
import asyncio
from agents import create_market_analysis_team
from observability import observability
from config import validate_config

async def main():
    # 1. 验证配置
    validate_config()
    
    # 2. 初始化可观测性
    observability.initialize()
    
    # 3. 创建Agent团队
    team = create_market_analysis_team()
    
    # 4. 执行分析
    result = await team.analyze_market("您的市场分析问题")
    
    if result:
        print(f"分析结果: {result.content}")
        print(f"可信度: {result.confidence:.2f}")

# 运行
asyncio.run(main())
```

### 高级配置

```python
# config.py 中的配置选项
from config import config

# 修改LLM设置
config.llm.default_model = "gpt-4o"
config.llm.request_timeout = 300

# 调整安全设置
config.security.enable_content_moderation = True
config.security.moderation_threshold = 0.7

# 可观测性设置
config.observability.enable_tracing = True
config.observability.phoenix_port = 6006
```

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    Demo演示层                                │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   CLI界面       │  │   批量处理      │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Agent协作层                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ 市场研究员  │ │ 战略分析师  │ │ 商业写作专家│           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│              ┌─────────────────────┐                       │
│              │   群聊管理器        │                       │
│              └─────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   基础设施层                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ 可观测性    │ │ 安全验证    │ │ 配置管理    │           │
│  │ (Phoenix)   │ │ (Pydantic)  │ │ (Config)    │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 使用场景

### 1. 市场分析
```bash
python main.py run-demo "分析AI芯片行业的竞争格局和技术趋势"
```

### 2. 投资研究
```bash
python main.py run-demo "评估新能源汽车产业链的投资机会和风险"
```

### 3. 战略规划
```bash
python main.py run-demo "制定一家SaaS公司进入东南亚市场的策略"
```

## 📊 可观测性

### Phoenix UI 访问方式

**方式1: 集成启动** (随演示自动启动)
```bash
python main.py run-demo "您的查询"
# Phoenix UI 会自动启动在 http://localhost:6006
```

**方式2: 独立启动** (推荐)
```bash
# 终端1: 启动 Phoenix UI
python scripts/start_phoenix.py

# 终端2: 运行演示
python main.py run-demo "您的查询"

# 浏览器访问: http://localhost:6006
```

**方式3: 故障排查**
```bash
# 如果无法访问，运行诊断工具
python check_phoenix.py
```

### 追踪数据内容

- **Agent 对话流程**: 完整的多Agent协作过程
- **LLM API 调用**: 详细的请求/响应和Token消耗  
- **性能指标**: 响应时间、成功率、错误统计
- **系统状态**: 实时监控和历史趋势

### 追踪数据详情

- **对话链路**: Agent间完整的信息传递
- **API调用**: 每次LLM请求的输入输出
- **安全检查**: 内容审核和验证结果
- **性能数据**: 延迟、吞吐量、成本分析
- **错误诊断**: 异常堆栈和故障恢复过程

## 🛡️ 安全机制

### 多层防护
1. **输入过滤**: OpenAI Moderation API检查用户输入
2. **输出验证**: Pydantic模型强制验证输出格式
3. **自修复循环**: 验证失败时自动重试和修正
4. **人机协同**: 关键决策点可接入人工审核

### 配置安全阈值
```python
# 调整内容审核敏感度
config.security.moderation_threshold = 0.7  # 0.0-1.0

# 设置最大重试次数
config.security.max_retry_attempts = 3
```

## 🔧 开发指南

### 添加新的Agent角色

```python
# 在agents.py中扩展
def add_technical_expert(team):
    expert = TrackedAssistantAgent(
        name="TechnicalExpert",
        system_message="""你是技术专家，专注于：
        - 技术可行性分析
        - 架构设计建议
        - 技术风险评估
        """,
        llm_config=team.llm_config
    )
    team.agents["technical"] = expert
    return expert
```

### 自定义验证规则

```python
# 在safety.py中扩展
class CustomOutput(BaseModel):
    title: str = Field(description="报告标题")
    summary: str = Field(description="执行摘要")
    recommendations: List[str] = Field(description="建议列表")
    confidence_score: float = Field(ge=0.0, le=1.0)
```

### 添加新的监控指标

```python
# 在observability.py中扩展
@traced_agent_operation("custom_operation")
def my_custom_function():
    with observability.create_span("custom_span") as span:
        span.set_attribute("custom.metric", "value")
        # 业务逻辑
```

## 📈 性能优化

### 配置优化建议
- **并发控制**: 调整max_round减少无效轮次
- **模型选择**: 使用cost-effective模型降低成本
- **缓存策略**: 考虑为重复查询添加缓存

### 监控关键指标
- **响应时间**: 目标<90秒（3-Agent场景）
- **Token效率**: 监控Token/质量比率
- **成功率**: 目标>95%验证通过率

## 🧪 测试与故障排查

### 分层测试方法

我们提供了三个层次的测试工具，按复杂度递增：

#### 1. 环境配置检查
```bash
python check_env.py
```
- ✅ 检查 `.env` 文件是否存在
- ✅ 验证 API 密钥格式
- ✅ 显示所有配置项状态

#### 2. 基础功能测试
```bash
python simple_test.py
```
- ✅ 测试 AutoGen 库导入
- ✅ 验证简单 Agent 对话
- ✅ 确认 API 连接正常

#### 2.5. Agent 专项调试
```bash
python debug_agent.py
```
- ✅ 测试 TrackedAssistantAgent 方法调用
- ✅ 验证不同参数传递方式
- ✅ 模拟 AutoGen 内部调用模式

#### 2.6. Phoenix UI 诊断
```bash
python check_phoenix.py
```
- ✅ 检查 Phoenix 库安装状态
- ✅ 诊断 Phoenix UI 和 GRPC 端口占用问题
- ✅ 测试 UI 启动和连接
- ✅ 提供自动化解决方案

#### 2.7. GRPC 端口冲突测试
```bash
python tests/test_grpc_fallback.py
```
- ✅ 模拟 GRPC 端口冲突场景
- ✅ 测试备用端口机制
- ✅ 验证系统健壮性
- ✅ 提供冲突解决方案

#### 3. 完整系统测试
```bash
python tests/test_demo.py         # 渐进式功能测试
# 或
python main.py run-demo --check-config "test"  # 集成测试
```
- ✅ 测试多 Agent 协作
- ✅ 验证可观测性系统
- ✅ 检查安全验证机制

### 常见问题解决

#### 1. **API密钥相关问题**

**错误信息**: `HTTP/1.1 401 Unauthorized` 或 `Incorrect API key provided`

**诊断流程**:
```bash
# 1. 检查配置格式
python check_env.py

# 2. 测试 API 连接
python simple_test.py

# 3. 如果显示 401 错误，说明密钥无效
```

**解决方案**:
1. **获取新的有效密钥**:
   - 访问: https://platform.openai.com/api-keys
   - 点击 "Create new secret key"
   - 复制完整密钥（sk-... 或 sk-proj-...）

2. **更新 .env 文件**:
   ```bash
   # 编辑 .env 文件
   nano .env
   
   # 更新为您的新密钥
   OPENAI_API_KEY=sk-proj-your-new-key-here
   ```

3. **验证修复**:
   ```bash
   python simple_test.py
   ```

**常见原因：**
- API 密钥已过期或被删除
- 账户余额不足
- 密钥权限设置错误
- 复制密钥时遗漏字符

#### 2. **AutoGen 兼容性问题**
```bash
# 专项调试工具
python debug_agent.py

# 检查 AutoGen 版本
pip show pyautogen

# 重新安装最新版本
pip install -U pyautogen autogen-agentchat
```

**常见错误：**
- `generate_reply() missing 1 required positional argument: 'messages'`
- `ConversableAgent.generate_reply() takes from 1 to 3 positional arguments but 4 were given`

**解决方案：**
- 运行 `debug_agent.py` 进行详细诊断
- 检查参数传递方式是否正确
- 确认 AutoGen 版本兼容性

#### 3. **Phoenix 可观测性问题**

**错误现象**: 无法访问 `http://localhost:6006`

**专项诊断工具**:
```bash
# Phoenix 专项诊断（推荐）
python check_phoenix.py
```

**手动诊断**:
```bash
# 检查端口占用
lsof -i :6006

# 使用不同端口
export PHOENIX_PORT=6007
python main.py run-demo "test"

# 手动启动 Phoenix
PHOENIX_PORT=6007 python -c "import phoenix as px; px.launch_app()"
```

**快速解决方案**:
- **Phoenix UI 端口被占用**: 使用 `export PHOENIX_PORT=6007`
- **GRPC 端口冲突**: 使用 `export OTEL_FALLBACK_PORT=4318`
- **Phoenix 未安装**: 运行 `pip install -U arize-phoenix`
- **独立启动 UI**: 运行 `python scripts/start_phoenix.py`
- **看到警告**: 查看 `PHOENIX_UPGRADE_NOTES.md`
- **不需要 UI**: 设置 `export ENABLE_TRACING=false`

#### 4. **GRPC/OTLP 端口冲突问题**

**错误信息**: `RuntimeError: Failed to bind to address [::]:4317`

**原因**: OpenTelemetry GRPC 端口 4317 被其他服务占用

**诊断方法**:
```bash
# 检查端口占用情况
lsof -i :4317

# 使用 Phoenix 诊断工具（推荐）
python check_phoenix.py
```

**解决方案**:

**方案 1: 使用备用端口**
```bash
export OTEL_FALLBACK_PORT=4318
export ENABLE_GRPC_FALLBACK=true
python main.py run-demo "test"
```

**方案 2: 禁用 OTLP 导出**
```bash
export ENABLE_GRPC_FALLBACK=false
python main.py run-demo "test"
```

**方案 3: 停止占用端口的服务**
```bash
# 查找占用进程
lsof -i :4317
# 停止相关服务（如 Docker、其他监控工具等）
```

**说明**: 
- ✅ GRPC 端口冲突不会影响 Phoenix UI 的使用
- ✅ 系统会自动尝试备用端口 4318
- ✅ 即使 GRPC 导出失败，本地追踪仍然正常工作

#### 5. **Agent 响应缓慢**
```bash
# 使用更快的模型进行测试
export DEFAULT_MODEL=gpt-3.5-turbo
python simple_test.py
```

**优化建议：**
- 使用 `gpt-3.5-turbo` 进行开发测试
- 调整 `REQUEST_TIMEOUT` 配置
- 检查网络连接和 API 服务状态

### 调试模式
```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
python main.py run-demo "your query"
```

## 📝 许可证

本项目基于 MIT 许可证开源。

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建特性分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 提交Pull Request

## 📞 支持与反馈

- **技术问题**: 提交GitHub Issue
- **功能建议**: 创建Feature Request
- **技术讨论**: 查看项目Wiki

---

> 💡 **提示**: 这个项目展示了如何将AutoGen的对话驱动理念工程化为生产级系统。通过完整的可观测性和安全机制，为构建可靠的多Agent应用提供了最佳实践参考。 