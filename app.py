from chat_integration import send_completion_request
from history import register_user, login_user, insert_history_prompt, get_last_three_history_prompts
from flask import Flask, jsonify, render_template, request, session, redirect, url_for

from flask_socketio import SocketIO, send, emit

from azure_connection.utils import AzureCredential

import pyodbc

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

credential = AzureCredential()

# Database connection setup

server_name = credential.get_secret_value('sql-server-name-gr-7')
server_port = credential.get_secret_value('sql-server-port')
server = f'{server_name},{server_port}'

database_name_hackathon = credential.get_secret_value('sql-database-name-hackathon')
username = credential.get_secret_value('sql-database-user-name-hackathon')
password = credential.get_secret_value('sql-database-user-password-hackathon')

database_name_history = credential.get_secret_value('sql-database-name-history')
username_history = credential.get_secret_value('sql-database-user-name-history')
password_history = credential.get_secret_value('sql-database-user-password-history')

driver = credential.get_secret_value('sql-server-driver')


fetch_tables_schema_sql = " SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES; "
fetch_columns_table_sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ? ORDER BY ORDINAL_POSITION;"
fetch_pk_table_sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ? AND CONSTRAINT_NAME LIKE 'PK%'"

connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database_name_hackathon};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

tables_with_columns = {}

history_prompts = []

# Establish connection
try:
    cnxn = pyodbc.connect(connection_string)
    cursor = cnxn.cursor()
    print("Connection successful")
except Exception as e:
    print("Error connecting to SQL Server: ", e)


@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/init-db-structure')
def init_db_structure():
    try:
        print('POBIERANIE')
        fetch_tables_and_initialize()
        populate_columns_for_tables()
        populate_primary_keys_for_tables()  # Add this line
        print('SUCCESS')
        return jsonify({'success': True, 'data': tables_with_columns}), 200
    except Exception as e:
        print('ERROR FETCHING DATABASE STRUCTURE')
        return jsonify({'error': str(e)}), 500

@app.route('/get-data')
def get_data():
    try:
        data = fetch_data_from_db()  # You can pass specific queries if needed
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/execute-query', methods=['POST'])
def execute_query():
    data = request.get_json()
    query_str = data['query']
    results = fetch_data_from_db(query_str)
    return jsonify(results)

@app.route('/process-query', methods=['POST'])
def process_query():
    global tables_with_columns
    global history_prompts

    data = request.get_json()
    nl_query = data.get('query')
    tab_name = data.get('tab_name', 'default_tab')  # Default tab name if not provided
    user = session.get('username', 'default_user')  # Default user if not in session

    if not nl_query:
        return jsonify({'error': 'No query provided'}), 400

    # Fetch last three history prompts
    history_prompts = get_last_three_history_prompts(user)
    print(history_prompts)

    try:
        print('TABLES')
        # print(tables_with_columns)
        result = send_completion_request(nl_query, tables_with_columns, history_prompts)
        print('SQL QUERY ')
        sql_query = result['content'].replace('\n', ' ')
        result['content'] = sql_query
        print(result['content'])
        query_data = fetch_data_from_db(result['content'])
        print('DATA LEN')
        result['query_data'] = query_data
        print(len(result['query_data']))

        success = True if query_data else False  # Assume success if query_data is not empty
        insert_result = insert_history_prompt(nl_query, sql_query, user, success, tab_name, result['total_cost'])
        print(f"Inserted into history with result: {insert_result}")
        updated_history = get_last_three_history_prompts(user)
        result['last_history'] = updated_history

        return jsonify(result)
    except Exception as e:
        print(jsonify({'error': str(e)}))
        return jsonify({'error': str(e)}), 500

@app.route('/register', methods=['GET'])
def register():
    # if request.method == 'POST':
    #     session['username'] = request.form['username']
    #     return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET'])
def login():
    # if request.method == 'POST':
    #     session['username'] = request.form['username']
    #     return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def handle_register():
    username = request.form['username']
    password = request.form['password']
    result = register_user(username, password)
    if result:
        # session['username'] = username
        return redirect(url_for('login'))
    return jsonify({'message': result})

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form['username']
    password = request.form['password']
    result = login_user(username, password)
    print('LOGIN RESULT')
    print(result)
    if result:
        session['username'] = username
        return render_template('index.html', username=session['username'])
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

def fetch_tables_and_initialize():
    global tables_with_columns
    # Ensure the SQL query is set to fetch both the TABLE_NAME and TABLE_SCHEMA
    cursor.execute(fetch_tables_schema_sql)
    # Fetch all rows and create dictionary keys as "schema.table"
    schema_table_pairs = cursor.fetchall()
    tables_with_columns = {f"{row.TABLE_SCHEMA}.{row.TABLE_NAME}": [] for row in schema_table_pairs}
    # print("Initialized tables with schema:", tables_with_columns)

def populate_columns_for_tables():
    global tables_with_columns
    for full_table_name in tables_with_columns.keys():
        schema, table = full_table_name.split('.')  # Split the full name into schema and table
        # Execute the query with parameters for schema and table
        cursor.execute(fetch_columns_table_sql, (schema, table))
        columns = [row[0] for row in cursor.fetchall()]
        tables_with_columns[full_table_name] = columns
    # print("Populated tables with columns:", tables_with_columns)

def populate_primary_keys_for_tables():
    global tables_with_columns
    for full_table_name in tables_with_columns.keys():
        schema, table = full_table_name.split('.')
        # Prepare the SQL query to fetch primary key columns
        cursor.execute(fetch_pk_table_sql, (schema, table))
        primary_keys = [row.COLUMN_NAME for row in cursor.fetchall()]

        # Update the dictionary to include both columns and primary keys
        # Ensure columns are already populated
        if full_table_name in tables_with_columns:
            tables_with_columns[full_table_name] = {
                "columns": tables_with_columns[full_table_name],
                "primary_keys": primary_keys
            }

def fetch_data_from_db(query_str='SELECT TOP 5 * FROM SalesLT.Customer;'):
    cursor.execute(query_str)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    return results
    

def format_data_as_string(data):
    # Convert the query result to a string format suitable for display
    return '\n'.join(str(row) for row in data)

if __name__ == '__main__':
    try:
        print('POBIERANIE')
        fetch_tables_and_initialize()
        populate_columns_for_tables()
        populate_primary_keys_for_tables()  # Add this line
        print(tables_with_columns)
        print('SUCCESS')
        # return jsonify({'success': True, 'data': tables_with_columns}), 200
    except Exception as e:
        print('ERROR')
        # return jsonify({'error': str(e)}), 500
    app.run(host='0.0.0.0', port=5000)
    # socketio.run(app)
