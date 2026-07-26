from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_firestore_client(mocker):
    """
    Mock fixture to isolate firestore operations from network dependencies.
    """
    mock_db = MagicMock()
    mocker.patch("google.cloud.firestore.Client", return_value=mock_db)
    return mock_db
