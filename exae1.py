import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

connection = psycopg2.connect(
    host="localhost",
    port="5432",
    database="sample",
    user="postgres",
    password="sampl12"
)

connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

writer = connection.cursor()

#writer.execute("create database hello")

writer.execute("create table emp_data (emp_id int, name varchar(20), dept varchar(20), salary int)")

writer.close()
connection.close()