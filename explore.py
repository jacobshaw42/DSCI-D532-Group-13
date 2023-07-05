import pandas as pd

df = pd.read_csv("/home/jacob/DSCI-D532-Group-13/data/HealthAutoExport-2021-06-01-2022-01-01 Data.csv")
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
#print(df1.head())
#print(df1.info())
df2 = df1.set_index("Date")
df3 = df2.stack().reset_index()
df3.rename(columns = {"level_1":"health_data_type",0:"value"}, inplace = True)
df3.loc[:,"type_unit_of_measurement"] = df3.health_data_type.apply(lambda x: x.split(" (")[1][:-1] if " (" in x else None)
df3.loc[:,"type"] = df3.health_data_type.apply(lambda x: x.split(" (")[0].replace(":","").replace("Analysis ","").replace("Apple ","").replace(" ", "_").replace("[","").replace("]","").lower() if " (" in x else None)
df3.loc[:,"day_of_month"] = df3.Date.apply(lambda x: x.split(" ")[0].split("-")[2])
df3.loc[:,"month"] = df3.Date.apply(lambda x: x.split(" ")[0].split("-")[1])
df3.loc[:,"year"] = df3.Date.apply(lambda x: x.split(" ")[0].split("-")[0])
#print(df3.head())
#print(df3["type"].unique())

types_index = {x:ind for ind,x in enumerate(df3["type"].unique())}
date_index = {x:ind for ind,x in enumerate(df3["Date"].unique())}

df3.loc[:,"date_index"] = df3["Date"].apply(lambda x: date_index[x])
df3.loc[:,"type_index"] = df3["type"].apply(lambda x: types_index[x])

healthDataFact = df3.loc[:,["date_index","type_index","value"]]
healthDataDim = df3.loc[:,["type_index","type","type_unit_of_measurement"]].drop_duplicates()
dateDim = df3.loc[:,["date_index","day_of_month","month","year"]].drop_duplicates()

print(healthDataFact)
print(healthDataDim)
print(dateDim)