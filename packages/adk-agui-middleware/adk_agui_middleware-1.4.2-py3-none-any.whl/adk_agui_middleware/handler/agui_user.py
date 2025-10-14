# Copyright (C) 2025 Trend Micro Inc. All rights reserved.
"""Handler for managing AGUI user interactions and agent execution workflow."""

import asyncio
from collections.abc import AsyncGenerator

from ag_ui.core import (
    BaseEvent,
    EventType,
    RunErrorEvent,
    RunFinishedEvent,
    RunStartedEvent,
)
from google.adk.events import Event
from google.genai import types

from ..event.error_event import AGUIErrorEvent
from ..loggers.exception import (
    adk_event_exception_handler,
    agui_event_exception_handler,
)
from ..utils.convert.agui_tool_message_to_adk_function_response import (
    convert_agui_tool_message_to_adk_function_response,
)
from .queue import QueueHandler
from .running import RunningHandler
from .session import SessionHandler
from .user_message import UserMessageHandler


class AGUIUserHandler:
    """Orchestrates user interactions with the agent through the AGUI interface.

    Manages the complete workflow of agent execution including session management,
    event translation, tool call tracking, and error handling. This handler is
    the primary coordinator for HITL (Human-in-the-Loop) workflows, managing
    the transition between agent execution and human intervention states.

    Key Responsibilities:
    - Orchestrates agent execution through the running handler
    - Manages session state and HITL workflow transitions
    - Tracks tool calls and manages pending tool call states
    - Coordinates between user messages, agent responses, and tool results
    """

    def __init__(
        self,
        running_handler: RunningHandler,
        user_message_handler: UserMessageHandler,
        session_handler: SessionHandler,
        queue_handler: QueueHandler,
    ):
        """Initialize the AGUI user handler.

        Sets up the handler with its dependent components for managing the complete
        agent interaction workflow including execution, message processing, and
        session state management.

        Args:
            :param running_handler: Handler for executing agent runs and event translation
            :param user_message_handler: Handler for processing user messages and tool results
            :param session_handler: Handler for session state management and HITL workflows
        """
        self.input_message: types.Content | None = None
        self.running_handler = running_handler
        self.user_message_handler = user_message_handler
        self.session_handler = session_handler
        self.queue_handler = queue_handler
        self.adk_queue = queue_handler.get_adk_queue()
        self.agui_queue = queue_handler.get_agui_queue()

        self.tool_call_info: dict[str, str] = {}

    async def _async_init(self) -> None:
        """Initialize asynchronous components of the handler.

        Performs async initialization that cannot be done in __init__, specifically
        setting up long-running tool IDs from pending tool calls in session state.
        This is crucial for resuming HITL workflows correctly.
        """
        self.tool_call_info = await self.session_handler.get_pending_tool_calls()
        self.running_handler.set_long_running_tool_ids(self.tool_call_info)
        await self.user_message_handler.init(self.tool_call_info)
        self.running_handler.update_agent_tools(
            self.agui_queue, self.user_message_handler.frontend_tools
        )

    async def _async_close(self) -> None:
        """Close internal async resources created during the run.

        Ensures the underlying runner and any associated resources are
        gracefully closed after a workflow completes or aborts.

        Raises:
            Exception: Propagates exceptions from the underlying runner close
        """
        await self.running_handler.close()

    @property
    def app_name(self) -> str:
        """Get the application name from the session handler.

        Returns:
            Application name string
        """
        return self.session_handler.app_name

    @property
    def user_id(self) -> str:
        """Get the user ID from the session handler.

        Returns:
            User identifier string
        """
        return self.session_handler.user_id

    @property
    def session_id(self) -> str:
        """Get the session ID from the session handler.

        Returns:
            Session identifier string
        """
        return self.session_handler.session_id

    @property
    def run_id(self) -> str:
        """Get the run ID from the user message content.

        Returns:
            Run identifier string
        """
        return self.user_message_handler.agui_content.run_id

    def call_start(self) -> RunStartedEvent:
        """Create a run started event.

        Creates a standardized run started event with the current session context.
        This event is sent to clients to indicate the beginning of agent processing.

        Returns:
            RunStartedEvent indicating the beginning of agent execution
        """
        return RunStartedEvent(
            type=EventType.RUN_STARTED, thread_id=self.session_id, run_id=self.run_id
        )

    def call_finished(self) -> RunFinishedEvent:
        """Create a run finished event.

        Creates a standardized run finished event with the current session context.
        This event is sent to clients to indicate the completion of agent processing.

        Returns:
            RunFinishedEvent indicating the completion of agent execution
        """
        return RunFinishedEvent(
            type=EventType.RUN_FINISHED, thread_id=self.session_id, run_id=self.run_id
        )

    def check_is_long_running_tool(self, adk_event: Event) -> bool:
        """Check if the ADK event contains long-running tool calls.

        Examines the event for function calls that are marked as long-running operations
        and updates the internal tool call tracking. This is critical for HITL workflow
        management as it determines when to pause agent execution and wait for human input.

        Args:
            :param adk_event: ADK event to examine for long-running tool calls

        Returns:
            True if the event contains long-running tool calls that should pause execution
        """
        if not adk_event.long_running_tool_ids:
            return False
        for func_call in adk_event.get_function_calls():
            if (
                func_call.id in adk_event.long_running_tool_ids
                and func_call.id
                and func_call.name
            ):
                self.tool_call_info[func_call.id] = func_call.name
                return True
        return False

    async def process_tool_result(self) -> RunErrorEvent | types.Content:
        """Process tool result submission or extract user message for agent processing.

        Determines whether the incoming message is a tool result completion (HITL) or
        a regular user message, then processes accordingly. For tool results, validates
        the tool call ID and converts the result to ADK format. For user messages,
        extracts the latest user input for agent processing.

        Returns:
            Either a RunErrorEvent if validation fails, or Content object for agent processing

        Raises:
            Exception: Handled internally and converted to error event
        """
        try:
            tool_message = self.user_message_handler.is_tool_result_submission
            if not tool_message:
                user_message = self.user_message_handler.get_latest_message()
                return (
                    user_message
                    if user_message
                    else AGUIErrorEvent.create_no_input_message_error(self.session_id)
                )
            tool_call_name = self.tool_call_info.pop(tool_message.tool_call_id, None)
            if not tool_call_name:
                return AGUIErrorEvent.create_no_tool_results_error(self.session_id)
            await self.session_handler.overwrite_pending_tool_calls(self.tool_call_info)
            return types.Content(
                parts=[
                    convert_agui_tool_message_to_adk_function_response(
                        tool_message, tool_call_name
                    )
                ],
                role="user",
            )
        except Exception as e:
            return AGUIErrorEvent.create_tool_processing_error_event(e)

    async def set_user_input(self) -> RunErrorEvent | None:
        """Set the user input message for agent processing.

        Processes the incoming message to determine user input and sets it for
        agent execution. Returns error if message processing fails, otherwise
        stores the processed input internally for use by the agent.

        Returns:
            RunErrorEvent if message processing fails, None if successful
        """
        result = await self.process_tool_result()
        if isinstance(result, RunErrorEvent):
            return result
        self.input_message = result
        return None

    async def _run_async_with_adk(self) -> None:
        """Run the ADK pipeline and push events onto the ADK queue.

        Executes the agent via the running handler and forwards produced
        ADK events to the ADK queue, guaranteeing a termination sentinel
        is sent even if an exception occurs.
        """
        async with adk_event_exception_handler(self.adk_queue):
            async for adk_event in self.running_handler.run_async_with_adk(
                user_id=self.user_id,
                session_id=self.session_id,
                new_message=self.input_message,
            ):
                await self.adk_queue.put(adk_event)

    async def _run_async_with_agui(self) -> None:
        """Translate ADK events to AGUI events and push onto the AGUI queue.

        Consumes ADK events from the ADK queue, translates them to AGUI
        events via the running handler, and forwards them to the AGUI queue.
        Guarantees a termination sentinel is sent even on exceptions.
        """
        async with agui_event_exception_handler(self.agui_queue):
            async for adk_event in self.adk_queue.get_iterator():
                async for agui_event in self.running_handler.run_async_with_agui(
                    adk_event
                ):
                    await self.agui_queue.put(agui_event)
                if self.check_is_long_running_tool(adk_event):
                    return
            async for (
                ag_ui_event
            ) in self.running_handler.force_close_streaming_message():
                await self.agui_queue.put(ag_ui_event)
            if (
                event_final_state
                := await self.running_handler.create_state_snapshot_event(
                    await self.session_handler.get_session_state()
                )
            ) is not None:
                await self.agui_queue.put(event_final_state)

    async def _run_workflow(self) -> AsyncGenerator[BaseEvent]:
        """Execute the complete agent workflow with session management.

        Manages the entire workflow including session creation, state updates,
        agent execution, pending tool call management, and run completion.
        This orchestrates the full lifecycle of an agent execution request.

        Yields:
            AGUI BaseEvent objects for the complete workflow
        """
        yield self.call_start()
        await self.session_handler.check_and_create_session(
            self.user_message_handler.initial_state
        )
        await self.session_handler.update_session_state(
            self.user_message_handler.initial_state
        )
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self._run_async_with_adk())
                tg.create_task(self._run_async_with_agui())
                async for agui_event in self.agui_queue.get_iterator():
                    yield agui_event
        except* Exception as eg:
            for exc in eg.exceptions:
                yield AGUIErrorEvent.create_execution_error_event(exc)
        await self.session_handler.overwrite_pending_tool_calls(self.tool_call_info)
        yield self.call_finished()

    async def run(self) -> AsyncGenerator[BaseEvent]:
        """Execute the complete AGUI user interaction workflow.

        Main entry point for processing user requests through the middleware.
        Handles initialization, input processing, workflow execution, and error handling.
        This method orchestrates the entire agent execution lifecycle from request
        processing to response generation.

        Yields:
            BaseEvent objects representing the complete agent interaction workflow

        Raises:
            Exception: All exceptions are caught and converted to error events
        """
        await self._async_init()
        if error := await self.set_user_input():
            yield error
            return
        try:
            async for event in self._run_workflow():
                yield event
        except Exception as e:
            yield AGUIErrorEvent.create_execution_error_event(e)
        finally:
            await self._async_close()
