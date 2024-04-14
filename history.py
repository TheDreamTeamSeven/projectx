from azure_connection.utils import AzureCredential
import bcrypt
import pyodbc
import time


# Database connection setup
credential = AzureCredential()

server_name = credential.get_secret_value('sql-server-name-gr-7')
server_port = credential.get_secret_value('sql-server-port')
server = f'{server_name},{server_port}'

database_name_history = credential.get_secret_value('sql-database-name-history')
username_history = credential.get_secret_value('sql-database-user-name-history')
password_history = credential.get_secret_value('sql-database-user-password-history')

driver = credential.get_secret_value('sql-server-driver')

connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database_name_history};UID={username_history};PWD={password_history};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

# USER HANDLING

def hash_password(password):
    # Hash a password for storing.
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def check_password(hashed_password, user_password):
    # Ensure both hashed_password and user_password are byte strings
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    if isinstance(user_password, str):
        user_password = user_password.encode('utf-8')
    
    return bcrypt.checkpw(user_password, hashed_password)

def register_user(username, password):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    try:
        # Check if the username already exists
        cursor.execute("SELECT Username FROM dbo.users WHERE Username = ?", username)
        if cursor.fetchone():
            return "Username already exists"

        # Hash the password
        hashed_password = hash_password(password)
        print('REGISTER')
        print(username, password, len(hashed_password))
        print(hashed_password)
        # Insert new user
        cursor.execute("INSERT INTO dbo.users (Username, PasswordHash) VALUES (?, ?)", username, hashed_password)
        print('TEST')
        conn.commit()
        return True
    except Exception as e:
        return f"REGISTER ERROR occurred: {e}"
        return False
    finally:
        cursor.close()
        conn.close()

def login_user(username, password):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT PasswordHash FROM dbo.users WHERE Username = ?", username)
        user_data = cursor.fetchone()
        if user_data:
            password_hash = user_data[0]
            # Verify the password
            if check_password(password_hash, password):
                return True
            else:
                return False
        else:
            return False
    except pyodbc.Error as e:
        return f"LOGIN ERROR occurred: {e}"
    finally:
        cursor.close()
        conn.close()


# PROMPT HANDLING

def insert_history_prompt(prompt, sql, user, success, tab_name):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    try:
        # Prepare the insert statement
        cursor.execute("""
            INSERT INTO dbo.historyPrompts (Prompt, Sql, Timestamp, [User], Success, TabName)
            VALUES (?, ?, GETDATE(), ?, ?, ?)
        """, (prompt, sql, user, success, tab_name))
        conn.commit()
        return "Insert successful"
    except pyodbc.Error as e:
        return f"Error inserting data: {e}"
    finally:
        cursor.close()
        conn.close()

def get_history_prompts(user):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Id, Prompt, Sql, Timestamp, [User], Success, TabName FROM dbo.historyPrompts WHERE [User] = ?", user)
        rows = cursor.fetchall()
        return rows  # Return as list of tuples
    except pyodbc.Error as e:
        return f"Error fetching data: {e}"
    finally:
        cursor.close()
        conn.close()