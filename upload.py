import sqlite3
import pandas as pd

def upload_csv(path, user_id):
    try:
        df = pd.read_csv(path)
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
    except Exception:
        return None
    df2 = df1.set_index("Date")
    df3 = df2.stack().reset_index()
    df3.rename(columns = {"level_1":"health_data_type",0:"value"}, inplace = True)
    df3.loc[:,"type_unit_of_measurement"] = df3.health_data_type.apply(lambda x: x.split(" (")[1][:-1] if " (" in x else None)
    df3.loc[:,"type"] = df3.health_data_type.apply(lambda x: x.split(" (")[0].replace(":","").replace("Analysis ","").replace("Apple ","").replace(" ", "_").replace("[","").replace("]","").lower() if " (" in x else None)
    df3["day"] = pd.to_datetime(df3["Date"]).dt.day
    df3["month"] = pd.to_datetime(df3["Date"]).dt.month
    df3["year"] = pd.to_datetime(df3["Date"]).dt.year

    types_index = {x:ind for ind,x in enumerate(df3["type"].unique())}
    date_index = {x:ind for ind,x in enumerate(df3["Date"].unique())}

    df3.loc[:,"date_index"] = df3["Date"].apply(lambda x: 1+date_index[x])
    df3.loc[:,"type_index"] = df3["type"].apply(lambda x: 1+types_index[x])

    healthDataFact = df3.loc[:,["date_index","type_index","value"]]
    dateDim = df3.loc[:,["date_index","day","month","year"]].drop_duplicates()
    
    date_index1 = healthDataFact.date_index.to_list()
    
    conn = sqlite3.connect('FinalProject.db')

    curDates = pd.read_sql("SELECT * FROM DateDim", conn)
    print(curDates)
    dateDim.rename(columns={'date_index':'id'},inplace=True)
    dateDim.loc[750] = ['751', 22,6,2023]
    print(dateDim)
    
    joined = pd.merge(curDates, dateDim,on=['day','month','year'],how='right',suffixes=('_old','_new'))
    #print(joined)
    changed = joined.loc[joined.id_old != joined.id_new, :]
    changed.id_old = changed['id_old'].fillna(changed["id_new"])
    newDate = changed.loc[changed.id_old == changed.id_new,:].rename(columns={'id_old':'id'}).drop('id_new',axis=1)
    print(changed)
    print(newDate)
    fix = {int(row['id_new']): int(row['id_old'])  for i, row in changed.iterrows()}
    print(fix)
    
    keys = fix.keys()
    healthDataFact.date_index = healthDataFact.date_index.apply(lambda x: fix[x] if x in keys else x)
    healthDataFact.rename(columns={'date_index':'date_id', 'type_index':'healthData_id'},inplace=True)
    healthDataFact['user_id'] = user_id
    
    date_index2 = healthDataFact.date_id.to_list()
    
    print(healthDataFact.head(20))
    
    print( date_index1 == date_index2)

    newDate.to_sql('DateDim',conn,if_exists='append',index=False)
    healthDataFact.to_sql('HealthFact', conn, if_exists='append',index=False)
#    print(newDate)


#upload_csv('/home/jacob/dsci532/FinalProject/DSCI-D532-Group-13/second.csv',2)