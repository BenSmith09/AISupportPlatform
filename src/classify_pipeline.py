
import logging

from database import get_connection
from classify_ticket import classify_ticket, MODEL

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s | %(message)s"
)

logging.getLogger("snowflake.connector").setLevel(
    logging.WARNING
)

BATCH_SIZE = 3
MAX_TICKETS_PER_RUN = 3


def get_unclassified_tickets(connection):
    """Find tickets without AI classifications."""

    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                t.TICKET_ID,
                t.DESCRIPTION
            FROM SUPPORT_INTELLIGENCE.RAW.SUPPORT_TICKETS t
            WHERE NOT EXISTS (
                SELECT 1
                FROM SUPPORT_INTELLIGENCE.ANALYTICS.AI_CLASSIFICATIONS a
                WHERE a.TICKET_ID = t.TICKET_ID
            )
            ORDER BY t.TICKET_ID
            LIMIT %s
        """, (BATCH_SIZE,))

        return cursor.fetchall()

    finally:
        cursor.close()


def save_classification(connection, ticket_id, result):
    """Save a classification if it doesn't already exist."""

    cursor = connection.cursor()

    try:
        cursor.execute("""
            MERGE INTO
                SUPPORT_INTELLIGENCE.ANALYTICS.AI_CLASSIFICATIONS
                AS target

            USING (
                SELECT
                    %s AS TICKET_ID,
                    %s AS CATEGORY,
                    %s AS LIKELY_CAUSE,
                    %s AS RECOMMENDED_ACTION,
                    %s AS CONFIDENCE,
                    %s AS MODEL_USED
            ) AS source

            ON target.TICKET_ID = source.TICKET_ID

            WHEN NOT MATCHED THEN
                INSERT (
                    TICKET_ID,
                    CATEGORY,
                    LIKELY_CAUSE,
                    RECOMMENDED_ACTION,
                    CONFIDENCE,
                    MODEL_USED
                )
                VALUES (
                    source.TICKET_ID,
                    source.CATEGORY,
                    source.LIKELY_CAUSE,
                    source.RECOMMENDED_ACTION,
                    source.CONFIDENCE,
                    source.MODEL_USED
                )
        """, (
            ticket_id,
            result["category"],
            result["likely_cause"],
            result["recommended_action"],
            result["confidence"],
            MODEL
        ))

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()


def main():
    print("Starting AI classification pipeline...")

    connection = get_connection()

    try:
        tickets = get_unclassified_tickets(connection)
        tickets = tickets[:MAX_TICKETS_PER_RUN]

        if not tickets:
            print("No unclassified tickets found.")
            return

        print(f"Found {len(tickets)} tickets to classify.")

        for ticket_id, description in tickets:
            print(f"\nClassifying ticket {ticket_id}...")

            try:
                result = classify_ticket(description)

                save_classification(
                    connection,
                    ticket_id,
                    result
                )

                print(
                    f"Saved ticket {ticket_id}: "
                    f"{result['category']}"
                )

            except Exception as error:
                print(
                    f"Failed to classify ticket {ticket_id}: "
                    f"{error}"
                )

        print("\nClassification batch complete.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
