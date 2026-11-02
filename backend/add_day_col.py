import sqlite3

conn = sqlite3.connect('db.sqlite3')
try:
    conn.execute("ALTER TABLE gigs_giglineup ADD COLUMN day varchar(60) NOT NULL DEFAULT ''")
    conn.commit()
    print("Column 'day' added successfully to gigs_giglineup")
except Exception as e:
    print(f"Error or already exists: {e}")
conn.close()
