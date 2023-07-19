from flask import Flask, render_template, request, jsonify, redirect, flash
import sqlite3
import pandas as pd
from login import LoginForm
import os
import sys

app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"]=os.urandom(32)

@app.route('/')
    
@app.route('/login', methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        conn = sqlite3.connect("FinalProject.db")
        curs = conn.cursor()
        curs.execute("SELECT * FROM UserDim WHERE email = (?)", [form.email.data])
        user = list(curs.fetchone())
        if form.email.data == user[2] and form.password.data == user[3]:
            return home_page()
        else:
            flash("Invalid Login",category="warning")
    return render_template('login.html', title="Login", form=form)

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

def query_button_3():
    conn = sqlite3.connect('FinalProject.db')
    c = conn.cursor()
    c.execute("SELECT * FROM HealthFact")
    colnames = [row[0] for row in c.description]
    df = pd.DataFrame(c.fetchall(), columns=colnames)
    conn.close()
    return df

def query_button_4():
    conn = sqlite3.connect('FinalProject.db')
    c = conn.cursor()
    c.execute("""SELECT HealthDim.*, DateDim.day, DateDim.month, DateDim.year, HealthFact.value
              FROM HealthDim
              JOIN HealthFact ON HealthDim.id = HealthFact.healthData_id
              JOIN DateDim DateDim ON DateDim.id = HealthFact.date_id
    """)
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
        start_row = int(request.args.get('start_row', 0))
        num_rows = 10
        table_data = query_button_2()
    elif button_id == 3:
        table_data = query_button_3()
    elif button_id == 4:
        table_data = query_button_4()
    else:
        return jsonify([])

    table_data_list = table_data.to_dict('records')
    return jsonify(table_data_list)
    
@app.route('/update_cell', methods=['POST'])
def update_cell():
    conn = sqlite3.connect('FinalProject.db')
    c = conn.cursor()
    data = request.get_json()
    column = data['column']
    id = data['id']
    value = data['value']

    if column == 'type':
        table = 'HealthDim'
        update_column = 'type'
    elif column == 'desc':
        table = 'HealthDim'
        update_column = 'desc'
    elif column == 'unit_of_measurement':
        table = 'HealthDim'
        update_column = 'unit_of_measurement'
    elif column == 'day':
        table = 'DateDim'
        update_column = 'day'
    elif column == 'month':
        table = 'DateDim'
        update_column = 'month'
    elif column == 'year':
        table = 'DateDim'
        update_column = 'year'
    elif column == 'value':
        table = 'HealthFact'
        update_column = 'value'
    else:
        return jsonify({'success': False})

    c.execute(f"UPDATE {table} SET {update_column} = ? WHERE id = ?", (value, id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run()