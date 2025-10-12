"""
Standardized state management for workflow nodes.

This module provides a consistent interface for accessing and managing 
workflow state, eliminating the need for manual workarounds and direct
__dict__ access.
"""

from typing import Any, Optional
from egregore.core.workflow.state import SharedState


class StateManager:
    """Centralized state management for workflow nodes"""
    
    def __init__(self, shared_state: SharedState):
        self.shared_state = shared_state
    
    def get_previous_output(self) -> Any:
        """Get previous node output with fallback logic"""
        # Check for manual override first (for tests)
        # Use direct __dict__ access to avoid triggering __getattr__
        if '_manual_previous_output' in self.shared_state.__dict__:
            return self.shared_state._manual_previous_output
        
        # Use standard previous_output property
        return self.shared_state.previous_output
    
    def set_previous_output(self, value: Any) -> None:
        """Set previous output with proper state management"""
        # For manual setting (primarily for tests), use the manual override
        self.shared_state._manual_previous_output = value
    
    def get_node_output(self, phase: str) -> Any:
        """Get output from a specific execution phase"""
        if not hasattr(self.shared_state, 'current') or self.shared_state.current is None:
            return None
            
        if phase == 'before_execute':
            return self.shared_state.current.before_execute
        elif phase == 'execute':
            return self.shared_state.current.execute
        elif phase == 'after_execute':
            return self.shared_state.current.after_execute
        else:
            return None
    
    def ensure_current_node(self, node) -> None:
        """Ensure current node state is properly initialized"""
        if not hasattr(self.shared_state, 'current') or self.shared_state.current is None:
            self.shared_state.set_current(node)
    
    def clear_manual_override(self) -> None:
        """Clear manual previous output override"""
        if '_manual_previous_output' in self.shared_state.__dict__:
            delattr(self.shared_state, '_manual_previous_output')


def get_state_manager(state: SharedState) -> StateManager:
    """Get or create a state manager for the given shared state"""
    if not hasattr(state, '_state_manager'):
        state._state_manager = StateManager(state)
    return state._state_manager