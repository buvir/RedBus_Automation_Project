import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
connection =psycopg2.connect(
    host='localhost',
    database='hi',
    user='postgres',
    password='sample12'
)
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor=connection.cursor()
cursor.execute("select * from tablehi")
version= cursor.fetchall()
print(version)
connection.close()