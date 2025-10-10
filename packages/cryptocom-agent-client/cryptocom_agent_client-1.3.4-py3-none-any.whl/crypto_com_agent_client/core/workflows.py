"""
Graph Workflow Module.

This module defines the `GraphWorkflow` class, which encapsulates the logic for
setting up and managing a LangGraph-based workflow. It integrates language models,
tools, and optional LangFuse handlers to process state transitions and execute tools.
"""

# Standard library imports
from typing import Annotated, Any, Literal, Optional, Self, TypedDict

# Third-party imports
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import (
    AnyMessage,
    BaseMessage,
    SystemMessage,
    trim_messages,
)
from langchain_core.runnables import Runnable
from langfuse.callback.langchain import LangchainCallbackHandler
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

# Internal application imports
from crypto_com_agent_client.lib.enums.node_enum import Node
from crypto_com_agent_client.lib.enums.role_enum import Role
from crypto_com_agent_client.lib.enums.workflow_enum import Workflow
from crypto_com_agent_client.lib.utils.token_usage import print_model_debug_info


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    chain_id: str
    private_key: str
    sso_wallet_url: str
    vectordb_context: Optional[str]
    vectordb_query: Optional[str]


class GraphWorkflow:
    """
    The `GraphWorkflow` class defines and manages a LangGraph workflow for processing
    state transitions and tool interactions.

    Responsibilities:
        - Integrate a language model, tools, and optional LangFuse callbacks.
        - Define and compile a state graph with nodes and conditional logic.
        - Manage the workflow's lifecycle, including setup and compilation.

    Attributes:
        model (Runnable[LanguageModelInput, BaseMessage]): The language model for message processing.
        instructions (str): System instructions to guide the workflow.
        langfuse (LangchainCallbackHandler): The handler for LangFuse callbacks.
        tool_node (ToolNode): Node for handling tool interactions.
        workflow (StateGraph): The state graph defining the workflow structure.

    Example:
        >>> from langgraph.prebuilt import ToolNode
        >>> from langfuse.callback.langchain import LangchainCallbackHandler
        >>> from core.model import Model
        >>> from core.workflows import GraphWorkflow
        >>>
        >>> # Initialize model and tools
        >>> model = Model(provider="OpenAI", api_key="your-api-key", model_name="gpt-4")
        >>> tool_node = ToolNode([some_tool_function])
        >>>
        >>> # Optional LangFuse handler
        >>> langfuse = LangchainCallbackHandler(
        ...     public_key="your-public-key",
        ...     secret_key="your-secret-key",
        ...     host="https://your-langfuse-instance.com"
        ... )
        >>>
        >>> # Initialize workflow
        >>> workflow = GraphWorkflow(
        ...     model=model,
        ...     langfuse=langfuse,
        ...     tool_node=tool_node,
        ...     instructions="Provide concise and accurate answers."
        ... )
        >>> compiled_workflow = workflow.compile(checkpointer=some_checkpointer)
    """

    def __init__(
        self: Self,
        model: Runnable[LanguageModelInput, BaseMessage],
        instructions: str,
        langfuse: LangchainCallbackHandler,
        tool_node: ToolNode,
        debug_logging: bool = False,
        model_handler: Any = None,
    ) -> None:
        """
        Initialize the workflow with the required components.

        Args:
            model (Runnable[LanguageModelInput, BaseMessage]): The language model for processing messages.
            instructions (str): System instructions to guide the workflow.
            langfuse (LangchainCallbackHandler): An optional LangFuse handler for callback integration.
            tool_node (ToolNode): A node representing tool execution within the workflow.
            debug_logging (bool): Enable/disable debug logging for model interactions.
            model_handler (Any): The Model handler instance for accessing knowledge base features.

        Attributes:
            model (Runnable[LanguageModelInput, BaseMessage]): The language model for message processing.
            instructions (str): Instructions for guiding the workflow.
            langfuse (LangchainCallbackHandler): The handler for LangFuse callbacks.
            tool_node (ToolNode): Node for handling tool interactions.
            workflow (StateGraph): The state graph defining the workflow structure.
            debug_logging (bool): Flag to control debug logging output.
            model_handler (Any): Model handler for knowledge base access.


        Example:
            >>> model = Model(provider="OpenAI", api_key="your-api-key", model_name="gpt-4")
            >>> tool_node = ToolNode([some_tool_function])
            >>> workflow = GraphWorkflow(
            ...     model=model,
            ...     instructions="Provide concise responses.",
            ...     langfuse=None,
            ...     tool_node=tool_node
            ... )
        """
        self.model: Runnable[LanguageModelInput, BaseMessage] = model
        self.instructions: str = instructions
        self.langfuse: LangchainCallbackHandler = langfuse
        self.tool_node: ToolNode = tool_node
        self.workflow: StateGraph = StateGraph(AgentState)
        self.debug_logging: bool = debug_logging
        self.model_handler: Any = model_handler

        # Configure the workflow graph
        self._setup_workflow()

    def _should_continue(self: Self, state: AgentState) -> Literal[Node.Tools, END]:
        """
        Decision logic for whether to continue to tools or end the workflow.

        Args:
            state (MessagesState): The current state of messages.

        Returns:
            Literal[Node.Tools, END]: Returns Node.Tools if a tool call is required, otherwise END.

        Example:
            >>> state = {Workflow.Messages: [{"content": "Some input", "tool_calls": ["tool1"]}]}
            >>> result = workflow._should_continue(state)
            >>> print(result)
            tools
        """
        messages: list[Any] = state[Workflow.Messages]
        last_message: Any = messages[-1]

        # Check if a tool call was made
        if last_message.tool_calls:
            return Node.Tools
        return END

    def _query_vector_db(self: Self, state: AgentState) -> dict[str, Any]:
        """
        Query vector database (Bedrock Knowledge Base) for relevant context.

        Args:
            state: The current agent state.

        Returns:
            Updated state with vector database results.
        """
        if self.debug_logging:
            print("\n🔍 VectorDB Step: Checking for knowledge base query need...")

        # Check if we have a Bedrock model with knowledge base configured
        if not self.model_handler:
            if self.debug_logging:
                print("📭 No model handler - skipping VectorDB")
            return {"vectordb_context": None}

        # Check if this is a Bedrock provider with knowledge base
        from crypto_com_agent_client.lib.enums.provider_enum import Provider

        if (
            not hasattr(self.model_handler, "provider")
            or self.model_handler.provider != Provider.Bedrock
        ):
            if self.debug_logging:
                print("📭 Not Bedrock provider - skipping VectorDB")
            return {"vectordb_context": None}

        if not hasattr(self.model_handler, "query_knowledge_base"):
            if self.debug_logging:
                print("📭 No knowledge base configured - skipping VectorDB")
            return {"vectordb_context": None}

        # Find the last human message to use as the query
        messages = state.get("messages", [])
        human_query = None
        for msg in reversed(messages):
            if hasattr(msg, "type") and msg.type == "human":
                human_query = msg.content
                break

        if not human_query:
            if self.debug_logging:
                print("📭 No human query found - skipping VectorDB")
            return {"vectordb_context": None}

        # Query the vector database (knowledge base)
        try:
            if self.debug_logging:
                print(f"🔍 Querying VectorDB for: {human_query[:50]}...")

            kb_results = self.model_handler.query_knowledge_base(
                human_query, max_results=3
            )

            if self.debug_logging:
                print(
                    f"📋 VectorDB response: {kb_results[:200] if kb_results else 'None'}..."
                )

            # Check if we have valid results
            if (
                kb_results
                and not kb_results.startswith("No")
                and not kb_results.startswith("Knowledge base query failed")
                and not kb_results.startswith("Knowledge base query error")
            ):

                if self.debug_logging:
                    print(f"✅ VectorDB context found - {len(kb_results)} chars")

                return {"vectordb_context": kb_results, "vectordb_query": human_query}
            else:
                if self.debug_logging:
                    print("📭 No relevant VectorDB results found")
                return {"vectordb_context": None}

        except Exception as e:
            if self.debug_logging:
                print(f"⚠️ VectorDB query failed: {str(e)}")
            return {"vectordb_context": None}

    def _call_model(self: Self, state: AgentState) -> dict[str, list[BaseMessage]]:
        """
        Call the model to process the current state with vector database context.

        This method trims message history, uses vector database context if available,
        invokes the language model, and returns the response.

        Args:
            state (AgentState): The current state including messages and vectordb context.

        Returns:
            dict[str, list[BaseMessage]]: The updated state with the model's response.
        """

        messages: list[Any] = state[Workflow.Messages]

        # Trim messages before sending to LLM (keep last 10 messages)
        selected_messages = trim_messages(
            messages,
            token_counter=len,  # Simple message count instead of token counting
            max_tokens=10,  # Keep the last 10 messages for better memory retention
            strategy="last",  # Keep the most recent messages
            start_on="human",  # Ensure the first message is a HumanMessage
            include_system=True,  # Retain SystemMessage (important for instructions)
            allow_partial=False,  # Do not allow partial messages
        )

        # Add system instructions as the first message
        system_message = SystemMessage(content=self.instructions)
        selected_messages.insert(0, system_message)

        # Use vector database context if available
        vectordb_context = state.get("vectordb_context")
        vectordb_query = state.get("vectordb_query")
        if self.debug_logging:
            print(f"vectordb_context: {vectordb_context}")
            print(f"vectordb_query: {vectordb_query}")

        if vectordb_context and vectordb_query:
            if self.debug_logging:
                print(f"\n📚 Using VectorDB context for model call")

            # Find and enhance the human message with vector database context
            enhanced_messages = []
            for msg in selected_messages:
                if (
                    hasattr(msg, "type")
                    and msg.type == "human"
                    and msg.content == vectordb_query
                ):
                    # Replace with enhanced version
                    from langchain_core.messages import HumanMessage

                    enhanced_input = f"""Based on the following information from the knowledge base:

{vectordb_context}

Please answer this question: {vectordb_query}

Use the knowledge base information above to provide an accurate and informed response. You can also use available tools/functions if needed to provide additional information or perform actions."""
                    enhanced_msg = HumanMessage(content=enhanced_input)
                    enhanced_messages.append(enhanced_msg)
                else:
                    enhanced_messages.append(msg)

            selected_messages = enhanced_messages

        # Invoke the model with or without LangFuse handler
        if self.langfuse:
            response: BaseMessage = self.model.invoke(
                selected_messages,
                config={Workflow.Callbacks: [self.langfuse]},
            )
        else:
            response: BaseMessage = self.model.invoke(selected_messages)

        # Debug logging for model input and response
        if self.debug_logging:
            print_model_debug_info(selected_messages, response, self.debug_logging)

        return {Workflow.Messages: [response]}

    def _setup_workflow(self: Self) -> None:
        """
        Setup the workflow graph with nodes, edges, and conditional logic.

        This method defines the workflow with:
            - VectorDB node for knowledge base queries
            - Agent node for language model processing
            - Tools node for tool execution
            - Proper routing between nodes

        Workflow: START -> [VectorDB?] -> Agent -> [Tools?] -> Agent -> END
        """
        # Vector database query node
        self.workflow.add_node(Node.VectorDB, self._query_vector_db)

        # Agent/LLM node
        self.workflow.add_node(Node.Agent, self._call_model)

        # Tool execution node
        self.workflow.add_node(Node.Tools, self.tool_node)

        # Start with VectorDB node (checks internally if KB is available)
        self.workflow.add_edge(START, Node.VectorDB)

        # VectorDB always goes to Agent
        self.workflow.add_edge(Node.VectorDB, Node.Agent)

        # Agent decides: Tools or END
        self.workflow.add_conditional_edges(Node.Agent, self._should_continue)

        # Tools always return to Agent
        self.workflow.add_edge(Node.Tools, Node.Agent)

    def compile(self: Self, checkpointer: Any) -> CompiledStateGraph:
        """
        Compile the workflow with the specified checkpointer.

        Args:
            checkpointer (Any): A checkpointer instance to manage workflow state.

        Returns:
            CompiledStateGraph: The compiled workflow graph ready for execution.

        Example:
            >>> compiled_workflow = workflow.compile(checkpointer=some_checkpointer)
            >>> print(compiled_workflow)
            <CompiledStateGraph object>
        """
        return self.workflow.compile(checkpointer=checkpointer)
