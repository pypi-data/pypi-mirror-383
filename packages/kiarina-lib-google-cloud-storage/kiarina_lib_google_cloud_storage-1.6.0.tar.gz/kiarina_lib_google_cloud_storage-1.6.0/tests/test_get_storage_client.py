from unittest.mock import MagicMock, patch

from kiarina.lib.google.cloud_storage import get_storage_client


def test_get_storage_client():
    # Mock get_credentials and storage.Client
    mock_credentials = MagicMock()
    mock_credentials.project_id = "test-project"
    mock_client = MagicMock()
    mock_client.project = "test-project"

    with (
        patch(
            "kiarina.lib.google.cloud_storage._get_storage_client.get_credentials",
            return_value=mock_credentials,
        ) as mock_get_credentials,
        patch(
            "kiarina.lib.google.cloud_storage._get_storage_client.storage.Client",
            return_value=mock_client,
        ) as mock_client_class,
    ):
        client = get_storage_client()
        assert client.project == "test-project"

        # Verify get_credentials was called with None (default)
        mock_get_credentials.assert_called_once_with(None)

        # Verify Client was called with correct credentials
        mock_client_class.assert_called_once_with(credentials=mock_credentials)


def test_get_storage_client_with_auth_config_key():
    # Mock get_credentials and storage.Client
    mock_credentials = MagicMock()
    mock_credentials.project_id = "custom-project"
    mock_client = MagicMock()
    mock_client.project = "custom-project"

    with (
        patch(
            "kiarina.lib.google.cloud_storage._get_storage_client.get_credentials",
            return_value=mock_credentials,
        ) as mock_get_credentials,
        patch(
            "kiarina.lib.google.cloud_storage._get_storage_client.storage.Client",
            return_value=mock_client,
        ) as mock_client_class,
    ):
        client = get_storage_client(auth_config_key="custom_auth")
        assert client.project == "custom-project"

        # Verify get_credentials was called with custom auth config key
        mock_get_credentials.assert_called_once_with("custom_auth")

        # Verify Client was called with correct credentials
        mock_client_class.assert_called_once_with(credentials=mock_credentials)
