#!/usr/bin/env python3
"""Migrate database to add name and updated_at columns to business_plans table"""

import sqlite3
import os

db_path = os.path.expanduser('~/.business-agent/tasks.db')

print(f"Migrating database at: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if name column exists
    cursor.execute("PRAGMA table_info(business_plans)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'name' not in columns:
        print("Adding 'name' column to business_plans table...")
        cursor.execute("ALTER TABLE business_plans ADD COLUMN name VARCHAR(255)")
        print("✅ Added 'name' column")
    else:
        print("✓ 'name' column already exists")

    if 'updated_at' not in columns:
        print("Adding 'updated_at' column to business_plans table...")
        cursor.execute("ALTER TABLE business_plans ADD COLUMN updated_at DATETIME")
        print("✅ Added 'updated_at' column")
    else:
        print("✓ 'updated_at' column already exists")

    conn.commit()
    print("\n✅ Database migration completed successfully!")

except Exception as e:
    print(f"❌ Error during migration: {e}")
    conn.rollback()
finally:
    conn.close()
