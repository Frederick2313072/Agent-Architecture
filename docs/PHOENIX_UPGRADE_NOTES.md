# Phoenix UI 升级说明

## 已修复的问题

### 1. Phoenix API 弃用警告

如果您看到以下警告信息，不用担心 - 这些已经在最新代码中修复：

```
❗️ The launch_app `port` parameter is deprecated and will be removed in a future release. Use the `PHOENIX_PORT` environment variable instead.
❗️ The launch_app `host` parameter is deprecated and will be removed in a future release. Use the `PHOENIX_HOST` environment variable instead.
```

### 2. GRPC 端口冲突错误

如果您看到以下错误信息，系统现在会自动处理：

```
RuntimeError: Failed to bind to address [::]:4317; set GRPC_VERBOSITY=debug environment variable to see detailed error message.
```

**新增功能**:
- ✅ 自动检测 GRPC 端口冲突
- ✅ 自动尝试备用端口 (4318)
- ✅ 优雅降级到仅本地追踪
- ✅ 详细的诊断信息

## 新的推荐用法

### 1. 环境变量方式（推荐）

```bash
# 设置端口
export PHOENIX_PORT=6006
export PHOENIX_HOST=localhost

# 启动 Phoenix
python start_phoenix.py
```

### 2. 一次性设置

```bash
# 直接设置环境变量并启动
PHOENIX_PORT=6007 python start_phoenix.py
```

### 3. 手动启动

```bash
# 新的正确方式
PHOENIX_PORT=6007 python -c "import phoenix as px; px.launch_app()"

# 旧方式（会产生警告）- 不推荐
python -c "import phoenix as px; px.launch_app(port=6007)"
```

## 代码更新说明

我们已经更新了以下文件以使用新的API：

- `observability.py` - 主要可观测性模块
- `start_phoenix.py` - 独立Phoenix启动器
- `check_phoenix.py` - Phoenix诊断工具

## SQLAlchemy 警告

您可能还会看到一些SQLAlchemy相关的警告：

```
SAWarning: Skipped unsupported reflection of expression-based index...
```

这些警告：
- ✅ **不影响功能** - Phoenix UI 会正常工作
- ✅ **可以忽略** - 这是Phoenix内部数据库的技术细节
- ✅ **正在修复** - Phoenix团队正在处理这些警告

## 验证修复

运行以下命令验证所有问题已修复：

```bash
# 1. 测试Phoenix启动（应该无警告）
python start_phoenix.py

# 2. 运行完整诊断（包括GRPC端口检查）
python check_phoenix.py

# 3. 测试GRPC端口冲突处理
python test_grpc_fallback.py

# 4. 运行完整演示
python demo.py run-demo "测试查询"
```

## 如果仍有问题

1. **确保使用最新代码**: 重新拉取最新版本
2. **更新依赖**: `pip install -U arize-phoenix`
3. **清理环境**: 重启终端会话
4. **运行诊断**: `python check_phoenix.py`

---

**总结**: Phoenix UI 现在使用推荐的环境变量方式启动，不会再产生弃用警告。任何SQLAlchemy警告都可以安全忽略。 