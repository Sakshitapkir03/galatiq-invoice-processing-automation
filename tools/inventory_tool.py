import sqlite3
from typing import Optional


def get_stock(item_name: str, db_path: str = "inventory.db") -> Optional[int]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT stock FROM inventory WHERE item = ?", (item_name,))
    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return row[0]