import json
import os.path
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List, Tuple, Set
import importlib.util
import inspect
import uuid
from dataclasses import asdict

from ai_six.agent.config import Config
from ai_six.object_model import (
    LLMProvider,
    UserMessage,
    AssistantMessage,
    SystemMessage,
    ToolMessage,
    ToolCall,
)
from ai_six.object_model import Usage
from ai_six.agent.session import Session
from ai_six.agent.session_manager import SessionManager
from ai_six.agent import tool_manager
from ai_six.agent.config import ToolConfig
from ai_six.tools.memory.list_sessions import ListSessions
from ai_six.tools.memory.load_session import LoadSession
from ai_six.tools.memory.get_session_id import GetSessionId
from ai_six.tools.memory.delete_session import DeleteSession
from ai_six.agent.summarizer import Summarizer
from ai_six.llm_providers.model_info import get_context_window_size


def generate_tool_call_id(original_id: Optional[str] = None) -> str:
    """
    Generate a UUID for tool call identification.

    Args:
        original_id: Optional original ID to preserve for debugging

    Returns:
        A string ID for the tool call, prefixed with ``tool_``
    """
    return f"tool_{uuid.uuid4().hex}"


class Agent:
    """Unified Agent class that handles LLM interactions, tool execution, and session management."""

    # Class-level set to track all agent names for uniqueness
    _all_agent_names: Set[str] = set()

    def __init__(self, config: Config) -> None:
        self.default_model_id = config.default_model_id
        self.system_prompt = config.system_prompt
        self.name = config.name
        self.description = config.description
        self._agent_configs = config.agents or []

        # Check name uniqueness if name is provided
        if self.name:
            if self.name in Agent._all_agent_names:
                raise ValueError(
                    f"Agent name '{self.name}' is not unique. An agent with this name already exists."
                )
            Agent._all_agent_names.add(self.name)

        # Store threshold ratio and calculate token threshold based on default model
        self.summary_threshold_ratio = config.summary_threshold_ratio
        context_window_size = get_context_window_size(self.default_model_id)
        self.token_threshold = int(context_window_size * config.summary_threshold_ratio)

        # Find LLM providers directory
        llm_providers_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "llm_providers"
        )
        assert os.path.isdir(llm_providers_dir), (
            f"LLM providers directory not found: {llm_providers_dir}"
        )

        # Discover available LLM providers
        self.llm_providers = Agent.discover_llm_providers(
            llm_providers_dir, config.provider_config
        )
        if not self.llm_providers:
            raise ValueError("No LLM providers found or initialized")
        self.model_provider_map = {
            model_id: llm_provider
            for llm_provider in self.llm_providers
            for model_id in llm_provider.models
        }

        # Initialize session and session manager first
        self.session_manager = SessionManager(config.memory_dir)
        self.session = self._create_new_session(config.memory_dir)

        # Discover and initialize all tools using ToolManager
        tool_config = ToolConfig.from_agent_config(config)
        self.tool_dict = tool_manager.get_tool_dict(tool_config, self._agent_configs)
        
        # Configure A2A integration if A2A tools are present (after session is created)
        def inject_system_message(message: SystemMessage):
            """Inject A2A interim messages into session."""
            self.session.add_message(message)
            
        self.tool_dict = tool_manager.configure_a2a_integration(
            self.tool_dict, 
            config.memory_dir, 
            self.session.session_id, 
            inject_system_message
        )

        # Session-related attributes
        self.checkpoint_interval = config.checkpoint_interval
        self.message_count_since_checkpoint = 0

        # Instantiate the summarizer with the first LLM provider
        self.summarizer = Summarizer(self.llm_providers[0])

        # Register memory tools with the agent
        self._register_memory_tools()

        # Load previous session if session_id is provided and exists
        if config.session_id:
            available_sessions = self.session_manager.list_sessions()
            if config.session_id in available_sessions:
                self.session = Session(config.memory_dir)  # Create a new session object
                self.session.load(config.session_id)  # Load from disk

    @classmethod
    def from_config_file(cls, config_file: str) -> "Agent":
        """Create an Agent instance from a configuration file.

        Parameters
        ----------
        config_file : str
            Path to the configuration file (json, yaml, or toml)

        Returns
        -------
        Agent
            A configured Agent instance
        """
        config = Config.from_file(config_file)
        return cls(config)

    @staticmethod
    def discover_llm_providers(
        llm_providers_dir: str, provider_config: Dict[str, dict[str, dict]]
    ) -> List[LLMProvider]:
        providers = []

        base_path = Path(llm_providers_dir).resolve()

        # Determine if we're in development mode (py/ai_six) or installed package (ai_six)
        # Check if path contains 'py/ai_six' or just 'ai_six'
        path_parts = base_path.parts
        is_development = 'py' in path_parts and path_parts[path_parts.index('py') + 1] == 'ai_six'

        if is_development:
            # Development structure: /path/to/ai-six/py/ai_six/llm_providers
            # Find the 'py' directory
            py_index = path_parts.index('py')
            module_root_path = Path(*path_parts[:py_index + 1])
            base_module = "py.ai_six.llm_providers"
        else:
            # Installed package structure: /path/to/site-packages/ai_six/llm_providers
            # Find the 'ai_six' directory
            try:
                ai_six_index = path_parts.index('ai_six')
                module_root_path = Path(*path_parts[:ai_six_index])
                base_module = "ai_six.llm_providers"
            except ValueError:
                # Fallback: use parent of llm_providers as ai_six, and its parent as root
                module_root_path = base_path.parent.parent
                base_module = "ai_six.llm_providers"

        # Walk through all .py files in the directory (non-recursive)
        for file_path in base_path.glob("*.py"):
            if file_path.name == "__init__.py":
                continue

            try:
                # Get the path relative to the Python root dir
                relative_path = file_path.relative_to(module_root_path)

                # Convert path parts to a valid Python module name
                module_name = ".".join(relative_path.with_suffix("").parts)

                # Validate it starts with the expected base_module prefix
                expected_prefix = base_module.split('.')[0]  # 'py' or 'ai_six'
                if not module_name.startswith(expected_prefix):
                    continue

                # Load module from file
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec is None:
                    continue

                module = importlib.util.module_from_spec(spec)

                try:
                    spec.loader.exec_module(module)
                except Exception as e:
                    continue

                # Inspect module for subclasses of LLMProvider
                for name, clazz in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(clazz, LLMProvider)
                        and clazz.__module__ != LLMProvider.__module__
                    ):
                        try:
                            # Get configuration for this provider type
                            provider_type = name.lower().replace("provider", "")
                            conf = provider_config.get(provider_type, {})

                            # Instantiate provider with configuration
                            provider = clazz(**conf)
                            providers.append(provider)
                        except Exception as e:
                            continue

            except Exception as e:
                # Handle any errors that occur during module loading
                print(f"Error loading module {module_name}: {e}")
                continue

        return providers

    def _create_new_session(self, memory_dir: str) -> Session:
        """Create a new session with optional system prompt."""
        session = Session(memory_dir)
        if self.system_prompt:
            system_message = SystemMessage(content=self.system_prompt)
            session.add_message(system_message)
        return session

    def _register_memory_tools(self) -> None:
        """Register memory management tools with the agent."""
        # Create tool instances with a reference to the agent
        list_sessions_tool = ListSessions(self)
        load_session_tool = LoadSession(self)
        get_session_id_tool = GetSessionId(self)
        delete_session_tool = DeleteSession(self)

        # Add tools to the agent's tool dictionary
        self.tool_dict[list_sessions_tool.name] = list_sessions_tool
        self.tool_dict[load_session_tool.name] = load_session_tool
        self.tool_dict[get_session_id_tool.name] = get_session_id_tool
        self.tool_dict[delete_session_tool.name] = delete_session_tool


    def _execute_tools(
        self,
        tool_calls: List[ToolCall],
        on_tool_call_func: Optional[Callable[[str, Dict[str, Any], str], None]] = None,
    ) -> Tuple[List[ToolCall], List[ToolMessage]]:
        """
        Execute a list of tool calls and return the corresponding tool messages.

        Args:
            tool_calls: List of tool calls to execute
            on_tool_call_func: Optional callback function for tool calls

        Returns:
            Tuple of (updated_tool_calls, tool_messages)
        """
        # Create a mapping of original IDs to new UUIDs if needed
        id_mapping = {}

        for tool_call in tool_calls:
            # Check if we need to replace the ID with a UUID
            if not tool_call.id or len(tool_call.id) < 32:  # Simple check for non-UUID
                new_id = generate_tool_call_id(tool_call.id)
                id_mapping[tool_call.id] = new_id

        # Update tool call IDs if needed
        updated_tool_calls = []
        for tool_call in tool_calls:
            updated_id = tool_call.id
            if tool_call.id in id_mapping:
                updated_id = id_mapping[tool_call.id]

            updated_tool_calls.append(
                ToolCall(
                    id=updated_id,
                    name=tool_call.name,
                    arguments=tool_call.arguments,
                    required=tool_call.required,
                )
            )

        # Execute tools and create tool messages
        tool_messages = []
        for tool_call in tool_calls:
            tool = self.tool_dict.get(tool_call.name)
            if tool is None:
                raise RuntimeError(f"Unknown tool: {tool_call.name}")

            try:
                kwargs = json.loads(tool_call.arguments)
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"Invalid arguments JSON for tool '{tool_call.name}'"
                )

            # Get the potentially updated tool call ID
            tool_call_id = tool_call.id
            if tool_call.id in id_mapping:
                tool_call_id = id_mapping[tool_call.id]

            try:
                # Set callback for AgentTools if available
                if (
                    hasattr(tool, "set_tool_call_callback")
                    and on_tool_call_func is not None
                ):
                    tool.set_tool_call_callback(on_tool_call_func)

                # Execute the tool
                tool_result = tool.run(**kwargs)

                # Call the callback if provided
                if on_tool_call_func is not None:
                    on_tool_call_func(tool_call.name, kwargs, str(tool_result))

                # Create the tool message
                tool_message = ToolMessage(
                    content=str(tool_result),
                    name=tool_call.name,
                    tool_call_id=tool_call_id,
                )
            except Exception as e:
                tool_message = ToolMessage(
                    content=str(e),
                    name=tool_call.name,
                    tool_call_id=tool_call_id,
                )

            tool_messages.append(tool_message)

        return updated_tool_calls, tool_messages

    def _checkpoint_if_needed(self) -> None:
        """Check if we need to save a checkpoint and do so if needed."""
        self.message_count_since_checkpoint += 1

        # Only save if we've reached the checkpoint interval exactly
        if self.message_count_since_checkpoint == self.checkpoint_interval:
            self.session.save()
            self.message_count_since_checkpoint = 0

            # Check and summarize if above token threshold (80% of context window)
            total_tokens = (
                self.session.usage.input_tokens + self.session.usage.output_tokens
            )
            if total_tokens >= self.token_threshold:
                context_window_size = get_context_window_size(self.default_model_id)
                print(
                    f"Session tokens ({total_tokens}) have reached {self.summary_threshold_ratio * 100}% of context window ({context_window_size}). Summarizing..."
                )
                self._summarize_and_reset_session()

    def _summarize_and_reset_session(self) -> None:
        """
        Summarize the current session, save detailed logs, and create a new session with the summary.
        This is triggered when the session token count exceeds the threshold (80% of context window by default).
        """
        # Save the current session before summarizing (ensure we have a complete record)
        self.session.save()

        # Generate summary using the first provider's model
        summary = self.summarizer.summarize(
            self.session.messages, self.default_model_id
        )

        # Append current session to the detailed log
        self._append_to_detailed_log(self.session.session_id, summary)

        # Store the old session ID for reference
        old_session_id = self.session.session_id

        # Create a new session with summary as the starting point
        new_session = self._create_new_session(self.session.memory_dir)
        summary_message = SystemMessage(
            content=f"Summary of previous conversation (session {old_session_id}):\n\n{summary}"
        )

        # Add an estimated token count for the summary message to track usage
        # This is an approximation - in a production system you might want to use a tokenizer
        estimated_summary_tokens = len(summary.split()) * 1.3  # Simple approximation

        # Add the message with usage info
        new_session.add_message(summary_message)

        # Create a new Usage object with the estimated summary tokens (Usage is immutable)
        new_session.usage = Usage(
            input_tokens=int(estimated_summary_tokens), output_tokens=0
        )

        # Update session reference and ID
        self.session = new_session
        self.active_session_id = new_session.session_id

        # Save the new session immediately
        self.session.save()

        print(
            f"Session summarized and reset. Previous session: {old_session_id}, New session: {new_session.session_id}"
        )

    def _append_to_detailed_log(self, session_id: str, summary: str) -> None:
        """
        Save detailed session logs including all messages and the generated summary.
        This maintains a complete history even after summarization.

        Args:
            session_id: The ID of the session being summarized
            summary: The generated summary text
        """
        log_filename = os.path.join(
            self.session.memory_dir, f"{session_id}_detailed_log.json"
        )

        # Convert Message objects to dictionaries for JSON serialization
        message_dicts = [asdict(msg) for msg in self.session.messages]

        # Include more metadata to make the logs more useful
        detailed_log = dict(
            session_id=session_id,
            messages=message_dicts,  # All original messages as dictionaries
            summary=summary,
            token_count=self.session.usage.input_tokens
            + self.session.usage.output_tokens,
            timestamp=str(uuid.uuid1().time),  # Using uuid1 time as a timestamp
            context_window_size=get_context_window_size(self.default_model_id),
        )

        # Create parent directory if it doesn't exist
        os.makedirs(self.session.memory_dir, exist_ok=True)

        # Save the detailed log
        with open(log_filename, "w") as f:
            json.dump(detailed_log, f, indent=4)

    def _send(
        self,
        model_id: str,
        on_tool_call_func: Optional[Callable[[str, dict, str], None]],
    ) -> str:
        llm_provider = self.model_provider_map.get(model_id)
        if llm_provider is None:
            raise RuntimeError(f"Unknown model ID: {model_id}")

        try:
            response = llm_provider.send(
                self.session.messages, self.tool_dict, model_id
            )
        except Exception as e:
            raise RuntimeError(f"Error sending message to LLM: {e}")

        if response.tool_calls:
            # Execute tools using the unified method
            updated_tool_calls, tool_messages = self._execute_tools(
                response.tool_calls, on_tool_call_func
            )

            # Create AssistantMessage object and add to session
            assistant_message = AssistantMessage(
                content=response.content,
                tool_calls=updated_tool_calls,
                usage=response.usage,
            )
            self.session.add_message(assistant_message)

            # Add all tool messages to session
            for tool_message in tool_messages:
                self.session.add_message(tool_message)

            # Continue the session with another send
            return self._send(model_id, on_tool_call_func)

        return response.content.strip()

    def run(
        self,
        get_input_func: Callable[[], str],
        on_tool_call_func: Optional[Callable[[str, dict, str], None]],
        on_response_func: Callable[[str], None],
    ) -> None:
        try:
            while user_input := get_input_func():
                message = UserMessage(content=user_input)
                self.session.add_message(message)
                self._checkpoint_if_needed()

                response = self._send(self.default_model_id, on_tool_call_func)
                message = AssistantMessage(content=response)
                self.session.add_message(message)
                self._checkpoint_if_needed()

                on_response_func(response)
        finally:
            # Save the session when we're done
            self.session.save()

    def send_message(
        self,
        message: str,
        model_id: str | None = None,
        on_tool_call_func: Optional[Callable[[str, Dict[str, Any], str], None]] = None,
    ) -> str:
        """Send a single message and get a response."""
        user_message = UserMessage(content=message)
        self.session.add_message(user_message)
        self._checkpoint_if_needed()
        model_id = model_id or self.default_model_id
        response = self._send(model_id, on_tool_call_func)
        assistant_message = AssistantMessage(content=response)
        self.session.add_message(assistant_message)
        self._checkpoint_if_needed()

        return response

    def stream_message(
        self,
        message: str,
        model_id: str,
        on_chunk_func: Callable[[str], None],
        on_tool_call_func: Optional[Callable[[str, Dict[str, Any], str], None]] = None,
        available_tool_ids: Optional[List[str]] = None,
    ) -> str:
        """
        Send a single message and stream the response.

        Args:
            message: The message to send
            model_id: The model ID to use
            on_chunk_func: Callback function that receives each chunk of the response
            on_tool_call_func: Callback function for tool calls

        Returns:
            The complete response
        """
        user_message = UserMessage(content=message)
        self.session.add_message(user_message)
        self._checkpoint_if_needed()

        llm_provider = self.model_provider_map.get(model_id)
        if llm_provider is None:
            raise RuntimeError(f"Unknown model ID: {model_id}")

        final_content = ""
        tool_calls_handled = False

        available_tools = self.tool_dict
        if available_tool_ids is not None:
            available_tools = {
                k: v for k, v in self.tool_dict.items() if k in available_tool_ids
            }
        try:
            for response in llm_provider.stream(
                self.session.messages, available_tools, model_id
            ):
                if response.content != final_content:
                    new_content = response.content[len(final_content) :]
                    final_content = response.content
                    if new_content and on_chunk_func:
                        on_chunk_func(new_content)

                if response.tool_calls and not tool_calls_handled:
                    tool_calls_handled = True

                    # Execute tools using the unified method
                    updated_tool_calls, tool_messages = self._execute_tools(
                        response.tool_calls, on_tool_call_func
                    )

                    # Create and add the assistant message with tool calls
                    tool_calls_message = AssistantMessage(
                        content=final_content, tool_calls=updated_tool_calls
                    )
                    self.session.add_message(tool_calls_message)

                    # Add tool result messages
                    for tool_msg in tool_messages:
                        self.session.add_message(tool_msg)

            if tool_calls_handled and message:
                continuation = self._send(model_id, on_tool_call_func)
                if continuation:
                    if on_chunk_func:
                        on_chunk_func(f"{continuation}")
                    final_content += f"{continuation}"

        except Exception as e:
            raise RuntimeError(f"Error streaming message: {e}")

        if not tool_calls_handled:
            assistant_message = AssistantMessage(content=final_content)
            self.session.add_message(assistant_message)
            self._checkpoint_if_needed()

        return final_content

    def get_session_id(self) -> str:
        """Get the current session ID."""
        return self.session.session_id

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions."""
        return self.session_manager.list_sessions()

    def load_session(self, session_id: str) -> bool:
        """
        Load a specific session.

        Args:
            session_id: ID of the session to load

        Returns:
            True if the session was loaded successfully, False otherwise
        """
        available_sessions = self.session_manager.list_sessions()
        if session_id not in available_sessions:
            return False

        # Load the session
        self.session.load(session_id)

        return True

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a specific session.

        Args:
            session_id: ID of the session to delete

        Returns:
            True if the session was deleted successfully, False otherwise
        """
        # Don't allow deleting the active session
        if session_id == self.session.session_id:
            return False

        try:
            self.session_manager.delete_session(session_id)
            return True
        except Exception as e:
            return False
