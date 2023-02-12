# import csv
# import mysql.connector
# from mysql.connector import Error
# import csv
#
#
# mydb = mysql.connector.connect(host='localhost',
#     user='root',
#     password='toor',
#     db='SEE_INV_withflask')
# cur = mydb.cursor()
#
# file = open('student.csv')
# csv_data = csv.reader(file)
#
# skipHeader = True
#
# for row in csv_data:
#     if skipHeader:
#         skipHeader = False
#         continue
#     query = "INSERT INTO student values(%s,%s,%s,%s,%s,%s)"
#     cur.execute(query,( row[0],row[1],row[2], row[3], row[4], row[5]))
#     mydb.commit()
# print("Done")