
from database import get_agent_connection


def run_readonly_query(sql):
    """Execute one predefined read-only query."""

    connection = get_agent_connection()

    try:
        cursor = connection.cursor()

        try:
            cursor.execute(sql)

            columns = [
                column[0].lower()
                for column in cursor.description
            ]

            rows = cursor.fetchall()

            return [
                dict(zip(columns, row))
                for row in rows
            ]

        finally:
            cursor.close()

    finally:
        connection.close()


def get_ticket_counts_by_product():
    """Count support tickets for each product."""

    sql = """
        SELECT
            PRODUCT,
            COUNT(*) AS TICKET_COUNT
        FROM SUPPORT_INTELLIGENCE.RAW.SUPPORT_TICKETS
        GROUP BY PRODUCT
        ORDER BY TICKET_COUNT DESC
    """

    return run_readonly_query(sql)


def get_high_priority_tickets():
    """Find unresolved high-priority tickets."""

    sql = """
        SELECT
            TICKET_ID,
            PRODUCT,
            PRIORITY,
            STATUS,
            CREATED_AT
        FROM SUPPORT_INTELLIGENCE.RAW.SUPPORT_TICKETS
        WHERE UPPER(PRIORITY) = 'HIGH'
          AND UPPER(STATUS) NOT IN ('CLOSED', 'RESOLVED')
        ORDER BY CREATED_AT DESC
        LIMIT 20
    """

    return run_readonly_query(sql)


def get_ai_category_summary():
    """Count tickets in each AI classification category."""

    sql = """
        SELECT
            CATEGORY,
            COUNT(*) AS TICKET_COUNT,
            ROUND(AVG(CONFIDENCE), 2) AS AVG_CONFIDENCE
        FROM SUPPORT_INTELLIGENCE.ANALYTICS.AI_CLASSIFICATIONS
        GROUP BY CATEGORY
        ORDER BY TICKET_COUNT DESC
    """

    return run_readonly_query(sql)



def get_dashboard_metrics():
    """Retrieve live support ticket dashboard metrics."""

    sql = """
        SELECT
            (SELECT COUNT(*)
             FROM SUPPORT_INTELLIGENCE.RAW.SUPPORT_TICKETS)
                AS TOTAL_TICKETS,

            (SELECT COUNT(*)
             FROM SUPPORT_INTELLIGENCE.RAW.SUPPORT_TICKETS
             WHERE UPPER(STATUS) NOT IN ('CLOSED', 'RESOLVED'))
                AS OPEN_TICKETS,

            (SELECT COUNT(*)
             FROM SUPPORT_INTELLIGENCE.ANALYTICS.AI_CLASSIFICATIONS)
                AS AI_CLASSIFIED
    """

    results = run_readonly_query(sql)
    return results[0]



def get_ticket_breakdown():
    """Retrieve ticket counts by product, priority and status."""

    sql = """
        SELECT
            PRODUCT,
            PRIORITY,
            STATUS,
            COUNT(*) AS TICKET_COUNT
        FROM SUPPORT_INTELLIGENCE.RAW.SUPPORT_TICKETS
        GROUP BY PRODUCT, PRIORITY, STATUS
        ORDER BY PRODUCT, PRIORITY, STATUS
    """

    return run_readonly_query(sql)


def get_ticket_monthly_trends():
    """Get monthly ticket counts by product and priority."""

    sql = """
        SELECT
            DATE_TRUNC('MONTH', CREATED_AT)::DATE AS MONTH,
            PRODUCT,
            PRIORITY,
            STATUS,
            COUNT(*) AS TICKET_COUNT
        FROM SUPPORT_INTELLIGENCE.RAW.SUPPORT_TICKETS
        WHERE CREATED_AT IS NOT NULL
        GROUP BY 1, 2, 3, 4
        ORDER BY MONTH
    """

    return run_readonly_query(sql)


if __name__ == "__main__":
    print("Testing Snowflake agent tools...\n")

    print("1. Tickets by product:")
    for row in get_ticket_counts_by_product():
        print(row)

    print("\n2. High-priority unresolved tickets:")
    for row in get_high_priority_tickets():
        print(row)

    print("\n3. AI classification summary:")
    for row in get_ai_category_summary():
        print(row)
