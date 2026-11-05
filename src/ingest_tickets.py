
import logging
from pathlib import Path

import pandas as pd

from database import get_connection

logging.getLogger("snowflake.connector").setLevel(logging.WARNING)

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "cleaned_tickets.csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s"
)


def upload_tickets(df, connection):
    """Insert only new support tickets into Snowflake."""

    columns = [
        "ticket_id", "customer", "product",
        "description", "priority", "status", "created_at"
    ]

    # Basic validation before uploading
    if list(df.columns) != columns:
        raise ValueError("Unexpected CSV columns")

    if df["ticket_id"].isna().any():
        raise ValueError("Missing ticket IDs")

    if df["ticket_id"].duplicated().any():
        raise ValueError("Duplicate ticket IDs in CSV")

    df = df.copy()
    df["ticket_id"] = pd.to_numeric(
        df["ticket_id"], errors="raise"
    ).astype(int)

    df["created_at"] = pd.to_datetime(
        df["created_at"], errors="raise"
    ).dt.date

    records = list(
        df[columns].itertuples(index=False, name=None)
    )

    cursor = connection.cursor()

    try:
        # Create temporary staging table
        cursor.execute("""
            CREATE OR REPLACE TEMPORARY TABLE TICKET_STAGING
            LIKE SUPPORT_INTELLIGENCE.RAW.SUPPORT_TICKETS
        """)

        # Start transaction after DDL
        cursor.execute("BEGIN")

        # Upload CSV records to staging table
        cursor.executemany("""
            INSERT INTO TICKET_STAGING (
                TICKET_ID, CUSTOMER, PRODUCT,
                DESCRIPTION, PRIORITY, STATUS, CREATED_AT
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, records)

        # Insert only tickets that don't already exist
        cursor.execute("""
            MERGE INTO
                SUPPORT_INTELLIGENCE.RAW.SUPPORT_TICKETS target
            USING TICKET_STAGING source
            ON target.TICKET_ID = source.TICKET_ID
            WHEN NOT MATCHED THEN
                INSERT (
                    TICKET_ID, CUSTOMER, PRODUCT,
                    DESCRIPTION, PRIORITY, STATUS, CREATED_AT
                )
                VALUES (
                    source.TICKET_ID, source.CUSTOMER,
                    source.PRODUCT, source.DESCRIPTION,
                    source.PRIORITY, source.STATUS,
                    source.CREATED_AT
                )
        """)

        result = cursor.fetchone()
        inserted = int(result[0])

        connection.commit()
        print(f"New tickets inserted: {inserted}")

    except Exception:
        connection.rollback()
        logging.exception("Snowflake ingestion failed")
        raise

    finally:
        cursor.close()



def main():
    print("Starting Snowflake ingestion...")

    # Read the cleaned CSV
    df = pd.read_csv(CSV_PATH)

    print(f"Loaded {len(df)} rows from CSV")

    # Connect to Snowflake
    connection = get_connection()

    try:
        cursor = connection.cursor()

        try:
            # Check existing ticket count
            cursor.execute("""
                SELECT COUNT(*)
                FROM SUPPORT_INTELLIGENCE.RAW.SUPPORT_TICKETS
            """)

            before = cursor.fetchone()[0]

            print(f"Tickets currently in Snowflake: {before}")
            upload_tickets(df, connection)

        finally:
            cursor.close()

    finally:
        connection.close()


if __name__ == "__main__":
    main()
