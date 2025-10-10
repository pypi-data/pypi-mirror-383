import os

import pytest


def require_env_vars():
    return pytest.mark.xfail(
        "KIARINA_LIB_CLOUDFLARE_AUTH_TEST_ACCOUNT_ID" not in os.environ
        or "KIARINA_LIB_CLOUDFLARE_AUTH_TEST_API_TOKEN" not in os.environ
        or "KIARINA_LIB_CLOUDFLARE_D1_TEST_DATABASE_ID" not in os.environ,
        reason="Cloudflare D1 test settings not set",
    )
