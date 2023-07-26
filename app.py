from flask import Flask, render_template, request, jsonify, redirect, flash, url_for, session
from flask_session import Session
import sqlite3
import pandas as pd
from login import LoginForm, SignUpForm, UpLoadCSV
from upload import upload_csv
import os
import base64
from io import BytesIO

import sqlite3
from flask import Response 
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

matplotlib.use('Agg')
import matplotlib.pyplot as plt


app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"]=os.urandom(32)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = "static/files"
Session(app)


@app.route('/')
def root():
    session["user_id"] = None
    return redirect(url_for("login_page"))

# @app.route('/visual', methods=["GET"])
# def visual():
#     return render_template('visual.html')
    

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
            return redirect(url_for("home_page"))
            #return home_page()
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
    if 'user_id' not in list(session.keys()):
        return redirect(url_for("login_page"))
    elif session['user_id'] is None:
        return redirect(url_for("login_page"))
    else:
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
    c.execute(f"SELECT *, ROW_NUMBER() OVER(ORDER BY id) as row_number FROM DateDim")  # Update column names here
    colnames = [row[0] for row in c.description]
    df = pd.DataFrame(c.fetchall(), columns=colnames)
    conn.close()
    return df

def query_button_3():
    conn = sqlite3.connect('FinalProject.db')
    c = conn.cursor()
    c.execute(f"SELECT id, healthData_id, user_id, date_id, value, ROW_NUMBER() OVER(ORDER BY id) as row_number FROM HealthFact WHERE user_id={session['user_id']}")
    colnames = [row[0] for row in c.description]
    df = pd.DataFrame(c.fetchall(), columns=colnames)
    conn.close()
    return df

def query_button_4():
    conn = sqlite3.connect('FinalProject.db')
    c = conn.cursor()
    c.execute(f"""SELECT HealthFact.healthData_id,HealthDim.type, HealthDim.desc, HealthDim.unit_of_measurement, DateDim.day, DateDim.month, DateDim.year, HealthFact.value, ROW_NUMBER() OVER(ORDER BY HealthFact.id) as row_number
              FROM HealthDim
              JOIN HealthFact ON HealthDim.id = HealthFact.healthData_id
              JOIN DateDim DateDim ON DateDim.id = HealthFact.date_id
              WHERE HealthFact.user_id = {session["user_id"]}
    """)
    colnames = [row[0] for row in c.description]
    df = pd.DataFrame(c.fetchall(), columns=colnames)
    conn.close()
    return df

@app.route('/get_table_data')
def get_table_data():
    if 'user_id' not in list(session.keys()):
        return redirect(url_for("login_page"))
    elif session['user_id'] is None:
        return redirect(url_for("login_page"))
    else:
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
            start_row = int(request.args.get('start_row', 0))
            num_rows = 10
            table_data = query_button_3()
        elif button_id == 4:
            table_data = query_button_4()
        else:
            return jsonify([])

        table_data_list = table_data.to_dict('records')
        return jsonify(table_data_list)
    
@app.route('/update_cell', methods=['POST'])
def update_cell():
    if 'user_id' not in list(session.keys()):
        return redirect(url_for("login_page"))
    elif session['user_id'] is None:
        return redirect(url_for("login_page"))
    else:
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


@app.route('/upload', methods=["GET","POST"])
def upload_page():
    form = UpLoadCSV()
    if 'user_id' not in list(session.keys()):
        return redirect(url_for("login_page"))
    elif session['user_id'] is None:
        return redirect(url_for("login_page"))
    elif form.validate_on_submit():
        uploaded = request.files.get('file')
        if uploaded.filename != "":
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], uploaded.filename)
            uploaded.save(file_path)
            upload_csv(file_path, session['user_id'])
            return redirect(url_for("home_page"))
    return render_template('upload.html', title="Upload", form=form)
            

@app.route('/delete_health_fact/<int:id>', methods=['GET'])
def delete_health_fact(id):
    if 'user_id' not in list(session.keys()):
        return redirect(url_for("login_page"))
    elif session['user_id'] is None:
        return redirect(url_for("login_page"))
    else:
        conn = sqlite3.connect('FinalProject.db')
        c = conn.cursor()
        c.execute(f"DELETE FROM HealthFact WHERE id=?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('home_page'))


@app.route('/visual', methods=["GET"])
def visual():

    conn = sqlite3.connect('FinalProject.db')
    c = conn.cursor()

    chart_data_list = []

    c.execute(f"""
    SELECT 
        hD.type,
        Round(AVG(hF.value),2) as avg_time
    FROM
        healthDim hD 
    INNER JOIN 
        healthFact hF ON hD.id = hF.healthData_id 
    WHERE
        type in ('active_energy', 'basal_energy_burned')
    AND 
        hF.user_id = {session["user_id"]}
    GROUP BY
        hD.type""")
    colnames = c.description   # gather collumn names from a new query
    colnames_list = []
    for row in colnames:
        colnames_list.append(row[0])

    df = pd.DataFrame(c.fetchall(), columns=colnames_list)
    df

    labels = df['type']
    sizes = df['avg_time']

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels)
    plt.title('Average Energy Burned')
    # Save it to a temporary buffer.
    buf = BytesIO()
    plt.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    chart_data_list.append(data)


    c.execute(f"""
    SELECT 
        dD.year,
        dD.month,
        round(SUM(hF.value),2) value
    FROM
        healthFact hF
    INNER JOIN 
        healthDim hD on hF.healthData_id = hD.id
    INNER JOIN 
        dateDim dD on hF.date_id = dD.id
    WHERE
        type in ('active_energy')
    AND 
        hF.user_id = {session["user_id"]}
    GROUP BY 
        dD.year,
        dD.month
    """)

    colnames = c.description   # gather collumn names from a new query
    colnames_list = []
    for row in colnames:
        colnames_list.append(row[0])
        
    df = pd.DataFrame(c.fetchall(), columns=colnames_list)
    print(df)

    x = df.pivot_table(index='year', columns='month', values='value', aggfunc='sum')
    x = x.fillna(0)
    x

    plt.figure(figsize = (8,5))
    ax = plt.subplot(121) 
    ax = sns.heatmap(x,linewidth = 1,cmap = 'Blues')
    #ax.set(xlabel='X-Axis', ylabel='Y-Axis')
    plt.title('Running Totals')

    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    # Save it to a temporary buffer.
    buf = BytesIO()
    plt.savefig(buf, format="png")
    # Embed the result in the html output.
    data1 = base64.b64encode(buf.getbuffer()).decode("ascii")
    chart_data_list.append(data1)

    c.execute(f"""
    select 
        dD.year,
        dD.month,
        strftime('%W', date(year ||'-01-01','+'||(month-1)||' month') ) week,
        hD.unit_of_measurement,
        max(hF.value) value
    FROM
        healthFact hF
    INNER JOIN
        dateDim dD on hF.date_id = dD.id
    INNER JOIN 
        healthDim hD on hF.healthData_id = hD.id
    WHERE
        hD.type = 'active_energy'
    AND 
        hF.user_id = {session["user_id"]}
    GROUP BY
        dD.year,
        dD.month,
        week,
        hD.unit_of_measurement;
    """)

    colnames = c.description   # gather collumn names from a new query
    colnames_list = []
    for row in colnames:
        colnames_list.append(row[0])

    df = pd.DataFrame(c.fetchall(), columns=colnames_list)
    df.head(10)

    c.execute(f"""
    select
        hD.type,
        hD.unit_of_measurement,
        Round(sum(hF.value),2) value
    FROM
        healthFact hF
    INNER JOIN 
        healthDim hD on hF.healthData_id = hD.id
    WHERE 
        hD.unit_of_measurement = 'count/min'
    AND 
        hF.user_id = {session["user_id"]}
    GROUP BY
        hD.type,
        hD.unit_of_measurement
    ORDER BY 
        sum(hF.value)  desc  limit 3;
    """)

    colnames = c.description   # gather collumn names from a new query
    colnames_list = []
    for row in colnames:
        colnames_list.append(row[0])

    df = pd.DataFrame(c.fetchall(), columns=colnames_list)
    df

    plt.figure(figsize=(5,3))
    sns.barplot(data=df, x="type", y="value")

    buf = BytesIO()
    plt.savefig(buf, format="png")
    # Embed the result in the html output.
    data2 = base64.b64encode(buf.getbuffer()).decode("ascii")
    chart_data_list.append(data2)

    c.execute(f"""
    select
        dD.year,
        hD.desc,
        Round(avg(hF.value),2) value
    FROM
        healthFact hF
    INNER JOIN 
        healthDim hD on hF.healthData_id = hD.id
    INNER JOIN 
        dateDim dD on hF.date_id = dD.id
    WHERE
        type like '%sleep%' 
    AND
        type not like '%awake%'
    AND 
        hF.user_id = {session["user_id"]}
    GROUP BY
        dD.year,
        hD.desc
    """)

    colnames = c.description   # gather collumn names from a new query
    colnames_list = []
    for row in colnames:
        colnames_list.append(row[0])

    df = pd.DataFrame(c.fetchall(), columns=colnames_list)
    df


    x = df.pivot_table(index='year', columns='desc', values='value', aggfunc='sum')

    x = x.fillna(0)
    x

    # create stacked bar chart for monthly temperatures
    x.plot(kind='bar', stacked=True, color=['red', 'skyblue', 'green'],figsize=(8,5))

    # labels for x & y axis
    plt.xlabel('years')
    plt.ylabel('Value')

    # Put a legend to the right of the current axis
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # title of plot
    plt.title('Sleep Analysis')
    buf = BytesIO()
    plt.savefig(buf, format="png")
    # Embed the result in the html output.
    data3 = base64.b64encode(buf.getbuffer()).decode("ascii")
    chart_data_list.append(data3)

    chart_images = []
    for data in chart_data_list:
        chart_images.append(f"<img src='data:image/png;base64,{data}'/>")

    # Join the list of chart images into a single HTML string
    html_response = ''.join(chart_images)
    header_names = ["Average Energy Burned", "Running Totals", "Top Active Energy", "Sleep Analysis"]
    #chart_data_with_headers = list(zip(chart_data_list, header_names))

    # Return the HTML response with all the chart images
    return render_template('visual.html', chart_data_list=chart_data_list, header_name=header_names )
    #return Response(html_response, content_type='text/html')


if __name__ == '__main__':
    app.run()