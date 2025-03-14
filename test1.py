import psycopg2

connection = psycopg2.connect(
    host="localhost",
    database="companyx",
    user="postgres",
    password="sample12"
)

cursor = connection.cursor()
cursor.execute("SELECT version()")
version = cursor.fetchone()
print("You are connected to - ", version)
connection.close()