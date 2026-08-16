from app import get_db_connection


def check_database():
    connection = get_db_connection()

    try:
        rows = connection.execute(
            """
                SELECT id, username, password
                FROM pass
                ORDER BY id
            """
        ).fetchall()

        if not rows:
            print("No events found in the database.")
            return []

        print("Events in the database:")
        for row in rows:
            print(f"id={row['id']} | username={row['username']} | password={row['password']}")

        return rows
    finally:
        connection.close()


if __name__ == "__main__":
    check_database()