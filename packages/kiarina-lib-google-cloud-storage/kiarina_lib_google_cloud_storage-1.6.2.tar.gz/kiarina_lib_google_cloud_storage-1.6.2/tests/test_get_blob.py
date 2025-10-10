from unittest.mock import MagicMock, patch

import pytest

from kiarina.lib.google.cloud_storage import get_blob, settings_manager


def test_get_blob_with_blob_name():
    """Test get_blob with explicit blob_name parameter."""
    settings_manager.user_config = {
        "default": {
            "bucket_name": "test-bucket",
        }
    }

    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.name = "data/file.json"
    mock_bucket.blob.return_value = mock_blob

    with patch(
        "kiarina.lib.google.cloud_storage._get_blob.get_bucket",
        return_value=mock_bucket,
    ):
        blob = get_blob(blob_name="data/file.json")
        assert blob.name == "data/file.json"
        mock_bucket.blob.assert_called_once_with("data/file.json")


def test_get_blob_with_pattern_and_placeholders():
    """Test get_blob with blob_name_pattern and placeholders."""
    settings_manager.user_config = {
        "default": {
            "bucket_name": "test-bucket",
            "blob_name_pattern": "users/{user_id}/files/{basename}",
        }
    }

    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.name = "users/123/files/profile.json"
    mock_bucket.blob.return_value = mock_blob

    with patch(
        "kiarina.lib.google.cloud_storage._get_blob.get_bucket",
        return_value=mock_bucket,
    ):
        blob = get_blob(placeholders={"user_id": "123", "basename": "profile.json"})
        assert blob.name == "users/123/files/profile.json"
        mock_bucket.blob.assert_called_once_with("users/123/files/profile.json")


def test_get_blob_with_fixed_pattern():
    """Test get_blob with fixed blob_name_pattern (no placeholders)."""
    settings_manager.user_config = {
        "default": {
            "bucket_name": "test-bucket",
            "blob_name_pattern": "data/fixed.json",
        }
    }

    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.name = "data/fixed.json"
    mock_bucket.blob.return_value = mock_blob

    with patch(
        "kiarina.lib.google.cloud_storage._get_blob.get_bucket",
        return_value=mock_bucket,
    ):
        blob = get_blob()
        assert blob.name == "data/fixed.json"
        mock_bucket.blob.assert_called_once_with("data/fixed.json")


def test_get_blob_priority_blob_name_over_placeholders():
    """Test that blob_name takes precedence over placeholders."""
    settings_manager.user_config = {
        "default": {
            "bucket_name": "test-bucket",
            "blob_name_pattern": "users/{user_id}/files/{basename}",
        }
    }

    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.name = "direct/path.json"
    mock_bucket.blob.return_value = mock_blob

    with patch(
        "kiarina.lib.google.cloud_storage._get_blob.get_bucket",
        return_value=mock_bucket,
    ):
        blob = get_blob(
            blob_name="direct/path.json",
            placeholders={"user_id": "123", "basename": "ignored.json"},
        )
        assert blob.name == "direct/path.json"
        mock_bucket.blob.assert_called_once_with("direct/path.json")


def test_get_blob_with_missing_placeholder():
    """Test error when placeholder is missing."""
    settings_manager.user_config = {
        "default": {
            "bucket_name": "test-bucket",
            "blob_name_pattern": "users/{user_id}/files/{basename}",
        }
    }

    with pytest.raises(
        ValueError,
        match=r"Missing placeholder 'basename' in blob_name_pattern: "
        r"users/\{user_id\}/files/\{basename\}",
    ):
        get_blob(placeholders={"user_id": "123"})


def test_get_blob_without_blob_name_and_pattern():
    """Test error when neither blob_name nor blob_name_pattern is provided."""
    settings_manager.user_config = {
        "default": {
            "bucket_name": "test-bucket",
        }
    }

    with pytest.raises(
        ValueError,
        match="blob_name is not provided, placeholders are not provided, "
        "and blob_name_pattern is not set in settings",
    ):
        get_blob()


def test_get_blob_with_placeholders_but_no_pattern():
    """Test error when placeholders are provided but pattern is not set."""
    settings_manager.user_config = {
        "default": {
            "bucket_name": "test-bucket",
        }
    }

    with pytest.raises(
        ValueError,
        match="placeholders provided but blob_name_pattern is not set in settings",
    ):
        get_blob(placeholders={"user_id": "123"})


def test_get_blob_with_custom_config_key():
    """Test get_blob with custom config_key."""
    settings_manager.user_config = {
        "custom": {
            "bucket_name": "custom-bucket",
            "blob_name_pattern": "custom/path.json",
        }
    }

    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.name = "custom/path.json"
    mock_bucket.blob.return_value = mock_blob

    with patch(
        "kiarina.lib.google.cloud_storage._get_blob.get_bucket",
        return_value=mock_bucket,
    ) as mock_get_bucket:
        blob = get_blob(config_key="custom")
        assert blob.name == "custom/path.json"
        mock_get_bucket.assert_called_once_with("custom", auth_config_key=None)


def test_get_blob_with_auth_config_key():
    """Test get_blob with custom auth_config_key."""
    settings_manager.user_config = {
        "default": {
            "bucket_name": "test-bucket",
            "blob_name_pattern": "data.json",
        }
    }

    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.name = "data.json"
    mock_bucket.blob.return_value = mock_blob

    with patch(
        "kiarina.lib.google.cloud_storage._get_blob.get_bucket",
        return_value=mock_bucket,
    ) as mock_get_bucket:
        blob = get_blob(auth_config_key="custom_auth")
        assert blob.name == "data.json"
        mock_get_bucket.assert_called_once_with(None, auth_config_key="custom_auth")


def test_get_blob_with_complex_pattern():
    """Test get_blob with complex multi-level pattern."""
    settings_manager.user_config = {
        "default": {
            "bucket_name": "test-bucket",
            "blob_name_pattern": "web/{user_id}/{agent_id}/files/{basename}",
        }
    }

    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.name = "web/user123/agent456/files/document.pdf"
    mock_bucket.blob.return_value = mock_blob

    with patch(
        "kiarina.lib.google.cloud_storage._get_blob.get_bucket",
        return_value=mock_bucket,
    ):
        blob = get_blob(
            placeholders={
                "user_id": "user123",
                "agent_id": "agent456",
                "basename": "document.pdf",
            }
        )
        assert blob.name == "web/user123/agent456/files/document.pdf"
        mock_bucket.blob.assert_called_once_with(
            "web/user123/agent456/files/document.pdf"
        )
