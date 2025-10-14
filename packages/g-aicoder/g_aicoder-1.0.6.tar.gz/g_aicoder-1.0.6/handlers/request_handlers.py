#!/usr/bin/env python3
"""
Request handlers module for gCoder
Handles different types of user requests and tool operations
"""

import asyncio
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import datetime
import glob


class RequestHandlers:
    """Handles various types of user requests and tool operations"""
    
    def __init__(self, assistant):
        self.assistant = assistant

    async def handle_read_file_request(self, match, streaming):
        """Handle file reading requests"""
        file_path = match.group(1)
        print(f"[REQUEST] Reading file: {file_path}")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"[FILE] Contents of {file_path}:")
                print("-" * 50)
                print(content)
                print("-" * 50)
                print(f"[SUCCESS] File read completed: {file_path} ({len(content)} characters)")
            except Exception as e:
                print(f"[ERROR] Error reading file: {e}")
        else:
            print(f"[ERROR] File not found: {file_path}")

    async def handle_edit_file_request(self, match, streaming):
        """Handle file editing requests"""
        file_path = match.group(1)
        instruction = match.group(2)
        await self.edit_file(file_path, instruction)

    async def handle_run_command_request(self, match, streaming):
        """Handle command execution requests"""
        command = match.group(1)
        print(f"[REQUEST] Executing command: {command}")
        await self.run_command(command)

    async def handle_search_request(self, match, streaming):
        """Handle search requests"""
        pattern = match.group(1)
        path = match.group(2) if len(match.groups()) > 1 else "."
        await self.search_files(pattern, path)

    async def handle_list_directory_request(self, match, streaming):
        """Handle directory listing requests"""
        path = match.group(1)
        await self.list_directory(path)

    async def handle_create_file_request(self, match, streaming):
        """Handle file creation requests with AI-generated content"""
        file_path = match.group(1)
        content_instruction = match.group(2) if len(match.groups()) > 1 else ""
        
        if content_instruction:
            # Use AI to generate content for the file
            await self.create_file_with_ai(file_path, content_instruction)
        else:
            # Create empty file
            await self.create_file(file_path, "")

    async def handle_analyze_request(self, match, streaming):
        """Handle codebase analysis requests"""
        path = match.group(1) if len(match.groups()) > 0 else "."
        await self.analyze_codebase(path)

    async def handle_image_request(self, match, streaming):
        """Handle image analysis requests"""
        image_path = match.group(1)
        await self.handle_image_command(image_path)

    async def handle_compound_request(self, match, streaming):
        """Handle compound requests with multiple actions"""
        # Extract all parts of the compound request
        groups = match.groups()
        actions = [group for group in groups if group and group.strip()]

        print(f"[PROCESS] Processing compound request with {len(actions)} actions...")

        for i, action in enumerate(actions, 1):
            print(f"\n[ACTION] Action {i}: {action.strip()}")
            # Recursively process each action
            await self.assistant.process_user_request(action.strip(), streaming)

    async def handle_help_request(self, match, streaming):
        """Handle help and capability requests"""
        print("\n[AI] gCoder Capabilities:")
        print("I can help you with:")
        print("[FILE] File Operations:")
        print("   • Read files: 'read main.py', 'show the contents of config.json'")
        print("   • Edit files: 'edit app.py to add error handling', 'modify the function to include validation'")
        print("   • Create files: 'create a new file utils.py', 'make an empty file test.txt'")
        print("   • List directories: 'list the contents of src/', 'show directory structure'")
        print("   • Search code: 'search for TODO comments', 'find all class definitions'")
        print()
        print("[CMD] Command Execution:")
        print("   • Run commands: 'run npm install', 'execute python script.py'")
        print("   • System commands: 'run ls -la', 'execute git status'")
        print()
        print("[ANALYZE] Code Analysis:")
        print("   • Analyze codebase: 'analyze the project', 'review the source code'")
        print("   • Code insights: 'examine the architecture', 'study the patterns'")
        print()
        print("[IMAGE] Multi-Modal Operations:")
        print("   • Image analysis: 'analyze the image diagram.png'")
        print("   • Vision-guided editing: 'edit code based on the screenshot'")
        print()
        print("[ADVANCED] Advanced Features:")
        print("   • Session management: 'session save myproject', 'session load work'")
        print("   • Compound requests: 'read main.py then edit it to add comments'")
        print("   • Natural language: Just describe what you want to do!")
        print()
        print("[TIPS] Tips:")
        print("   • Use natural language - no need to remember exact commands")
        print("   • Chain multiple actions: 'first read the file, then edit it'")
        print("   • Be specific about what you want to accomplish")
        print("   • Ask for help anytime with 'help' or 'what can you do'")

    async def edit_file(self, file_path: str, instruction: str):
        """Edit a file with AI assistance"""
        try:
            # Check if permission is already granted
            if not self.assistant.permission_manager.has_permission("edit_file"):
                # Ask for permission (Tasks 5 & 6)
                if not self.assistant.permission_manager.ask_permission("edit_file"):
                    print("❌ File editing cancelled by user.")
                    return

            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return

            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()

            # Create prompt for editing
            prompt = f"""System: You are an expert software developer helping to edit code files. When you provide code, wrap it in ```language markdown blocks.

User: Here is a file I want to edit:

File: {file_path}
Content:
```language
{file_content}
```

Instruction: {instruction}

Please provide the improved/modified version of this file, wrapped in code blocks.
Assistant:"""

            response = await self.assistant.call_ollama_api(prompt)

            if response:
                # Extract code from response
                code_match = re.search(r'```[^\n]*\n(.*?)\n```', response, re.DOTALL)
                if code_match:
                    new_content = code_match.group(1).strip()
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✓ File updated: {file_path}")
                else:
                    print("Could not extract code from AI response. Here is the full response:")
                    print(response)
            else:
                print("Failed to get AI response for editing.")

        except Exception as e:
            print(f"Error editing file: {e}")

    async def search_files(self, pattern: str, path: str = "."):
        """Search for patterns in files using grep-like functionality"""
        try:
            target_path = Path(path)
            if not target_path.exists():
                print(f"Path not found: {path}")
                return

            code_extensions = ['*.py', '*.js', '*.ts', '*.java', '*.c', '*.cpp', '*.cs', '*.php', '*.rb', '*.go', '*.rs', '*.txt', '*.md']
            matches = []

            print(f"[SEARCH] Searching for '{pattern}' in {os.path.abspath(path)}")

            for ext_pattern in code_extensions:
                for file_path in target_path.rglob(ext_pattern):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            for line_num, line in enumerate(lines, 1):
                                if re.search(pattern, line, re.IGNORECASE):
                                    matches.append({
                                        'file': str(file_path.relative_to(target_path)) if file_path.is_relative_to(target_path) else str(file_path),
                                        'line': line_num,
                                        'content': line.strip(),
                                        'path': str(file_path)
                                    })
                    except Exception:
                        continue

            if matches:
                print(f"Found {len(matches)} matches:")
                for match in matches[:50]:  # Limit to first 50 results
                    print(f"{match['file']}:{match['line']}: {match['content']}")
                if len(matches) > 50:
                    print(f"... and {len(matches) - 50} more matches")
            else:
                print("No matches found")

        except Exception as e:
            print(f"Error searching files: {e}")

    async def create_file(self, file_path: str, content: str = ""):
        """Create a new file with optional content"""
        try:
            # Check if permission is already granted
            if not self.assistant.permission_manager.has_permission("create_file"):
                # Ask for permission (Tasks 5 & 6)
                if not self.assistant.permission_manager.ask_permission("create_file"):
                    print("❌ File creation cancelled by user.")
                    return

            full_path = Path(file_path)
            if full_path.exists():
                print(f"File already exists: {file_path}")
                overwrite = input("Overwrite? (y/N): ").lower().strip()
                if overwrite != 'y':
                    return

            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] File created: {file_path}")

        except Exception as e:
            print(f"Error creating file: {e}")

    async def create_file_with_ai(self, file_path: str, instruction: str):
        """Create a new file with AI-generated content"""
        try:
            # Check if permission is already granted
            if not self.assistant.permission_manager.has_permission("create_file"):
                # Ask for permission (Tasks 5 & 6)
                if not self.assistant.permission_manager.ask_permission("create_file"):
                    print("❌ File creation cancelled by user.")
                    return

            full_path = Path(file_path)
            if full_path.exists():
                print(f"File already exists: {file_path}")
                overwrite = input("Overwrite? (y/N): ").lower().strip()
                if overwrite != 'y':
                    return

            # Determine file type from extension for better AI prompting
            file_extension = full_path.suffix.lower()
            language_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.java': 'java',
                '.c': 'c',
                '.cpp': 'cpp',
                '.cs': 'csharp',
                '.php': 'php',
                '.rb': 'ruby',
                '.go': 'go',
                '.rs': 'rust',
                '.html': 'html',
                '.css': 'css',
                '.json': 'json',
                '.xml': 'xml',
                '.yaml': 'yaml',
                '.yml': 'yaml',
                '.md': 'markdown',
                '.txt': 'text'
            }
            language = language_map.get(file_extension, 'text')

            # Create prompt for file creation
            prompt = f"""System: You are an expert software developer creating a new file. When you provide code, wrap it in ```{language} markdown blocks.

User: Please create a new file called {file_path} with the following content:

{instruction}

Please provide the complete file content, wrapped in code blocks.
Assistant:"""

            response = await self.assistant.call_ai_api(prompt)

            if response:
                # Extract code from response
                code_match = re.search(r'```[^\n]*\n(.*?)\n```', response, re.DOTALL)
                if code_match:
                    content = code_match.group(1).strip()
                    
                    # Create directory if needed
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write the content to file
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"[OK] File created with AI-generated content: {file_path}")
                    print(f"File size: {len(content)} characters")
                    
                    # Show preview of the created file
                    preview_lines = content.split('\n')[:10]
                    total_lines = len(content.split('\n'))
                    print("Preview:")
                    for i, line in enumerate(preview_lines, 1):
                        print(f"  {i:2d}: {line}")
                    if total_lines > 10:
                        print(f"  ... and {total_lines - 10} more lines")
                else:
                    print("Could not extract code from AI response. Here is the full response:")
                    print(response)
            else:
                print("Failed to get AI response for file creation.")

        except Exception as e:
            print(f"Error creating file with AI: {e}")

    async def copy_file(self, source: str, dest: str):
        """Copy a file from source to destination"""
        try:
            # Check if permission is already granted
            if not self.assistant.permission_manager.has_permission("copy_file"):
                # Ask for permission (Tasks 5 & 6)
                if not self.assistant.permission_manager.ask_permission("copy_file"):
                    print("❌ File copy cancelled by user.")
                    return

            shutil.copy2(source, dest)
            print(f"[OK] File copied: {source} -> {dest}")
        except Exception as e:
            print(f"Error copying file: {e}")

    async def move_file(self, source: str, dest: str):
        """Move/rename a file"""
        try:
            # Check if permission is already granted
            if not self.assistant.permission_manager.has_permission("move_file"):
                # Ask for permission (Tasks 5 & 6)
                if not self.assistant.permission_manager.ask_permission("move_file"):
                    print("❌ File move cancelled by user.")
                    return

            shutil.move(source, dest)
            print(f"[OK] File moved: {source} -> {dest}")
        except Exception as e:
            print(f"Error moving file: {e}")

    async def delete_file(self, file_path: str):
        """Delete a file"""
        try:
            # Check if permission is already granted
            if not self.assistant.permission_manager.has_permission("delete_file"):
                # Ask for permission (Tasks 5 & 6)
                if not self.assistant.permission_manager.ask_permission("delete_file"):
                    print("❌ File deletion cancelled by user.")
                    return

            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"[OK] File deleted: {file_path}")
            else:
                print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error deleting file: {e}")

    async def list_directory(self, path: str = "."):
        """List directory contents with details"""
        try:
            target_path = Path(path)
            if not target_path.exists():
                print(f"Path not found: {path}")
                return

            print(f"📁 Contents of {os.path.abspath(path)}:")
            items = list(target_path.iterdir())
            items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

            for item in items:
                size = ""
                if item.is_file():
                    file_size = item.stat().st_size
                    if file_size < 1024:
                        size = f"{file_size}B"
                    elif file_size < 1024*1024:
                        size = f"{file_size//1024}K"
                    else:
                        size = f"{file_size//(1024*1024)}M"
                else:
                    size = "DIR"

                mod_time = datetime.datetime.fromtimestamp(item.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                print(f"{'[DIR]' if item.is_dir() else ''}{item.name:<30} {size:>8} {mod_time}")

        except Exception as e:
            print(f"Error listing directory: {e}")

    async def run_command(self, command: str):
        """Execute a terminal command with permission checking"""
        try:
            # Check if permission is already granted
            if not self.assistant.permission_manager.has_permission("run_command"):
                # Ask for permission (Tasks 5 & 6)
                if not self.assistant.permission_manager.ask_permission("run_command"):
                    print("❌ Command execution cancelled by user.")
                    return
            
            print(f"Executing: {command}")
            import subprocess
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            print(f"Exit code: {result.returncode}")
        except Exception as e:
            print(f"Error executing command: {e}")

    async def analyze_codebase(self, path: str = "."):
        """Analyze the codebase in the given directory"""
        try:
            target_path = Path(path)
            if not target_path.exists():
                print(f"Path not found: {path}")
                return

            # Collect code files
            code_extensions = ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.cs', '.php', '.rb', '.go', '.rs']
            code_files = []
            total_files = 0

            for file_path in target_path.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    if file_path.suffix.lower() in code_extensions:
                        rel_path = file_path.relative_to(target_path)
                        file_info = {
                            'path': str(rel_path),
                            'extension': file_path.suffix,
                            'size': file_path.stat().st_size
                        }
                        code_files.append(file_info)

            # Sample up to 10 files for analysis
            sample_files = code_files[:10]
            analysis_text = f"Codebase Analysis for: {os.path.abspath(path)}\n"
            analysis_text += f"Total files: {total_files}, Code files: {len(code_files)}\n\n"

            for file_info in sample_files:
                try:
                    with open(target_path / file_info['path'], 'r', encoding='utf-8') as f:
                        content = f.read()
                        preview = content[:500] + "..." if len(content) > 500 else content

                    analysis_text += f"File: {file_info['path']}\n"
                    analysis_text += f"Size: {file_info['size']} bytes\n"
                    analysis_text += f"Preview:\n{preview}\n\n"
                except Exception as e:
                    analysis_text += f"File: {file_info['path']} (could not read: {e})\n\n"

            # Ask AI to analyze
            prompt = f"""System: You are a senior software engineer analyzing a codebase.

User: Please analyze this codebase and provide insights:

{analysis_text}

Assistant:"""

            response = await self.assistant.call_ollama_api(prompt)
            if response:
                print("🔍 Codebase Analysis:")
                print(response)
            else:
                print("Failed to get codebase analysis.")

        except Exception as e:
            print(f"Error analyzing codebase: {e}")

    async def handle_image_command(self, image_path: str):
        """Handle image analysis command"""
        if not image_path:
            print("Usage: image <image_file_path>")
            return

        try:
            if not os.path.exists(image_path):
                print(f"❌ Image file not found: {image_path}")
                return

            if not self.assistant.image_analyzer.is_supported_format(image_path):
                supported = ', '.join(self.assistant.image_analyzer.SUPPORTED_FORMATS)
                print(f"❌ Unsupported format. Supported: {supported}")
                return

            print("🔍 Analyzing image...")
            result = await self.assistant.image_analyzer.analyze_image(image_path)

            if result:
                print("Image Analysis:")
                print(result)
            else:
                print("❌ Failed to analyze image. Make sure you have a vision-capable model.")
                print("Try: ollama pull llava")

        except Exception as e:
            print(f"Error analyzing image: {e}")
