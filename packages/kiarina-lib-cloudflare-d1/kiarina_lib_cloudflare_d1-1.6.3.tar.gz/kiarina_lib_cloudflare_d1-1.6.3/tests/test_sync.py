import os
from unittest.mock import patch

from kiarina.lib.cloudflare.auth import CloudflareAuthSettings
from kiarina.lib.cloudflare.d1 import D1Settings, create_d1_client

from .conftest import require_env_vars


@require_env_vars()
def test_sync() -> None:
    auth_settings = CloudflareAuthSettings.model_validate(
        {
            "account_id": os.environ["KIARINA_LIB_CLOUDFLARE_AUTH_TEST_ACCOUNT_ID"],
            "api_token": os.environ["KIARINA_LIB_CLOUDFLARE_AUTH_TEST_API_TOKEN"],
        }
    )

    settings = D1Settings(
        database_id=os.environ["KIARINA_LIB_CLOUDFLARE_D1_TEST_DATABASE_ID"],
    )

    with (
        patch(
            "kiarina.lib.cloudflare.d1._sync.registry.settings_manager"
        ) as mock_settings_manager,
        patch(
            "kiarina.lib.cloudflare.d1._sync.registry.auth_settings_manager"
        ) as mock_auth_settings_manager,
    ):
        mock_settings_manager.get_settings.return_value = settings
        mock_auth_settings_manager.get_settings.return_value = auth_settings

        client = create_d1_client()
        result = client.query("SELECT 1")
        assert len(result.first.rows) == 1
