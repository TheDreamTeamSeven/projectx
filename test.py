from chat_integration import send_completion_request
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, send, emit

from azure_connection.utils import AzureCredential

import pyodbc

credential = AzureCredential()

# Database connection setup

server_name = credential.get_secret_value('sql-server-name-gr-7')
server_port = credential.get_secret_value('sql-server-port')
server = f'{server_name},{server_port}'

database_name_hackathon = credential.get_secret_value('sql-database-name-hackathon')
username = credential.get_secret_value('sql-database-user-name-hackathon')
password = credential.get_secret_value('sql-database-user-password-hackathon')

driver = credential.get_secret_value('sql-server-driver')

# Azure Bastion configuration
bastion_host = '52.143.190.84'
bastion_username = 'azureuser'
bastion_password = 'VM-Password1'

# Connection string template for SQL Server through Azure Bastion
connection_string_template = (
    f'DRIVER={driver};'
    f'SERVER={server};'
    f'DATABASE={database_name_hackathon};'
    f'UID={username};'
    f'PWD={password};'
    f'Encrypt=yes;'
    f'TrustServerCertificate=no;'
    f'Connection Timeout=30;'
    f'Host={bastion_host};'
    f'BastionUid={bastion_username};'
    f'BastionPwd={bastion_password};'
)

tables_with_columns = {}

# Establish connection
try:
    cnxn = pyodbc.connect(connection_string_template)
    cursor = cnxn.cursor()
    print("Connection successful")
except Exception as e:
    print("Error connecting to SQL Server:", e)

# Your existing Flask routes and socketio event handlers...
