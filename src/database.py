
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


def get_agent_connection():
    """Create a read-only Snowflake connection for the AI agent."""

    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")

    if not account or not user:
        raise ValueError(
            "Missing Snowflake account or username"
        )

    return snowflake.connector.connect(
        account=account,
        user=user,
        authenticator="OAUTH_AUTHORIZATION_CODE",
        warehouse="SUPPORT_WH",
        database="SUPPORT_INTELLIGENCE",
        schema="ANALYTICS",
        role="SUPPORT_AGENT_READONLY",
        login_timeout=60,
        session_parameters={
            "QUERY_TAG": "ai_support_readonly_agent",
            "STATEMENT_TIMEOUT_IN_SECONDS": 30
        }
    )

