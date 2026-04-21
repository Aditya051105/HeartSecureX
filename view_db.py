import sqlite3
import pandas as pd

conn = sqlite3.connect('users.db')
df = pd.read_sql_query("SELECT * FROM user_inputs", conn)
print(df)
conn.close()