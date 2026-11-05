
from database import get_connection


def main():
    print("Connecting to Snowflake...", flush=True)

    connection = None

    try:
        connection = get_connection()

        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT
                    CURRENT_DATABASE(),
                    CURRENT_SCHEMA(),
                    CURRENT_WAREHOUSE()
            """)

            result = cursor.fetchone()

            print("Connection successful!")
            print(f"Database: {result[0]}")
            print(f"Schema: {result[1]}")
            print(f"Warehouse: {result[2]}")

        finally:
            cursor.close()

    except Exception as error:
        print(f"Connection failed: {error}")
        raise

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    main()
