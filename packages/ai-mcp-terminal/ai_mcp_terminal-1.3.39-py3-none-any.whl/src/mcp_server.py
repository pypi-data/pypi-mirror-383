"""
MCP服务器 - 实现标准MCP协议
"""
import asyncio
import json
import sys
import threading
import time
import webbrowser
from datetime import datetime
from typing import Any, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# 全局变量，用于跟踪是否需要强制重新加载
FORCE_RELOAD = True

# 尝试相对导入，如果失败则使用绝对导入
try:
    from .terminal_manager import TerminalManager
    from .web_server import WebTerminalServer
except ImportError:
    from terminal_manager import TerminalManager
    from web_server import WebTerminalServer


class MCPTerminalServer:
    """MCP终端服务器"""
    
    def __init__(self):
        self.server = Server("ai-mcp-terminal")
        self.terminal_manager = TerminalManager()
        self.web_server = None
        self.web_server_started = False
        self.uvicorn_server = None  # 保存uvicorn server引用
        self.web_server_thread = None  # 保存Web服务器线程引用
        self._start_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._setup_handlers()
        
    def reset_web_server(self):
        """重置Web服务器状态（在shutdown时调用）"""
        print(f"[INFO] 开始重置Web服务器...", file=sys.stderr)
        
        # 停止uvicorn server释放端口
        if self.uvicorn_server:
            try:
                print(f"[INFO] 正在关闭uvicorn服务器，释放端口...", file=sys.stderr)
                # uvicorn server的shutdown需要在其事件循环中调用
                if self.web_server and self.web_server.loop:
                    import asyncio
                    # 在web服务器的事件循环中调度shutdown
                    asyncio.run_coroutine_threadsafe(
                        self.uvicorn_server.shutdown(),
                        self.web_server.loop
                    )
                    print(f"[INFO] uvicorn服务器shutdown已调度", file=sys.stderr)
            except Exception as e:
                print(f"[ERROR] 停止uvicorn失败: {e}", file=sys.stderr)
        
        # 重置状态
        self.web_server_started = False
        self.web_server = None
        self.uvicorn_server = None
        
        print(f"[SUCCESS] Web服务器状态已重置，端口已释放 ✅", file=sys.stderr)
    
    def start_web_server(self):
        """启动Web服务器（在后台线程）"""
        import sys
        print(f"[Web] start_web_server开始", file=sys.stderr)
        sys.stderr.flush()
        
        if self.web_server_started:
            print(f"[Web] Web服务器已启动，跳过", file=sys.stderr)
            sys.stderr.flush()
            return
        
        print(f"[Web] 创建WebTerminalServer实例...", file=sys.stderr)
        sys.stderr.flush()
        
        self.web_server = WebTerminalServer(self.terminal_manager)
        
        print(f"[Web] WebTerminalServer创建完成", file=sys.stderr)
        sys.stderr.flush()
        
        # 设置shutdown回调
        self.web_server.shutdown_callback = self.reset_web_server
        print(f"[Web] shutdown回调已设置", file=sys.stderr)
        sys.stderr.flush()
        
        def run_web_server():
            import uvicorn
            
            print(f"[WebThread] run_web_server线程开始", file=sys.stderr)
            sys.stderr.flush()
            
            # 创建新的事件循环用于这个线程
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 保存循环引用到web_server
            self.web_server.loop = loop
            print(f"[WebThread] 事件循环创建: {loop}", file=sys.stderr)
            sys.stderr.flush()
            
            # 同时设置到terminal_manager，用于线程安全的事件触发
            self.terminal_manager._web_server_loop = loop
            print(f"[WebThread] 事件循环已设置到terminal_manager", file=sys.stderr)
            sys.stderr.flush()
            
            port = self.web_server.find_available_port()
            self.web_server.port = port
            print(f"[WebThread] 端口已设置: {port}", file=sys.stderr)
            sys.stderr.flush()
            
            print(f"\n=== AI-MCP Terminal Web界面 ===", file=sys.stderr)
            print(f"Web界面地址: http://localhost:{port}", file=sys.stderr)
            print(f"您可以在此查看AI执行的所有终端命令", file=sys.stderr)
            print(f"===========================\n", file=sys.stderr)
            
            # 启动后打开浏览器
            def open_browser():
                time.sleep(2)
                webbrowser.open(f"http://localhost:{port}")
                print(f"[提示] 浏览器已自动打开Web界面", file=sys.stderr)
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            config = uvicorn.Config(
                self.web_server.app,
                host="0.0.0.0",
                port=port,
                log_level="error"  # 降低日志级别
            )
            server = uvicorn.Server(config)
            
            # 保存server引用到外部，以便shutdown时使用
            self.uvicorn_server = server
            
            loop.run_until_complete(server.serve())
        
        web_thread = threading.Thread(target=run_web_server, daemon=True)
        web_thread.start()
        self.web_server_thread = web_thread
        self.web_server_started = True
        
        # 不再阻塞等待，Web服务器在后台启动
        # time.sleep(2) 已移除，避免阻塞MCP
        print(f"[INFO] Web服务器线程已启动，正在后台初始化...", file=sys.stderr)
    
    def _setup_handlers(self):
        """设置MCP处理器"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """列出所有可用工具"""
            return [
                Tool(
                    name="create_session",
                    description="创建新的终端会话。⚠️重要：请务必传入cwd参数为AI当前工作目录，否则终端会在错误的位置创建！💡优化：可以传入initial_command，创建后立即执行命令，减少MCP调用次数！🔥新功能：可以指定shell_type选择终端类型（cmd/powershell/bash等）。首次调用时会自动打开Web界面",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "会话名称（可选，如果不提供则自动生成）"
                            },
                            "cwd": {
                                "type": "string",
                                "description": "⚠️必需！AI的当前工作目录，终端将在此目录创建。请使用os.getcwd()或项目根目录"
                            },
                            "shell_type": {
                                "type": "string",
                                "description": "🔥可选：指定终端类型。可选值：'cmd'(Windows CMD)、'powershell'(PowerShell)、'pwsh'(PowerShell Core)、'bash'(Git Bash/WSL)、'zsh'、'fish'。💡建议：Windows命令用cmd/powershell，Unix命令用bash。如不指定则自动检测最佳shell",
                                "enum": ["cmd", "powershell", "pwsh", "bash", "zsh", "fish", "sh"]
                            },
                            "initial_command": {
                                "type": "string",
                                "description": "💡可选：终端创建后立即执行的命令。这样可以将create+execute合并为一步，提高效率！"
                            }
                        },
                        "required": ["cwd"]
                    }
                ),
                Tool(
                    name="execute_command",
                    description="在指定终端会话中执行命令。命令会异步执行，不会阻塞AI对话。支持长时间运行的命令如npm run等",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "终端会话ID"
                            },
                            "command": {
                                "type": "string",
                                "description": "要执行的命令"
                            }
                        },
                        "required": ["session_id", "command"]
                    }
                ),
                Tool(
                    name="broadcast_command",
                    description="向多个终端会话并发执行同一命令（真正的并发，使用asyncio.gather）",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "终端会话ID列表（可选，如果不提供则广播到所有会话）"
                            },
                            "command": {
                                "type": "string",
                                "description": "要执行的命令"
                            }
                        },
                        "required": ["command"]
                    }
                ),
                Tool(
                    name="execute_batch",
                    description="批量并发执行：同时向多个终端发送不同的命令（真正的并发）。注意：需要终端已存在",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "commands": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "session_id": {
                                            "type": "string",
                                            "description": "终端会话ID"
                                        },
                                        "command": {
                                            "type": "string",
                                            "description": "要执行的命令"
                                        }
                                    },
                                    "required": ["session_id", "command"]
                                },
                                "description": "命令列表，每个包含session_id和command"
                            }
                        },
                        "required": ["commands"]
                    }
                ),
                Tool(
                    name="create_batch",
                    description="🚀最高效：批量创建终端并立即执行初始命令（创建+执行一步完成，真正的并发）。适合同时启动多个服务，效率最高！🔥新功能：每个终端可指定不同的shell_type",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sessions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "description": "会话名称"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "description": "工作目录"
                                        },
                                        "shell_type": {
                                            "type": "string",
                                            "description": "可选：指定终端类型（cmd/powershell/bash等），不指定则自动检测",
                                            "enum": ["cmd", "powershell", "pwsh", "bash", "zsh", "fish", "sh"]
                                        },
                                        "initial_command": {
                                            "type": "string",
                                            "description": "创建后立即执行的命令"
                                        }
                                    },
                                    "required": ["name", "cwd", "initial_command"]
                                },
                                "description": "会话列表，每个包含name、cwd、可选shell_type和initial_command"
                            }
                        },
                        "required": ["sessions"]
                    }
                ),
                Tool(
                    name="get_all_sessions",
                    description="获取所有终端会话的列表和状态",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_session_status",
                    description="获取指定终端会话的详细状态",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "终端会话ID"
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="get_output",
                    description="获取终端会话的输出历史（单个终端）。💡提示：如果需要读取多个终端，使用get_batch_output更高效！",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "终端会话ID"
                            },
                            "lines": {
                                "type": "number",
                                "description": "获取最近N行输出（默认100行，only_last_command=False时生效）"
                            },
                            "only_last_command": {
                                "type": "boolean",
                                "description": "💡性能优化：是否只获取最后一次命令的输出（默认false）。推荐设为true，避免读取大量历史数据"
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="get_batch_output",
                    description="🚀批量获取多个终端的输出（多线程并发，速度极快！）💡提示：不提供session_ids则自动获取所有终端。默认只返回每个终端最后一次命令的输出，避免大量历史数据传输",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "终端会话ID列表（可选，不提供则获取所有终端的输出）"
                            },
                            "only_last_command": {
                                "type": "boolean",
                                "description": "是否只获取最后一次命令的输出（默认true，性能优化）。设为false会返回更多历史"
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="kill_session",
                    description="终止指定的终端会话",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "终端会话ID"
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="get_stats",
                    description="获取系统统计信息，包括内存使用率、终端数量等",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """调用工具"""
            import sys
            
            # 强制flush所有输出，避免缓冲区问题
            sys.stdout.flush()
            sys.stderr.flush()
            
            print(f"\n[MCP] ========== 工具调用开始 ==========", file=sys.stderr)
            sys.stderr.flush()
            print(f"[MCP] 工具名: {name}", file=sys.stderr)
            sys.stderr.flush()
            print(f"[MCP] 参数: {arguments}", file=sys.stderr)
            sys.stderr.flush()
            
            # 首次调用时启动Web服务器（异步，不阻塞）
            # 检查Web服务器是否真正可用
            web_server_exists = self.web_server is not None
            
            print(f"[MCP] Web服务器检查: started={self.web_server_started}, exists={web_server_exists}", file=sys.stderr)
            sys.stderr.flush()
            
            if not self.web_server_started:
                try:
                    print(f"[MCP] 首次调用，启动Web服务器...", file=sys.stderr)
                    sys.stderr.flush()
                    
                    self.start_web_server()
                    print(f"[MCP] Web服务器启动完成", file=sys.stderr)
                    sys.stderr.flush()
                except Exception as web_err:
                    print(f"[MCP] Web服务器启动失败: {web_err}", file=sys.stderr)
                    import traceback
                    traceback.print_exc(file=sys.stderr)
                    sys.stderr.flush()
                    # 继续执行，不因Web服务器失败而中断MCP
            else:
                print(f"[MCP] Web服务器已启动，跳过启动步骤", file=sys.stderr)
                sys.stderr.flush()
            
            try:
                if name == "create_session":
                    # 获取当前工作目录（AI的工作目录）
                    import os
                    cwd = arguments.get("cwd") or os.getcwd()
                    initial_command = arguments.get("initial_command")
                    shell_type_arg = arguments.get("shell_type")  # 获取用户指定的终端类型
                    
                    print(f"[MCP] create_session参数: cwd={cwd}, shell_type={shell_type_arg}, initial_command={initial_command}", file=sys.stderr)
                    sys.stderr.flush()
                    
                    session_id = self.terminal_manager.create_session(
                        name=arguments.get("name"),
                        cwd=cwd,
                        shell_type=shell_type_arg  # 传递shell_type参数
                    )
                    
                    # 获取会话信息
                    session_info = self.terminal_manager.get_session_status(session_id)
                    shell_type = session_info.get('shell_type', 'unknown')
                    
                    web_url = f"http://localhost:{self.web_server.port}" if self.web_server else "Web服务器启动中..."
                    
                    # 根据Shell类型提供命令建议
                    shell_tips = {
                        'bash': "✅ 使用Unix命令：ls, pwd, cd, echo $USER, grep, curl\n⚠️ Windows CMD命令需要：cmd /c \"命令\"",
                        'zsh': "✅ 使用Unix命令：ls, pwd, cd, echo $USER, grep, curl\n⚠️ Windows CMD命令需要：cmd /c \"命令\"",
                        'fish': "✅ 使用Unix命令：ls, pwd, cd, echo $USER, grep, curl\n⚠️ Windows CMD命令需要：cmd /c \"命令\"",
                        'powershell': "✅ 使用PowerShell命令：Get-ChildItem, Get-Location, $env:USERNAME\n✅ 支持管道和对象操作",
                        'pwsh': "✅ 使用PowerShell Core命令：Get-ChildItem, Get-Location, $env:USERNAME\n✅ 跨平台PowerShell",
                        'cmd': "✅ 使用Windows CMD命令：dir, echo %USERNAME%, findstr\n⚠️ Unix命令不可用",
                        'sh': "✅ 使用基本Unix命令：ls, pwd, cd, echo $USER",
                        'dash': "✅ 使用基本Unix命令：ls, pwd, cd, echo $USER"
                    }
                    
                    tip = shell_tips.get(shell_type, "⚠️ 未知Shell类型，请谨慎使用命令")
                    
                    # 如果提供了初始命令，立即执行
                    if initial_command:
                        print(f"[MCP] 检测到initial_command，立即执行: {initial_command}", file=sys.stderr)
                        sys.stderr.flush()
                        await self.terminal_manager.execute_command(
                            session_id, 
                            initial_command, 
                            source="ai"
                        )
                        
                        result = {
                            "success": True,
                            "session_id": session_id,
                            "cwd": cwd,
                            "shell_type": shell_type,
                            "web_url": web_url,
                            "command_tips": tip,
                            "initial_command": initial_command,
                            "initial_command_status": "executing",
                            "message": f"""✅ 终端会话已创建并自动执行命令

📋 会话信息:
  - 会话ID: {session_id}
  - Shell类型: {shell_type}
  - 工作目录: {cwd}
  - Web界面: {web_url}

🚀 初始命令: {initial_command}
🔄 状态: 后台执行中

💡 优势: 创建+执行一步完成，效率提升50%！
   命令输出将实时显示在Web界面。

💡 命令使用建议:
{tip}"""
                        }
                    else:
                        result = {
                            "success": True,
                            "session_id": session_id,
                            "cwd": cwd,
                            "shell_type": shell_type,
                            "web_url": web_url,
                            "command_tips": tip,
                            "message": f"""✅ 终端会话已创建成功

📋 会话信息:
  - 会话ID: {session_id}
  - Shell类型: {shell_type}
  - 工作目录: {cwd}
  - Web界面: {web_url}

💡 命令使用建议:
{tip}

💡 提示: 下次可以使用initial_command参数在创建时就执行命令，减少MCP调用！
🌐 提示: 用户可在Web界面实时查看所有操作"""
                        }
                
                elif name == "execute_command":
                    print(f"[DEBUG] execute_command开始", file=sys.stderr)
                    sys.stderr.flush()
                    
                    session_id = arguments["session_id"]
                    command = arguments["command"]
                    
                    print(f"[DEBUG] session_id={session_id}, command={command}", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # 执行命令（立即返回，不等待完成）
                    exec_result = await self.terminal_manager.execute_command(
                        session_id, command, source="ai"
                    )
                    
                    print(f"[DEBUG] exec_result={exec_result}", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # 检查exec_result是否为None
                    if exec_result is None:
                        print(f"[ERROR] execute_command返回None！", file=sys.stderr)
                        sys.stderr.flush()
                        result = {
                            "success": False,
                            "error": "execute_command returned None",
                            "session_id": session_id,
                            "command": command
                        }
                    else:
                        print(f"[DEBUG] 构建result", file=sys.stderr)
                        sys.stderr.flush()
                        
                        web_url = f"http://localhost:{self.web_server.port}" if self.web_server else ""
                        
                        result = {
                            "success": True,
                            "session_id": session_id,
                            "command": command,
                            "status": "executing",  # 正在执行中
                            "web_url": web_url,
                            "exec_result": exec_result,  # 添加原始结果
                            "message": f"""✅ 命令已发送到终端 {session_id}（后台执行，不阻塞AI对话）

📋 命令: {command}
🔄 状态: 后台执行中
🌐 实时输出: {web_url}

💡 您可以继续与AI对话，命令在后台运行。
   所有输出将实时显示在Web界面。"""
                        }
                        
                        print(f"[DEBUG] result已构建: {result is not None}", file=sys.stderr)
                        sys.stderr.flush()
                
                elif name == "broadcast_command":
                    import sys
                    command = arguments["command"]
                    session_ids = arguments.get("session_ids")
                    
                    print(f"[DEBUG] broadcast_command call", file=sys.stderr)
                    sys.stderr.flush()
                    
                    if not session_ids:
                        session_ids = [s["session_id"] for s in self.terminal_manager.get_all_sessions()]
                        print(f"  Auto get session_ids: {session_ids}", file=sys.stderr)
                        sys.stderr.flush()
                    
                    # 真正的并发执行 - 使用 asyncio.gather
                    print(f"  Broadcasting to {len(session_ids)} terminals concurrently", file=sys.stderr)
                    sys.stderr.flush()
                    
                    tasks = [
                        self.terminal_manager.execute_command(sid, command, source="ai")
                        for sid in session_ids
                    ]
                    await asyncio.gather(*tasks)
                    
                    web_url = f"http://localhost:{self.web_server.port}" if self.web_server else ""
                    
                    result = {
                        "success": True,
                        "session_count": len(session_ids),
                        "session_ids": session_ids,
                        "command": command,
                        "status": "executing",  # 所有终端都在执行中
                        "web_url": web_url,
                        "message": f"""✅ 命令已广播到 {len(session_ids)} 个终端（后台并发执行）

📋 命令: {command}
📊 终端数: {len(session_ids)}
🔄 状态: 所有终端后台执行中
🌐 实时输出: {web_url}

💡 您可以继续与AI对话，命令在后台运行。
   所有终端的输出将实时显示在Web界面。"""
                    }
                    print(f"[DEBUG] broadcast_command result: {result}", file=sys.stderr)
                    sys.stderr.flush()
                
                elif name == "execute_batch":
                    import sys
                    commands = arguments["commands"]
                    
                    print(f"[DEBUG] execute_batch call: {len(commands)} commands", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # 验证所有会话是否存在
                    invalid_sessions = []
                    for cmd in commands:
                        sid = cmd["session_id"]
                        if sid not in self.terminal_manager.sessions:
                            invalid_sessions.append(sid)
                    
                    if invalid_sessions:
                        result = {
                            "success": False,
                            "error": f"以下会话不存在: {', '.join(invalid_sessions)}",
                            "invalid_sessions": invalid_sessions
                        }
                    else:
                        # 真正的并发执行 - 使用 asyncio.gather
                        print(f"  Executing {len(commands)} commands concurrently", file=sys.stderr)
                        sys.stderr.flush()
                        
                        tasks = [
                            self.terminal_manager.execute_command(
                                cmd["session_id"], 
                                cmd["command"], 
                                source="ai"
                            )
                            for cmd in commands
                        ]
                        results = await asyncio.gather(*tasks)
                        
                        web_url = f"http://localhost:{self.web_server.port}" if self.web_server else ""
                        
                        result = {
                            "success": True,
                            "executed_count": len(commands),
                            "commands": commands,
                            "status": "executing",
                            "web_url": web_url,
                            "message": f"""✅ 批量命令已并发执行到 {len(commands)} 个终端
    
📋 命令数: {len(commands)}
🔄 状态: 所有命令并发执行中
🌐 实时输出: {web_url}

💡 真正的并发执行：所有命令同时开始，互不等待。
   每个终端的输出将实时显示在Web界面。"""
                        }
                        print(f"[DEBUG] execute_batch result: {result}", file=sys.stderr)
                        sys.stderr.flush()
                
                elif name == "create_batch":
                    import sys
                    sessions = arguments["sessions"]
                    
                    print(f"[DEBUG] create_batch call: {len(sessions)} sessions", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # 并发创建所有会话并执行初始命令
                    async def create_and_execute(session_info):
                        name = session_info["name"]
                        cwd = session_info["cwd"]
                        initial_command = session_info["initial_command"]
                        shell_type = session_info.get("shell_type")  # 获取可选的shell_type
                        
                        # 创建会话
                        session_id = self.terminal_manager.create_session(
                            name=name,
                            cwd=cwd,
                            shell_type=shell_type  # 传递shell_type
                        )
                        
                        # 立即执行初始命令
                        await self.terminal_manager.execute_command(
                            session_id,
                            initial_command,
                            source="ai"
                        )
                        
                        return {
                            "session_id": session_id,
                            "name": name,
                            "cwd": cwd,
                            "initial_command": initial_command,
                            "status": "executing"
                        }
                    
                    print(f"  Creating {len(sessions)} sessions concurrently with initial commands", file=sys.stderr)
                    sys.stderr.flush()
                    
                    tasks = [create_and_execute(s) for s in sessions]
                    created_sessions = await asyncio.gather(*tasks)
                    
                    web_url = f"http://localhost:{self.web_server.port}" if self.web_server else ""
                    
                    result = {
                        "success": True,
                        "created_count": len(created_sessions),
                        "sessions": created_sessions,
                        "web_url": web_url,
                        "message": f"""✅ 批量创建 {len(created_sessions)} 个终端并同时执行初始命令

📋 创建数量: {len(created_sessions)}
🚀 每个终端的初始命令都已开始执行
🔄 状态: 所有命令并发执行中
🌐 实时输出: {web_url}

💡 效率提升：
  - 旧方式：创建N个终端 + 执行N个命令 = 2N次MCP调用
  - 新方式：批量创建并执行 = 1次MCP调用
  - 提升：{len(created_sessions)*2}次调用 → 1次调用，效率提升{len(created_sessions)*200}%！

🎯 所有终端已同时创建并开始执行，真正的并发！"""
                    }
                    print(f"[DEBUG] create_batch result: created {len(created_sessions)} sessions", file=sys.stderr)
                    sys.stderr.flush()
                
                elif name == "get_all_sessions":
                    print(f"[MCP] 开始执行get_all_sessions", file=sys.stderr)
                    sys.stderr.flush()
                    sessions = self.terminal_manager.get_all_sessions()
                    print(f"[MCP] 获取到{len(sessions)}个会话", file=sys.stderr)
                    sys.stderr.flush()
                    result = {
                        "success": True,
                        "sessions": sessions,
                        "count": len(sessions)
                    }
                    print(f"[MCP] get_all_sessions结果已准备", file=sys.stderr)
                    sys.stderr.flush()
                
                elif name == "get_session_status":
                    session_id = arguments["session_id"]
                    status = self.terminal_manager.get_session_status(session_id)
                    
                    if status is None:
                        result = {
                            "success": False,
                            "error": f"会话 {session_id} 不存在"
                        }
                    else:
                        result = {
                            "success": True,
                            "status": status
                        }
                
                elif name == "get_output":
                    print(f"[MCP] 开始执行get_output", file=sys.stderr)
                    sys.stderr.flush()
                    session_id = arguments["session_id"]
                    lines = arguments.get("lines", 100)
                    only_last_command = arguments.get("only_last_command", False)
                    print(f"[MCP] 参数: session_id={session_id}, lines={lines}, only_last_command={only_last_command}", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # 检查会话是否存在
                    if session_id not in self.terminal_manager.sessions:
                        print(f"[MCP] 会话不存在: {session_id}", file=sys.stderr)
                        sys.stderr.flush()
                        result = {
                            "success": False,
                            "error": f"会话 {session_id} 不存在",
                            "session_id": session_id,
                            "output": []
                        }
                        print(f"[MCP] 返回错误结果: {result}", file=sys.stderr)
                        sys.stderr.flush()
                    else:
                        # 获取输出
                        print(f"[MCP] 调用terminal_manager.get_output...", file=sys.stderr)
                        sys.stderr.flush()
                        success, output, metadata = self.terminal_manager.get_output(
                            session_id, 
                            lines=lines,
                            only_last_command=only_last_command
                        )
                        print(f"[MCP] 获取到输出，成功: {success}, 条目数: {len(output) if output else 0}", file=sys.stderr)
                        if metadata:
                            print(f"[MCP] 元数据: {metadata.get('ai_suggestion', {}).get('action', 'N/A')}", file=sys.stderr)
                        sys.stderr.flush()
                        
                        # 确保正确处理不存在的会话
                        if not success:
                            result = {
                                "success": False,
                                "error": f"会话 {session_id} 不存在",
                                "session_id": session_id,
                                "output": []
                            }
                            print(f"[MCP] 会话不存在，返回错误结果: {result}", file=sys.stderr)
                            sys.stderr.flush()
                        else:
                            result = {
                                "success": True,
                                "session_id": session_id,
                                "output": output,
                                "only_last_command": only_last_command
                            }
                            
                            # 添加元数据（帮助AI判断是否需要继续等待）
                            if metadata:
                                result["metadata"] = metadata
                                
                                # 优先处理紧急通知（重复查询）
                                if "ai_urgent_notice" in metadata:
                                    urgent = metadata["ai_urgent_notice"]
                                    cmd_info = f"命令: {urgent.get('command', 'N/A')}\n  终端类型: {urgent.get('shell_type', 'N/A')}"
                                    result["ai_urgent_notice"] = f"""
🚨🚨🚨 {urgent['action']} 🚨🚨🚨

📊 当前状态:
  - {cmd_info}
  - 查询次数: {metadata.get('query_count', 'N/A')}
  - 当前输出: {urgent['current_output'][:150]}{'...' if len(urgent['current_output']) > 150 else ''}
  - 原因: {urgent['reason']}

⚠️⚠️⚠️ 必须立即采取行动（不要再查询了）:
{chr(10).join(f'  {sug}' for sug in urgent['suggestions'])}

💡 停止重复查询！AI应该：
  ❌ 不要再调用 get_output
  ✅ 立即执行 kill_session 结束卡住的会话
  ✅ 创建正确类型的终端（Windows命令用cmd，Unix命令用bash）
  ✅ 继续其他任务
"""
                                # 如果有AI建议，添加友好的提示消息
                                elif "ai_suggestion" in metadata:
                                    suggestion = metadata["ai_suggestion"]
                                    severity = suggestion.get('severity', 'medium')
                                    
                                    # 根据严重性调整图标
                                    if severity == 'high':
                                        icon = "🚨"
                                        urgency = "【高优先级】"
                                    elif severity == 'medium':
                                        icon = "⚠️"
                                        urgency = "【中等优先级】"
                                    else:
                                        icon = "💡"
                                        urgency = "【提示】"
                                    
                                    result["ai_notice"] = f"""
{icon} {urgency} {suggestion['action']}

📊 运行状态:
  - 命令: {metadata.get('command', 'N/A')}
  - 运行时间: {metadata.get('running_seconds', 0)}秒
  - 输出长度: {metadata.get('output_length', 0)}字符

💡 建议的操作:
{chr(10).join(f'  • {opt}' for opt in suggestion['options'])}

原因: {suggestion['reason']}

🎯 后续步骤:
  1. 如果是错误的终端类型 → kill_session + 创建正确终端
  2. 如果服务已启动 → 继续其他操作
  3. 如果卡住 → kill_session + 重新尝试
"""
                            print(f"[MCP] 会话存在，返回输出结果", file=sys.stderr)
                            sys.stderr.flush()
                    
                    print(f"[MCP] get_output结果已准备", file=sys.stderr)
                    sys.stderr.flush()
                
                elif name == "get_batch_output":
                    print(f"[MCP] 开始执行get_batch_output", file=sys.stderr)
                    sys.stderr.flush()
                    
                    session_ids = arguments.get("session_ids")
                    only_last_command = arguments.get("only_last_command", True)  # 默认为True，性能优化
                    
                    # 如果没有提供session_ids，获取所有会话
                    if not session_ids:
                        session_ids = [s["session_id"] for s in self.terminal_manager.get_all_sessions()]
                        print(f"[MCP] 未提供session_ids，自动获取所有: {session_ids}", file=sys.stderr)
                        sys.stderr.flush()
                    
                    print(f"[MCP] 批量获取{len(session_ids)}个终端输出，only_last_command={only_last_command}", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # 批量获取输出
                    outputs = self.terminal_manager.get_batch_output(
                        session_ids,
                        only_last_command=only_last_command
                    )
                    
                    # 统计
                    total_commands = sum(len(output) for output in outputs.values())
                    
                    result = {
                        "success": True,
                        "session_count": len(session_ids),
                        "total_commands": total_commands,
                        "only_last_command": only_last_command,
                        "outputs": outputs,
                        "message": f"""✅ 批量获取 {len(session_ids)} 个终端的输出

📊 统计:
  - 终端数: {len(session_ids)}
  - 命令总数: {total_commands}
  - 模式: {'仅最后一次命令' if only_last_command else '完整历史'}

💡 性能优化: 只读取最后一次命令的输出，避免传输大量历史数据。
   如需完整历史，设置 only_last_command=false"""
                    }
                    
                    print(f"[MCP] get_batch_output完成: {len(session_ids)}个终端, {total_commands}个命令", file=sys.stderr)
                    sys.stderr.flush()
                
                elif name == "kill_session":
                    session_id = arguments["session_id"]
                    success = await self.terminal_manager.kill_session(session_id)
                    
                    result = {
                        "success": success,
                        "session_id": session_id,
                        "message": f"终端 {session_id} 已终止" if success else f"终端 {session_id} 不存在或已终止"
                    }
                
                elif name == "get_stats":
                    import sys
                    print(f"[DEBUG] get_stats调用", file=sys.stderr)
                    
                    stats = self.terminal_manager.get_stats()
                    print(f"[DEBUG] stats结果: {stats}", file=sys.stderr)
                    
                    memory_check = self.terminal_manager.check_memory_and_suggest_cleanup()
                    print(f"[DEBUG] memory_check结果: {memory_check}", file=sys.stderr)
                    
                    result = {
                        "success": True,
                        "stats": stats,
                        "memory_check": memory_check
                    }
                    
                    # 如果需要清理，添加建议
                    if memory_check and memory_check.get("should_cleanup"):
                        result["warning"] = "内存使用率过高，建议清理终端"
                        result["cleanup_suggestions"] = memory_check.get("suggestions", [])
                    
                    print(f"[DEBUG] get_stats返回结果: {result}", file=sys.stderr)
                
                else:
                    result = {
                        "success": False,
                        "error": f"未知工具: {name}"
                    }
                
                import sys
                print(f"\n[MCP] 工具 {name} 执行完成", file=sys.stderr)
                print(f"[MCP] 准备返回result: {result}", file=sys.stderr)
                
                # ===== 全局错误保护：确保永远返回有效结果 =====
                
                # 1. 确保result已定义
                if 'result' not in locals() or result is None:
                    print(f"[ERROR] result未定义或为None！工具: {name}", file=sys.stderr)
                    sys.stderr.flush()
                    result = {
                        "success": False,
                        "error": f"内部错误：工具 {name} 未正确设置返回值",
                        "tool": name,
                        "recovery": "系统已捕获错误并返回默认值",
                        "suggestion": "请重试或使用不同的参数"
                    }
                
                # 2. 验证result的类型
                if not isinstance(result, dict):
                    print(f"[ERROR] result不是字典类型！工具: {name}, 类型: {type(result)}, 值: {result}", file=sys.stderr)
                    sys.stderr.flush()
                    result = {
                        "success": False,
                        "error": f"内部错误：工具 {name} 返回了无效类型: {type(result)}",
                        "tool": name,
                        "recovery": "系统已将返回值转换为标准格式"
                    }
                
                # 3. 确保必要字段存在
                if "success" not in result:
                    print(f"[WARNING] result缺少success字段，自动添加！工具: {name}", file=sys.stderr)
                    sys.stderr.flush()
                    result["success"] = False
                
                # 4. 确保错误时有错误信息
                if not result.get("success") and "error" not in result:
                    print(f"[WARNING] 失败但缺少error字段，自动添加！工具: {name}", file=sys.stderr)
                    sys.stderr.flush()
                    result["error"] = f"工具 {name} 执行失败，但未提供详细错误信息"
                
                # 5. 添加调试信息（帮助定位问题）
                if not result.get("success"):
                    result["debug_info"] = {
                        "tool": name,
                        "arguments": arguments,
                        "timestamp": datetime.now().isoformat()
                    }
                
                # 序列化JSON
                try:
                    print(f"[MCP] 开始JSON序列化...", file=sys.stderr)
                    sys.stderr.flush()
                    json_text = json.dumps(result, ensure_ascii=False, indent=2)
                    print(f"[MCP] JSON序列化成功，长度: {len(json_text)}", file=sys.stderr)
                    sys.stderr.flush()
                except Exception as json_err:
                    print(f"[ERROR] JSON序列化失败: {json_err}", file=sys.stderr)
                    print(f"[ERROR] result内容: {result}", file=sys.stderr)
                    json_text = json.dumps({
                        "success": False,
                        "error": f"JSON序列化失败: {str(json_err)}"
                    }, ensure_ascii=False, indent=2)
                
                response = [TextContent(
                    type="text",
                    text=json_text
                )]
                print(f"[MCP] 返回response，数量: {len(response)}", file=sys.stderr)
                print(f"[MCP] ========== 工具调用结束 ==========\n", file=sys.stderr)
                return response
                
            except asyncio.TimeoutError:
                # 超时错误（单独处理）
                import sys
                print(f"[ERROR] 工具执行超时: {name}", file=sys.stderr)
                sys.stderr.flush()
                
                error_result = {
                    "success": False,
                    "error": f"工具 {name} 执行超时",
                    "error_type": "TimeoutError",
                    "tool": name,
                    "recovery": "操作已超时但系统正常运行",
                    "suggestion": "请检查命令是否正确，或增加超时时间",
                    "debug_info": {
                        "arguments": arguments,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                return [TextContent(
                    type="text",
                    text=json.dumps(error_result, ensure_ascii=False, indent=2)
                )]
                
            except KeyError as e:
                # 参数缺失错误
                import sys
                print(f"[ERROR] 工具参数缺失: {name}, 缺少参数: {e}", file=sys.stderr)
                sys.stderr.flush()
                
                error_result = {
                    "success": False,
                    "error": f"缺少必需参数: {str(e)}",
                    "error_type": "KeyError",
                    "tool": name,
                    "recovery": "系统已捕获参数错误",
                    "suggestion": f"请提供缺少的参数: {str(e)}",
                    "debug_info": {
                        "provided_arguments": list(arguments.keys()) if arguments else [],
                        "missing_parameter": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                }
                return [TextContent(
                    type="text",
                    text=json.dumps(error_result, ensure_ascii=False, indent=2)
                )]
                
            except ValueError as e:
                # 值错误（如会话不存在）
                import sys
                print(f"[ERROR] 工具参数值错误: {name}, 错误: {e}", file=sys.stderr)
                sys.stderr.flush()
                
                error_result = {
                    "success": False,
                    "error": str(e),
                    "error_type": "ValueError",
                    "tool": name,
                    "recovery": "系统已捕获值错误",
                    "suggestion": "请检查参数值是否正确（如会话ID是否存在）",
                    "debug_info": {
                        "arguments": arguments,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                return [TextContent(
                    type="text",
                    text=json.dumps(error_result, ensure_ascii=False, indent=2)
                )]
                
            except Exception as e:
                # 通用异常捕获（兜底）
                import sys
                import traceback
                print(f"[ERROR] 工具执行异常: {name}", file=sys.stderr)
                print(f"[ERROR] 异常类型: {type(e).__name__}", file=sys.stderr)
                print(f"[ERROR] 异常信息: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                sys.stderr.flush()
                
                error_result = {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "tool": name,
                    "recovery": "系统已捕获未知错误但保持运行",
                    "suggestion": "这是一个未预期的错误，请检查参数或重试",
                    "debug_info": {
                        "arguments": arguments,
                        "exception_type": type(e).__name__,
                        "traceback": traceback.format_exc(),
                        "timestamp": datetime.now().isoformat()
                    }
                }
                return [TextContent(
                    type="text",
                    text=json.dumps(error_result, ensure_ascii=False, indent=2)
                )]
    
    async def run(self):
        """运行MCP服务器"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """主函数"""
    server = MCPTerminalServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())

