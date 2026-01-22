import sqlite3

db_path = "data/prices.sqlite"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()
print("tables:", tables)

cur.execute("PRAGMA table_info(prices_weekly);")
cols = cur.fetchall()
print("columns:")
for c in cols:
    print(c)

conn.close()
