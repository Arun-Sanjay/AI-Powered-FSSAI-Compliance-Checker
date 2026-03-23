import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "fssai_compliance.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Additives table — FSSAI Schedule I approved food additives
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS additives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            e_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            function TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('approved', 'restricted', 'banned')),
            max_limit_ppm REAL,
            permitted_categories TEXT,
            notes TEXT
        )
    """)

    # Allergen keywords — maps ingredient keywords to allergen categories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS allergen_keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            allergen_category TEXT NOT NULL
        )
    """)

    # Claims rules — FSSAI thresholds for nutritional/health claims
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS claims_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim TEXT NOT NULL,
            condition_field TEXT NOT NULL,
            operator TEXT NOT NULL,
            threshold REAL NOT NULL,
            unit TEXT NOT NULL,
            regulation TEXT NOT NULL
        )
    """)

    # Mandatory label fields per FSSAI regulations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mandatory_fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field_name TEXT NOT NULL,
            json_key TEXT NOT NULL,
            fssai_reference TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_database()
