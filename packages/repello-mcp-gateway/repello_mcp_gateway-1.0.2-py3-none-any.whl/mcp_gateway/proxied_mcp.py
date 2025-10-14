import asyncio
import logging
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional, Tuple

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.server.fastmcp import Context
from repello_argus_client import ArgusClient, Verdict

from mcp_gateway.exceptions import AnalysisError

logger = logging.getLogger(__name__)


class ProxiedMCP:
    """Manages the connection and interaction with a single downstream MCP server."""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self._session: Optional[ClientSession] = None
        self._client_cm: Optional[Any] = None
        self._server_info: Optional[types.InitializeResult] = None
        self._exit_stack = AsyncExitStack()
        self._tools: List[types.Tool] = []
        self._resources: List[types.Resource] = []
        self._prompts: List[types.Prompt] = []
        self._transport_type = "http" if "url" in config else "stdio"
        logger.info(
            f"Initialized Proxied Server: {self.name} (transport: {self._transport_type})"
        )

    def _create_argus_client(self, mcp_context: Context) -> ArgusClient:
        return ArgusClient.create(
            api_key=mcp_context.request_context.lifespan_context.api_key,
            asset_id=mcp_context.request_context.lifespan_context.tracking_id,
            session_id=mcp_context.request_context.lifespan_context.session_id,
            save=True,
        )

    async def start(self) -> None:
        if self._session is not None:
            logger.warning(f"Server '{self.name}' already started.")
            return

        logger.info(f"Starting proxied server: {self.name}...")

        try:
            if self._transport_type == "http":
                url = self.config.get("url", "")
                headers = self.config.get("headers", {})
                logger.info(f"Connecting to HTTP MCP server at: {url}")
                self._client_cm = sse_client(url=url, headers=headers)
                read, write = await self._exit_stack.enter_async_context(self._client_cm)
            else:
                server_params = StdioServerParameters(
                    command=self.config.get("command", ""),
                    args=self.config.get("args", []),
                    env=self.config.get("env", None),
                )
                self._client_cm = stdio_client(server_params)
                read, write = await self._exit_stack.enter_async_context(self._client_cm)

            session_cm = ClientSession(read, write)
            self._session = await self._exit_stack.enter_async_context(session_cm)

            self._server_info = await self._session.initialize()
            logger.info(
                f"Proxied server '{self.name}' started and initialized successfully."
            )

            await self._fetch_initial_capabilities()
        except Exception:
            self._server_info = None
            await self.stop()
            raise

    async def _fetch_initial_capabilities(self):
        if not self.session:
            logger.warning(
                f"Cannot fetch capabilities for {self.name}, session inactive."
            )
            return

        try:
            tools_res, resources_res, prompts_res = await asyncio.gather(
                self.session.list_tools(),
                self.session.list_resources(),
                self.session.list_prompts(),
                return_exceptions=True,
            )

            if isinstance(tools_res, Exception):
                logger.debug(f"Failed to list tools for {self.name}: {tools_res}")
                self._tools = []
            else:
                self._tools = self._extract_list(tools_res, "tools", types.Tool)

            if isinstance(resources_res, Exception):
                logger.debug(
                    f"Failed to list resources for {self.name}: {resources_res}"
                )
                self._resources = []
            else:
                self._resources = self._extract_list(
                    resources_res, "resources", types.Resource
                )

            if isinstance(prompts_res, Exception):
                logger.debug(f"Failed to list prompts for {self.name}: {prompts_res}")
                self._prompts = []
            else:
                self._prompts = self._extract_list(prompts_res, "prompts", types.Prompt)

            logger.info(
                f"Fetched initial capabilities for {self.name}: "
                f"{len(self._tools)} tools, "
                f"{len(self._resources)} resources, "
                f"{len(self._prompts)} prompts."
            )
        except Exception:
            self._tools, self._resources, self._prompts = [], [], []
            raise

    def _extract_list(
        self, result: Any, attribute_name: str, expected_type: type
    ) -> List[Any]:
        if hasattr(result, attribute_name):
            items = getattr(result, attribute_name)
        elif isinstance(result, list):
            items = result
        else:
            return []

        if isinstance(items, list):
            return [item for item in items if isinstance(item, expected_type)]
        return []

    async def stop(self) -> None:
        logger.info(f"Stopping proxied MCP: {self.name}...")
        await self._exit_stack.aclose()
        self._session = None
        self._client_cm = None
        self._server_info = None
        self._tools, self._resources, self._prompts = [], [], []
        logger.info(f"Proxied MCP '{self.name}' stopped.")

    @property
    def session(self) -> ClientSession:
        if self._session is None:
            raise RuntimeError(f"Server '{self.name}' session not started.")
        return self._session

    async def list_prompts(self) -> List[types.Prompt]:
        return self._prompts

    async def get_prompt(
        self,
        name: str,
        arguments: Optional[Dict[str, str]] = None,
        mcp_context: Optional[Context] = None,
    ) -> types.GetPromptResult:
        client = self._create_argus_client(mcp_context)
        result = await self.session.get_prompt(name, arguments=arguments)
        sanitized_result = client.check_content(content=str(result))
        if sanitized_result["verdict"] == Verdict.BLOCKED:
            raise AnalysisError(
                f"Prompt blocked by gateway policy for '{self.name}/{name}'."
            )
        return result

    async def list_resources(self) -> List[types.Resource]:
        return self._resources

    async def read_resource(
        self,
        uri: str,
        mcp_context: Optional[Context] = None,
    ) -> Tuple[bytes, Optional[str]]:
        content, mime_type = await self.session.read_resource(uri)
        if not mime_type or not (
            mime_type.startswith("text/") or mime_type in ("application/json",)
        ):
            return content, mime_type
        client = self._create_argus_client(mcp_context)
        sanitized_content = client.check_content(content=str(content))
        if sanitized_content["verdict"] == Verdict.BLOCKED:
            raise AnalysisError(
                f"Resource access blocked by gateway policy for '{self.name}/{uri}'."
            )
        return content, mime_type

    async def list_tools(self) -> List[types.Tool]:
        return self._tools

    def _wrap_tool_arguments(
        self, tool_name: str, tool_args: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        if tool_args is None:
            return None
        try:
            tool_obj = next((t for t in self._tools if t.name == tool_name), None)
            if tool_obj and hasattr(tool_obj, "inputSchema") and tool_obj.inputSchema:
                properties = tool_obj.inputSchema.get("properties", {}) or {}
                required = tool_obj.inputSchema.get("required", []) or []
                expects_params = ("params" in properties) or ("params" in required)
                only_params = (
                    list(properties.keys()) == ["params"]
                    if isinstance(properties, dict)
                    else False
                )
                if (expects_params or only_params) and "params" not in tool_args:
                    return {"params": tool_args}
        except Exception:
            pass
        return tool_args

    async def _call_tool_with_retry(
        self, name: str, arguments: Optional[Dict[str, Any]]
    ) -> types.CallToolResult:
        try:
            return await self.session.call_tool(name, arguments=arguments)
        except Exception as e:
            msg = str(e)
            if ("Missing required parameter" in msg and "params" in msg) or (
                "required property" in msg and "params" in msg
            ):
                wrapped_args = (
                    {"params": arguments or {}}
                    if not (arguments and "params" in arguments)
                    else arguments
                )
                return await self.session.call_tool(name, arguments=wrapped_args)
            raise

    async def call_tool(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
        mcp_context: Optional[Context] = None,
    ) -> types.CallToolResult:
        client = self._create_argus_client(mcp_context)
        sanitized_args = client.check_content(
            content=f"Tool call {self.name}/{name} with arguments {str(arguments)}"
        )
        if sanitized_args["verdict"] == Verdict.BLOCKED:
            raise AnalysisError(
                f"Tool call blocked by gateway policy for '{self.name}/{name}'."
            )
        final_arguments = self._wrap_tool_arguments(name, arguments or {})
        result = await self._call_tool_with_retry(name, final_arguments)
        sanitized_result = client.check_content(
            content=f"Tool call {self.name}/{name} result {str(result)}"
        )
        if sanitized_result["verdict"] == Verdict.BLOCKED:
            raise AnalysisError(
                f"Tool result blocked by gateway policy for '{self.name}/{name}'."
            )
        return result

    async def get_capabilities(self) -> Optional[types.ServerCapabilities]:
        if self._server_info is None:
            return None
        if self._server_info.capabilities is None:
            return None
        return self._server_info.capabilities
