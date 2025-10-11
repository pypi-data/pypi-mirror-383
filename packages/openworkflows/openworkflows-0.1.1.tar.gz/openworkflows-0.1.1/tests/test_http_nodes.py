"""Tests for HTTP request nodes."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from openworkflows import Workflow


@pytest.mark.asyncio
async def test_http_get_basic():
    """Test basic HTTP GET request with URL template."""
    workflow = Workflow()
    workflow.add_node(
        "fetch", "http_get", {"url_template": "https://api.example.com/users/{user_id}"}
    )

    # Mock the HTTP client
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 123, "name": "John Doe"}
    mock_response.headers = {"content-type": "application/json"}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await workflow.run(inputs={"user_id": 123})

    assert result["fetch"]["status_code"] == 200
    assert result["fetch"]["body"] == {"id": 123, "name": "John Doe"}
    assert "content-type" in result["fetch"]["headers"]
    mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_http_post_with_body():
    """Test HTTP POST request with URL and body templates."""
    workflow = Workflow()
    workflow.add_node(
        "create_user",
        "http_post",
        {
            "url_template": "https://api.example.com/users",
            "body_template": '{"name": "{name}", "email": "{email}"}',
        },
    )

    # Mock the HTTP client
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 456, "name": "Jane Doe", "email": "jane@example.com"}
    mock_response.headers = {"content-type": "application/json"}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await workflow.run(inputs={"name": "Jane Doe", "email": "jane@example.com"})

    assert result["create_user"]["status_code"] == 201
    assert result["create_user"]["body"]["id"] == 456
    mock_post.assert_called_once()
    # Verify body was filled correctly
    call_kwargs = mock_post.call_args.kwargs
    assert '"name": "Jane Doe"' in call_kwargs["content"]
    assert '"email": "jane@example.com"' in call_kwargs["content"]


@pytest.mark.asyncio
async def test_http_request_node_get():
    """Test generic HTTP request node with GET method."""
    workflow = Workflow()
    workflow.add_node(
        "fetch",
        "http_request",
        {
            "method": "GET",
            "url_template": "https://api.example.com/posts/{post_id}",
        },
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "title": "Test Post"}
    mock_response.headers = {}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await workflow.run(inputs={"post_id": 1})

    assert result["fetch"]["status_code"] == 200
    assert result["fetch"]["body"]["title"] == "Test Post"


@pytest.mark.asyncio
async def test_http_request_node_post():
    """Test generic HTTP request node with POST method."""
    workflow = Workflow()
    workflow.add_node(
        "create",
        "http_request",
        {
            "method": "POST",
            "url_template": "https://api.example.com/posts",
            "body_template": '{"title": "{title}", "content": "{content}"}',
        },
    )

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 2, "title": "New Post"}
    mock_response.headers = {}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await workflow.run(inputs={"title": "New Post", "content": "Some content"})

    assert result["create"]["status_code"] == 201


@pytest.mark.asyncio
async def test_http_get_with_custom_headers():
    """Test HTTP GET with custom headers."""
    workflow = Workflow()
    workflow.add_node(
        "fetch",
        "http_get",
        {
            "url_template": "https://api.example.com/data",
            "headers": {"Authorization": "Bearer token123", "X-Custom": "value"},
        },
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "data"
    mock_response.json.side_effect = Exception("Not JSON")
    mock_response.headers = {}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await workflow.run()

    # Verify headers were passed
    call_kwargs = mock_get.call_args.kwargs
    assert call_kwargs["headers"]["Authorization"] == "Bearer token123"
    assert call_kwargs["headers"]["X-Custom"] == "value"
    # Non-JSON response should return text
    assert result["fetch"]["body"] == "data"


@pytest.mark.asyncio
async def test_http_missing_template_variable():
    """Test that missing template variables raise an error."""
    workflow = Workflow()
    workflow.add_node(
        "fetch", "http_get", {"url_template": "https://api.example.com/users/{user_id}"}
    )

    with pytest.raises(Exception, match="Missing URL template variable"):
        # No user_id provided
        await workflow.run()


@pytest.mark.asyncio
async def test_http_post_missing_body_variable():
    """Test that missing body template variables raise an error."""
    workflow = Workflow()
    workflow.add_node(
        "create",
        "http_post",
        {
            "url_template": "https://api.example.com/users",
            "body_template": '{"name": "{name}", "email": "{email}"}',
        },
    )

    with pytest.raises(Exception, match="Missing body template variable"):
        # Only name provided, email missing
        await workflow.run(inputs={"name": "John"})


@pytest.mark.asyncio
async def test_http_variables_from_upstream_node():
    """Test HTTP node receiving variables from upstream node."""
    workflow = Workflow()
    workflow.add_node("prepare", "merge", {"mode": "dict"})
    workflow.add_node(
        "fetch",
        "http_get",
        {"url_template": "https://api.example.com/users/{user_id}"},
    )

    workflow.connect("prepare.result", "fetch.variables")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 999}
    mock_response.headers = {}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await workflow.run(inputs={"user_id": 999})

    assert result["fetch"]["status_code"] == 200


@pytest.mark.asyncio
async def test_http_request_all_methods():
    """Test that all HTTP methods work correctly."""
    methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

    for method in methods:
        workflow = Workflow()
        config = {
            "method": method,
            "url_template": "https://api.example.com/resource",
        }
        if method in ["POST", "PUT", "PATCH"]:
            config["body_template"] = '{"data": "test"}'
        workflow.add_node("request", "http_request", config)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "ok"
        mock_response.json.side_effect = Exception("Not JSON")
        mock_response.headers = {}

        client_method = method.lower()
        with patch(f"httpx.AsyncClient.{client_method}", new_callable=AsyncMock) as mock_method:
            mock_method.return_value = mock_response

            result = await workflow.run()

        assert result["request"]["status_code"] == 200
        mock_method.assert_called_once()


@pytest.mark.asyncio
async def test_http_timeout_parameter():
    """Test that timeout parameter is used."""
    workflow = Workflow()
    workflow.add_node(
        "fetch",
        "http_get",
        {
            "url_template": "https://api.example.com/data",
            "timeout": 60,
        },
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "data"
    mock_response.json.side_effect = Exception("Not JSON")
    mock_response.headers = {}

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        _ = await workflow.run()

    # Verify timeout was passed to AsyncClient
    mock_client_class.assert_called_once_with(timeout=60)
