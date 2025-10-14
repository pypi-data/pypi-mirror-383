#!/usr/bin/env python3
"""
Streaming response module for Cline Clone
Provides real-time streaming output for better user experience
"""

import asyncio
import aiohttp
import json
import time
import threading
import queue
import os
from typing import Callable, Optional, Dict, Any, List, AsyncGenerator
from concurrent.futures import ThreadPoolExecutor, as_completed


class StreamingAnalyzer:
    """Handles streaming responses from Ollama models"""

    def __init__(self, ollama_config: Dict[str, Any]):
        self.config = ollama_config
        self.is_streaming = False

    async def stream_chat_response(self, prompt: str, callback: Callable[[str], None]) -> Optional[str]:
        """
        Stream chat response with real-time output
        callback is called for each chunk of text received
        """
        try:
            self.is_streaming = True

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.get('timeout', 600))) as session:
                request_data = {
                    "model": self.config['name'],
                    "prompt": prompt,
                    "stream": True,  # Enable streaming
                    "options": {
                        "temperature": self.config.get('temperature', 0.7),
                        "num_predict": self.config.get('max_tokens', 4096)
                    }
                }

                full_response = ""
                chunk_count = 0

                async with session.post(
                    f"{self.config['base_url']}/api/generate",
                    json=request_data
                ) as response:
                    if response.status != 200:
                        error_msg = await response.text()
                        raise Exception(f"Streaming API error: {response.status} - {error_msg}")

                    async for line in response.content:
                        if not self.is_streaming:
                            break  # Allow interruption

                        line = line.decode('utf-8').strip()
                        if not line:
                            continue

                        try:
                            chunk = json.loads(line)
                            token = chunk.get('response', '')

                            if token:
                                full_response += token
                                chunk_count += 1

                                # Call callback with new token
                                if callback:
                                    callback(token)

                                # Small delay to prevent overwhelming output
                                if chunk_count % 10 == 0:  # Every 10 tokens
                                    await asyncio.sleep(0.01)

                        except json.JSONDecodeError:
                            continue

            return full_response

        except Exception as e:
            if callback:
                callback(f"\n[Error] Streaming failed: {e}\n")
            return None
        finally:
            self.is_streaming = False

    async def stream_edit_response(self, file_content: str, instruction: str, callback: Callable[[str], None]) -> Optional[str]:
        """
        Stream file editing suggestions with real-time output
        """
        try:
            prompt = f"""System: You are an expert software developer helping to edit code files. When you provide code, wrap it in ```language markdown blocks.

User: Here is a file I want you to edit:

File content:
```python
{file_content}
```

Instruction: {instruction}

Please provide the improved/modified version of this file.
Assistant:"""

            return await self.stream_chat_response(prompt, callback)

        except Exception as e:
            if callback:
                callback(f"\n[Error] Streaming edit failed: {e}\n")
            return None

    async def stream_analysis_response(self, codebase_summary: str, callback: Callable[[str], None]) -> Optional[str]:
        """
        Stream codebase analysis with real-time output
        """
        try:
            prompt = f"""System: You are a senior software engineer analyzing a codebase.

User: Please analyze this codebase and provide insights:

{codebase_summary}

Assistant:"""

            return await self.stream_chat_response(prompt, callback)

        except Exception as e:
            if callback:
                callback(f"\n[Error] Streaming analysis failed: {e}\n")
            return None

    def stop_streaming(self):
        """Stop any ongoing streaming operation"""
        self.is_streaming = False

    async def stream_with_interruptible_progress(self, prompt: str, callback: Callable[[str], None], show_progress: bool = True) -> Optional[str]:
        """
        Stream with progress indication and ability to interrupt
        """
        try:
            self.is_streaming = True

            if show_progress:
                progress_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
                progress_index = 0

                def progress_callback(token: str):
                    nonlocal progress_index
                    if show_progress and progress_index % 20 == 0:  # Show progress every 20 chars
                        indicator = progress_chars[(progress_index // 20) % len(progress_chars)]
                        print(f"\r{indicator} AI thinking...", end="", flush=True)
                    progress_index += len(token)
                    callback(token)

            else:
                progress_callback = callback

            result = await self.stream_chat_response(prompt, progress_callback)

            if show_progress:
                print("\r" + " " * 20 + "\r", end="", flush=True)  # Clear progress line

            return result

        except KeyboardInterrupt:
            self.stop_streaming()
            if callback:
                callback("\n[Interrupted by user]\n")
            return None
        finally:
            self.is_streaming = False


class StreamingCommandExecutor:
    """Handles streaming output for long-running commands with performance optimization"""

    def __init__(self):
        self.is_running = False

    async def stream_command_output(self, command: str, callback: Callable[[str], None],
                                   timeout: int = 300) -> tuple[int, str, str]:
        """
        Execute command and stream output in real-time
        Returns (exit_code, stdout, stderr)
        """
        import subprocess
        import asyncio
        import threading
        import select
        import fcntl

        stdout_content = []
        stderr_content = []

        def make_async(fd):
            """Make file descriptor asynchronous"""
            fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)

        def stream_output(pipe, callback, is_stdout=True):
            """Stream output from pipe with optimized buffering"""
            try:
                make_async(pipe.fileno())

                buffer = ""
                while self.is_running:
                    try:
                        # Non-blocking read
                        chunk = pipe.read(8192)
                        if not chunk:
                            break

                        chunk_str = chunk.decode('utf-8', errors='replace')
                        buffer += chunk_str

                        # Process complete lines
                        lines = buffer.split('\n')
                        buffer = lines.pop()  # Keep incomplete line in buffer

                        for line in lines:
                            line_str = line + '\n'

                            if is_stdout:
                                stdout_content.append(line_str)
                            else:
                                stderr_content.append(line_str)

                            if callback:
                                callback(line_str)

                    except (OSError, IOError):
                        # No data available, brief pause
                        time.sleep(0.01)
                        continue

                # Process remaining buffer
                if buffer and self.is_running:
                    buffer += '\n'
                    if is_stdout:
                        stdout_content.append(buffer)
                    else:
                        stderr_content.append(buffer)

                    if callback:
                        callback(buffer)

            except Exception as e:
                error_msg = f"\n[Streaming error: {e}]\n"
                if callback:
                    callback(error_msg)

        try:
            self.is_running = True

            # Start subprocess with optimized settings
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd(),
                bufsize=0,  # Unbuffered
                preexec_fn=os.setsid if os.name != 'nt' else None  # New process group
            )

            # Start streaming threads with higher priority
            stdout_thread = threading.Thread(
                target=stream_output,
                args=(process.stdout, callback, True),
                daemon=True
            )
            stderr_thread = threading.Thread(
                target=stream_output,
                args=(process.stderr, callback, False),
                daemon=True
            )

            stdout_thread.start()
            stderr_thread.start()

            # Monitor process with heartbeat
            start_time = time.time()
            last_output_time = time.time()

            try:
                while time.time() - start_time < timeout:
                    if process.poll() is not None:
                        # Process finished
                        break

                    # Send heartbeat every second if no output
                    current_time = time.time()
                    if current_time - last_output_time > 1.0:
                        last_output_time = current_time
                        await asyncio.sleep(0.1)  # Brief async pause

                    await asyncio.sleep(0.01)  # Small delay to prevent busy waiting

                exit_code = process.poll()

                if exit_code is None:
                    # Timeout reached
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                        exit_code = process.returncode or -1
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                        exit_code = -1

                # Wait for threads to finish processing remaining output
                await asyncio.sleep(0.1)  # Allow threads to finish

            except asyncio.TimeoutError:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

                return (-1, ''.join(stdout_content), ''.join(stderr_content) + "\n[Timeout]\n")

        except Exception as e:
            return (-1, "", f"[Error] Command execution failed: {e}")

        finally:
            self.is_running = False

        return (exit_code or 0, ''.join(stdout_content), ''.join(stderr_content))

    def stop_command(self):
        """Stop any running command"""
        self.is_running = False


class PerformanceOptimizer:
    """Optimizes streaming performance and resource usage"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection_pool_size = config.get('performance', {}).get('connection_pool_size', 10)
        self.max_concurrent_streams = config.get('performance', {}).get('max_concurrent_streams', 3)
        self.enable_caching = config.get('performance', {}).get('enable_caching', True)
        self.cache = {}
        self.cache_max_size = config.get('performance', {}).get('cache_max_size', 50)

    async def get_semaphore(self) -> asyncio.Semaphore:
        """Get semaphore for limiting concurrent streams"""
        if not hasattr(self, '_semaphore'):
            self._semaphore = asyncio.Semaphore(self.max_concurrent_streams)
        return self._semaphore

    def cached_request(self, key: str) -> Optional[str]:
        """Get cached response if available"""
        if not self.enable_caching:
            return None

        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < 3600:  # 1 hour cache
                return entry['response']

            # Remove expired entry
            del self.cache[key]

        return None

    def cache_response(self, key: str, response: str):
        """Cache response for future use"""
        if not self.enable_caching:
            return

        # Remove oldest entries if cache is full
        if len(self.cache) >= self.cache_max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]

        self.cache[key] = {
            'response': response,
            'timestamp': time.time()
        }

    async def create_optimized_session(self) -> aiohttp.ClientSession:
        """Create optimized aiohttp session"""
        connector = aiohttp.TCPConnector(
            limit=self.connection_pool_size,
            limit_per_host=self.connection_pool_size,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=60,
            enable_cleanup_closed=True,
        )

        return aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=self.config.get('timeout', 300)),
            headers={'Connection': 'keep-alive'}
        )
