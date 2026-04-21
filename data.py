import sqlite3
import pandas as pd

# Connect to your database
conn = sqlite3.connect('../users.db')

# Read the user_inputs table into a DataFrame
df = pd.read_sql_query("SELECT * FROM user_inputs", conn)

# Show the data
print(df)

conn.close()