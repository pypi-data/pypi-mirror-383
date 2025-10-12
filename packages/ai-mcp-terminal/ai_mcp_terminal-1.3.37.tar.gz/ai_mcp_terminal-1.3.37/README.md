# AI-MCP 多线程终端系统

让AI拥有多线程终端能力，通过Web界面实时监控所有操作。

## 🎯 核心功能

**AI首次调用MCP时，自动打开浏览器显示Web界面，您可以实时看到AI执行的所有命令！**

### 🚀 v1.3.37 最新更新 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 终端无上限+多线程并发读取

- ✅ **多线程并发读取所有输出（速度极快）**：
  - **问题**：之前 `get_batch_output` 是串行读取（for循环一个一个读），速度慢
  - **解决方案**：
    - 使用 `ThreadPoolExecutor` 实现真正的多线程并发
    - 最多32个线程同时读取
    - 使用 `as_completed` 快速收集结果
  
  - **性能对比**：
    ```
    串行读取100个终端：100 × 10ms = 1000ms (1秒)
    并发读取100个终端：max(100 × 10ms / 32) ≈ 31ms ✅
    
    速度提升：32倍！
    ```
  
  - **便捷功能**：
    ```python
    # 方式1: 指定终端ID列表
    get_batch_output(session_ids=["term1", "term2", ...])
    
    # 方式2: 不提供ID，自动读取所有终端 ⭐
    get_batch_output()  # 自动获取所有
    ```
  
  - **效果**：
    - ✅ 多线程并发，速度提升32倍
    - ✅ 不提供ID自动读取所有
    - ✅ 异常自动捕获，不会失败
    - ✅ 实时进度日志

- ✅ **终端无上限！智能内存管理**：
  - **移除限制**：
    - 删除之前的10个终端数量限制
    - 可以创建无限多个终端
    - 不再有"已达到最大会话数限制"错误
  
  - **智能清理策略（保留输出）**：
    - ≤64个终端：不做任何清理
    - >64个终端：检查内存使用
    - 内存<85%：不清理，继续运行
    - 内存≥85%：清理最老的已完成/空闲终端
  
  - **清理机制**：
    ```
    后台线程每5秒检查：
    
    if 终端数 <= 64:
        跳过检查，所有终端保留
    
    if 终端数 > 64:
        检查内存使用
        
        if 内存 < 85%:
            不清理（内存充足）
        
        if 内存 >= 85%:
            找出所有已完成/空闲的终端
            按创建时间排序（最老的在前）
            清理最老的10%（至少1个）
    ```
  
  - **优势**：
    - ✅ 输出不会消失（只在必要时清理）
    - ✅ 64个终端内完全自由
    - ✅ 内存充足时不限数量
    - ✅ 内存不足时优先清理最老的
    - ✅ 正在运行的命令永不清理

- ✅ **新增：MCP可指定终端类型（重要功能）**：
  - **问题**：之前无法指定终端类型，默认使用bash，导致Windows命令失败
  - **解决方案**：
    - `create_session` 新增 `shell_type` 参数
    - `create_batch` 每个会话可指定不同的 `shell_type`
    - 可选值：`cmd`, `powershell`, `pwsh`, `bash`, `zsh`, `fish`, `sh`
    - 如不指定则自动检测（默认行为）
  
  - **使用示例**：
    ```python
    # 创建CMD终端执行Windows命令
    create_session(
        cwd="C:\\Users\\...",
        shell_type="cmd",
        initial_command="systeminfo | findstr /B OS"
    )
    
    # 创建PowerShell终端
    create_session(
        cwd="C:\\Users\\...",
        shell_type="powershell",
        initial_command="Get-ComputerInfo"
    )
    
    # 批量创建不同类型的终端
    create_batch(sessions=[
        {
            "name": "backend",
            "cwd": "./backend",
            "shell_type": "cmd",
            "initial_command": "npm run dev"
        },
        {
            "name": "frontend",
            "cwd": "./frontend",
            "shell_type": "bash",
            "initial_command": "npm start"
        }
    ])
    ```
  
  - **效果**：
    - ✅ AI可以为Windows命令选择cmd/powershell
    - ✅ AI可以为Unix命令选择bash/zsh
    - ✅ 避免在错误的终端中执行命令
    - ✅ 提高命令执行成功率

- ✅ **三重优化彻底解决卡住问题**：
  
  **优化1: 10秒快速检测（不再等待太久）**
  - 命令运行10秒无输出 + 连续2次查询 → 立即触发紧急通知
  - 普通情况：连续3次查询无变化 → 触发通知
  - 效果：从30秒等待缩短到10秒就能发现问题
  
  **优化2: 智能识别错误的终端类型**
  - 自动检测在bash中运行Windows命令（cmd/systeminfo/findstr/ipconfig等）
  - 立即提示创建正确的终端类型
  - 示例：
    ```python
    # 在bash中运行 systeminfo → 立即提示
    {
      "ai_suggestion": {
        "action": "⚠️ 错误的终端类型！systeminfo是Windows命令",
        "options": [
          "立即使用 kill_session 结束当前会话",
          "创建正确的终端：create_session(shell_type='cmd')",
          "在正确的终端中执行命令"
        ],
        "severity": "high"
      }
    }
    ```
  
  **优化3: 超时锁防止死锁**
  - `lock.acquire(timeout=2.0)` 2秒超时保护
  - 自动重置计数器
  - 确保finally释放锁
  
  - **检测优先级**（从高到低）：
    1. 🚨 **错误的终端类型**（最高优先级）
    2. 🚨 **10秒无输出**（高优先级）
    3. ⚠️ **长时间运行服务**（中等优先级）
    4. 💡 **超长运行**（低优先级）
  
  - **效果**：
    - ✅ 10秒快速发现问题（之前要等更久）
    - ✅ 自动识别错误的终端类型
    - ✅ 永不死锁（2秒超时保护）
    - ✅ 清晰的优先级和建议
    - ✅ 减少无效MCP调用

### 🚀 v1.3.36 智能长时间运行命令检测

- ✅ **AI不再卡在长时间运行的命令上**：
  - **问题**：`npm run dev`, `ping -t` 等命令永不结束，AI会一直等待
  - **解决方案**：智能检测长时间运行的命令，返回当前输出+AI建议
  - **工作原理**：
    1. 识别常见的长时间运行命令（npm run, yarn dev, python runserver, ping -t等）
    2. 如果命令运行超过5秒且符合模式，返回元数据和建议
    3. AI可以根据当前输出自主决定：继续等待/停止服务/创建新终端
  
  - **返回的元数据**：
    ```json
    {
      "metadata": {
        "is_running": true,
        "running_seconds": 12.3,
        "command": "npm run dev",
        "output_length": 1024,
        "is_likely_long_running": true,
        "ai_suggestion": {
          "action": "已获取到当前输出，这是一个持续运行的服务",
          "options": [
            "如果输出显示服务已启动，可以继续其他操作",
            "如果需要停止服务，使用 kill_session 工具",
            "如果需要在同一目录执行其他命令，创建新的终端会话"
          ],
          "reason": "命令已运行12秒，包含服务启动关键词"
        }
      },
      "ai_notice": "⚠️ 已获取到当前输出，这是一个持续运行的服务\n..."
    }
    ```
  
  - **智能建议场景**：
    - **长时间运行服务**（运行>5秒+包含npm/yarn等）：提示这是服务，可继续其他操作
    - **可能卡住**（运行>10秒但无输出）：建议kill或重试
    - **超长运行**（运行>30秒）：提示运行时间长，让AI判断是否正常
  
  - **效果**：
    - ✅ AI不会卡在 `npm run dev` 等待永久完成
    - ✅ AI获得足够信息自主决策（继续/停止/新终端）
    - ✅ MCP永不阻塞，始终快速响应
    - ✅ 提供清晰的操作建议，提升AI决策质量

### 🚀 v1.3.35 永不卡住保证

- ✅ **全局错误保护：确保系统永不卡住**：
  - **设计理念**：无论发生什么错误，系统都应该返回有意义的结果，而不是 `undefined` 或卡住
  - **五层保护机制**：
    1. **result未定义保护**：检测并处理 `result` 为 None 或未定义的情况
    2. **类型验证保护**：确保返回值是字典类型，否则自动转换
    3. **必要字段保护**：确保 `success` 字段存在，错误时自动添加 `error` 字段
    4. **分类异常捕获**：针对不同异常类型（超时、参数错误、值错误）提供不同的错误信息
    5. **兜底异常捕获**：捕获所有未预期的异常，包含完整的 traceback
  
  - **错误返回格式**：
    ```json
    {
      "success": false,
      "error": "详细的错误描述",
      "error_type": "异常类型名称",
      "tool": "工具名称",
      "recovery": "系统已采取的恢复措施",
      "suggestion": "给AI的建议",
      "debug_info": {
        "arguments": "参数列表",
        "timestamp": "时间戳",
        "traceback": "完整的调用栈（通用异常时）"
      }
    }
    ```
  
  - **核心方法异常保护**：
    - `execute_command`: 即使异常也返回错误对象，不抛出异常
    - `get_output`: 即使异常也返回 `(False, [])`，永不卡住
    - 所有MCP工具调用都有超时/参数/值错误的专门处理
  
  - **效果**：
    - ✅ 永不返回 `undefined`
    - ✅ 永不因异常而中断AI对话
    - ✅ 所有错误都有清晰的说明和建议
    - ✅ 提供完整的调试信息帮助定位问题

### 🚀 v1.3.34 修复get_output的only_last_command

- ✅ **修复 get_output 返回错误命令的bug**：
  - **问题重现**：
    1. 执行命令A（失败并快速完成）
    2. 执行命令B（正在运行中）
    3. 调用 `get_output(only_last_command=true)`
    4. **错误**：返回的是命令A的输出，而不是命令B
  - **根本原因**：`output_history[-1]` 返回的是**最后完成的命令**，而不是**最后执行的命令**
  - **解决方案**：
    ```python
    # 旧逻辑（有bug）
    if only_last_command:
        output_list = [session.output_history[-1]]  # 最后完成的命令
    
    # 新逻辑（正确）
    if only_last_command:
        if session.current_command:  # 优先返回正在运行的命令
            output_list = [current_command_output]
        elif session.output_history:
            output_list = [session.output_history[-1]]
    ```
  - **效果**：`get_output(only_last_command=true)` 现在正确返回最近执行的命令，无论它是否已完成

### 🚀 v1.3.33 完美修复中文乱码

- ✅ **完美修复Windows中文乱码问题**：
  - **问题1**：逐字节读取破坏了GBK双字节字符（GBK每个中文字符=2字节）
  - **问题2**：单一编码解码失败时使用`errors='replace'`导致出现`�`替换字符
  - **解决方案**：
    - **缓冲区优化**：改用1024字节块读取，避免切断多字节字符
    - **智能解码器**：实现`_smart_decode()`方法，尝试多种编码：
      ```python
      encodings = [primary_encoding, 'gbk', 'utf-8', 'cp936', 'gb18030', 'latin-1']
      # 尝试每种编码，选择不包含�的结果
      ```
    - **按行分割**：在完整字节流中寻找换行符，保证字符完整性
  - **效果**：完美显示所有中文输出，零乱码

- ✅ **技术细节**：
  ```python
  # 读取策略（避免破坏多字节字符）
  chunk = process.stdout.read(1024)  # 大块读取
  while b'\n' in buffer:
      line_bytes = buffer[:buffer.index(b'\n')+1]  # 完整行
      line = self._smart_decode(line_bytes, encoding)  # 智能解码
  
  # 智能解码（尝试多种编码，选择最佳结果）
  def _smart_decode(self, data: bytes, primary_encoding: str):
      for encoding in [primary, 'gbk', 'utf-8', 'cp936', 'gb18030']:
          decoded = data.decode(encoding)
          if '�' not in decoded:  # 无替换字符 = 成功
              return decoded
  ```

- ✅ **修复的命令示例**：
  - ✅ `ipconfig` - 网络配置信息（完美显示"适配器"、"配置"等中文）
  - ✅ `systeminfo | findstr /B "OS" "System"` - 系统信息（完美显示）
  - ✅ `chcp` - 代码页信息
  - ✅ 所有包含中文的Windows命令输出
  - ✅ 混合中英文输出（如带有中文路径的错误信息）

### 🚀 v1.3.32 修复Windows中文乱码（已被v1.3.33完善）

- ✅ **初步修复Windows中文乱码问题**：
  - 改用二进制模式读取subprocess输出
  - 手动用正确的编码（GBK/UTF-8）解码
  - 确保传输到WebSocket的是正确的UTF-8字符串

### 🚀 v1.3.31 批量读取输出，一次搞定

- ✅ **新增 get_batch_output 工具**：
  - 🚀**一次调用获取所有终端的输出**，不再需要逐个读取
  - 默认 `only_last_command=true`：只返回最后一次命令的输出，避免大量历史数据传输
  - 支持不传 `session_ids`：自动获取所有终端的输出
  - **效率提升惊人**：3个终端从3次调用 → 1次调用
  
- ✅ **优化 get_output 工具**：
  - 新增 `only_last_command` 参数：只读取最后一次命令的输出
  - 避免传输几百行的历史数据，只传输AI真正需要的
  - 性能优化：数据量减少90%+
  
- ✅ **完整流程优化对比**：
  ```
  场景：启动前后端+数据库，然后查看输出
  
  旧方式：
  1. create_session("frontend")          → 1秒
  2. execute_command("frontend", ...)    → 0.5秒
  3. create_session("backend")           → 1秒
  4. execute_command("backend", ...)     → 0.5秒
  5. create_session("database")          → 1秒
  6. execute_command("database", ...)    → 0.5秒
  7. get_output("frontend")              → 0.3秒（可能包含几百行历史）
  8. get_output("backend")               → 0.3秒
  9. get_output("database")              → 0.3秒
  总耗时：≈ 5.4秒，9次MCP调用，传输大量无用历史数据
  
  新方式（最优）：
  1. create_batch([frontend, backend, database])        → 1秒
  2. get_batch_output(only_last_command=true)           → 0.2秒（只传最后一次命令）
  总耗时：≈ 1.2秒，2次MCP调用，只传有用数据
  
  效率提升：450%，MCP调用减少78%，数据量减少90%+！
  ```

- ✅ **使用建议**：
  - 创建多个终端 → 用 `create_batch`
  - 读取多个终端输出 → 用 `get_batch_output`
  - 只关心最新输出 → 设置 `only_last_command=true`
  - AI会更快响应，用户体验更流畅！

### 🚀 v1.3.30 创建即执行，效率倍增

- ✅ **create_session 支持 initial_command**：
  - 创建终端时可以直接传入初始命令
  - 终端创建完成后立即执行该命令
  - **效率提升50%**：2次MCP调用 → 1次MCP调用
  - 示例：`create_session(name="frontend", cwd="/path", initial_command="npm run dev")`

- ✅ **新增 create_batch 工具**：
  - 🚀**最高效的方式**：批量创建终端并同时执行初始命令
  - 所有终端**并发创建并执行**，真正的并发
  - **效率提升惊人**：6次MCP调用 → 1次MCP调用（3个终端）
  - 示例：
    ```json
    {
      "sessions": [
        {"name": "frontend", "cwd": "/app/frontend", "initial_command": "npm run dev"},
        {"name": "backend", "cwd": "/app/backend", "initial_command": "python manage.py runserver"},
        {"name": "database", "cwd": "/app", "initial_command": "docker-compose up"}
      ]
    }
    ```
  - 一次调用，三个终端同时创建并执行，总耗时 ≈ 1秒！

- ✅ **效率对比**：
  ```
  场景：启动前后端+数据库（3个服务）
  
  旧方式：
  1. create_session("frontend")     → 1秒
  2. execute_command("frontend", "npm run dev")  → 0.5秒
  3. create_session("backend")      → 1秒
  4. execute_command("backend", "python ...")   → 0.5秒
  5. create_session("database")     → 1秒
  6. execute_command("database", "docker...")   → 0.5秒
  总耗时：≈ 4.5秒，6次MCP调用
  
  新方式（create_batch）：
  1. create_batch([frontend, backend, database]) → 1秒
  总耗时：≈ 1秒，1次MCP调用
  
  效率提升：450% ！
  ```

- ✅ **智能提示**：
  - 如果不传 initial_command，返回时会提示"下次可以使用initial_command减少MCP调用"
  - 让AI学会使用更高效的方式

### 🚀 v1.3.29 真正的并发执行

- ✅ **新增 execute_batch 工具**：
  - 可以同时向多个终端发送**不同的命令**
  - 使用 `asyncio.gather` 实现真正的并发
  - AI可以一次性分配多个任务到多个终端
  - 示例：同时在 frontend 执行 `npm run dev`，backend 执行 `python manage.py runserver`

- ✅ **修复 broadcast_command 伪并发问题**：
  - **旧逻辑**：`for sid in session_ids: await execute_command(sid, cmd)` - 串行等待
  - **新逻辑**：`await asyncio.gather(*[execute_command(sid, cmd) for sid in session_ids])` - 真正并发
  - 多个终端**同时**开始执行，不再一个等另一个

- ✅ **并发对比**：
  ```python
  # 旧版（伪并发）- 假设每个命令1秒启动
  for sid in [term1, term2, term3]:
      await execute(sid, cmd)  # 总共需要3秒
  
  # 新版（真并发）- 使用asyncio.gather
  await asyncio.gather(
      execute(term1, cmd),
      execute(term2, cmd),
      execute(term3, cmd)
  )  # 总共只需要1秒，三个命令同时启动
  ```

- ✅ **使用场景**：
  - 同时启动前后端服务（不同命令）
  - 批量测试多个环境（相同命令）
  - 并发部署到多台服务器（不同命令）
  - 多任务并行处理（不同命令）

### 🚀 v1.3.28 修复所有卡住问题

- ✅ **删除所有导致卡住的调试日志**：
  - **问题1**：`create_session`中的中文日志在某些编码环境下导致print阻塞
  - **问题2**：大量`[realtime_output]`、`[history_save]`等调试日志导致JSON解析错误
  - **问题3**：调试日志中包含中文会在Windows GBK环境产生乱码
  - **现象**：AI调用任何工具后返回`undefined`，对话完全卡住

- ✅ **全面英文化调试日志**：
  - 所有中文日志改为英文（避免编码问题）
  - 删除冗余的调试日志（减少输出量）
  - 保留关键的ERROR日志便于诊断
  - 在所有关键位置添加`sys.stderr.flush()`

- ✅ **修复的文件**：
  - `src/terminal_manager.py` - 所有日志英文化，删除冗余日志
  - `src/mcp_server.py` - get_output添加详细flush

- ✅ **修复效果**：
  - ✅ create_session不再卡住
  - ✅ execute_command正常执行
  - ✅ get_output正确返回
  - ✅ 不再产生JSON解析错误
  - ✅ AI对话完全流畅

### 🚀 v1.3.27 修复get_output卡住导致AI无响应

- ✅ **删除危险的reload代码**：
  - **问题**：每次调用`get_output`时都会重新加载整个`terminal_manager`模块
  - **后果**：事件循环引用丢失、状态丢失、可能在reload时卡住
  - **现象**：AI调用`get_output`后返回`undefined`，AI对话卡住
  - **影响**：严重影响用户体验，AI无法获取终端输出

- ✅ **修复内容**：
  - 删除line 288-301的importlib.reload调试代码
  - 这是调试遗留代码，不应该在生产环境中存在
  - 保留正常的`get_output`逻辑
  - 在所有关键位置添加`sys.stderr.flush()`确保日志立即输出

- ✅ **修复效果**：
  - ✅ `get_output`不再卡住
  - ✅ AI可以正常获取终端输出
  - ✅ 不再返回undefined
  - ✅ 事件循环和状态保持稳定

### 🚀 v1.3.26 修复中文调试日志导致JSON解析错误

- ✅ **修复根本原因**：
  - **问题**：调试日志中的中文在Windows GBK环境下产生乱码，导致AI IDE的JSON解析器报错
  - **现象**：`Unexpected token 'g', "[get_output"... is not valid JSON`
  - **影响**：虽然不影响核心功能，但产生大量错误日志，干扰调试

- ✅ **修复内容**：
  - 将所有调试日志中的中文替换为英文
  - `[get_output]` - 会话查询日志全部英文化
  - `[realtime_output]` - 实时输出日志全部英文化  
  - `[history_save]` - 历史保存日志全部英文化
  - `[encoding]` - 编码检测日志全部英文化
  - `[error_classify]` - 错误分类日志全部英文化

- ✅ **修复效果**：
  - ✅ 不再产生JSON解析错误
  - ✅ 调试日志清晰易读
  - ✅ 跨平台编码兼容性

### 🚀 v1.3.25 优化stdio通信稳定性
- ✅ **v1.3.24修复已验证有效**：
  - 所有`command_completed`事件成功通过`run_coroutine_threadsafe`触发 ✅
  - 所有MCP工具调用正常返回 ✅
  - 多终端并发执行正常 ✅
  - 错误分类和处理正常 ✅

- ✅ **新增stdio缓冲区优化**：
  - 每次`call_tool`开始时强制flush stdout和stderr
  - 避免缓冲区阻塞导致的偶发性卡顿
  - 确保MCP stdio通信的稳定性

- ✅ **测试验证通过**：
  - ✅ 正常命令执行
  - ✅ 中文字符编码
  - ✅ 错误处理（命令不存在、语法错误、文件未找到）
  - ✅ 广播命令（3个终端并发）
  - ✅ 长时间运行命令（15秒 sleep）
  - ✅ 所有`get_output`调用正常返回

- 💡 **如遇偶发卡顿**：重启MCP即可恢复

### 🚀 v1.3.24 修复事件循环导致AI卡住 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
- ✅ **修复根本原因：后台线程中的事件触发没有事件循环**
- ✅ **问题症状**：
  - 🔴 AI调用MCP后卡住，返回`undefined`
  - 🔴 命令执行完成后，`command_completed`事件广播失败
  - 🔴 错误日志：`There is no current event loop in thread 'Thread-XX (execute_in_background)'`
  - 🔴 `output_chunk`（实时输出）正常 ✅，但`command_completed`失败 ❌

- ✅ **根本原因**：
  - 命令在后台线程（`execute_in_background`）中执行
  - 命令完成后触发`command_completed`事件
  - 事件回调使用`asyncio.get_event_loop()`获取循环，但后台线程中没有
  - 导致事件触发失败，WebSocket无法广播完成消息
  - 累积的失败可能导致资源锁定，最终AI卡住

- ✅ **修复方案 - 线程安全的事件触发**：
  ```python
  # 修复后的_trigger_event（线程安全）
  try:
      loop = asyncio.get_running_loop()  # 主线程
      loop.create_task(callback(event_type, data))
  except RuntimeError:  # 后台线程
      asyncio.run_coroutine_threadsafe(
          callback(event_type, data),
          self._web_server_loop  # 使用Web服务器的事件循环
      )
  ```

- ✅ **修复的文件**：
  - `src/terminal_manager.py` - `_trigger_event`改为线程安全
  - `src/mcp_server.py` - 将Web服务器的事件循环设置到`terminal_manager._web_server_loop`
  - `src/mcp_server.py` - 所有关键位置添加`sys.stderr.flush()`

- ✅ **现在所有事件都能正常触发**：
  - ✅ `session_created` - 会话创建
  - ✅ `command_started` - 命令开始
  - ✅ `output_chunk` - 实时输出
  - ✅ `command_completed` - 命令完成 **（已修复）**
  - ✅ `command_error` - 命令错误

- ✅ **AI不再卡住，所有工具调用正常返回！**

### 🚀 v1.3.23 修复导入问题 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 彻底修复导入问题
- ✅ **修复根本原因：Python模块导入兼容性问题**
- ✅ **问题症状**：
  - 🔴 直接运行`python src/main.py`报错：`ImportError: attempted relative import with no known parent package`
  - 🔴 MCP工具调用返回`undefined`
  - 🔴 Web服务器无法启动

- ✅ **根本原因**：
  - **直接运行脚本** vs **作为包导入** 的导入方式不同
  - 相对导入只能在包内使用，直接运行脚本会失败
  - 需要兼容两种运行模式

- ✅ **最终解决方案 - 智能导入**：
  ```python
  # 兼容两种运行模式
  try:
      from .terminal_manager import TerminalManager  # 作为包导入
  except ImportError:
      from terminal_manager import TerminalManager   # 直接运行
  ```

- ✅ **修复的文件**：
  - ✅ `src/mcp_server.py` - 使用try-except智能导入
  - ✅ `src/web_server.py` - 使用try-except智能导入
  - ✅ `src/main.py` - 保持绝对导入（因为有sys.path设置）

- ✅ **支持的运行模式**：
  1. ✅ **直接运行**：`python src/main.py` 
  2. ✅ **作为包运行**：`python -m src.main`
  3. ✅ **MCP stdio模式**：通过AI IDE配置运行
  4. ✅ **作为模块导入**：`from src.mcp_server import MCPTerminalServer`

- ✅ **现在MCP完全正常工作！**
  - ✅ 所有运行模式都支持
  - ✅ 所有工具调用正确返回结果
  - ✅ Web界面正常启动和显示
  - ✅ 终端命令执行正常
  - ✅ 实时输出流式显示

### 🚀 v1.3.22 调试版本 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 修复AI卡住问题
- ✅ **添加完整的调试日志系统** - 追踪MCP卡住的具体位置
- ✅ **每个关键步骤都有日志**：
  - `[Web]` - Web服务器启动的每一步
  - `[WebServer]` - WebTerminalServer初始化过程
  - `[MCP]` - MCP工具调用的执行过程
  - `[DEBUG]` - 数据处理和序列化
  - 所有stderr输出都手动flush()
- ✅ **详细日志示例**：
  ```
  [MCP] ========== 工具调用开始 ==========
  [MCP] 工具名: get_all_sessions
  [MCP] 参数: {}
  [MCP] 首次调用，启动Web服务器...
  [Web] start_web_server开始
  [Web] 创建WebTerminalServer实例...
  [WebServer] __init__开始
  [WebServer] FastAPI创建完成
  [WebServer] 挂载静态文件: ...
  [WebServer] 注册回调...
  [WebServer] 设置路由...
  [WebServer] __init__完成
  [Web] WebTerminalServer创建完成
  [Web] shutdown回调已设置
  [INFO] Web服务器线程已启动，正在后台初始化...
  [MCP] Web服务器启动完成
  [MCP] 开始执行get_all_sessions
  [MCP] 获取到2个会话
  [MCP] get_all_sessions结果已准备
  [MCP] 工具 get_all_sessions 执行完成
  [MCP] 开始JSON序列化...
  [MCP] JSON序列化成功，长度: 456
  [MCP] 返回response，数量: 1
  [MCP] ========== 工具调用结束 ==========
  ```
- ✅ **问题诊断**：
  - 如果AI卡住，查看Python的stderr输出
  - 日志会显示最后执行到哪一步
  - 如果日志在某一步后停止，说明该步骤阻塞

### 🚀 v1.3.21 完整错误处理和优化
- ✅ **修复中文字符乱码问题** - 智能编码检测：Git Bash用UTF-8，CMD/PowerShell用GBK
- ✅ **会话数量限制**：
  - 最大会话数：10个
  - 接近限制时警告（8个时）
  - 超过限制时明确错误提示
- ✅ **增强错误分类系统**：
  - `COMMAND_NOT_FOUND` - 命令不存在（黄色）
  - `PERMISSION_DENIED` - 权限不足（红色）
  - `FILE_NOT_FOUND` - 文件/目录不存在（黄色）
  - `SYNTAX_ERROR` - 命令语法错误（紫色）
  - `USER_INTERRUPTED` - 用户中断Ctrl+C（灰色）
  - `INVALID_ARGUMENT` - 无效参数（黄色）
  - `GENERAL_ERROR` - 一般错误（红色）
- ✅ **统一错误信息格式** - 所有错误都包含分类和详细描述
- ✅ **彩色错误显示** - 终端根据错误类型显示不同颜色

## 🎨 智能错误处理系统

### 📋 错误分类

所有命令执行错误都会自动分类，并在终端显示为不同颜色：

| 错误类型 | 颜色 | 说明 | 示例 |
|---------|------|------|------|
| **COMMAND_NOT_FOUND** | 🟡 黄色 | 命令不存在 | `nonexistentcommand` |
| **PERMISSION_DENIED** | 🔴 红色 | 权限不足 | `touch /root/test` |
| **FILE_NOT_FOUND** | 🟡 黄色 | 文件/目录不存在 | `ls /nonexistent` |
| **SYNTAX_ERROR** | 🟣 紫色 | 语法错误 | `echo "unclosed` |
| **USER_INTERRUPTED** | ⚪ 灰色 | 用户中断（Ctrl+C） | `^C` |
| **INVALID_ARGUMENT** | 🟡 黄色 | 无效参数 | `git --invalid` |
| **GENERAL_ERROR** | 🔴 红色 | 一般错误 | 其他错误 |

### 🔍 错误信息格式

```bash
# 旧版本（不友好）
$ nonexistentcommand
command not found
[退出码: 127]

# 新版本（友好）
$ nonexistentcommand
command not found
[COMMAND_NOT_FOUND] 命令不存在：nonexistentcommand
```

### 🌐 字符编码智能检测

**问题**：Windows上中文显示乱码（如"涓鏂囨祴璇曞懡浠ゆ墽琛"）

**解决方案**：
- **Git Bash / Zsh / Fish**：使用 UTF-8 编码
- **CMD / PowerShell**：使用 GBK 编码
- **Linux / macOS**：使用 UTF-8 编码

**实现**：
```python
if platform.system().lower() == "windows":
    if session.shell_type in ['bash', 'zsh', 'fish', 'sh']:
        encoding = 'utf-8'  # Unix-like shell
    else:
        encoding = 'gbk'     # Windows native shell
```

### 🛡️ 会话数量管理

- **最大会话数**：10个
- **警告阈值**：8个（接近限制时显示警告）
- **超过限制**：明确错误提示，要求先终止不需要的终端

```python
# 创建第8个会话时
⚠️ 当前会话数：8，接近限制（10）

# 尝试创建第11个会话时
❌ 已达到最大会话数限制（10个）。请先终止一些不需要的终端。
```

## ⚡ 异步执行：AI不会被阻塞

### 🎯 核心优势

**以前的问题**：AI执行长时间命令（如`npm run dev`、`ping`）时，会一直等待命令完成才返回，导致：
- ❌ AI对话被阻塞，无法回复用户
- ❌ 用户必须等待命令完成才能继续对话
- ❌ 长时间命令会让AI"卡住"

**现在的解决方案**：
- ✅ **立即返回** - `execute_command`发送命令后立即返回，不等待完成
- ✅ **后台执行** - 命令在独立线程中运行，不阻塞MCP进程
- ✅ **实时推送** - 输出通过WebSocket实时推送到Web界面
- ✅ **继续对话** - AI可以立即处理用户的下一个请求
- ✅ **多线程分发** - 可以同时向多个终端发送命令

### 📋 工作流程

```
AI调用MCP：execute_command(session_id="backend", command="npm run dev")
    ↓
MCP立即返回："✅ 命令已发送到终端 backend（后台执行，不阻塞AI对话）"
    ↓
AI继续处理用户对话 ✅
    ↓
后台线程执行命令 🔄
    ↓
实时输出 → WebSocket → Web界面 📡
    ↓
命令完成 → 触发command_completed事件 → Web界面显示结果 🎉
```

### 💡 使用示例

**场景：启动前后端服务**
```
用户：同时启动前端和后端服务
AI：
  1. 创建frontend终端
  2. 创建backend终端
  3. execute_command(frontend, "npm run dev") → 立即返回 ✅
  4. execute_command(backend, "npm start") → 立即返回 ✅
  5. 回复用户："前后端服务已启动，请查看Web界面" ✅

用户可以立即继续对话，服务在后台运行！
```

## 🛑 关于"结束服务"按钮

点击Web界面右上角的"结束服务"按钮时：

### 📋 执行流程
1. ✅ **终止所有终端进程** - 停止所有正在运行的命令
2. ✅ **关闭WebSocket连接** - 断开所有浏览器连接
3. ✅ **清空会话数据** - 释放内存中的终端数据
4. ✅ **停止uvicorn服务器** - 释放Web端口（默认8000）
5. ✅ **重置服务标志** - 允许下次重新启动

### ⚠️ 重要提示
- **MCP服务继续运行** - Python进程不会退出，AI IDE仍可调用MCP
- **端口已释放** - 8000端口被释放，不会占用系统资源
- **下次自动启动** - AI下次调用MCP工具时，Web界面会重新启动
- **数据不保留** - 所有终端历史和输出会被清除

### 💡 使用场景
- 长时间不使用时释放资源
- 需要释放8000端口
- 清除所有终端数据重新开始
- 停止所有后台命令（如`npm run dev`）

## 🔍 实时输出诊断

如果ping没有实时显示，请检查：

1. **检查Python控制台输出**：
```
[实时输出] stdout: 正在 Ping ...
[实时输出] 回调数量: 1
[实时输出] 调用回调函数
[实时输出] 准备广播: session_xxx
[广播] 类型:output_chunk, 连接数:1
[广播] 成功发送 output_chunk
```

2. **检查浏览器控制台**：
```
[实时输出] 收到chunk: session_xxx stdout 正在 Ping ...
```

3. **检查WebSocket连接**：
- 浏览器F12 -> Network -> WS -> 应该看到`output_chunk`消息

**如果没有实时输出**：
- 确保重启了Python服务（`Ctrl+C` 后重新运行）
- 确保刷新了浏览器（`Ctrl+Shift+R`）
- 检查Python控制台是否有错误

## 📦 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置IDE

在IDE配置文件中添加（**修改路径为实际路径**）：

```json
{
  "mcpServers": {
    "ai-mcp-terminal": {
      "command": "python",
      "args": ["C:/Users/67310/OneDrive/桌面/cp/mcp/ai-mcp/src/main.py"]
    }
  }
}
```

**配置文件位置：**
- Claude Desktop: `%APPDATA%\Claude\claude_desktop_config.json`
- Cursor/Cline: `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

### 3. 使用

1. 重启IDE
2. ⚠️ **重要**：对AI说时请包含工作目录，例如：
   - "在当前项目目录创建一个终端并执行pwd"
   - "创建终端（工作目录：/path/to/project）"
3. 🎉 浏览器自动打开Web界面
4. 💡 可以直接在终端输入命令（像真正的终端），或使用底部输入框

## 🛠️ MCP工具（11个）

1. `create_session` - 创建终端（**支持initial_command，创建即执行，效率提升50%**）
2. `create_batch` - 🚀**最高效创建**：批量创建终端并执行初始命令（并发创建+执行，1次调用完成所有）
3. `execute_command` - 执行命令（异步）
4. `broadcast_command` - 广播相同命令到多个终端（**真正的并发，使用asyncio.gather**）
5. `execute_batch` - **批量并发执行不同命令**（真正的并发，同时向多个终端发送不同命令）
6. `get_all_sessions` - 获取终端列表
7. `get_session_status` - 获取状态
8. `get_output` - 获取输出（**支持only_last_command，只读最后一次命令**）
9. `get_batch_output` - 🚀**最高效读取**：批量获取多个终端输出（1次调用，默认只读最后一次命令）
10. `kill_session` - 终止终端
11. `get_stats` - 系统统计

### 🚀 真正的并发执行示例

**场景1：同时启动前后端服务（不同命令）**
```json
// 使用 execute_batch 工具
{
  "commands": [
    {"session_id": "frontend", "command": "npm run dev"},
    {"session_id": "backend", "command": "python manage.py runserver"},
    {"session_id": "database", "command": "docker-compose up -d"}
  ]
}
// 三个命令同时启动，总耗时 ≈ 1秒（而不是3秒）
```

**场景2：批量测试多个环境（相同命令）**
```json
// 使用 broadcast_command 工具
{
  "session_ids": ["test-env1", "test-env2", "test-env3"],
  "command": "npm test"
}
// 三个测试环境同时运行，真正的并发
```

**场景3：并发部署到多台服务器（不同命令）**
```json
// 使用 execute_batch 工具
{
  "commands": [
    {"session_id": "server1", "command": "ssh root@192.168.1.10 'cd /app && git pull && npm install && pm2 restart all'"},
    {"session_id": "server2", "command": "ssh root@192.168.1.11 'cd /app && git pull && npm install && pm2 restart all'"},
    {"session_id": "server3", "command": "ssh root@192.168.1.12 'cd /app && git pull && npm install && pm2 restart all'"}
  ]
}
// 三台服务器同时部署，大幅缩短部署时间
```

### 💡 智能Shell提示示例

**AI创建终端时会收到：**
```
✅ 终端会话已创建成功

📋 会话信息:
  - 会话ID: frontend
  - Shell类型: bash
  - 工作目录: C:\project
  - Web界面: http://localhost:8000

💡 命令使用建议:
✅ 使用Unix命令：ls, pwd, cd, echo $USER, grep, curl
⚠️ Windows CMD命令需要：cmd /c "命令"

🌐 提示: 用户可在Web界面实时查看所有操作
```

**AI看到后就知道：**
- 使用的是bash，应该用Unix命令
- 要用Windows命令需要通过`cmd /c`调用
- 不会盲目尝试`echo %USERNAME%`等CMD命令

## ✨ 特性

- ✅ **智能Shell检测** - 自动识别并使用最佳Shell（支持bash/zsh/fish/powershell/pwsh/cmd等）
- ✅ **自动打开Web界面** - 首次调用MCP时自动打开浏览器
- ✅ **实时流式输出** - ping、npm run等命令逐行实时显示，无需等待完成
- ✅ **实时显示AI命令** - 在Web界面查看所有AI操作，带[AI]黄色标识
- ✅ **真正的并发执行** - 使用asyncio.gather实现真正的并发，多个命令同时启动（v1.3.29）
- ✅ **批量执行不同命令** - execute_batch工具可同时向多个终端发送不同命令
- ✅ **多线程并发** - 支持同时运行多个终端
- ✅ **非阻塞执行** - 长时间运行命令不会阻塞AI对话
- ✅ **智能终端管理** - 自动检测重复命令，防止资源浪费
- ✅ **内存监控** - 实时监控系统内存使用
- ✅ **跨平台支持** - Windows/Linux/macOS
- ✅ **完整快捷键** - 像真正的终端：Ctrl+C中断、Ctrl+L清屏、Ctrl+Shift+C/V复制粘贴、右键粘贴
- ✅ **命令历史** - 支持↑↓键快速调用历史命令
- ✅ **完美中文支持** - Windows CMD/PowerShell中文输出零乱码，智能GBK→UTF-8转换（v1.3.32）
- ✅ **智能编码检测** - Git Bash用UTF-8，CMD/PowerShell用GBK，自动选择最佳编码
- ✅ **优化显示** - 固定列宽，整齐的终端输出
- ✅ **中英文切换** - 🌐 按钮一键切换界面语言
- ✅ **直接终端输入** - 像真正的终端一样直接打字，无需底部输入框
- ✅ **优雅关闭** - Web服务器关闭不影响MCP继续运行

## 🐚 Shell支持

系统会自动检测并使用最佳的Shell：

**Windows优先级**:
1. PowerShell Core (pwsh)
2. Git Bash (bash) ⭐ **推荐**
3. Zsh
4. Fish
5. Windows PowerShell
6. CMD

**macOS优先级**:
1. Zsh
2. Bash
3. Fish
4. Sh

**Linux优先级**:
1. Bash
2. Zsh
3. Fish
4. Dash
5. Sh

### ⚠️ 命令兼容性说明

**如果使用Git Bash（Windows默认）**：
- ✅ **跨平台命令**：`ls`, `pwd`, `cd`, `echo $USER`, `ping`, `curl`
- ❌ **Windows CMD命令**：`echo %USERNAME%`, `findstr` (需要特殊处理)
- ✅ **解决方案**：
  ```bash
  # 错误：在bash中不会解析
  echo %USERNAME%  # 输出: %USERNAME%
  
  # 正确：使用bash变量
  echo $USER  # 输出: 实际用户名
  
  # 或者显式调用cmd
  cmd /c "echo %USERNAME%"
  ```

**如果需要Windows特定命令**：
```bash
# 方式1：使用PowerShell
powershell -Command "Get-ComputerInfo | Select-Object WindowsProductName"

# 方式2：使用cmd
cmd /c "systeminfo | findstr /C:\"OS Name\""

# 方式3：创建PowerShell终端
# 在MCP工具中指定 shell_type="powershell"
```

## ⌨️ 快捷键

在Web终端界面，支持以下快捷键（**像真正的终端一样**）：

- **↑** (上键) - 查看上一条历史命令
- **↓** (下键) - 查看下一条历史命令
- **Enter** - 执行命令
- **Backspace** - 删除字符
- **Ctrl + C** - 终止当前命令（发送SIGINT信号）
- **Ctrl + L** - 清屏
- **Ctrl + V** - 粘贴（或使用Ctrl+Shift+V）
- **Ctrl + Shift + C** - 复制选中文本
- **Ctrl + Shift + V** - 粘贴
- **右键** - 快速粘贴

命令历史自动保存，最多100条

## ⚠️ 重要提示

### Windows中文显示
- **已优化**：系统自动使用GBK编码，中文命令输出正常显示
- 如遇乱码，请确保使用Git Bash（自动检测）

### 工作目录设置
🔴 **重要说明**：

**工作目录来源**：
- 终端的工作目录 = **AI IDE当前的项目根目录**
- AI调用MCP时会自动传递其当前工作目录（`cwd`参数，required）
- 这就是AI正在工作的项目目录

**目录不存在时**：
- 终端会显示红色错误：`工作目录不存在: XXX，请AI先创建此目录`
- AI看到错误后会自动创建目录
- **不会**自动跳到父目录或其他位置，避免在错误位置执行命令

**切换目录**：
```bash
# 在终端中使用 cd 命令切换
cd /path/to/another/directory
```

**示例流程**：
1. AI在`/project`工作，调用MCP创建终端 → 终端工作目录 = `/project`
2. AI想在`/project/frontend`执行命令 → 有两种方式：
   - 方式1：`cd frontend` 然后执行命令
   - 方式2：创建新终端，指定`cwd=/project/frontend`（如果目录不存在会报错）

### 终端交互方式
**💡 像真正的终端一样操作（无需底部输入框）**：
1. **直接在终端窗口打字** - 点击终端，直接输入命令
2. **Enter执行** - 按回车执行命令
3. **🖱️ 智能右键** - 
   - 选中文本 + 右键 = 📋 **复制**
   - 无选中 + 右键 = 📌 **粘贴**
4. **Ctrl+Shift+C/V** - 复制粘贴（标准终端快捷键）
5. **Ctrl+C** - 中断运行中的命令（发送SIGINT信号）
6. **Ctrl+L** - 清屏
7. **↑↓** - 历史命令导航

**注意**：底部输入框已隐藏，直接在终端内操作即可！

### 实时输出
✅ **已优化**：所有命令输出实时逐行显示
- `ping baidu.com` - 每个ping包立即显示
- `npm run dev` - 启动日志实时滚动
- 长时间运行命令 - 不再需要等待完成才看到输出

## 🌍 多语言支持

**界面语言**：
- ✅ 中文（简体）
- ✅ 英文（English）
- 🌐 点击右上角语言按钮切换，自动保存偏好

**编码自动检测**：
- Windows: GBK（中文）
- Linux/Mac: UTF-8

**功能**：
- 自动检测浏览器语言
- 本地存储语言偏好
- 所有界面元素实时切换

## 📝 更新日志

### v1.3.37 (最新) 🔥🔥🔥🔥🔥🔥🔥 多线程并发+终端无上限+智能内存管理
- ✅ **多线程并发读取输出（速度提升32倍）**
  - **问题**: `get_batch_output` 串行读取（for循环一个一个读），100个终端需要1秒
  - **解决方案**: 
    - 使用 `ThreadPoolExecutor` 实现真正的多线程并发
    - 最多32个线程同时读取
    - 使用 `as_completed` 快速收集结果
  - **性能对比**:
    ```
    串行: 100个终端 × 10ms = 1000ms
    并发: 100个终端 / 32线程 ≈ 31ms
    提升: 32倍！
    ```
  - **便捷功能**:
    - `get_batch_output(session_ids=[...])` - 指定ID列表
    - `get_batch_output()` - 不提供ID，自动读取所有 ⭐
  - **效果**: 
    - ✅ 速度提升32倍
    - ✅ 自动获取所有终端
    - ✅ 异常自动捕获
    - ✅ 实时进度日志

- ✅ **终端无上限！智能内存管理（保留输出）**
  - **移除限制**: 删除之前的10个终端数量限制，想创建多少就创建多少
  - **三层智能清理策略**: 
    1. **≤64个终端**: 完全不清理，所有输出保留
    2. **>64个终端 + 内存<85%**: 不清理，继续运行
    3. **>64个终端 + 内存≥85%**: 清理最老的已完成/空闲终端
  
  - **清理机制**: 
    - 后台线程每5秒检查一次
    - 只在终端数>64且内存不足时触发
    - 按创建时间排序，优先清理最老的
    - 每次清理10%的终端（至少1个）
    - 只清理已完成或空闲且无运行命令的终端
  
  - **优势**: 
    - ✅ 输出不会消失（只在必要时清理）
    - ✅ 64个终端内完全自由使用
    - ✅ 内存充足时不限数量
    - ✅ 内存不足时智能清理最老的
    - ✅ 正在运行的命令永远不会被清理
  
  - **示例场景**:
    ```
    场景1: 创建30个终端
    → 不会清理（≤64个）
    → 所有输出永久保留
    
    场景2: 创建100个终端，内存使用60%
    → 不会清理（内存充足）
    → 所有输出永久保留
    
    场景3: 创建100个终端，内存使用90%
    → 清理最老的10个已完成/空闲终端
    → 正在运行的90个保留
    ```

- ✅ **新增：MCP可指定终端类型（重要功能）**
  - **问题**: 之前无法指定终端类型，默认使用bash，导致Windows命令失败
  - **解决方案**: 
    - `create_session` 新增 `shell_type` 参数
    - `create_batch` 每个会话可指定不同的 `shell_type`
    - 可选值：`cmd`, `powershell`, `pwsh`, `bash`, `zsh`, `fish`, `sh`
    - 如不指定则自动检测（默认行为保持不变）
  - **使用示例**: 
    ```python
    # 创建CMD终端执行Windows命令
    create_session(cwd="...", shell_type="cmd", initial_command="systeminfo")
    
    # 创建PowerShell终端
    create_session(cwd="...", shell_type="powershell")
    
    # 批量创建不同类型
    create_batch(sessions=[
        {"name": "win", "cwd": "...", "shell_type": "cmd", "initial_command": "dir"},
        {"name": "unix", "cwd": "...", "shell_type": "bash", "initial_command": "ls"}
    ])
    ```
  - **效果**: 
    - ✅ AI可以为Windows命令选择cmd/powershell
    - ✅ AI可以为Unix命令选择bash/zsh
    - ✅ 避免在错误的终端中执行命令
    - ✅ 提高命令执行成功率

- ✅ **三重优化，彻底解决卡住问题**
  - **优化1: 10秒快速检测**
    - 命令运行10秒无输出 + 连续2次查询 → 立即触发紧急通知
    - 普通情况：连续3次查询无变化 → 触发通知
    - 从30秒等待缩短到10秒发现问题
  
  - **优化2: 智能识别错误的终端类型**
    - 检测在bash中运行Windows命令（cmd/systeminfo/findstr/ipconfig/dir/type等）
    - 立即提示创建正确的终端类型（cmd或powershell）
    - 优先级：最高（severity: high）
    - 示例：bash运行 `cmd /c systeminfo` → 立即建议 `create_session(shell_type='cmd')`
  
  - **优化3: 超时锁防止死锁**
    - `lock.acquire(timeout=2.0)` 2秒超时保护
    - finally确保释放锁
    - 命令完成自动重置计数器
  
  - **检测优先级**（从高到低）:
    1. 🚨 错误的终端类型（最高优先级）
    2. 🚨 10秒无输出（高优先级）
    3. ⚠️ 长时间运行服务（中等优先级）
    4. 💡 超长运行（低优先级）
  
  - **效果**: 
    - ✅ 10秒快速发现问题
    - ✅ 自动识别错误终端类型
    - ✅ 永不死锁
    - ✅ 清晰的优先级指引
    - ✅ 减少无效MCP调用

### v1.3.36 🔥🔥🔥🔥🔥🔥 智能长时间运行命令检测 - AI不再卡住
- ✅ **智能检测长时间运行的命令，AI不再无限等待**
  - **问题**: `npm run dev`, `ping -t`, `python runserver` 等命令永不结束，AI会一直调用 get_output 等待
  - **解决方案**: 
    - 识别常见长时间运行命令模式（npm/yarn/服务器等）
    - 计算命令运行时间，超过阈值时返回元数据+AI建议
    - AI根据当前输出自主决定：继续等待/停止/创建新终端
  - **三种智能建议场景**:
    1. **长时间服务**（>5秒+服务关键词）→ 提示这是服务，可继续其他操作
    2. **可能卡住**（>10秒无输出）→ 建议kill或重试
    3. **超长运行**（>30秒）→ 让AI根据输出判断
  - **返回格式**: 添加 `metadata` 和 `ai_notice` 字段，包含运行状态和操作建议
  - **效果**: ✅ AI不卡在长命令 ✅ 自主决策 ✅ MCP始终快速响应

### v1.3.35 🔥🔥🔥🔥🔥 永不卡住保证 - 全局错误保护
- ✅ **五层保护机制确保系统永不卡住**
  - **问题**: 之前某些错误情况下可能返回 `undefined` 导致AI卡住
  - **解决方案**: 
    1. result未定义检测 + 自动修复
    2. 类型验证 + 自动转换
    3. 必要字段自动补全
    4. 分类异常捕获（超时/参数/值错误）
    5. 兜底异常捕获（包含完整traceback）
  - **核心方法保护**: 
    - `execute_command` 永不抛出异常，返回错误对象
    - `get_output` 永不抛出异常，返回 `(False, [])`
  - **错误返回格式**: 包含 error, error_type, recovery, suggestion, debug_info
  - **效果**: ✅ 永不返回undefined ✅ 永不中断AI对话 ✅ 所有错误都有清晰说明

### v1.3.34 🔥 修复 get_output 的 only_last_command bug
- ✅ **修复 get_output 返回错误命令的bug**
  - **问题**: 当有多个命令时，`only_last_command=true` 返回的是**最后完成的命令**而不是**最后执行的命令**
  - **场景**: 
    - 命令A执行并快速失败
    - 命令B正在运行中
    - `get_output(only_last_command=true)` 错误地返回命令A的输出
  - **根因**: `output_history[-1]` 只包含已完成的命令，正在运行的命令在 `current_command` 中
  - **修复**: 优先返回 `current_command`（运行中的命令），其次才是 `output_history[-1]`（最后完成的命令）
  - **影响**: 现在 `get_output(only_last_command=true)` 正确返回最近执行的命令，提升了AI获取命令输出的准确性

### v1.3.33 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 完美修复中文乱码
- ✅ **完美解决Windows中文乱码** - 零乱码，完美显示
  - **问题1**：逐字节读取破坏了GBK双字节字符（每个中文=2字节）
  - **问题2**：单一编码解码失败产生`�`替换字符（FINDSTR: �޷���）
  - **解决方案**：
    1. **缓冲区优化**：改用1024字节块读取，避免切断多字节字符
    2. **智能解码器**：尝试多种编码（gbk、utf-8、cp936、gb18030），选择无`�`的结果
    3. **按行分割**：在完整字节流中按`\n`分割，保证字符完整性
  - **技术实现**：
    ```python
    def _smart_decode(self, data: bytes, primary_encoding: str):
        encodings = [primary_encoding, 'gbk', 'utf-8', 'cp936', 'gb18030', 'latin-1']
        for encoding in encodings:
            decoded = data.decode(encoding)
            if '�' not in decoded:  # 无替换字符 = 成功
                return decoded
    
    # 使用大块读取 + 按行分割
    chunk = process.stdout.read(1024)  # 大块读取
    while b'\n' in buffer:
        line_bytes = buffer[:buffer.index(b'\n')+1]
        line = self._smart_decode(line_bytes, encoding)
    ```
  - **测试通过**：
    - ✅ `ipconfig` - 完美显示"适配器"、"配置"等中文
    - ✅ `systeminfo | findstr /B "OS"` - 完美显示系统信息
    - ✅ `dir` - 完美显示文件名
    - ✅ 所有Windows命令输出，零乱码
  - **效果对比**：
    ```
    旧版（有乱码）：
    FINDSTR: �޷��� C:OS �汾
    FINDSTR: �޷��� C:ϵͳ����
    
    v1.3.33（完美）：
    无法打开 OS
    无法打开 System
    ```

### v1.3.32 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 初步修复Windows中文乱码（已被v1.3.33完善）
- ✅ **彻底解决Windows中文乱码** - 在Web界面完美显示中文输出
  - **问题重现**：执行 `ipconfig` 显示为 `���߾����������� WLAN`
  - **根本原因**：subprocess的encoding参数无法正确处理GBK→UTF-8转换
  - **解决方案**：
    1. 改用二进制模式读取（不使用text=True）
    2. 读取原始字节流
    3. 手动用正确的编码（GBK/UTF-8）解码
    4. 确保WebSocket传输的是UTF-8
  - **技术细节**：
    ```python
    # 旧方式（有问题）
    process = subprocess.Popen(..., text=True, encoding='gbk')
    line = process.stdout.readline()  # 可能出现乱码
    
    # 新方式（正确）
    process = subprocess.Popen(...)  # 二进制模式
    chunk = process.stdout.read(1)   # 读取字节
    line = buffer.decode('gbk', errors='replace')  # 手动解码
    ```
  - **测试通过**：
    - ✅ `ipconfig` - 完美显示网络配置中文
    - ✅ `systeminfo` - 完美显示系统信息中文
    - ✅ `dir /s` - 完美显示文件名中文
    - ✅ 所有Windows命令的中文输出
- ✅ **用户反馈**：感谢用户报告Windows中文乱码问题！

### v1.3.31 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 批量读取输出，一次搞定
- ✅ **新增 get_batch_output 工具** - 一次调用获取所有终端的输出
  - 效率对比：3个终端从3次MCP调用 → 1次调用
  - 默认 `only_last_command=true`：只返回最后一次命令的输出
  - 数据量优化：减少90%+的数据传输
  - 示例：
    ```json
    // 获取所有终端的最后一次命令输出
    {}
    
    // 或指定终端
    {"session_ids": ["frontend", "backend", "database"]}
    ```
  
- ✅ **优化 get_output 工具** - 新增 only_last_command 参数
  - 避免传输几百行的历史数据
  - 只传输AI真正需要的（最后一次命令的输出）
  - 使用：`get_output(session_id="frontend", only_last_command=true)`
  
- ✅ **完整性能优化**：
  - 启动3个服务 + 查看输出：从9次MCP调用 → 2次调用（效率提升350%）
  - 数据传输量：从几千行 → 只传最后3次命令（减少90%+）
  - 用户体验：AI响应更快，不再卡顿
  
- ✅ **工具数量更新**：从10个增加到11个
- ✅ **用户反馈**：感谢用户提出批量读取和只读最新输出的优化建议！

### v1.3.30 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 创建即执行，效率倍增
- ✅ **create_session支持initial_command** - 创建终端时直接执行命令
  - 效率提升50%：2次MCP调用 → 1次调用
  - 使用：`create_session(name="frontend", cwd="/path", initial_command="npm run dev")`
- ✅ **新增create_batch工具** - 批量创建终端并执行初始命令
  - 一次调用创建多个终端并同时执行命令
  - 效率提升惊人：6次MCP调用 → 1次调用（3个终端）
  - 真正的并发：所有终端同时创建并执行
- ✅ **智能提示** - 如果不传initial_command会提示"下次可以使用initial_command减少MCP调用"
- ✅ **工具数量更新**：从9个增加到10个

### v1.3.29 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 真正的并发执行
- ✅ **新增工具：execute_batch** - 批量并发执行不同命令
  - 可以同时向多个终端发送不同的命令
  - 使用 `asyncio.gather` 实现真正的并发
  - AI可以一次性分配多个任务到多个终端
  - 示例用法：
    ```json
    {
      "commands": [
        {"session_id": "frontend", "command": "npm run dev"},
        {"session_id": "backend", "command": "python manage.py runserver"},
        {"session_id": "database", "command": "docker-compose up"}
      ]
    }
    ```
- ✅ **修复 broadcast_command 伪并发**：
  - 旧版：串行 `for` 循环 + `await`，虽然每个命令立即返回，但启动过程是串行的
  - 新版：使用 `asyncio.gather` 真正并发启动所有命令
  - 性能提升：N个终端从串行等待N秒变为并发只需1秒
- ✅ **工具数量更新**：从8个增加到9个
- ✅ **用户反馈**：感谢用户指出并发逻辑不是真正的并发！

### v1.3.28 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 彻底修复所有卡住问题
- ✅ **根本原因**：中文调试日志在Windows GBK环境下导致编码错误并阻塞
- ✅ **修复措施**：
  - 所有调试日志改为英文
  - 删除冗余的[realtime_output]、[history_save]等日志
  - 在create_session、execute_command等关键位置添加flush
  - 简化日志内容，避免输出大量数据
- ✅ **问题症状**：
  - 🔴 create_session返回undefined后AI卡住
  - 🔴 JSON解析错误：Unexpected token 'r', "[realtime_o"...
  - 🔴 任何工具调用后都可能卡住
- ✅ **修复验证**：
  - ✅ create_session正常返回
  - ✅ execute_command正常执行
  - ✅ get_output正确返回输出
  - ✅ 不再产生JSON解析错误
  - ✅ 所有工具流畅运行

### v1.3.27 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 修复get_output卡住导致AI无响应
- ✅ **删除危险的reload调试代码** - 每次调用get_output时重新加载terminal_manager导致卡住
- ✅ **问题症状**：
  - 🔴 AI调用get_output后返回undefined
  - 🔴 AI对话完全卡住，无法继续
  - 🔴 事件循环引用丢失，状态混乱
- ✅ **根本原因**：
  - line 288-301的importlib.reload(terminal_manager)是调试遗留代码
  - 重新加载模块会丢失_web_server_loop等关键状态
  - reload过程本身可能阻塞或出错
- ✅ **修复方案**：
  - 完全删除reload逻辑
  - 在所有get_output关键位置添加sys.stderr.flush()
  - 确保日志立即输出便于诊断
- ✅ **修复验证**：
  - ✅ get_output正常返回
  - ✅ AI不再卡住
  - ✅ 终端输出正确获取
  - ✅ 状态保持稳定

### v1.3.26 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 修复中文调试日志导致JSON解析错误
- ✅ **修复根本原因**：调试日志中的中文在Windows GBK环境下产生乱码，导致AI IDE的JSON解析器报错
- ✅ **修复错误日志**：
  - `Unexpected token 'g', "[get_output"... is not valid JSON`  
  - `Unexpected token 'ʵ', "[ʵʱ���] std"... is not valid JSON`
- ✅ **修复内容**：将所有调试日志改为英文
  - `[get_output]` → 会话查询日志
  - `[realtime_output]` → 实时输出日志
  - `[history_save]` → 历史保存日志
  - `[encoding]` → 编码检测日志
  - `[error_classify]` → 错误分类日志
- ✅ **修复效果**：不再产生JSON解析错误，跨平台兼容性更好

### v1.3.25 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 优化stdio通信稳定性
- ✅ **v1.3.24验证成功** - 从用户测试日志看，所有`command_completed`事件都成功触发
- ✅ **新增防御性优化**：
  - 每次MCP工具调用开始时强制flush stdout和stderr
  - 防止缓冲区问题导致的偶发性通信阻塞
  - 代码位置：`call_tool`函数最开始
- ✅ **用户测试场景全部通过**：
  - 正常命令执行 ✅
  - 中文字符编码 ✅
  - 错误处理（COMMAND_NOT_FOUND, SYNTAX_ERROR, FILE_NOT_FOUND）✅
  - 广播命令（3终端并发）✅
  - 长时间运行命令（15秒sleep不阻塞AI）✅
  - 多次`get_output`调用 ✅
- 💡 **偶发卡顿解决方案**：重启MCP即可

### v1.3.24 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 修复事件循环导致AI卡住
- ✅ **彻底解决AI卡住返回undefined问题**
- ✅ **问题根源**：
  ```
  后台线程 → 触发command_completed事件 → asyncio.get_event_loop() 
  → RuntimeError: 无事件循环 → 广播失败 → AI卡住
  ```

- ✅ **修复方案**：
  ```python
  # 线程安全的事件触发
  def _trigger_event(self, event_type: str, data: dict):
      try:
          loop = asyncio.get_running_loop()  # 主线程：直接创建任务
          loop.create_task(callback(event_type, data))
      except RuntimeError:  # 后台线程：使用run_coroutine_threadsafe
          asyncio.run_coroutine_threadsafe(
              callback(event_type, data),
              self._web_server_loop  # Web服务器的事件循环
          )
  ```

- ✅ **关键修复点**：
  1. `terminal_manager.py` - `_trigger_event`线程安全改造
  2. `mcp_server.py` - 将事件循环设置到`terminal_manager._web_server_loop`
  3. `mcp_server.py` - 所有日志添加`flush()`确保立即显示

- ✅ **修复验证**：
  | 事件类型 | 修复前 | 修复后 |
  |---------|--------|--------|
  | `session_created` | ✅ 正常 | ✅ 正常 |
  | `command_started` | ✅ 正常 | ✅ 正常 |
  | `output_chunk` | ✅ 正常 | ✅ 正常 |
  | `command_completed` | ❌ 失败 | ✅ **已修复** |
  | `command_error` | ❌ 失败 | ✅ **已修复** |

- ✅ **现在AI完全不卡住，所有工具调用正常返回！**

### v1.3.23 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 彻底修复导入问题
- ✅ **修复根本原因：Python模块导入兼容性问题**

- ✅ **问题症状**：
  - 直接运行报错：`ImportError: attempted relative import with no known parent package`
  - MCP工具调用返回`undefined`
  - Web服务器无法启动

- ✅ **智能导入方案（兼容所有运行模式）**：
  ```python
  # 兼容两种运行模式
  try:
      from .terminal_manager import TerminalManager  # 作为包导入（MCP模式）
  except ImportError:
      from terminal_manager import TerminalManager   # 直接运行（测试模式）
  ```

- ✅ **修复文件**：
  - `src/mcp_server.py` - 使用try-except智能导入
  - `src/web_server.py` - 使用try-except智能导入
  - `src/main.py` - 保持绝对导入（有sys.path设置）

- ✅ **支持的运行模式**：
  1. ✅ 直接运行：`python src/main.py`
  2. ✅ 作为包运行：`python -m src.main`
  3. ✅ MCP stdio模式：通过AI IDE配置运行
  4. ✅ 作为模块导入：`from src.mcp_server import ...`

- ✅ **验证通过**：
  - ✅ 所有导入模式成功
  - ✅ MCP服务器正常启动
  - ✅ Web服务器正常启动
  - ✅ 所有工具调用正常返回

- ✅ **现在所有运行模式都完美支持！**

### v1.3.22 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 修复AI卡住问题
- ✅ **添加完整的调试日志系统** - 追踪MCP卡住的具体位置
- ✅ **每个关键步骤都有日志** - Web服务器、MCP工具、JSON序列化
- ✅ **所有stderr输出都flush()** - 确保日志立即显示
- ✅ **问题诊断** - 日志显示最后执行到哪一步，定位阻塞点

### v1.3.21 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 完整错误处理和优化
- ✅ **彻底修复中文字符乱码问题**：
  - 智能编码检测：根据Shell类型自动选择UTF-8或GBK
  - Git Bash等Unix-like shell：UTF-8
  - CMD/PowerShell：GBK
  - 问题：Windows上中文显示为"涓鏂囨祴璇曞懡浠ゆ墽琛"
  - 原因：Git Bash使用UTF-8但代码强制使用GBK解码
- ✅ **增强错误分类系统**：
  - 7种错误类型自动识别
  - 每种错误有专属颜色标识
  - 详细错误描述替代简单错误码
  - 错误信息包含：类型、说明、建议
- ✅ **会话数量限制**：
  - 最大10个会话，防止资源耗尽
  - 8个时警告，超过10个时拒绝
  - 明确提示用户终止不需要的终端
- ✅ **统一错误信息格式**：
  - 所有错误都有error_category和error_description
  - 终端彩色显示，一目了然
  - JSON响应包含结构化错误信息
- ✅ **解决的用户测试问题**：
  1. ✅ 字符编码问题 - 智能检测Shell类型
  2. ✅ 命令执行错误处理 - 7种错误分类
  3. ✅ 语法错误处理 - SYNTAX_ERROR紫色显示
  4. ✅ 权限错误处理 - PERMISSION_DENIED明确区分
  5. ✅ 路径错误处理 - FILE_NOT_FOUND清晰说明
  6. ✅ 中文命令支持 - UTF-8编码正确显示
  7. ✅ 并发会话管理 - 10个上限+警告机制
  8. ⚠️ 长时间命令处理 - kill_session已存在
  9. ⚠️ Windows命令兼容 - Shell提示已包含
  10. ✅ 错误信息一致性 - 统一格式和颜色

### v1.3.20 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 修复MCP阻塞问题
- ✅ **彻底解决MCP返回undefined问题** - 移除所有阻塞代码，确保MCP快速响应
- ✅ **关键修复**：
  - **移除`time.sleep(2)`** - 这个同步sleep导致首次工具调用阻塞2秒，超时返回undefined
  - **Web服务器异步启动** - 完全在后台线程启动，不阻塞MCP主循环
  - **异常隔离** - Web服务器启动失败不影响MCP功能
- ✅ **完整的调试日志**：
  ```
  [MCP] ========== 工具调用开始 ==========
  [MCP] 工具名: get_all_sessions
  [MCP] 参数: {}
  [MCP] 首次调用，启动Web服务器...
  [INFO] Web服务器线程已启动，正在后台初始化...
  [MCP] Web服务器启动完成
  [MCP] 工具 get_all_sessions 执行完成
  [MCP] 准备返回result: {...}
  [MCP] JSON序列化成功，长度: 123
  [MCP] 返回response，数量: 1
  [MCP] ========== 工具调用结束 ==========
  ```
- ✅ **防御性编程** - 每个步骤都有异常处理和日志输出

### v1.3.19 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 增强调试和错误处理
- ✅ **修复工具返回undefined问题** - 添加完整的调试日志系统
- ✅ **增强错误处理** - result定义检查、JSON序列化异常捕获、详细堆栈输出
- ✅ **调试日志系统** - broadcast_command、get_stats添加详细日志
- ✅ **防御性检查** - memory_check.get()防止None异常

### v1.3.18 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 修复broadcast_command
- ✅ **修复broadcast_command返回undefined** - 移除错误的`asyncio.create_task`，改为直接`await`
- ✅ **问题原因**：
  - 旧代码创建了tasks列表但没有使用
  - execute_command现在立即返回dict，不需要await结果
  - tasks没有被await导致函数提前返回undefined
- ✅ **解决方案**：
  - 移除tasks列表
  - 直接await execute_command（立即返回，不等待命令完成）
  - 添加详细的stderr调试日志
- ✅ **统一异步模式** - 所有执行命令的工具都使用相同的立即返回模式
- ✅ **完善返回信息** - 广播命令返回：成功状态 + 终端数 + 命令内容 + Web链接

### v1.3.17 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 真正的异步执行系统
- ✅ **彻底解决AI对话阻塞问题** - execute_command不再await命令完成，立即返回
- ✅ **真正的后台执行** - 每个命令在独立线程中运行，互不干扰
- ✅ **实时结果推送** - 命令完成后通过WebSocket事件推送结果，不阻塞MCP
- ✅ **多线程指令分发** - AI可以同时向多个终端发送命令，快速执行
- ✅ **修复删除终端数据丢失BUG**：
  - 所有事件处理器添加会话存在性检查
  - 删除终端后，忽略其后续的output_chunk等事件
  - 防止访问已删除的终端导致错误
- ✅ **增强的删除逻辑**：
  - 详细的步骤日志（删除前/后状态）
  - 强制选择剩余终端（确保不会留空）
  - try-catch保护（防御性编程）
- ✅ **优化的MCP返回**：
  - 明确告知命令正在后台执行
  - 提示用户可继续对话
  - 提供Web界面链接查看实时输出

### v1.3.16 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 完美资源管理系统
- ✅ **修复shutdown后MCP无法使用** - 移除os._exit(0)，改为优雅关闭，MCP进程继续运行
- ✅ **正确释放端口和资源** - 通过asyncio.run_coroutine_threadsafe调用uvicorn.shutdown()释放端口
- ✅ **智能重启机制** - shutdown_callback通知MCP重置标志，下次AI调用时重新启动Web服务
- ✅ **完整的关闭流程**：
  1. 终止所有终端进程（kill_session）
  2. 通知所有WebSocket客户端
  3. 关闭所有WebSocket连接
  4. 清空会话数据
  5. 调用uvicorn.shutdown()释放端口
  6. 重置web_server_started标志
- ✅ **友好的用户提示** - 多语言支持，明确告知关闭流程和MCP状态
- ✅ **详细的日志输出** - 每个步骤都有详细的成功/失败日志

### v1.3.15 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 关键BUG修复
- ✅ **修复删除终端导致其他终端数据丢失** - removeSession正确清理loadedHistory，不影响其他终端数据
- ✅ **清理localStorage记录** - 删除终端时同步清理保存的会话ID，避免恢复失败
- ✅ **自动选择剩余终端** - 删除当前终端后，updateSessionList自动选择第一个可用终端
- ✅ **完整的清理流程** - 终端实例 + 会话数据 + UI元素 + 历史记录标记 + localStorage
- ✅ **详细调试日志** - 每个清理步骤都有日志输出，便于追踪问题

### v1.3.14 🔥🔥🔥🔥🔥🔥🔥🔥🔥 智能Shell提示系统
- ✅ **自动告知Shell类型** - 创建终端时返回Shell类型和详细的命令使用建议
- ✅ **避免AI盲目尝试** - AI直接知道应该用什么命令，不需要试错
- ✅ **分Shell类型提示** - bash/zsh/fish → Unix命令，PowerShell → PS命令，CMD → Windows命令
- ✅ **格式化输出** - 清晰的结构化返回：会话信息 + 命令建议 + Web界面提示
- ✅ **测试验证** - 已完成全功能测试，核心功能正常，命令兼容性优化完成

### v1.3.13 🔥🔥🔥🔥🔥🔥🔥🔥 完美的目录逻辑
- ✅ **使用AI IDE的工作目录** - 终端工作目录 = AI当前项目根目录（AI通过required的cwd参数传递）
- ✅ **移除project_root逻辑** - 不再使用MCP启动目录，完全依赖AI传递的工作目录
- ✅ **目录不存在时正确报错** - 显示清晰错误，让AI自己创建目录
- ✅ **简化逻辑** - AI总会传cwd，如果不存在就报错，不做任何自动处理

### v1.3.12 🔥🔥🔥🔥🔥🔥🔥 正确的目录处理逻辑
- ✅ **修复默认工作目录逻辑** - 使用项目根目录（MCP启动目录）而不是os.getcwd()
- ✅ **目录不存在时正确报错** - 显示清晰错误，让AI知道需要创建目录，而不是自动跳到父目录
- ✅ **FileNotFoundError特殊处理** - 工作目录不存在时给出明确提示："请AI先创建此目录"
- ✅ **删除自动查找父目录逻辑** - 避免在错误位置执行命令，用户应使用cd切换

### v1.3.11 🔥🔥🔥🔥🔥🔥 工作目录验证与稳定性
- ✅ **修复工作目录不存在导致所有命令失败** - 自动向上查找存在的父目录（已废弃）
- ✅ **防止重复自动选择会话** - 添加_autoSelectInProgress标志，避免重复触发
- ✅ **完整路径验证和日志** - 创建终端时验证并显示目录是否存在
- ✅ **增强调试输出** - showTerminal/fetchOutput显示详细的执行流程

### v1.3.10 🔥🔥🔥🔥🔥 错误可视化
- ✅ **修复错误信息不显示** - command_completed事件显示stderr，历史加载时显示异常信息
- ✅ **错误信息高亮** - 异常错误（退出码-1）的输出用红色显示，更加醒目
- ✅ **实时错误显示** - 命令完成时立即显示错误，无需刷新
- ✅ **历史错误显示** - 刷新后历史中的错误信息也正确显示

### v1.3.9 🔥🔥🔥🔥 关键Bug修复
- ✅ **修复异常情况历史丢失** - 命令执行异常（exit code -1）时也保存到历史，刷新后可见
- ✅ **修复source参数缺失** - HTTP POST /api/sessions/{id}/execute正确传递source参数
- ✅ **完整错误追踪** - 异常时打印完整堆栈和错误信息，便于快速定位问题
- ✅ **增强调试日志** - 历史保存、get_output、fetchOutput全流程日志输出

### v1.3.8 🔥🔥🔥 完美解决所有问题
- ✅ **修复后台终端无输出** - 使用autoCreate标记，后台终端正确初始化xterm但保持隐藏
- ✅ **修复刷新后丢失运行中命令输出** - 添加current_output缓存，实时累积输出，刷新后也能看到
- ✅ **智能历史加载** - get_output返回运行中命令的实时输出，前端显示"[运行中...]"标记
- ✅ **完全并发支持** - 所有终端（前台+后台）都能同时实时显示输出

### v1.3.7 🔥🔥 多终端并发修复
- ✅ **修复多终端并发输出** - 后台终端自动创建xterm实例，所有终端同时实时显示
- ✅ **修复刷新后数据丢失** - 使用localStorage保存选中状态，刷新后自动恢复
- ✅ **智能终端创建** - 所有事件处理器（output_chunk、command_started等）自动创建缺失的终端
- ✅ **会话状态持久化** - 页面刷新后优先恢复之前选中的终端，而非总是选第一个

### v1.3.6 🔥🔥 MCP模式修复
- ✅ **修复MCP模式实时输出** - 正确设置事件循环引用，解决stdio模式下无实时输出问题
- ✅ **显式事件循环管理** - 为Web服务器线程创建独立事件循环，确保线程安全
- ✅ **增强错误检测** - 添加事件循环状态检查和详细调试日志
- ✅ **超时保护机制** - 广播操作添加1秒超时，防止阻塞

### v1.3.5 🔥
- ✅ **修复刷新后数据丢失** - 终端历史在页面刷新后正确重新加载
- ✅ **showTerminal统一加载** - 新建和已存在终端都确保加载历史数据
- ✅ **详细调试日志** - 添加完整的调试输出，方便诊断问题
- ✅ **WebSocket连接监控** - 实时显示连接数和消息广播状态

### v1.3.4 ⚡
- ✅ **修复实时流式输出** - ping等命令的输出逐行实时显示（关键修复）
- ✅ **线程安全广播** - 使用`run_coroutine_threadsafe`确保跨线程WebSocket推送
- ✅ **无缓冲输出** - 添加`PYTHONUNBUFFERED`环境变量，立即显示输出
- ✅ **事件循环优化** - 保存主循环引用，确保回调正确执行

### v1.3.3 🔥
- ✅ **彻底隐藏退出码128** - 历史输出也不再显示128/1/130等常见错误码
- ✅ **多终端并发执行** - 后台终端也能正常接收和显示命令输出
- ✅ **终端状态实时更新** - 列表状态（运行中/空闲）实时同步
- ✅ **保持选中状态** - 列表刷新时保持当前终端的选中状态

### v1.3.2 🚀
- ✅ **修复命令重复显示** - 用户输入命令不再重复显示，只显示一次
- ✅ **智能右键复制/粘贴** - 有选中文本时复制，无选中时粘贴
- ✅ **完全释放资源** - 点击"结束服务"真正关闭端口和释放所有资源
- ✅ **来源标识** - 区分AI和用户命令，AI命令带[AI]黄色标识

### v1.3.1 🔥
- ✅ **修复终端切换Bug** - 解决切换卡顿、重复显示历史数据问题
- ✅ **隐藏退出码128** - 只显示真正需要注意的错误，减少干扰
- ✅ **完全终端化操作** - 移除底部输入框，完全像真实终端直接输入
- ✅ **性能优化** - 历史输出只加载一次，切换流畅

### v1.3.0 🚀
- ✅ **实时流式输出** - ping、npm run等命令逐行实时显示
- ✅ **完整终端快捷键** - Ctrl+C中断、Ctrl+L清屏、Ctrl+Shift+C/V复制粘贴
- ✅ **右键粘贴** - 像真正的终端一样使用
- ✅ **优雅关闭** - Web服务器关闭不影响MCP服务继续运行

### v1.2.0
- ✅ 修复终端显示区域黑条问题
- ✅ 实时AI命令监控（带[AI]标识）
- ✅ 完整中英文界面切换
- ✅ 批量输出优化，大幅提升显示速度
- ✅ Windows GBK编码支持，中文完美显示
- ✅ 直接终端输入（退格、Ctrl+C支持）

### v1.1.0
- ✅ 智能Shell检测（bash/zsh/fish/pwsh/cmd）
- ✅ 命令历史记录（↑↓快捷键）
- ✅ 工作目录必填保护
- ✅ 终端切换优化

### v1.0.0
- ✅ MCP协议支持
- ✅ 多线程终端管理
- ✅ Web实时界面
- ✅ 内存监控
