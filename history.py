from azure_connection.utils import AzureCredential
import pyodbc


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
