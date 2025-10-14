#!/usr/bin/env python3
"""
Core AI Assistant module for gCoder
Handles AI API calls, configuration, and conversation management
"""

import json
import aiohttp
import logging
import asyncio
import re
from pathlib import Path
from typing import Dict, Optional
import datetime

from utils.session_manager import SessionManager
from utils.streaming_analyzer import StreamingAnalyzer
from utils.image_analyzer import ImageAnalyzer
from core.permission_manager import PermissionManager


class AICodeAssistant:
    """Main AI assistant class handling core functionality"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            # Use default config location
            config_path = Path.home() / '.gcoder' / 'config.json'

        self.config = self.load_config(config_path)
        self.conversation_history = []
        self.setup_logging()

        # Initialize modules
        self.session_manager = SessionManager()
        self.permission_manager = PermissionManager()

        # Initialize permission manager based on config
        if self.config.get('permissions', {}).get('granted', False):
            self.permission_manager.grant_global_permission()

        # Use the selected model's config for modules
        model_config = self.config['models'][self.config['selected_model']]
        self.streaming_analyzer = StreamingAnalyzer(model_config)
        self.image_analyzer = ImageAnalyzer(model_config)

    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file with first-run setup"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

                # Check if first run and update model if needed
                if 'selected_model' not in config:
                    print("🤖 Welcome to g-aicoder!")
                    print("It looks like this is your first time running g-aicoder.")
                    print("Let's set up your preferences.\n")

                    # Ask for permissions
                    print("📋 Permissions Setup:")
                    print("g-aicoder can perform file operations, run commands, and analyze your codebase.")
                    print("This includes reading, writing, and executing operations on your system.")
                    permission_granted = input(
                        "Do you grant g-aicoder permission to perform these operations? (y/N): ").lower().strip()
                    config['permissions'] = {'granted': permission_granted == 'y', 'asked': True}

                    # Show available models
                    print("\n🤖 Model Setup:")
                    print("Available models:")

                    models = list(config['models'].keys())
                    for i, model_id in enumerate(models, 1):
                        model = config['models'][model_id]
                        print(f"{i}. {model['name']} - {model['description']} ({model['provider']})")

                    model_choice = input(f"\nSelect model (1-{len(models)}, default: 1): ").strip()

                    if model_choice and model_choice.isdigit():
                        selected_model = models[int(model_choice) - 1]
                    else:
                        selected_model = models[0]

                    config['selected_model'] = selected_model

                    # If cloud provider, ask for API key
                    model_config = config['models'][selected_model]
                    if model_config['type'] == 'cloud' and not model_config.get('api_key'):
                        print(f"\n🔑 {model_config['provider']} API Setup:")
                        api_key = input(f"Enter your {model_config['provider']} API key: ").strip()
                        if api_key:
                            config['models'][selected_model]['api_key'] = api_key
                            print(f"✅ {model_config['provider']} API configured!")
                        else:
                            print("⚠️ No API key provided. You'll need to add it later in config.json")

                    # Save updated config
                    with open(config_path, 'w') as f:
                        json.dump(config, f, indent=2)

                    if config['permissions']['granted']:
                        print("✅ Setup complete! You can now use g-aicoder.")
                        print(f"🌐 Using {model_config['name']} from {model_config['provider']}")
                    else:
                        print("⚠️ Warning: Some features may be limited without permissions.")

                return config

        except FileNotFoundError:
            # First run - create config and ask for setup
            print("🚀 First time setup for gCoder!")
            print("Let's configure your development environment.\n")

            # Ask for permissions
            print("📋 Permissions Setup:")
            print("gCoder can perform file operations, run commands, and analyze your codebase.")
            print("This includes reading, writing, and executing operations on your system.")
            permission_granted = input(
                "Do you grant gCoder permission to perform these operations? (y/N): ").lower().strip()

            # Create default config structure with new model-based format
            default_config = {
                "default_mode": "ollama",
                "models": {
                    "qwen2.5-coder:7b": {
                        "name": "qwen2.5-coder:7b",
                        "description": "Qwen2.5 Coder 7B - Recommended for coding",
                        "provider": "ollama",
                        "type": "local",
                        "base_url": "http://localhost:11434",
                        "api_endpoint": "/api/generate",
                        "timeout": 600,
                        "temperature": 0.7,
                        "max_tokens": 4096
                    },
                    "openai-gpt-4": {
                        "name": "gpt-4",
                        "description": "GPT-4 - Most capable model",
                        "provider": "openai",
                        "type": "cloud",
                        "base_url": "https://api.openai.com/v1",
                        "api_endpoint": "/chat/completions",
                        "api_key": "",
                        "timeout": 60,
                        "temperature": 0.7,
                        "max_tokens": 4096
                    },
                    "openai-gpt-3.5-turbo": {
                        "name": "gpt-3.5-turbo",
                        "description": "GPT-3.5 Turbo - Fast and cost-effective",
                        "provider": "openai",
                        "type": "cloud",
                        "base_url": "https://api.openai.com/v1",
                        "api_endpoint": "/chat/completions",
                        "api_key": "",
                        "timeout": 60,
                        "temperature": 0.7,
                        "max_tokens": 4096
                    },
                    "anthropic-claude-3-sonnet-20240229": {
                        "name": "claude-3-sonnet-20240229",
                        "description": "Claude 3 Sonnet - Balanced performance",
                        "provider": "anthropic",
                        "type": "cloud",
                        "base_url": "https://api.anthropic.com/v1",
                        "api_endpoint": "/messages",
                        "api_key": "",
                        "timeout": 60,
                        "temperature": 0.7,
                        "max_tokens": 4096
                    },

                    "google-gemini-pro": {
                        "name": "gemini-pro",
                        "description": "Gemini Pro - General purpose model",
                        "provider": "google",
                        "type": "cloud",
                        "base_url": "https://generativelanguage.googleapis.com/v1",
                        "api_endpoint": "/models/{model}:generateContent",
                        "api_key": "",
                        "timeout": 60,
                        "temperature": 0.7,
                        "max_tokens": 4096
                    },
                    "deepseek-deepseek-coder": {
                        "name": "deepseek-coder",
                        "description": "DeepSeek Coder - Specialized for coding",
                        "provider": "deepseek",
                        "type": "cloud",
                        "base_url": "https://api.deepseek.com/v1",
                        "api_endpoint": "/chat/completions",
                        "api_key": "",
                        "timeout": 60,
                        "temperature": 0.7,
                        "max_tokens": 4096
                    }
                },
                "app": {
                    "name": "g-aicoder",
                    "version": "1.0.5"
                },
                "permissions": {
                    "granted": permission_granted == 'y',
                    "asked": True
                },
                "selected_model": "ollama-qwen2.5-coder:7b"
            }

            # Now run the setup process using the new model-based config
            print("\n🤖 Model Setup:")
            print("Available models:")

            models = list(default_config['models'].keys())
            for i, model_id in enumerate(models, 1):
                model = default_config['models'][model_id]
                print(f"{i}. {model['name']} - {model['description']} ({model['provider']})")

            model_choice = input(f"\nSelect model (1-{len(models)}, default: 1): ").strip()

            if model_choice and model_choice.isdigit():
                selected_model = models[int(model_choice) - 1]
            else:
                selected_model = models[0]

            default_config['selected_model'] = selected_model
            model_config = default_config['models'][selected_model]

            # If cloud provider, ask for API key
            if model_config['type'] == 'cloud' and not model_config.get('api_key'):
                print(f"\n🔑 {model_config['provider']} API Setup:")
                api_key = input(f"Enter your {model_config['provider']} API key: ").strip()
                if api_key:
                    default_config['models'][selected_model]['api_key'] = api_key
                    print(f"✅ {model_config['provider']} API configured!")
                else:
                    print("⚠️ No API key provided. You'll need to add it later in config.json")

            # Save the config
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)

            if default_config['permissions']['granted']:
                print("✅ Setup complete! You can now use g-aicoder.")
                print(f"🌐 Using {model_config['name']} from {model_config['provider']}")
            else:
                print("⚠️ Warning: Some features may be limited without permissions.")

            return default_config

    def setup_logging(self):
        """Setup minimal logging"""
        self.logger = logging.getLogger('gcoder')
        self.logger.setLevel(logging.WARNING)

    async def call_ai_api(self, prompt: str) -> Optional[str]:
        """Call AI API with proper error handling for multiple providers"""
        try:
            model_config = self.config['models'][self.config['selected_model']]
            provider = model_config['provider']

            if provider == 'ollama':
                return await self.call_ollama_api(prompt, model_config)
            elif provider == 'openai':
                return await self.call_openai_api(prompt, model_config)
            elif provider == 'anthropic':
                return await self.call_anthropic_api(prompt, model_config)
            elif provider == 'google':
                return await self.call_google_api(prompt, model_config)
            elif provider == 'deepseek':
                return await self.call_deepseek_api(prompt, model_config)
            else:
                print(f"Unknown AI provider: {provider}")
                return None
        except Exception as e:
            print(f"Error calling AI API: {e}")
            return None

    async def call_ollama_api(self, prompt: str, model_config: Dict) -> Optional[str]:
        """Call Ollama API with proper error handling"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=model_config['timeout'])) as session:
                request_data = {
                    "model": model_config['name'],
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": model_config['temperature'],
                        "num_predict": model_config['max_tokens']
                    }
                }

                # Use configurable API endpoint
                api_endpoint = model_config.get('api_endpoint', '/api/generate')
                async with session.post(
                        f"{model_config['base_url']}{api_endpoint}",
                        json=request_data
                ) as response:
                    if response.status != 200:
                        error_msg = await response.text()
                        raise Exception(f"Ollama API error: {response.status} - {error_msg}")

                    result = await response.json()
                    return result.get('response', '').strip()

        except aiohttp.ClientError as e:
            print(f"Network error: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    async def call_openai_api(self, prompt: str, model_config: Dict) -> Optional[str]:
        """Call OpenAI API with proper error handling"""
        try:
            headers = {
                "Authorization": f"Bearer {model_config['api_key']}",
                "Content-Type": "application/json"
            }

            request_data = {
                "model": model_config['name'],
                "messages": [
                    {"role": "system", "content": "You are an expert software developer."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": model_config['temperature'],
                "max_tokens": model_config['max_tokens']
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=model_config['timeout'])) as session:
                # Use configurable API endpoint
                api_endpoint = model_config.get('api_endpoint', '/chat/completions')
                async with session.post(
                        f"{model_config['base_url']}{api_endpoint}",
                        headers=headers,
                        json=request_data
                ) as response:
                    if response.status != 200:
                        error_msg = await response.text()
                        raise Exception(f"OpenAI API error: {response.status} - {error_msg}")

                    result = await response.json()
                    return result['choices'][0]['message']['content'].strip()

        except aiohttp.ClientError as e:
            print(f"Network error: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    async def call_anthropic_api(self, prompt: str, model_config: Dict) -> Optional[str]:
        """Call Anthropic API with proper error handling"""
        try:
            headers = {
                "x-api-key": model_config['api_key'],
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }

            request_data = {
                "model": model_config['name'],
                "max_tokens": model_config['max_tokens'],
                "temperature": model_config['temperature'],
                "system": "You are an expert software developer.",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=model_config['timeout'])) as session:
                # Use configurable API endpoint
                api_endpoint = model_config.get('api_endpoint', '/messages')
                async with session.post(
                        f"{model_config['base_url']}{api_endpoint}",
                        headers=headers,
                        json=request_data
                ) as response:
                    if response.status != 200:
                        error_msg = await response.text()
                        raise Exception(f"Anthropic API error: {response.status} - {error_msg}")

                    result = await response.json()
                    return result['content'][0]['text'].strip()

        except aiohttp.ClientError as e:
            print(f"Network error: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    async def call_google_api(self, prompt: str, model_config: Dict) -> Optional[str]:
        """Call Google AI API with proper error handling"""
        try:
            headers = {
                "Content-Type": "application/json"
            }

            request_data = {
                "contents": [
                    {
                        "parts": [
                            {"text": "You are an expert software developer."},
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": model_config['temperature'],
                    "maxOutputTokens": model_config['max_tokens']
                }
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=model_config['timeout'])) as session:
                # Use configurable API endpoint with model substitution
                api_endpoint = model_config.get('api_endpoint', '/models/{model}:generateContent')
                api_endpoint = api_endpoint.replace('{model}', model_config['name'])
                full_url = f"{model_config['base_url']}{api_endpoint}?key={model_config['api_key']}"

                async with session.post(
                        full_url,
                        headers=headers,
                        json=request_data
                ) as response:
                    if response.status != 200:
                        error_msg = await response.text()
                        raise Exception(f"Google AI API error: {response.status} - {error_msg}")

                    result = await response.json()
                    return result['candidates'][0]['content']['parts'][0]['text'].strip()

        except aiohttp.ClientError as e:
            print(f"Network error: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    async def call_deepseek_api(self, prompt: str, model_config: Dict) -> Optional[str]:
        """Call DeepSeek API with proper error handling"""
        try:
            headers = {
                "Authorization": f"Bearer {model_config['api_key']}",
                "Content-Type": "application/json"
            }

            request_data = {
                "model": model_config['name'],
                "messages": [
                    {"role": "system", "content": "You are an expert software developer."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": model_config['temperature'],
                "max_tokens": model_config['max_tokens']
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=model_config['timeout'])) as session:
                # Use configurable API endpoint
                api_endpoint = model_config.get('api_endpoint', '/chat/completions')
                async with session.post(
                        f"{model_config['base_url']}{api_endpoint}",
                        headers=headers,
                        json=request_data
                ) as response:
                    if response.status != 200:
                        error_msg = await response.text()
                        raise Exception(f"DeepSeek API error: {response.status} - {error_msg}")

                    result = await response.json()
                    return result['choices'][0]['message']['content'].strip()

        except aiohttp.ClientError as e:
            print(f"Network error: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def format_prompt(self, user_input: str) -> str:
        """Format prompt with system context for coding tasks"""
        system_prompt = """You are an expert software developer. You can:
                                - Write and modify code
                                - Execute terminal commands
                                - Analyze and improve existing code
                                - Help with development workflows
                                - Provide technical guidance
                                - Always return code with file name at top within comment.
                                You are helping with coding tasks. Be helpful, provide detailed explanations, and focus on practical solutions."""

        if not self.conversation_history:
            return f"System: {system_prompt}\n\nUser: {user_input}\n\nAssistant:"
        else:
            # Combine conversation history for context
            history_text = "\n".join([
                f"User: {msg['user']}\nAssistant: {msg['assistant']}"
                for msg in self.conversation_history[-3:]  # Keep last 3 exchanges
            ])
            return f"System: {system_prompt}\n\n{history_text}\nUser: {user_input}\n\nAssistant:"

    async def stream_response(self, prompt: str, show_thinking: bool = True) -> Optional[str]:
        """Stream AI response with Claude Code-style display, thinking animation (only for text queries), and automatic file operations"""

        def print_callback(token: str):
            print(token, end="", flush=True)

        try:
            model_config = self.config['models'][self.config['selected_model']]
            provider = model_config['provider']

            full_response = ""

            # Show thinking animation only for text queries (not for file operations, commands, etc.)
            thinking_task = None
            if show_thinking:
                print("🤔 Thinking... ", end="", flush=True)
                thinking_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
                thinking_task = asyncio.create_task(self.show_thinking_animation(thinking_chars))

            try:
                if provider == 'ollama':
                    full_response = await self.streaming_analyzer.stream_chat_response(prompt, print_callback)
                else:
                    # For non-Ollama models, use regular API call with simulated streaming
                    response = await self.call_ai_api(prompt)
                    if response:
                        full_response = response
                        # Format response with Claude Code-style display
                        formatted_response = self.format_claude_code_response(response)
                        print(formatted_response)

                # After getting the full response, check if it contains file operations
                if full_response:
                    await self.execute_file_operations_from_response(full_response)

                return full_response
            finally:
                # Stop thinking animation if it was started
                if thinking_task:
                    thinking_task.cancel()
                    try:
                        await thinking_task
                    except asyncio.CancelledError:
                        pass
                    print("\r" + " " * 50 + "\r", end="", flush=True)  # Clear the thinking line

        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def format_claude_code_response(self, response: str) -> str:
        """Format AI response with Claude Code-style display"""
        lines = response.split('\n')
        formatted_lines = []

        for line in lines:
            # Skip empty lines at the beginning
            if not formatted_lines and not line.strip():
                continue

            # Handle code blocks
            if line.strip().startswith('```'):
                if line.strip() == '```':
                    formatted_lines.append("```")
                else:
                    # Extract language from code block
                    lang = line.strip()[3:].strip()
                    formatted_lines.append(f"```{lang}")
            else:
                formatted_lines.append(line)

        # Join with proper spacing
        formatted_response = '\n'.join(formatted_lines)

        # Add Claude Code-style header
        header = "🤖 Assistant:\n"
        separator = "─" * 60 + "\n"

        return header + separator + formatted_response + "\n"

    async def show_thinking_animation(self, chars: list):
        """Show a thinking animation while processing"""
        i = 0
        while True:
            print(f"\r[AI] Thinking... {chars[i % len(chars)]}", end="", flush=True)
            await asyncio.sleep(0.1)
            i += 1

    async def execute_file_operations_from_response(self, response: str):
        """Parse AI response and automatically execute file operations with proper directory handling"""
        try:
            # Look for file paths in the lines immediately before code blocks
            lines = response.split('\n')
            total_matches = 0

            for i, line in enumerate(lines):
                # Skip lines that contain HTML attributes (href, src) to avoid false positives
                if any(attr in line for attr in ['href=', 'src=', 'link rel=', 'script src=']):
                    continue

                # Look for file path patterns in the current line - improved to extract only the file path
                file_path_pattern = r'([^/\s][^`\n]*?\.(?:py|js|ts|java|c|cpp|cs|php|rb|go|rs|txt|md|html|css|json|xml|yaml|yml))'
                file_match = re.search(file_path_pattern, line, re.IGNORECASE)

                if file_match:
                    # Extract just the file path part, not the entire matched text
                    file_path = self.extract_file_path_only(line)

                    # Skip if the extracted path contains HTML attributes or quotes
                    if any(char in file_path for char in ['=', "'", '"', 'href', 'src']):
                        continue

                    # Look for the next code block after this line
                    for j in range(i + 1, min(i + 5, len(lines))):  # Check next 5 lines
                        if lines[j].strip().startswith('```'):
                            # Found a code block, extract content
                            code_start = j
                            code_end = code_start
                            for k in range(code_start + 1, len(lines)):
                                if lines[k].strip() == '```':
                                    code_end = k
                                    break

                            if code_end > code_start:
                                # Extract code content
                                code_content = '\n'.join(lines[code_start + 1:code_end])
                                if code_content.strip():
                                    total_matches += 1
                                    print(f"\n[AI ACTION] Detected file creation: {file_path}")
                                    await self.create_file_from_ai_response(file_path.strip(), code_content.strip())
                                    break  # Move to next file path

        except Exception as e:
            print(f"[Error executing file operations: {e}]")

    def clean_file_path(self, file_path: str) -> str:
        """Clean file path while preserving directory structure"""
        # Remove common prefixes and clean up the path
        cleaned = file_path.strip()

        # Remove common prefixes like "file called", "create", etc.
        prefixes_to_remove = [
            r'^file\s+called\s+',
            r'^create\s+',
            r'^make\s+',
            r'^write\s+',
            r'^a\s+',
            r'^the\s+',
            r'^I\'ll\s+',
            r'^I will\s+',
            r'^Let me\s+',
            r'^I\'m going to\s+'
        ]

        for prefix in prefixes_to_remove:
            cleaned = re.sub(prefix, '', cleaned, flags=re.IGNORECASE)

        # Remove quotes
        cleaned = cleaned.replace('"', '').replace("'", "")

        # Remove trailing punctuation and whitespace
        cleaned = re.sub(r'[.,;:!?]\s*$', '', cleaned)

        return cleaned.strip()

    def extract_file_path_only(self, file_path: str) -> str:
        """Extract just the file path from potentially messy text, preserving directory structure"""
        # Sort extensions by length (longest first) to avoid matching shorter extensions first
        file_extensions = sorted([
            '.py', '.js', '.ts', '.java', '.c', '.cpp', '.cs', '.php', '.rb', '.go', '.rs',
            '.txt', '.md', '.html', '.css', '.json', '.xml', '.yaml', '.yml'
        ], key=len, reverse=True)

        for ext in file_extensions:
            if ext in file_path:
                # Find the position of the extension
                ext_pos = file_path.find(ext)
                if ext_pos != -1:
                    # Extract from the beginning of the file path
                    # Look backwards to find the start of the file path
                    start_pos = 0
                    for i in range(ext_pos - 1, -1, -1):
                        if file_path[i] in [' ', ':', '\n', '\t']:
                            start_pos = i + 1
                            break

                    # Extract the file path including the extension
                    extracted = file_path[start_pos:ext_pos + len(ext)]
                    return extracted

        # If no file extension found, use the cleaning method
        return self.clean_file_path(file_path)

    def extract_filename(self, file_path: str) -> str:
        """Extract just the filename from potentially messy text"""
        # Look for patterns like "simple Python file called test_auto.py"
        # Extract just the filename part
        filename_pattern = r'([^/\s]+\.(?:py|js|ts|java|c|cpp|cs|php|rb|go|rs|txt|md|html|css|json|xml|yaml|yml))'
        match = re.search(filename_pattern, file_path)
        if match:
            return match.group(1)
        return file_path

    async def create_file_from_ai_response(self, file_path: str, content: str):
        """Create a file based on AI response content"""
        try:
            from handlers.request_handlers import RequestHandlers
            handlers = RequestHandlers(self)

            # Check if permission is already granted
            if not self.permission_manager.has_permission("create_file"):
                # Ask for permission
                if not self.permission_manager.ask_permission("create_file"):
                    print("[AI ACTION] File creation cancelled by user.")
                    return

            full_path = Path(file_path)
            if full_path.exists():
                print(f"[AI ACTION] File already exists: {file_path}")
                overwrite = input("Overwrite? (y/N): ").lower().strip()
                if overwrite != 'y':
                    return

            # Create directory if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the content to file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"[AI ACTION] File created: {file_path}")
            print(f"[AI ACTION] File size: {len(content)} characters")

            # Show preview
            preview_lines = content.split('\n')[:5]
            print("[AI ACTION] Preview:")
            for i, line in enumerate(preview_lines, 1):
                print(f"  {i}: {line}")
            if len(content.split('\n')) > 5:
                remaining_lines = len(content.split('\n')) - 5
                print(f"  ... and {remaining_lines} more lines")

        except Exception as e:
            print(f"[AI ACTION] Error creating file: {e}")

    async def show_conversation_history(self):
        """Show recent conversation history"""
        history = self.session_manager.get_conversation_history(10)
        if not history:
            print("No conversation history available.")
            return

        print("📜 Recent conversation history:")
        for i, entry in enumerate(history[-10:], 1):  # Show last 10
            time = datetime.datetime.fromisoformat(entry['timestamp']).strftime('%H:%M')
            print(f"{i:2d}. [{time}] You: {entry['user'][:50]}{'...' if len(entry['user']) > 50 else ''}")
            print(f"     AI: {entry['assistant'][:50]}{'...' if len(entry['assistant']) > 50 else ''}")
            print()
