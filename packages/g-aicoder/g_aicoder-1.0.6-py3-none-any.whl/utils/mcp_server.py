#!/usr/bin/env python3
"""
MCP (Model Context Protocol) server implementation for Cline Clone
Provides external tool integration and API calling capabilities
"""

import asyncio
import json
import aiohttp
import logging
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import os

class MCPServer:
    """MCP server for external tool integration"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tools = {}
        self.resources = {}
        self.logger = logging.getLogger('mcp_server')

    async def initialize(self):
        """Initialize MCP server and load tools"""
        await self.load_builtin_tools()
        await self.load_external_tools()

    async def load_builtin_tools(self):
        """Load built-in MCP tools"""
        self.tools = {
            'http_request': self.http_request_tool(),
            'file_system': self.file_system_tool(),
            'git_operations': self.git_operations_tool(),
            'process_runner': self.process_runner_tool(),
            'web_search': self.web_search_tool(),
            'database_query': self.database_query_tool(),
        }

    async def load_external_tools(self):
        """Load external MCP tools from configuration"""
        # Load tools from config.json if specified
        external_tools = self.config.get('mcp', {}).get('external_tools', [])
        for tool_config in external_tools:
            if tool_config.get('enabled', False):
                await self.load_external_tool(tool_config)

    async def load_external_tool(self, tool_config: Dict[str, Any]):
        """Load a single external tool"""
        try:
            tool_name = tool_config['name']
            tool_type = tool_config.get('type', 'http')

            if tool_type == 'http':
                self.tools[tool_name] = self.create_http_tool(tool_config)
            elif tool_type == 'websocket':
                self.tools[tool_name] = self.create_websocket_tool(tool_config)
            elif tool_type == 'executable':
                self.tools[tool_name] = self.create_executable_tool(tool_config)

            self.logger.info(f"Loaded external tool: {tool_name}")
        except Exception as e:
            self.logger.error(f"Failed to load external tool {tool_config.get('name', 'unknown')}: {e}")

    def http_request_tool(self) -> Dict[str, Any]:
        """Built-in HTTP request tool"""
        return {
            'name': 'http_request',
            'description': 'Make HTTP requests to REST APIs',
            'parameters': {
                'method': {'type': 'string', 'enum': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']},
                'url': {'type': 'string'},
                'headers': {'type': 'object', 'optional': True},
                'body': {'type': 'string', 'optional': True},
                'timeout': {'type': 'integer', 'default': 30}
            },
            'handler': self.handle_http_request
        }

    def file_system_tool(self) -> Dict[str, Any]:
        """Built-in file system operations tool"""
        return {
            'name': 'file_system',
            'description': 'Advanced file system operations with permissions and metadata',
            'parameters': {
                'operation': {'type': 'string', 'enum': ['read', 'write', 'chmod', 'chown', 'stat']},
                'path': {'type': 'string'},
                'content': {'type': 'string', 'optional': True},
                'mode': {'type': 'integer', 'optional': True},
                'encoding': {'type': 'string', 'default': 'utf-8'}
            },
            'handler': self.handle_file_system
        }

    def git_operations_tool(self) -> Dict[str, Any]:
        """Built-in Git operations tool"""
        return {
            'name': 'git_operations',
            'description': 'Git repository operations',
            'parameters': {
                'operation': {'type': 'string', 'enum': ['status', 'commit', 'push', 'pull', 'clone', 'branch', 'log']},
                'repo_path': {'type': 'string', 'default': '.'},
                'message': {'type': 'string', 'optional': True},
                'branch': {'type': 'string', 'optional': True},
                'remote': {'type': 'string', 'optional': True}
            },
            'handler': self.handle_git_operations
        }

    def process_runner_tool(self) -> Dict[str, Any]:
        """Built-in process runner with advanced options"""
        return {
            'name': 'process_runner',
            'description': 'Run system processes with full control',
            'parameters': {
                'command': {'type': 'string'},
                'args': {'type': 'array', 'items': {'type': 'string'}, 'optional': True},
                'cwd': {'type': 'string', 'optional': True},
                'env': {'type': 'object', 'optional': True},
                'timeout': {'type': 'integer', 'default': 300},
                'background': {'type': 'boolean', 'default': False},
                'shell': {'type': 'boolean', 'default': True}
            },
            'handler': self.handle_process_runner
        }

    def web_search_tool(self) -> Dict[str, Any]:
        """Built-in web search tool"""
        return {
            'name': 'web_search',
            'description': 'Search the web for information',
            'parameters': {
                'query': {'type': 'string'},
                'engine': {'type': 'string', 'enum': ['google', 'bing', 'duckduckgo'], 'default': 'duckduckgo'},
                'max_results': {'type': 'integer', 'default': 5}
            },
            'handler': self.handle_web_search
        }

    def database_query_tool(self) -> Dict[str, Any]:
        """Built-in database query tool"""
        return {
            'name': 'database_query',
            'description': 'Execute database queries',
            'parameters': {
                'connection_string': {'type': 'string'},
                'query': {'type': 'string'},
                'driver': {'type': 'string', 'enum': ['sqlite3', 'mysql', 'postgresql'], 'default': 'sqlite3'}
            },
            'handler': self.handle_database_query
        }

    def create_http_tool(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a configurable HTTP tool for external APIs"""
        return {
            'name': config['name'],
            'description': config.get('description', f"HTTP API tool for {config['name']}"),
            'parameters': config.get('parameters', {
                'method': {'type': 'string', 'enum': ['GET', 'POST', 'PUT', 'DELETE']},
                'endpoint': {'type': 'string'},
                'data': {'type': 'object', 'optional': True}
            }),
            'config': config,
            'handler': self.handle_configurable_http
        }

    def create_websocket_tool(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a WebSocket tool for real-time communication"""
        return {
            'name': config['name'],
            'description': config.get('description', f"WebSocket tool for {config['name']}"),
            'parameters': {
                'action': {'type': 'string', 'enum': ['connect', 'send', 'close']},
                'message': {'type': 'string', 'optional': True}
            },
            'config': config,
            'handler': self.handle_websocket
        }

    def create_executable_tool(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a tool that runs external executables"""
        return {
            'name': config['name'],
            'description': config.get('description', f"Executable tool for {config['name']}"),
            'parameters': config.get('parameters', {
                'args': {'type': 'array', 'items': {'type': 'string'}, 'optional': True}
            }),
            'config': config,
            'handler': self.handle_executable
        }

    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Call a tool by name with parameters"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")

        tool = self.tools[tool_name]
        handler = tool['handler']

        try:
            # Validate parameters against tool schema
            self.validate_parameters(parameters, tool.get('parameters', {}))

            # Call the handler
            return await handler(parameters, tool)

        except Exception as e:
            self.logger.error(f"Tool {tool_name} execution failed: {e}")
            raise

    def validate_parameters(self, parameters: Dict[str, Any], schema: Dict[str, Any]):
        """Validate parameters against schema"""
        for param_name, param_config in schema.items():
            if not param_config.get('optional', False) and param_name not in parameters:
                raise ValueError(f"Required parameter '{param_name}' is missing")

            if param_name in parameters:
                param_value = parameters[param_name]
                expected_type = param_config.get('type')

                if expected_type and not self.validate_type(param_value, expected_type):
                    raise ValueError(f"Parameter '{param_name}' must be of type {expected_type}")

                if 'enum' in param_config and param_value not in param_config['enum']:
                    raise ValueError(f"Parameter '{param_name}' must be one of: {param_config['enum']}")

    def validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type"""
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'integer':
            return isinstance(value, int)
        elif expected_type == 'boolean':
            return isinstance(value, bool)
        elif expected_type == 'array':
            return isinstance(value, list)
        elif expected_type == 'object':
            return isinstance(value, dict)
        return True

    # Tool handlers
    async def handle_http_request(self, params: Dict[str, Any], tool: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HTTP request tool"""
        try:
            timeout = aiohttp.ClientTimeout(total=params.get('timeout', 30))
            async with aiohttp.ClientSession(timeout=timeout) as session:
                method = params['method'].upper()
                url = params['url']

                kwargs = {}
                if 'headers' in params:
                    kwargs['headers'] = params['headers']
                if 'body' in params and method in ['POST', 'PUT', 'PATCH']:
                    kwargs['data'] = params['body']

                async with session.request(method, url, **kwargs) as response:
                    return {
                        'status': response.status,
                        'headers': dict(response.headers),
                        'text': await response.text(),
                        'url': str(response.url)
                    }
        except Exception as e:
            return {'error': str(e)}

    async def handle_file_system(self, params: Dict[str, Any], tool: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file system operations"""
        operation = params['operation']
        path = params['path']

        try:
            if operation == 'read':
                encoding = params.get('encoding', 'utf-8')
                with open(path, 'r', encoding=encoding) as f:
                    return {'content': f.read()}
            elif operation == 'write':
                encoding = params.get('encoding', 'utf-8')
                with open(path, 'w', encoding=encoding) as f:
                    f.write(params.get('content', ''))
                return {'success': True}
            elif operation == 'stat':
                stat_info = os.stat(path)
                return {
                    'size': stat_info.st_size,
                    'mtime': stat_info.st_mtime,
                    'mode': oct(stat_info.st_mode),
                    'is_file': os.path.isfile(path),
                    'is_dir': os.path.isdir(path)
                }
            else:
                return {'error': f'Unsupported operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    async def handle_git_operations(self, params: Dict[str, Any], tool: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Git operations"""
        import subprocess
        operation = params['operation']
        repo_path = params.get('repo_path', '..')

        try:
            commands = {
                'status': ['git', 'status', '--porcelain'],
                'log': ['git', 'log', '--oneline', '-10'],
                'branch': ['git', 'branch', '-a'],
                'clone': ['git', 'clone', params.get('remote', ''), repo_path] if 'remote' in params else None,
            }

            if operation in commands and commands[operation]:
                result = subprocess.run(
                    commands[operation],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                return {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
            elif operation == 'commit':
                if 'message' not in params:
                    return {'error': 'Commit message required'}
                subprocess.run(['git', 'add', '.'], cwd=repo_path)
                result = subprocess.run(
                    ['git', 'commit', '-m', params['message']],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                return {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
            else:
                return {'error': f'Unsupported Git operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    async def handle_process_runner(self, params: Dict[str, Any], tool: Dict[str, Any]) -> Dict[str, Any]:
        """Handle advanced process execution"""
        import subprocess

        try:
            command = params['command']
            args = params.get('args', [])
            cwd = params.get('cwd', os.getcwd())
            env = params.get('env', os.environ.copy())
            timeout = params.get('timeout', 300)
            background = params.get('background', False)
            shell = params.get('shell', True)

            if shell:
                # Use shell=True and pass command as string
                full_command = command
                if args:
                    full_command += ' ' + ' '.join(args)
            else:
                # Use shell=False and pass command as list
                full_command = [command] + args

            if background:
                # Run in background
                process = subprocess.Popen(
                    full_command,
                    shell=shell,
                    cwd=cwd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                return {
                    'pid': process.pid,
                    'background': True,
                    'status': 'started'
                }
            else:
                # Run synchronously
                result = subprocess.run(
                    full_command,
                    shell=shell,
                    cwd=cwd,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                return {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode,
                    'background': False
                }
        except subprocess.TimeoutExpired:
            return {'error': 'Process timed out'}
        except Exception as e:
            return {'error': str(e)}

    async def handle_configurable_http(self, params: Dict[str, Any], tool: Dict[str, Any]) -> Dict[str, Any]:
        """Handle configurable HTTP tool"""
        config = tool['config']
        base_url = config.get('base_url', '')

        # Build full URL
        endpoint = params.get('endpoint', '')
        url = base_url + endpoint if endpoint.startswith('/') else base_url + '/' + endpoint

        # Set up request
        request_params = {
            'method': params.get('method', 'GET'),
            'url': url,
            'timeout': config.get('timeout', 30)
        }

        # Add headers from config and params
        headers = config.get('headers', {}).copy()
        if 'headers' in params:
            headers.update(params['headers'])
        if headers:
            request_params['headers'] = headers

        # Add authentication if configured
        auth = config.get('auth')
        if auth:
            if auth['type'] == 'bearer':
                headers['Authorization'] = f"Bearer {auth['token']}"
            elif auth['type'] == 'basic':
                import base64
                auth_string = base64.b64encode(f"{auth['username']}:{auth['password']}".encode()).decode()
                headers['Authorization'] = f"Basic {auth_string}"

        # Add body if provided
        if 'data' in params and params['method'] in ['POST', 'PUT', 'PATCH']:
            request_params['body'] = json.dumps(params['data'])
            headers['Content-Type'] = 'application/json'

        return await self.handle_http_request({**params, **request_params}, tool)

    async def handle_websocket(self, params: Dict[str, Any], tool: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WebSocket operations"""
        # WebSocket implementation would go here
        # For now, return placeholder
        return {'error': 'WebSocket tool not fully implemented'}

    async def handle_executable(self, params: Dict[str, Any], tool: Dict[str, Any]) -> Dict[str, Any]:
        """Handle external executable"""
        config = tool['config']
        executable = config.get('command', '')
        args = params.get('args', [])

        command = [executable] + args

        process_params = {
            'command': command[0],
            'args': command[1:],
            'shell': False,
            'timeout': config.get('timeout', 60)
        }

        return await self.handle_process_runner(process_params, tool)

    async def handle_web_search(self, params: Dict[str, Any], tool: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web search operations"""
        # Web search implementation would go here
        # For now, return placeholder
        return {'error': 'Web search tool not fully implemented'}

    async def handle_database_query(self, params: Dict[str, Any], tool: Dict[str, Any]) -> Dict[str, Any]:
        """Handle database operations"""
        # Database operations would go here
        # For now, return placeholder
        return {'error': 'Database tool not fully implemented'}

class SecurityManager:
    """Security sandboxing for command execution"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sandbox_enabled = config.get('security', {}).get('sandbox', True)
        self.allowed_commands = set(config.get('security', {}).get('allowed_commands', []))
        self.blocked_commands = set(config.get('security', {}).get('blocked_commands', []))

    def validate_command(self, command: str) -> bool:
        """Validate if a command is safe to execute"""
        if not self.sandbox_enabled:
            return True

        command_lower = command.lower().strip()

        # Check blocked commands
        for blocked in self.blocked_commands:
            if blocked.lower() in command_lower:
                return False

        # If whitelist is enabled, check against allowed commands
        if self.allowed_commands:
            command_parts = command_lower.split()
            base_command = command_parts[0] if command_parts else ""
            if base_command not in self.allowed_commands:
                return False

        return True

    def sanitize_path(self, path: str) -> str:
        """Sanitize file paths to prevent directory traversal"""
        path = os.path.normpath(path)
        if path.startswith('..') or path.startswith('/'):
            raise ValueError("Unsafe path detected")
        return path

    def validate_url(self, url: str) -> bool:
        """Validate URLs for safety"""
        if not url.startswith(('http://', 'https://')):
            return False

        # Additional URL validation logic could go here
        return True

class InteractiveShell:
    """Interactive shell mode for persistent terminal sessions"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.current_shell = None
        self.is_running = False
        self.cwd = os.getcwd()

    async def start_shell_session(self, shell_type: str = None) -> None:
        """Start an interactive shell session"""
        import pty
        import select
        import termios
        import tty

        if shell_type is None:
            shell_type = os.environ.get('SHELL', '/bin/bash')

        try:
            # Create PTY
            master_fd, slave_fd = pty.openpty()

            # Start shell process
            self.current_shell = subprocess.Popen(
                shell_type,
                preexec_fn=os.setsid,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                cwd=self.cwd
            )

            # Close slave FD in parent
            os.close(slave_fd)

            # Set terminal to raw mode
            old_tty = termios.tcgetattr(0)
            tty.setraw(0)

            self.is_running = True

            try:
                while self.is_running:
                    # Wait for input from either stdin or shell
                    rlist, _, _ = select.select([0, master_fd], [], [], 0.1)

                    if 0 in rlist:  # stdin has data
                        data = os.read(0, 1024)
                        if not data:  # EOF
                            break
                        os.write(master_fd, data)

                    if master_fd in rlist:  # shell has output
                        data = os.read(master_fd, 1024)
                        if not data:  # EOF
                            break
                        os.write(1, data)

            finally:
                # Restore terminal
                termios.tcsetattr(0, termios.TCSADRAIN, old_tty)

        except Exception as e:
            print(f"Shell session failed: {e}")
        finally:
            if self.current_shell:
                self.current_shell.terminate()
                try:
                    self.current_shell.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.current_shell.kill()
            self.is_running = False

    def stop_shell(self):
        """Stop the current shell session"""
        self.is_running = False
        if self.current_shell:
            self.current_shell.terminate()

    def change_directory(self, path: str):
        """Change shell working directory"""
        if os.path.isdir(path):
            self.cwd = os.path.abspath(path)

    async def run_command_in_shell(self, command: str) -> Dict[str, Any]:
        """Run a command in the current shell session"""
        if not self.current_shell:
            return {'error': 'No active shell session'}

        try:
            # Send command to shell
            if not command.endswith('\n'):
                command += '\n'

            # This is a simplified version - full implementation would need
            # proper PTY handling and output capture
            return {'error': 'Interactive command execution not fully implemented'}

        except Exception as e:
            return {'error': str(e)}
