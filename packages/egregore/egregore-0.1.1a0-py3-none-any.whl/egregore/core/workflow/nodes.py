#%%
import asyncio
from egregore.core.workflow.base_node import Node, AsyncNode, node, decision
from typing import Literal, Dict, Callable, Any, Optional, TYPE_CHECKING, Type
from pydantic import BaseModel

if TYPE_CHECKING:
    from egregore.core.agent import Agent




class AgentNode(AsyncNode):
    """
    Workflow node that wraps Agent execution with intelligent parameter mapping.
    
    This node enables seamless integration of AI agents as workflow nodes,
    providing automatic state management and parameter mapping from previous
    workflow steps. The node name defaults to the agent's ID but can be overridden.
    
    Args:
        agent: The Agent instance to execute
        name: Optional node name override (uses agent.agent_id by default)
        run_type: Agent method to call ('call', 'acall', 'stream', etc.)
        **kwargs: Additional parameters to pass to the agent method
        
    Example:
        agent = Agent(provider="openai:gpt-4")
        
        # Correct usage - via agent.__call__:
        node1 = agent(temperature=0.8)  # Uses agent ID
        node2 = agent("custom_name", temperature=0.8)  # Custom name
        
        # Use in workflows:
        workflow = Sequence(
            load_data >>
            agent(temperature=0.1) >>
            agent("analyzer", temperature=0.8) >>
            save_results
        )
        
        # Note: Direct AgentNode() creation is internal - always use agent()
    """
    
    def __init__(self, 
                 agent: 'Agent', 
                 name: Optional[str] = None, 
                 run_type: str = "call", 
                 **kwargs) -> None:
        """
        Initialize AgentNode with agent and configuration.
        
        Args:
            agent: Agent instance to execute
            name: Optional node name override (uses agent.agent_id by default)
            run_type: Agent method to call (default: "call")
            **kwargs: Parameters to pass to agent method
            
        Raises:
            ValueError: If run_type is not a valid agent method
            TypeError: If agent is not a valid Agent instance
        """
        # Validate agent parameter
        if not hasattr(agent, 'call'):
            raise TypeError("agent must be a valid Agent instance with 'call' method")
            
        # Validate run_type parameter
        if not hasattr(agent, run_type):
            available_methods = [method for method in ['call', 'acall', 'chat', 'stream', 'astream'] 
                               if hasattr(agent, method)]
            raise ValueError(
                f"Agent does not have method '{run_type}'. "
                f"Available methods: {available_methods}"
            )
        
        # Use agent ID as default name, allow override
        self.node_name = name.strip() if name else agent.agent_id
        
        # Initialize parent with proper label
        super().__init__(label=self.node_name)
        
        # Store agent reference and configuration
        self.agent = agent
        self.run_type = run_type
        self.call_kwargs = kwargs
        
        # Log node creation for debugging
        debug_msg = f"Created AgentNode '{self.node_name}' with run_type='{run_type}' and kwargs: {self.call_kwargs}"
    
    async def _async_execute_impl(self, *args, **kwargs) -> Any:
        """
        Execute the agent with workflow integration and intelligent parameter mapping.
        
        This method leverages the intelligent parameter mapping system to automatically
        pass previous node outputs to the agent, with optional SharedState access.
        
        Args:
            *args: Input data from previous workflow step (automatically mapped)
            **kwargs: Additional execution parameters
            
        Returns:
            Agent response result
            
        Raises:
            AgentExecutionError: If agent execution fails
        """
        try:
            # Get input data from intelligent parameter mapping
            # The parameter mapping system automatically passes previous output as first arg
            input_data = args[0] if args else None
            
            # Get the agent method to call
            agent_method = getattr(self.agent, self.run_type)
            
            # Prepare method arguments
            # For agent methods, the first parameter is usually the message/input
            # Always provide input_data (may be None) as first argument
            call_args = [input_data]
            
            # Merge execution kwargs with stored kwargs (execution takes priority)
            merged_kwargs = {**self.call_kwargs, **kwargs}
            
            # Handle both async and sync agent methods
            if asyncio.iscoroutinefunction(agent_method):
                # Agent method is async - await it directly
                result = await agent_method(*call_args, **merged_kwargs)
            else:
                # Agent method is sync - run it in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    lambda: agent_method(*call_args, **merged_kwargs)
                )
            
            # Store result in workflow state for access by other nodes
            # This integrates with the workflow state management system
            if hasattr(self, 'state') and self.state is not None:
                self.state[self.node_name] = result
                
                # Notify observers for Cerebrum integration
                if hasattr(self.state, '_notify_state_change'):
                    notification_metadata = {
                        'result': result,
                        'agent_config': {
                            'run_type': self.run_type,
                            'parameters': self.call_kwargs
                        },
                        'input_data': str(args[0])[:100] + ('...' if args and len(str(args[0])) > 100 else '') if args else None,
                        'execution_type': 'async' if asyncio.iscoroutinefunction(getattr(self.agent, self.run_type)) else 'sync'
                    }
                    
                    try:
                        self.state._notify_state_change(
                            'agent_execution', 
                            self.node_name, 
                            notification_metadata
                        )
                    except Exception as notify_error:
                        # Don't let notification errors break execution
                        debug_msg = f"Observer notification failed for AgentNode '{self.node_name}': {notify_error}"
                
                # Debug logging of state storage
                debug_msg = f"Stored result for AgentNode '{self.node_name}' in workflow state"
            
            return result
            
        except Exception as e:
            # Store error information in state for debugging
            if hasattr(self, 'state') and self.state is not None:
                error_info = {
                    'error': str(e),
                    'agent_node': self.node_name,
                    'run_type': self.run_type,
                    'input_data': str(args[0])[:100] if args else None  # Truncated for safety
                }
                self.state[f"{self.node_name}_error"] = error_info
                
                # Notify observers of agent execution error
                if hasattr(self.state, '_notify_state_change'):
                    try:
                        self.state._notify_state_change(
                            'agent_error',
                            self.node_name,
                            error_info
                        )
                    except Exception as notify_error:
                        # Don't let notification errors mask the original error
                        pass
            
            raise AgentExecutionError(f"Agent '{self.node_name}' execution failed: {e}") from e
    
    def _execute_impl(self, *args, **kwargs) -> Any:
        """
        Synchronous wrapper for async agent execution.
        
        This method provides backward compatibility with synchronous workflow
        execution by running the async_execute method in an event loop.
        
        Args:
            *args: Input data from previous workflow step
            **kwargs: Additional execution parameters
            
        Returns:
            Agent response result
        """
        try:
            return asyncio.run(self._async_execute_impl(*args, **kwargs))
        except Exception as e:
            raise AgentExecutionError(f"Agent '{self.node_name}' execution failed: {e}") from e


class AgentExecutionError(Exception):
    """
    Raised when agent execution fails in workflow context.
    
    This exception provides context about which agent node failed and why,
    helping with debugging and error handling in complex workflows.
    """
    pass