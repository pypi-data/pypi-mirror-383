"""
Enhanced Decision Node with Pattern Matching

This module provides the main EnhancedDecision class and helper functions
for creating sophisticated pattern-based decision nodes.
"""

from typing import Any, List, Optional, Union
import inspect
from ..base_node import Node, BaseNode, NodeMapper, NodeType
from .patterns import (
    Pattern, ValuePattern, ClassPattern, InstancePattern, 
    PredicatePattern, DefaultPattern, RangePattern, ListPattern, DictPattern
from .exceptions import MaxIterationsExceededError, InvalidPatternError


class EnhancedDecision(Node):
    """Enhanced decision node with sophisticated pattern matching capabilities
    
    Supports:
    - Value matching: 'hello' >> handler
    - Type matching: str >> handler, int >> handler
    - Instance patterns: HTTPResponse(status_code=200) >> handler
    - Lambda predicates: lambda x: x > 0 >> handler
    - Default cases: _ >> handler
    - Loop control: max_iter parameter
    - Range matching: range(1, 10) >> handler
    - List matching: [1, 2, 3] >> handler
    - Dict patterns: {'status': 'ok'} >> handler
    """
    
    def __init__(self, *patterns, max_iter: Optional[int] = None, name: str = None):
        """Initialize enhanced decision node
        
        Args:
            *patterns: Pattern objects or condition >> node mappings
            max_iter: Maximum iterations before falling back to default pattern
            name: Optional name for the decision node
        """
        super().__init__(label=name or "EnhancedDecision")
        
        self.max_iter = max_iter
        self.iteration_count = 0
        self.last_selected_node = None  # Track last selected target node
        self.patterns: List[Pattern] = []
        
        # Process input patterns
        self._process_patterns(patterns)
        
        # Sort patterns by priority (lower number = higher priority)
        self.patterns.sort(key=lambda p: p.priority)
        
        # Update name with pattern info
        if not name:
            pattern_summary = self._create_pattern_summary()
            self.name = f"EnhancedDecision({pattern_summary})"
    
    def _process_patterns(self, patterns):
        """Process input patterns and convert to Pattern objects"""
        for pattern_input in patterns:
            if isinstance(pattern_input, Pattern):
                # Already a Pattern object
                self.patterns.append(pattern_input)
            elif isinstance(pattern_input, NodeMapper):
                # Convert NodeMapper to appropriate Pattern
                self.patterns.append(self._convert_nodemapper_to_pattern(pattern_input))
            elif hasattr(pattern_input, '__rshift__'):
                # This might be a lambda or other callable that supports >>
                # We'll handle it in the next workflow iteration
                raise InvalidPatternError(pattern_input, "Lambda patterns must use >> operator (lambda x: condition >> handler)")
            else:
                raise InvalidPatternError(pattern_input, "must be a Pattern object or NodeMapper")
    
    def _convert_nodemapper_to_pattern(self, node_mapper: NodeMapper) -> Pattern:
        """Convert NodeMapper to appropriate Pattern type"""
        condition = node_mapper.condition
        target_node = self._resolve_target_node(node_mapper.node)
        
        # Determine pattern type based on condition
        if condition == "_":
            return DefaultPattern(target_node)
        elif isinstance(condition, type):
            return ClassPattern(condition, target_node)
        elif isinstance(condition, range):
            return RangePattern(condition, target_node)
        elif isinstance(condition, (list, tuple)):
            return ListPattern(condition, target_node)
        elif isinstance(condition, dict):
            return DictPattern(condition, target_node)
        elif callable(condition) and not isinstance(condition, type):
            return PredicatePattern(condition, target_node)
        elif hasattr(condition, '__class__') and hasattr(condition, '__dict__'):
            # Instance pattern (object with attributes)
            return InstancePattern(condition, target_node)
        else:
            # Default to value pattern
            return ValuePattern(condition, target_node)
    
    def _resolve_target_node(self, node):
        """Resolve NodeType to actual node instance"""
        if isinstance(node, NodeType):
            return node.node_instance
        return node
    
    def _create_pattern_summary(self) -> str:
        """Create a summary string of patterns for naming"""
        if not self.patterns:
            return "no_patterns"
        
        summaries = []
        for pattern in self.patterns[:3]:  # Show first 3 patterns
            if isinstance(pattern, ValuePattern):
                summaries.append(repr(pattern.value))
            elif isinstance(pattern, ClassPattern):
                summaries.append(pattern.class_type.__name__)
            elif isinstance(pattern, DefaultPattern):
                summaries.append("_")
            else:
                summaries.append(pattern.__class__.__name__.replace('Pattern', ''))
        
        if len(self.patterns) > 3:
            summaries.append("...")
        
        return ", ".join(summaries)
    
    def execute(self, *args, **kwargs):
        """Execute decision with enhanced pattern matching - returns decision result"""
        # Get the output from the previous node for decision making
        last_output = self.state.get_previous_output()
        
        # Try to match patterns in priority order
        matched_node = None
        for pattern in self.patterns:
            try:
                if pattern.matches(last_output, self.state):
                    matched_node = pattern.target_node
                    
                    # Check if we're selecting the same node again
                    if matched_node == self.last_selected_node:
                        self.iteration_count += 1
                        # Check max_iter limit
                        if self.max_iter and self.iteration_count >= self.max_iter:
                            raise MaxIterationsExceededError(
                                self.max_iter, 
                                self.iteration_count,
                                self.name
                    else:
                        # Different node selected, reset counter
                        self.iteration_count = 1
                        self.last_selected_node = matched_node
                    
                    break
            except MaxIterationsExceededError:
                # Re-raise max iterations error
                raise
            except Exception as e:
                # Pattern matching failed - continue to next pattern
                continue
        
        # Set the next node for workflow continuation
        if matched_node:
            self.next_node = matched_node
        else:
            # No pattern matched - terminate workflow
            self.next_node = None
        
        # Decision nodes return the original input to pass through to next node
        # The actual logic execution happens when workflow moves to next_node
        return last_output
    
    
    def add_pattern(self, pattern: Union[Pattern, NodeMapper]):
        """Add a new pattern to the decision
        
        Args:
            pattern: Pattern object or NodeMapper to add
        """
        if isinstance(pattern, Pattern):
            self.patterns.append(pattern)
        elif isinstance(pattern, NodeMapper):
            self.patterns.append(self._convert_nodemapper_to_pattern(pattern))
        else:
            raise InvalidPatternError(pattern, "must be a Pattern object or NodeMapper")
        
        # Re-sort patterns by priority
        self.patterns.sort(key=lambda p: p.priority)
    
    def remove_pattern(self, pattern_or_index: Union[Pattern, int]):
        """Remove a pattern from the decision
        
        Args:
            pattern_or_index: Pattern object to remove or index
        """
        if isinstance(pattern_or_index, int):
            if 0 <= pattern_or_index < len(self.patterns):
                self.patterns.pop(pattern_or_index)
        else:
            try:
                self.patterns.remove(pattern_or_index)
            except ValueError:
                pass  # Pattern not found
    
    def get_pattern_info(self) -> List[dict]:
        """Get information about all patterns
        
        Returns:
            List of dictionaries with pattern information
        """
        return [
            {
                'type': pattern.__class__.__name__,
                'priority': pattern.priority,
                'target_node': getattr(pattern.target_node, 'name', str(pattern.target_node)),
                'repr': repr(pattern)
            }
            for pattern in self.patterns
        ]
    
    def __repr__(self) -> str:
        pattern_count = len(self.patterns)
        max_iter_info = f", max_iter={self.max_iter}" if self.max_iter else ""
        return f"EnhancedDecision({pattern_count} patterns{max_iter_info})"


# Convenience functions and syntax sugar

def decision(*patterns, max_iter: Optional[int] = None, name: str = None) -> EnhancedDecision:
    """Create an enhanced decision node with pattern matching
    
    Args:
        *patterns: Patterns to match against (condition >> node pairs)
        max_iter: Maximum iterations before falling back to default
        name: Optional name for the decision node
        
    Returns:
        EnhancedDecision instance
        
    Examples:
        decision(
            str >> string_handler,
            int >> number_handler,
            HTTPResponse(status_code=200) >> success_handler,
            lambda x: x > 100 >> big_value_handler,
            _ >> default_handler,
            max_iter=3
    """
    return EnhancedDecision(*patterns, max_iter=max_iter, name=name)


class DefaultMarker:
    """Marker class for default patterns"""
    
    def __rshift__(self, target_node):
        """Support _ >> node syntax"""
        from ..base_node import NodeType
        if isinstance(target_node, NodeType):
            target_node = target_node.node_instance
        return DefaultPattern(target_node)
    
    def __repr__(self):
        return "_"


# Global default marker instance
_ = DefaultMarker()


# Type pattern creation helper - we can't modify built-in types directly
# Instead, we'll provide wrapper functions and document the syntax

def create_type_pattern(type_class: type, target_node):
    """Create a ClassPattern for a type - use this instead of type >> node"""
    from ..base_node import NodeType
    if isinstance(target_node, NodeType):
        target_node = target_node.node_instance
    return ClassPattern(type_class, target_node)

def create_range_pattern(range_obj: range, target_node):
    """Create a RangePattern - use this instead of range >> node"""
    from ..base_node import NodeType
    if isinstance(target_node, NodeType):
        target_node = target_node.node_instance
    return RangePattern(range_obj, target_node)

# Note: For type matching, users should use:
# decision(
#     create_type_pattern(str, handler),  # Instead of str >> handler
#     "value" >> handler,                 # Direct values still work with >>
#     _ >> default_handler
# )