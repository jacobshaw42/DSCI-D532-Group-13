from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd

app = Flask(__name__)

@app.route('/')
@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/home')
def home_page():
    start_row = int(request.args.get('start_row', 0))  # Get the starting row index
    num_rows = 10  # Display 10 rows at a time
    HealthDim_query = query_button_1(start_row, num_rows)
    return render_template('home.html', HealthDim_query=HealthDim_query, num_rows=num_rows, start_row=start_row)

def query_button_1(start_row, num_rows):
    conn = sqlite3.connect('FinalProject.db')
    c = conn.cursor()
    c.execute(f"SELECT *, ROW_NUMBER() OVER(ORDER BY id) + {start_row} as row_number FROM HealthDim LIMIT {start_row}, {num_rows}")
    colnames = [row[0] for row in c.description]
    df = pd.DataFrame(c.fetchall(), columns=colnames)
    conn.close()
    return df


def query_button_2():
    conn = sqlite3.connect('FinalProject.db')
    c = conn.cursor()
    c.execute("SELECT id, day, month, year FROM DateDim")  # Update column names here
    colnames = [row[0] for row in c.description]
    df = pd.DataFrame(c.fetchall(), columns=colnames)
    conn.close()
    return df

@app.route('/get_table_data')
def get_table_data():
    button_id = int(request.args.get('id'))

    if button_id == 1:
        start_row = int(request.args.get('start_row', 0))
        num_rows = 10
        table_data = query_button_1(start_row, num_rows)
    elif button_id == 2:
        table_data = query_button_2()
    else:
        return jsonify([])

    table_data_list = table_data.to_dict('records')
    return jsonify(table_data_list)
    

if __name__ == '__main__':
    app.run()