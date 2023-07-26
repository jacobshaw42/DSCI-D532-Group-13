

import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


conn = sqlite3.connect('FinalProject.db')
c = conn.cursor()


c.execute('''
SELECT 
    hD.type,
    Round(AVG(hF.value),2) as avg_time
FROM
    healthDim hD 
INNER JOIN 
    healthFact hF ON hD.id = hF.healthData_id 
WHERE
    type in ('active_energy', 'basal_energy_burned')
GROUP BY
    hD.type''')
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


c.execute('''
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
GROUP BY 
    dD.year,
    dD.month
''')

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
ax = sns.heatmap(x,linewidth = 1,cmap = 'Blues')
#ax.set(xlabel='X-Axis', ylabel='Y-Axis')
plt.title('Running Totals')



c.execute('''
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
where hD.type = 'active_energy'
GROUP BY
    dD.year,
    dD.month,
    week,
    hD.unit_of_measurement;
''')

colnames = c.description   # gather collumn names from a new query
colnames_list = []
for row in colnames:
    colnames_list.append(row[0])

df = pd.DataFrame(c.fetchall(), columns=colnames_list)
df.head(10)



c.execute('''
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
GROUP BY
    hD.type,
    hD.unit_of_measurement
ORDER BY 
    sum(hF.value)  desc  limit 3;
''')

colnames = c.description   # gather collumn names from a new query
colnames_list = []
for row in colnames:
    colnames_list.append(row[0])

df = pd.DataFrame(c.fetchall(), columns=colnames_list)
df

plt.figure(figsize=(5,3))
sns.barplot(data=df, x="type", y="value")




sql = c.execute('''
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
and  type not like '%awake%'
GROUP BY
    dD.year,
    hD.desc
''')

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

