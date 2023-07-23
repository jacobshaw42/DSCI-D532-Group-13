from flask import Flask, render_template, request, jsonify, redirect, flash, url_for, session
from flask_session import Session
import sqlite3
import pandas as pd
from login import LoginForm, SignUpForm, UpLoadCSV
from wtforms import ValidationError
import os
import sys

app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"]=os.urandom(32)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def root():
    session["user_id"] = None
    return redirect(url_for("login_page"))

@app.route('/login', methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        conn = sqlite3.connect("FinalProject.db")
        curs = conn.cursor()
        curs.execute("SELECT * FROM UserDim WHERE email = (?)", [form.email.data])
        user = curs.fetchone()
        if user is None:
            flash("Email is not valid!", category="warning")
        elif form.email.data == user[2] and form.password.data == user[3]:
            session["user_id"] = user[0]
            return home_page()
        else:
            flash("Invalid Password!",category="warning")
    return render_template('login.html', title="Login", form=form)

@app.route('/signup', methods=['GET','POST'])
def signup_page():
    form = SignUpForm()
    if form.validate_on_submit():
        conn = sqlite3.connect("FinalProject.db")
        curs = conn.cursor()
        curs.execute("SELECT * FROM UserDim WHERE email = (?)", [form.email.data])
        user = curs.fetchone()
        if form.password.data != form.password_confirm.data:
            flash("Passwords do not match!", category="warning")
            return render_template('signup.html', title="signup", form=form)
        elif user is None:
            curs.execute("INSERT INTO UserDim(name, email, password) VALUES((?), (?), (?))", [form.name.data, form.email.data, form.password.data])
            conn.commit()
            return login_page()
        else:
            flash("Email is already used!",category="warning")
    return render_template('signup.html', title="SignUp", form=form)

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
    c.execute(f"SELECT * FROM HealthFact WHERE user_id={session['user_id']}")
    colnames = [row[0] for row in c.description]
    df = pd.DataFrame(c.fetchall(), columns=colnames)
    conn.close()
    return df

def query_button_4():
    conn = sqlite3.connect('FinalProject.db')
    c = conn.cursor()
    c.execute(f"""SELECT HealthDim.*, DateDim.day, DateDim.month, DateDim.year, HealthFact.value
              FROM HealthDim
              JOIN HealthFact ON HealthDim.id = HealthFact.healthData_id
              JOIN DateDim DateDim ON DateDim.id = HealthFact.date_id
              WHERE HealthFact.user_id = {session["user_id"]}
    """)
    colnames = [row[0] for row in c.description]
    df = pd.DataFrame(c.fetchall(), columns=colnames)
    conn.close()
    return df

@app.route('/schema')
def schema_page():
    return render_template('schema.html')

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

"""
@app.route('/upload', methods=["GET","POST"])
def upload_page():
    form = UpLoadCSV()
    if form.validate_on_submit():
        uploaded = request.files('file')
        if uploaded.filename != "":
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], uploaded.filename)
"""

@app.route('/delete_health_fact/<int:id>', methods=['GET'])
def delete_health_fact(id):
    conn = sqlite3.connect('FinalProject.db')
    c = conn.cursor()
    c.execute(f"DELETE FROM HealthFact WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home_page'))


if __name__ == '__main__':
    app.run()