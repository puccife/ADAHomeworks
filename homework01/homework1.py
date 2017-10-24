import csv
import glob
import numpy as np
import datetime as time
from functools import reduce
import matplotlib.pyplot as plt
import collections
import pandas as pd

columns_guinea = ['Date','Description','Totals']
columns_liberia = ['National', 'Variable', 'Date']
columns_sierraleone = ['National', 'variable', 'date']

path_guinea = r'./data/ebola/guinea_data'
path_liberia = r'./data/ebola/liberia_data'
path_sierraleone = r'./data/ebola/sl_data'

allFiles = glob.glob(path_guinea + "/*.csv")
frame = pd.DataFrame()
list_ = []
for file_ in allFiles:
    df = pd.read_csv(file_,index_col=None, header=0)
    list_.append(df)
df = pd.concat(list_)
df = pd.DataFrame(df)
df.dropna(axis=0, how='all')
df = df.fillna(0)
df = df.set_index('Description')
col_list= list(df)
print(col_list)
col_list.remove('Date')
col_list.remove('Totals')
df = df.convert_objects(convert_numeric=True)
df['TotalsByCity'] = df[col_list].sum(axis=1, numeric_only=True)
df = df.fillna(0)
# df["MAX"] = df[['TotalsByCity', 'Totals']].max(axis=1)
df["MAX"] = df['TotalsByCity']
df = df[['MAX','Date']]
df['day'] = pd.DatetimeIndex(df['Date']).day
df.Date = pd.to_datetime(df.Date).dt.strftime('%m/%Y')
df_confirmed = df.loc['Total deaths of confirmed']
df_newcases = df.loc['New cases of confirmed']

df_confirmed.loc['max_deaths'] = df_confirmed.Date.map(lambda x: df_confirmed.groupby('Date')['MAX'].max()[x])
df_confirmed['max_day'] = df_confirmed.Date.map(lambda x: df_confirmed.groupby('Date')['day'].max()[x])
df_confirmed['min_deaths'] = df_confirmed.Date.map(lambda x: df_confirmed.groupby('Date')['MAX'].min()[x])
df_confirmed['min_day'] = df_confirmed.Date.map(lambda x: df_confirmed.groupby('Date')['day'].min()[x])
df_confirmed['days'] = df_confirmed['max_day'] - df_confirmed['min_day'] + 1
df_confirmed = df_confirmed.groupby(['Date']).first()
del df_confirmed['MAX']
del df_confirmed['day']
del df_confirmed['min_day']
del df_confirmed['max_day']
df_newcases['guinea_new_mean'] = df_newcases.Date.map(lambda x: df_newcases.groupby('Date')['MAX'].mean()[x])
df_newcases = df_newcases.groupby(['Date']).first()
del df_newcases['MAX']
result_guinea = pd.merge(df_newcases.reset_index(), df_confirmed.reset_index(), on=['Date'], how='inner').set_index(['Date'])
result_guinea['deaths_x'] = result_guinea['max_deaths'] - result_guinea['max_deaths'].shift(+1)
result_guinea['deaths_y'] = result_guinea['max_deaths'].sub(result_guinea['min_deaths'], axis=0)
result_guinea['deaths'] = result_guinea[['deaths_x', 'deaths_y']].max(axis=1)
result_guinea['guinea_death_mean'] = result_guinea['deaths'] / result_guinea['days']
del result_guinea['max_deaths']
del result_guinea['min_deaths']
del result_guinea['deaths']
del result_guinea['deaths_x']
del result_guinea['deaths_y']
del result_guinea['days']
del result_guinea['day']
print(result_guinea)

allFiles = glob.glob(path_liberia + "/*.csv")
frame = pd.DataFrame()
list_ = []
for file_ in allFiles:
    df = pd.read_csv(file_,index_col=None, header=0)
    list_.append(df)
df = pd.concat(list_)
df = pd.DataFrame(df)
df = df.fillna(0)
df = df.set_index('Variable')
col_list= list(df)
print(col_list)
col_list.remove('Date')
col_list.remove('National')
df = df.convert_objects(convert_numeric=True)
df['TotalsByCity'] = df[col_list].sum(axis=1, numeric_only=True)
df = df.fillna(0)
# df["MAX"] = df['TotalsByCity']
df["MAX"] = df[['TotalsByCity', 'National']].max(axis=1)
df = df[['MAX','Date']]
df['day'] = pd.DatetimeIndex(df['Date']).day
df.Date = pd.to_datetime(df.Date).dt.strftime('%m/%Y')
df_confirmed = df.loc['Total death/s in confirmed cases']
df_newcases = df.loc['New case/s (confirmed)']
df_confirmed['max_deaths'] = df_confirmed.Date.map(lambda x: df_confirmed.groupby('Date')['MAX'].max()[x])
df_confirmed['max_day'] = df_confirmed.Date.map(lambda x: df_confirmed.groupby('Date')['day'].max()[x])
df_confirmed['min_deaths'] = df_confirmed.Date.map(lambda x: df_confirmed.groupby('Date')['MAX'].min()[x])
df_confirmed['min_day'] = df_confirmed.Date.map(lambda x: df_confirmed.groupby('Date')['day'].min()[x])
df_confirmed['days'] = df_confirmed['max_day'] - df_confirmed['min_day'] + 1
df_confirmed = df_confirmed.groupby(['Date']).first()
del df_confirmed['MAX']
del df_confirmed['day']
del df_confirmed['min_day']
del df_confirmed['max_day']
df_newcases = df_newcases[df_newcases['MAX'] < 1000]
df_newcases['liberia_new_mean'] = df_newcases.Date.map(lambda x: df_newcases.groupby('Date')['MAX'].mean()[x])
df_newcases = df_newcases.groupby(['Date']).first()
del df_newcases['MAX']
result_liberia = pd.merge(df_newcases.reset_index(), df_confirmed.reset_index(), on=['Date'], how='inner').set_index(['Date'])
result_liberia['deaths_x'] = result_liberia['max_deaths'] - result_liberia['max_deaths'].shift(+1)
result_liberia['deaths_y'] = result_liberia['max_deaths'].sub(result_liberia['min_deaths'], axis=0)
result_liberia['deaths'] = result_liberia[['deaths_x', 'deaths_y']].max(axis=1)
result_liberia['liberia_death_mean'] = result_liberia['deaths'] / result_liberia['days']
del result_liberia['max_deaths']
del result_liberia['min_deaths']
del result_liberia['deaths']
del result_liberia['deaths_x']
del result_liberia['deaths_y']
del result_liberia['days']
del result_liberia['day']

allFiles = glob.glob(path_sierraleone + "/*.csv")
frame = pd.DataFrame()
list_ = []
for file_ in allFiles:
    df = pd.read_csv(file_,index_col=None, header=0)
    list_.append(df)
df = pd.concat(list_)
df = pd.DataFrame(df)
df = df.fillna(0)
df = df.set_index('variable')
col_list= list(df)
print(col_list)
col_list.remove('date')
col_list.remove('National')
df = df.convert_objects(convert_numeric=True)
df['TotalsByCity'] = df[col_list].sum(axis=1, numeric_only=True)
df = df.fillna(0)
df["MAX"] = df['TotalsByCity']
# df["MAX"] = df[['TotalsByCity', 'National']].max(axis=1)
df = df[['MAX','date']]
df.rename(columns={"date": "Date"}, inplace=True)
df['day'] = pd.DatetimeIndex(df['Date']).day
df.Date = pd.to_datetime(df.Date).dt.strftime('%m/%Y')
df_newcases = df.loc['new_confirmed']
df_confirmed = df.loc['death_confirmed']

df_confirmed['max_deaths'] = df_confirmed.Date.map(lambda x: df_confirmed.groupby('Date')['MAX'].max()[x])
df_confirmed['max_day'] = df_confirmed.Date.map(lambda x: df_confirmed.groupby('Date')['day'].max()[x])
df_confirmed['min_deaths'] = df_confirmed.Date.map(lambda x: df_confirmed.groupby('Date')['MAX'].min()[x])
df_confirmed['min_day'] = df_confirmed.Date.map(lambda x: df_confirmed.groupby('Date')['day'].min()[x])
df_confirmed['days'] = df_confirmed['max_day'] - df_confirmed['min_day'] + 1
df_confirmed = df_confirmed.groupby(['Date']).first()
del df_confirmed['MAX']
del df_confirmed['day']
del df_confirmed['min_day']
del df_confirmed['max_day']
df_newcases['sierra_new_mean'] = df_newcases.Date.map(lambda x: df_newcases.groupby('Date')['MAX'].mean()[x])
df_newcases = df_newcases.groupby(['Date']).first()
del df_newcases['MAX']
result_sierra = pd.merge(df_newcases.reset_index(), df_confirmed.reset_index(), on=['Date'], how='inner').set_index(['Date'])
result_sierra['deaths_x'] = result_sierra['max_deaths'] - result_sierra['max_deaths'].shift(+1)
result_sierra['deaths_y'] = result_sierra['max_deaths'].sub(result_sierra['min_deaths'], axis=0)
result_sierra['deaths'] = result_sierra[['deaths_x', 'deaths_y']].max(axis=1)
result_sierra['sierra_death_mean'] = result_sierra['deaths'] / result_sierra['days']
del result_sierra['max_deaths']
del result_sierra['min_deaths']
del result_sierra['deaths']
del result_sierra['deaths_x']
del result_sierra['deaths_y']
del result_sierra['days']
del result_sierra['day']

result = pd.merge(result_liberia.reset_index(), result_guinea.reset_index(), on=['Date'], how='outer').set_index(['Date'])
result = pd.merge(result.reset_index(), result_sierra.reset_index(), on=['Date'], how='outer').set_index(['Date'])
print(result)
result.plot()

plt.show()
