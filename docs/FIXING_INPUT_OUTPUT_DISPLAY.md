# 🔧 修复 Phoenix UI Input/Output 显示问题

## 问题描述
Phoenix UI 中的 input 和 output 字段显示 "--" 而不是实际的 LLM 调用内容。

## 根本原因
系统使用的是标准 OpenTelemetry instrumentation，但 Phoenix 更好地支持 OpenInference instrumentation 来捕获详细的 LLM 调用内容。

## 🚀 完整修复步骤

### 步骤 1：更新依赖包
```bash
# 卸载旧的instrumentation包
pip uninstall opentelemetry-instrumentation-openai opentelemetry-instrumentation-anthropic -y

# 安装新的OpenInference instrumentation包
pip install openinference-instrumentation-openai>=0.1.12
pip install openinference-instrumentation-anthropic>=0.1.5  
pip install arize-phoenix>=4.0.0

# 或者直接使用requirements.txt
pip install -r requirements.txt
```

### 步骤 2：验证依赖安装
```bash
python3 test_openinference.py
```

### 步骤 3：测试修复效果
```bash
# 启动Phoenix UI（新终端）
python3 start_phoenix.py

# 运行测试（另一个终端）  
python3 demo.py run-demo "请简单说'测试成功'"
```

### 步骤 4：检查Phoenix UI
1. 访问 http://localhost:6006
2. 点击 "Traces" 标签
3. 查看最新的trace记录
4. 展开 `openai.chat` span
5. 确认 input 和 output 字段显示实际内容

## 🔍 验证要点

### ✅ 正常情况下应该看到：
- **input 字段**: 显示实际的消息内容（如：`[{"role": "user", "content": "请简单说'测试成功'"}]`）
- **output 字段**: 显示 LLM 的实际响应内容
- **Token 使用量**: 显示具体的 token 数量
- **延迟信息**: 显示实际的响应时间

### ❌ 问题情况：
- input/output 显示 "--"
- cumulative tokens 显示 0
- 缺少详细的调用信息

## 📊 技术细节

### 主要变更：
1. **替换 instrumentation 库**：
   - 从 `opentelemetry-instrumentation-openai` → `openinference-instrumentation-openai`
   - 从 `opentelemetry-instrumentation-anthropic` → `openinference-instrumentation-anthropic`

2. **更新导入语句**：
   ```python
   # 旧的导入
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor
   
   # 新的导入  
   from openinference.instrumentation.openai import OpenAIInstrumentor
   ```

3. **简化配置**：
   ```python
   # OpenInference 默认捕获所有内容，无需额外参数
   OpenAIInstrumentor().instrument()
   ```

## 🛠️ 故障排除

### 如果依然显示 "--"：
1. **重启 Phoenix UI**：
   ```bash
   # 停止现有的Phoenix进程
   pkill -f phoenix
   
   # 重新启动
   python3 start_phoenix.py
   ```

2. **清理 Phoenix 数据**：
   ```bash
   rm -rf phoenix/  # 删除本地Phoenix数据目录
   ```

3. **检查 API 密钥**：
   ```bash
   python3 check_env.py
   ```

4. **验证端口状态**：
   ```bash
   python3 check_phoenix.py
   ```

### 如果出现导入错误：
```bash
# 强制重新安装所有依赖
pip install --force-reinstall -r requirements.txt
```

## 📝 测试清单

- [ ] 依赖安装成功
- [ ] ObservabilityManager 初始化无错误
- [ ] OpenAI 调用成功 
- [ ] Phoenix UI 显示新的 trace
- [ ] input 字段显示实际消息内容
- [ ] output 字段显示 LLM 响应
- [ ] Token 使用量正确显示
- [ ] 延迟信息准确

## 🎯 预期结果

修复后，Phoenix UI 应该显示：
```
input: [{"role": "user", "content": "请简单说'测试成功'"}]
output: "测试成功"
cumulative tokens: 25 (具体数值)
latency: 1.2s (具体时间)
```

而不是：
```
input: --
output: --  
cumulative tokens: 0
latency: 0.00ms
```

## 📞 进一步支持

如果问题持续存在，请：
1. 运行 `python3 test_openinference.py` 获取详细诊断信息
2. 检查 Phoenix UI 的 Console 日志
3. 查看系统日志中的 OpenInference 相关错误信息 