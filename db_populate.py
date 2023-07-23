import sqlite3
from db_create import *

conn = sqlite3.connect('FinalProject.db')
c = conn.cursor()

for _, row in dateDim.iterrows():
    day = int(row["day_of_month"])
    month = int(row["month"])
    year = int(row["year"])

    c.execute("INSERT INTO DateDim (day, month, year) VALUES (?, ?, ?)", (day, month, year))
    
user_id = 1
for _, row in healthDataFact.iterrows():
    date_id = row["date_index"]
    healthData_id = row["type_index"]
    value = row["value"]

    c.execute("INSERT INTO HealthFact (user_id, date_id, healthData_id, value) VALUES (?, ?, ?, ?)", (user_id, date_id, healthData_id, value))

descriptions = {
    "basal_energy_burned": "Calories burned during rest",
    "sleep_asleep": "Duration of deep sleep",
    "sleep_in_bed": "Time spent in bed",
    "sleep_core": "Duration of sleep cycle",
    "sleep_deep": "Duration of deep sleep",
    "sleep_rem": "Duration of REM sleep",
    "sleep_awake": "Duration of awake time during sleep",
    "step_count": "Number of steps taken",
    "active_energy": "Calories burned during activity",
    "exercise_time": "Duration of exercise",
    "stand_time": "Duration of standing",
    "flights_climbed": "Number of flights of stairs climbed",
    "heart_rate_min": "Minimum heart rate",
    "heart_rate_max": "Maximum heart rate",
    "heart_rate_avg": "Average heart rate",
    "resting_heart_rate": "Resting heart rate",
    "stair_speed_down": "Speed while descending stairs",
    "stair_speed_up": "Speed while ascending stairs"
}

for _, row in healthDataDim.iterrows():
    id = row["type_index"]
    health_type = row["type"]
    unit_of_measurement = row["type_unit_of_measurement"]

    if health_type in descriptions:
        desc = descriptions[health_type]
    else:
        desc = None
    
    c.execute("INSERT INTO HealthDim (id, type, desc, unit_of_measurement) VALUES (?, ?, ?, ?)",
              ( id, health_type, desc, unit_of_measurement))

c.execute("INSERT INTO UserDim (id, name, email, password) VALUES(1,'example','example@example.com','example')")

conn.commit()
conn.close()