from flask import Flask, render_template, request
import sqlite3
import pandas as pd

app = Flask(__name__)

@app.route('/')
@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/home')
def home_page():
    num_rows = int(request.args.get('num_rows', 5))
    HealthDim_query = query_details()
    return render_template('home.html', HealthDim_query = HealthDim_query, num_rows=num_rows)

def query_details():
    conn = sqlite3.connect('FinalProject.db')
    c = conn.cursor()
    c.execute("SELECT * FROM HealthDim")
    colnames = [row[0] for row in c.description]
    df = pd.DataFrame(c.fetchall(), columns=colnames)
    return df

if __name__ == '__main__':
    app.run()