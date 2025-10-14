"""
终端管理器 - 管理多个终端会话
"""
import asyncio
import os
import platform
import psutil
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import threading
import queue


class TerminalSession:
    """终端会话类"""
    
    def __init__(self, session_id: str, shell_type: str, cwd: str = None):
        self.session_id = session_id
        self.shell_type = shell_type
        
        # 工作目录：AI IDE传递的当前工作目录（required参数，总会有值）
        # 如果AI没传（理论上不应该），就用当前目录
        self.cwd = os.path.abspath(cwd) if cwd else os.getcwd()
        
        # 不在这里验证目录是否存在，让命令执行时报错
        # 这样AI能看到错误并自己创建目录
        
        self.status = "idle"  # idle, running, completed, waiting_input
        self.created_at = datetime.now()
        self.last_command = None
        self.last_command_time = None
        self.last_completed_at = None  # 🆕 最后完成时间
        self.last_exit_code = None  # 🆕 最后退出码
        self.output_history = []
        self.current_output = ""  # 当前运行命令的实时输出缓存
        self.current_command = None  # 当前运行的命令
        self.current_command_start_time = None  # 🆕 当前命令开始时间
        self.process = None
        self.output_queue = queue.Queue()
        self.lock = threading.Lock()
        
        # 追踪get_output调用（用于检测AI重复查询）
        self.get_output_call_count = 0  # 对当前命令的查询次数
        self.last_output_length = 0  # 上次输出的长度
        
        # 🆕 v2.0: 交互检测
        self.waiting_input = False  # 是否等待输入
        self.last_prompt_line = None  # 最后一行输出（可能是提示）
        self.interaction_detected_at = None  # 检测到交互的时间
        
        # 🆕 v2.0: 环境信息缓存
        self.environment = {}  # 环境信息（node版本、python版本等）
        self.environment_checked_at = None  # 环境检查时间
        
    def get_info(self) -> dict:
        """获取会话信息"""
        info = {
            "session_id": self.session_id,
            "shell_type": self.shell_type,
            "cwd": self.cwd,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_command": self.last_command,
            "last_command_time": self.last_command_time.isoformat() if self.last_command_time else None,
            "is_alive": self.process is not None and self.process.poll() is None,
            "query_count": self.get_output_call_count,  # 🎯 查询次数
        }
        
        # 添加运行时长
        if self.current_command_start_time:
            running_seconds = (datetime.now() - self.current_command_start_time).total_seconds()
            info["running_seconds"] = round(running_seconds, 1)
        
        # 添加查询警告
        if self.get_output_call_count >= 3:
            info["query_warning"] = f"已查询{self.get_output_call_count}次，还剩{max(0, 5-self.get_output_call_count)}次将自动终止"
        
        return info


class TerminalManager:
    """终端管理器"""
    
    def _smart_decode(self, data: bytes, primary_encoding: str) -> str:
        """
        智能解码：尝试多种编码方式，避免出现乱码
        
        优先级策略：
        1. 优先尝试 UTF-8（大多数程序输出都是UTF-8，包括Node.js、Python、emoji等）
        2. 如果UTF-8失败，尝试 GBK（Windows系统命令）
        3. 最后尝试其他编码
        
        Args:
            data: 要解码的字节数据
            primary_encoding: 参考编码（用于确定备选编码列表）
        
        Returns:
            解码后的字符串
        """
        if not data:
            return ''
        
        # 🔧 修复：优先尝试UTF-8（适用于大多数程序输出）
        # 原因：Node.js/Python/npm等程序输出UTF-8，emoji也是UTF-8
        encodings_to_try = [
            'utf-8',      # ← 优先UTF-8（程序输出、emoji）
            'gbk',        # ← 次选GBK（Windows系统命令）
            'cp936',      # Windows简体中文
            'gb18030',    # GBK的超集
            'latin-1'     # 最后的备选，能解码任何字节
        ]
        
        # 去重，保持顺序
        seen = set()
        encodings_to_try = [x for x in encodings_to_try if not (x.lower() in seen or seen.add(x.lower()))]
        
        # 尝试每种编码
        for encoding in encodings_to_try:
            try:
                decoded = data.decode(encoding)
                # 如果解码成功且不包含replacement字符，就使用这个结果
                if '�' not in decoded:
                    return decoded
                # 如果包含replacement字符但这是最后一种编码，也返回
                if encoding == encodings_to_try[-1]:
                    return decoded
            except (UnicodeDecodeError, LookupError):
                continue
        
        # 如果所有编码都失败（理论上不应该发生），使用errors='ignore'
        return data.decode('utf-8', errors='ignore')
    
    def __init__(self):
        self.sessions: Dict[str, TerminalSession] = {}
        self.command_tracker = defaultdict(list)  # 追踪相同命令的执行
        self.lock = threading.Lock()
        self.memory_threshold = 85  # 内存阈值百分比（从95降到85更安全）
        self.session_threshold = 64  # 超过64个终端才检查内存
        self.event_callbacks = defaultdict(list)  # 事件回调字典
        
        # 启动智能清理线程（超过64个终端+内存不足时自动清理最老的）
        self._start_smart_cleanup_thread()
        
    def get_preferred_shell(self) -> str:
        """智能获取首选Shell类型 - 优先bash，其次powershell，最后cmd
        
        环境变量支持：
        - AI_MCP_PREFERRED_SHELL: 强制指定shell（bash/powershell/cmd/zsh等）
        """
        import sys
        
        # 1. 优先检查环境变量强制指定
        env_shell = os.environ.get('AI_MCP_PREFERRED_SHELL', '').strip().lower()
        if env_shell:
            print(f"[ShellDetect] ✅ 环境变量指定: AI_MCP_PREFERRED_SHELL={env_shell}", file=sys.stderr)
            sys.stderr.flush()
            return env_shell
        
        system = platform.system().lower()
        
        print(f"[ShellDetect] 开始检测首选终端，系统: {system}", file=sys.stderr)
        sys.stderr.flush()
        
        if system == "windows":
            # Windows shell优先级：bash → powershell → pwsh → cmd（Git Bash首选，跨平台兼容性最佳）
            shells_priority = [
                ("bash", [  # Git Bash 或 WSL bash（第一优先）
                    r"C:\Program Files\Git\bin\bash.exe",
                    r"C:\Program Files (x86)\Git\bin\bash.exe",
                    os.path.expandvars(r"%PROGRAMFILES%\Git\bin\bash.exe"),
                    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Git\bin\bash.exe"),
                    os.path.expanduser(r"~\scoop\apps\git\current\bin\bash.exe"),  # Scoop安装
                    "bash"  # PATH中的bash（WSL）
                ]),
                ("powershell", ["powershell"]),  # PowerShell（第二优先）
                ("pwsh", ["pwsh"]),  # PowerShell Core（第三优先）
                ("cmd", ["cmd"]),  # CMD（最后选择）
                ("zsh", ["zsh"]),  # 其他shell
                ("fish", ["fish"])
            ]
            
        elif system == "darwin":
            # macOS shell优先级：zsh → bash → fish → sh（macOS默认zsh）
            shells_priority = [
                ("zsh", ["zsh"]),
                ("bash", ["bash"]),
                ("fish", ["fish"]),
                ("sh", ["sh"])
            ]
            
        else:
            # Linux/Unix shell优先级：bash → zsh → fish → dash → sh（标准bash优先）
            shells_priority = [
                ("bash", ["bash"]),
                ("zsh", ["zsh"]),
                ("fish", ["fish"]),
                ("dash", ["dash"]),
                ("sh", ["sh"])
            ]
        
        # 检测第一个可用的shell
        for shell_type, shell_commands in shells_priority:
            print(f"[ShellDetect] 检测 {shell_type}...", file=sys.stderr)
            sys.stderr.flush()
            
            for cmd in shell_commands:
                # 优先检查文件路径是否存在（Git Bash等固定位置的shell）
                if os.path.sep in cmd or cmd.endswith('.exe'):
                    print(f"[ShellDetect] 检查路径: {cmd}", file=sys.stderr)
                    sys.stderr.flush()
                    if os.path.exists(cmd):
                        print(f"[ShellDetect] ✅ 找到shell: {shell_type} at {cmd}", file=sys.stderr)
                        sys.stderr.flush()
                        return shell_type
                    else:
                        print(f"[ShellDetect] ❌ 路径不存在: {cmd}", file=sys.stderr)
                        sys.stderr.flush()
            
            # 如果所有路径都不存在，再检查是否在PATH中
            for cmd in shell_commands:
                if not (os.path.sep in cmd or cmd.endswith('.exe')):
                    print(f"[ShellDetect] 检查PATH: {cmd}", file=sys.stderr)
                    sys.stderr.flush()
                    if self._command_exists(cmd):
                        print(f"[ShellDetect] ✅ 找到shell: {shell_type} (PATH)", file=sys.stderr)
                        sys.stderr.flush()
                        return shell_type
        
        # 默认返回
        print(f"[ShellDetect] ⚠️ 未找到bash/powershell，使用默认", file=sys.stderr)
        sys.stderr.flush()
        return "powershell" if system == "windows" else "bash"
    
    def _command_exists(self, command: str) -> bool:
        """检查命令是否存在"""
        try:
            if platform.system().lower() == "windows":
                subprocess.run(["where", command], capture_output=True, check=True)
            else:
                subprocess.run(["which", command], capture_output=True, check=True)
            return True
        except:
            return False
    
    def _get_shell_executable(self, shell_type: str) -> str:
        """获取Shell可执行文件路径"""
        system = platform.system().lower()
        
        # Windows特殊处理
        if system == "windows":
            if shell_type == "bash":
                # Git Bash路径
                git_bash_paths = [
                    r"C:\Program Files\Git\bin\bash.exe",
                    r"C:\Program Files (x86)\Git\bin\bash.exe"
                ]
                for path in git_bash_paths:
                    if os.path.exists(path):
                        return path
                return "bash"  # 回退到PATH中的bash
            
            elif shell_type == "pwsh":
                return "pwsh"
            elif shell_type == "powershell":
                return "powershell"
            elif shell_type == "cmd":
                return "cmd"
        
        # Unix-like系统
        return shell_type  # zsh, bash, fish等直接使用命令名
    
    def register_callback(self, callback, event_type: str = 'default'):
        """注册事件回调"""
        self.event_callbacks[event_type].append(callback)
    
    def _trigger_event(self, event_type: str, data: dict):
        """触发事件（线程安全）"""
        import sys
        print(f"[DEBUG] Trigger event: {event_type}, data keys: {list(data.keys())}", file=sys.stderr)
        sys.stderr.flush()
        
        # 触发默认回调
        for callback in self.event_callbacks['default']:
            try:
                # 线程安全的事件触发：
                # 1. 首先尝试获取当前运行的事件循环（主线程）
                # 2. 如果没有，说明在后台线程中，需要使用run_coroutine_threadsafe
                import asyncio
                import threading
                
                try:
                    # 尝试获取当前线程的事件循环
                    loop = asyncio.get_running_loop()
                    # 如果成功，直接创建任务
                    loop.create_task(callback(event_type, data))
                    print(f"[DEBUG] Event {event_type} triggered in event loop", file=sys.stderr)
                except RuntimeError:
                    # 没有运行中的事件循环，说明在后台线程中
                    # 需要找到Web服务器的事件循环并调度任务
                    # 这个事件循环会在web_server中设置
                    if hasattr(self, '_web_server_loop') and self._web_server_loop:
                        print(f"[DEBUG] Event {event_type} via run_coroutine_threadsafe", file=sys.stderr)
                        sys.stderr.flush()
                        asyncio.run_coroutine_threadsafe(
                            callback(event_type, data),
                            self._web_server_loop
                        )
                    else:
                        print(f"[WARNING] Cannot trigger event {event_type}: no event loop", file=sys.stderr)
                        sys.stderr.flush()
                        
            except Exception as e:
                print(f"[ERROR] Event callback failed: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
                sys.stderr.flush()
    
    def create_session(self, name: str = None, shell_type: str = None, cwd: str = None) -> str:
        """创建新的终端会话（无数量限制，超过64个+内存不足时智能清理）"""
        import sys
        
        # 已移除会话数量限制 - 终端无上限
        # 超过64个终端+内存不足时，智能清理最老的已完成/空闲终端
        
        session_id = name or str(uuid.uuid4())[:8]
        
        if shell_type is None:
            shell_type = self.get_preferred_shell()
        
        # 获取shell可执行文件路径（用于日志）
        shell_exe = self._get_shell_executable(shell_type)
        
        with self.lock:
            session = TerminalSession(session_id, shell_type, cwd)
            self.sessions[session_id] = session
        
        dir_exists = os.path.exists(session.cwd)
        print(f"[INFO] Create session: {session_id}", file=sys.stderr)
        print(f"       Shell type: {shell_type}", file=sys.stderr)
        print(f"       Shell path: {shell_exe}", file=sys.stderr)
        print(f"       Working dir: {session.cwd}", file=sys.stderr)
        print(f"       Dir exists: {dir_exists}", file=sys.stderr)
        sys.stderr.flush()
        if not dir_exists:
            print(f"       [WARNING] Directory not found! AI should create it first", file=sys.stderr)
            sys.stderr.flush()
        
        # 触发会话创建事件
        self._trigger_event('session_created', {
            'session_id': session_id,
            'shell_type': shell_type,
            'shell_exe': shell_exe
        })
            
        return session_id
    
    async def execute_command(
        self, 
        session_id: str, 
        command: str, 
        timeout: int = None,
        source: str = "ai"
    ) -> dict:
        """在指定会话中执行命令（真正的异步非阻塞）
        
        立即返回，不等待命令完成！命令在后台执行，结果通过事件推送。
        """
        try:
            if session_id not in self.sessions:
                error_msg = f"会话 {session_id} 不存在"
                print(f"[ERROR] execute_command: {error_msg}", file=sys.stderr)
                sys.stderr.flush()
                return {
                    "status": "error",
                    "error": error_msg,
                    "session_id": session_id,
                    "recovery": "请先使用 create_session 创建会话"
                }
        
            session = self.sessions[session_id]
        
            # 检查是否需要终止旧的相同命令
            await self._check_duplicate_command(session, command)
            
            # 更新会话状态
            with session.lock:
                session.status = "running"
                session.last_command = command
                session.last_command_time = datetime.now()
            
            # 触发命令开始事件
            self._trigger_event('command_started', {
                'session_id': session_id,
                'command': command,
                'source': source
            })
            
            # 在后台线程中执行命令（不等待完成！）
            def execute_in_background():
                result = self._execute_sync(session, command, timeout)
                
                # 执行完成后触发事件
                self._trigger_event('command_completed', {
                    'session_id': session_id,
                    'command': command,
                    'stdout': result[0],
                    'stderr': result[1],
                    'returncode': result[2]
                })
                    
                # 重置查询计数器
                with session.lock:
                    session.get_output_call_count = 0
                    session.last_output_length = 0
            
            # 启动后台线程，不等待
            thread = threading.Thread(target=execute_in_background, daemon=True)
            thread.start()
            
            # 立即返回，不等待命令完成
            return {
                "status": "started",
                "session_id": session_id,
                "command": command,
                "message": "命令已在后台开始执行"
            }
                
        except Exception as e:
            # 全局异常捕获：永不卡住
            print(f"[ERROR] execute_command异常: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
            # 返回错误信息而不是抛出异常
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "session_id": session_id,
                "command": command,
                "recovery": "系统已捕获错误，终端会话仍可用"
            }
    
    def _execute_sync(
        self, 
        session: TerminalSession, 
        command: str, 
        timeout: int = None
    ) -> Tuple[str, str, int]:
        """同步执行命令"""
        try:
            # 获取shell可执行文件
            shell_exe = self._get_shell_executable(session.shell_type)
            
            # 根据shell类型构建命令
            if session.shell_type in ["bash", "zsh", "fish", "sh", "dash"]:
                # Unix-like shell使用 -c 参数
                shell_cmd = [shell_exe, "-c", command]
                
            elif session.shell_type in ["powershell", "pwsh"]:
                # PowerShell使用 -Command 参数
                shell_cmd = [shell_exe, "-NoLogo", "-NonInteractive", "-Command", command]
                
            elif session.shell_type == "cmd":
                # CMD使用 /c 参数
                shell_cmd = [shell_exe, "/c", command]
                
            else:
                # 未知shell类型，尝试使用通用方式
                shell_cmd = [shell_exe, "-c", command]
            
            # 智能检测编码
            import sys
            if platform.system().lower() == "windows":
                # Windows上根据shell类型选择编码
                if session.shell_type in ['bash', 'zsh', 'fish', 'sh']:
                    # Git Bash等Unix-like shell使用UTF-8
                    encoding = 'utf-8'
                else:
                    # CMD和PowerShell使用GBK
                    encoding = 'gbk'
            else:
                # Linux/macOS使用UTF-8
                encoding = 'utf-8'
            
            print(f"[encoding] session={session.session_id} shell={session.shell_type} encoding={encoding}", file=sys.stderr)
            
            # 设置环境变量禁用缓冲
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            
            # 执行命令（使用二进制模式，手动解码以确保正确处理编码）
            process = subprocess.Popen(
                shell_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0,  # 无缓冲
                env=env,
                cwd=session.cwd
            )
            
            session.process = process
            
            # 设置当前命令和清空输出缓存
            with session.lock:
                session.current_command = command
                session.current_output = ""
                session.current_command_start_time = datetime.now()  # 🆕 记录开始时间
                session.get_output_call_count = 0  # 重置查询计数
                session.last_output_length = 0  # 重置输出长度
            
            # 实时读取输出的线程（使用更大的缓冲区，避免破坏多字节字符）
            stdout_lines = []
            stderr_lines = []
            
            def read_stdout():
                try:
                    buffer = b''
                    while True:
                        # 读取更大的块（1024字节），避免破坏多字节字符
                        chunk = process.stdout.read(1024)
                        if not chunk:
                            # 处理剩余buffer
                            if buffer:
                                try:
                                    line = self._smart_decode(buffer, encoding)
                                    stdout_lines.append(line)
                                    with session.lock:
                                        session.current_output += line
                                    for callback in self.event_callbacks['output_chunk']:
                                        try:
                                            callback({
                                                'session_id': session.session_id,
                                                'chunk': line,
                                                'stream': 'stdout'
                                            })
                                        except Exception as e:
                                            print(f"[ERROR] output_chunk callback: {e}")
                                except Exception as e:
                                    print(f"[ERROR] decode buffer: {e}")
                            break
                        
                        buffer += chunk
                        
                        # 按行分割并发送（保留最后的不完整行）
                        while b'\n' in buffer:
                            line_end = buffer.index(b'\n') + 1
                            line_bytes = buffer[:line_end]
                            buffer = buffer[line_end:]
                            
                            try:
                                line = self._smart_decode(line_bytes, encoding)
                            except Exception:
                                line = line_bytes.decode('utf-8', errors='replace')
                        
                        stdout_lines.append(line)
                        
                        # 累积到current_output
                        with session.lock:
                            session.current_output += line
                        
                                # 实时推送输出到WebSocket
                        for callback in self.event_callbacks['output_chunk']:
                            try:
                                callback({
                                    'session_id': session.session_id,
                                    'chunk': line,
                                    'stream': 'stdout'
                                })
                            except Exception as e:
                                        print(f"[ERROR] output_chunk callback: {e}")
                            except Exception as e:
                                print(f"[ERROR] decode stdout: {e}")
                    
                    process.stdout.close()
                except Exception as e:
                    print(f"[ERROR] read_stdout failed: {e}")
                    import traceback
                    traceback.print_exc()
            
            def read_stderr():
                try:
                    buffer = b''
                    while True:
                        # 读取更大的块（1024字节），避免破坏多字节字符
                        chunk = process.stderr.read(1024)
                        if not chunk:
                            # 处理剩余buffer
                            if buffer:
                                try:
                                    line = self._smart_decode(buffer, encoding)
                                    stderr_lines.append(line)
                                    with session.lock:
                                        session.current_output += line
                                    for callback in self.event_callbacks['output_chunk']:
                                        try:
                                            callback({
                                                'session_id': session.session_id,
                                                'chunk': line,
                                                'stream': 'stderr'
                                            })
                                        except Exception as e:
                                            print(f"[ERROR] output_chunk callback: {e}")
                                except Exception as e:
                                    print(f"[ERROR] decode buffer: {e}")
                            break
                        
                        buffer += chunk
                        
                        # 按行分割并发送（保留最后的不完整行）
                        while b'\n' in buffer:
                            line_end = buffer.index(b'\n') + 1
                            line_bytes = buffer[:line_end]
                            buffer = buffer[line_end:]
                            
                            try:
                                line = self._smart_decode(line_bytes, encoding)
                            except Exception:
                                line = line_bytes.decode('utf-8', errors='replace')
                        
                        stderr_lines.append(line)
                        
                        # 累积到current_output
                        with session.lock:
                            session.current_output += line
                        
                                # 实时推送错误输出到WebSocket
                        for callback in self.event_callbacks['output_chunk']:
                            try:
                                callback({
                                    'session_id': session.session_id,
                                    'chunk': line,
                                    'stream': 'stderr'
                                })
                            except Exception as e:
                                        print(f"[ERROR] output_chunk callback: {e}")
                            except Exception as e:
                                print(f"[ERROR] decode stderr: {e}")
                    
                    process.stderr.close()
                except Exception as e:
                    print(f"[ERROR] read_stderr failed: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 启动实时读取线程
            stdout_thread = threading.Thread(target=read_stdout, daemon=True)
            stderr_thread = threading.Thread(target=read_stderr, daemon=True)
            stdout_thread.start()
            stderr_thread.start()
            
            # 等待进程结束
            returncode = process.wait(timeout=timeout)
            
            # 等待读取线程结束
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)
            
            # 合并输出
            stdout = ''.join(stdout_lines)
            stderr = ''.join(stderr_lines)
            
            # 保存输出
            output = stdout + stderr
            with session.lock:
                # 错误分类
                error_category = None
                error_description = None
                
                if returncode != 0:
                    stderr_lower = stderr.lower()
                    stdout_lower = stdout.lower()
                    combined_output = (stderr_lower + stdout_lower).strip()
                    
                    # 识别命令不存在错误
                    if 'command not found' in combined_output or 'not recognized' in combined_output or 'is not recognized as' in combined_output:
                        error_category = "COMMAND_NOT_FOUND"
                        cmd_name = command.split()[0] if command.split() else command
                        error_description = f"命令不存在：{cmd_name}"
                        
                        # 🆕 智能建议：检测是否是Windows特定命令在bash中执行
                        windows_commands = ['dir', 'cls', 'copy', 'move', 'del', 'rd', 'md', 'type', 'findstr', 'systeminfo', 'tasklist', 'ipconfig', 'netstat']
                        bash_commands = ['ls', 'clear', 'cp', 'mv', 'rm', 'rmdir', 'mkdir', 'cat', 'grep', 'uname', 'ps', 'ifconfig', 'ss']
                        
                        if cmd_name.lower() in windows_commands and session.shell_type == 'bash':
                            # Windows命令在bash中执行失败
                            history_item["ai_suggestion"] = {
                                "issue": f"Windows命令 '{cmd_name}' 在bash终端中不可用",
                                "solution": "需要在Windows终端（cmd/powershell）中执行",
                                "action": f"create_session(shell_type='cmd') 然后 execute_command('{command}')",
                                "reason": f"命令 '{cmd_name}' 是Windows特定命令，bash不支持"
                            }
                        elif cmd_name.lower() in bash_commands and session.shell_type in ['cmd', 'powershell']:
                            # Bash命令在Windows终端中执行失败
                            history_item["ai_suggestion"] = {
                                "issue": f"Unix/Linux命令 '{cmd_name}' 在{session.shell_type}终端中不可用",
                                "solution": "需要在bash终端中执行",
                                "action": f"create_session(shell_type='bash') 然后 execute_command('{command}')",
                                "reason": f"命令 '{cmd_name}' 是Unix/Linux命令，{session.shell_type}不支持"
                            }
                    
                    elif 'permission denied' in combined_output or 'access denied' in combined_output:
                        error_category = "PERMISSION_DENIED"
                        error_description = "权限不足，可能需要管理员权限"
                    elif 'no such file or directory' in combined_output:
                        error_category = "FILE_NOT_FOUND"
                        error_description = "文件或目录不存在"
                    elif 'syntax error' in combined_output or 'unexpected' in combined_output:
                        error_category = "SYNTAX_ERROR"
                        error_description = "命令语法错误，请检查命令格式"
                    elif returncode == 130:
                        error_category = "USER_INTERRUPTED"
                        error_description = "用户中断（Ctrl+C）"
                    elif returncode == 128:
                        error_category = "INVALID_ARGUMENT"
                        error_description = "无效的命令参数"
                    else:
                        error_category = "GENERAL_ERROR"
                        error_description = f"命令执行失败，退出码：{returncode}"
                    
                
                history_item = {
                    "command": command,
                    "output": output,
                    "returncode": returncode,
                    "timestamp": datetime.now().isoformat()
                }
                
                # 添加错误分类信息
                if error_category:
                    history_item["error_category"] = error_category
                    history_item["error_description"] = error_description
                
                session.output_history.append(history_item)
                session.status = "idle" if returncode == 0 else "completed"
                session.process = None
                # 🆕 记录完成信息
                session.last_exit_code = returncode
                session.last_completed_at = datetime.now()
                session.waiting_input = False  # 重置交互标志
                # 清空当前命令和输出缓存
                session.current_command = None
                session.current_output = ""
                session.current_command_start_time = None
            
            return stdout, stderr, returncode
            
        except subprocess.TimeoutExpired:
            process.kill()
            error_msg = "命令执行超时"
            with session.lock:
                # 保存错误到历史
                session.output_history.append({
                    "command": command,
                    "output": error_msg,
                    "returncode": -1,
                    "timestamp": datetime.now().isoformat()
                })
                session.status = "idle"
                session.process = None
                session.last_exit_code = -1  # 🆕
                session.last_completed_at = datetime.now()  # 🆕
                session.current_command = None
                session.current_output = ""
                session.current_command_start_time = None  # 🆕
            return "", error_msg, -1
        except FileNotFoundError as e:
            # 工作目录不存在的特殊处理
            error_msg = f"Working directory not found: {session.cwd}\nPlease create it first or use cd to switch directory"
            print(f"[ERROR] Working directory not found: {session.cwd}")
            
            with session.lock:
                # 保存错误到历史
                session.output_history.append({
                    "command": command,
                    "output": error_msg,
                    "returncode": -1,
                    "timestamp": datetime.now().isoformat()
                })
                session.status = "idle"
                session.process = None
                session.last_exit_code = -1  # 🆕
                session.last_completed_at = datetime.now()  # 🆕
                session.current_command = None
                session.current_output = ""
                session.current_command_start_time = None  # 🆕
            return "", error_msg, -1
            
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Command execution exception: {command}, error: {error_msg}")
            import traceback
            traceback.print_exc()
            
            with session.lock:
                # 保存错误到历史
                session.output_history.append({
                    "command": command,
                    "output": error_msg,
                    "returncode": -1,
                    "timestamp": datetime.now().isoformat()
                })
                session.status = "idle"
                session.process = None
                session.last_exit_code = -1  # 🆕
                session.last_completed_at = datetime.now()  # 🆕
                session.current_command = None
                session.current_output = ""
                session.current_command_start_time = None  # 🆕
            return "", error_msg, -1
    
    async def _check_duplicate_command(self, session: TerminalSession, command: str):
        """检查并处理重复命令"""
        # 识别项目级别的命令（如 npm run, python manage.py 等）
        project_commands = ["npm run", "yarn", "python -m", "node", "npm start", "npm dev"]
        
        is_project_cmd = any(cmd in command for cmd in project_commands)
        
        if is_project_cmd:
            # 检查是否有相同的命令正在运行
            for sid, s in self.sessions.items():
                if s.status == "running" and s.last_command == command and s.cwd == session.cwd:
                    # 终止旧命令
                    await self.kill_session(sid)
                    break
    
    def interrupt_commands(self, session_ids: List[str]) -> dict:
        """
        批量并发中断多个终端的命令（v2.0.3新增）
        
        Args:
            session_ids: 要中断的会话ID列表
        
        Returns:
            中断结果字典
        """
        import sys
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        print(f"[InterruptBatch] 开始并发中断 {len(session_ids)} 个终端的命令", file=sys.stderr)
        sys.stderr.flush()
        
        results = {
            "success_count": 0,
            "failed_count": 0,
            "no_command_count": 0,
            "results": {}
        }
        
        def interrupt_single(session_id):
            """中断单个会话的命令"""
            try:
                result = self.interrupt_command(session_id)
                return session_id, result
            except Exception as e:
                return session_id, {
                    "success": False,
                    "error": str(e),
                    "session_id": session_id
                }
        
        # 使用线程池并发中断（最多100线程，提升并发性能）
        max_workers = min(100, max(10, len(session_ids)))
        
        print(f"[InterruptBatch] 使用 {max_workers} 个线程并发中断", file=sys.stderr)
        sys.stderr.flush()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(interrupt_single, sid): sid for sid in session_ids}
            
            for future in as_completed(futures):
                try:
                    session_id, result = future.result()
                    if result.get("success"):
                        results["success_count"] += 1
                        results["results"][session_id] = {
                            "success": True,
                            "status": result.get("status", "idle")
                        }
                    elif "No running command" in result.get("error", ""):
                        results["no_command_count"] += 1
                        results["results"][session_id] = {
                            "success": True,
                            "status": "idle",
                            "message": "No running command"
                        }
                    else:
                        results["failed_count"] += 1
                        results["results"][session_id] = {
                            "success": False,
                            "error": result.get("error", "Unknown error")
                        }
                except Exception as e:
                    session_id = futures[future]
                    results["failed_count"] += 1
                    results["results"][session_id] = {
                        "success": False,
                        "error": str(e)
                    }
        
        print(f"[InterruptBatch] 完成: 成功{results['success_count']}, 无命令{results['no_command_count']}, 失败{results['failed_count']}", file=sys.stderr)
        sys.stderr.flush()
        
        return results
    
    def interrupt_command(self, session_id: str) -> dict:
        """
        中断当前命令但保留终端（Ctrl+C效果）
        
        Args:
            session_id: 会话ID
        
        Returns:
            操作结果
        """
        import sys
        
        if session_id not in self.sessions:
            return {
                "success": False,
                "error": "Session not found",
                "session_id": session_id
            }
        
        session = self.sessions[session_id]
        
        with session.lock:
            if session.process and session.process.poll() is None:
                try:
                    print(f"[Interrupt] 中断命令: {session_id}", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # 发送SIGINT（Ctrl+C）信号
                    parent = psutil.Process(session.process.pid)
                    
                    # 先尝试优雅终止子进程
                    for child in parent.children(recursive=True):
                        try:
                            child.terminate()  # SIGTERM
                        except:
                            pass
                    
                    # 终止主进程
                    parent.terminate()
                    
                    # 等待一小段时间
                    import time
                    time.sleep(0.5)
                    
                    # 如果还没结束，强制kill
                    if session.process.poll() is None:
                        for child in parent.children(recursive=True):
                            try:
                                child.kill()
                            except:
                                pass
                        parent.kill()
                    
                    # 更新状态为idle（可以继续使用）
                    session.status = "idle"
                    session.process = None
                    session.current_command = None
                    session.current_output = ""
                    session.last_exit_code = 130  # Ctrl+C的退出码
                    session.last_completed_at = datetime.now()
                    
                    print(f"[Interrupt] 命令已中断，终端变为空闲: {session_id}", file=sys.stderr)
                    sys.stderr.flush()
                    
                    return {
                        "success": True,
                        "session_id": session_id,
                        "message": "命令已中断，终端现在空闲",
                        "status": "idle"
                    }
                except Exception as e:
                    print(f"[Interrupt] 中断失败: {e}", file=sys.stderr)
                    sys.stderr.flush()
                    return {
                        "success": False,
                        "error": str(e),
                        "session_id": session_id
                    }
            else:
                return {
                    "success": False,
                    "error": "No running command",
                    "session_id": session_id,
                    "message": "终端当前没有运行命令"
                }
    
    def _kill_session_sync(self, session_id: str) -> bool:
        """同步终止单个会话（内部方法）- 删除整个终端"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        with session.lock:
            if session.process and session.process.poll() is None:
                try:
                    # 终止进程及其子进程
                    parent = psutil.Process(session.process.pid)
                    for child in parent.children(recursive=True):
                        child.kill()
                    parent.kill()
                except:
                    pass
                
            session.status = "completed"
            session.process = None
        
        # 从管理器中移除
        with self.lock:
            del self.sessions[session_id]
        
        return True
    
    async def kill_session(self, session_id: str) -> bool:
        """
        终止单个会话（兼容旧接口，内部调用并发版本）
        
        推荐使用 kill_sessions([session_id]) 获取更详细的结果
        """
        result = self.kill_sessions([session_id])
        return result["results"].get(session_id, {}).get("success", False)
    
    def kill_sessions(self, session_ids: List[str]) -> dict:
        """
        批量并发删除多个终端会话（v2.1新增）
        
        Args:
            session_ids: 要删除的会话ID列表
        
        Returns:
            删除结果字典
        """
        import sys
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import asyncio
        
        print(f"[KillBatch] 开始并发删除 {len(session_ids)} 个终端", file=sys.stderr)
        sys.stderr.flush()
        
        results = {
            "success_count": 0,
            "failed_count": 0,
            "results": {}
        }
        
        def kill_single(session_id):
            """删除单个会话的包装函数"""
            try:
                # 直接调用同步方法
                success = self._kill_session_sync(session_id)
                return session_id, success, None
            except Exception as e:
                return session_id, False, str(e)
        
        # 使用线程池并发删除（最多100线程，提升并发性能）
        max_workers = min(100, max(10, len(session_ids)))
        
        print(f"[KillBatch] 使用 {max_workers} 个线程并发删除", file=sys.stderr)
        sys.stderr.flush()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(kill_single, sid): sid for sid in session_ids}
            
            for future in as_completed(futures):
                try:
                    session_id, success, error = future.result()
                    if success:
                        results["success_count"] += 1
                        results["results"][session_id] = {"success": True}
                    else:
                        results["failed_count"] += 1
                        results["results"][session_id] = {
                            "success": False,
                            "error": error or "Session not found"
                        }
                except Exception as e:
                    session_id = futures[future]
                    results["failed_count"] += 1
                    results["results"][session_id] = {
                        "success": False,
                        "error": str(e)
                    }
        
        print(f"[KillBatch] 删除完成: 成功 {results['success_count']}/{len(session_ids)}", file=sys.stderr)
        sys.stderr.flush()
        
        return {
            "success": True,
            "total": len(session_ids),
            "success_count": results["success_count"],
            "failed_count": results["failed_count"],
            "results": results["results"]
        }
    
    async def execute_after_completion(
        self, 
        wait_for_session_id: str,
        command: str,
        target_session_id: Optional[str] = None,
        create_new: bool = False,
        new_session_config: Optional[dict] = None,
        timeout: float = 300
    ) -> dict:
        """
        等待指定终端完成后执行命令（链式执行，v2.1新增）
        
        Args:
            wait_for_session_id: 要等待完成的会话ID
            command: 要执行的命令
            target_session_id: 目标会话ID（如果为None且create_new=False，则使用wait_for_session_id）
            create_new: 是否创建新终端执行
            new_session_config: 新终端配置（如果create_new=True）
            timeout: 等待超时时间（秒）
        
        Returns:
            执行结果字典
        """
        import sys
        import time
        
        print(f"[ChainExec] 等待终端 {wait_for_session_id} 完成", file=sys.stderr)
        sys.stderr.flush()
        
        # 等待指定会话完成
        start_time = time.time()
        wait_result = self.wait_for_completion(
            session_ids=[wait_for_session_id],
            timeout=timeout,
            check_interval=0.5
        )
        
        # 检查结果
        if wait_for_session_id in wait_result["completed"]:
            print(f"[ChainExec] 终端 {wait_for_session_id} 已完成（成功）", file=sys.stderr)
            sys.stderr.flush()
        elif wait_for_session_id in wait_result["failed"]:
            print(f"[ChainExec] 终端 {wait_for_session_id} 已完成（失败）", file=sys.stderr)
            sys.stderr.flush()
            return {
                "success": False,
                "error": f"等待的终端 {wait_for_session_id} 执行失败",
                "exit_code": wait_result["results"].get(wait_for_session_id, {}).get("exit_code"),
                "waited_seconds": wait_result["elapsed_time"]
            }
        elif wait_for_session_id in wait_result["timeout"]:
            return {
                "success": False,
                "error": f"等待终端 {wait_for_session_id} 超时",
                "waited_seconds": timeout
            }
        else:
            return {
                "success": False,
                "error": f"终端 {wait_for_session_id} 不存在或状态未知",
                "waited_seconds": wait_result["elapsed_time"]
            }
        
        # 确定目标终端
        if create_new:
            print(f"[ChainExec] 创建新终端执行命令", file=sys.stderr)
            sys.stderr.flush()
            
            # 使用新终端配置或复制等待终端的配置
            if new_session_config:
                config = new_session_config
            else:
                wait_session = self.sessions.get(wait_for_session_id)
                if wait_session:
                    config = {
                        "cwd": wait_session.cwd,
                        "shell_type": wait_session.shell_type
                    }
                else:
                    config = {}
            
            # 创建新终端
            new_session_id = self.create_session(
                cwd=config.get("cwd"),
                shell_type=config.get("shell_type")
            )
            target_session_id = new_session_id
        else:
            # 使用现有终端
            if target_session_id is None:
                target_session_id = wait_for_session_id
            
            print(f"[ChainExec] 在终端 {target_session_id} 中执行命令", file=sys.stderr)
            sys.stderr.flush()
        
        # 执行命令（异步调用）
        exec_result = await self.execute_command(target_session_id, command)
        
        # 确保返回值可JSON序列化
        return {
            "success": True,
            "waited_for": str(wait_for_session_id),
            "executed_in": str(target_session_id),
            "created_new": bool(create_new),
            "command": str(command),
            "exec_result": {
                "status": exec_result.get("status"),
                "session_id": exec_result.get("session_id"),
                "command": exec_result.get("command"),
                "message": exec_result.get("message"),
                "error": exec_result.get("error")
            }
        }
    
    def get_session_status(self, session_id: str) -> Optional[dict]:
        """获取会话状态"""
        if session_id not in self.sessions:
            return None
        
        return self.sessions[session_id].get_info()
    
    def get_all_sessions(self) -> List[dict]:
        """获取所有会话"""
        with self.lock:
            return [s.get_info() for s in self.sessions.values()]
    
    def get_output(self, session_id: str, lines: int = 100, only_last_command: bool = False) -> tuple[bool, List[dict], Optional[dict]]:
        """获取会话输出历史（包括运行中命令的实时输出）
        
        参数:
            session_id: 会话ID
            lines: 获取最近N行（only_last_command=False时生效）
            only_last_command: 是否只获取最后一次命令的输出（性能优化）
        
        返回: (success, output_list, metadata)
            metadata 包含运行状态信息，帮助AI判断是否需要继续等待
        """
        try:
            if session_id not in self.sessions:
                # 确保返回False和空列表（永不卡住）
                print(f"[WARNING] get_output: 会话 {session_id} 不存在", file=sys.stderr)
                return False, [], None
            
            session = self.sessions[session_id]
            
            # 使用超时锁防止死锁
            lock_acquired = session.lock.acquire(timeout=2.0)
            if not lock_acquired:
                print(f"[ERROR] get_output: 获取会话锁超时，可能死锁", file=sys.stderr)
                sys.stderr.flush()
                return False, [], {
                    "error": "获取会话锁超时",
                    "suggestion": "会话可能处于异常状态，建议使用 kill_session 重启"
                }
            
            try:
                metadata = None
                current_output_len = len(session.current_output)
                
                # 追踪重复查询
                if session.current_command:
                    # 检查输出是否有变化
                    if current_output_len == session.last_output_length:
                        session.get_output_call_count += 1
                    else:
                        session.get_output_call_count = 1
                    session.last_output_length = current_output_len
                
                if only_last_command:
                    # 只返回最后一次命令的输出
                    # 优先返回正在运行的命令，其次才是历史记录中最后完成的命令
                    if session.current_command:
                        # 有运行中的命令，返回它
                        output_list = [{
                            "command": session.current_command,
                            "output": session.current_output,
                            "returncode": None,  # 还在运行中，没有退出码
                            "timestamp": datetime.now().isoformat(),
                            "is_running": True  # 标记为运行中
                        }]
                        
                        # 检测长时间运行的命令
                        metadata = self._analyze_running_command(session)
                        
                    elif session.output_history:
                        # 没有运行中的命令，返回历史中最后完成的命令
                        output_list = [session.output_history[-1]]
                    else:
                        # 既没有运行中的命令，也没有历史记录
                        output_list = []
                else:
                    # 返回最近N行历史记录
                    output_list = list(session.output_history[-lines:])
                    
                    # 如果有正在运行的命令，追加到列表末尾
                    if session.current_command:
                        running_item = {
                            "command": session.current_command,
                            "output": session.current_output,
                            "returncode": None,  # 还在运行中，没有退出码
                            "timestamp": datetime.now().isoformat(),
                            "is_running": True  # 标记为运行中
                        }
                        output_list.append(running_item)
                        
                        # 检测长时间运行的命令
                        metadata = self._analyze_running_command(session)
                
                # 🎯 智能查询机制：AI作为调度器，不等待终端
                # 查询次数 1-2: 正常查询
                # 查询次数 3-4: 警告提醒
                # 查询次数 ≥5: 自动终止进程
                running_time = 0
                if session.last_command_time:
                    running_time = (datetime.now() - session.last_command_time).total_seconds()
                
                # 总是返回查询次数（让AI知道查了几次）
                if not metadata:
                    metadata = {}
                metadata["query_count"] = session.get_output_call_count
                metadata["running_seconds"] = round(running_time, 1)
                
                # 🔪 核心逻辑：查询≥5次，自动终止！
                if session.current_command and session.get_output_call_count >= 5:
                    # 立即终止进程
                    try:
                        if session.process and session.process.poll() is None:
                            if sys.platform == 'win32':
                                # Windows: 强制结束整个进程树
                                subprocess.run(['taskkill', '/F', '/T', '/PID', str(session.process.pid)], 
                                             capture_output=True, timeout=3)
                            else:
                                # Unix: 发送SIGKILL
                                os.killpg(os.getpgid(session.process.pid), signal.SIGKILL)
                            
                            session.process = None
                            session.status = "completed"
                            session.last_exit_code = -999  # 特殊退出码：自动终止
                            session.current_command = None
                            
                            # 保存输出到历史
                            if session.current_output:
                                session.output_history.append({
                                    "command": session.last_command,
                                    "output": session.current_output,
                                    "returncode": -999,
                                    "timestamp": datetime.now().isoformat()
                                })
                            session.current_output = ""
                            
                            print(f"[AUTO-KILL] 终端 {session_id} 查询超过5次，已自动终止", file=sys.stderr)
                    except Exception as e:
                        print(f"[AUTO-KILL] 终止失败: {e}", file=sys.stderr)
                    
                    # 返回终止信息
                    metadata["auto_killed"] = True
                    metadata["ai_urgent_notice"] = {
                        "status": f"🔪 已自动终止（累计查询{session.get_output_call_count}次）",
                        "last_output": session.current_output[-500:] if session.current_output else "(无输出)",
                        "analysis": {
                            "command": session.last_command,
                            "shell_type": session.shell_type,
                            "running_time": f"{round(running_time, 1)}秒",
                            "output_length": f"{current_output_len}字符",
                            "exit_code": -999,
                            "reason": "命令执行时间过长，自动终止"
                        },
                        "ai_next_actions": [
                            "✅ 分析最后输出，判断是否部分成功",
                            "✅ 继续执行其他并发任务",
                            "💡 如果失败，分析原因并尝试新方案",
                            "🚀 不要等待，立即分发下一个任务"
                        ]
                    }
                
                # ⚠️ 查询3-4次：警告（不终止）
                elif session.current_command and session.get_output_call_count >= 3:
                    metadata["repeated_query_warning"] = True
                    metadata["ai_notice"] = {
                        "warning": f"⚠️ 已查询{session.get_output_call_count}次（还剩{5-session.get_output_call_count}次将自动终止）",
                        "suggestion": "建议：继续执行其他任务，稍后再查询",
                        "current_progress": session.current_output[-200:] if session.current_output else "(无输出)"
                    }
                
                # 🎯 总是添加AI指令：结束对话！
                if not metadata:
                    metadata = {}
                metadata["ai_instruction"] = {
                    "rule": "🚨 立即结束对话！不要再次调用get_output/check_completion",
                    "action": "向用户展示当前结果，让用户等待，下次对话再查询"
                }
                
                return True, output_list, metadata
            finally:
                # 确保释放锁
                session.lock.release()
            
        except Exception as e:
            # 全局异常捕获：永不卡住
            print(f"[ERROR] get_output异常: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
            # 返回空结果而不是抛出异常
            return False, [], None
    
    def _analyze_running_command(self, session: TerminalSession) -> dict:
        """分析正在运行的命令，判断是否是长时间运行的命令
        
        返回元数据帮助AI决策
        """
        command = session.current_command
        output = session.current_output
        start_time = session.last_command_time
        
        if not start_time:
            return None
        
        # 计算运行时间
        running_seconds = (datetime.now() - start_time).total_seconds()
        
        # 识别长时间运行的命令模式
        long_running_patterns = [
            'npm run', 'yarn dev', 'yarn start', 'npm start', 'npm dev',
            'python manage.py runserver', 'rails server', 'flask run',
            'ng serve', 'next dev', 'vite', 'webpack serve',
            'ping -t', 'tail -f', 'watch', 'nodemon'
        ]
        
        is_long_running = any(pattern in command.lower() for pattern in long_running_patterns)
        
        # 构建元数据
        metadata = {
            "is_running": True,
            "running_seconds": round(running_seconds, 1),
            "command": command,
            "output_length": len(output),
            "is_likely_long_running": is_long_running,
        }
        
        # 根据情况给出建议（按优先级）
        
        # 高优先级：10秒无输出（可能卡住）
        if running_seconds > 10 and len(output) == 0:
            metadata["ai_suggestion"] = {
                "action": "命令已运行10秒但无任何输出，极可能卡住",
                "options": [
                    "使用 kill_session 结束这个会话",
                    "创建新会话重新尝试",
                    "检查命令是否正确",
                    "如果是Windows命令，创建对应的终端类型（cmd/powershell）"
                ],
                "reason": f"命令已运行 {round(running_seconds)}秒但没有任何输出",
                "severity": "high"
            }
        # 中优先级：长时间运行服务
        elif is_long_running and running_seconds > 5:
            metadata["ai_suggestion"] = {
                "action": "已获取到当前输出，这是一个持续运行的服务",
                "options": [
                    "如果输出显示服务已启动，可以继续其他操作",
                    "如果需要停止服务，使用 kill_session 工具",
                    "如果需要在同一目录执行其他命令，创建新的终端会话"
                ],
                "reason": f"命令已运行 {round(running_seconds)}秒，包含服务启动关键词",
                "severity": "medium"
            }
        # 低优先级：超长运行
        elif running_seconds > 30:
            metadata["ai_suggestion"] = {
                "action": "命令运行时间较长",
                "options": [
                    "如果输出看起来正常，可以继续等待",
                    "如果看起来卡住，使用 kill_session",
                    "创建新终端继续其他操作"
                ],
                "reason": f"命令已运行 {round(running_seconds)}秒",
                "severity": "low"
            }
        
        return metadata
    
    def get_all_outputs(self, only_last_command: bool = True) -> dict:
        """一次性并发获取所有终端的输出（超级便捷！）
        
        参数:
            only_last_command: 是否只获取最后一次命令的输出（默认True）
        
        返回: {session_id: output_list} 的字典
        """
        with self.lock:
            session_ids = list(self.sessions.keys())
        
        if not session_ids:
            return {}
        
        return self.get_batch_output(session_ids, only_last_command)
    
    def get_batch_output(self, session_ids: List[str], only_last_command: bool = True) -> dict:
        """批量获取多个会话的输出（真正的多线程并发）
        
        参数:
            session_ids: 会话ID列表
            only_last_command: 是否只获取最后一次命令的输出（默认True，性能优化）
        
        返回: {session_id: output_list} 的字典
        """
        import sys
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        print(f"[BatchOutput] 开始并发读取 {len(session_ids)} 个终端的输出", file=sys.stderr)
        sys.stderr.flush()
        
        results = {}
        
        # 定义单个读取任务
        def read_single_output(session_id):
            success, output, metadata = self.get_output(session_id, only_last_command=only_last_command)
            return session_id, success, output, metadata
        
        # 使用线程池并发读取（最多100线程，提升读取性能）
        max_workers = min(100, max(10, len(session_ids)))
        
        print(f"[BatchOutput] 使用 {max_workers} 个线程并发读取", file=sys.stderr)
        sys.stderr.flush()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = {executor.submit(read_single_output, sid): sid for sid in session_ids}
            
            # 收集结果
            for future in as_completed(futures):
                try:
                    session_id, success, output, metadata = future.result()
                    if success:
                        results[session_id] = output
                    else:
                        results[session_id] = []
                except Exception as e:
                    session_id = futures[future]
                    print(f"[BatchOutput] 读取 {session_id} 失败: {e}", file=sys.stderr)
                    sys.stderr.flush()
                    results[session_id] = []
        
        print(f"[BatchOutput] 并发读取完成，成功: {len([r for r in results.values() if r])}/{len(session_ids)}", file=sys.stderr)
        sys.stderr.flush()
        
        return results
    
    def get_memory_usage(self) -> dict:
        """获取内存使用情况"""
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free
        }
    
    def check_memory_and_suggest_cleanup(self) -> dict:
        """检查内存并提供清理建议"""
        memory = self.get_memory_usage()
        suggestions = []
        
        if memory["percent"] >= self.memory_threshold:
            # 内存超过阈值，提供清理建议
            idle_sessions = []
            running_sessions = []
            
            for sid, session in self.sessions.items():
                if session.status == "idle" or session.status == "completed":
                    idle_sessions.append(sid)
                elif session.status == "running":
                    running_sessions.append(sid)
            
            if idle_sessions:
                suggestions.append({
                    "type": "kill_idle",
                    "message": f"建议清除 {len(idle_sessions)} 个空闲终端",
                    "session_ids": idle_sessions
                })
            
            # 检查重复运行的终端
            cmd_groups = defaultdict(list)
            for sid, session in self.sessions.items():
                if session.last_command:
                    key = f"{session.cwd}:{session.last_command}"
                    cmd_groups[key].append(sid)
            
            duplicate_sessions = []
            for key, sids in cmd_groups.items():
                if len(sids) > 1:
                    # 保留最新的，清除其他的
                    duplicate_sessions.extend(sids[:-1])
            
            if duplicate_sessions:
                suggestions.append({
                    "type": "kill_duplicate",
                    "message": f"建议清除 {len(duplicate_sessions)} 个重复终端",
                    "session_ids": duplicate_sessions
                })
        
        return {
            "memory": memory,
            "suggestions": suggestions,
            "should_cleanup": memory["percent"] >= self.memory_threshold
        }
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        with self.lock:
            running = sum(1 for s in self.sessions.values() if s.status == "running")
            idle = sum(1 for s in self.sessions.values() if s.status == "idle")
            completed = sum(1 for s in self.sessions.values() if s.status == "completed")
            
        memory = self.get_memory_usage()
        
        return {
            "total_sessions": len(self.sessions),
            "running": running,
            "idle": idle,
            "completed": completed,
            "memory_percent": memory["percent"],
            "memory_used_gb": round(memory["used"] / (1024**3), 2),
            "memory_total_gb": round(memory["total"] / (1024**3), 2)
        }
    
    def _start_smart_cleanup_thread(self):
        """启动智能清理线程（超过64个终端+内存不足时自动清理最老的已完成/空闲终端）"""
        import sys
        
        def smart_cleanup_worker():
            print("[SmartCleanup] 智能清理线程已启动", file=sys.stderr)
            print("[SmartCleanup] 策略: 超过64个终端时检查内存，内存不足清理最老的已完成/空闲终端", file=sys.stderr)
            sys.stderr.flush()
            
            while True:
                try:
                    time.sleep(5)  # 每5秒检查一次
                    
                    with self.lock:
                        session_count = len(self.sessions)
                    
                    # 只在超过64个终端时才检查
                    if session_count <= self.session_threshold:
                        continue
                    
                    # 检查内存使用
                    memory = self.get_memory_usage()
                    memory_percent = memory["percent"]
                    
                    print(f"[SmartCleanup] 终端数: {session_count}, 内存使用: {memory_percent:.1f}%", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # 内存充足，不清理
                    if memory_percent < self.memory_threshold:
                        print(f"[SmartCleanup] 内存充足({memory_percent:.1f}% < {self.memory_threshold}%)，不清理", file=sys.stderr)
                        sys.stderr.flush()
                        continue
                    
                    # 内存不足，需要清理
                    print(f"[SmartCleanup] ⚠️ 内存不足({memory_percent:.1f}% >= {self.memory_threshold}%)，开始清理", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # 获取所有已完成/空闲的终端，按创建时间排序（最老的在前）
                    sessions_to_cleanup = []
                    
                    with self.lock:
                        for session_id, session in self.sessions.items():
                            # 只清理已完成或空闲且无运行命令的终端
                            if (session.status in ['completed', 'idle'] and 
                                session.current_command is None):
                                sessions_to_cleanup.append({
                                    'session_id': session_id,
                                    'created_at': session.created_at,
                                    'status': session.status,
                                    'age_seconds': (datetime.now() - session.created_at).total_seconds()
                                })
                    
                    if not sessions_to_cleanup:
                        print("[SmartCleanup] 没有可清理的终端（所有终端都在运行中）", file=sys.stderr)
                        sys.stderr.flush()
                        continue
                    
                    # 按创建时间排序，最老的在前
                    sessions_to_cleanup.sort(key=lambda x: x['created_at'])
                    
                    # 计算需要清理多少个（清理到内存降到阈值以下）
                    # 保守策略：每次清理10%的终端
                    cleanup_count = max(1, int(session_count * 0.1))
                    cleanup_count = min(cleanup_count, len(sessions_to_cleanup))
                    
                    print(f"[SmartCleanup] 找到 {len(sessions_to_cleanup)} 个可清理终端，计划清理 {cleanup_count} 个", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # 清理最老的终端
                    for i in range(cleanup_count):
                        session_info = sessions_to_cleanup[i]
                        session_id = session_info['session_id']
                        age = session_info['age_seconds']
                        
                        print(f"[SmartCleanup] 清理终端: {session_id} (存在{age:.0f}秒, 状态:{session_info['status']})", file=sys.stderr)
                        sys.stderr.flush()
                        
                        try:
                            self.kill_session(session_id)
                        except Exception as e:
                            print(f"[SmartCleanup] 清理失败: {e}", file=sys.stderr)
                            sys.stderr.flush()
                    
                    # 清理后重新检查内存
                    memory_after = self.get_memory_usage()
                    print(f"[SmartCleanup] 清理完成，内存: {memory_after['percent']:.1f}%", file=sys.stderr)
                    sys.stderr.flush()
                
                except Exception as e:
                    print(f"[SmartCleanup] 异常: {e}", file=sys.stderr)
                    import traceback
                    traceback.print_exc(file=sys.stderr)
                    sys.stderr.flush()
        
        cleanup_thread = threading.Thread(target=smart_cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    # ==================== 🆕 v2.0 新增功能 ====================
    
    def detect_environment(self, session_id: str, force_refresh: bool = False) -> dict:
        """
        检测终端的环境信息（Node版本、Python版本、Git分支等）
        
        带全局超时保护，防止卡住
        
        Args:
            session_id: 会话ID
            force_refresh: 是否强制刷新（忽略缓存）
        
        Returns:
            环境信息字典
        """
        import sys
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
        
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # 检查缓存（5分钟内有效）
        if not force_refresh and session.environment_checked_at:
            age = (datetime.now() - session.environment_checked_at).total_seconds()
            if age < 300:  # 5分钟缓存
                return session.environment
        
        def _detect_with_timeout():
            """实际的检测逻辑，在独立线程中运行（极速模式：0.3秒超时）"""
            env_info = {}
            
            # 检测Node.js版本（极速：0.3秒超时）
            try:
                result = subprocess.run(
                    ["node", "--version"],
                    cwd=session.cwd,
                    capture_output=True,
                    timeout=0.3,  # 减少到0.3秒
                    text=True,
                    shell=False
                )
                if result.returncode == 0:
                    env_info["node_version"] = result.stdout.strip()
                else:
                    env_info["node_version"] = None
            except subprocess.TimeoutExpired:
                env_info["node_version"] = None  # 静默失败
            except Exception:
                env_info["node_version"] = None  # 静默失败
            
            # 检测Python版本（极速：0.3秒超时）
            try:
                result = subprocess.run(
                    ["python", "--version"],
                    cwd=session.cwd,
                    capture_output=True,
                    timeout=0.3,  # 减少到0.3秒
                    text=True,
                    shell=False
                )
                if result.returncode == 0:
                    version = result.stdout.strip() or result.stderr.strip()
                    env_info["python_version"] = version
                else:
                    env_info["python_version"] = None
            except subprocess.TimeoutExpired:
                env_info["python_version"] = None  # 静默失败
            except Exception:
                env_info["python_version"] = None  # 静默失败
            
            # 检测Git分支（极速：0.3秒超时）
            try:
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=session.cwd,
                    capture_output=True,
                    timeout=0.3,  # 减少到0.3秒
                    text=True,
                    shell=False
                )
                if result.returncode == 0:
                    env_info["git_branch"] = result.stdout.strip()
                else:
                    env_info["git_branch"] = None
            except subprocess.TimeoutExpired:
                env_info["git_branch"] = None  # 静默失败
            except Exception:
                env_info["git_branch"] = None  # 静默失败
            
            # 检测npm版本（极速：0.3秒超时）
            try:
                result = subprocess.run(
                    ["npm", "--version"],
                    cwd=session.cwd,
                    capture_output=True,
                    timeout=0.3,  # 减少到0.3秒
                    text=True,
                    shell=False
                )
                if result.returncode == 0:
                    env_info["npm_version"] = result.stdout.strip()
                else:
                    env_info["npm_version"] = None
            except subprocess.TimeoutExpired:
                env_info["npm_version"] = None  # 静默失败
            except Exception:
                env_info["npm_version"] = None  # 静默失败
            
            return env_info
        
        # 使用线程池+全局超时执行检测（极速模式：1秒）
        executor = None
        try:
            print(f"[EnvDetect] 极速环境检测开始（全局1秒超时）: {session_id}", file=sys.stderr)
            sys.stderr.flush()
            
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(_detect_with_timeout)
            try:
                # 全局超时：1秒（极速模式）
                env_info = future.result(timeout=1.0)
                print(f"[EnvDetect] ✅ 检测完成: {session_id}", file=sys.stderr)
                sys.stderr.flush()
            except FutureTimeoutError:
                print(f"[EnvDetect] ⏱️ 全局超时(1秒)，返回空结果: {session_id}", file=sys.stderr)
                sys.stderr.flush()
                # 取消future，不等待线程
                future.cancel()
                # 全局超时，返回所有null
                env_info = {
                    "node_version": None,
                    "python_version": None,
                    "git_branch": None,
                    "npm_version": None,
                    "timeout": True
                }
        except Exception as e:
            print(f"[ERROR] 环境检测异常 for {session_id}: {e}", file=sys.stderr)
            sys.stderr.flush()
            env_info = {
                "node_version": None,
                "python_version": None,
                "git_branch": None,
                "npm_version": None,
                "error": str(e)
            }
        finally:
            # 立即关闭线程池，不等待（使用wait=False）
            if executor:
                try:
                    # Python 3.9+ 支持 cancel_futures
                    import sys as _sys
                    if _sys.version_info >= (3, 9):
                        executor.shutdown(wait=False, cancel_futures=True)
                    else:
                        executor.shutdown(wait=False)
                    print(f"[DEBUG] 线程池已关闭(不等待): {session_id}", file=sys.stderr)
                    sys.stderr.flush()
                except Exception as ex:
                    print(f"[WARNING] 线程池关闭异常: {ex}", file=sys.stderr)
                    sys.stderr.flush()
        
        # 更新缓存
        session.environment = env_info
        session.environment_checked_at = datetime.now()
        
        return env_info
    
    def send_input(self, session_id: str, input_text: str, echo: bool = True) -> dict:
        """
        向终端发送输入（用于响应交互式命令）
        
        Args:
            session_id: 会话ID
            input_text: 要发送的输入文本
            echo: 是否回显输入
        
        Returns:
            操作结果
        """
        session = self.sessions.get(session_id)
        if not session:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        if not session.process or session.process.poll() is not None:
            return {
                "success": False,
                "error": "No active process"
            }
        
        try:
            # 发送输入到进程的stdin
            if session.process.stdin:
                session.process.stdin.write(input_text.encode())
                session.process.stdin.flush()
                
                # 更新状态
                session.waiting_input = False
                session.interaction_detected_at = None
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "input_sent": input_text if echo else "***",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Process stdin not available"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def detect_interactions(self, session_ids: Optional[List[str]] = None) -> dict:
        """
        检测所有等待输入的终端（非阻塞，立即返回）
        
        Args:
            session_ids: 要检查的会话ID列表，None表示检查所有
        
        Returns:
            交互检测结果
        """
        import sys
        print(f"[DetectInteractions] 开始检测交互状态", file=sys.stderr)
        sys.stderr.flush()
        
        if session_ids is None:
            session_ids = list(self.sessions.keys())
        
        print(f"[DetectInteractions] 检测 {len(session_ids)} 个会话", file=sys.stderr)
        sys.stderr.flush()
        
        interactions = []
        
        for session_id in session_ids:
            session = self.sessions.get(session_id)
            if not session:
                print(f"[DetectInteractions] 会话 {session_id} 不存在", file=sys.stderr)
                sys.stderr.flush()
                continue
            
            print(f"[DetectInteractions] 检查会话 {session_id}, 进程存在:{session.process is not None}, 有命令:{session.current_command is not None}", file=sys.stderr)
            sys.stderr.flush()
            
            # 检查是否可能在等待输入
            if session.process and session.process.poll() is None:
                # 进程仍在运行，检查最近的输出
                if session.current_output:
                    lines = session.current_output.strip().split('\n')
                    if lines:
                        last_line = lines[-1].strip()
                        
                        # 检测常见的输入提示模式
                        prompt_patterns = [
                            # 项目初始化
                            ("package name:", "text_input", "project_name"),
                            ("project name:", "text_input", "project_name"),
                            ("version:", "text_input", "version"),
                            ("description:", "text_input", "description"),
                            ("author:", "text_input", "author"),
                            
                            # 确认提示
                            ("(y/n)", "yes_no", None),
                            ("(Y/N)", "yes_no", None),
                            ("yes/no", "yes_no", None),
                            
                            # 选择提示
                            ("select", "choice", None),
                            ("choose", "choice", None),
                            
                            # 密码输入
                            ("password:", "password", None),
                            ("passphrase:", "password", None),
                        ]
                        
                        detected_pattern = None
                        prompt_type = "text_input"
                        pattern_name = None
                        
                        for pattern, ptype, pname in prompt_patterns:
                            if pattern.lower() in last_line.lower():
                                detected_pattern = pattern
                                prompt_type = ptype
                                pattern_name = pname
                                break
                        
                        # 如果检测到提示，或者输出长时间没有变化但进程还在运行
                        if detected_pattern or (
                            session.current_command_start_time and
                            (datetime.now() - session.current_command_start_time).total_seconds() > 3 and
                            session.last_output_length == len(session.current_output)
                        ):
                            # 检测到可能在等待输入
                            if not session.waiting_input:
                                session.waiting_input = True
                                session.interaction_detected_at = datetime.now()
                                session.last_prompt_line = last_line
                            
                            waiting_seconds = (datetime.now() - session.interaction_detected_at).total_seconds()
                            
                            interaction = {
                                "session_id": session_id,
                                "command": session.current_command,
                                "prompt": last_line,
                                "waiting_seconds": round(waiting_seconds, 1),
                                "last_output_line": last_line,
                                "detected_pattern": detected_pattern or "unknown",
                                "suggestions": {
                                    "type": prompt_type,
                                    "pattern_name": pattern_name
                                }
                            }
                            
                            # 提取默认值
                            if "(" in last_line and ")" in last_line:
                                start = last_line.find("(")
                                end = last_line.find(")")
                                default = last_line[start+1:end].strip()
                                interaction["suggestions"]["default_value"] = default
                            
                            interactions.append(interaction)
        
        result = {
            "success": True,
            "interactions": interactions,
            "count": len(interactions)
        }
        
        print(f"[DetectInteractions] 完成，检测到 {len(interactions)} 个交互", file=sys.stderr)
        sys.stderr.flush()
        
        return result
    
    def get_terminal_states(self, session_ids: Optional[List[str]] = None, include_environment: bool = True) -> dict:
        """
        获取所有终端的详细状态（AI调度的核心工具）
        
        Args:
            session_ids: 要查询的会话ID列表，None表示所有
            include_environment: 是否包含环境信息（会增加一些延迟）
        
        Returns:
            终端状态字典
        """
        import sys
        print(f"[DEBUG] get_terminal_states开始执行", file=sys.stderr)
        sys.stderr.flush()
        
        try:
            if session_ids is None:
                print(f"[DEBUG] 获取所有会话列表", file=sys.stderr)
                sys.stderr.flush()
                session_ids = list(self.sessions.keys())
                print(f"[DEBUG] 找到 {len(session_ids)} 个会话", file=sys.stderr)
                sys.stderr.flush()
            
            terminals = {}
            summary = {
                "total": 0,
                "idle": 0,
                "running": 0,
                "waiting_input": 0,
                "completed": 0
            }
            
            for idx, session_id in enumerate(session_ids):
                print(f"[DEBUG] 处理会话 {idx+1}/{len(session_ids)}: {session_id}", file=sys.stderr)
                sys.stderr.flush()
                
                try:
                    session = self.sessions.get(session_id)
                    if not session:
                        print(f"[DEBUG] 会话 {session_id} 不存在，跳过", file=sys.stderr)
                        sys.stderr.flush()
                        continue
                    
                    print(f"[DEBUG] 检查会话状态: {session_id}", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # 确定状态
                    state = session.status
                    if session.waiting_input:
                        state = "waiting_input"
                    elif session.process:
                        try:
                            print(f"[DEBUG] 检查进程状态: {session_id}", file=sys.stderr)
                            sys.stderr.flush()
                            poll_result = session.process.poll()
                            if poll_result is None:
                                state = "running"
                            print(f"[DEBUG] 进程poll结果: {poll_result}", file=sys.stderr)
                            sys.stderr.flush()
                        except Exception as e:
                            print(f"[WARNING] poll失败 for {session_id}: {e}", file=sys.stderr)
                            sys.stderr.flush()
                    elif session.last_exit_code is not None:
                        state = "completed"
                    elif not session.last_command:
                        state = "idle"
                    
                    print(f"[DEBUG] 会话状态确定: {session_id} -> {state}", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # 计算运行时间
                    running_seconds = 0
                    if session.current_command_start_time:
                        running_seconds = (datetime.now() - session.current_command_start_time).total_seconds()
                    
                    # 判断是否可以复用
                    can_reuse = (
                        state in ["idle", "completed"] and
                        session.current_command is None and
                        (not session.process or session.process.poll() is not None)
                    )
                    
                    terminal_state = {
                        "state": state,
                        "shell_type": session.shell_type,
                        "cwd": session.cwd,
                        "last_command": session.last_command,
                        "last_exit_code": session.last_exit_code,
                        "last_completed_at": session.last_completed_at.isoformat() if session.last_completed_at else None,
                        "current_command": session.current_command,
                        "running_seconds": round(running_seconds, 1),
                        "can_reuse": can_reuse,
                        "interaction_waiting": session.waiting_input,
                    }
                    
                    # 可选：包含环境信息
                    if include_environment:
                        print(f"[DEBUG] 开始检测环境: {session_id}", file=sys.stderr)
                        sys.stderr.flush()
                        try:
                            terminal_state["environment"] = self.detect_environment(session_id, force_refresh=False)
                            print(f"[DEBUG] 环境检测完成: {session_id}", file=sys.stderr)
                            sys.stderr.flush()
                        except Exception as e:
                            print(f"[WARNING] detect_environment失败 for {session_id}: {e}", file=sys.stderr)
                            sys.stderr.flush()
                            terminal_state["environment"] = {"error": str(e)}
                    else:
                        print(f"[DEBUG] 跳过环境检测: {session_id}", file=sys.stderr)
                        sys.stderr.flush()
                    
                    terminals[session_id] = terminal_state
                    
                    # 更新统计
                    summary["total"] += 1
                    if state == "idle":
                        summary["idle"] += 1
                    elif state == "running":
                        summary["running"] += 1
                    elif state == "waiting_input":
                        summary["waiting_input"] += 1
                    elif state == "completed":
                        summary["completed"] += 1
                    
                    print(f"[DEBUG] 会话处理完成: {session_id}", file=sys.stderr)
                    sys.stderr.flush()
                    
                except Exception as e:
                    print(f"[ERROR] 处理会话 {session_id} 时发生异常: {e}", file=sys.stderr)
                    import traceback
                    traceback.print_exc(file=sys.stderr)
                    sys.stderr.flush()
                    # 继续处理下一个会话
                    continue
            
            print(f"[DEBUG] get_terminal_states完成，返回 {len(terminals)} 个终端状态", file=sys.stderr)
            sys.stderr.flush()
            
            return {
                "success": True,
                "terminals": terminals,
                "summary": summary
            }
        
        except Exception as e:
            print(f"[ERROR] get_terminal_states发生严重异常: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
            # 返回空结果而不是崩溃
            return {
                "success": False,
                "error": str(e),
                "terminals": {},
                "summary": {
                    "total": 0,
                    "idle": 0,
                    "running": 0,
                    "waiting_input": 0,
                    "completed": 0
                }
            }
    
    def wait_for_completion(
        self, 
        session_ids: List[str], 
        timeout: float = 300, 
        check_interval: float = 1.0
    ) -> dict:
        """
        等待一组终端完成（用于依赖管理）
        
        Args:
            session_ids: 要等待的会话ID列表
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
        
        Returns:
            等待结果
        """
        import sys
        print(f"[WaitCompletion] 开始等待 {len(session_ids)} 个终端完成，超时{timeout}秒", file=sys.stderr)
        sys.stderr.flush()
        
        # 预检查：检测没有命令的会话
        no_command_sessions = []
        for session_id in session_ids:
            session = self.sessions.get(session_id)
            if session and session.current_command is None and session.last_command is None:
                no_command_sessions.append(session_id)
        
        if no_command_sessions:
            error_msg = f"⚠️ 以下会话没有执行任何命令，无法等待完成：{', '.join(no_command_sessions)}"
            print(f"[WaitCompletion] {error_msg}", file=sys.stderr)
            sys.stderr.flush()
            return {
                "success": False,
                "error": error_msg,
                "no_command_sessions": no_command_sessions,
                "suggestion": "请先使用 execute_command 执行命令，或使用 create_session(initial_command='...') 创建时直接执行命令",
                "completed": [],
                "failed": [],
                "timeout": [],
                "still_running": [],
                "results": {},
                "elapsed_time": 0
            }
        
        start_time = time.time()
        completed = []
        failed = []
        timeout_sessions = []
        
        while True:
            # 检查超时
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                # 记录超时的会话
                for sid in session_ids:
                    if sid not in completed and sid not in failed:
                        timeout_sessions.append(sid)
                print(f"[WaitCompletion] 超时！{len(timeout_sessions)}个会话超时", file=sys.stderr)
                sys.stderr.flush()
                break
            
            # 检查每个会话
            all_done = True
            for session_id in session_ids:
                if session_id in completed or session_id in failed:
                    continue
                
                session = self.sessions.get(session_id)
                if not session:
                    print(f"[WaitCompletion] 会话 {session_id} 不存在", file=sys.stderr)
                    sys.stderr.flush()
                    failed.append(session_id)
                    continue
                
                # 检查进程状态
                if session.process:
                    returncode = session.process.poll()
                    if returncode is not None:
                        # 进程已结束
                        if returncode == 0:
                            print(f"[WaitCompletion] 会话 {session_id} 成功完成", file=sys.stderr)
                            sys.stderr.flush()
                            completed.append(session_id)
                        else:
                            print(f"[WaitCompletion] 会话 {session_id} 失败 (exit={returncode})", file=sys.stderr)
                            sys.stderr.flush()
                            failed.append(session_id)
                    else:
                        # 进程仍在运行
                        print(f"[WaitCompletion] 会话 {session_id} 仍在运行... ({elapsed:.1f}s)", file=sys.stderr)
                        sys.stderr.flush()
                        all_done = False
                else:
                    # 没有活动进程
                    print(f"[WaitCompletion] 会话 {session_id} 没有进程，检查状态", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # 如果有退出码，说明已经执行过命令
                    if session.last_exit_code is not None:
                        if session.last_exit_code == 0:
                            completed.append(session_id)
                        else:
                            failed.append(session_id)
                    # 如果从未执行过命令（这个不应该发生，因为预检查已经过滤了）
                    elif session.current_command is None and session.last_command is None:
                        print(f"[WaitCompletion] ⚠️ 会话 {session_id} 从未执行命令（预检查遗漏），标记为失败", file=sys.stderr)
                        sys.stderr.flush()
                        failed.append(session_id)
                    else:
                        # 有命令但无进程，可能已完成
                        completed.append(session_id)
            
            if all_done:
                break
            
            # 等待下一次检查
            time.sleep(check_interval)
        
        # 收集结果详情
        results = {}
        for session_id in completed + failed:
            session = self.sessions.get(session_id)
            if session:
                duration = 0
                if session.current_command_start_time and session.last_completed_at:
                    duration = (session.last_completed_at - session.current_command_start_time).total_seconds()
                
                results[session_id] = {
                    "exit_code": session.last_exit_code,
                    "duration": round(duration, 1)
                }
        
        # 仍在运行的会话
        still_running = [sid for sid in session_ids if sid not in completed and sid not in failed and sid not in timeout_sessions]
        
        result = {
            "success": True,
            "completed": completed,
            "failed": failed,
            "timeout": timeout_sessions,
            "still_running": still_running,
            "results": results,
            "elapsed_time": round(time.time() - start_time, 1)
        }
        
        print(f"[WaitCompletion] 完成: 成功{len(completed)}, 失败{len(failed)}, 超时{len(timeout_sessions)}, 仍运行{len(still_running)}", file=sys.stderr)
        sys.stderr.flush()
        
        return result
    
    def send_keys(self, session_id: str, keys: str, is_text: bool = False) -> dict:
        """
        发送按键或文本到终端（v1.0.2新增）
        
        Args:
            session_id: 会话ID
            keys: 按键名称或文本内容
                  - 按键名称: "UP", "CTRL_C", "F1", "Ctrl+C" 等
                  - 文本内容: 任意字符串（当is_text=True时）
            is_text: 是否作为普通文本发送（True）还是解析为按键（False）
        
        Returns:
            操作结果
        """
        from .key_mapper import KeyMapper
        
        if session_id not in self.sessions:
            return {
                "success": False,
                "error": "Session not found",
                "session_id": session_id
            }
        
        session = self.sessions[session_id]
        
        with session.lock:
            if not session.process or session.process.poll() is not None:
                return {
                    "success": False,
                    "error": "No running process",
                    "session_id": session_id,
                    "message": "终端当前没有运行进程"
                }
            
            try:
                # 转换按键为控制序列
                if is_text:
                    # 作为普通文本发送
                    input_data = KeyMapper.map_text(keys)
                else:
                    # 解析为按键
                    input_data = KeyMapper.map_key(keys)
                
                # 发送到进程的stdin
                if session.process.stdin:
                    session.process.stdin.write(input_data.encode('utf-8'))
                    session.process.stdin.flush()
                    
                    return {
                        "success": True,
                        "session_id": session_id,
                        "sent": keys,
                        "is_text": is_text,
                        "message": f"已发送: {keys}"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Process stdin not available",
                        "session_id": session_id
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "session_id": session_id
                }
    
    def send_text(self, session_id: str, text: str) -> dict:
        """
        快速发送文本到终端（v1.0.2新增）
        这是send_keys的便捷方法，专门用于发送文本
        
        Args:
            session_id: 会话ID
            text: 要发送的文本
        
        Returns:
            操作结果
        """
        return self.send_keys(session_id, text, is_text=True)
    
    def get_live_output(self, session_id: str, since: Optional[str] = None, max_lines: int = 100) -> dict:
        """
        获取实时输出流（v1.0.2新增）
        
        Args:
            session_id: 会话ID
            since: 从某个时间点开始获取（ISO格式），None表示获取最新的
            max_lines: 最大返回行数
        
        Returns:
            实时输出内容
        """
        if session_id not in self.sessions:
            return {
                "success": False,
                "error": "Session not found",
                "session_id": session_id
            }
        
        session = self.sessions[session_id]
        
        with session.lock:
            # 追踪查询次数（防止AI循环调用）
            if session.current_command:
                current_output_len = len(session.current_output)
                if current_output_len == session.last_output_length:
                    session.get_output_call_count += 1
                else:
                    session.get_output_call_count = 1
                session.last_output_length = current_output_len
            
            output_lines = []
            
            # 如果有当前运行的命令，返回其实时输出
            if session.current_output:
                lines = session.current_output.split('\n')
                output_lines = lines[-max_lines:] if len(lines) > max_lines else lines
            
            # 如果没有当前输出，返回最后一次命令的输出
            elif session.output_history:
                last_output = session.output_history[-1]
                lines = last_output.get('output', '').split('\n')
                output_lines = lines[-max_lines:] if len(lines) > max_lines else lines
            
            # 计算运行时间
            running_time = 0
            if session.current_command_start_time:
                running_time = (datetime.now() - session.current_command_start_time).total_seconds()
            
            result = {
                "success": True,
                "session_id": session_id,
                "output_lines": output_lines,
                "total_lines": len(output_lines),
                "is_running": session.status == "running",
                "current_command": session.current_command,
                "timestamp": datetime.now().isoformat(),
                "query_count": session.get_output_call_count,
                "running_seconds": round(running_time, 1)
            }
            
            # 🚨 查询保护：≥3次就警告，≥5次就自动终止
            if session.current_command and session.get_output_call_count >= 3:
                result["warning"] = f"⚠️ 已查询{session.get_output_call_count}次！不要继续查询！"
                result["ai_must_stop"] = True
                result["reason"] = "单次对话中重复查询会导致循环"
                
            if session.current_command and session.get_output_call_count >= 5:
                # 自动终止进程
                if session.process and session.process.poll() is None:
                    try:
                        if sys.platform == 'win32':
                            subprocess.run(['taskkill', '/F', '/T', '/PID', str(session.process.pid)], 
                                         capture_output=True, timeout=3)
                        else:
                            os.killpg(os.getpgid(session.process.pid), signal.SIGKILL)
                    except:
                        pass
                
                result["success"] = False
                result["error"] = f"❌ 自动终止：查询{session.get_output_call_count}次后仍在运行"
                result["action_taken"] = "进程已被自动终止"
                result["ai_instruction"] = "立即结束对话！不要再次调用任何查询工具！"
            
            return result
    
    def wait_for_text(self, session_id: str, text: str, timeout: float = 30) -> dict:
        """
        等待特定文本出现在输出中（v1.0.2新增）
        
        Args:
            session_id: 会话ID
            text: 要等待的文本（支持子串匹配）
            timeout: 超时时间（秒）
        
        Returns:
            等待结果
        """
        if session_id not in self.sessions:
            return {
                "success": False,
                "error": "Session not found",
                "session_id": session_id
            }
        
        session = self.sessions[session_id]
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with session.lock:
                # 检查当前输出
                if text in session.current_output:
                    return {
                        "success": True,
                        "session_id": session_id,
                        "found": True,
                        "text": text,
                        "elapsed_time": round(time.time() - start_time, 2),
                        "message": f"找到文本: {text}"
                    }
            
            # 等待一小段时间
            time.sleep(0.1)
        
        # 超时
        return {
            "success": False,
            "session_id": session_id,
            "found": False,
            "text": text,
            "elapsed_time": round(time.time() - start_time, 2),
            "error": "Timeout",
            "message": f"等待超时，未找到文本: {text}"
        }
    
    def batch_send_keys(self, interactions: List[dict]) -> dict:
        """
        批量发送按键到多个终端（v1.0.2新增）
        
        Args:
            interactions: 交互列表，每项包含:
                - session_id: 会话ID
                - keys: 按键或文本
                - is_text: 是否为文本（可选，默认False）
        
        Returns:
            批量操作结果
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = {
            "success_count": 0,
            "failed_count": 0,
            "results": {}
        }
        
        def send_single(interaction):
            session_id = interaction.get("session_id")
            keys = interaction.get("keys")
            is_text = interaction.get("is_text", False)
            
            try:
                result = self.send_keys(session_id, keys, is_text)
                return session_id, result
            except Exception as e:
                return session_id, {
                    "success": False,
                    "error": str(e),
                    "session_id": session_id
                }
        
        # 并发发送（最多100线程，提升发送性能）
        max_workers = min(100, max(10, len(interactions)))
        
        print(f"[BatchSendKeys] 使用 {max_workers} 个线程并发发送", file=sys.stderr)
        sys.stderr.flush()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(send_single, interaction): interaction for interaction in interactions}
            
            for future in as_completed(futures):
                try:
                    session_id, result = future.result()
                    if result.get("success"):
                        results["success_count"] += 1
                    else:
                        results["failed_count"] += 1
                    results["results"][session_id] = result
                except Exception as e:
                    results["failed_count"] += 1
        
        results["total"] = len(interactions)
        results["message"] = f"批量发送完成: 成功{results['success_count']}/{results['total']}"
        
        return results

