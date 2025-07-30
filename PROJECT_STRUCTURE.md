# 📁 Agent Workflow 项目结构

## 🎯 结构概览

本项目采用现代Python项目的标准目录结构，按功能模块清晰组织代码：

```
原型验证/
├── 📦 src/                        # 核心源代码包
├── 🧪 tests/                      # 测试套件
├── 🛠️ scripts/                   # 工具脚本
├── 📚 docs/                       # 项目文档
├── 📊 data/                       # 数据文件
├── ⚙️ config/                     # 配置模板
├── 🚀 main.py                     # 主入口文件
├── 📦 setup.py                    # 项目安装配置
└── 📋 requirements.txt            # Python依赖
```

## 📦 src/ - 核心源代码

```
src/
├── __init__.py                    # 包初始化，定义公共API
├── config.py                      # 配置管理（环境变量、验证）
├── observability.py              # 可观测性（OpenTelemetry + Phoenix）
├── safety.py                     # 安全机制（内容审核、输出验证）
├── agents.py                     # AutoGen Agent实现
└── demo.py                       # 演示功能入口
```

**职责说明**：
- `config.py`: 统一管理所有配置项，支持环境变量和默认值
- `observability.py`: 实现完整的追踪和监控体系
- `safety.py`: 多层次内容安全和数据验证
- `agents.py`: 核心的Agent协作逻辑
- `demo.py`: 用户友好的演示界面

## 🧪 tests/ - 测试套件

```
tests/
├── __init__.py                    # 测试包初始化
├── test_openinference.py         # OpenInference追踪功能测试
├── test_grpc_fallback.py         # GRPC端口冲突处理测试
├── test_demo.py                  # 演示功能集成测试
├── debug_agent.py                # Agent调试工具
└── simple_test.py                # 基础功能快速测试
```

**测试策略**：
- 单元测试：验证各模块独立功能
- 集成测试：验证系统协作效果
- 调试工具：提供问题排查能力

## 🛠️ scripts/ - 工具脚本

```
scripts/
├── check_env.py                  # 环境配置检查工具
├── check_phoenix.py              # Phoenix UI诊断工具
├── start_phoenix.py              # Phoenix独立启动器
└── complete_tracing_guide.py     # 完整追踪演示指南
```

**工具用途**：
- 环境诊断：快速发现配置问题
- 系统监控：独立的UI启动和检查
- 学习资源：完整的使用教程

## 📚 docs/ - 项目文档

```
docs/
├── Agent_Workflow_实验报告.md     # 完整实验报告
├── TRACING_TUTORIAL.md           # 追踪功能详细教程
└── FIXING_INPUT_OUTPUT_DISPLAY.md # 常见问题解决方案
```

**文档类型**：
- 实验报告：系统性能和效果分析
- 教程指南：功能使用说明
- 故障排查：问题诊断和解决

## 📊 data/ - 数据文件

```
data/
└── Dataset_*.csv                 # Phoenix导出的追踪数据
```

**数据管理**：
- 追踪数据：系统运行的详细记录
- 实验结果：用于性能分析和优化

## ⚙️ config/ - 配置模板

```
config/
├── env_template.txt              # 环境变量配置模板
└── sample_queries.json           # 示例查询集合
```

**配置管理**：
- 模板文件：标准化配置格式
- 示例数据：快速上手参考

## 🚀 项目入口文件

### main.py - 主入口
- 用户友好的统一入口
- 自动处理模块路径
- 支持所有演示功能

### setup.py - 安装配置
- 标准Python包配置
- 依赖管理
- 开发环境安装支持

## 📋 使用方式对比

### ✅ 推荐方式（新结构）

```bash
# 主要功能
python main.py run-demo "您的查询"

# 环境检查
python scripts/check_env.py

# 功能测试
python tests/simple_test.py

# UI启动
python scripts/start_phoenix.py
```

### ❌ 旧方式（已废弃）

```bash
# 不再推荐
python demo.py run-demo "您的查询"
python check_env.py
python simple_test.py
python start_phoenix.py
```

## 🔄 迁移完成状态

### ✅ 已完成
- [x] 创建标准目录结构
- [x] 移动所有源代码文件
- [x] 更新所有导入路径
- [x] 创建包初始化文件
- [x] 更新README文档
- [x] 创建主入口文件
- [x] 配置项目安装

### 📈 项目结构优势

1. **标准化**：符合Python项目最佳实践
2. **模块化**：清晰的功能分离和职责划分
3. **可维护性**：便于代码导航和维护
4. **可扩展性**：易于添加新功能和测试
5. **专业性**：适合生产环境部署和团队协作

这个新的项目结构使代码更加专业、易于维护，并为后续的功能扩展和团队协作奠定了良好基础。 