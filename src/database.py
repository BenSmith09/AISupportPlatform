
import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Connect to Snowflake using browser-based OAuth."""

    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")

    if not account or not user:
        raise ValueError(
            "Missing SNOWFLAKE_ACCOUNT or SNOWFLAKE_USER"
        )

    return snowflake.connector.connect(
        account=account,
        user=user,
        authenticator="OAUTH_AUTHORIZATION_CODE",
        warehouse=os.getenv(
            "SNOWFLAKE_WAREHOUSE", "SUPPORT_WH"
        ),
        database=os.getenv(
            "SNOWFLAKE_DATABASE", "SUPPORT_INTELLIGENCE"
        ),
        schema=os.getenv(
            "SNOWFLAKE_SCHEMA", "RAW"
        ),
        role=os.getenv(
            "SNOWFLAKE_ROLE", "ACCOUNTADMIN"
        ),
        login_timeout=60,
        session_parameters={
            "QUERY_TAG": "ai_support_platform"
        }
    )
