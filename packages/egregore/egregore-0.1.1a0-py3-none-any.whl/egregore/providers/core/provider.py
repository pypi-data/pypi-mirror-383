"""General Purpose provider implementation - Supporting 30+ LLM providers via any-llm integration."""

from typing import (
    Iterator,
    AsyncIterator,
    Optional,
    Dict,
    Any,
    List,
    Union,
    Type,
    Set,
    TYPE_CHECKING,
    cast,
    Iterable,
)
import asyncio

if TYPE_CHECKING:
    from egregore.core.tool_calling.tool_declaration import ToolDeclaration

import logging
from .interface import BaseProvider, StreamChunk
from egregore.core.messaging import ProviderResponse, ProviderThread
from .structured_output import StructuredResponse

from .model_manager import GeneralPurposeModelManager
from .translation import GeneralPurposeTranslator
from .config import validate_provider_config, validate_model_config
from .exceptions import map_anyllm_error
from ..data.data_manager import data_manager
from .interceptors import (
    InterceptorRegistry,
    AnthropicOAuthInterceptor,
    GoogleOAuthInterceptor,
    OpenRouterInterceptor,
)

logger = logging.getLogger(__name__)


class GeneralPurposeProvider(BaseProvider):
    """General Purpose provider implementation supporting 30+ providers via any-llm."""

    def __init__(self, provider_name: str, **config):
        """Initialize General Purpose provider with specific provider backend.

        Args:
            provider_name: Name of the specific provider (e.g., 'anthropic', 'google', 'openrouter')
            **config: Provider configuration parameters
        """
        # Validate and store the provider name BEFORE calling super()
        self.provider_name = data_manager.validate_provider_name(provider_name)

        super().__init__(**config)

        # Initialize components following OpenAI pattern
        self.translator = GeneralPurposeTranslator(
            provider_name=self.provider_name, model_manager=self.model_manager
        )

        # Initialize interceptor registry
        self.interceptor_registry = InterceptorRegistry()
        self._initialize_interceptors()

        # Initialize any-llm client (will be created on first use)
        self._any_llm_client = None
        self._cleanup_tasks = []

    # Required BaseProvider abstract methods (same signatures as OpenAI)

    def call(
        self,
        provider_thread: ProviderThread,
        model: Optional[str] = None,
        tools: Optional[List["ToolDeclaration"]] = None,
        result_type: Optional[Type[Any]] = None,
        max_retries: int = 3,
        **kwargs,
    ) -> Union[ProviderResponse, StructuredResponse]:
        """Synchronous completion with optional structured output."""
        try:
            # Validate and process parameters (following OpenAI pattern)
            processed_params = self._process_parameters(model, **kwargs)
            final_model = processed_params.pop("model")

            # Handle structured output BEFORE translation
            if result_type:
                structured_format = self.format_structured_output(result_type)
                if structured_format:
                    processed_params["response_format"] = structured_format
                    logger.debug(f"Added structured output format for {result_type}")
                else:
                    logger.warning(
                        f"Could not create structured format for {result_type}"
                    )

            # Add tools to processed_params if provided
            if tools:
                formatted_tools = self.format_tools(tools)
                processed_params["tools"] = formatted_tools
                logger.debug(f"Added {len(formatted_tools)} tools to request")

                # Model selection policy handled at config/planning level; do not auto-switch here

            # Use translator to format request to any-llm format
            anyllm_request = self.format_provider_thread(
                provider_thread=provider_thread, model=final_model, **processed_params
            )

            # Apply interceptors to the request
            anyllm_request = self.interceptor_registry.apply_request_interceptors(
                anyllm_request
            )

            import any_llm

            logger.info(
                f"Making any-llm API call with provider {self.provider_name} and model {final_model}"
            )

            # Handle sync call in async context - any_llm detects running event loop
            try:
                asyncio.get_running_loop()
                # Event loop running - use thread to avoid "sync API in async context" error
                import threading

                result: List[Any] = [None]
                exception: List[Optional[Exception]] = [None]

                def run_completion():
                    try:
                        result[0] = any_llm.completion(**anyllm_request)
                    except Exception as e:
                        exception[0] = e

                thread = threading.Thread(target=run_completion)
                thread.start()
                thread.join()

                if exception[0]:
                    raise exception[0]
                response = result[0]
            except RuntimeError:
                # No event loop - safe to call directly
                response = any_llm.completion(**anyllm_request)

            # Convert response back to corev2 format
            provider_response = self.format_provider_response(response)

            # Handle structured output if needed
            if result_type is not None:
                return self._handle_structured_result(provider_response, result_type)

            return provider_response

        except Exception as e:
            mapped_error = map_anyllm_error(e, self.provider_name)
            logger.error(
                f"AnyLLM API call failed for {self.provider_name}: {mapped_error}"
            )
            raise mapped_error

    async def acall(
        self,
        provider_thread: ProviderThread,
        model: Optional[str] = None,
        tools: Optional[List["ToolDeclaration"]] = None,
        result_type: Optional[Type[Any]] = None,
        max_retries: int = 3,
        **kwargs,
    ) -> Union[ProviderResponse, StructuredResponse]:
        """Asynchronous completion with optional structured output."""
        try:
            # Validate and process parameters (following OpenAI pattern)
            processed_params = self._process_parameters(model, **kwargs)
            final_model = processed_params.pop("model")

            # Handle structured output BEFORE translation
            if result_type:
                structured_format = self.format_structured_output(result_type)
                if structured_format:
                    processed_params["response_format"] = structured_format
                    logger.debug(f"Added structured output format for {result_type}")
                else:
                    logger.warning(
                        f"Could not create structured format for {result_type}"
                    )

            # Add tools to processed_params if provided
            if tools:
                formatted_tools = self.format_tools(tools)
                processed_params["tools"] = formatted_tools
                logger.debug(f"Added {len(formatted_tools)} tools to request")

                # Model selection policy handled at config/planning level; do not auto-switch here

            # Use translator to format request to any-llm format
            anyllm_request = self.format_provider_thread(
                provider_thread=provider_thread, model=final_model, **processed_params
            )

            # Make async any-llm API call
            import any_llm

            logger.info(
                f"Making async any-llm API call with provider {self.provider_name} and model {final_model}"
            )

            # Check if any-llm supports async completion
            if hasattr(any_llm, "acompletion"):
                response = await any_llm.acompletion(**anyllm_request)
            else:
                # Fallback to sync call in thread pool
                import asyncio

                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, lambda: any_llm.completion(**anyllm_request)
                )

            # Convert response back to corev2 format
            provider_response = self.format_provider_response(response)

            # Handle structured output if needed
            if result_type is not None:
                return self._handle_structured_result(provider_response, result_type)

            return provider_response

        except Exception as e:
            mapped_error = map_anyllm_error(e, self.provider_name)
            logger.error(
                f"Async AnyLLM API call failed for {self.provider_name}: {mapped_error}"
            )
            raise mapped_error

    def stream(
        self,
        provider_thread: ProviderThread,
        model: Optional[str] = None,
        tools: Optional[List["ToolDeclaration"]] = None,
        max_retries: int = 3,
        **kwargs,
    ) -> Iterator[StreamChunk]:
        """Synchronous streaming completion."""
        try:
            # Validate and process parameters
            processed_params = self._process_parameters(model, **kwargs)
            final_model = processed_params.pop("model")
            processed_params["stream"] = True  # Force streaming

            # Add tools to processed_params if provided
            if tools:
                logger.debug(
                    "Tools provided for streaming - tool calls may appear in streaming chunks"
                )
                # Model selection policy handled at config/planning level; do not auto-switch here

            # Use translator to format request to any-llm format
            anyllm_request = self.format_provider_thread(
                provider_thread=provider_thread, model=final_model, **processed_params
            )

            # Make streaming any-llm API call
            import any_llm

            logger.info(
                f"Starting any-llm streaming with provider {self.provider_name} and model {final_model}"
            )

            # Check if any-llm supports streaming
            if hasattr(any_llm, "completion") and "stream" in anyllm_request:
                # Handle sync streaming in async context - any_llm detects running event loop
                try:
                    asyncio.get_running_loop()
                    # Event loop running - use thread to avoid "sync API in async context" error
                    import threading
                    import queue

                    chunk_queue = queue.Queue()

                    def run_streaming():
                        try:
                            stream = any_llm.completion(**anyllm_request)
                            for chunk in stream:
                                chunk_queue.put(chunk)
                            chunk_queue.put(None)  # End signal
                        except Exception as e:
                            chunk_queue.put(e)  # Exception signal

                    thread = threading.Thread(target=run_streaming)
                    thread.start()

                    # Yield chunks as they come
                    accumulated_content = ""
                    while True:
                        chunk = chunk_queue.get()
                        if chunk is None:  # End signal
                            break
                        if isinstance(chunk, Exception):  # Exception signal
                            raise chunk

                        try:
                            stream_chunk = self._convert_anyllm_chunk_to_stream_chunk(
                                chunk, accumulated_content
                            )
                            accumulated_content = stream_chunk.content
                            yield stream_chunk
                        except Exception as chunk_error:
                            logger.warning(
                                f"Error processing streaming chunk: {chunk_error}"
                            )
                            continue

                    thread.join()

                except RuntimeError:
                    # No event loop - safe to call directly
                    stream = any_llm.completion(**anyllm_request)

                # Convert streaming chunks to StreamChunk objects
                accumulated_content = ""
                for chunk in stream:
                    try:
                        stream_chunk = self._convert_anyllm_chunk_to_stream_chunk(
                            chunk, accumulated_content
                        )
                        accumulated_content = stream_chunk.content
                        yield stream_chunk
                    except Exception as chunk_error:
                        logger.warning(
                            f"Error processing streaming chunk: {chunk_error}"
                        )
                        continue
            else:
                # Fallback: make non-streaming call and yield as single chunk
                logger.warning(
                    "Streaming not supported, falling back to single response"
                )
                anyllm_request = dict(
                    anyllm_request
                )  # ensure mutable plain dict for item assignment
                anyllm_request["stream"] = False
                response = any_llm.completion(**anyllm_request)

                # Convert full response to single StreamChunk
                provider_response = self.format_provider_response(response)
                content_text = self._extract_content_text(provider_response)

                yield StreamChunk(
                    delta=content_text,
                    content=content_text,
                    finish_reason="stop",
                    tool_calls=None,
                    partial_tool_calls=None,
                    tool_call_state=None,
                    tool_call_id=None,
                    function_name=None,
                    arguments_delta=None,
                    tool_result=None,
                    usage=None,
                    model=final_model,
                    metadata={
                        "provider": self.provider_name,
                        "model": final_model,
                        "streaming": False,
                        "fallback": True,
                    },
                )

        except Exception as e:
            mapped_error = map_anyllm_error(e, self.provider_name)
            logger.error(
                f"AnyLLM streaming failed for {self.provider_name}: {mapped_error}"
            )
            raise mapped_error

    async def astream(
        self,
        provider_thread: ProviderThread,
        model: Optional[str] = None,
        tools: Optional[List["ToolDeclaration"]] = None,
        max_retries: int = 3,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        """Asynchronous streaming completion."""
        try:
            # Validate and process parameters
            processed_params = self._process_parameters(model, **kwargs)
            final_model = processed_params.pop("model")
            processed_params["stream"] = True  # Force streaming

            # Add tools to processed_params if provided
            if tools:
                logger.debug(
                    "Tools provided for async streaming - tool calls may appear in streaming chunks"
                )
                # Model selection policy handled at config/planning level; do not auto-switch here

            # Use translator to format request to any-llm format
            anyllm_request = self.format_provider_thread(
                provider_thread=provider_thread, model=final_model, **processed_params
            )

            # Make async streaming any-llm API call
            import any_llm
            import asyncio

            logger.info(
                f"Starting async any-llm streaming with provider {self.provider_name} and model {final_model}"
            )

            # Check if any-llm supports async streaming
            if hasattr(any_llm, "acompletion"):
                # Try async streaming
                try:
                    stream = await any_llm.acompletion(**anyllm_request)

                    # Convert streaming chunks to StreamChunk objects
                    accumulated_content = ""
                    # Check if stream is async iterable
                    try:
                        # Try async iteration - check for None and proper async iterator
                        if stream is not None and hasattr(stream, '__aiter__') and callable(getattr(stream, '__aiter__', None)):
                            # Cast to AsyncIterator for type checker only after runtime validation
                            async_stream = cast(AsyncIterator[Any], stream)
                            async for chunk in async_stream:
                                try:
                                    stream_chunk = self._convert_anyllm_chunk_to_stream_chunk(
                                        chunk, accumulated_content
                                    )
                                    accumulated_content = stream_chunk.content
                                    yield stream_chunk
                                except Exception as chunk_error:
                                    logger.warning(
                                        f"Error processing async streaming chunk: {chunk_error}"
                                    )
                                    continue
                        else:
                            # Handle non-streaming response
                            logger.warning("Response is not async iterable, treating as single response")
                            provider_response = self.format_provider_response(stream)
                            content_text = self._extract_content_text(provider_response)
                            yield StreamChunk(
                                delta=content_text,
                                content=content_text,
                                finish_reason="stop",
                                tool_calls=None,
                                partial_tool_calls=None,
                                tool_call_state=None,
                                tool_call_id=None,
                                function_name=None,
                                arguments_delta=None,
                                tool_result=None,
                                usage=None,
                                model=None,
                                metadata={"provider": self.provider_name, "fallback": True}
                            )
                    except Exception as stream_error:
                        logger.error(f"Error processing stream: {stream_error}")
                        raise

                except Exception as async_error:
                    logger.warning(
                        f"Async streaming failed, falling back to sync in thread pool: {async_error}"
                    )
                    # Fallback to sync streaming in thread pool
                    loop = asyncio.get_event_loop()

                    def sync_stream():
                        return list(
                            self.stream(
                                provider_thread, model, tools, max_retries, **kwargs
                            )
                        )

                    chunks = await loop.run_in_executor(None, sync_stream)
                    for chunk in chunks:
                        yield chunk

            else:
                # Fallback to sync streaming in thread pool
                logger.info("Using sync streaming in thread pool for async astream")
                loop = asyncio.get_event_loop()

                def sync_stream():
                    return list(
                        self.stream(
                            provider_thread, model, tools, max_retries, **kwargs
                        )
                    )

                chunks = await loop.run_in_executor(None, sync_stream)
                for chunk in chunks:
                    yield chunk

        except Exception as e:
            mapped_error = map_anyllm_error(e, self.provider_name)
            logger.error(
                f"Async AnyLLM streaming failed for {self.provider_name}: {mapped_error}"
            )
            raise mapped_error

    def validate_provider_config(self, config: Dict[str, Any]) -> None:
        """Validate provider-specific configuration."""
        validate_provider_config(self.provider_name, config)

    def validate_model_config(self, config: Dict[str, Any]) -> None:
        """Validate model-specific configuration."""
        validate_model_config(self.provider_name, config)

    def _create_model_manager(self) -> GeneralPurposeModelManager:
        """Create model manager for this provider."""
        return GeneralPurposeModelManager(
            provider_name=self.provider_name, config=self.config
        )

    def get_supported_params(self) -> Set[str]:
        """Get supported parameters for this provider."""
        # Fallback to empty set; model managers may not expose this method
        getter = getattr(self.model_manager, "get_supported_params", None)
        if callable(getter):
            try:
                result = getter()
                if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
                    # Cast to Iterable for type checker
                    iterable_result = cast(Iterable[str], result)
                    return set(iterable_result)
                else:
                    return set()
            except Exception:
                return set()
        return set()

    async def refresh_models(self) -> None:
        """Refresh model information."""
        await self.model_manager.refresh_models()

    def format_provider_thread(
        self, provider_thread: ProviderThread, **kwargs
    ) -> Dict[str, Any]:
        """Format ProviderThread to any-llm format."""
        return self.translator.translate_to_native(provider_thread, **kwargs)

    def format_provider_response(self, native_response: Any) -> ProviderResponse:
        """Format any-llm response to ProviderResponse."""
        return self.translator.translate_from_native(native_response)

    def format_structured_output(
        self, result_type: Type[Any], **provider_options
    ) -> Optional[Dict[str, Any]]:
        """Create any-llm structured output format specification."""
        return self.translator._create_response_format(result_type)

    def format_tools(self, tools: List["ToolDeclaration"]) -> List[Dict[str, Any]]:
        """Format ToolDeclarations to any-llm tool format."""
        if not tools:
            return []

        formatted_tools = []

        for tool in tools:
            # Convert to OpenAI-compatible format (any-llm uses OpenAI format)
            tool_spec = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or f"Execute {tool.name}",
                },
            }

            # Add parameters schema if available
            if tool.parameters:
                tool_spec["function"]["parameters"] = tool.parameters.to_openai_schema()
            else:
                # Default empty parameters schema
                tool_spec["function"]["parameters"] = {
                    "type": "object",
                    "properties": {},
                    "required": [],
                }

            formatted_tools.append(tool_spec)
            logger.debug(f"Formatted tool {tool.name} for {self.provider_name}")

        logger.info(f"Formatted {len(formatted_tools)} tools for {self.provider_name}")
        return formatted_tools

    # Provider-specific helper methods

    def _get_any_llm_client(self):
        """Get or create any-llm client for this provider."""
        if self._any_llm_client is None:
            # Any-llm client initialization handled by unified provider architecture
            # Client creation is managed through the interceptor registry and translator
            pass
        return self._any_llm_client

    def _process_parameters(self, model: Optional[str], **kwargs) -> Dict[str, Any]:
        """Process and validate parameters following OpenAI pattern."""
        # Get model from parameter hierarchy: call param > config default > fallback
        final_model = model or self.config.get("default_model", "gpt-3.5-turbo")

        # Start with call-specific parameters
        processed = kwargs.copy()

        # Set final model and provider
        processed["model"] = final_model
        processed["provider"] = self.provider_name

        # Validate parameters
        self.validate_model_config(processed)

        logger.debug(f"Processed parameters for {self.provider_name}:{final_model}")
        return processed

    def _handle_structured_result(
        self, provider_response: ProviderResponse, result_type: Type[Any]
    ) -> Union[ProviderResponse, StructuredResponse]:
        """Handle structured output result with smart parsing."""
        try:
            # Extract text content from ProviderResponse
            content_text = self._extract_content_text(provider_response)

            # Check if content is already conformant to expected type
            if isinstance(content_text, result_type):
                return StructuredResponse(
                    parsed_result=content_text,
                    raw_response=provider_response,
                    result_type=result_type,
                    fallback_used="direct",
                    confidence=1.0,
                    retries_used=0,
                    parse_time=0.0,
                    metadata={"native_support": True},
                )

            # Try to parse JSON content
            if self._is_json_string(content_text):
                try:
                    import json
                    import time

                    start_time = time.time()

                    json_data = json.loads(content_text)

                    # Try to create Pydantic model instance
                    if hasattr(result_type, "model_validate"):
                        # Pydantic v2
                        parsed_result = result_type.model_validate(json_data)
                    elif hasattr(result_type, "parse_obj"):
                        # Pydantic v1
                        parsed_result = result_type.parse_obj(json_data)
                    else:
                        # Direct instantiation for non-Pydantic types
                        parsed_result = (
                            result_type(**json_data)
                            if isinstance(json_data, dict)
                            else json_data
                        )

                    parse_time = time.time() - start_time

                    return StructuredResponse(
                        parsed_result=parsed_result,
                        raw_response=provider_response,
                        result_type=result_type,
                        fallback_used="json_parse",
                        confidence=0.9,
                        retries_used=0,
                        parse_time=parse_time,
                        metadata={"any_llm_support": True},
                    )

                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    logger.warning(f"Failed to parse JSON structured output: {e}")

            # Fallback: return original response
            logger.warning(
                f"Could not parse structured output for {result_type}, returning raw response"
            )
            return provider_response

        except Exception as e:
            logger.error(f"Error handling structured result: {e}")
            return provider_response

    def _extract_content_text(self, provider_response: ProviderResponse) -> str:
        """Extract text content from ProviderResponse."""
        content_parts = []
        for content_block in provider_response.content:
            if hasattr(content_block, "content") and isinstance(
                getattr(content_block, "content", None), str
            ):
                content_parts.append(content_block.content)  # type: ignore
        return "\n".join(content_parts).strip()

    def _is_json_string(self, text: str) -> bool:
        """Check if text appears to be JSON."""
        text = text.strip()
        return (text.startswith("{") and text.endswith("}")) or (
            text.startswith("[") and text.endswith("]")
        )

    def _initialize_interceptors(self) -> None:
        """Initialize provider-specific interceptors."""
        # Add Anthropic OAuth interceptor for anthropic provider
        if self.provider_name.lower() == "anthropic":
            oauth_interceptor = AnthropicOAuthInterceptor(
                provider_name=self.provider_name, **self.config
            )
            self.interceptor_registry.register(oauth_interceptor)
            logger.info("Registered AnthropicOAuthInterceptor for Anthropic provider")

        # Add Google OAuth interceptor for google provider
        if self.provider_name.lower() == "google":
            google_oauth_interceptor = GoogleOAuthInterceptor(
                provider_name=self.provider_name, **self.config
            )
            self.interceptor_registry.register(google_oauth_interceptor)
            logger.info("Registered GoogleOAuthInterceptor for Google provider")

        # Add OpenRouter routing interceptor for openrouter provider
        if self.provider_name.lower() == "openrouter":
            routing_interceptor = OpenRouterInterceptor(
                provider_name=self.provider_name, **self.config
            )
            self.interceptor_registry.register(routing_interceptor)
            logger.info("Registered OpenRouterInterceptor for OpenRouter provider")

        # Future interceptors can be added here as needed

    def _convert_anyllm_chunk_to_stream_chunk(
        self, anyllm_chunk: Any, accumulated_content: str
    ) -> StreamChunk:
        """Convert any-llm streaming chunk to StreamChunk format."""
        try:
            # Handle both dict and any-llm object chunks
            if hasattr(anyllm_chunk, "model_dump"):
                chunk_dict = anyllm_chunk.model_dump()
            elif hasattr(anyllm_chunk, "dict"):
                chunk_dict = anyllm_chunk.dict()
            elif isinstance(anyllm_chunk, dict):
                chunk_dict = anyllm_chunk
            else:
                chunk_dict = dict(anyllm_chunk)

            # Extract delta content from chunk
            delta_content = ""
            choices = chunk_dict.get("choices", [])

            if choices:
                first_choice = choices[0]
                delta = first_choice.get("delta", {})

                # Extract text content from delta
                if isinstance(delta, dict) and "content" in delta:
                    delta_content = delta["content"] or ""
                elif isinstance(delta, str):
                    delta_content = delta

            # Update accumulated content
            new_accumulated = accumulated_content + delta_content

            # Extract finish reason
            finish_reason = None
            if choices:
                finish_reason = choices[0].get("finish_reason")

            # Create StreamChunk
            return StreamChunk(
                delta=delta_content,
                content=new_accumulated,
                finish_reason=finish_reason,
                tool_calls=None,
                partial_tool_calls=None,
                tool_call_state=None,
                tool_call_id=None,
                function_name=None,
                arguments_delta=None,
                tool_result=None,
                usage=chunk_dict.get("usage"),
                model=chunk_dict.get("model"),
                metadata={
                    "provider": self.provider_name,
                    "chunk_id": chunk_dict.get("id"),
                    "streaming": True,
                    "model": chunk_dict.get("model"),
                },
            )

        except Exception as e:
            logger.warning(f"Error converting any-llm chunk: {e}")
            # Fallback to basic chunk
            return StreamChunk(
                delta="",
                content=accumulated_content,
                finish_reason="error",
                tool_calls=None,
                partial_tool_calls=None,
                tool_call_state=None,
                tool_call_id=None,
                function_name=None,
                arguments_delta=None,
                tool_result=None,
                usage=None,
                model=None,
                metadata={"provider": self.provider_name, "error": str(e)},
            )
    
    async def cleanup(self):
        """
        Clean up provider resources and HTTP clients.
        
        This method should be called before the event loop shuts down
        to properly close HTTP connections and avoid cleanup errors.
        """
        try:
            # Cancel any cleanup tasks we've tracked
            import asyncio
            for task in self._cleanup_tasks:
                if isinstance(task, asyncio.Task) and not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    except Exception:
                        pass  # Ignore cleanup errors
            
            self._cleanup_tasks.clear()
            
            # Force cleanup of any-llm internal HTTP clients
            # any-llm uses httpx internally, which creates background tasks
            try:
                import any_llm
                # If any-llm has an internal client, try to close it
                if hasattr(any_llm, '_client') and any_llm._client:
                    if hasattr(any_llm._client, 'aclose'):
                        await any_llm._client.aclose()
                    any_llm._client = None
                
                # Clear any cached client instances
                if hasattr(any_llm, '_async_client') and any_llm._async_client:
                    if hasattr(any_llm._async_client, 'aclose'):
                        await any_llm._async_client.aclose()
                    any_llm._async_client = None
                        
            except ImportError:
                pass  # any_llm not available
            except Exception as e:
                # Silently handle cleanup errors
                pass
                
            # Clear our own client reference
            self._any_llm_client = None
            
        except Exception:
            # Never let cleanup errors propagate
            pass
