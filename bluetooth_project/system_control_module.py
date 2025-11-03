"""
System Control Module
=====================
Handles Windows system operations including screen locking and wake simulation.
Uses Windows API calls through ctypes and os modules.

Platform: Windows 10/11
Author: Professional Development Team
Version: 1.0.0
"""

import os
import sys
import ctypes
from typing import Optional
from enum import Enum

import config_module as config


class SystemState(Enum):
    """Enumeration of possible system states."""
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    UNKNOWN = "unknown"


class WindowsSystemController:
    """
    Manages Windows system lock/unlock operations.
    
    Attributes:
        current_state (SystemState): Current lock state of the system
        lock_count (int): Number of times system has been locked
        unlock_count (int): Number of times system has been unlocked
    """
    
    def __init__(self):
        """Initialize the system controller."""
        self.current_state = SystemState.UNKNOWN
        self.lock_count = 0
        self.unlock_count = 0
        self._validate_platform()
    
    def _validate_platform(self):
        """Ensure the script is running on Windows."""
        if sys.platform != "win32":
            raise RuntimeError("This module only supports Windows operating systems.")
    
    def lock_system(self) -> bool:
        """
        Lock the Windows workstation.
        
        This immediately locks the screen and requires user credentials to unlock.
        Uses the Windows API LockWorkStation function.
        
        Returns:
            bool: True if lock command executed successfully, False otherwise
        """
        try:
            if config.VERBOSE_LOGGING:
                print("[ACTION] Executing system lock...")
            
            # Call Windows API to lock workstation
            result = os.system("rundll32.exe user32.dll,LockWorkStation")
            
            if result == 0:
                self.current_state = SystemState.LOCKED
                self.lock_count += 1
                if config.VERBOSE_LOGGING:
                    print(f"[SUCCESS] System locked (Total locks: {self.lock_count})")
                return True
            else:
                print(f"[WARNING] Lock command returned non-zero status: {result}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to lock system: {e}")
            return False
    
    def wake_system(self) -> bool:
        """
        Simulate system wake/activity.
        
        Note: True wake from sleep requires hardware-level triggers.
        This function simulates user activity by generating a mouse event,
        which can wake the display or prevent sleep mode.
        
        Returns:
            bool: True if wake command executed successfully, False otherwise
        """
        try:
            if config.VERBOSE_LOGGING:
                print("[ACTION] Simulating system wake/activity...")
            
            # MOUSEEVENTF_MOVE with no delta = simulated activity without visible cursor movement
            # This keeps the system awake and can turn on the display
            ctypes.windll.user32.mouse_event(0x0001, 0, 0, 0, 0)
            
            self.current_state = SystemState.UNLOCKED
            self.unlock_count += 1
            
            if config.VERBOSE_LOGGING:
                print(f"[SUCCESS] System activity simulated (Total wakes: {self.unlock_count})")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to wake system: {e}")
            return False
    
    def get_state(self) -> SystemState:
        """
        Get the current system state.
        
        Returns:
            SystemState: Current lock state
        """
        return self.current_state
    
    def get_statistics(self) -> dict:
        """
        Get statistics about system operations.
        
        Returns:
            dict: Dictionary containing lock/unlock counts and current state
        """
        return {
            "current_state": self.current_state.value,
            "total_locks": self.lock_count,
            "total_unlocks": self.unlock_count
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

# Global controller instance
_controller: Optional[WindowsSystemController] = None


def get_controller() -> WindowsSystemController:
    """
    Get or create the global system controller instance.
    
    Returns:
        WindowsSystemController: Singleton controller instance
    """
    global _controller
    if _controller is None:
        _controller = WindowsSystemController()
    return _controller


def lock_system() -> bool:
    """Convenience function to lock the system."""
    return get_controller().lock_system()


def wake_system() -> bool:
    """Convenience function to wake the system."""
    return get_controller().wake_system()


def get_system_state() -> SystemState:
    """Convenience function to get current system state."""
    return get_controller().get_state()


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("System Control Module - Test Mode")
    print("=" * 60)
    
    controller = WindowsSystemController()
    
    print("\nTesting lock functionality...")
    controller.lock_system()
    
    print("\nCurrent statistics:")
    stats = controller.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
