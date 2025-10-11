"""Unit tests for tools endpoint."""

import pytest
from fastapi import HTTPException

from llama_stack_client import APIConnectionError

# Import the function directly to bypass decorators
from app.endpoints import tools
from models.responses import ToolsResponse
from models.config import (
    Configuration,
    ServiceConfiguration,
    LlamaStackConfiguration,
    UserDataCollection,
    ModelContextProtocolServer,
)

# Shared mock auth tuple with 4 fields as expected by the application
MOCK_AUTH = ("mock_user_id", "mock_username", False, "mock_token")


@pytest.fixture
def mock_configuration():
    """Create a mock configuration with MCP servers."""
    return Configuration(
        name="test",
        service=ServiceConfiguration(),
        llama_stack=LlamaStackConfiguration(url="http://localhost:8321"),
        user_data_collection=UserDataCollection(feedback_enabled=False),
        mcp_servers=[
            ModelContextProtocolServer(
                name="filesystem-tools",
                provider_id="model-context-protocol",
                url="http://localhost:3000",
            ),
            ModelContextProtocolServer(
                name="git-tools",
                provider_id="model-context-protocol",
                url="http://localhost:3001",
            ),
        ],
    )


@pytest.fixture
def mock_tools_response(mocker):
    """Create mock tools response from LlamaStack client."""
    # Create mock tools that behave like dict when converted
    tool1 = mocker.Mock()
    tool1.__dict__.update(
        {
            "identifier": "filesystem_read",
            "description": "Read contents of a file from the filesystem",
            "parameters": [
                {
                    "name": "path",
                    "description": "Path to the file to read",
                    "parameter_type": "string",
                    "required": True,
                    "default": None,
                }
            ],
            "provider_id": "model-context-protocol",
            "toolgroup_id": "filesystem-tools",
            "type": "tool",
            "metadata": {},
        }
    )
    # Make dict() work on the mock
    tool1.keys.return_value = tool1.__dict__.keys()
    tool1.__getitem__ = lambda self, key: self.__dict__[key]
    tool1.__iter__ = lambda self: iter(self.__dict__)

    tool2 = mocker.Mock()
    tool2.__dict__.update(
        {
            "identifier": "git_status",
            "description": "Get the status of a git repository",
            "parameters": [
                {
                    "name": "repository_path",
                    "description": "Path to the git repository",
                    "parameter_type": "string",
                    "required": True,
                    "default": None,
                }
            ],
            "provider_id": "model-context-protocol",
            "toolgroup_id": "git-tools",
            "type": "tool",
            "metadata": {},
        }
    )
    # Make dict() work on the mock
    tool2.keys.return_value = tool2.__dict__.keys()
    tool2.__getitem__ = lambda self, key: self.__dict__[key]
    tool2.__iter__ = lambda self: iter(self.__dict__)

    return [tool1, tool2]


@pytest.mark.asyncio
async def test_tools_endpoint_success(
    mocker, mock_configuration, mock_tools_response
):  # pylint: disable=redefined-outer-name
    """Test successful tools endpoint response."""
    # Mock configuration
    mocker.patch("app.endpoints.tools.configuration", mock_configuration)

    # Mock authorization decorator to bypass i
    mocker.patch("app.endpoints.tools.authorize", lambda action: lambda func: func)

    # Mock client holder and clien
    mock_client_holder = mocker.patch("app.endpoints.tools.AsyncLlamaStackClientHolder")
    mock_client = mocker.AsyncMock()
    mock_client_holder.return_value.get_client.return_value = mock_client

    # Mock toolgroups.list response
    mock_toolgroup1 = mocker.Mock()
    mock_toolgroup1.identifier = "filesystem-tools"
    mock_toolgroup2 = mocker.Mock()
    mock_toolgroup2.identifier = "git-tools"
    mock_client.toolgroups.list.return_value = [mock_toolgroup1, mock_toolgroup2]

    # Mock tools.list responses for each MCP server
    mock_client.tools.list.side_effect = [
        [mock_tools_response[0]],  # filesystem-tools response
        [mock_tools_response[1]],  # git-tools response
    ]

    # Mock request and auth
    mock_request = mocker.Mock()
    mock_auth = MOCK_AUTH

    # Call the endpoint
    response = await tools.tools_endpoint_handler.__wrapped__(mock_request, mock_auth)

    # Verify response
    assert isinstance(response, ToolsResponse)
    assert len(response.tools) == 2

    # Verify first tool
    tool1 = response.tools[0]
    assert tool1["identifier"] == "filesystem_read"
    assert tool1["description"] == "Read contents of a file from the filesystem"
    assert tool1["server_source"] == "http://localhost:3000"
    assert tool1["toolgroup_id"] == "filesystem-tools"

    # Verify second tool
    tool2 = response.tools[1]
    assert tool2["identifier"] == "git_status"
    assert tool2["description"] == "Get the status of a git repository"
    assert tool2["server_source"] == "http://localhost:3001"
    assert tool2["toolgroup_id"] == "git-tools"

    # Verify client calls
    assert mock_client.tools.list.call_count == 2
    mock_client.tools.list.assert_any_call(toolgroup_id="filesystem-tools")
    mock_client.tools.list.assert_any_call(toolgroup_id="git-tools")


@pytest.mark.asyncio
async def test_tools_endpoint_no_mcp_servers(mocker):
    """Test tools endpoint with no MCP servers configured."""
    # Mock configuration with no MCP servers
    mock_config = Configuration(
        name="test",
        service=ServiceConfiguration(),
        llama_stack=LlamaStackConfiguration(url="http://localhost:8321"),
        user_data_collection=UserDataCollection(feedback_enabled=False),
        mcp_servers=[],
    )
    mocker.patch("app.endpoints.tools.configuration", mock_config)

    # Mock authorization decorator to bypass i
    mocker.patch("app.endpoints.tools.authorize", lambda action: lambda func: func)

    # Mock client holder and clien
    mock_client_holder = mocker.patch("app.endpoints.tools.AsyncLlamaStackClientHolder")
    mock_client = mocker.AsyncMock()
    mock_client_holder.return_value.get_client.return_value = mock_client

    # Mock toolgroups.list response - empty for no MCP servers
    mock_client.toolgroups.list.return_value = []

    # Mock request and auth
    mock_request = mocker.Mock()
    mock_auth = MOCK_AUTH

    # Call the endpoint
    response = await tools.tools_endpoint_handler.__wrapped__(mock_request, mock_auth)

    # Verify response
    assert isinstance(response, ToolsResponse)
    assert len(response.tools) == 0


@pytest.mark.asyncio
async def test_tools_endpoint_api_connection_error(
    mocker, mock_configuration
):  # pylint: disable=redefined-outer-name
    """Test tools endpoint with API connection error from individual servers."""
    # Mock configuration
    mocker.patch("app.endpoints.tools.configuration", mock_configuration)

    # Mock authorization decorator to bypass i
    mocker.patch("app.endpoints.tools.authorize", lambda action: lambda func: func)

    # Mock client holder and clien
    mock_client_holder = mocker.patch("app.endpoints.tools.AsyncLlamaStackClientHolder")
    mock_client = mocker.AsyncMock()
    mock_client_holder.return_value.get_client.return_value = mock_client

    # Mock toolgroups.list response
    mock_toolgroup1 = mocker.Mock()
    mock_toolgroup1.identifier = "filesystem-tools"
    mock_toolgroup2 = mocker.Mock()
    mock_toolgroup2.identifier = "git-tools"
    mock_client.toolgroups.list.return_value = [mock_toolgroup1, mock_toolgroup2]

    # Mock API connection error - create a proper APIConnectionError
    api_error = APIConnectionError(request=mocker.Mock())
    mock_client.tools.list.side_effect = api_error

    # Mock request and auth
    mock_request = mocker.Mock()
    mock_auth = MOCK_AUTH

    # Call the endpointt - should not raise exception but return empty tools
    response = await tools.tools_endpoint_handler.__wrapped__(mock_request, mock_auth)

    # Verify response - should be empty since all servers failed
    assert isinstance(response, ToolsResponse)
    assert len(response.tools) == 0


@pytest.mark.asyncio
async def test_tools_endpoint_partial_failure(  # pylint: disable=redefined-outer-name
    mocker, mock_configuration, mock_tools_response
):
    """Test tools endpoint with one MCP server failing."""
    # Mock configuration
    mocker.patch("app.endpoints.tools.configuration", mock_configuration)

    # Mock authorization decorator to bypass i
    mocker.patch("app.endpoints.tools.authorize", lambda action: lambda func: func)

    # Mock client holder and clien
    mock_client_holder = mocker.patch("app.endpoints.tools.AsyncLlamaStackClientHolder")
    mock_client = mocker.AsyncMock()
    mock_client_holder.return_value.get_client.return_value = mock_client

    # Mock toolgroups.list response
    mock_toolgroup1 = mocker.Mock()
    mock_toolgroup1.identifier = "filesystem-tools"
    mock_toolgroup2 = mocker.Mock()
    mock_toolgroup2.identifier = "git-tools"
    mock_client.toolgroups.list.return_value = [mock_toolgroup1, mock_toolgroup2]

    # Mock tools.list responses - first succeeds, second fails
    mock_client.tools.list.side_effect = [
        [mock_tools_response[0]],  # filesystem-tools response
        Exception("Server unavailable"),  # git-tools fails
    ]

    # Mock request and auth
    mock_request = mocker.Mock()
    mock_auth = MOCK_AUTH

    # Call the endpoint
    response = await tools.tools_endpoint_handler.__wrapped__(mock_request, mock_auth)

    # Verify response - should have only one tool from the successful server
    assert isinstance(response, ToolsResponse)
    assert len(response.tools) == 1
    assert response.tools[0]["identifier"] == "filesystem_read"
    assert response.tools[0]["server_source"] == "http://localhost:3000"

    # Verify both servers were attempted
    assert mock_client.tools.list.call_count == 2


@pytest.mark.asyncio
async def test_tools_endpoint_builtin_toolgroup(
    mocker, mock_configuration
):  # pylint: disable=redefined-outer-name
    """Test tools endpoint with built-in toolgroups."""
    # Mock configuration
    mocker.patch("app.endpoints.tools.configuration", mock_configuration)

    # Mock authorization decorator to bypass i
    mocker.patch("app.endpoints.tools.authorize", lambda action: lambda func: func)

    # Mock client holder and clien
    mock_client_holder = mocker.patch("app.endpoints.tools.AsyncLlamaStackClientHolder")
    mock_client = mocker.AsyncMock()
    mock_client_holder.return_value.get_client.return_value = mock_client

    # Mock toolgroups.list response with built-in toolgroup
    mock_toolgroup = mocker.Mock()
    mock_toolgroup.identifier = "builtin-tools"  # Not in MCP server names
    mock_client.toolgroups.list.return_value = [mock_toolgroup]

    # Mock tools.list response for built-in toolgroup
    mock_tool = mocker.Mock()
    mock_tool.__dict__.update(
        {
            "identifier": "builtin_tool",
            "description": "A built-in tool",
            "parameters": [],
            "provider_id": "builtin",
            "toolgroup_id": "builtin-tools",
            "type": "tool",
            "metadata": {},
        }
    )
    mock_tool.keys.return_value = mock_tool.__dict__.keys()
    mock_tool.__getitem__ = lambda self, key: self.__dict__[key]
    mock_tool.__iter__ = lambda self: iter(self.__dict__)

    mock_client.tools.list.return_value = [mock_tool]

    # Mock request and auth
    mock_request = mocker.Mock()
    mock_auth = MOCK_AUTH

    # Call the endpoint
    response = await tools.tools_endpoint_handler.__wrapped__(mock_request, mock_auth)

    # Verify response
    assert isinstance(response, ToolsResponse)
    assert len(response.tools) == 1
    assert response.tools[0]["identifier"] == "builtin_tool"
    assert response.tools[0]["server_source"] == "builtin"


@pytest.mark.asyncio
async def test_tools_endpoint_mixed_toolgroups(mocker):
    """Test tools endpoint with both MCP and built-in toolgroups."""
    # Mock configuration with MCP servers
    mock_config = Configuration(
        name="test",
        service=ServiceConfiguration(),
        llama_stack=LlamaStackConfiguration(url="http://localhost:8321"),
        user_data_collection=UserDataCollection(feedback_enabled=False),
        mcp_servers=[
            ModelContextProtocolServer(
                name="filesystem-tools",
                provider_id="model-context-protocol",
                url="http://localhost:3000",
            ),
        ],
    )
    mocker.patch("app.endpoints.tools.configuration", mock_config)

    # Mock authorization decorator to bypass i
    mocker.patch("app.endpoints.tools.authorize", lambda action: lambda func: func)

    # Mock client holder and clien
    mock_client_holder = mocker.patch("app.endpoints.tools.AsyncLlamaStackClientHolder")
    mock_client = mocker.AsyncMock()
    mock_client_holder.return_value.get_client.return_value = mock_client

    # Mock toolgroups.list response with both MCP and built-in toolgroups
    mock_toolgroup1 = mocker.Mock()
    mock_toolgroup1.identifier = "filesystem-tools"  # MCP server toolgroup
    mock_toolgroup2 = mocker.Mock()
    mock_toolgroup2.identifier = "builtin-tools"  # Built-in toolgroup
    mock_client.toolgroups.list.return_value = [mock_toolgroup1, mock_toolgroup2]

    # Mock tools.list responses
    mock_tool1 = mocker.Mock()
    mock_tool1.__dict__.update(
        {
            "identifier": "filesystem_read",
            "description": "Read file",
            "parameters": [],
            "provider_id": "model-context-protocol",
            "toolgroup_id": "filesystem-tools",
            "type": "tool",
            "metadata": {},
        }
    )
    mock_tool1.keys.return_value = mock_tool1.__dict__.keys()
    mock_tool1.__getitem__ = lambda self, key: self.__dict__[key]
    mock_tool1.__iter__ = lambda self: iter(self.__dict__)

    mock_tool2 = mocker.Mock()
    mock_tool2.__dict__.update(
        {
            "identifier": "builtin_tool",
            "description": "Built-in tool",
            "parameters": [],
            "provider_id": "builtin",
            "toolgroup_id": "builtin-tools",
            "type": "tool",
            "metadata": {},
        }
    )
    mock_tool2.keys.return_value = mock_tool2.__dict__.keys()
    mock_tool2.__getitem__ = lambda self, key: self.__dict__[key]
    mock_tool2.__iter__ = lambda self: iter(self.__dict__)

    mock_client.tools.list.side_effect = [[mock_tool1], [mock_tool2]]

    # Mock request and auth
    mock_request = mocker.Mock()
    mock_auth = MOCK_AUTH

    # Call the endpoint
    response = await tools.tools_endpoint_handler.__wrapped__(mock_request, mock_auth)

    # Verify response - should have both tools with correct server sources
    assert isinstance(response, ToolsResponse)
    assert len(response.tools) == 2

    # Find tools by identifier to avoid order dependency
    mcp_tool = next(t for t in response.tools if t["identifier"] == "filesystem_read")
    builtin_tool = next(t for t in response.tools if t["identifier"] == "builtin_tool")

    assert mcp_tool["server_source"] == "http://localhost:3000"
    assert builtin_tool["server_source"] == "builtin"


@pytest.mark.asyncio
async def test_tools_endpoint_value_attribute_error(
    mocker, mock_configuration
):  # pylint: disable=redefined-outer-name
    """Test tools endpoint with ValueError/AttributeError in toolgroups.list."""
    # Mock configuration
    mocker.patch("app.endpoints.tools.configuration", mock_configuration)

    # Mock authorization decorator to bypass i
    mocker.patch("app.endpoints.tools.authorize", lambda action: lambda func: func)

    # Mock client holder and clien
    mock_client_holder = mocker.patch("app.endpoints.tools.AsyncLlamaStackClientHolder")
    mock_client = mocker.AsyncMock()
    mock_client_holder.return_value.get_client.return_value = mock_client

    # Mock toolgroups.list to raise ValueError
    mock_client.toolgroups.list.side_effect = ValueError("Invalid response format")

    # Mock request and auth
    mock_request = mocker.Mock()
    mock_auth = MOCK_AUTH

    # Call the endpointt - should not raise exception but return empty tools
    response = await tools.tools_endpoint_handler.__wrapped__(mock_request, mock_auth)

    # Verify response - should be empty since toolgroups.list failed
    assert isinstance(response, ToolsResponse)
    assert len(response.tools) == 0


@pytest.mark.asyncio
async def test_tools_endpoint_apiconnection_error_toolgroups(  # pylint: disable=redefined-outer-name
    mocker, mock_configuration
):
    """Test tools endpoint with APIConnectionError in toolgroups.list."""
    # Mock configuration
    mocker.patch("app.endpoints.tools.configuration", mock_configuration)

    # Mock authorization decorator to bypass i
    mocker.patch("app.endpoints.tools.authorize", lambda action: lambda func: func)

    # Mock client holder and clien
    mock_client_holder = mocker.patch("app.endpoints.tools.AsyncLlamaStackClientHolder")
    mock_client = mocker.AsyncMock()
    mock_client_holder.return_value.get_client.return_value = mock_client

    # Mock toolgroups.list to raise APIConnectionError
    api_error = APIConnectionError(request=mocker.Mock())
    mock_client.toolgroups.list.side_effect = api_error

    # Mock request and auth
    mock_request = mocker.Mock()
    mock_auth = MOCK_AUTH

    # Call the endpointt and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await tools.tools_endpoint_handler.__wrapped__(mock_request, mock_auth)

    assert exc_info.value.status_code == 500
    assert "Unable to connect to Llama Stack" in exc_info.value.detail["response"]


@pytest.mark.asyncio
async def test_tools_endpoint_client_holder_apiconnection_error(  # pylint: disable=redefined-outer-name
    mocker, mock_configuration
):
    """Test tools endpoint with APIConnectionError in client holder."""
    # Mock configuration
    mocker.patch("app.endpoints.tools.configuration", mock_configuration)

    # Mock authorization decorator to bypass i
    mocker.patch("app.endpoints.tools.authorize", lambda action: lambda func: func)

    # Mock client holder to raise APIConnectionError
    mock_client_holder = mocker.patch("app.endpoints.tools.AsyncLlamaStackClientHolder")
    api_error = APIConnectionError(request=mocker.Mock())
    mock_client_holder.return_value.get_client.side_effect = api_error

    # Mock request and auth
    mock_request = mocker.Mock()
    mock_auth = MOCK_AUTH

    # Call the endpointt and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await tools.tools_endpoint_handler.__wrapped__(mock_request, mock_auth)

    assert exc_info.value.status_code == 500
    assert "Unable to connect to Llama Stack" in exc_info.value.detail["response"]


@pytest.mark.asyncio
async def test_tools_endpoint_general_exception(
    mocker, mock_configuration
):  # pylint: disable=redefined-outer-name
    """Test tools endpoint with general exception."""
    # Mock configuration
    mocker.patch("app.endpoints.tools.configuration", mock_configuration)

    # Mock authorization decorator to bypass i
    mocker.patch("app.endpoints.tools.authorize", lambda action: lambda func: func)

    # Mock client holder to raise exception
    mock_client_holder = mocker.patch("app.endpoints.tools.AsyncLlamaStackClientHolder")
    mock_client_holder.return_value.get_client.side_effect = Exception(
        "Unexpected error"
    )

    # Mock request and auth
    mock_request = mocker.Mock()
    mock_auth = MOCK_AUTH

    # Call the endpointt and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await tools.tools_endpoint_handler.__wrapped__(mock_request, mock_auth)

    assert exc_info.value.status_code == 500
    assert "Unable to retrieve list of tools" in exc_info.value.detail["response"]
