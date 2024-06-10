import os

import psycopg2

url = os.environ.get("DB_URL")

database = psycopg2.connect(url)
