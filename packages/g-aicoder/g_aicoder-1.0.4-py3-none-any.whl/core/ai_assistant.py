#!/usr/bin/env python3
"""
Core AI Assistant module for gCoder
Handles AI API calls, configuration, and conversation management
"""

import argparse
import asyncio
import json
import os
import sys
import aiohttp
import logging
import re
import subprocess
import shutil
import base64
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import datetime
import glob

from session_manager import SessionManager
from streaming_analyzer import StreamingAnalyzer
from image_analyzer import ImageAnalyzer


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
        # Use the selected provider's config for modules
        provider_config = self.config['providers'][self.config['ai_provider']]
        self.streaming_analyzer = StreamingAnalyzer(provider_config)
        self.image_analyzer = ImageAnalyzer(provider_config)

    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file with first-run setup"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

                # Check if first run and update model if needed
                if 'ai_provider' not in config:
                    print("🤖 Welcome to gCoder!")
                    print("It looks like this is your first time running gCoder.")
                    print("Let's set up your preferences.\n")

                    # Ask for permissions
                    print("📋 Permissions Setup:")
                    print("gCoder can perform file operations, run commands, and analyze your codebase.")
                    print("This includes reading, writing, and executing operations on your system.")
                    permission_granted = input("Do you grant gCoder permission to perform these operations? (y/N): ").lower().strip()
                    config['permissions'] = {'granted': permission_granted == 'y', 'asked': True}

                    # Ask for AI provider preference
                    print("\n🤖 AI Provider Setup:")
                    print("Available providers:")
                    
                    providers = list(config['providers'].keys())
                    for i, provider_id in enumerate(providers, 1):
                        provider = config['providers'][provider_id]
                        print(f"{i}. {provider['name']} ({provider['type']})")
                    
                    provider_choice = input(f"\nSelect provider (1-{len(providers)}, default: 1): ").strip()
                    
                    if provider_choice and provider_choice.isdigit():
                        selected_provider = providers[int(provider_choice) - 1]
                    else:
                        selected_provider = providers[0]
                    
                    config['ai_provider'] = selected_provider
                    provider_config = config['providers'][selected_provider]
                    
                    # Show available models for selected provider
                    print(f"\n🤖 {provider_config['name']} Model Setup:")
                    print("Available models:")
                    
                    for i, model in enumerate(provider_config['models'], 1):
                        print(f"{i}. {model['name']} - {model['description']}")
                    
                    model_choice = input(f"\nSelect model (1-{len(provider_config['models'])}, default: 1): ").strip()
                    
                    if model_choice and model_choice.isdigit():
                        selected_model = provider_config['models'][int(model_choice) - 1]['name']
                    else:
                        selected_model = provider_config['models'][0]['name']
                    
                    # Update the selected model in provider config
                    config['providers'][selected_provider]['selected_model'] = selected_model
                    
                    # If cloud provider, ask for API key
                    if provider_config['type'] == 'cloud':
                        print(f"\n🔑 {provider_config['name']} API Setup:")
                        api_key = input(f"Enter your {provider_config['name']} API key: ").strip()
                        if api_key:
                            config['providers'][selected_provider]['api_key'] = api_key
                            print(f"✅ {provider_config['name']} API configured!")
                        else:
                            print("⚠️ No API key provided. You'll need to add it later in config.json")
                    
                    # Save updated config
                    with open(config_path, 'w') as f:
                        json.dump(config, f, indent=2)

                    if config['permissions']['granted']:
                        print("✅ Setup complete! You can now use gCoder.")
                        provider_name = config['providers'][selected_provider]['name']
                        print(f"🌐 Using {provider_name} with model: {selected_model}")
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

            # Create default config structure
            default_config = {
                "ai_provider": "ollama",
                "providers": {
                    "ollama": {
                        "name": "Ollama (Local)",
                        "type": "local",
                        "base_url": "http://localhost:11434",
                        "models": [
                            {
                                "name": "qwen2.5-coder:7b",
                                "description": "Qwen2.5 Coder 7B - Recommended for coding"
                            },
                            {
                                "name": "codellama:7b",
                                "description": "Code Llama 7B - Meta's code-focused model"
                            },
                            {
                                "name": "deepseek-coder:6.7b",
                                "description": "DeepSeek Coder 6.7B - Lightweight coding assistant"
                            },
                            {
                                "name": "llava:7b",
                                "description": "LLaVA 7B - Vision-capable model"
                            }
                        ],
                        "selected_model": "qwen2.5-coder:7b",
                        "timeout": 600,
                        "temperature": 0.7,
                        "max_tokens": 4096
                    },
                    "openai": {
                        "name": "OpenAI",
                        "type": "cloud",
                        "base_url": "https://api.openai.com/v1",
                        "api_key": "",
                        "models": [
                            {
                                "name": "gpt-4",
                                "description": "GPT-4 - Most capable model"
                            },
                            {
                                "name": "gpt-3.5-turbo",
                                "description": "GPT-3.5 Turbo - Fast and cost-effective"
                            }
                        ],
                        "selected_model": "gpt-4",
                        "timeout": 60,
                        "temperature": 0.7,
                        "max_tokens": 4096
                    },
                    "anthropic": {
                        "name": "Anthropic",
                        "type": "cloud",
                        "base_url": "https://api.anthropic.com/v1",
                        "api_key": "",
                        "models": [
                            {
                                "name": "claude-3-sonnet-20240229",
                                "description": "Claude 3 Sonnet - Balanced performance"
                            },
                            {
                                "name": "claude-3-haiku-20240307",
                                "description": "Claude 3 Haiku - Fast and efficient"
                            }
                        ],
                        "selected_model": "claude-3-sonnet-20240229",
                        "timeout": 60,
                        "temperature": 0.7,
                        "max_tokens": 4096
                    },
                    "google": {
                        "name": "Google AI",
                        "type": "cloud",
                        "base_url": "https://generativelanguage.googleapis.com/v1",
                        "api_key": "",
                        "models": [
                            {
                                "name": "gemini-pro",
                                "description": "Gemini Pro - General purpose model"
                            }
                        ],
                        "selected_model": "gemini-pro",
                        "timeout": 60,
                        "temperature": 0.7,
                        "max_tokens": 4096
                    },
                    "deepseek": {
                        "name": "DeepSeek",
                        "type": "cloud",
                        "base_url": "https://api.deepseek.com/v1",
                        "api_key": "",
                        "models": [
                            {
                                "name": "deepseek-coder",
                                "description": "DeepSeek Coder - Specialized for coding"
                            }
                        ],
                        "selected_model": "deepseek-coder",
                        "timeout": 60,
                        "temperature": 0.7,
                        "max_tokens": 4096
                    }
                },
                "app": {
                    "name": "gCoder",
                    "version": "1.0.0"
                },
                "permissions": {
                    "granted": permission_granted == 'y',
                    "asked": True
                }
            }

            # Now run the setup process using the default config
            print("\n🤖 AI Provider Setup:")
            print("Available providers:")
            
            providers = list(default_config['providers'].keys())
            for i, provider_id in enumerate(providers, 1):
                provider = default_config['providers'][provider_id]
                print(f"{i}. {provider['name']} ({provider['type']})")
            
            provider_choice = input(f"\nSelect provider (1-{len(providers)}, default: 1): ").strip()
            
            if provider_choice and provider_choice.isdigit():
                selected_provider = providers[int(provider_choice) - 1]
            else:
                selected_provider = providers[0]
            
            default_config['ai_provider'] = selected_provider
            provider_config = default_config['providers'][selected_provider]
            
            # Show available models for selected provider
            print(f"\n🤖 {provider_config['name']} Model Setup:")
            print("Available models:")
            
            for i, model in enumerate(provider_config['models'], 1):
                print(f"{i}. {model['name']} - {model['description']}")
            
            model_choice = input(f"\nSelect model (1-{len(provider_config['models'])}, default: 1): ").strip()
            
            if model_choice and model_choice.isdigit():
                selected_model = provider_config['models'][int(model_choice) - 1]['name']
            else:
                selected_model = provider_config['models'][0]['name']
            
            # Update the selected model in provider config
            default_config['providers'][selected_provider]['selected_model'] = selected_model
            
            # If cloud provider, ask for API key
            if provider_config['type'] == 'cloud':
                print(f"\n🔑 {provider_config['name']} API Setup:")
                api_key = input(f"Enter your {provider_config['name']} API key: ").strip()
                if api_key:
                    default_config['providers'][selected_provider]['api_key'] = api_key
                    print(f"✅ {provider_config['name']} API configured!")
                else:
                    print("⚠️ No API key provided. You'll need to add it later in config.json")

            # Save the config
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)

            if default_config['permissions']['granted']:
                print("✅ Setup complete! You can now use gCoder.")
                provider_name = default_config['providers'][selected_provider]['name']
                print(f"🌐 Using {provider_name} with model: {selected_model}")
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
            provider = self.config['ai_provider']
            
            if provider == 'ollama':
                return await self.call_ollama_api(prompt)
            elif provider == 'openai':
                return await self.call_openai_api(prompt)
            elif provider == 'anthropic':
                return await self.call_anthropic_api(prompt)
            elif provider == 'google':
                return await self.call_google_api(prompt)
            elif provider == 'deepseek':
                return await self.call_deepseek_api(prompt)
            else:
                print(f"Unknown AI provider: {provider}")
                return None
        except Exception as e:
            print(f"Error calling AI API: {e}")
            return None

    async def call_ollama_api(self, prompt: str) -> Optional[str]:
        """Call Ollama API with proper error handling"""
        try:
            provider_config = self.config['providers']['ollama']
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=provider_config['timeout'])) as session:
                request_data = {
                    "model": provider_config['selected_model'],
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": provider_config['temperature'],
                        "num_predict": provider_config['max_tokens']
                    }
                }

                # Use configurable API endpoint
                api_endpoint = provider_config.get('api_endpoint', '/api/generate')
                async with session.post(
                    f"{provider_config['base_url']}{api_endpoint}",
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

    async def call_openai_api(self, prompt: str) -> Optional[str]:
        """Call OpenAI API with proper error handling"""
        try:
            provider_config = self.config['providers']['openai']
            headers = {
                "Authorization": f"Bearer {provider_config['api_key']}",
                "Content-Type": "application/json"
            }

            request_data = {
                "model": provider_config['selected_model'],
                "messages": [
                    {"role": "system", "content": "You are an expert software developer."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": provider_config['temperature'],
                "max_tokens": provider_config['max_tokens']
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=provider_config['timeout'])) as session:
                # Use configurable API endpoint
                api_endpoint = provider_config.get('api_endpoint', '/chat/completions')
                async with session.post(
                    f"{provider_config['base_url']}{api_endpoint}",
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

    async def call_anthropic_api(self, prompt: str) -> Optional[str]:
        """Call Anthropic API with proper error handling"""
        try:
            provider_config = self.config['providers']['anthropic']
            headers = {
                "x-api-key": provider_config['api_key'],
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }

            request_data = {
                "model": provider_config['selected_model'],
                "max_tokens": provider_config['max_tokens'],
                "temperature": provider_config['temperature'],
                "system": "You are an expert software developer.",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=provider_config['timeout'])) as session:
                # Use configurable API endpoint
                api_endpoint = provider_config.get('api_endpoint', '/messages')
                async with session.post(
                    f"{provider_config['base_url']}{api_endpoint}",
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

    async def call_google_api(self, prompt: str) -> Optional[str]:
        """Call Google AI API with proper error handling"""
        try:
            provider_config = self.config['providers']['google']
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
                    "temperature": provider_config['temperature'],
                    "maxOutputTokens": provider_config['max_tokens']
                }
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=provider_config['timeout'])) as session:
                # Use configurable API endpoint with model substitution
                api_endpoint = provider_config.get('api_endpoint', '/models/{model}:generateContent')
                api_endpoint = api_endpoint.replace('{model}', provider_config['selected_model'])
                full_url = f"{provider_config['base_url']}{api_endpoint}?key={provider_config['api_key']}"
                
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

    async def call_deepseek_api(self, prompt: str) -> Optional[str]:
        """Call DeepSeek API with proper error handling"""
        try:
            provider_config = self.config['providers']['deepseek']
            headers = {
                "Authorization": f"Bearer {provider_config['api_key']}",
                "Content-Type": "application/json"
            }

            request_data = {
                "model": provider_config['selected_model'],
                "messages": [
                    {"role": "system", "content": "You are an expert software developer."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": provider_config['temperature'],
                "max_tokens": provider_config['max_tokens']
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=provider_config['timeout'])) as session:
                # Use configurable API endpoint
                api_endpoint = provider_config.get('api_endpoint', '/chat/completions')
                async with session.post(
                    f"{provider_config['base_url']}{api_endpoint}",
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
            return await self.streaming_analyzer.stream_chat_response(prompt, print_callback)
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
