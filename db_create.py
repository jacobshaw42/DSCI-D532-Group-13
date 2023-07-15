import sqlite3
import pandas as pd

df = pd.read_csv("HealthAutoExport-2021-06-01-2023-06-20 Data.csv")
cols = [
        "Date",
        "Active Energy (kcal)",
        "Apple Exercise Time (min)",
        "Apple Stand Time (min)",
        "Basal Energy Burned (kcal)",
        "Flights Climbed (count)",
        "Heart Rate [Min] (count/min)",
        "Heart Rate [Max] (count/min)",
        "Heart Rate [Avg] (count/min)",
        "Resting Heart Rate (count/min)",
        "Sleep Analysis [Asleep] (hr)",
        "Sleep Analysis [In Bed] (hr)",
        "Sleep Analysis [Core] (hr)",
        "Sleep Analysis [Deep] (hr)",
        "Sleep Analysis [REM] (hr)",
        "Sleep Analysis [Awake] (hr)",
        "Stair Speed: Down (ft/s)",
        "Stair Speed: Up (ft/s)",
        "Step Count (count)",
    ]

df1 = df.loc[:,cols]
df2 = df1.set_index("Date")
df3 = df2.stack().reset_index()
df3.rename(columns = {"level_1":"health_data_type",0:"value"}, inplace = True)
df3.loc[:,"type_unit_of_measurement"] = df3.health_data_type.apply(lambda x: x.split(" (")[1][:-1] if " (" in x else None)
df3.loc[:,"type"] = df3.health_data_type.apply(lambda x: x.split(" (")[0].replace(":","").replace("Analysis ","").replace("Apple ","").replace(" ", "_").replace("[","").replace("]","").lower() if " (" in x else None)
df3["day_of_month"] = pd.to_datetime(df3["Date"]).dt.day
df3["month"] = pd.to_datetime(df3["Date"]).dt.month
df3["year"] = pd.to_datetime(df3["Date"]).dt.year

types_index = {x:ind for ind,x in enumerate(df3["type"].unique())}
date_index = {x:ind for ind,x in enumerate(df3["Date"].unique())}

df3.loc[:,"date_index"] = df3["Date"].apply(lambda x: date_index[x])
df3.loc[:,"type_index"] = df3["type"].apply(lambda x: types_index[x])

healthDataFact = df3.loc[:,["date_index","type_index","value"]]
healthDataDim = df3.loc[:,["type_index","type","type_unit_of_measurement"]].drop_duplicates()
dateDim = df3.loc[:,["date_index","day_of_month","month","year"]].drop_duplicates()


conn = sqlite3.connect('FinalProject.db')
c = conn.cursor()

c.execute('''CREATE TABLE HealthFact(
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    date_id INTEGER,
    healthData_id INTEGER,
    value NUMERIC (10,2)
);''')

c.execute('''CREATE TABLE UserDim(
    id INTEGER PRIMARY KEY,
    name VARCHAR (100),
    email VARCHAR (100)
);''')

c.execute('''CREATE TABLE DateDim(
    id INTEGER PRIMARY KEY,
    day INTEGER (2),
    month INTEGER (2),
    year INTEGER (4)
);''')

c.execute('''CREATE TABLE HealthDim(
    id INTEGER PRIMARY KEY,
    type VARCHAR (25),
    desc VARCHAR (255),
    unit_of_measurement VARCHAR (20)
);''')

c.execute('''CREATE TABLE HealthClassifier(
    id INTEGER PRIMARY KEY,
    healthData_id INTEGER,
    classifier VARCHAR (25),
    lower_bound NUMERIC,
    upper_bound NUMERIC
);''')

conn.commit()
conn.close()