# server.py
import argparse
import asyncio
import inspect
import logging
import os
import sys
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Tuple

from mcp import types
from mcp.server.fastmcp import Context, FastMCP
from repello_argus_client import ArgusClient, Verdict

from mcp_gateway.config import load_config
from mcp_gateway.exceptions import AnalysisError
from mcp_gateway.proxied_mcp import ProxiedMCP
from mcp_gateway import __version__


class GatewayContext:
    """Context holding the managed proxied servers and API configuration."""

    def __init__(self, tracking_id: str = "", api_key: str = "", session_id: str = ""):
        self.proxied_servers: Dict[str, ProxiedMCP] = {}
        self.tracking_id = tracking_id
        self.api_key = api_key
        self.session_id = session_id

# Global Config for Args
cli_args = None
log_level = os.environ.get("LOGLEVEL", "INFO").upper()

# Configure logging
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _get_param_signatures_from_schema(
    schema: Optional[Dict[str, Any]], is_prompt: bool = False
) -> List[Tuple[str, type]]:
    """Extract parameter signatures from JSON schema or prompt arguments."""
    param_signatures = []
    if is_prompt and hasattr(schema, "arguments"):
        for arg in schema.arguments:
            param_signatures.append((arg.name, str))
    elif schema and isinstance(schema, dict):
        properties = schema.get("properties", {})
        for param_name, param_schema in properties.items():
            param_type = Any
            json_type = param_schema.get("type")
            if json_type:
                type_mapping = {
                    "string": str,
                    "integer": int,
                    "boolean": bool,
                    "number": float,
                    "object": Dict[str, Any],
                    "array": List[Any],
                }
                param_type = type_mapping.get(json_type, Any)
            param_signatures.append((param_name, param_type))
    return param_signatures


def _create_dynamic_handler(
    param_signatures: List[Tuple[str, type]],
    return_type: type,
    handler_func: Callable,
    name: str,
    server_name: str,
    capability_name: str,
    capability_type: str,
) -> Callable:
    """Create a typed handler function that forwards to ProxiedMCP methods."""
    parameters = [
        inspect.Parameter(
            name="ctx",
            annotation=Context,
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
    ]
    annotations = {"ctx": Context, "return": return_type}
    for param_name, type_ann in param_signatures:
        parameters.append(
            inspect.Parameter(
                name=param_name,
                annotation=type_ann,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        )
        annotations[param_name] = type_ann
    sig = inspect.Signature(parameters=parameters)

    async def dynamic_handler(*args, **kwargs):
        ctx = kwargs.get("ctx", args[0] if args else None)
        handler_kwargs = {k: v for k, v in kwargs.items() if k != "ctx"}
        try:
            result = await handler_func(
                name=capability_name,
                arguments=handler_kwargs,
                mcp_context=ctx,
            )
            return result
        except AnalysisError as se:
            if capability_type == "tool":
                return types.CallToolResult(
                    content=[
                        types.TextContent(type="text", text=f"Gateway policy violation: {se}")
                    ],
                    isError=True,
                )
            else:
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="assistant",
                            content=types.TextContent(
                                type="text", text=f"Gateway policy violation: {se}"
                            ),
                        )
                    ]
                )
        except Exception as e:
            logger.error(
                f"Error executing {capability_type} '{name}': {e}",
                exc_info=True,
            )
            if capability_type == "tool":
                return types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text", text=f"Error executing {capability_type} '{name}': {e}"
                        )
                    ],
                    isError=True,
                )
            else:
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="assistant",
                            content=types.TextContent(
                                type="text",
                                text=f"Error executing {capability_type} '{name}': {e}",
                            ),
                        )
                    ]
                )

    dynamic_handler.__signature__ = sig
    dynamic_handler.__annotations__ = annotations
    return dynamic_handler


def register_downstream_capabilities(gateway_mcp: FastMCP, context: GatewayContext):
    """Dynamically register all downstream tools and prompts with the gateway."""
    logger.info("Registering downstream capabilities with the gateway...")
    registered_tools = 0
    registered_prompts = 0

    for server_name, proxied_server in context.proxied_servers.items():
        if not proxied_server.session:
            logger.warning(f"Skipping registration for inactive server: {server_name}")
            continue

        # Register tools
        for tool in proxied_server._tools:
            dynamic_tool_name = f"{server_name}_{tool.name}"
            param_signatures = _get_param_signatures_from_schema(
                tool.inputSchema if hasattr(tool, "inputSchema") else None
            )
            handler = _create_dynamic_handler(
                param_signatures=param_signatures,
                return_type=types.CallToolResult,
                handler_func=proxied_server.call_tool,
                name=dynamic_tool_name,
                server_name=server_name,
                capability_name=tool.name,
                capability_type="tool",
            )
            handler.__name__ = dynamic_tool_name
            handler.__doc__ = tool.description or f"Proxied tool from {server_name}"
            
            tool_decorator = gateway_mcp.tool(name=dynamic_tool_name, description=tool.description)
            tool_decorator(handler)
            registered_tools += 1
            logger.debug(f"Registered tool: {dynamic_tool_name}")

        # Register prompts
        for prompt in proxied_server._prompts:
            dynamic_prompt_name = f"{server_name}_{prompt.name}"
            param_signatures = _get_param_signatures_from_schema(prompt, is_prompt=True)
            handler = _create_dynamic_handler(
                param_signatures=param_signatures,
                return_type=types.GetPromptResult,
                handler_func=proxied_server.get_prompt,
                name=dynamic_prompt_name,
                server_name=server_name,
                capability_name=prompt.name,
                capability_type="prompt",
            )
            handler.__name__ = dynamic_prompt_name
            handler.__doc__ = prompt.description or f"Proxied prompt from {server_name}"
            
            prompt_decorator = gateway_mcp.prompt(
                name=dynamic_prompt_name, description=prompt.description
            )
            prompt_decorator(handler)
            registered_prompts += 1
            logger.debug(f"Registered prompt: {dynamic_prompt_name}")

    logger.info(
        f"Registration complete: {registered_tools} tools and {registered_prompts} prompts"
    )


async def validate_credentials(tracking_id: str, api_key: str, session_id: str):
    try:
        client = ArgusClient.create(
            api_key=api_key,
            asset_id=tracking_id,
            session_id=session_id,
            save=False,
        )
        test_result = client.check_content(content="test validation content")
        if test_result["verdict"] not in [Verdict.PASSED, Verdict.FLAGGED, Verdict.BLOCKED]:
            logging.getLogger(__name__).warning(
                f"Unexpected verdict result: {test_result['verdict']}"
            )
    except Exception as e:
        if "401" in str(e) or "unauthorized" in str(e).lower():
            raise ValueError(
                "Invalid tracking_id or api_key. Please check your credentials."
            ) from e
        elif "connection" in str(e).lower() or "network" in str(e).lower():
            raise ValueError(
                "Could not connect to the Repello Argus API. Please check your network connection."
            ) from e
        else:
            raise ValueError(f"Credential validation failed: {e}") from e


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[GatewayContext]:
    global cli_args
    session_id = str(uuid.uuid4())

    await validate_credentials(cli_args.tracking_id, cli_args.api_key, session_id)

    proxied_server_configs = load_config(cli_args.mcp_json_path)
    context = GatewayContext(
        tracking_id=cli_args.tracking_id,
        api_key=cli_args.api_key,
        session_id=session_id,
    )

    for name, server_config in proxied_server_configs.items():
        proxied_server = ProxiedMCP(name, server_config)
        context.proxied_servers[name] = proxied_server

    if context.proxied_servers:
        start_tasks = [s.start() for s in context.proxied_servers.values()]
        if start_tasks:
            results = await asyncio.gather(*start_tasks, return_exceptions=True)
            failed_servers = []
            for i, result in enumerate(results):
                server_name = list(context.proxied_servers.keys())[i]
                if isinstance(result, Exception):
                    failed_servers.append(server_name)
            for name in failed_servers:
                context.proxied_servers.pop(name, None)

    # Register all downstream tools and prompts with the gateway
    register_downstream_capabilities(server, context)

    try:
        yield context
    finally:
        stop_tasks = [s.stop() for s in context.proxied_servers.values() if s._session is not None]
        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)


mcp = FastMCP("MCP Gateway", lifespan=lifespan)


@mcp.tool()
async def get_metadata(ctx: Context) -> Dict[str, Any]:
    """Provides metadata about all available proxied MCPs from the active GatewayContext."""
    gateway_context: GatewayContext = ctx.request_context.lifespan_context
    metadata: Dict[str, Any] = {}

    if not gateway_context.proxied_servers:
        return {"status": "standalone_mode", "message": "No proxied MCPs configured"}

    for name, server in gateway_context.proxied_servers.items():
        server_metadata: Dict[str, Any] = {
            "status": "inactive",
            "capabilities": None,
            "original_tools": [],
            "original_resources": [],
            "original_prompts": [],
        }

        if not server or not server.session:
            server_metadata["error"] = "Server session not active or start failed"
            metadata[name] = server_metadata
            continue

        try:
            server_metadata["status"] = "active"
            capabilities = await server.get_capabilities()
            server_metadata["capabilities"] = (
                capabilities.model_dump() if capabilities else None
            )

            if capabilities and capabilities.tools:
                server_metadata["original_tools"] = [
                    tool.model_dump() for tool in server._tools
                ]
            if capabilities and capabilities.resources:
                server_metadata["original_resources"] = [
                    res.model_dump() for res in server._resources
                ]
            if capabilities and capabilities.prompts:
                server_metadata["original_prompts"] = [
                    p.model_dump() for p in server._prompts
                ]

            metadata[name] = server_metadata
        except Exception as e:
            metadata[name] = {
                "status": "error",
                "error": f"Failed to retrieve metadata: {e}",
            }
    return metadata


def parse_args(args=None):
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="MCP Gateway Server")
    parser.add_argument(
        "--mcp-json-path",
        type=str,
        required=True,
        help="Path to the mcp.json configuration file",
    )
    parser.add_argument(
        "--tracking-id",
        type=str,
        required=True,
        help="The tracking ID (asset_id) for the Repello Argus API.",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        required=True,
        help="The API key for the Repello Argus API.",
    )

    if args is None:
        args = sys.argv[1:]
    return parser.parse_args(args)


def main():
    """Main entry point for the server."""
    global cli_args
    cli_args = parse_args()

    logger.info("Starting MCP gateway server directly...")
    mcp.run()


if __name__ == "__main__":
    main()
