#!/usr/bin/env python3
"""
Chat and session management module for gCoder
Handles interactive chat sessions, session commands, and user interaction
"""

import asyncio
import re
import datetime
from typing import Dict, Optional, List, Tuple


class ChatManager:
    """Manages chat sessions, user interaction, and session commands"""
    
    def __init__(self, assistant, request_handlers):
        self.assistant = assistant
        self.request_handlers = request_handlers

    def display_ganesha_banner(self):
        """Display the Ganesha banner"""
        banner = """
       ______________________________________________________________________
       |                       OM SHREE GANESHAYA NAMA                      |
       |         MANGALAM BHAGAWAN VISHNU MANGALAM GARUDADHWAJA             |
       |           MANGALAM PUNDARIKAKSHA MANGALAYA TANO HARI               |
       ----------------------------------------------------------------------
       """
        print(banner)

    async def chat_session(self, streaming: bool = True):
        """Start interactive chat session with Cline-like tool use capabilities"""
        self.display_ganesha_banner()
        print(f"\n{self.assistant.config['app']['name']} v{self.assistant.config['app']['version']}")
        
        # List available models on startup (Task 1)
        print("[AI] Available models:")
        models = list(self.assistant.config['models'].keys())
        for i, model_id in enumerate(models, 1):
            model = self.assistant.config['models'][model_id]
            current = " (current)" if model_id == self.assistant.config['selected_model'] else ""
            print(f"  {i}. {model['name']} - {model['description']} ({model['provider']}){current}")
        
        # Show current model info
        model_config = self.assistant.config['models'][self.assistant.config['selected_model']]
        print(f"\nUsing {model_config['name']} from {model_config['provider']}")
        if model_config['provider'] == 'ollama':
            print("Make sure Ollama is running: 'ollama serve'")
        print("You can now work naturally - mention files, run commands, edit code directly!")
        print("Type 'exit' to quit, 'help' for commands\n")

        # Load existing conversation history if available
        if self.assistant.session_manager:
            history = self.assistant.session_manager.get_conversation_history(10)
            if history:
                print(f"[INFO] Loaded {len(history)} previous conversation entries from session '{self.assistant.session_manager.current_session['id']}'\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input or user_input.lower() in ['exit', 'quit', 'bye']:
                    # Save session before exiting
                    if self.assistant.session_manager:
                        self.assistant.session_manager.save_session()
                        print("\n[Session saved]")
                    break

                # Handle "/" commands (Task 4)
                if user_input.startswith('/'):
                    await self.handle_slash_command(user_input)
                    continue

                # Handle explicit commands (for backwards compatibility)
                if user_input.lower() == 'help':
                    print("\nUsage:")
                    print("Just type naturally and I'll understand:")
                    print("• 'read main.py'           - Read a file")
                    print("• 'edit app.py to add...'  - Edit code")
                    print("• 'run ls -la'            - Execute commands")
                    print("• 'search function.*name'  - Find patterns")
                    print("• 'analyze .'             - Analyze codebase")
                    print("• 'image screenshot.png'   - Analyze images")
                    print("• 'session save myproj'    - Session commands")
                    print("\nSlash Commands:")
                    print("• '/help'                  - Show this help")
                    print("• '/models'                - List available models")
                    print("• '/switch <model>'        - Switch to different model")
                    print("• '/clear'                 - Clear conversation history")
                    print("• '/exit'                  - Exit the application")
                    print()
                    continue

                elif user_input.startswith('session '):
                    await self.handle_session_command(user_input)
                    continue

                # Enhanced natural language processing with tool calling
                await self.process_user_request(user_input, streaming)

            except KeyboardInterrupt:
                # Save session before exiting
                if self.assistant.session_manager:
                    self.assistant.session_manager.save_session()
                    print("\n[Session saved]")
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}\n")

    async def process_user_request(self, user_input: str, streaming: bool = True):
        """Process natural language requests and execute appropriate tools with advanced pattern matching"""
        try:
            # Enhanced tool patterns for complex, longer inputs
            tool_patterns = [
                # Complex file reading patterns
                (
                    r'(?:read|show|display|view|open|examine)\s+(?:the\s+)?(?:content\s+of\s+)?(?:the\s+)?(?:file\s+)?(?:called\s+)?["\']?([^"\']+\.(?:py|js|ts|java|c|cpp|cs|php|rb|go|rs|txt|md|html|css|json|xml|yaml|yml))["\']?',
                    self.request_handlers.handle_read_file_request),

                # Complex file editing patterns with longer instructions
                (
                    r'(?:edit|modify|update|change|improve|fix|refactor)\s+(?:the\s+)?(?:file\s+)?(?:called\s+)?["\']?([^"\']+\.(?:py|js|ts|java|c|cpp|cs|php|rb|go|rs|txt|md|html|css|json|xml|yaml|yml))["\']?\s+(?:to\s+|and\s+|by\s+)?(.+?)(?=\s*$)',
                    self.request_handlers.handle_edit_file_request),

                # Command execution with complex commands
                (r'(?:run|execute|call|invoke|start|launch)\s+(?:the\s+)?(?:command\s+)?["\']?(.+?)["\']?(?:\s|$)',
                 self.request_handlers.handle_run_command_request),

                # Advanced search patterns
                (
                    r'(?:search|find|grep|look\s+for)\s+(?:for\s+)?["\']?(.+?)["\']?(?:\s+in\s+(?:the\s+)?(?:file\s+)?["\']?([^"\']+)["\']?)?(?:\s|$)',
                    self.request_handlers.handle_search_request),

                # Directory listing with complex paths
                (
                    r'(?:list|show|display|explore)\s+(?:the\s+)?(?:contents?\s+of\s+)?(?:the\s+)?(?:directory|folder|dir)\s+(?:called\s+)?["\']?([^"\']+)["\']?',
                    self.request_handlers.handle_list_directory_request),

                # File creation with content
                (
                    r'(?:create|make|new|generate)\s+(?:a\s+)?(?:file\s+)?(?:called\s+)?["\']?([^"\']+\.(?:py|js|ts|java|c|cpp|cs|php|rb|go|rs|txt|md|html|css|json|xml|yaml|yml))["\']?(?:\s+with\s+content\s+["\']?(.+?)["\']?)?(?:\s|$)',
                    self.request_handlers.handle_create_file_request),

                # Codebase analysis patterns
                (
                    r'(?:analyze|examine|review|study|investigate)\s+(?:the\s+)?(?:codebase|project|code|source|repository)(?:\s+in\s+(?:the\s+)?(?:directory|folder|path)\s+["\']?([^"\']+)["\']?)?(?:\s|$)',
                    self.request_handlers.handle_analyze_request),

                # Image analysis patterns
                (
                    r'(?:analyze|examine|look\s+at|check|review)\s+(?:the\s+)?(?:image|picture|photo|screenshot|diagram)\s+(?:file\s+)?["\']?([^"\']+\.(?:png|jpg|jpeg|gif|bmp|webp|tiff))["\']?',
                    self.request_handlers.handle_image_request),

                # Compound requests (multiple actions)
                (r'(?:please\s+)?(?:first|then|after\s+that|next)\s+(.+?)(?:\s*,?\s*(?:then|and|after)\s+(.+?))*(?:\s*$)',
                 self.request_handlers.handle_compound_request),

                # Help and information requests
                (r'(?:help|what\s+can\s+you\s+do|show\s+me\s+your\s+capabilities|list\s+commands)',
                 self.request_handlers.handle_help_request),
            ]

            # Try to match against enhanced tool patterns
            for pattern, handler in tool_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE | re.DOTALL)
                if match:
                    try:
                        await handler(match, streaming)
                        return
                    except Exception as e:
                        print(f"Error executing tool: {e}")
                        continue  # Try next pattern instead of breaking

            # If no tool pattern matched, fall back to regular chat
            prompt = self.assistant.format_prompt(user_input)

            if streaming:
                # Show thinking animation only for text queries (not for tool operations)
                response = await self.assistant.stream_response(prompt, show_thinking=True)
            else:
                response = await self.assistant.call_ai_api(prompt)
                if response:
                    formatted_response = self.assistant.format_claude_code_response(response)
                    print(formatted_response)

            if response:
                # No need for extra newline as it's handled in format_claude_code_response
                pass

            if response:
                # Update conversation histories
                entry = {
                    "user": user_input,
                    "assistant": response,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                self.assistant.conversation_history.append(entry)

                # Save to session manager
                if self.assistant.session_manager:
                    self.assistant.session_manager.add_conversation_entry(user_input, response)
        except Exception as e:
            print(f"Error processing request: {e}")

    async def handle_slash_command(self, command: str):
        """Handle slash commands (Task 4)"""
        parts = command[1:].split()  # Remove the leading '/'
        if not parts:
            print("Usage: /<command> [args]")
            print("Available commands: help, models, switch, clear, exit")
            return

        subcommand = parts[0].lower()

        try:
            if subcommand == 'help':
                print("\nSlash Commands:")
                print("• '/help'                  - Show this help")
                print("• '/models'                - List available models")
                print("• '/switch <model>'        - Switch to different model")
                print("• '/clear'                 - Clear conversation history")
                print("• '/exit'                  - Exit the application")
                print()

            elif subcommand == 'models':
                print("\n[AI] Available models:")
                models = list(self.assistant.config['models'].keys())
                for i, model_id in enumerate(models, 1):
                    model = self.assistant.config['models'][model_id]
                    current = " (current)" if model_id == self.assistant.config['selected_model'] else ""
                    print(f"  {i}. {model['name']} - {model['description']} ({model['provider']}){current}")

            elif subcommand == 'switch':
                if len(parts) < 2:
                    print("Usage: /switch <model_number_or_name>")
                    print("Use '/models' to see available models")
                    return

                target = ' '.join(parts[1:])
                models = list(self.assistant.config['models'].keys())
                
                # Try to match by number
                if target.isdigit():
                    model_num = int(target)
                    if 1 <= model_num <= len(models):
                        selected_model = models[model_num - 1]
                    else:
                        print(f"[ERROR] Invalid model number. Please choose between 1 and {len(models)}")
                        return
                else:
                    # Try to match by name
                    selected_model = None
                    for model_id in models:
                        model = self.assistant.config['models'][model_id]
                        if target.lower() in model['name'].lower() or target.lower() in model_id.lower():
                            selected_model = model_id
                            break
                    
                    if not selected_model:
                        print(f"[ERROR] Model '{target}' not found. Use '/models' to see available models.")
                        return

                # Switch to the selected model
                self.assistant.config['selected_model'] = selected_model
                model_config = self.assistant.config['models'][selected_model]
                print(f"[OK] Switched to {model_config['name']} from {model_config['provider']}")

            elif subcommand == 'clear':
                self.assistant.conversation_history.clear()
                if self.assistant.session_manager:
                    self.assistant.session_manager.current_session['conversation'] = []
                print("[OK] Conversation history cleared")

            elif subcommand == 'exit':
                # Save session before exiting
                if self.assistant.session_manager:
                    self.assistant.session_manager.save_session()
                    print("\n[Session saved]")
                print("Goodbye!")
                exit(0)

            else:
                print(f"[ERROR] Unknown command: /{subcommand}")
                print("Use '/help' to see available commands")

        except Exception as e:
            print(f"Error with slash command: {e}")

    async def handle_session_command(self, command: str):
        """Handle session-related commands"""
        parts = command.split()
        if len(parts) < 2:
            print("Usage: session <list|save|load|import|export> [args]")
            return

        subcommand = parts[1].lower()

        try:
            if subcommand == 'list':
                sessions = self.assistant.session_manager.list_sessions()
                if sessions:
                    print("[INFO] Available sessions:")
                    for session in sessions:
                        active = " (current)" if session['id'] == self.assistant.session_manager.current_session['id'] else ""
                        created = datetime.datetime.fromisoformat(session['created']).strftime('%Y-%m-%d %H:%M')
                        print(f"  - {session['id']}{active} ({len(session.get('conversation', []))} entries, created {created})")
                        if session.get('description'):
                            print(f"    {session['description']}")
                else:
                    print("No sessions found.")

            elif subcommand == 'save':
                if len(parts) < 3:
                    print("Usage: session save <name>")
                    return

                session_name = ' '.join(parts[2:])
                if self.assistant.session_manager.create_session(session_name):
                    print(f"[OK] Session saved as: {session_name}")
                else:
                    print("[ERROR] Failed to save session.")

            elif subcommand == 'load':
                if len(parts) < 3:
                    print("Usage: session load <name>")
                    return

                session_name = ' '.join(parts[2:])
                if self.assistant.session_manager.load_session(session_name):
                    print(f"[OK] Switched to session: {session_name}")
                    # Reload conversation history
                    self.assistant.conversation_history = self.assistant.session_manager.get_conversation_history(20)
                    print(f"[INFO] Loaded {len(self.assistant.conversation_history)} conversation entries")
                else:
                    print(f"[ERROR] Session not found: {session_name}")

            elif subcommand == 'export':
                if len(parts) < 3:
                    print("Usage: session export <filename>")
                    return

                filename = ' '.join(parts[2:])
                if self.assistant.session_manager.export_session(filename):
                    print(f"[OK] Session exported to: {filename}")
                else:
                    print("[ERROR] Failed to export session.")

            elif subcommand == 'import':
                if len(parts) < 4:
                    print("Usage: session import <filename> <new-session-name>")
                    return

                filename = parts[2]
                new_name = ' '.join(parts[3:])
                if self.assistant.session_manager.import_session(filename, new_name):
                    print(f"[OK] Session imported as: {new_name}")
                else:
                    print("[ERROR] Failed to import session.")

        except Exception as e:
            print(f"Error with session command: {e}")
