# utils/db.py
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="testwave"
    )
from sqlalchemy import create_engine

# Update this with your database name
database_name = 'testwave'

# Use an empty password by removing any text between the single quotes after 'root:'
engine = create_engine(f'mysql+pymysql://root:@localhost/{database_name}')

