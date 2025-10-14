#!/usr/bin/env python3
"""
Permission management module for g-aicoder
Handles command execution permissions and user consent
"""

from typing import Dict, Set, Optional


class PermissionManager:
    """Manages command execution permissions and user consent"""
    
    def __init__(self):
        self.permissions = {
            'granted': False,
            'asked': False,
            'session_commands': set(),  # Commands allowed for this session
            'remembered_commands': set()  # Commands always allowed
        }
    
    def ask_permission(self, command_name: str) -> bool:
        """
        Ask for permission to execute a command (Tasks 5 & 6)
        
        Returns:
            bool: True if permission granted, False otherwise
        """
        print(f"\n🔐 G-AiCoder asks for following permissions:")
        print(f"Command: {command_name}")
        print("a. Allow")
        print("b. Allow and Remember for this session for this command")
        print("c. Tell to do differently")
        
        while True:
            choice = input("\nChoose (a/b/c): ").strip().lower()
            
            if choice == 'a':
                print("✅ Permission granted for this execution")
                return True
            elif choice == 'b':
                self.permissions['session_commands'].add(command_name)
                print("✅ Permission granted and remembered for this session")
                return True
            elif choice == 'c':
                print("❌ Permission denied. Please rephrase your request.")
                return False
            else:
                print("❌ Invalid choice. Please choose a, b, or c.")
    
    def has_permission(self, command_name: str) -> bool:
        """
        Check if permission is granted for a command
        
        Args:
            command_name: The command to check permission for
            
        Returns:
            bool: True if permission is granted, False otherwise
        """
        # Check if command is in remembered commands
        if command_name in self.permissions['remembered_commands']:
            return True
        
        # Check if command is in session commands
        if command_name in self.permissions['session_commands']:
            return True
        
        # Check global permission
        if self.permissions['granted']:
            return True
            
        return False
    
    def grant_global_permission(self):
        """Grant global permission for all commands"""
        self.permissions['granted'] = True
        self.permissions['asked'] = True
    
    def deny_global_permission(self):
        """Deny global permission"""
        self.permissions['granted'] = False
        self.permissions['asked'] = True
    
    def remember_command(self, command_name: str):
        """Remember a command as always allowed"""
        self.permissions['remembered_commands'].add(command_name)
    
    def clear_session_permissions(self):
        """Clear session-specific permissions"""
        self.permissions['session_commands'].clear()
    
    def get_permission_status(self) -> Dict:
        """Get current permission status"""
        return {
            'global_granted': self.permissions['granted'],
            'session_commands': list(self.permissions['session_commands']),
            'remembered_commands': list(self.permissions['remembered_commands'])
        }
