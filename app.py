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

connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

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
