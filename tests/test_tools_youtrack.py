from unittest.mock import MagicMock, patch

import httpx
import pytest

from worksbyworrell.warlock.tools.youtrack import _request


@pytest.mark.anyio
@patch.dict(
    "os.environ",
    {"YOUTRACK_URL": "https://youtrack.example.com", "YOUTRACK_TOKEN": "perm-test-token"},
)
@patch("httpx.AsyncClient.request")
async def test_request_retries_on_429(mock_request):
    """Test that _request retries when encountering HTTP 429 status code."""
    resp_429 = MagicMock(spec=httpx.Response)
    resp_429.status_code = 429
    resp_429.raise_for_status.side_effect = httpx.HTTPStatusError(
        "429", request=MagicMock(), response=resp_429
    )

    resp_200 = MagicMock(spec=httpx.Response)
    resp_200.status_code = 200

    mock_request.side_effect = [resp_429, resp_200]

    result = await _request("GET", "/api/issues")
    assert result == resp_200
    assert mock_request.call_count == 2
