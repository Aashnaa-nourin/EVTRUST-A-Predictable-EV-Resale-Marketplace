import sqlite3
import pandas as pd

conn = sqlite3.connect('db.sqlite3')
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'django_%' AND name NOT LIKE 'auth_%'", conn)['name'].tolist()
out = ''
for table in tables:
    schema = pd.read_sql_query(f'PRAGMA table_info({table})', conn)
    count = pd.read_sql_query(f'SELECT COUNT(*) as count FROM {table}', conn).iloc[0]['count']
    out += f'Table: {table} (Rows: {count})\n'
    out += schema[['name', 'type']].to_string(index=False) + '\n\n'
    if count > 0:
        data = pd.read_sql_query(f'SELECT * FROM {table} LIMIT 2', conn)
        out += "Sample Rows:\n"
        out += data.to_string(index=False) + '\n\n'
print(out)
