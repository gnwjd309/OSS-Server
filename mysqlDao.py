import mysql.connector
import sys

try:
    chat_db = mysql.connector.connect(host="localhost", user="root", passwd="0000", database="user",charset='utf8')
except:
    sys.exit("Error connecting to the database. Please check your inputs.")

db_cursor = chat_db.cursor()

# Users Table
try:
    db_cursor.execute("CREATE TABLE users (name VARCHAR(255) NOT NULL, id VARCHAR(255) NOT NULL UNIQUE, pw VARCHAR(32) NOT NULL, registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)default character set utf8 collate utf8_general_ci")
    print("users table created successfully.")
except mysql.connector.DatabaseError:
    sys.exit("Error creating the table. Please check if it already exists.")

describe_query = "DESCRIBE users"
db_cursor.execute(describe_query)
records = db_cursor.fetchall()
print(records)