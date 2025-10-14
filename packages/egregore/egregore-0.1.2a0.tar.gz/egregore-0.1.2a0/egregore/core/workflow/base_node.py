"""
Egregore Workflow Base Node Implementation

This module provides the core workflow node functionality with intelligent 
parameter mapping for the new input-first design pattern.
"""

# Standard library imports
import asyncio
import copy
import inspect
import re
import uuid
import warnings
from abc import ABC, abstractmethod
from collections import deque, OrderedDict
from typing import (
    Optional, Any, List, Tuple, Set, Dict, Callable, Literal, Union, Type,
    get_type_hints, TYPE_CHECKING
)
# Egregore imports

# Initialize logger

# Type checking imports
if TYPE_CHECKING:
    from egregore.core.workflow.state import SharedState

from egregore.core.workflow.state import SharedState, NodeOutput


class NodeRegistry:
    """Central registry for all workflow nodes with GUID-based tracking"""
    
    def __init__(self):
        self.nodes: Dict[str, 'BaseNode'] = {}  # guid -> node
        self.aliases: Dict[str, str] = {}     # alias -> guid  
        self.canonical_map: Dict[str, List[str]] = {}  # canonical_name -> [guids]
        
    def register_node(self, node: 'BaseNode') -> str:
        """Register node and return its GUID"""
        if not node.guid:
            node.guid = str(uuid.uuid4())
            
        self.nodes[node.guid] = node
        
        # Track canonical mappings
        canonical = node.canonical_name or node.name
        if canonical:
            if canonical not in self.canonical_map:
                self.canonical_map[canonical] = []
            self.canonical_map[canonical].append(node.guid)
        
        # Track aliases
        if node.alias_name:
            self.aliases[node.alias_name] = node.guid
            
        return node.guid
    
    def get_node_by_guid(self, guid: str) -> Optional['BaseNode']:
        """Get node by GUID"""
        return self.nodes.get(guid)
    
    def get_nodes_by_canonical(self, canonical_name: str) -> List['BaseNode']:
        """Get all nodes (including aliases) for a canonical component"""
        guids = self.canonical_map.get(canonical_name, [])
        return [self.nodes[guid] for guid in guids if guid in self.nodes]
    
    def resolve_reference(self, node_ref: str) -> Optional['BaseNode']:
        """Resolve node reference (name, alias, or GUID)"""
        # Try alias first
        if node_ref in self.aliases:
            return self.nodes[self.aliases[node_ref]]
        
        # Try GUID
        if node_ref in self.nodes:
            return self.nodes[node_ref]
        
        # Try canonical name (return first match)
        for node in self.nodes.values():
            if node.name == node_ref or node.canonical_name == node_ref:
                return node
                
        return None

# Global registry instance
_global_node_registry = NodeRegistry()

# Legacy dict for backward compatibility
node_registry = {}


def _ensure_node_instance(node):
    """Utility function to ensure we have a node instance, not NodeType
    
    Args:
        node: Either a NodeType object or a Node instance
        
    Returns:
        Node instance ready for execution
        
    Raises:
        TypeError: If node is not a valid executable type
    """
    if isinstance(node, NodeType):
        return node.node_instance
    elif hasattr(node, 'execute') or hasattr(node, 'async_execute'):
        return node
    else:
        raise TypeError(f"Invalid node type: {type(node).__name__}. "
                      f"Expected Node, NodeType, or object with execute/async_execute method.")

    
def get_default_params(func:Callable):
    params = inspect.signature(func).parameters
    return OrderedDict((k, v.default) for k, v in params.items() if v.default is not inspect.Parameter.empty)

class BaseNode:
    """The base class for all nodes in the action graph."""

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", self.__class__.__name__)
        self.next_node = None
        self._first_node: "BaseNode" = self
        # May be set by chaining logic in NodeMapper
        self._prev_shift: Optional["NodeMapper"] = None
        
        # Node identity and registry integration
        self.guid = str(uuid.uuid4())  # Stable, unique identifier
        self.alias_name = None         # Logical alias: "processor_2"
        self.canonical_name = None     # Original component name
        
        # Auto-register with global registry
        _global_node_registry.register_node(self)
    
    def alias(self, alias_name: str) -> 'BaseNode':
        """Create aliased reference for reused nodes
        
        Args:
            alias_name: Name to use for this aliased instance
            
        Returns:
            New BaseNode instance with shared logic but distinct identity
            
        Raises:
            ValueError: If alias name conflicts with existing names
        """
        # Phase 6: Validate alias name conflicts
        if not alias_name or not alias_name.strip():
            raise ValueError("Alias name cannot be empty")
        
        # Check for conflicts with existing aliases
        if alias_name in _global_node_registry.aliases:
            existing_node = _global_node_registry.nodes[_global_node_registry.aliases[alias_name]]
            raise ValueError(f"Alias name '{alias_name}' already exists for node '{existing_node.name}' (GUID: {existing_node.guid[:8]}...)")
        
        # Check for conflicts with canonical node names
        if alias_name in _global_node_registry.canonical_map:
            conflicting_guids = _global_node_registry.canonical_map[alias_name]
            if conflicting_guids:
                existing_node = _global_node_registry.nodes[conflicting_guids[0]]
                raise ValueError(f"Alias name '{alias_name}' conflicts with existing canonical node name (GUID: {existing_node.guid[:8]}...)")
        
        # Check for conflicts with node names in the registry
        for node in _global_node_registry.nodes.values():
            if node.name == alias_name:
                raise ValueError(f"Alias name '{alias_name}' conflicts with existing node name (GUID: {node.guid[:8]}...)")
        
        aliased_node = copy.copy(self)  # Shallow copy
        aliased_node.alias_name = alias_name
        aliased_node.canonical_name = self.name
        aliased_node.guid = str(uuid.uuid4())  # New GUID for new logical instance
        
        # Register the aliased node
        _global_node_registry.register_node(aliased_node)
        
        return aliased_node
    
    @property
    def effective_name(self) -> str:
        """Name used in state management and references"""
        return self.alias_name if self.alias_name else self.name
    
    def set(self, shared_state: SharedState):
        self.state = shared_state

    def __rshift__(self, other: Union["BaseNode", "NodeType"]):
        # Normalize to BaseNode for safe attribute access
        target: BaseNode
        if isinstance(other, NodeType):
            target = other.node_instance
        else:
            target = other
        self.next_node = target
        target._first_node = self._first_node
        if self._prev_shift is not None:
            target._prev_shift = self._prev_shift
        return target

    def __rrshift__(self, other: Any):
        if isinstance(other, bool):
            # Find the first node in the chain starting from self
            first_node = self._get_first_node_in_chain()
            return NodeMapper(other, first_node)
        if isinstance(other, str):
            # Find the first node in the chain starting from self
            first_node = self._get_first_node_in_chain()
            return NodeMapper(other, first_node)
        if isinstance(other, NodeType):
            # Find the first node in the chain starting from self
            first_node = self._get_first_node_in_chain()
            return NodeMapper(other.node_instance, first_node)
    
    def _get_first_node_in_chain(self):
        """Get the first node in a chain when this node is the result of >> operations"""
        # If this node has a _first_node reference, use it
        if hasattr(self, '_first_node') and self._first_node is not None:
            return self._first_node
        # Otherwise, return self (this node is the first in the chain)
        return self

    def run(self):
        # Initialize current state for this node execution
        self.state.set_current(self)
        
        # Start execution tracking if controller is available
        execution_entry = None
        if (
            hasattr(self.state, 'workflow') and self.state.workflow is not None and
            hasattr(self.state.workflow, 'controller') and self.state.workflow.controller is not None
        ):
            input_value = self.state.get_previous_output()
            execution_entry = self.state.workflow.controller.start_node_execution(self, input_value)
        
        try:
            self._execute()
            
            # Complete execution tracking and return result
            output_value = getattr(self.state.current, 'execute', None)
            if execution_entry and (
                hasattr(self.state, 'workflow') and self.state.workflow is not None and
                hasattr(self.state.workflow, 'controller') and self.state.workflow.controller is not None
            ):
                self.state.workflow.controller.complete_node_execution(execution_entry, output_value)
            
            return output_value
                
        except Exception as e:
            # Record execution error
            if execution_entry and (
                hasattr(self.state, 'workflow') and self.state.workflow is not None and
                hasattr(self.state.workflow, 'controller') and self.state.workflow.controller is not None
            ):
                self.state.workflow.controller.error_node_execution(execution_entry, e)
            raise

    def _execute(self):
        # The execute wrapper automatically handles previous_output
        result = self.execute()
        self.state.current.execute = result
        
    # Lifecycle methods removed in Plan 16: Lifecycle Simplification
    # Use separate nodes for setup/cleanup instead

    def execute(self, *args, **kwargs):
        # Import here to avoid circular imports
        from .agent_interceptor import workflow_node_context
        from .agent_discovery import get_agent_registry
        
        # Always execute within discovery context
        with workflow_node_context(self.name):
            try:
                # Notify that node execution is starting
                registry = get_agent_registry()
                registry._notify_observers("node_execution_started", self.name, {
                    "node": self,
                    "args": str(args)[:100] if args else "",
                    "kwargs": {k: str(v)[:50] for k, v in kwargs.items()}
                })
                
                # Call the actual implementation
                result = self._execute_impl(*args, **kwargs)
                
                # Notify completion
                registry._notify_observers("node_execution_completed", self.name, {
                    "node": self,
                    "result": str(result)[:100] if result else None
                })
                
                return result
                
            except Exception as e:
                # Notify error
                get_agent_registry()._notify_observers("node_execution_failed", self.name, {
                    "node": self,
                    "error": str(e)
                })
                raise
    
    def _execute_impl(self, *args, **kwargs):
        raise NotImplementedError(f"Execute is not implemented for {self.name}")

    # Lifecycle methods removed in Plan 16: Lifecycle Simplification
    # Use separate nodes for setup/cleanup instead


class NodeMapper:
    """A node that maps a condition to a node."""
    def __init__(self, condition:Any, node:Union[BaseNode, "NodeType"]):
        self.condition = condition
        self.node: BaseNode = node.node_instance if isinstance(node, NodeType) else node
        # Add this to track the end of a chain starting from this MapNode
        self._chain_end_node: BaseNode = self.node
        # Track the complete chain sequence for restoration
        self._complete_chain: List[BaseNode] = [self.node]

    def __repr__(self):
        return f"CASE ({self.condition} >> {self.node})"

    def __rshift__(self, other: Union["BaseNode", "NodeType"]):
        # Always resolve to BaseNode instances to keep type checker happy
        target: BaseNode = other.node_instance if isinstance(other, NodeType) else other
        end_node: BaseNode = self._chain_end_node
        end_node.next_node = target
        self._chain_end_node = target
        # Track complete chain using BaseNode
        self._complete_chain.append(target)
        target._prev_shift = self
        return self 

    
class Node(BaseNode):
    """Core Node class used to build the action graph."""
    def __init__(self,  label:Optional[str] = None,*args, **kwargs):
        
        if label is not None:
            class_name = self.__class__.__name__ 
            self.name = f"{class_name}({label})"
        else:
            self.name = self.__class__.__name__ 
        kwargs['name'] = self.name
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.name

    # Lifecycle methods removed in Plan 16: Lifecycle Simplification
    # Use separate nodes for setup/cleanup instead
    

class Decision(Node):
    """A node that maps a condition to a node."""
    def __init__(self, *node_map:list[NodeMapper], max_iter: Optional[int] = None):
        # Ensure the input node_map actually contains MapNodes
        valid_maps = [item for item in node_map if isinstance(item, NodeMapper)]
        super().__init__(label="Decision") # Give DecisionT a base name
        self.maps = valid_maps # Directly use the validated MapNodes
        self.max_iter = max_iter  # Per-decision-node execution limit

        # Build name based on the actual conditions received
        conditions_str = ", ".join(str(m.condition) for m in self.maps)
        # Use a more descriptive name format
        self.name = f"Decision({conditions_str if conditions_str else 'NoMaps'})"

    def execute(self):
        pass # Decision logic happens in run

    def run(self):
        # Check max_iter limit for this decision node before execution
        if self.max_iter is not None:
            current_count = self.state.get_node_execution_count_local(self.name)
            if current_count >= self.max_iter:
                self.next_node = None  # Stop execution
                return None
            # Increment after the check
            self.state.increment_node_execution(self.name)
        else:
            # Still track execution count for monitoring
            self.state.increment_node_execution(self.name)
        
        # Call the base run method to set up state properly
        super().run()
        
        # Get the output from the previous node's execution for decision making
        last_output = self.state.get_previous_output()
        
        self.next_node = None # Default to no next node if no condition matches
        for map_item in self.maps:
            if map_item.condition == last_output:
                # Ensure we get the node instance if it's a NodeType
                if isinstance(map_item.node, NodeType):
                    self.next_node = map_item.node.node_instance
                else:
                    self.next_node = map_item.node
                break # Take the first match

    def __str__(self):
        string = f"Decision ({self.name}):\n"
        for map_item in self.maps:
            string += f"  When {map_item.condition} >> Go to {map_item.node.name}\n"
        return string

        


def decision(*args:list[Union[NodeMapper, BaseNode]], max_iter: Optional[int] = None, **kwds: Any) -> Decision:
        assert len(args) > 1, "Decision must have at least two arguments"
        processed_args = []
        for arg in args:
            if isinstance(arg, NodeMapper):
                if isinstance(arg.node, NodeType):
                    # Create new NodeMapper but preserve chaining information
                    new_mapper = NodeMapper(arg.condition, arg.node.node_instance)
                    # Preserve the chain end node information
                    if hasattr(arg, '_chain_end_node'):
                        new_mapper._chain_end_node = arg._chain_end_node
                        if isinstance(new_mapper._chain_end_node, NodeType):
                            new_mapper._chain_end_node = new_mapper._chain_end_node.node_instance
                    
                    # Preserve the complete chain information
                    if hasattr(arg, '_complete_chain'):
                        new_mapper._complete_chain = []
                        for chain_node in arg._complete_chain:
                            if isinstance(chain_node, NodeType):
                                new_mapper._complete_chain.append(chain_node.node_instance)
                            else:
                                new_mapper._complete_chain.append(chain_node)
                    
                    # DON'T modify next_node here - it breaks multi-node chains
                    # The original chain A -> B -> C should be preserved
                    # Chain restoration happens in _handle_decision_node if needed
                        
                    arg = new_mapper
                processed_args.append(arg)
                current = arg.node
                if isinstance(current, NodeType):
                    current = current.node_instance

                while current.next_node:
                    processed_args.append(current.next_node)
                    current = current.next_node
            elif isinstance(arg, BaseNode):
                 pass


        return Decision(*processed_args, max_iter=max_iter, **kwds)


def _analyze_function_signature(callable_func: Callable) -> Dict[str, Any]:
    """Analyze function signature for intelligent parameter mapping
    
    Args:
        callable_func: Function to analyze
        
    Returns:
        Dict containing:
        - sig: Function signature
        - type_hints: Type hints dictionary  
        - state_param: Name of SharedState parameter (if any)
        - input_params: List of input parameter objects
        - param_names: List of input parameter names
        
    Raises:
        ValueError: If multiple SharedState parameters found
    """
    sig = inspect.signature(callable_func)
    type_hints = get_type_hints(callable_func)
    
    
    state_param = None
    input_params = []
    param_names = []
    
    for name, param in sig.parameters.items():
        # Check if this parameter is annotated with SharedState
        param_type = type_hints.get(name)
        if param_type is not None and getattr(param_type, '__name__', None) == 'SharedState':
            if state_param is not None:
                raise ValueError(f"Only one SharedState parameter allowed, found: {state_param}, {name}")
            state_param = name
        elif param.default is inspect.Parameter.empty and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            # This is an input parameter (non-default, non-state, not *args or **kwargs)
            input_params.append(param)
            param_names.append(name)
    
    return {
        'sig': sig,
        'type_hints': type_hints,
        'state_param': state_param,
        'input_params': input_params,
        'param_names': param_names
    }


def map_outputs_to_parameters(previous_output: Any, input_params: List, param_names: List[str]) -> List[Any]:
    """Map node output to function parameters based on output types and parameter structure
    
    This is the core intelligence of the parameter mapping system. It automatically
    maps previous node outputs to current node input parameters using these rules:
    
    1. Single parameter: Gets entire output (no unpacking)
    2. Multiple params + tuple/list output: Positional mapping
    3. Multiple params + dict output: Named mapping by parameter names
    4. Fallback: Replicate single output to all parameters
    
    Args:
        previous_output: Output from the previous workflow node
        input_params: List of parameter objects (from inspect.signature)
        param_names: List of parameter names for dict mapping
        
    Returns:
        List of arguments to pass to the function (*args style)
    """
    # Case 1: Single parameter - gets entire output (no unpacking)
    if len(input_params) == 1:
        return [previous_output]
    
    # Case 2: Multiple params + tuple/list output - positional mapping
    if isinstance(previous_output, (tuple, list)) and len(previous_output) >= len(input_params):
        return list(previous_output)[:len(input_params)]
    
    # Case 3: Multiple params + dict output - named mapping by parameter names
    if isinstance(previous_output, dict):
        return [previous_output.get(name) for name in param_names]
    
    # Fallback for other cases - will implement in subsequent tasks
    return [previous_output] * len(input_params) if input_params else []


# Performance optimization: Cache signature analysis results
# Maps function id() -> signature analysis dict for create_intelligent_wrapper
# Provides ~6x speedup for repeated wrapper creation of the same function
_signature_analysis_cache: Dict[int, Dict[str, Any]] = {}

def create_intelligent_wrapper(callable_func: Callable) -> Callable:
    """Create wrapper with intelligent parameter mapping and advanced system integration
    
    This is the core wrapper that enables the new input-first workflow design pattern.
    It automatically maps previous node outputs to current node input parameters using
    intelligent type-based mapping rules.
    
    Supported Parameter Patterns:
        Single parameter:
            @node('processor') def func(input_data): ...
            -> Gets entire previous output
            
        Multiple parameters with tuple/list input:
            @node('processor') def func(a, b, c): ... 
            -> Positional mapping: (val1, val2, val3) -> a=val1, b=val2, c=val3
            
        Multiple parameters with dict input:
            @node('processor') def func(name, age): ...
            -> Named mapping: {"name": "Alice", "age": 30} -> name="Alice", age=30
            
        State parameter injection:
            @node('processor') def func(input_data, state: SharedState): ...
            -> Automatically injects workflow state as keyword argument
            
        Mixed patterns:
            @node('processor') def func(a, b, state: SharedState, debug=False): ...
            -> Combines positional mapping + state injection + default parameters
    
    Advanced System Integration:
        - GUID-based node storage (instance.state.set_node_output)
        - Observer notifications (_notify_state_change events)
        - Node aliasing support (effective_name property)
        - Performance optimization with signature analysis caching
        - Conditional advanced features (only when node.name exists)
    
    Performance Features:
        - Signature analysis results cached by function ID
        - Sub-millisecond execution overhead for simple functions
        - Scales well with parameter count (linear performance)
    
    Args:
        callable_func: Original function to wrap with intelligent parameter mapping
        
    Returns:
        Wrapped function that handles:
        - Automatic parameter mapping from previous node outputs
        - SharedState injection for annotated parameters
        - GUID-based result storage and observer notifications
        - Error handling and performance optimization
        
    Raises:
        ValueError: If function has multiple SharedState parameters
        RuntimeError: If wrapped function execution fails
        
    Example:
        @node('data_processor')
        def process_data(name, age, state: SharedState, debug=False):
            return f"Processing {name} ({age}) in {state.instance_name}"
            
        # Previous node outputs: {"name": "Alice", "age": 30}
        # Result: "Processing Alice (30) in workflow_instance"
    """
    # Performance optimization: Use cached signature analysis
    cache_key = id(callable_func)
    if cache_key in _signature_analysis_cache:
        sig_analysis = _signature_analysis_cache[cache_key]
    else:
        sig_analysis = _analyze_function_signature(callable_func)
        _signature_analysis_cache[cache_key] = sig_analysis
    
    def wrapper(*args, **kwargs):
        """The actual wrapper that gets called when the node executes"""
        instance: Node = args[0]  # First arg is always the node instance
        previous_output = instance.state.get_previous_output()
        
        # Use our intelligent parameter mapping system
        input_params = sig_analysis['input_params']
        param_names = sig_analysis['param_names']
        state_param = sig_analysis['state_param']
        
        
        # Map previous output to function parameters
        mapped_args = map_outputs_to_parameters(previous_output, input_params, param_names)
        
        # Prepare function call arguments
        call_kwargs = {}
        if state_param:
            call_kwargs[state_param] = instance.state
            
        # Merge any additional kwargs passed to the wrapper
        call_kwargs.update(kwargs)
        
        # If we have a state parameter, use keyword arguments for all parameters
        # to avoid positional conflicts
        if state_param:
            # Convert positional mapped_args to keyword arguments
            # BUT preserve SharedState that was already injected
            for i, param_name in enumerate(param_names):
                if i < len(mapped_args) and param_name != state_param:
                    # Don't overwrite the SharedState parameter with the mapped arg
                    call_kwargs[param_name] = mapped_args[i]
            # Call with kwargs only
            result = callable_func(**call_kwargs)
        else:
            # No state parameter, use positional arguments as before
            result = callable_func(*mapped_args, **call_kwargs)
        
        # CRITICAL: Preserve existing advanced system integration
        if hasattr(instance, 'name') and instance.name:
            # Phase 2: Use enhanced GUID-based set_node_output method
            if hasattr(instance.state, 'set_node_output'):
                instance.state.set_node_output(instance, result)
            else:
                # Fallback for backward compatibility
                instance.state[instance.name] = result
            
            # Observer notifications for external system integration
            if hasattr(instance.state, '_notify_state_change'):
                instance.state._notify_state_change('node_execution', instance.name, result)
        
        return result
    
    # Expose original function for direct testing
    wrapper.exec = callable_func
    
    return wrapper


class NodeType:
    def __init__(self, node: Type[Node]):
        self.node: Type[Node] = node

        self._instance = None
    
    def _assign_method(self, method_name:str, callable_func: Callable) -> Callable:
        """Assign method with intelligent parameter mapping"""
        
        # Use new intelligent wrapper for parameter mapping
        wrapper = create_intelligent_wrapper(callable_func)
            
        setattr(self.node, method_name, wrapper)
        method = getattr(self.node, method_name)
        method.__doc__ = callable_func.__doc__
        
        # Store original function for testing access
        self.exec = callable_func
        
        return callable_func # Return the original function

    def __call__(self, callable_func: Callable):
        """Direct decorator usage: @node('name') - function becomes the node"""
        self._assign_method('_execute_impl', callable_func)
        return self  # Return NodeType instance to maintain .node_instance access
    
    def __repr__(self):
        name = getattr(self.node, "__name__", None) or getattr(self.node, "__class__", type(self.node)).__name__
        return f"<NodeType: [{name}] >"
    
    @property
    def node_instance(self) -> Node:

        if self._instance is None:
            # Instantiate Node class
            self._instance = self.node()
        return self._instance
    
    def alias(self, alias_name: str) -> 'BaseNode':
        """Create aliased reference for reused nodes"""
        # Get the node instance and create alias
        node_instance = self.node_instance
        return node_instance.alias(alias_name)
    
    def __rrshift__(self, other: Any):
        if isinstance(other, bool):
            return NodeMapper(other, self.node_instance)
        if isinstance(other, str):
            return NodeMapper(other, self.node_instance)
        if isinstance(other, NodeType):
            return NodeMapper(other.node_instance, self)
        else:
            return NodeMapper(other, self.node_instance)


    def __rshift__(self, other: Union["BaseNode", "NodeType"]):
        left: BaseNode = self.node_instance
        target: BaseNode = other.node_instance if isinstance(other, NodeType) else other
        left.next_node = target
        target._first_node = left._first_node
        if left._prev_shift is not None:
            target._prev_shift = left._prev_shift
        return target

def node(name:str):
    if name not in node_registry:
        def __init__(self, *args, **kwargs):
            self.name = name
            Node.__init__(self, *args, **kwargs)

        class_attrs = {
            "__init__": __init__,
        }
        NewNodeClass = type(name, (Node,), class_attrs)
        node_registry[name] = NewNodeClass 
        n = NodeType(node_registry[name])
    else:
        n = NodeType(node_registry[name])

    return n


class BatchNode(Node):
    """
    A node designed to process a batch of items.
    Subclasses should implement _execute_item for individual item logic.
    """
    def __init__(self, label: Optional[str] = None, *args, **kwargs):
        super().__init__(label=label or "Batch", *args, **kwargs)

    def _execute_item(self, item: Any, *args, **kwargs) -> Any:
        """Process a single item from the batch."""
        raise NotImplementedError(f"_execute_item is not implemented for {self.name}")

    def execute(self, *args, **kwargs) -> List[Any]:
        """
        Executes _execute_item for each item in the input batch.
        Expects the batch to be the first argument or retrieved from state.
        """
        items = self.state.get_previous_output() # Default to previous output
        # Allow overriding via direct args if needed, simplistic check:
        if args and isinstance(args[0], (list, tuple)):
             items = args[0]
             args = args[1:] # Adjust args for _execute_item


        if not isinstance(items, (list, tuple)):
            warnings.warn(f"{self.name} received non-iterable input for batch processing: {type(items)}. Returning empty list.")
            return []

        results = []
        for item in items:
            try:
                # Pass remaining args and all kwargs to item execution
                result = self._execute_item(item, *args, **kwargs)
                results.append(result)
            except Exception as e:
                # Decide error handling: append None, raise, skip? Append None for now.
                results.append(None)
        return results


# --- Asynchronous Nodes ---

class AsyncNode(Node):
    """
    A node that performs its operations asynchronously.
    Subclasses should implement async_execute and optionally others.
    Requires an async-aware sequence runner.
    """
    def __init__(self, label: Optional[str] = None, max_retries: int = 0, retry_wait: float = 0.5, *args, **kwargs):
        super().__init__(label=label or "Async", *args, **kwargs)
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        # Indicate that standard run won't work
        self._is_async = True


    async def async_execute(self, *args, **kwargs) -> Any:
        """Asynchronous execution with native agent discovery."""
        # Import here to avoid circular imports
        from .agent_interceptor import workflow_node_context
        from .agent_discovery import get_agent_registry
        
        # Always execute within discovery context
        with workflow_node_context(self.name):
            try:
                # Notify that node execution is starting
                registry = get_agent_registry()
                registry._notify_observers("node_execution_started", self.name, {
                    "node": self,
                    "args": str(args)[:100] if args else "",
                    "kwargs": {k: str(v)[:50] for k, v in kwargs.items()}
                })
                
                # Call the actual async implementation
                result = await self._async_execute_impl(*args, **kwargs)
                
                # Notify completion
                registry._notify_observers("node_execution_completed", self.name, {
                    "node": self,
                    "result": str(result)[:100] if result else None
                })
                
                return result
                
            except Exception as e:
                # Notify error
                get_agent_registry()._notify_observers("node_execution_failed", self.name, {
                    "node": self,
                    "error": str(e)
                })
                raise
    
    async def _async_execute_impl(self, *args, **kwargs) -> Any:
        """Asynchronous core execution logic - implement in subclasses."""
        raise NotImplementedError(f"_async_execute_impl is not implemented for {self.name}")
        
    # Lifecycle methods removed in Plan 16: Lifecycle Simplification
    # Use separate nodes for setup/cleanup instead

    async def async_execute_fallback(self, error: Exception, *args, **kwargs) -> Any:
        """Asynchronous logic to run if all retries fail."""
        raise error # Default is to re-raise the last error


    async def async_run(self, *args, **kwargs) -> Any:
        """Orchestrates the async execution lifecycle."""
        exec_result = None
        last_error = None
        
        # Simple retry logic for backward compatibility
        for attempt in range(self.max_retries + 1):
            try:
                exec_result = await self.async_execute(*args, **kwargs)
                self.state.current.execute = exec_result
                last_error = None  # Success
                break
            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_wait)
                else:
                    break

        # If we still have an error after all attempts, try fallback
        if last_error:
            try:
                exec_result = await self.async_execute_fallback(last_error, *args, **kwargs)
                self.state.current.execute = exec_result
                last_error = None  # Fallback succeeded
            except Exception:
                # Fallback also failed - re-raise original error
                raise last_error

        return exec_result


    # Override synchronous methods to prevent accidental use
    def execute(self, *args, **kwargs):
         raise RuntimeError(f"{self.name} is an AsyncNode. Use an async runner and async_execute.")
         
    # Lifecycle methods removed in Plan 16: Lifecycle Simplification
    # Use separate nodes for setup/cleanup instead

    def run(self):
         raise RuntimeError(f"{self.name} is an AsyncNode and requires an async-compatible sequence runner (e.g., calling async_run).")


class AsyncBatchNode(AsyncNode, BatchNode):
    """
    Processes a batch of items asynchronously, one after another.
    Subclasses should implement async_execute_item.
    """
    def __init__(self, label: Optional[str] = None, *args, **kwargs):
        # Combine initializers, prioritize AsyncNode for retry logic etc.
        AsyncNode.__init__(self, label=label or "AsyncBatch", *args, **kwargs)
        # BatchNode init logic is mainly naming, covered by AsyncNode's super call chain.

    async def async_execute_item(self, item: Any, *args, **kwargs) -> Any:
        """Process a single item from the batch asynchronously."""
        raise NotImplementedError(f"async_execute_item is not implemented for {self.name}")

    async def async_execute(self, *args, **kwargs) -> List[Any]:
        """
        Executes async_execute_item sequentially for each item in the batch.
        """
        items = self.state.get_previous_output() # Default to previous output
        # Allow overriding via direct args
        if args and isinstance(args[0], (list, tuple)):
             items = args[0]
             args = args[1:] # Adjust args for item execution


        if not isinstance(items, (list, tuple)):
            warnings.warn(f"{self.name} received non-iterable input for async batch processing: {type(items)}. Returning empty list.")
            return []

        results = []
        for item in items:
            try:
                 # Pass remaining args/kwargs
                result = await self.async_execute_item(item, *args, **kwargs)
                results.append(result)
            except Exception as e:
                results.append(None) # Or handle error differently
        return results

    # Need to override the sync _execute_item from BatchNode
    def _execute_item(self, item: Any, *args, **kwargs) -> Any:
        raise RuntimeError(f"{self.name} uses async_execute_item.")


class AsyncParallelBatchNode(AsyncBatchNode):
    """
    Processes a batch of items asynchronously and in parallel.
    Subclasses should implement async_execute_item.
    """
    def __init__(self, label: Optional[str] = None, *args, **kwargs):
        super().__init__(label=label or "AsyncParallelBatch", *args, **kwargs)

    async def async_execute(self, *args, **kwargs) -> List[Any]:
        """
        Executes async_execute_item concurrently for all items in the batch.
        """
        items = self.state.get_previous_output() # Default to previous output
        # Allow overriding via direct args
        if args and isinstance(args[0], (list, tuple)):
             items = args[0]
             args = args[1:] # Adjust args for item execution


        if not isinstance(items, (list, tuple)):
            warnings.warn(f"{self.name} received non-iterable input for async parallel batch processing: {type(items)}. Returning empty list.")
            return []

        tasks = []
        for item in items:
             # Create a task for each item execution
             # Pass remaining args/kwargs
             task = asyncio.create_task(self.async_execute_item(item, *args, **kwargs))
             tasks.append(task)

        # Run all tasks concurrently and gather results
        # return_exceptions=True allows the gather to complete even if some tasks fail
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results, potentially logging errors for exceptions
        processed_results = []
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                processed_results.append(None) # Or handle error differently
            else:
                processed_results.append(res)

        return processed_results


class ParallelNode(AsyncNode):
    """Node that executes multiple child nodes in parallel with enhanced features"""
    
    def __init__(self, *nodes, max_concurrent: Optional[int] = None, timeout: Optional[float] = None, optimization_enabled: bool = True):
        super().__init__(label="Parallel")
        
        # ENHANCED: Convert all NodeType objects to instances to prevent runtime errors
        resolved_nodes = []
        for node in nodes:
            try:
                resolved_node = _ensure_node_instance(node)
                resolved_nodes.append(resolved_node)
                if isinstance(node, NodeType):
                    pass  # NodeType handling
            except TypeError as e:
                raise TypeError(f"Invalid node for parallel execution: {e}")
        
        self.parallel_nodes = resolved_nodes
        self.name = f"parallel_{id(self)}"
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        
        # Plan 10: Resource optimization support
        self.optimization_enabled = optimization_enabled
        
        # Integration with existing egregore systems (if optimization enabled)
        if optimization_enabled:
            try:
                # Optional dependency; ignore if not present
                from ..memory_management import get_resource_tracker, get_memory_monitor  # type: ignore
                self.resource_tracker = get_resource_tracker()
                self.memory_monitor = get_memory_monitor()
            except ImportError:
                self.resource_tracker = None
                self.memory_monitor = None
        else:
            self.resource_tracker = None
            self.memory_monitor = None
        
        # Validate unique names
        self._validate_unique_names()
    
    def _validate_unique_names(self):
        """Validate that all parallel nodes have unique names"""
        names = []
        for node in self.parallel_nodes:
            # Enhanced: Better name extraction for resolved instances
            if hasattr(node, 'name') and node.name:
                name = node.name
            elif hasattr(node, '__class__'):
                name = node.__class__.__name__
            else:
                name = str(node)
            names.append(name)
        
        if len(names) != len(set(names)):
            duplicates = [name for name in names if names.count(name) > 1]
            node_info = [f"{getattr(node, 'name', node.__class__.__name__)}" for node in self.parallel_nodes]
            raise ValueError(
                f"Parallel nodes must have unique names. "
                f"Duplicates found: {list(set(duplicates))}. "
                f"Node names: {node_info}"
            )
    
    def _find_terminal_node(self, start_node):
        """Find the terminal (last) node in a chain starting from start_node"""
        current = start_node
        while hasattr(current, 'next_node') and current.next_node is not None:
            current = current.next_node
        return current
    
    def _get_terminal_node_name(self, node):
        """Get the name of the terminal node in a branch"""
        terminal_node = self._find_terminal_node(node)
        if hasattr(terminal_node, 'name') and terminal_node.name:
            return terminal_node.name
        elif hasattr(terminal_node, '__class__'):
            return terminal_node.__class__.__name__
        else:
            return str(terminal_node)
    # Plan 10: Resource optimization methods
    def _allocate_resources(self) -> dict:
        """Calculate optimal resource allocation for parallel execution"""
        import os
        
        if not self.optimization_enabled or not self.memory_monitor:
            # Fallback configuration
            return {
                "max_workers": self.max_concurrent or len(self.parallel_nodes),
                "memory_limit_mb": float('inf'),
                "cpu_limit": os.cpu_count(),
                "batch_size": None
            }
        
        # Get current system state
        try:
            available_memory = self.memory_monitor.get_available_memory()
        except Exception:
            available_memory = 1000.0  # 1GB fallback
        
        available_cpu = os.cpu_count()
        
        # Estimate memory per node (can be enhanced with profiling)
        estimated_memory_per_node = 50.0  # MB - conservative estimate
        
        # Calculate optimal workers based on resource constraints
        memory_limited_workers = int(available_memory * 0.7 / estimated_memory_per_node)
        cpu_limited_workers = available_cpu
        resource_limited_workers = min(memory_limited_workers, cpu_limited_workers or memory_limited_workers)
        
        optimal_workers = min(
            self.max_concurrent or len(self.parallel_nodes),
            len(self.parallel_nodes),
            max(1, resource_limited_workers)  # At least 1 worker
        )
        
        # Calculate batch size for load balancing
        batch_size = max(1, len(self.parallel_nodes) // optimal_workers) if optimal_workers > 1 else None
        
        resource_config = {
            "max_workers": optimal_workers,
            "memory_limit_mb": available_memory * 0.8,  # Reserve 20%
            "cpu_limit": available_cpu,
            "batch_size": batch_size
        }
        
        return resource_config
    
    def _create_execution_batches(self, resource_config: dict) -> list:
        """Create balanced batches for execution based on resource configuration"""
        batch_size = resource_config.get("batch_size")
        
        if not batch_size or batch_size >= len(self.parallel_nodes):
            # Single batch - execute all at once (with semaphore limiting)
            return [self.parallel_nodes]
        
        # Create multiple batches
        batches = []
        for i in range(0, len(self.parallel_nodes), batch_size):
            batch = self.parallel_nodes[i:i + batch_size]
            batches.append(batch)
        
        return batches
    
    async def _execute_optimized(self, *args, **kwargs):
        """Resource-optimized parallel execution"""
        # Step 1: Analyze system resources and create configuration
        resource_config = self._allocate_resources()
        
        # Step 2: Create execution batches based on resource limits
        batches = self._create_execution_batches(resource_config)
        
        # Step 3: Execute batches with resource monitoring
        try:
            all_results = []
            for batch_idx, batch in enumerate(batches):
                batch_results = await self._execute_batch(batch, resource_config, *args, **kwargs)
                all_results.extend(batch_results)
            
            return all_results
            
        finally:
            # Release any allocated resources
            if self.resource_tracker:
                try:
                    self.resource_tracker.release_resources(self.name or "parallel_node")
                except Exception as e:
                    pass
    
    async def _execute_batch(self, batch: list, resource_config: dict, *args, **kwargs) -> list:
        """Execute a batch of nodes with resource limits"""
        import asyncio
        
        # Create semaphore to limit concurrent execution
        max_workers = min(resource_config["max_workers"], len(batch))
        semaphore = asyncio.Semaphore(max_workers)
        
        async def execute_with_limit(node):
            async with semaphore:
                if self.resource_tracker:
                    try:
                        with self.resource_tracker.track_execution(getattr(node, 'name', str(node))):
                            return await self._execute_single_node(node, *args, **kwargs)
                    except Exception:
                        # Fallback if resource tracking fails
                        return await self._execute_single_node(node, *args, **kwargs)
                else:
                    return await self._execute_single_node(node, *args, **kwargs)
        
        # Execute all nodes in batch concurrently (but limited by semaphore)
        tasks = [execute_with_limit(node) for node in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                node_name = getattr(batch[i], 'name', str(batch[i]))
                # Re-raise the exception to maintain existing error handling behavior
                raise ParallelExecutionError(f"Node '{node_name}' failed in parallel execution: {result}") from result
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_single_node(self, node, *args, **kwargs):
        """Execute a single node with proper error handling"""
        # Set state for node
        node.state = self.state
        
        # Execute based on node type
        if hasattr(node, 'async_execute'):
            # Async node
            return await node.async_execute(*args, **kwargs)
        else:
            # Sync node - run in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: node.execute(*args, **kwargs)
            )
    
    async def async_execute(self, *args, **kwargs):
        """Execute all nodes in parallel with optional optimization"""
        
        # Plan 10: Route to optimized execution if enabled
        if self.optimization_enabled:
            return await self._execute_optimized_with_state_handling(*args, **kwargs)
        else:
            return await self._execute_basic(*args, **kwargs)
    
    async def _execute_optimized_with_state_handling(self, *args, **kwargs):
        """Wrapper for optimized execution with state change notifications"""
        # Notify start of parallel execution
        if hasattr(self.state, '_notify_state_change'):
            self.state._notify_state_change('parallel_start', self.name, {
                'node_count': len(self.parallel_nodes),
                'node_names': [getattr(n, 'name', str(n)) for n in self.parallel_nodes],
                'max_concurrent': self.max_concurrent,
                'timeout': self.timeout,
                'optimization_enabled': True
            })
        
        try:
            # Use optimized execution
            results = await self._execute_optimized(*args, **kwargs)
            
            # Process and store results in state (maintaining compatibility) - return as dictionary
            final_results = {}
            for i, result in enumerate(results):
                node = self.parallel_nodes[i]
                # Get terminal node name for this branch
                terminal_node_name = self._get_terminal_node_name(node)
                final_results[terminal_node_name] = result
                
                # Store result by terminal node name (Phase 2: enhanced storage)
                if hasattr(self.state, 'set_node_output'):
                    self.state.set_node_output(node, result)
                else:
                    # Fallback for backward compatibility  
                    self.state[terminal_node_name] = result
                
                # NEW: Plan 20 - Store child node execution in state.executions for workflow_state() access
                from .state import NodeOutput
                child_execution = NodeOutput(name=terminal_node_name)
                child_execution.execute = result
                self.state.executions.append(child_execution)
                
                # NEW: Plan 20 - Add child node to execution sequence
                self.state.execution_sequence.append(node)
                
                # Notify observers of completion
                if hasattr(self.state, '_notify_state_change'):
                    self.state._notify_state_change('parallel_node_complete', terminal_node_name, result)
            
            # Notify completion of parallel block
            if hasattr(self.state, '_notify_state_change'):
                self.state._notify_state_change('parallel_complete', self.name, {
                    'results': final_results,
                    'node_names': [getattr(n, 'name', str(n)) for n in self.parallel_nodes],
                    'optimization_enabled': True
                })
            
            return final_results
            
        except Exception as e:
            # Handle timeout and other errors
            if hasattr(self.state, '_notify_state_change'):
                self.state._notify_state_change('parallel_error', self.name, {
                    'error': str(e),
                    'optimization_enabled': True
                })
            raise
    
    async def _execute_basic(self, *args, **kwargs):
        """Basic parallel execution without optimization (existing behavior)"""
        # Notify start of parallel execution
        if hasattr(self.state, '_notify_state_change'):
            self.state._notify_state_change('parallel_start', self.name, {
                'node_count': len(self.parallel_nodes),
                'node_names': [getattr(n, 'name', str(n)) for n in self.parallel_nodes],
                'max_concurrent': self.max_concurrent,
                'timeout': self.timeout,
                'optimization_enabled': False
            })
        
        try:
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(self.max_concurrent or len(self.parallel_nodes))
            
            # Create tasks for all nodes
            tasks = []
            for node in self.parallel_nodes:
                task = self._create_node_task(node, semaphore, *args, **kwargs)
                tasks.append(task)
            
            # Execute with timeout if specified
            if self.timeout:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=self.timeout
                )
            else:
                results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle errors - return as dictionary
            final_results = {}
            for i, (node, result) in enumerate(zip(self.parallel_nodes, results)):
                # Get terminal node name for this branch
                terminal_node_name = self._get_terminal_node_name(node)
                
                if isinstance(result, Exception):
                    error_info = {
                        'node': terminal_node_name,
                        'error': str(result),
                        'error_type': type(result).__name__
                    }
                    
                    # Notify observers of error
                    if hasattr(self.state, '_notify_state_change'):
                        self.state._notify_state_change('parallel_node_error', terminal_node_name, error_info)
                    
                    # Re-raise with context
                    raise ParallelExecutionError(
                        f"Node '{terminal_node_name}' failed in parallel execution: {result}"
                    ) from result
                else:
                    # Store result with terminal node name as key
                    final_results[terminal_node_name] = result
                    
                    # Store result by terminal node name (Phase 2: enhanced storage)
                    if hasattr(self.state, 'set_node_output'):
                        self.state.set_node_output(node, result)
                    else:
                        # Fallback for backward compatibility  
                        self.state[terminal_node_name] = result
                    
                    # NEW: Plan 20 - Store child node execution in state.executions for workflow_state() access
                    from .state import NodeOutput
                    child_execution = NodeOutput(name=node_name)  
                    child_execution.execute = result
                    self.state.executions.append(child_execution)
                    
                    # NEW: Plan 20 - Add child node to execution sequence
                    self.state.execution_sequence.append(node)
                    
                    # Notify observers of completion
                    if hasattr(self.state, '_notify_state_change'):
                        self.state._notify_state_change('parallel_node_complete', node_name, result)
            
            # Notify completion of parallel block
            if hasattr(self.state, '_notify_state_change'):
                self.state._notify_state_change('parallel_complete', self.name, {
                    'results': final_results,
                    'node_names': [getattr(n, 'name', str(n)) for n in self.parallel_nodes]
                })
            
            return final_results
            
        except asyncio.TimeoutError:
            timeout_error = ParallelTimeoutError(
                f"Parallel execution timed out after {self.timeout} seconds"
            )
            
            # Notify observers of timeout
            if hasattr(self.state, '_notify_state_change'):
                self.state._notify_state_change('parallel_timeout', self.name, {
                    'timeout': self.timeout,
                    'node_names': [getattr(n, 'name', str(n)) for n in self.parallel_nodes]
                })
            
            raise timeout_error
    
    async def _create_node_task(self, node, semaphore, *args, **kwargs):
        """Create async task for node execution with concurrency control"""
        async with semaphore:
            # FIXED: Ensure NodeType objects are converted to instances
            actual_node = _ensure_node_instance(node)
            if isinstance(node, NodeType):
                pass
            
            # Set state for node
            actual_node.state = self.state
            
            # Execute based on node type
            if isinstance(actual_node, AsyncNode):
                # Async node
                return await actual_node.async_execute(*args, **kwargs)
            else:
                # Sync node - run in thread pool
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None,
                    lambda: actual_node.execute(*args, **kwargs)  # ✅ Fixed - using actual_node
                )
    
    def execute(self, *args, **kwargs):
        """Sync wrapper for async execution"""
        return asyncio.run(self.async_execute(*args, **kwargs))


class ParallelExecutionError(Exception):
    """Raised when a node fails during parallel execution"""
    pass


class ParallelTimeoutError(Exception):
    """Raised when parallel execution times out"""
    pass


def parallel(*nodes, max_concurrent: Optional[int] = None, timeout: Optional[float] = None) -> ParallelNode:
    """
    Create a parallel execution node
    
    Args:
        *nodes: Variable number of nodes to execute in parallel
        max_concurrent: Maximum number of concurrent executions (optional)
        timeout: Timeout in seconds for parallel block (optional)
        
    Returns:
        ParallelNode: Node that executes all children in parallel
    
    Example:
        # Basic parallel execution
        workflow = Sequence(
            load_data >>
            parallel(
                clean_data,
                validate_schema,
                extract_features
            ) >>
            process_results
        
        # With concurrency limit and timeout
        parallel_node = parallel(
            node1, node2, node3,
            max_concurrent=2,
            timeout=30.0
    """
    return ParallelNode(*nodes, max_concurrent=max_concurrent, timeout=timeout)


# %%
# Intelligent Parameter Mapping System (Ported from V1)

def _analyze_function_signature(callable_func: Callable) -> Dict[str, Any]:
    """Analyze function signature for intelligent parameter mapping
    
    Args:
        callable_func: Function to analyze
        
    Returns:
        Dict containing:
        - sig: Function signature
        - type_hints: Type hints dictionary  
        - state_param: Name of SharedState parameter (if any)
        - input_params: List of input parameter objects
        - param_names: List of input parameter names
        
    Raises:
        ValueError: If multiple SharedState parameters found
    """
    sig = inspect.signature(callable_func)
    type_hints = get_type_hints(callable_func)
    
    state_param = None
    input_params = []
    param_names = []
    
    for name, param in sig.parameters.items():
        # Check if this parameter is annotated with SharedState
        param_type = type_hints.get(name)
        if param_type is not None and getattr(param_type, '__name__', None) == 'SharedState':
            if state_param is not None:
                raise ValueError(f"Only one SharedState parameter allowed, found: {state_param}, {name}")
            state_param = name
        elif param.default is inspect.Parameter.empty and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            # This is an input parameter (non-default, non-state, not *args or **kwargs)
            input_params.append(param)
            param_names.append(name)
    
    return {
        'sig': sig,
        'type_hints': type_hints,
        'state_param': state_param,
        'input_params': input_params,
        'param_names': param_names
    }


def map_outputs_to_parameters(previous_output: Any, input_params: List, param_names: List[str]) -> List[Any]:
    """Map node output to function parameters based on output types and parameter structure
    
    This is the core intelligence of the parameter mapping system. It automatically
    maps previous node outputs to current node input parameters using these rules:
    
    1. Single parameter: Gets entire output (no unpacking)
    2. Multiple params + tuple/list output: Positional mapping
    3. Multiple params + dict output: Named mapping by parameter names
    4. Fallback: Replicate single output to all parameters
    
    Args:
        previous_output: Output from the previous workflow node
        input_params: List of parameter objects (from inspect.signature)
        param_names: List of parameter names for dict mapping
        
    Returns:
        List of arguments to pass to the function (*args style)
    """
    # Case 1: Single parameter - gets entire output (no unpacking)
    if len(input_params) == 1:
        return [previous_output]
    
    # Case 2: Multiple params + tuple/list output - positional mapping
    if isinstance(previous_output, (tuple, list)) and len(previous_output) >= len(input_params):
        return list(previous_output)[:len(input_params)]
    
    # Case 3: Multiple params + dict output - named mapping by parameter names
    if isinstance(previous_output, dict):
        return [previous_output.get(name) for name in param_names]
    
    # Fallback for other cases
    return [previous_output] * len(input_params) if input_params else []


# Performance optimization: Cache signature analysis results
# Maps function id() -> signature analysis dict for create_intelligent_wrapper
# Provides ~6x speedup for repeated wrapper creation of the same function
_signature_analysis_cache: Dict[int, Dict[str, Any]] = {}


def create_intelligent_wrapper(callable_func: Callable) -> Callable:
    """Create wrapper with intelligent parameter mapping and advanced system integration
    
    This is the core wrapper that enables the new input-first workflow design pattern.
    It automatically maps previous node outputs to current node input parameters using
    intelligent type-based mapping rules.
    
    Supported Parameter Patterns:
        Single parameter:
            @node('processor') def func(input_data): ...
            -> Gets entire previous output
            
        Multiple parameters with tuple/list input:
            @node('processor') def func(a, b, c): ... 
            -> Positional mapping: (val1, val2, val3) -> a=val1, b=val2, c=val3
            
        Multiple parameters with dict input:
            @node('processor') def func(name, age): ...
            -> Named mapping: {"name": "Alice", "age": 30} -> name="Alice", age=30
            
        State parameter injection:
            @node('processor') def func(input_data, state: SharedState): ...
            -> Automatically injects workflow state as keyword argument
            
        Mixed patterns:
            @node('processor') def func(a, b, state: SharedState, debug=False): ...
            -> Combines positional mapping + state injection + default parameters
    
    Args:
        callable_func: Original function to wrap with intelligent parameter mapping
        
    Returns:
        Wrapped function with parameter mapping capabilities
        
    Raises:
        ValueError: If function has multiple SharedState parameters
    """
    # Performance optimization: Use cached signature analysis
    cache_key = id(callable_func)
    if cache_key in _signature_analysis_cache:
        sig_analysis = _signature_analysis_cache[cache_key]
    else:
        sig_analysis = _analyze_function_signature(callable_func)
        _signature_analysis_cache[cache_key] = sig_analysis
    
    def wrapper(*args, **kwargs):
        """The actual wrapper that gets called when the node executes"""
        instance: Node = args[0]  # First arg is always the node instance
        previous_output = instance.state.get_previous_output()
        
        # Use our intelligent parameter mapping system
        input_params = sig_analysis['input_params']
        param_names = sig_analysis['param_names']
        state_param = sig_analysis['state_param']
        
        # Map previous output to function parameters
        mapped_args = map_outputs_to_parameters(previous_output, input_params, param_names)
        
        # Prepare function call arguments
        call_kwargs = {}
        if state_param:
            call_kwargs[state_param] = instance.state
            
        # Merge any additional kwargs passed to the wrapper
        call_kwargs.update(kwargs)
        
        # If we have a state parameter, use keyword arguments for all parameters
        # to avoid positional conflicts
        if state_param:
            # Convert positional mapped_args to keyword arguments
            for i, param_name in enumerate(param_names):
                if i < len(mapped_args):
                    call_kwargs[param_name] = mapped_args[i]
            # Call with kwargs only
            result = callable_func(**call_kwargs)
        else:
            # No state parameter, use positional arguments
            result = callable_func(*mapped_args, **call_kwargs)
        
        # Advanced system integration (if available)
        if hasattr(instance, 'name') and instance.name:
            # Store result by GUID-based method if available
            if hasattr(instance.state, 'set_node_output'):
                instance.state.set_node_output(instance, result)
            else:
                # Fallback to name-based storage
                instance.state[instance.name] = result
        
        return result
    
    return wrapper

node_registry = {}

class NodeFactory:
    """Factory class for creating nodes. 
    typically imported as N

    @N.register("A")
    def test_n(t=0):
        if t is not None:   
            return t
    """
    def __init__(self):
        self.registry = node_registry
    
    def register(self, name: str, method: Optional[Literal["execute"]] = None, node_type: type[Node] = Node ):
        """Decorator to register a node type with the factory. By default the method is 'execute'."""
        if name not in self.registry:
            def __init__(self, *args, **kwargs):
                self.name = name
                Node.__init__(self, *args, **kwargs)

            class_attrs = {
                "__init__": __init__,

            }
            NewNodeClass = type(name, (Node,), class_attrs)
            self.registry[name] = NewNodeClass
            n = NodeType(self.registry[name])
            
            
        else:
            n = NodeType(self.registry[name])
        
        if method is None:
            return n
        
        if method == "execute":
            # Return a decorator that binds the function to the node's execute
            return n.__call__
        # Lifecycle methods removed in Plan 16: Lifecycle Simplification
        else:
            raise ValueError(f"Unknown method: {method}. Only 'execute' is supported.")

    
    def __getitem__(self, name: str):
        return self.registry[name]
    
    def __call__(self, name: str):
        """Create or retrieve a node type, supporting decorator syntax @node('name')"""
        if name not in self.registry:
            # Auto-register the node if it doesn't exist (enables @node('name') syntax)
            return self.register(name)
        else:
            return NodeType(self.registry[name])

node_factory = NodeFactory()

#%%