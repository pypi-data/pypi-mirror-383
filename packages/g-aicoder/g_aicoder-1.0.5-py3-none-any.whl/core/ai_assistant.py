#!/usr/bin/env python3
"""
Core AI Assistant module for gCoder
Handles AI API calls, configuration, and conversation management
"""

import json
import aiohttp
import logging
import asyncio
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
                    permission_granted = input("Do you grant g-aicoder permission to perform these operations? (y/N): ").lower().strip()
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
            permission_granted = input("Do you grant gCoder permission to perform these operations? (y/N): ").lower().strip()

            # Create default config structure with new model-based format
            default_config = {
                "default_mode": "ollama",
                "models": {
                    "ollama-qwen2.5-coder:7b": {
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
                    "ollama-codellama:7b": {
                        "name": "codellama:7b",
                        "description": "Code Llama 7B - Meta's code-focused model",
                        "provider": "ollama",
                        "type": "local",
                        "base_url": "http://localhost:11434",
                        "api_endpoint": "/api/generate",
                        "timeout": 600,
                        "temperature": 0.7,
                        "max_tokens": 4096
                    },
                    "ollama-deepseek-coder:6.7b": {
                        "name": "deepseek-coder:6.7b",
                        "description": "DeepSeek Coder 6.7B - Lightweight coding assistant",
                        "provider": "ollama",
                        "type": "local",
                        "base_url": "http://localhost:11434",
                        "api_endpoint": "/api/generate",
                        "timeout": 600,
                        "temperature": 0.7,
                        "max_tokens": 4096
                    },
                    "ollama-llava:7b": {
                        "name": "llava:7b",
                        "description": "LLaVA 7B - Vision-capable model",
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
                    "anthropic-claude-3-haiku-20240307": {
                        "name": "claude-3-haiku-20240307",
                        "description": "Claude 3 Haiku - Fast and efficient",
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

    async def stream_response(self, prompt: str) -> Optional[str]:
        """Stream AI response with real-time output"""
        def print_callback(token: str):
            print(token, end="", flush=True)

        try:
            model_config = self.config['models'][self.config['selected_model']]
            provider = model_config['provider']
            
            # Only use streaming for Ollama models
            if provider == 'ollama':
                return await self.streaming_analyzer.stream_chat_response(prompt, print_callback)
            else:
                # For non-Ollama models, use regular API call with simulated streaming
                response = await self.call_ai_api(prompt)
                if response:
                    # Simulate streaming by printing character by character
                    for char in response:
                        print(char, end="", flush=True)
                        await asyncio.sleep(0.01)  # Small delay for streaming effect
                    print()  # New line at the end
                return response
        except Exception as e:
            print(f"[Streaming error: {e}]")
            return None

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
