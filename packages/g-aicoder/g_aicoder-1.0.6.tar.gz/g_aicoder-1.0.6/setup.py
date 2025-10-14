#!/usr/bin/env python3
"""
Setup script for Cline Clone - Python version of AI assistant
Makes the tool installable and executable with automatic path setup
"""

import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop


class PostInstallCommand(install):
    """Post-installation for production installs."""

    def run(self):
        # Run the standard install process
        install.run(self)

        # Perform custom post-install actions
        self._post_install_setup()

    def _post_install_setup(self):
        """Add the installed script to PATH and create working directory."""
        try:
            # Get the installed script path
            script_name = 'gcoder' if sys.platform != 'win32' else 'gcoder.exe'

            # Try to add to PATH
            self._add_to_path(script_name)

            # Create working directory
            self._create_working_directory()

            print("\n[SUCCESS] gCoder installation completed successfully!")
            print("[INFO] You can now use 'gcoder' command from anywhere in your terminal")
            print("[INFO] Working directory created at: ~/.gcoder")
            print("\nQuick start:")
            print("   gcoder chat    # Start interactive chat")
            print("   gcoder --help  # Show all available commands")

        except Exception as e:
            print(f"\n⚠️  Post-install setup warning: {e}")
            print("The tool is still functional, but PATH setup may need manual configuration.")

    def _add_to_path(self, script_name):
        """Add the installed script to system PATH."""
        try:
            if sys.platform == 'win32':
                # Windows PATH setup
                self._windows_path_setup(script_name)
            else:
                # Unix-like systems
                self._unix_path_setup(script_name)
        except Exception as e:
            print(f"PATH setup skipped: {e}")

    def _windows_path_setup(self, script_name):
        """Windows-specific PATH setup."""
        import winreg

        try:
            # Get Python scripts directory
            scripts_dir = Path(sys.executable).parent / 'Scripts'
            script_path = scripts_dir / script_name

            if script_path.exists():
                # Add to user PATH (safer than system PATH)
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                   'Environment',
                                   0, winreg.KEY_READ | winreg.KEY_WRITE)

                try:
                    current_path, _ = winreg.QueryValueEx(key, 'PATH')
                    if str(scripts_dir) not in current_path:
                        new_path = current_path + os.pathsep + str(scripts_dir)
                        winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
                        print("✅ Added to Windows user PATH")
                        print("🔄 Please restart your terminal/command prompt")
                except FileNotFoundError:
                    # PATH doesn't exist yet
                    winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, str(scripts_dir))
                    print("✅ Added to Windows user PATH (new)")
                finally:
                    winreg.CloseKey(key)

        except Exception as e:
            print(f"Windows PATH setup failed: {e}")

    def _unix_path_setup(self, script_name):
        """Unix-like systems PATH setup."""
        try:
            # Check if script was installed in standard location
            script_paths = [
                Path.home() / '.local' / 'bin' / script_name,
                Path(sys.executable).parent / script_name,
                Path('/usr/local/bin') / script_name,
                Path('/usr/bin') / script_name
            ]

            script_found = None
            for script_path in script_paths:
                if script_path.exists():
                    script_found = script_path
                    break

            if script_found:
                # Check if already in PATH
                current_path = os.environ.get('PATH', '')
                script_dir = str(script_found.parent)

                if script_dir not in current_path:
                    # Try to add to shell configuration
                    self._update_shell_config(script_dir)
                else:
                    print("✅ Script already in PATH")
            else:
                print("ℹ️ Script installed but not automatically found in PATH")
                print("Add Python's bin directory to your PATH manually if needed")

        except Exception as e:
            print(f"Unix PATH setup failed: {e}")

    def _update_shell_config(self, script_dir):
        """Update shell configuration files."""
        shell_config_files = [
            Path.home() / '.bashrc',
            Path.home() / '.zshrc',
            Path.home() / '.profile',
        ]

        export_line = f'\nexport PATH="{script_dir}:$PATH"  # Added by Cline Clone installer\n'

        for config_file in shell_config_files:
            if config_file.exists():
                try:
                    content = config_file.read_text()

                    # Check if already added
                    if script_dir in content:
                        print(f"PATH already configured in {config_file.name}")
                        continue

                    # Add to config
                    content += export_line
                    config_file.write_text(content)
                    print(f"Added to {config_file.name}")

                except Exception as e:
                    print(f"Failed to update {config_file.name}: {e}")

        print("Please run 'source ~/.bashrc' (or restart terminal) to apply PATH changes")

    def _create_working_directory(self):
        """Create the application working directory."""
        work_dir = Path.home() / '.gcoder'

        try:
            work_dir.mkdir(exist_ok=True)

            # Create subdirectories
            (work_dir / 'sessions').mkdir(exist_ok=True)
            (work_dir / 'cache').mkdir(exist_ok=True)
            (work_dir / 'logs').mkdir(exist_ok=True)

            # Create default config if doesn't exist
            config_file = work_dir / 'config.json'
            if not config_file.exists():
                default_config = {
                    "ollama": {
                        "base_url": "http://localhost:11434",
                        "model": "qwen2.5-coder:7b",
                        "timeout": 600,
                        "temperature": 0.7,
                        "max_tokens": 4096
                    },
                    "app": {
                        "name": "gCoder",
                        "version": "1.0.0",
                        "working_directory": str(work_dir)
                    },
                    "performance": {
                        "connection_pool_size": 10,
                        "max_concurrent_streams": 3,
                        "enable_caching": True,
                        "cache_max_size": 50
                    },
                    "security": {
                        "sandbox": True,
                        "allowed_commands": [],
                        "blocked_commands": ["rm -rf /", "format", "del /s"]
                    },
                    "mcp": {
                        "enabled": True,
                        "external_tools": []
                    }
                }

                import json
                config_file.write_text(json.dumps(default_config, indent=2))

            print(f"✅ Working directory created: {work_dir}")

        except Exception as e:
            print(f"Failed to create working directory: {e}")


class PostDevelopCommand(develop):
    """Post-installation for development installs."""

    def run(self):
        # Run the standard develop process
        develop.run(self)

        # Perform minimal setup for development
        self._dev_setup()

    def _dev_setup(self):
        """Minimal setup for development installs."""
        work_dir = Path.home() / '.gcoder'
        work_dir.mkdir(exist_ok=True)
        print("✅ Development installation completed")
        print(f"📁 Working directory: {work_dir}")


def read_requirements():
    """Read requirements from requirements.txt."""
    try:
        with open('requirements.txt', 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        # Fallback requirements
        return [
            'aiohttp>=3.13.0',
            'Pillow>=10.0.0',
            'setuptools>=65.0',
        ]


def read_readme():
    """Read README content."""
    try:
        with open('README.md', 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except FileNotFoundError:
        return "gCoder - Advanced AI development assistant with multi-modal intelligence"


# Package metadata
try:
    with open('main.py', 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                VERSION = line.split('=')[1].strip().strip('"\'')
                break
        else:
            VERSION = '1.0.0'
except Exception:
    VERSION = '1.0.0'

setup(
    name="gcoder",
    version=VERSION,
    author="gCoder Project",
    author_email="",
    description="gCoder - Advanced AI development assistant with multi-modal intelligence",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/prdpspkt/gCoder",

    # Package configuration
    packages=find_packages(),
    py_modules=['main', 'session_manager', 'streaming_analyzer', 'image_analyzer', 'mcp_server'],
    include_package_data=True,
    python_requires='>=3.8',

    # Dependencies
    install_requires=read_requirements(),

    # Entry points - this creates the executable
    entry_points={
        'console_scripts': [
            'gcoder=main:main',
        ],
    },

    # Custom install command
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },

    # Classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],

    keywords="ai assistant coding development claude ollama terminal",

    # Project info
    project_urls={
        "Bug Reports": "https://github.com/prdpspkt/gCoder/issues",
        "Source": "https://github.com/prdpspkt/gCoder",
    },
)
