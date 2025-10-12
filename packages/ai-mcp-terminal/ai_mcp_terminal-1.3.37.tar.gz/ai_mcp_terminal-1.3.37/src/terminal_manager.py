"""
终端管理器 - 管理多个终端会话
"""
import asyncio
import os
import platform
import psutil
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
        
        self.status = "idle"  # idle, running, completed
        self.created_at = datetime.now()
        self.last_command = None
        self.last_command_time = None
        self.output_history = []
        self.current_output = ""  # 当前运行命令的实时输出缓存
        self.current_command = None  # 当前运行的命令
        self.process = None
        self.output_queue = queue.Queue()
        self.lock = threading.Lock()
        
        # 追踪get_output调用（用于检测AI重复查询）
        self.get_output_call_count = 0  # 对当前命令的查询次数
        self.last_output_length = 0  # 上次输出的长度
        
    def get_info(self) -> dict:
        """获取会话信息"""
        return {
            "session_id": self.session_id,
            "shell_type": self.shell_type,
            "cwd": self.cwd,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_command": self.last_command,
            "last_command_time": self.last_command_time.isoformat() if self.last_command_time else None,
            "is_alive": self.process is not None and self.process.poll() is None
        }


class TerminalManager:
    """终端管理器"""
    
    def _smart_decode(self, data: bytes, primary_encoding: str) -> str:
        """
        智能解码：尝试多种编码方式，避免出现乱码
        
        Args:
            data: 要解码的字节数据
            primary_encoding: 首选编码（如gbk, utf-8）
        
        Returns:
            解码后的字符串
        """
        if not data:
            return ''
        
        # 编码尝试列表（按优先级）
        encodings_to_try = [
            primary_encoding,
            'gbk',
            'utf-8',
            'cp936',  # Windows简体中文
            'gb18030',  # GBK的超集
            'latin-1'  # 最后的备选，能解码任何字节
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
        return data.decode(primary_encoding, errors='ignore')
    
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
        """智能获取首选Shell类型"""
        system = platform.system().lower()
        
        if system == "windows":
            # Windows shell优先级
            shells_priority = [
                # 现代shell
                ("pwsh", ["pwsh"]),  # PowerShell Core
                ("bash", [  # Git Bash 或 WSL bash
                    r"C:\Program Files\Git\bin\bash.exe",
                    r"C:\Program Files (x86)\Git\bin\bash.exe",
                    os.path.expandvars(r"%PROGRAMFILES%\Git\bin\bash.exe"),
                    "bash"
                ]),
                ("zsh", ["zsh"]),  # Zsh (如果安装)
                ("fish", ["fish"]),  # Fish shell
                ("powershell", ["powershell"]),  # Windows PowerShell
                ("cmd", ["cmd"])  # CMD (最后选择)
            ]
            
        elif system == "darwin":
            # macOS shell优先级
            shells_priority = [
                ("zsh", ["zsh"]),
                ("bash", ["bash"]),
                ("fish", ["fish"]),
                ("sh", ["sh"])
            ]
            
        else:
            # Linux/Unix shell优先级
            shells_priority = [
                ("bash", ["bash"]),
                ("zsh", ["zsh"]),
                ("fish", ["fish"]),
                ("dash", ["dash"]),
                ("sh", ["sh"])
            ]
        
        # 检测第一个可用的shell
        for shell_type, shell_commands in shells_priority:
            for cmd in shell_commands:
                # 如果是路径，检查文件是否存在
                if os.path.sep in cmd or cmd.endswith('.exe'):
                    if os.path.exists(cmd):
                        return shell_type
                # 否则检查命令是否在PATH中
                elif self._command_exists(cmd):
                    return shell_type
        
        # 默认返回
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
                    
                    if 'command not found' in stderr_lower or 'not recognized' in stderr_lower:
                        error_category = "COMMAND_NOT_FOUND"
                        error_description = f"命令不存在：{command.split()[0] if command.split() else command}"
                    elif 'permission denied' in stderr_lower or 'access denied' in stderr_lower:
                        error_category = "PERMISSION_DENIED"
                        error_description = "权限不足，可能需要管理员权限"
                    elif 'no such file or directory' in stderr_lower:
                        error_category = "FILE_NOT_FOUND"
                        error_description = "文件或目录不存在"
                    elif 'syntax error' in stderr_lower or 'unexpected' in stderr_lower:
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
                # 清空当前命令和输出缓存
                session.current_command = None
                session.current_output = ""
            
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
                session.current_command = None
                session.current_output = ""
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
                session.current_command = None
                session.current_output = ""
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
                session.current_command = None
                session.current_output = ""
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
    
    async def kill_session(self, session_id: str) -> bool:
        """终止会话"""
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
                
                # 检测重复查询（AI多次查询但输出无变化）
                # 如果命令运行超过10秒且连续2次查询无输出 → 立即建议
                # 或者连续3次查询无变化 → 建议
                running_time = 0
                if session.last_command_time:
                    running_time = (datetime.now() - session.last_command_time).total_seconds()
                
                quick_stuck_detected = (running_time > 10 and 
                                       session.get_output_call_count >= 2 and 
                                       current_output_len == 0)
                normal_stuck_detected = session.get_output_call_count >= 3
                
                if session.current_command and (quick_stuck_detected or normal_stuck_detected):
                    if not metadata:
                        metadata = {}
                    metadata["repeated_query_detected"] = True
                    metadata["query_count"] = session.get_output_call_count
                    
                    if quick_stuck_detected:
                        action_msg = f"⚠️ 命令运行{round(running_time)}秒仍无输出，极可能卡住"
                    else:
                        action_msg = f"⚠️ 检测到连续{session.get_output_call_count}次查询但输出无变化"
                    
                    metadata["ai_urgent_notice"] = {
                        "action": action_msg,
                        "current_output": session.current_output[:200] if session.current_output else "(无输出)",
                        "suggestions": [
                            "🚫 停止继续查询get_output（浪费调用）",
                            f"✅ 立即执行：kill_session(\"{session_id}\")",
                            "✅ 如果是Windows命令，创建对应终端：create_session(shell_type='cmd')",
                            "✅ 或创建bash新会话：create_session(...)",
                            "⚠️ 不要在bash中运行Windows命令（cmd/systeminfo/findstr等）"
                        ],
                        "reason": f"运行{round(running_time)}秒，查询{session.get_output_call_count}次，输出长度{current_output_len}字符",
                        "command": session.current_command,
                        "shell_type": session.shell_type
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
        
        # 检测不可能成功的命令（错误的终端类型）
        wrong_terminal_detected = False
        wrong_terminal_suggestion = None
        
        # 检测在bash中运行Windows命令
        if session.shell_type in ['bash', 'zsh', 'fish', 'sh']:
            windows_cmd_patterns = [
                ('cmd /c', 'cmd', '这是Windows CMD命令'),
                ('powershell', 'powershell', '这是PowerShell命令'),
                ('systeminfo', 'cmd', 'systeminfo是Windows命令'),
                ('ipconfig', 'cmd', 'ipconfig是Windows命令'),
                ('dir ', 'cmd', 'dir是Windows命令'),
                ('type ', 'cmd', 'type是Windows命令'),
                ('findstr', 'cmd', 'findstr是Windows命令'),
            ]
            
            for pattern, correct_shell, reason in windows_cmd_patterns:
                if pattern in command.lower():
                    wrong_terminal_detected = True
                    wrong_terminal_suggestion = {
                        "current_shell": session.shell_type,
                        "correct_shell": correct_shell,
                        "reason": reason
                    }
                    break
        
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
        
        # 最高优先级：错误的终端类型
        if wrong_terminal_detected:
            metadata["ai_suggestion"] = {
                "action": f"⚠️ 错误的终端类型！{wrong_terminal_suggestion['reason']}",
                "options": [
                    f"立即使用 kill_session 结束当前会话",
                    f"创建正确的终端：create_session(shell_type='{wrong_terminal_suggestion['correct_shell']}')",
                    f"在正确的终端中执行命令"
                ],
                "reason": f"当前是{wrong_terminal_suggestion['current_shell']}终端，但命令需要{wrong_terminal_suggestion['correct_shell']}",
                "severity": "high"
            }
        # 高优先级：10秒无输出（可能卡住）
        elif running_seconds > 10 and len(output) == 0:
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
        
        # 使用线程池并发读取（最多32个线程）
        max_workers = min(32, len(session_ids))
        
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

