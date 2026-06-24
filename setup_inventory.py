import sqlite3


def setup_inventory(db_path: str = "inventory.db") -> None:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS inventory")

    cursor.execute("""
        CREATE TABLE inventory (
            item TEXT PRIMARY KEY,
            stock INTEGER
        )
    """)

    cursor.executemany(
        "INSERT INTO inventory VALUES (?, ?)",
        [
            ("WidgetA", 15),
            ("WidgetB", 10),
            ("GadgetX", 5),
            ("FakeItem", 0),
        ],
    )

    conn.commit()
    conn.close()

    print(f"Inventory database created at {db_path}")


if __name__ == "__main__":
    setup_inventory()