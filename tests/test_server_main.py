import sys
from unittest.mock import patch

import pytest

try:
    from worksbyworrell.warlock.main import main
except ImportError:
    main = None


def test_server_entrypoint_is_defined():
    assert main is not None, "Server main entrypoint is not defined."


@pytest.mark.skipif(main is None, reason="Server entrypoint not yet implemented.")
@patch("worksbyworrell.warlock.main.mcp")
def test_main_starts_with_stdio(mock_mcp):
    """Verify that the server defaults to stdio transport."""
    test_args = ["warlock-mcp"]
    with patch.object(sys, "argv", test_args):
        main()
    mock_mcp.run.assert_called_once_with(transport="stdio")


@pytest.mark.skipif(main is None, reason="Server entrypoint not yet implemented.")
@patch("worksbyworrell.warlock.main.mcp")
@patch("worksbyworrell.warlock.main.uvicorn")
def test_main_starts_with_streamable_http(mock_uvicorn, mock_mcp):
    """Verify that the server can start with streamable-http transport."""
    mock_mcp.settings.log_level = "info"
    test_args = [
        "warlock-mcp",
        "--transport",
        "streamable-http",
        "--host",
        "127.0.0.1",
        "--port",
        "9090",
    ]
    with patch.object(sys, "argv", test_args):
        main()
    assert mock_mcp.settings.host == "127.0.0.1"
    assert mock_mcp.settings.port == 9090
    assert mock_mcp.settings.transport_security.enable_dns_rebinding_protection is False
    mock_uvicorn.run.assert_called_once()
    assert mock_uvicorn.run.call_args.kwargs["host"] == "127.0.0.1"
    assert mock_uvicorn.run.call_args.kwargs["port"] == 9090


@pytest.mark.skipif(main is None, reason="Server entrypoint not yet implemented.")
@patch("worksbyworrell.warlock.main.mcp")
@patch("worksbyworrell.warlock.main.uvicorn")
def test_main_starts_with_sse(mock_uvicorn, mock_mcp):
    """Verify that the server can start with the standard sse transport."""
    mock_mcp.settings.log_level = "info"
    test_args = ["warlock-mcp", "--transport", "sse", "--host", "0.0.0.0", "--port", "8080"]
    with patch.object(sys, "argv", test_args):
        main()
    assert mock_mcp.settings.host == "0.0.0.0"
    assert mock_mcp.settings.port == 8080
    assert mock_mcp.settings.transport_security.enable_dns_rebinding_protection is False
    mock_uvicorn.run.assert_called_once()
    assert mock_uvicorn.run.call_args.kwargs["host"] == "0.0.0.0"
    assert mock_uvicorn.run.call_args.kwargs["port"] == 8080
