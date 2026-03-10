import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2

url = os.getenv('DATABASE_URL').replace('postgresql+asyncpg://', 'postgresql://', 1)
conn = psycopg2.connect(url)
cur = conn.cursor()
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
for row in cur.fetchall():
    print(row[0])
conn.close()
