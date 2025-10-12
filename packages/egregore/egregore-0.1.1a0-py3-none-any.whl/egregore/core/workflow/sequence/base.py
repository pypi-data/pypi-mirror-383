"""
Core Sequence implementation for workflow orchestration.
Provides composable workflow sequences with JSON serialization for Cerebrum integration.
"""

import asyncio
import uuid
import json
import time
import os
from datetime import datetime
from typing import List, Dict, Set, Tuple, Any, TypeVar, Optional
from collections import deque
from pathlib import Path

from egregore.core.workflow.base_node import BaseNode, NodeType, Node, Decision, AsyncNode
from egregore.core.workflow.state import SharedState, InitialInput, NodeOutput, WorkflowStateContext
from egregore.core.workflow.base_node import decision, node_factory as node, NodeMapper, BatchNode
from egregore.core.workflow.exceptions import create_error_context, WorkflowError, FatalError, TimeoutError
from egregore.core.workflow.error_handler import AsyncErrorHandler, create_error_handler
from egregore.core.workflow.memory_management import (
    CopyOnWriteState, StatePool, ResourceTracker, MemoryMonitor,
    get_state_pool, get_resource_tracker, get_memory_monitor
)



class WorkflowStoppedException(Exception):
    """Raised when workflow is stopped via controller"""
    pass


class WorkflowController:
    """External controller for workflow execution management with execution tracking"""
    
    def __init__(self, workflow: 'Sequence'):
        self.workflow = workflow
        self._state = 'ready'  # ready, running, paused, stopped, completed, error
        self._control_event = asyncio.Event()
        self._control_event.set()  # Start unpaused
        self._stop_requested = False
        
        # Track current execution location for nested sequences
        self.current_execution_path = []  # e.g., ["main_workflow", "seq1", "node_e"]
        self.execution_depth = 0
        
        # Execution tracking
        from ..execution import ExecutionHistory
        self.execution_history = ExecutionHistory()
        self.current_execution = None
        self.execution_counter = 0
        
        # Phase 3: Position tracking for workflow traversal
        self.execution_position = 0  # Track position in workflow sequence
        
        # Performance metrics
        self.total_execution_time = 0.0
        self.node_execution_counts = {}
        
        # Phase 6: Node Registry for GUID-based tracking
        from ..base_node import NodeRegistry
        self.node_registry = NodeRegistry()
        self._register_workflow_nodes(workflow)
        
        # Reporting system
        from ..reporting import WorkflowReportingSystem
        self.reporting = WorkflowReportingSystem(self)
        
        # Plan 7: Checkpoint management
        self.auto_checkpoint_enabled = True
        self.checkpoint_dir = Path(".checkpoints")
        self.checkpoint_retention_days = 7
        self.auto_checkpoint_interval = 1  # Every N successful nodes
        self._auto_checkpoint_counter = 0
        
        # Hook system registry
        self._hook_registry = {
            "pre_sequence": [],           # [(hook_func, target_name), ...]
            "post_sequence": [],          
            "on_sequence_error": [],      
            "pre_execution": [],          
            "post_execution": [],         
            "on_error": [],               
        }
        
        # Callback subscribers (new clean API)
        self._callback_subscribers = []   # For controller.subscribe()
        self._subscription_counter = 0    # For unique subscription IDs
        
    def pause(self) -> None:
        """Pause workflow execution"""
        if self._state == 'running':
            self._state = 'paused'
            self._control_event.clear()
            
            # Notify observers with execution location
            if hasattr(self.workflow.state, '_notify_state_change'):
                self.workflow.state._notify_state_change('workflow_paused', self.workflow.name, {
                    'timestamp': time.time(),
                    'controller_state': self._state,
                    'current_execution_path': self.current_execution_path.copy(),
                    'execution_depth': self.execution_depth
                })
    
    def resume(self) -> None:
        """Resume paused workflow execution"""
        if self._state == 'paused':
            self._state = 'running'
            self._control_event.set()
            
            # Notify observers
            if hasattr(self.workflow.state, '_notify_state_change'):
                self.workflow.state._notify_state_change('workflow_resumed', self.workflow.name, {
                    'timestamp': time.time(),
                    'controller_state': self._state
                })
    
    def stop(self) -> None:
        """Stop workflow execution"""
        if self._state in ['running', 'paused']:
            self._state = 'stopped'
            self._stop_requested = True
            self._control_event.set()  # Unblock if paused
            
            # Notify observers
            if hasattr(self.workflow.state, '_notify_state_change'):
                self.workflow.state._notify_state_change('workflow_stopped', self.workflow.name, {
                    'timestamp': time.time(),
                    'controller_state': self._state
                })
    
    def restart(self) -> None:
        """Restart workflow from beginning"""
        self._state = 'ready'
        self._stop_requested = False
        self._control_event.set()
        
        # Reset workflow state
        self.workflow.state = SharedState(self.workflow.state.instance_name)
        
        # Restore workflow reference
        self.workflow.state.workflow = self.workflow
        
        # Notify observers
        if hasattr(self.workflow.state, '_notify_state_change'):
            self.workflow.state._notify_state_change('workflow_restarted', self.workflow.name, {
                'timestamp': time.time(),
                'controller_state': self._state
            })
    
    @property
    def state(self) -> str:
        """Get current controller state"""
        return self._state
    
    @property
    def is_running(self) -> bool:
        """Check if workflow is currently running"""
        return self._state == 'running'
    
    @property
    def is_paused(self) -> bool:
        """Check if workflow is paused"""
        return self._state == 'paused'
    
    @property
    def is_stopped(self) -> bool:
        """Check if workflow is stopped"""
        return self._state == 'stopped'
    
    async def _check_control_state(self) -> None:
        """Internal method to check for pause/stop during execution"""
        # Wait if paused
        await self._control_event.wait()
        
        # Check if stop was requested
        if self._stop_requested:
            raise WorkflowStoppedException("Workflow execution was stopped")
    
    # Execution tracking methods
    def start_node_execution(self, node: 'BaseNode', input_value: Any) -> 'ExecutionEntry':
        """Phase 3: Record the start of node execution with enhanced identity tracking"""
        from ..execution import ExecutionEntry
        
        # Phase 3: Use factory method with position tracking
        entry = ExecutionEntry.from_node(node, input_value, self.execution_position)
        
        self.current_execution = entry
        self.execution_history.add_entry(entry)
        self.execution_counter += 1
        
        # Phase 3: Increment position for next node
        self.execution_position += 1
        
        # Update metrics (legacy support)
        self.node_execution_counts[entry.node_name] = \
            self.node_execution_counts.get(entry.node_name, 0) + 1
        
        # Phase 3: Notify event subscribers of node execution start
        if hasattr(self, 'reporting') and self.reporting:
            self.reporting._notify_subscribers('node_execution_started', {
                'node_name': entry.effective_name,
                'node_guid': entry.node_guid,
                'execution_id': entry.execution_id,
                'input_value': str(input_value)[:100] if input_value else None,
                'timestamp': entry.start_time.isoformat() if entry.start_time else None
            })
        
        return entry
    
    def complete_node_execution(self, entry: 'ExecutionEntry', output_value: Any) -> None:
        """Record the completion of node execution with automatic checkpointing"""
        entry.complete(output_value)
        
        if entry.duration:
            self.total_execution_time += entry.duration
        
        # Plan 7: Automatic checkpoint after successful node execution
        if self.auto_checkpoint_enabled:
            self._auto_checkpoint(entry.effective_name)
        
        # Phase 4: Check performance thresholds after completion
        if hasattr(self, 'reporting') and self.reporting:
            self.reporting.check_performance_thresholds(entry)
            
            # Phase 3: Notify event subscribers
            self.reporting._notify_subscribers('node_execution_completed', {
                'node_name': entry.effective_name,
                'node_guid': entry.node_guid,
                'execution_id': entry.execution_id,
                'duration': entry.duration,
                'output_value': str(output_value)[:100] if output_value else None,
                'timestamp': entry.end_time.isoformat() if entry.end_time else None
            })
        
        self.current_execution = None
    
    def error_node_execution(self, entry: 'ExecutionEntry', error: Exception) -> None:
        """Record an error during node execution"""
        entry.fail(error)
        self.current_execution = None
    
    def get_execution_summary(self) -> dict:
        """Get summary of execution metrics"""
        return {
            'total_executions': len(self.execution_history),
            'total_execution_time': self.total_execution_time,
            'node_execution_counts': self.node_execution_counts.copy(),
            'unique_nodes': len(self.node_execution_counts),
            'current_execution': self.current_execution.node_name if self.current_execution else None
        }
    
    def _register_workflow_nodes(self, workflow: 'Sequence') -> None:
        """Phase 6: Register all nodes in workflow with registry"""
        def register_recursive(node):
            if node and node not in visited:
                # Register node with registry
                self.node_registry.register_node(node)
                visited.add(node)
                
                # Follow next_node chain
                if hasattr(node, 'next_node') and node.next_node:
                    register_recursive(node.next_node)
                
                # For Decision nodes, register both branches
                if hasattr(node, 'true_node') and node.true_node:
                    register_recursive(node.true_node)
                if hasattr(node, 'false_node') and node.false_node:
                    register_recursive(node.false_node)
                
                # For Sequence nodes, register their internal chain
                if hasattr(node, 'start') and node.start:
                    register_recursive(node.start)
                
        visited = set()
        if workflow.start:
            register_recursive(workflow.start)
    
    # Plan 7: Checkpoint Management Methods
    def _auto_checkpoint(self, node_name: str) -> Optional[str]:
        """Create automatic checkpoint after successful node execution"""
        if not self.auto_checkpoint_enabled:
            return None
        
        self._auto_checkpoint_counter += 1
        
        # Only checkpoint every N successful nodes
        if self._auto_checkpoint_counter % self.auto_checkpoint_interval != 0:
            return None
        
        checkpoint_id = f"auto_{node_name}_{self.execution_counter}_{int(time.time())}"
        return self._create_checkpoint(checkpoint_id, checkpoint_type="auto")
    
    def _create_checkpoint(self, checkpoint_id: str, checkpoint_type: str = "manual") -> str:
        """Create a checkpoint with workflow state and controller data"""
        try:
            # Ensure checkpoint directory exists
            self.checkpoint_dir.mkdir(exist_ok=True)
            
            # Create checkpoint data
            checkpoint_data = {
                "checkpoint_id": checkpoint_id,
                "checkpoint_type": checkpoint_type,
                "timestamp": datetime.now().isoformat(),
                "workflow_name": self.workflow.name,
                "workflow_id": self.workflow.workflow_id,
                
                # Workflow serialization using Plan 15 JSON
                "workflow_json": self.workflow.to_json(),
                
                # Workflow state (separate from JSON structure)
                "workflow_state": {
                    "state_dict": self.workflow.state.state.copy(),
                    "instance_name": self.workflow.state.instance_name,
                    "executions": len(self.workflow.state.executions)
                },
                
                # Controller state
                "controller_state": {
                    "execution_counter": self.execution_counter,
                    "execution_position": self.execution_position,
                    "total_execution_time": self.total_execution_time,
                    "node_execution_counts": self.node_execution_counts.copy(),
                    "auto_checkpoint_counter": self._auto_checkpoint_counter,
                    "current_execution_path": self.current_execution_path.copy(),
                    "execution_depth": self.execution_depth
                },
                
                # Execution history summary (last 10 entries for space efficiency)
                "recent_execution_history": [
                    {
                        "node_name": entry.node_name,
                        "effective_name": entry.effective_name,
                        "execution_id": entry.execution_id,
                        "duration": entry.duration,
                        "status": entry.status,
                        "timestamp": entry.start_time.isoformat() if entry.start_time else None
                    }
                    for entry in self.execution_history.get_recent(10)
                ]
            }
            
            # Save checkpoint file
            checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            # Checkpoint created successfully
            
            return checkpoint_id
            
        except Exception as e:
            return None
    
    def save(self, checkpoint_name: str = None) -> str:
        """Create manual checkpoint with optional custom name"""
        if checkpoint_name is None:
            checkpoint_name = f"manual_{int(time.time())}"
        
        # Sanitize checkpoint name for filename
        safe_name = "".join(c for c in checkpoint_name if c.isalnum() or c in ("_", "-", "."))
        checkpoint_id = f"manual_{safe_name}_{self.execution_counter}_{int(time.time())}"
        
        return self._create_checkpoint(checkpoint_id, checkpoint_type="manual")
    
    def load(self, checkpoint_id: str) -> 'Sequence':
        """Load workflow from checkpoint and return restored workflow"""
        try:
            # Find checkpoint file
            checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
            if not checkpoint_file.exists():
                raise FileNotFoundError(f"Checkpoint {checkpoint_id} not found")
            
            # Load checkpoint data
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            # Restore workflow using Plan 15 JSON serialization
            restored_workflow = Sequence.from_json(checkpoint_data["workflow_json"])
            
            # Restore workflow state
            if "workflow_state" in checkpoint_data:
                workflow_state = checkpoint_data["workflow_state"]
                restored_workflow.state.state.update(workflow_state["state_dict"])
                restored_workflow.state.instance_name = workflow_state["instance_name"]
            
            # Restore controller state
            controller_state = checkpoint_data["controller_state"]
            restored_workflow.controller.execution_counter = controller_state["execution_counter"]
            restored_workflow.controller.execution_position = controller_state["execution_position"]
            restored_workflow.controller.total_execution_time = controller_state["total_execution_time"]
            restored_workflow.controller.node_execution_counts = controller_state["node_execution_counts"]
            restored_workflow.controller._auto_checkpoint_counter = controller_state["auto_checkpoint_counter"]
            restored_workflow.controller.current_execution_path = controller_state["current_execution_path"]
            restored_workflow.controller.execution_depth = controller_state["execution_depth"]
            
            
            return restored_workflow
            
        except Exception as e:
            raise
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List available checkpoints with metadata"""
        if not self.checkpoint_dir.exists():
            return []
        
        checkpoints = []
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                with open(checkpoint_file, 'r') as f:
                    data = json.load(f)
                
                checkpoints.append({
                    "checkpoint_id": data["checkpoint_id"],
                    "checkpoint_type": data["checkpoint_type"],
                    "timestamp": data["timestamp"],
                    "workflow_name": data["workflow_name"],
                    "file_path": str(checkpoint_file),
                    "file_size": checkpoint_file.stat().st_size
                })
            except (json.JSONDecodeError, KeyError, OSError) as e:
                pass  # Skip corrupted files
        
        # Sort by timestamp (newest first)
        checkpoints.sort(key=lambda x: x["timestamp"], reverse=True)
        return checkpoints
    
    def cleanup_old_checkpoints(self, days: int = None) -> int:
        """Remove checkpoints older than specified days (default: retention_days)"""
        if days is None:
            days = self.checkpoint_retention_days
        
        if not self.checkpoint_dir.exists():
            return 0
        
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(days=days)
        removed_count = 0
        
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                # Check file modification time
                file_mtime = datetime.fromtimestamp(checkpoint_file.stat().st_mtime)
                if file_mtime < cutoff_time:
                    checkpoint_file.unlink()
                    removed_count += 1
            except OSError as e:
                pass
        return removed_count
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a specific checkpoint"""
        try:
            checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
            if checkpoint_file.exists():
                checkpoint_file.unlink()
                return True
            else:
                return False
        except OSError as e:
            return False
    
    def subscribe(self, callback) -> str:
        """Subscribe to workflow events with clean callback API
        
        Args:
            callback: Function that accepts (event_type: str, event_data: dict)
            
        Returns:
            Subscription ID for unsubscribing
        """
        self._subscription_counter += 1
        subscription_id = f"sub_{self._subscription_counter}"
        
        self._callback_subscribers.append({
            'id': subscription_id,
            'callback': callback
        })
        
        return subscription_id
    
    def _register_hook(self, hook_type: str, hook_func, target: str = None) -> None:
        """Register a hook function for the specified hook type and optional target
        
        Args:
            hook_type: Type of hook (pre_execution, post_execution, etc.)
            hook_func: Hook function to register
            target: Optional target name (node/sequence name). None = all targets
        """
        if hook_type not in self._hook_registry:
            raise ValueError(f"Invalid hook type: {hook_type}. Valid types: {list(self._hook_registry.keys())}")
        
        # Store as tuple: (hook_func, target_name) - keeping it simple for now
        # FUTURE: Use weak references to prevent memory leaks in long-running workflows
        self._hook_registry[hook_type].append((hook_func, target))
    
    def _cleanup_hook_reference(self, dead_ref):
        """Clean up dead weak references from hook registry"""
        for hook_type, hooks in self._hook_registry.items():
            self._hook_registry[hook_type] = [
                (hook_ref, target) for hook_ref, target in hooks 
                if hook_ref is not dead_ref
            ]
    
    def _unregister_hook(self, hook_type: str, hook_func) -> bool:
        """Unregister a hook function from the specified hook type
        
        Args:
            hook_type: Type of hook (pre_execution, post_execution, etc.)
            hook_func: Hook function to unregister
            
        Returns:
            True if hook was found and removed, False otherwise
        """
        if hook_type not in self._hook_registry:
            raise ValueError(f"Invalid hook type: {hook_type}. Valid types: {list(self._hook_registry.keys())}")
        
        # Find and remove all instances of this hook function (regardless of target)
        original_count = len(self._hook_registry[hook_type])
        self._hook_registry[hook_type] = [
            (func, target) for func, target in self._hook_registry[hook_type] 
            if func != hook_func
        ]
        new_count = len(self._hook_registry[hook_type])
        
        return new_count < original_count  # True if any were removed
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from workflow events using subscription ID
        
        Args:
            subscription_id: ID returned from subscribe() method
            
        Returns:
            True if subscription was found and removed, False otherwise
        """
        original_count = len(self._callback_subscribers)
        
        # Remove subscription with matching ID
        self._callback_subscribers = [
            sub for sub in self._callback_subscribers 
            if sub['id'] != subscription_id
        ]
        
        new_count = len(self._callback_subscribers)
        return new_count < original_count  # True if any were removed
    
    def _create_hook_decorator(self, hook_type: str):
        """Create a hook decorator for the specified hook type
        
        Args:
            hook_type: Type of hook (pre_execution, post_execution, etc.)
            
        Returns:
            Decorator function that can be called with or without arguments
        """
        def decorator(*args, **kwargs):
            # Case 1: @seq.hooks.pre_execution (no arguments) - function passed directly
            if len(args) == 1 and callable(args[0]) and not self._is_target_parameter(args[0]):
                hook_func = args[0]
                # Register hook with no target (global)
                self._register_hook(hook_type, hook_func, target=None)
                return hook_func
            
            # Case 2: @seq.hooks.pre_execution("node_name") or @seq.hooks.on_error(ValueError)
            elif len(args) >= 1:
                target = args[0]
                
                # Handle combined targeting: @seq.hooks.on_error(ValueError, "node_name")
                if len(args) == 2:
                    target = (args[0], args[1])
                
                def inner_decorator(hook_func):
                    # Register hook with specific target (string, exception class, or tuple)
                    self._register_hook(hook_type, hook_func, target=target)
                    return hook_func
                return inner_decorator
            
            else:
                # Invalid usage
                raise ValueError(f"Invalid hook decorator usage for {hook_type}")
        
        return decorator
    
    def _is_target_parameter(self, arg) -> bool:
        """Check if an argument is a target parameter (not a hook function)"""
        # String targets
        if isinstance(arg, str):
            return True
        # Exception class targets
        if isinstance(arg, type) and issubclass(arg, Exception):
            return True
        # Tuple targets
        if isinstance(arg, tuple):
            return True
        # Otherwise, assume it's a function
        return False
    
    async def _execute_single_hook(self, hook_func, *args):
        """Execute a single hook function with async support
        
        Args:
            hook_func: Hook function to execute
            *args: Arguments to pass to the hook function
        """
        import asyncio
        
        if asyncio.iscoroutinefunction(hook_func):
            # Async hook
            await hook_func(*args)
        else:
            # Sync hook
            hook_func(*args)
    
    async def _execute_hooks(self, hook_type: str, context: dict = None) -> None:
        """Execute all registered hooks of the specified type
        
        Args:
            hook_type: Type of hook to execute (pre_execution, post_execution, etc.)
            context: Context data containing node, sequence, result, error, etc.
        """
        if hook_type not in self._hook_registry:
            return
        
        context = context or {}
        hooks = self._hook_registry[hook_type]
        
        # Filter hooks based on targeting and exception type
        target_name = context.get('target_name')
        error = context.get('error')
        filtered_hooks = self._get_matching_hooks(hooks, target_name, error)
        
        for hook_func, target in filtered_hooks:
            try:
                # Hook function is stored directly for now
                
                # Execute hook with appropriate arguments based on hook type
                if hook_type in ['pre_execution', 'post_execution', 'on_error']:
                    # Node-level hooks
                    node = context.get('node')
                    if hook_type == 'pre_execution':
                        await self._execute_single_hook(hook_func, node)
                    elif hook_type == 'post_execution':
                        result = context.get('result')
                        await self._execute_single_hook(hook_func, node, result)
                    elif hook_type == 'on_error':
                        error = context.get('error')
                        await self._execute_single_hook(hook_func, error, node)
                        
                elif hook_type in ['pre_sequence', 'post_sequence', 'on_sequence_error']:
                    # Sequence-level hooks
                    sequence = context.get('sequence')
                    if hook_type == 'pre_sequence':
                        await self._execute_single_hook(hook_func, sequence)
                    elif hook_type == 'post_sequence':
                        result = context.get('result')
                        await self._execute_single_hook(hook_func, sequence, result)
                    elif hook_type == 'on_sequence_error':
                        error = context.get('error')
                        await self._execute_single_hook(hook_func, error, sequence)
                        
            except Exception as e:
                # Hook failures should not break workflow execution
                func_name = getattr(hook_func, '__name__', 'unknown') if 'hook_func' in locals() and hook_func else 'dead_reference'
                print(f"Hook execution failed: {func_name} ({hook_type}): {e}")
        
        # CALLBACK BRIDGE FIX: Fire callback events after hook execution
        await self._notify_callback_subscribers(hook_type, context)
    
    def _execute_hooks_sync(self, hook_type: str, context: dict = None) -> None:
        """Execute hooks synchronously for sync workflows
        
        Args:
            hook_type: Type of hook to execute (pre_execution, post_execution, etc.)
            context: Context data containing node, sequence, result, error, etc.
        """
        if hook_type not in self._hook_registry:
            return
            
        context = context or {}
        hooks = self._hook_registry[hook_type]
        
        # Filter hooks based on targeting and exception type
        target_name = context.get('target_name')
        error = context.get('error')
        filtered_hooks = self._get_matching_hooks(hooks, target_name, error)
        
        for hook_func, target in filtered_hooks:
            try:
                # Execute hook with appropriate arguments based on hook type
                if hook_type in ['pre_execution', 'post_execution', 'on_error']:
                    # Node-level hooks
                    node = context.get('node')
                    if hook_func:
                        hook_func(node)
                elif hook_type in ['pre_sequence', 'post_sequence']:
                    # Sequence-level hooks
                    sequence = context.get('sequence')
                    result = context.get('result')
                    if hook_func:
                        hook_func(sequence, result)
                else:
                    # Generic context hooks
                    if hook_func:
                        hook_func(context)
            except Exception as e:
                # Hook failures should not break workflow execution
                func_name = getattr(hook_func, '__name__', 'unknown') if hook_func else 'dead_reference'
                print(f"Sync hook execution failed: {func_name} ({hook_type}): {e}")
    
    async def _notify_callback_subscribers(self, hook_type: str, context: dict):
        """Convert hook execution to callback events and notify subscribers
        
        Args:
            hook_type: The type of hook that was executed
            context: Hook execution context
        """
        # Convert hook event to callback event format
        event_data = self._convert_hook_to_callback_event(hook_type, context)
        
        # Notify all callback subscribers
        for subscriber in self._callback_subscribers:
            try:
                callback_func = subscriber['callback']
                if asyncio.iscoroutinefunction(callback_func):
                    await callback_func(hook_type, event_data)
                else:
                    callback_func(hook_type, event_data)
            except Exception as e:
                print(f"Callback subscriber failed: {e}")
    
    def _convert_hook_to_callback_event(self, hook_type: str, context: dict) -> dict:
        """Convert hook execution context to callback event data
        
        Args:
            hook_type: Type of hook executed
            context: Hook execution context
            
        Returns:
            Event data dictionary for callback subscribers
        """
        event_data = {
            'timestamp': time.time(),
        }
        
        if hook_type in ['pre_sequence', 'post_sequence', 'on_sequence_error']:
            # Sequence-level events
            sequence = context.get('sequence')
            if sequence:
                event_data['sequence_name'] = sequence.name
                event_data['sequence_id'] = getattr(sequence, 'workflow_id', 'unknown')
                
            if hook_type == 'post_sequence':
                event_data['result'] = context.get('result')
                # Calculate duration if start time available
                if hasattr(sequence, '_monitoring_start_time'):
                    event_data['duration'] = time.time() - sequence._monitoring_start_time
                    
            elif hook_type == 'on_sequence_error':
                error = context.get('error')
                if error:
                    event_data['error'] = str(error)
                    event_data['error_type'] = type(error).__name__
                    
        elif hook_type in ['pre_execution', 'post_execution', 'on_error']:
            # Node-level events
            node = context.get('node')
            if node:
                event_data['node_name'] = getattr(node, 'name', 'unknown')
                event_data['node_guid'] = getattr(node, 'guid', 'unknown')
                
            if hook_type == 'post_execution':
                event_data['result'] = context.get('result')
                event_data['output_value'] = context.get('result')
                
            elif hook_type == 'on_error':
                error = context.get('error')
                if error:
                    event_data['error'] = str(error)
                    event_data['error_type'] = type(error).__name__
        
        return event_data
    
    def _get_matching_hooks(self, hooks: list, target_name: str = None, error: Exception = None) -> list:
        """Filter hooks based on targeting logic and exception type filtering
        
        Args:
            hooks: List of (hook_ref, target) tuples (with weak references)
            target_name: Current target name (node/sequence name)
            error: Exception instance for error hook filtering
            
        Returns:
            Filtered list of hooks that should execute for this target
        """
        matching_hooks = []
        
        # Standard filtering - no complex exception handling for now
        for hook_func, hook_target in hooks:
            if self._hook_matches_criteria(hook_target, target_name, error):
                matching_hooks.append((hook_func, hook_target))
        
        return matching_hooks
    
    def _calculate_exception_specificity(self, hook_exception_class: type, actual_error: Exception) -> int:
        """Calculate exception specificity for most-specific-first matching
        
        Returns:
            -1 if no match, 0+ for match depth (0 = exact match, higher = more general)
        """
        if not isinstance(actual_error, hook_exception_class):
            return -1
            
        # Calculate inheritance distance (0 = exact match, higher = more general)
        error_class = type(actual_error)
        if error_class == hook_exception_class:
            return 0
            
        # Find distance in inheritance hierarchy
        distance = 0
        for base_class in error_class.__mro__[1:]:  # Skip self
            distance += 1
            if base_class == hook_exception_class:
                return distance
                
        return -1  # Not in hierarchy
    
    def _hook_matches_criteria(self, hook_target, target_name: str = None, error: Exception = None) -> bool:
        """Check if a hook matches the current execution criteria
        
        Args:
            hook_target: Hook target (can be None, string, exception class, or tuple)
            target_name: Current target name
            error: Current exception (for error hooks)
            
        Returns:
            True if hook should execute, False otherwise
        """
        # Handle different hook target types
        if hook_target is None:
            # Global hook - always matches
            return True
            
        elif isinstance(hook_target, str):
            # String target - match by name
            return hook_target == target_name
            
        elif isinstance(hook_target, type) and issubclass(hook_target, Exception):
            # Exception class target - match by exception type
            return error is not None and isinstance(error, hook_target)
            
        elif isinstance(hook_target, tuple) and len(hook_target) == 2:
            # Combined target: (exception_class, target_name)
            exception_class, target_str = hook_target
            exception_matches = error is not None and isinstance(error, exception_class)
            target_matches = target_str == target_name
            return exception_matches and target_matches
            
        else:
            # Unknown target type - don't match
            return False


class HooksProxy:
    """Clean facade for hook registration: seq.hooks.pre_execution"""
    
    def __init__(self, controller: 'WorkflowController'):
        self._controller = controller
    
    @property
    def pre_execution(self):
        """@seq.hooks.pre_execution or @seq.hooks.pre_execution("NodeName")"""
        return self._controller._create_hook_decorator('pre_execution')
    
    @property
    def post_execution(self):
        """@seq.hooks.post_execution or @seq.hooks.post_execution("NodeName")"""
        return self._controller._create_hook_decorator('post_execution')
    
    @property
    def on_error(self):
        """@seq.hooks.on_error or @seq.hooks.on_error("NodeName")"""
        return self._controller._create_hook_decorator('on_error')
    
    @property
    def pre_sequence(self):
        """@seq.hooks.pre_sequence or @seq.hooks.pre_sequence("SequenceName")"""
        return self._controller._create_hook_decorator('pre_sequence')
    
    @property
    def post_sequence(self):
        """@seq.hooks.post_sequence or @seq.hooks.post_sequence("SequenceName")"""
        return self._controller._create_hook_decorator('post_sequence')
    
    @property
    def on_sequence_error(self):
        """@seq.hooks.on_sequence_error or @seq.hooks.on_sequence_error("SequenceName")"""
        return self._controller._create_hook_decorator('on_sequence_error')


class Sequence(Node):  # Inherits from Node for composability
    """Composable workflow sequence with JSON serialization for Cerebrum"""

    def __init__(self, chain_result: BaseNode, name: str = None, max_steps: int = 1000):
        # Generate unique name if not provided
        desired_name = name or f"Sequence_{uuid.uuid4().hex[:8]}"
        super().__init__(label=desired_name)
        # Override the name set by Node.__init__ to keep it simple
        self.name = desired_name
        
        # Initialize SharedState with our name
        self.state = SharedState(instance_name=self.name)
        
        # Set workflow reference for controller access
        self.state.workflow = self
        
        # Workflow configuration
        self.max_steps = max_steps
        self.workflow_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        
        # Build the workflow chain
        self.start = self._build_chain(chain_result)
        
        # Create controller for external workflow control
        self.controller = WorkflowController(self)
        
        # Create hooks proxy for clean hook API
        self._hooks_proxy = None
    
    def enable_loop_control(self, max_iterations: int = 10, max_nested_loops: int = 5):
        """Enable advanced loop control with specified limits"""
        self.state.max_loop_iterations = max_iterations
        self.state.max_nested_loops = max_nested_loops
        self.state.loop_detection_enabled = True
        return self
    
    @property
    def hooks(self) -> HooksProxy:
        """Access to hook registration: seq.hooks.pre_execution"""
        if self._hooks_proxy is None:
            self._hooks_proxy = HooksProxy(self.controller)
        return self._hooks_proxy

    def _build_chain(self, chain_result: BaseNode) -> BaseNode:
        """Build the workflow chain from the input"""
        if isinstance(chain_result, NodeType):
            start_node = chain_result.node_instance
        elif hasattr(chain_result, '_first_node'):
            start_node = chain_result._first_node
            if isinstance(start_node, NodeType):
                start_node = start_node.node_instance
        else:
            start_node = chain_result
        
        return start_node

    def execute(self, *args, **kwargs):
        """Execute workflow synchronously - required for Node inheritance"""
        return asyncio.run(self.async_execute(*args, **kwargs))

    async def async_execute(self, *args, **kwargs):
        """Execute workflow asynchronously with controller support"""
        # NEW: Set up workflow state context for Plan 18
        with WorkflowStateContext(self.state):
            try:
                self.controller._state = 'running'
                
                # Execute pre_sequence hooks
                await self.controller._execute_hooks('pre_sequence', {
                    'sequence': self,
                    'target_name': self.name
                })
                
                # Notify start
                if hasattr(self.state, '_notify_state_change'):
                    self.state._notify_state_change('workflow_started', self.name, {
                        'timestamp': time.time(),
                        'workflow_id': self.workflow_id
                    })
                
                # Handle input data and set initial_input helper property
                input_data = None
                if self.state and hasattr(self.state, 'executions') and self.state.executions:
                    # If we're part of a larger workflow, get previous result
                    input_data = self.state[-1]
                elif args:
                    # Direct execution with arguments
                    input_data = args[0]
                    # NEW: Set the enhanced initial_input property
                    self.state.initial_input = input_data
                    # Also set the legacy NodeOutput for backward compatibility
                    if hasattr(self.state, '_legacy_initial_input'):
                        self.state._legacy_initial_input.execute = input_data
                    self.state.set_previous_output(input_data)
                
                # Execute sequence with controller support
                result = await self._run_sequence_async(*args, **kwargs)
                
                self.controller._state = 'completed'
                
                # Execute post_sequence hooks
                await self.controller._execute_hooks('post_sequence', {
                    'sequence': self,
                    'result': result,
                    'target_name': self.name
                })
                
                # Store result by node name (for when used as a node)
                if hasattr(self.state, '__setitem__'):
                    self.state[self.name] = result
                
                # Notify completion
                if hasattr(self.state, '_notify_state_change'):
                    self.state._notify_state_change('workflow_completed', self.name, {
                        'timestamp': time.time(),
                        'result': str(result)[:100] if result else None
                    })
                
                return result
                
            except WorkflowStoppedException:
                # Workflow was stopped via controller
                return None
            except Exception as e:
                self.controller._state = 'error'
                
                # Execute on_sequence_error hooks
                await self.controller._execute_hooks('on_sequence_error', {
                    'sequence': self,
                    'error': e,
                    'target_name': self.name
                })
                
                # Notify error
                if hasattr(self.state, '_notify_state_change'):
                    self.state._notify_state_change('workflow_error', self.name, {
                        'timestamp': time.time(),
                        'error': str(e)
                    })
                raise
            finally:
                # Clear the generic state store after workflow execution
                if hasattr(self.state, 'clear_store'):
                    self.state.clear_store()

    async def _run_sequence_async(self, *args, **kwargs):
        """Run sequence with controller checks and execution tracking"""
        current_node = self.start
        step_count = 0
        executed_nodes = set()
        result = None
        
        while current_node is not None and step_count < self.max_steps:
            # Update execution location
            node_name = getattr(current_node, 'name', str(current_node))
            self.controller.current_execution_path.append(node_name)
            
            # Notify observers of current execution location
            if hasattr(self.state, '_notify_state_change'):
                self.state._notify_state_change('execution_location_update', self.name, {
                    'current_node': node_name,
                    'execution_path': self.controller.current_execution_path.copy(),
                    'depth': self.controller.execution_depth
                })
            
            # Check controller state before execution
            await self.controller._check_control_state()
            
            # Check for infinite loops
            if current_node in executed_nodes and not isinstance(current_node, Decision):
                pass  # Would normally check for loops here
            
            # Set state for the node
            current_node.state = self.state
            
            # Execute current node based on type
            try:
                # ★ START EXECUTION TRACKING - Proper execution lifecycle
                input_value = self.state.get_previous_output()
                execution_entry = self.controller.start_node_execution(current_node, input_value)
                
                # ✅ PRE-EXECUTION HOOKS - Execute before node execution
                await self.controller._execute_hooks('pre_execution', {
                    'node': current_node,
                    'target_name': node_name,
                    'execution_path': self.controller.current_execution_path.copy() if self.controller.current_execution_path else [],
                    'depth': self.controller.execution_depth,
                    'args': args,
                    'kwargs': kwargs
                })
                
                if isinstance(current_node, Sequence):
                    # Entering nested sequence
                    self.controller.execution_depth += 1
                    result = await current_node.async_execute(*args, **kwargs)
                    self.controller.execution_depth -= 1
                    # Store nested sequence result by name in parent state
                    if hasattr(self.state, '__setitem__'):
                        self.state[current_node.name] = result
                elif isinstance(current_node, Decision):
                    # Handle decision nodes with special data flow handling
                    # Pass the current result (from previous node) as decision criteria
                    result = self._handle_decision_node(current_node, result, *args, **kwargs)
                    
                    # For decision nodes, we need to track the correct data for the next node
                    # The result should be the data that flows to the selected branch, not the decision criteria
                    # We'll track this in the execution history so the next node gets the right data
                    pass  # Continue with normal tracking but with the corrected result
                elif hasattr(current_node, 'async_execute'):
                    # Async node
                    result = await current_node.async_execute(*args, **kwargs)
                else:
                    # Sync node - use run() method for proper execution hooks
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, current_node.run)
                
                # ✅ POST-EXECUTION HOOKS - Execute after successful node execution
                await self.controller._execute_hooks('post_execution', {
                    'node': current_node,
                    'result': result,
                    'target_name': node_name,
                    'execution_path': self.controller.current_execution_path.copy() if self.controller.current_execution_path else [],
                    'depth': self.controller.execution_depth
                })
                
                # ★ COMPLETE EXECUTION TRACKING - Records the result properly
                self.controller.complete_node_execution(execution_entry, result)
                
                # Track execution
                execution = NodeOutput(name=node_name)
                execution.execute = result
                self.state.executions.append(execution)
                self.state.execution_sequence.append(current_node)
                executed_nodes.add(current_node)
                
                # Store node result by name in state for indexing
                if hasattr(current_node, 'name') and current_node.name and hasattr(self.state, '__setitem__'):
                    self.state[current_node.name] = result
                
            except Exception as e:
                # ★ RECORD EXECUTION ERROR - Proper error tracking
                if 'execution_entry' in locals():
                    self.controller.error_node_execution(execution_entry, e)
                
                # ✅ ERROR EXECUTION HOOKS - Execute on node failure
                try:
                    await self.controller._execute_hooks('on_error', {
                        'node': current_node,
                        'error': e,
                        'target_name': node_name,
                        'execution_path': self.controller.current_execution_path.copy() if self.controller.current_execution_path else [],
                        'depth': self.controller.execution_depth
                    })
                except Exception as hook_error:
                    pass
                raise
            
            # Update execution location (node completed)
            if self.controller.current_execution_path:
                self.controller.current_execution_path.pop()
            
            # Move to next node and update args to pass result from previous node
            current_node = current_node.next_node
            step_count += 1
            
            # Update args to pass the result from this node to the next node
            # The first execution uses the original args, subsequent nodes get the previous result
            if current_node is not None and result is not None:
                args = (result,)  # Pass previous node's result as input to next node
        
        if step_count >= self.max_steps:
            raise RuntimeError(f"Sequence execution exceeded maximum steps ({self.max_steps}). Possible infinite loop.")
        
        return result

    def get_pre_decision_data(self):
        """Get data from node before the decision-making node
        
        Helper function to reliably get pre-decision data from controller execution history.
        Falls back to current decision criteria if history is unavailable.
        """
        if (self.state.workflow and 
            hasattr(self.state.workflow, 'controller') and
            self.state.workflow.controller.execution_history):
            
            history = self.state.workflow.controller.execution_history
            completed_entries = [entry for entry in history.entries 
                               if entry.output_value is not None]
            
            if len(completed_entries) >= 2:
                return completed_entries[-2].output_value
        
        # Fallback: use current criteria
        return self.state.get_previous_output() if hasattr(self.state, 'get_previous_output') else None

    def _handle_decision_node(self, decision_node: Decision, previous_result, *args, **kwargs):
        """Handle decision node execution with proper data flow for arbitrary length chains"""
        
        # The decision criteria is the result from the immediately previous node
        decision_criteria = previous_result
        
        # For correct_input_data, we want the data that should flow to the selected branch
        # This should be the data from BEFORE the decision-making node
        correct_input_data = self.get_pre_decision_data()
        
        # 2. Handle iteration counting for loops
        if not hasattr(decision_node, '_iteration_count'):
            decision_node._iteration_count = 0
        decision_node._iteration_count += 1
        
        # 3. Check max_iter limits  
        if hasattr(decision_node, 'max_iter') and decision_node.max_iter and decision_node._iteration_count > decision_node.max_iter:
            # Max iterations exceeded - return current data and stop
            return correct_input_data
        
        # 4. Find matching branch
        selected_branch = None
        for map_item in decision_node.maps:
            if map_item.condition == decision_criteria:
                selected_branch = map_item.node
                break
        
        if selected_branch is None:
            # No match found
            return correct_input_data
        
        # 5. Handle different branch types
        # Note: Sequence is already available in this module's scope
        
        if isinstance(selected_branch, Sequence):
            # Case A: Branch is nested sequence
            return selected_branch.execute(correct_input_data)
        else:
            # Case B: Branch is node chain - set up for sequence continuation
            # Instead of executing the branch ourselves, set up the decision node's next_node
            # so the main sequence execution loop will continue with the selected branch
            
            # Extract actual node from NodeType wrapper if needed
            if isinstance(selected_branch, NodeType):
                actual_node = selected_branch.node_instance
            else:
                actual_node = selected_branch
            
            # Find the mapper for this branch to get complete chain info
            selected_mapper = None
            for map_item in decision_node.maps:
                if map_item.condition == decision_criteria:
                    selected_mapper = map_item
                    break
            
            # Restore the complete chain if it was broken during decision construction
            if (selected_mapper and hasattr(selected_mapper, '_complete_chain') and 
                len(selected_mapper._complete_chain) > 1):
                
                chain = selected_mapper._complete_chain
                
                # Rebuild the complete chain linkage
                for i in range(len(chain) - 1):
                    current_node = chain[i]
                    next_node = chain[i + 1]
                    if hasattr(current_node, 'next_node'):
                        current_node.next_node = next_node
            
            # Legacy fallback for older chain restoration
            elif (hasattr(actual_node, 'next_node') and getattr(actual_node, 'next_node', None) is None and
                  selected_mapper and hasattr(selected_mapper, '_chain_end_node')):
                chain_end = getattr(selected_mapper, '_chain_end_node', None)
                if chain_end and chain_end != actual_node:
                    actual_node.next_node = chain_end
            
            # Set the decision node's next_node to the selected branch
            decision_node.next_node = actual_node
            
            # Log chain linkage for debugging
            if hasattr(actual_node, 'next_node'):
                pass
            
            # Update state to ensure the selected branch gets the correct input data
            if hasattr(self.state, 'set_previous_output'):
                self.state.set_previous_output(correct_input_data)
            
            # Return the correct input data so it flows to the next node
            return correct_input_data

    def get_schema(self, format: str = "mermaid", mode: str = "overview") -> str:
        """Generate a schema representation of the workflow pipeline
        
        Args:
            format: The schema format ("mermaid", "json", "text")
            mode: The detail mode for mermaid format ("overview", "full")
                  - "overview": High-level view showing sequences as single blocks
                  - "full": Detailed view expanding all nested sequences and nodes
            
        Returns:
            Schema representation as a string
        """
        if format.lower() == "mermaid":
            from .mermaid_renderer import render_mermaid_schema
            return render_mermaid_schema(self, mode=mode)
        elif format.lower() == "json":
            return json.dumps(self.to_json(), indent=2)
        elif format.lower() == "text":
            return self._generate_text_schema()
        else:
            raise ValueError(f"Unsupported schema format: {format}. Supported formats: mermaid, json, text")
    
    def _generate_text_schema(self) -> str:
        """Generate a text-based schema representation"""
        if not self.start:
            return f"Empty Sequence: {self.name}"
        
        lines = [f"Workflow Schema: {self.name}"]
        lines.append("=" * (20 + len(self.name)))
        lines.append("")
        
        visited = set()
        
        def traverse_text(node, depth=0, prefix=""):
            # Phase 4: Use GUID for text serialization consistency
            if not node or node.guid in visited:
                return
            visited.add(node.guid)
            
            indent = "  " * depth
            node_name = getattr(node, 'name', str(node))
            
            # Node type indicators
            if isinstance(node, Sequence):
                icon = "🔄"
                node_type = "Sequence"
            elif hasattr(node, 'parallel_nodes'):
                icon = "⚡"
                node_type = "Parallel"
            elif isinstance(node, Decision):
                icon = "❓"
                node_type = "Decision"
            elif hasattr(node, 'agent'):
                icon = "🤖"
                node_type = "Agent"
            else:
                icon = "📋"
                node_type = "Node"
            
            lines.append(f"{indent}{prefix}{icon} {node_name} ({node_type})")
            
            # Handle parallel nodes
            if hasattr(node, 'parallel_nodes'):
                for i, child in enumerate(node.parallel_nodes):
                    child_prefix = f"├─ " if i < len(node.parallel_nodes) - 1 else "└─ "
                    traverse_text(child, depth + 1, child_prefix)
            
            # Handle decision nodes
            elif isinstance(node, Decision):
                for i, map_item in enumerate(node.maps):
                    target_node = map_item.node
                    if isinstance(target_node, NodeType):
                        target_node = target_node.node_instance
                    condition = str(map_item.condition)
                    branch_prefix = f"├─ [{condition}] " if i < len(node.maps) - 1 else f"└─ [{condition}] "
                    traverse_text(target_node, depth + 1, branch_prefix)
            
            # Handle nested sequences
            elif isinstance(node, Sequence) and node.start:
                traverse_text(node.start, depth + 1, "└─ ")
            
            # Continue with next node
            if hasattr(node, 'next_node') and node.next_node:
                traverse_text(node.next_node, depth, "")
        
        traverse_text(self.start)
        
        # Add metadata
        lines.append("")
        lines.append("Metadata:")
        lines.append(f"  - Workflow ID: {self.workflow_id}")
        lines.append(f"  - Created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"  - Max Steps: {self.max_steps}")
        lines.append(f"  - Controller State: {self.controller.state}")
        
        return "\n".join(lines)

    # Legacy compatibility methods
    def run(self, *args, **kwargs):
        """Legacy run method for backward compatibility"""
        return self.execute(*args, **kwargs)

    async def run_async(self, *args, **kwargs):
        """Legacy async run method for backward compatibility"""
        return await self.async_execute(*args, **kwargs)

    def __call__(self, *args, reset_state=True, **kwargs):
        """Legacy callable interface for backward compatibility"""
        if reset_state:
            self.state = SharedState(instance_name=self.name)
            self.state.workflow = self
        return self.execute(*args, **kwargs)

    def _run_node(self, node: BaseNode, *args, **kwargs):
        """Legacy _run_node method for compatibility"""
        node.state = self.state
        
        if isinstance(node, Decision):
            return self._handle_decision_node(node, *args, **kwargs)
        
        execution = self.state.set_current(node)
        
        # Plan 16: Lifecycle Simplification - removed before/after_execute calls
        try:
            execute_output = node.execute(*args, **kwargs)
            execution.execute = execute_output
        except (NotImplementedError, AttributeError):
            execute_output = None
        
        self.state.executions.append(execution)
        self.state.execution_sequence.append(node)
        
        return execute_output

    # JSON Serialization for Cerebrum
    def to_json(self) -> Dict[str, Any]:
        """Serialize workflow structure to JSON for Cerebrum visual builder"""
        return {
            'workflow_id': self.workflow_id,
            'name': self.name,
            'type': 'sequence',
            'nodes': self._serialize_nodes(),
            'connections': self._serialize_connections(),
            'metadata': {
                'created_at': self.created_at.isoformat(),
                'version': '1.0',
                'max_steps': self.max_steps,
                'description': getattr(self, 'description', '')
            }
        }

    def _serialize_nodes(self) -> List[Dict[str, Any]]:
        """Serialize all nodes in the workflow"""
        nodes = []
        visited = set()
        position_x = 0
        
        def serialize_node_recursive(node):
            nonlocal position_x
            # Phase 4: Use GUID instead of id(node) for stable, cross-platform serialization
            if node.guid in visited:
                return
            visited.add(node.guid)
            
            node_id = f"node_{node.guid}"
            node_name = getattr(node, 'name', str(node))
            node_data = {
                'id': node_id,
                'name': node_name,
                'type': self._get_node_type(node),
                'position': {'x': position_x, 'y': 100},
                # Phase 4: Add alias information to JSON format
                'guid': node.guid,
                'alias': node.alias_name,
                'canonical_name': node.canonical_name or node.name,
                'effective_name': node.effective_name
            }
            
            # Handle special node types
            if hasattr(node, 'parallel_nodes'):  # ParallelNode
                node_data['type'] = 'parallel'
                # Store child references for connection generation, but don't nest the data
                node_data['children'] = []
                child_position_y = 50  # Offset children vertically
                for i, child in enumerate(node.parallel_nodes):
                    child_data = {
                        'id': f"node_{child.guid}",  # Phase 4: Use GUID for parallel children
                        'name': getattr(child, 'name', str(child)),
                        'type': self._get_node_type(child),
                        # Phase 4: Include alias info for parallel children
                        'guid': child.guid,
                        'alias': child.alias_name,
                        'canonical_name': child.canonical_name or child.name,
                        'effective_name': child.effective_name
                    }
                    node_data['children'].append(child_data)
                    
                    # Add parallel children as separate top-level nodes with proper positioning
                    child_node_data = {
                        'id': f"node_{child.guid}",  # Phase 4: Use GUID for parallel child nodes
                        'name': getattr(child, 'name', str(child)),
                        'type': self._get_node_type(child),
                        'position': {'x': position_x + 100, 'y': child_position_y + (i * 100)},
                        # Phase 4: Include alias info for parallel child nodes
                        'guid': child.guid,
                        'alias': child.alias_name,
                        'canonical_name': child.canonical_name or child.name,
                        'effective_name': child.effective_name
                    }
                    nodes.append(child_node_data)
                    visited.add(child.guid)  # Phase 4: Mark GUID as visited to avoid duplicate processing
                    
            elif isinstance(node, Decision):  # Decision node
                node_data['type'] = 'decision'
                node_data['conditions'] = {}
                for map_item in node.maps:
                    condition_key = str(map_item.condition)
                    target_node = map_item.node
                    if isinstance(target_node, NodeType):
                        target_node = target_node.node_instance
                    node_data['conditions'][condition_key] = {
                        'target_id': f"node_{target_node.guid}",  # Phase 4: GUID for decision targets
                        'target_name': getattr(target_node, 'name', str(target_node))
                    }
                    
            elif hasattr(node, 'agent'):  # AgentNode
                node_data['type'] = 'agent'
                node_data['agent_config'] = {
                    'name': getattr(node, 'node_name', 'unknown'),
                    'run_type': getattr(node, 'run_type', 'call'),
                    'kwargs': getattr(node, 'call_kwargs', {})
                }
                
            elif isinstance(node, Sequence):  # Nested sequence
                node_data['type'] = 'sequence'
                node_data['nested_workflow'] = node.to_json()
            
            nodes.append(node_data)
            position_x += 200
            
            # Continue with next node
            if hasattr(node, 'next_node') and node.next_node:
                serialize_node_recursive(node.next_node)
        
        # Start serialization
        if self.start:
            serialize_node_recursive(self.start)
        
        return nodes

    def _serialize_connections(self) -> List[Dict[str, Any]]:
        """Serialize connections between nodes"""
        connections = []
        visited = set()
        
        def serialize_connections_recursive(node):
            # Phase 4: Use GUID instead of id(node) for stable connections
            if node.guid in visited:
                return
            visited.add(node.guid)
            
            node_id = f"node_{node.guid}"
            
            # Handle different connection types
            if hasattr(node, 'next_node') and node.next_node:
                connection = {
                    'id': f"conn_{node.guid}_{node.next_node.guid}",  # Phase 4: GUID-based connection IDs
                    'from': node_id,
                    'to': f"node_{node.next_node.guid}",  # Phase 4: GUID-based target
                    'type': 'sequence'
                }
                connections.append(connection)
                serialize_connections_recursive(node.next_node)
                
            elif hasattr(node, 'parallel_nodes'):  # Parallel connections
                for child in node.parallel_nodes:
                    connection = {
                        'id': f"conn_{node.guid}_{child.guid}",  # Phase 4: GUID for parallel connections
                        'from': node_id,
                        'to': f"node_{child.guid}",  # Phase 4: GUID for parallel targets
                        'type': 'parallel'
                    }
                    connections.append(connection)
                    
            elif isinstance(node, Decision):  # Decision connections
                for map_item in node.maps:
                    target_node = map_item.node
                    if isinstance(target_node, NodeType):
                        target_node = target_node.node_instance
                    connection = {
                        'id': f"conn_{node.guid}_{target_node.guid}",  # Phase 4: GUID for decision connections
                        'from': node_id,
                        'to': f"node_{target_node.guid}",  # Phase 4: GUID for decision targets
                        'type': 'decision',
                        'condition': str(map_item.condition)
                    }
                    connections.append(connection)
                    serialize_connections_recursive(target_node)
        
        if self.start:
            serialize_connections_recursive(self.start)
        
        return connections

    def _get_node_type(self, node) -> str:
        """Determine node type for serialization"""
        if hasattr(node, 'parallel_nodes'):
            return 'parallel'
        elif isinstance(node, Decision):
            return 'decision'
        elif hasattr(node, 'agent'):
            return 'agent'
        elif isinstance(node, Sequence):
            return 'sequence'
        else:
            return 'node'

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'Sequence':
        """Reconstruct Sequence from JSON for Cerebrum workflow builder"""
        # For now, create a placeholder implementation
        # Full reconstruction would require rebuilding the node graph
        
        name = json_data.get('name', 'Reconstructed')
        workflow_id = json_data.get('workflow_id')
        
        # Create a minimal sequence for now
        # FUTURE: Implement complete workflow state reconstruction from persisted data
        instance = cls(None, name=name)
        instance.workflow_id = workflow_id
        
        return instance

    def __repr__(self):
        return f"Sequence({self.name})"

    def _repr_markdown_(self):
        """Jupyter notebook representation"""
        return f"**Sequence: {self.name}**\n\nWorkflow ID: `{self.workflow_id}`\n\nController State: `{self.controller.state}`"