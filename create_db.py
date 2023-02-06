import mysql.connector
from mysql.connector import Error

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="toor"
)

print(connection.is_connected())
cursor = connection.cursor()

cursor.execute("CREATE DATABASE users")

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        database="users",
        password="toor")
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor(buffered=True)
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

except Error as e:
    print("Error while connecting to MySQL", e)



