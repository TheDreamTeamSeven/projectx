from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, send, emit
import pyodbc

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Database connection setup
server = 'hackaton-gr7-sqlserverm7d1m.database.windows.net,1433'
database = 'hackaton-gr7-sqldb'
username = 'hacksqlusr012993'
password = 'hacksqlusrP@ssw00rd'
driver = '{ODBC Driver 18 for SQL Server}'

fetch_tables_sql = "SELECT table_name FROM INFORMATION_SCHEMA.TABLES WHERE table_type = 'BASE TABLE';"
fetch_columns_table_sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '%s' ORDER BY ORDINAL_POSITION;"

connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

tables_with_columns = {}

# Establish connection
try:
    cnxn = pyodbc.connect(connection_string)
    cursor = cnxn.cursor()
    print("Connection successful")
except Exception as e:
    print("Error connecting to SQL Server:", e)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init-db-structure')
def init_db_structure():
    try:
        print('POBIERANIE')
        fetch_tables_and_initialize()
        populate_columns_for_tables()
        print('SUCCESS')
        return jsonify({'success': True, 'data': tables_with_columns}), 200
    except Exception as e:
        print('ERROR')
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
    data = request.get_json()
    nl_query = data.get('query')
    if not nl_query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        # Assuming get_sql_query_in_json is a function from chat_integration.py that handles the processing
        from chat_integration import get_sql_query_in_json
        # Pass the global table structure along with the query
        result = get_sql_query_in_json(nl_query, tables_with_columns)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('message')
def handle_message(data):
    print('Received message: ' + data['data'] + ' on tab ' + str(data['tabId']))
    if data['data'].startswith('/query'):
        # Handle command to fetch data from the database
        query_data = fetch_data_from_db()
        response_text = format_data_as_string(query_data)
        emit('response', {'tabId': data['tabId'], 'data': response_text})
    else:
        emit('response', {'tabId': data['tabId'], 'data': 'User: ' + data['data']})

def fetch_tables_and_initialize():
    global tables_with_columns
    cursor.execute(fetch_tables_sql)
    tables = [row[0] for row in cursor.fetchall()]
    tables_with_columns = {table: [] for table in tables}
    print(tables)

def populate_columns_for_tables():
    global tables_with_columns
    for table in tables_with_columns.keys():
        query = fetch_columns_table_sql % table
        cursor.execute(query)
        columns = [row[0] for row in cursor.fetchall()]
        tables_with_columns[table] = columns
    print(tables_with_columns)

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
    socketio.run(app)
