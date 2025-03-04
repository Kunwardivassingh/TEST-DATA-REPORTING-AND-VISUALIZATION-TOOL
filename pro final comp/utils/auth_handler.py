from datetime import datetime
import bcrypt
import mysql.connector
import numpy as np
import pandas as pd
from utils.db import get_db_connection
import uuid
# Register a new user
def register_user(username, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
    if cursor.fetchone():
        return False, "Username or email already exists."
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                   (username, email, hashed_password))
    conn.commit()
    cursor.close()
    conn.close()
    return True, "User registered successfully."

# Validate user login
def validate_login(email, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
        return True, user["id"]
    return False, "Invalid email or password."

# Reset user password
def reset_password(email, new_password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (hashed_password, email))
    conn.commit()
    cursor.close()
    conn.close()
    return True, "Password reset successfully."

# utils/auth_handler.py
from utils.db import get_db_connection
import pandas as pd

def save_dataset_to_db(df):
    """
    Save DataFrame to database, replacing any previous dataset completely
    """
    try:
        # Clean up the DataFrame columns
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        df.columns = df.columns.str.replace('[^a-zA-Z0-9_]', '', regex=True)
        
        # Rename 'id' column if it exists to prevent conflict
        if 'id' in df.columns:
            df = df.rename(columns={'id': 'record_id'})

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Start transaction
            conn.start_transaction()

            # Drop the existing table if it exists
            cursor.execute("DROP TABLE IF EXISTS datasets")
            
            # Define dtype mapping
            dtype_mapping = {
                'int64': 'BIGINT',
                'int32': 'INT',
                'float64': 'DOUBLE',
                'float32': 'FLOAT',
                'object': 'VARCHAR(255)',  # Use VARCHAR instead of TEXT
                'datetime64[ns]': 'DATETIME',
                'bool': 'BOOLEAN',
                'category': 'VARCHAR(255)',
                'string': 'VARCHAR(255)'  # Use VARCHAR instead of TEXT
            }

            # Create the new table with upload timestamp
            column_definitions = []
            for column in df.columns:
                dtype = str(df[column].dtype)
                mysql_type = dtype_mapping.get(dtype, 'TEXT')  # Default to TEXT if not found
                clean_column = column.strip().lower().replace(' ', '_')
                clean_column = ''.join(e for e in clean_column if e.isalnum() or e == '_')
                column_definitions.append(f"`{clean_column}` {mysql_type}")

            # Create the SQL statement for table creation
            create_table_query = f"""
            CREATE TABLE datasets (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `upload_timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                {', '.join(column_definitions)}
            );
            """
            cursor.execute(create_table_query)

            # Prepare insert query
            columns = ['upload_timestamp'] + list(df.columns)
            columns_str = ", ".join([f"`{col}`" for col in columns])
            placeholders = ", ".join(["%s"] * len(columns))
            insert_query = f"INSERT INTO datasets ({columns_str}) VALUES ({placeholders})"

            # Prepare data for insert with timestamp
            current_time = datetime.now()
            data_to_insert = []
            for _, row in df.iterrows():
                row_data = [current_time]  # Add timestamp
                for col in df.columns:
                    value = row[col]
                    # Handle different data types
                    if pd.isna(value):
                        value = None
                    elif isinstance(value, pd.Timestamp):
                        value = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(value, bool):
                        value = int(value)
                    elif isinstance(value, (np.int64, np.int32)):
                        value = int(value)
                    elif isinstance(value, (np.float64, np.float32)):
                        value = float(value)
                    # Append the value to the row data
                    row_data.append(value)
                data_to_insert.append(tuple(row_data))

            # Insert the data
            cursor.executemany(insert_query, data_to_insert)
            
            # Commit the transaction
            conn.commit()

            return True, f"Dataset successfully replaced. {len(df)} rows inserted."

        except mysql.connector.Error as err:
            conn.rollback()
            return False, f"Database Error: {str(err)}"
        except Exception as e:
            conn.rollback()
            return False, f"Error processing dataset: {str(e)}"
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        return False, f"Error processing DataFrame: {str(e)}"
    
def fetch_dataset_from_db(table_name='datasets', conditions=None, columns=None):
    """
    Fetch dataset from database with flexible querying options
    
    Args:
        table_name (str): Name of the table to query
        conditions (dict): Dictionary of conditions {column: value}
        columns (list): List of columns to fetch. If None, fetches all columns
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get all column names if not specified
        if not columns:
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = [column['Field'] for column in cursor.fetchall()]
            
        # Build the SELECT query
        columns_str = ", ".join([f"`{col}`" for col in columns])
        query = f"SELECT {columns_str} FROM {table_name}"
        
        # Add WHERE clause if conditions are provided
        params = []
        if conditions:
            where_clauses = []
            for column, value in conditions.items():
                where_clauses.append(f"`{column}` = %s")
                params.append(value)
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
        
        # Execute query
        cursor.execute(query, params)
        data = cursor.fetchall()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Convert data types appropriately
        for column in df.columns:
            # Try to convert to numeric
            if df[column].dtype == 'object':
                try:
                    df[column] = pd.to_numeric(df[column], errors='ignore')
                except:
                    pass
                    
            # Convert datetime strings to datetime objects
            if df[column].dtype == 'object':
                try:
                    df[column] = pd.to_datetime(df[column], errors='ignore')
                except:
                    pass
        
        return df
    
    except mysql.connector.Error as err:
        print(f"MySQL Error: {str(err)}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return pd.DataFrame()
    finally:
        cursor.close()
        conn.close()