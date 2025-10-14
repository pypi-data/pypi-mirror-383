#!/usr/bin/env python3
"""
gCoder - Python AI assistant for terminal-based development
Advanced AI-powered coding tool using Ollama with local models

Refactored version with clean modular structure
"""

__version__ = "1.0.6"

import argparse
import asyncio
import sys

from core.ai_assistant import AICodeAssistant
from handlers.request_handlers import RequestHandlers
from core.chat_manager import ChatManager


def main():
    """Entry point for the CLI application - wraps async main_async function."""
    asyncio.run(main_async())


async def main_async():
    parser = argparse.ArgumentParser(description="gCoder - Python AI assistant for terminal-based development")
    parser.add_argument('--config', type=str, default='config.json', help='Config file path')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Note: Removed explicit 'chat' subcommand as per Task 3
    # Chat is now the default behavior when no command is specified

    # Edit command
    edit_parser = subparsers.add_parser('edit', help='Edit a file with AI assistance')
    edit_parser.add_argument('file', help='File to edit')
    edit_parser.add_argument('--instruction', type=str, help='Editing instruction')

    # Run command
    run_parser = subparsers.add_parser('run', help='Execute a terminal command')
    run_parser.add_argument('command', help='Command to execute')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for patterns in files')
    search_parser.add_argument('pattern', help='Regex pattern to search for')
    search_parser.add_argument('--path', type=str, default='.', help='Path to search in')

    # File operations
    file_parser = subparsers.add_parser('file', help='File operations: create, copy, move, delete')
    file_parser.add_argument('operation', choices=['create', 'copy', 'move', 'delete'], help='Operation to perform')
    file_parser.add_argument('args', nargs='+', help='Arguments for the operation')

    # List directory
    list_parser = subparsers.add_parser('list', help='List directory contents')
    list_parser.add_argument('path', nargs='?', default='.', help='Directory to list')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze codebase')
    analyze_parser.add_argument('--path', type=str, default='.', help='Path to analyze')

    # Image analysis command
    image_parser = subparsers.add_parser('image', help='Analyze images using AI vision')
    image_parser.add_argument('image_path', help='Path to image file')
    image_parser.add_argument('--context', type=str, default='code', choices=['code', 'error', 'ui', 'terminal', 'general'], help='Analysis context')

    args = parser.parse_args()

    # Initialize the AI assistant
    assistant = AICodeAssistant(args.config)
    
    # Initialize request handlers
    request_handlers = RequestHandlers(assistant)
    
    # Initialize chat manager
    chat_manager = ChatManager(assistant, request_handlers)

    if not args.command:
        await chat_manager.chat_session()
    elif args.command == 'edit':
        instruction = args.instruction or f"Please review and improve the code in {args.file}"
        await request_handlers.edit_file(args.file, instruction)
    elif args.command == 'search':
        await request_handlers.search_files(args.pattern, args.path)
    elif args.command == 'file':
        if args.operation == 'create':
            content = args.args[1] if len(args.args) > 1 else ""
            await request_handlers.create_file(args.args[0], content)
        elif args.operation == 'copy':
            if len(args.args) != 2:
                print("Error: copy requires source and destination")
                return
            await request_handlers.copy_file(args.args[0], args.args[1])
        elif args.operation == 'move':
            if len(args.args) != 2:
                print("Error: move requires source and destination")
                return
            await request_handlers.move_file(args.args[0], args.args[1])
        elif args.operation == 'delete':
            await request_handlers.delete_file(args.args[0])
    elif args.command == 'list':
        await request_handlers.list_directory(args.path)
    elif args.command == 'run':
        await request_handlers.run_command(args.command)
    elif args.command == 'analyze':
        await request_handlers.analyze_codebase(args.path)
    elif args.command == 'image':
        await request_handlers.handle_image_command(args.image_path)
    else:
        parser.print_help()
        return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
