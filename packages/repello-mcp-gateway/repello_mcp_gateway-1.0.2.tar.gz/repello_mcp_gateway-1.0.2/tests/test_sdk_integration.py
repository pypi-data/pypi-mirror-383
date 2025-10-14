import uuid
from unittest.mock import MagicMock, patch

import pytest

from mcp_gateway.server import GatewayContext, validate_credentials


MOCK_TRACKING_ID = "asset-123"
MOCK_API_KEY = "secret-key"
MOCK_SESSION_ID = str(uuid.uuid4())


def test_parse_args_still_available():
    from mcp_gateway.server import parse_args

    args = [
        "--mcp-json-path",
        "/path/to/mcp.json",
        "--tracking-id",
        MOCK_TRACKING_ID,
        "--api-key",
        MOCK_API_KEY,
    ]
    parsed_args = parse_args(args)
    assert parsed_args.mcp_json_path == "/path/to/mcp.json"
    assert parsed_args.tracking_id == MOCK_TRACKING_ID
    assert parsed_args.api_key == MOCK_API_KEY


@patch("mcp_gateway.server.ArgusClient")
@pytest.mark.asyncio
async def test_validate_credentials_success(mock_client):
    instance = MagicMock()
    instance.check_content.return_value = {"verdict": "passed"}
    mock_client.create.return_value = instance

    await validate_credentials(MOCK_TRACKING_ID, MOCK_API_KEY, MOCK_SESSION_ID)
    mock_client.create.assert_called_once()
    instance.check_content.assert_called_once()


@patch("mcp_gateway.server.ArgusClient")
@pytest.mark.asyncio
async def test_validate_credentials_invalid_key(mock_client):
    mock_client.create.side_effect = Exception("401 Unauthorized")
    with pytest.raises(ValueError, match="Invalid tracking_id or api_key"):
        await validate_credentials(MOCK_TRACKING_ID, "invalid", MOCK_SESSION_ID)


@patch("mcp_gateway.proxied_mcp.ArgusClient")
@pytest.mark.asyncio
async def test_tool_call_uses_sdk(mock_client):
    from mcp_gateway.proxied_mcp import ProxiedMCP

    client_instance = MagicMock()
    client_instance.check_content.return_value = {"verdict": "passed"}
    mock_client.create.return_value = client_instance

    server = ProxiedMCP("s", {"url": "http://example"})
    # inject fake session methods for unit test context
    server._session = MagicMock()
    server._tools = []
    
    # Mock call_tool to return an awaitable
    async def mock_call_tool(name, arguments):
        return {"ok": True}
    
    server._session.call_tool = mock_call_tool

    result = await server.call_tool("t", {"a": 1}, mcp_context=MagicMock(request_context=MagicMock(lifespan_context=GatewayContext(tracking_id=MOCK_TRACKING_ID, api_key=MOCK_API_KEY, session_id=MOCK_SESSION_ID))))
    assert result == {"ok": True}
