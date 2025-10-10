from pydantic_settings import BaseSettings
from pydantic_settings_manager import SettingsManager


class GoogleCloudStorageSettings(BaseSettings):
    bucket_name: str | None = None

    blob_name_pattern: str | None = None
    """
    Blob name pattern with placeholders.
    
    Examples:
        - "data.json" (fixed name)
        - "files/{basename}" (single placeholder)
        - "web/{user_id}/{agent_id}/files/{basename}" (multiple placeholders)
    """


settings_manager = SettingsManager(GoogleCloudStorageSettings, multi=True)
