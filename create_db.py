import mysql.connector
from mysql.connector import Error

# connection = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     passwd="root@123"
# )
#
# print(connection.is_connected())
# cursor = connection.cursor()
#
# cursor.execute("CREATE DATABASE users")
# def connect():
#     try:
#         connection = mysql.connector.connect(host="localhost",
#                                              database="SEE_INV_withflask",
#                                              user="root",
#                                              password="root@123")
#         if connection.is_connected():
#             db_Info = connection.get_server_info()
#             print("Connected to MySQL Server version ", db_Info)
#             cursor = connection.cursor(buffered=True)
#             cursor.execute("select database();")
#             record = cursor.fetchone()
#             print("You're connected to database: ", record)
#             return cursor, connection
#     except Error as e:
#         print("Error while connecting to MySQL", e)




