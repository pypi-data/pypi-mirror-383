#!/usr/bin/env python3
"""Agent client for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json
import logging
from collections.abc import AsyncGenerator, Mapping
from typing import Any, BinaryIO

import httpx

from glaip_sdk.client._agent_payloads import (
    AgentCreateRequest,
    AgentListParams,
    AgentListResult,
    AgentUpdateRequest,
)
from glaip_sdk.client.base import BaseClient
from glaip_sdk.client.run_rendering import (
    AgentRunRenderingManager,
    compute_timeout_seconds,
)
from glaip_sdk.config.constants import (
    DEFAULT_AGENT_FRAMEWORK,
    DEFAULT_AGENT_RUN_TIMEOUT,
    DEFAULT_AGENT_TYPE,
    DEFAULT_AGENT_VERSION,
    DEFAULT_MODEL,
)
from glaip_sdk.exceptions import NotFoundError
from glaip_sdk.models import Agent
from glaip_sdk.utils.client_utils import (
    aiter_sse_events,
    create_model_instances,
    find_by_name,
    prepare_multipart_data,
)
from glaip_sdk.utils.rendering.renderer import RichStreamRenderer
from glaip_sdk.utils.validation import validate_agent_instruction

# API endpoints
AGENTS_ENDPOINT = "/agents/"

# SSE content type
SSE_CONTENT_TYPE = "text/event-stream"

# Set up module-level logger
logger = logging.getLogger("glaip_sdk.agents")


class AgentClient(BaseClient):
    """Client for agent operations."""

    def __init__(
        self,
        *,
        parent_client: BaseClient | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the agent client.

        Args:
            parent_client: Parent client to adopt session/config from
            **kwargs: Additional arguments for standalone initialization
        """
        super().__init__(parent_client=parent_client, **kwargs)
        self._renderer_manager = AgentRunRenderingManager(logger)

    def list_agents(
        self,
        query: AgentListParams | None = None,
        **kwargs: Any,
    ) -> AgentListResult:
        """List agents with optional filtering and pagination support.

        Args:
            query: Query parameters for filtering agents. If None, uses kwargs to create query.
            **kwargs: Individual filter parameters for backward compatibility.
        """
        if query is not None and kwargs:
            # Both query object and individual parameters provided
            raise ValueError(
                "Provide either `query` or individual filter arguments, not both."
            )

        if query is None:
            # Create query from individual parameters for backward compatibility
            query = AgentListParams(**kwargs)

        params = query.to_query_params()
        envelope = self._request_with_envelope(
            "GET",
            AGENTS_ENDPOINT,
            params=params if params else None,
        )

        if not isinstance(envelope, dict):
            envelope = {"data": envelope}

        data_payload = envelope.get("data") or []
        items = create_model_instances(data_payload, Agent, self)

        return AgentListResult(
            items=items,
            total=envelope.get("total"),
            page=envelope.get("page"),
            limit=envelope.get("limit"),
            has_next=envelope.get("has_next"),
            has_prev=envelope.get("has_prev"),
            message=envelope.get("message"),
        )

    def sync_langflow_agents(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> dict[str, Any]:
        """Sync LangFlow agents by fetching flows from the LangFlow server.

        This method synchronizes agents with LangFlow flows. It fetches all flows
        from the configured LangFlow server and creates/updates corresponding agents.

        Args:
            base_url: Custom LangFlow server base URL. If not provided, uses LANGFLOW_BASE_URL env var.
            api_key: Custom LangFlow API key. If not provided, uses LANGFLOW_API_KEY env var.

        Returns:
            Response containing sync results and statistics

        Raises:
            ValueError: If LangFlow server configuration is missing
        """
        payload = {}
        if base_url is not None:
            payload["base_url"] = base_url
        if api_key is not None:
            payload["api_key"] = api_key

        return self._request("POST", "/agents/langflow/sync", json=payload)

    def get_agent_by_id(self, agent_id: str) -> Agent:
        """Get agent by ID."""
        data = self._request("GET", f"/agents/{agent_id}")

        if isinstance(data, str):
            # Some backends may respond with plain text for missing agents.
            message = data.strip() or f"Agent '{agent_id}' not found"
            raise NotFoundError(message, status_code=404)

        if not isinstance(data, dict):
            raise NotFoundError(
                f"Agent '{agent_id}' not found (unexpected response type)",
                status_code=404,
            )

        return Agent(**data)._set_client(self)

    def find_agents(self, name: str | None = None) -> list[Agent]:
        """Find agents by name."""
        result = self.list_agents(name=name)
        agents = list(result)
        if name is None:
            return agents
        return find_by_name(agents, name, case_sensitive=False)

    # ------------------------------------------------------------------ #
    # Renderer delegation helpers
    # ------------------------------------------------------------------ #
    def _get_renderer_manager(self) -> AgentRunRenderingManager:
        manager = getattr(self, "_renderer_manager", None)
        if manager is None:
            manager = AgentRunRenderingManager(logger)
            self._renderer_manager = manager
        return manager

    def _create_renderer(
        self, renderer: RichStreamRenderer | str | None, **kwargs: Any
    ) -> RichStreamRenderer:
        manager = self._get_renderer_manager()
        verbose = kwargs.get("verbose", False)
        if isinstance(renderer, RichStreamRenderer) or hasattr(renderer, "on_start"):
            return renderer  # type: ignore[return-value]
        return manager.create_renderer(renderer, verbose=verbose)

    def _process_stream_events(
        self,
        stream_response: httpx.Response,
        renderer: RichStreamRenderer,
        timeout_seconds: float,
        agent_name: str | None,
        meta: dict[str, Any],
    ) -> tuple[str, dict[str, Any], float | None, float | None]:
        manager = self._get_renderer_manager()
        return manager.process_stream_events(
            stream_response,
            renderer,
            timeout_seconds,
            agent_name,
            meta,
        )

    def _finalize_renderer(
        self,
        renderer: RichStreamRenderer,
        final_text: str,
        stats_usage: dict[str, Any],
        started_monotonic: float | None,
        finished_monotonic: float | None,
    ) -> str:
        manager = self._get_renderer_manager()
        return manager.finalize_renderer(
            renderer,
            final_text,
            stats_usage,
            started_monotonic,
            finished_monotonic,
        )

    def create_agent(
        self,
        name: str,
        instruction: str,
        model: str = DEFAULT_MODEL,
        tools: list[str | Any] | None = None,
        agents: list[str | Any] | None = None,
        timeout: int = DEFAULT_AGENT_RUN_TIMEOUT,
        *,
        mcps: list[str | Any] | None = None,
        tool_configs: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> "Agent":
        """Create a new agent."""
        if not name or not name.strip():
            raise ValueError("Agent name cannot be empty or whitespace")

        instruction = validate_agent_instruction(instruction)

        agent_type = kwargs.pop("agent_type", kwargs.pop("type", DEFAULT_AGENT_TYPE))
        framework = kwargs.pop("framework", DEFAULT_AGENT_FRAMEWORK)
        version = kwargs.pop("version", DEFAULT_AGENT_VERSION)
        language_model_id = kwargs.pop("language_model_id", None)
        provider_override = kwargs.pop("provider", None)
        model_name_override = kwargs.pop("model_name", None)
        account_id = kwargs.pop("account_id", None)
        description = kwargs.pop("description", None)
        metadata = kwargs.pop("metadata", None)
        agent_config = kwargs.pop("agent_config", None)
        a2a_profile = kwargs.pop("a2a_profile", None)
        mcps = mcps if mcps is not None else kwargs.pop("mcps", None)
        tool_configs = (
            tool_configs
            if tool_configs is not None
            else kwargs.pop("tool_configs", None)
        )

        request = AgentCreateRequest(
            name=name,
            instruction=instruction,
            model=model,
            language_model_id=language_model_id,
            provider=provider_override,
            model_name=model_name_override,
            agent_type=agent_type,
            framework=framework,
            version=version,
            account_id=account_id,
            description=description,
            metadata=metadata,
            tools=tools,
            agents=agents,
            mcps=mcps,
            tool_configs=tool_configs,
            agent_config=agent_config,
            timeout=timeout,
            a2a_profile=a2a_profile,
            extras=kwargs,
        )

        payload = request.to_payload()

        full_agent_data = self._post_then_fetch(
            id_key="id",
            post_endpoint=AGENTS_ENDPOINT,
            get_endpoint_fmt=f"{AGENTS_ENDPOINT}{{id}}",
            json=payload,
        )
        return Agent(**full_agent_data)._set_client(self)

    def update_agent(
        self,
        agent_id: str,
        name: str | None = None,
        instruction: str | None = None,
        model: str | None = None,
        **kwargs: Any,
    ) -> "Agent":
        """Update an existing agent."""
        current_agent = self.get_agent_by_id(agent_id)

        language_model_id = kwargs.pop("language_model_id", None)
        provider_override = kwargs.pop("provider", None)
        model_name_override = kwargs.pop("model_name", None)
        agent_type_override = kwargs.pop("agent_type", kwargs.pop("type", None))
        framework_override = kwargs.pop("framework", None)
        version_override = kwargs.pop("version", None)
        account_id = kwargs.pop("account_id", None)
        description = kwargs.pop("description", None)
        metadata = kwargs.pop("metadata", None)
        tools = kwargs.pop("tools", None)
        tool_configs = kwargs.pop("tool_configs", None)
        agents_value = kwargs.pop("agents", None)
        mcps = kwargs.pop("mcps", None)
        agent_config = kwargs.pop("agent_config", None)
        a2a_profile = kwargs.pop("a2a_profile", None)

        request = AgentUpdateRequest(
            name=name,
            instruction=instruction,
            description=description,
            model=model,
            language_model_id=language_model_id,
            provider=provider_override,
            model_name=model_name_override,
            agent_type=agent_type_override,
            framework=framework_override,
            version=version_override,
            account_id=account_id,
            metadata=metadata,
            tools=tools,
            tool_configs=tool_configs,
            agents=agents_value,
            mcps=mcps,
            agent_config=agent_config,
            a2a_profile=a2a_profile,
            extras=kwargs,
        )

        payload = request.to_payload(current_agent)

        data = self._request("PUT", f"/agents/{agent_id}", json=payload)
        return Agent(**data)._set_client(self)

    def delete_agent(self, agent_id: str) -> None:
        """Delete an agent."""
        self._request("DELETE", f"/agents/{agent_id}")

    def _prepare_sync_request_data(
        self,
        message: str,
        files: list[str | BinaryIO] | None,
        tty: bool,
        **kwargs: Any,
    ) -> tuple[dict | None, dict | None, list | None, dict, Any | None]:
        """Prepare request data for synchronous agent runs with renderer support.

        Args:
            message: Message to send
            files: Optional files to include
            tty: Whether to enable TTY mode
            **kwargs: Additional request parameters

        Returns:
            Tuple of (payload, data_payload, files_payload, headers, multipart_data)
        """
        headers = {"Accept": SSE_CONTENT_TYPE}

        if files:
            # Handle multipart data for file uploads
            multipart_data = prepare_multipart_data(message, files)
            if "chat_history" in kwargs and kwargs["chat_history"] is not None:
                multipart_data.data["chat_history"] = kwargs["chat_history"]
            if "pii_mapping" in kwargs and kwargs["pii_mapping"] is not None:
                multipart_data.data["pii_mapping"] = kwargs["pii_mapping"]

            return (
                None,
                multipart_data.data,
                multipart_data.files,
                headers,
                multipart_data,
            )
        else:
            # Simple JSON payload for text-only requests
            payload = {"input": message, "stream": True, **kwargs}
            if tty:
                payload["tty"] = True
            return payload, None, None, headers, None

    def _get_timeout_values(
        self, timeout: float | None, **kwargs: Any
    ) -> tuple[float, float]:
        """Get request timeout and execution timeout values.

        Args:
            timeout: Request timeout (overrides instance timeout)
            **kwargs: Additional parameters including execution timeout

        Returns:
            Tuple of (request_timeout, execution_timeout)
        """
        request_timeout = timeout or self.timeout
        execution_timeout = kwargs.get("timeout", DEFAULT_AGENT_RUN_TIMEOUT)
        return request_timeout, execution_timeout

    def run_agent(
        self,
        agent_id: str,
        message: str,
        files: list[str | BinaryIO] | None = None,
        tty: bool = False,
        *,
        renderer: RichStreamRenderer | str | None = "auto",
        **kwargs,
    ) -> str:
        """Run an agent with a message, streaming via a renderer."""
        (
            payload,
            data_payload,
            files_payload,
            headers,
            multipart_data,
        ) = self._prepare_sync_request_data(message, files, tty, **kwargs)

        render_manager = self._get_renderer_manager()
        verbose = kwargs.get("verbose", False)
        r = self._create_renderer(renderer, verbose=verbose)
        meta = render_manager.build_initial_metadata(agent_id, message, kwargs)
        render_manager.start_renderer(r, meta)

        final_text = ""
        stats_usage: dict[str, Any] = {}
        started_monotonic: float | None = None
        finished_monotonic: float | None = None

        try:
            response = self.http_client.stream(
                "POST",
                f"/agents/{agent_id}/run",
                json=payload,
                data=data_payload,
                files=files_payload,
                headers=headers,
            )

            with response as stream_response:
                stream_response.raise_for_status()

                timeout_seconds = compute_timeout_seconds(kwargs)
                agent_name = kwargs.get("agent_name")

                (
                    final_text,
                    stats_usage,
                    started_monotonic,
                    finished_monotonic,
                ) = self._process_stream_events(
                    stream_response,
                    r,
                    timeout_seconds,
                    agent_name,
                    meta,
                )

        except KeyboardInterrupt:
            try:
                r.close()
            finally:
                raise
        except Exception:
            try:
                r.close()
            finally:
                raise
        finally:
            if multipart_data:
                multipart_data.close()

        return self._finalize_renderer(
            r,
            final_text,
            stats_usage,
            started_monotonic,
            finished_monotonic,
        )

    def _prepare_request_data(
        self,
        message: str,
        files: list[str | BinaryIO] | None,
        **kwargs,
    ) -> tuple[dict | None, dict | None, dict | None, dict | None]:
        """Prepare request data for async agent runs.

        Returns:
            Tuple of (payload, data_payload, files_payload, headers)
        """
        if files:
            # Handle multipart data for file uploads
            multipart_data = prepare_multipart_data(message, files)
            # Inject optional multipart extras expected by backend
            if "chat_history" in kwargs and kwargs["chat_history"] is not None:
                multipart_data.data["chat_history"] = kwargs["chat_history"]
            if "pii_mapping" in kwargs and kwargs["pii_mapping"] is not None:
                multipart_data.data["pii_mapping"] = kwargs["pii_mapping"]

            headers = {"Accept": SSE_CONTENT_TYPE}
            return None, multipart_data.data, multipart_data.files, headers
        else:
            # Simple JSON payload for text-only requests
            payload = {"input": message, "stream": True, **kwargs}
            headers = {"Accept": SSE_CONTENT_TYPE}
            return payload, None, None, headers

    def _create_async_client_config(
        self, timeout: float | None, headers: dict | None
    ) -> dict:
        """Create async client configuration with proper headers and timeout."""
        config = self._build_async_client(timeout or self.timeout)
        if headers:
            config["headers"] = {**config["headers"], **headers}
        return config

    async def _stream_agent_response(
        self,
        async_client: httpx.AsyncClient,
        agent_id: str,
        payload: dict | None,
        data_payload: dict | None,
        files_payload: dict | None,
        headers: dict | None,
        timeout_seconds: float,
        agent_name: str | None,
    ) -> AsyncGenerator[dict, None]:
        """Stream the agent response and yield parsed JSON chunks."""
        async with async_client.stream(
            "POST",
            f"/agents/{agent_id}/run",
            json=payload,
            data=data_payload,
            files=files_payload,
            headers=headers,
        ) as stream_response:
            stream_response.raise_for_status()

            async for event in aiter_sse_events(
                stream_response, timeout_seconds, agent_name
            ):
                try:
                    chunk = json.loads(event["data"])
                    yield chunk
                except json.JSONDecodeError:
                    logger.debug("Non-JSON SSE fragment skipped")
                    continue

    async def arun_agent(
        self,
        agent_id: str,
        message: str,
        files: list[str | BinaryIO] | None = None,
        *,
        timeout: float | None = None,
        **kwargs,
    ) -> AsyncGenerator[dict, None]:
        """Async run an agent with a message, yielding streaming JSON chunks.

        Args:
            agent_id: ID of the agent to run
            message: Message to send to the agent
            files: Optional list of files to include
            timeout: Request timeout in seconds
            **kwargs: Additional arguments (chat_history, pii_mapping, etc.)

        Yields:
            Dictionary containing parsed JSON chunks from the streaming response

        Raises:
            AgentTimeoutError: When agent execution times out
            httpx.TimeoutException: When general timeout occurs
            Exception: For other unexpected errors
        """
        # Prepare request data
        payload, data_payload, files_payload, headers = self._prepare_request_data(
            message, files, **kwargs
        )

        # Create async client configuration
        async_client_config = self._create_async_client_config(timeout, headers)

        # Get execution timeout for streaming control
        timeout_seconds = kwargs.get("timeout", DEFAULT_AGENT_RUN_TIMEOUT)
        agent_name = kwargs.get("agent_name")

        try:
            # Create async client and stream response
            async with httpx.AsyncClient(**async_client_config) as async_client:
                async for chunk in self._stream_agent_response(
                    async_client,
                    agent_id,
                    payload,
                    data_payload,
                    files_payload,
                    headers,
                    timeout_seconds,
                    agent_name,
                ):
                    yield chunk

        finally:
            # Ensure cleanup - this is handled by the calling context
            # but we keep this for safety in case of future changes
            pass
