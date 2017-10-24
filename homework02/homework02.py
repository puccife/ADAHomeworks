import pandas as pd
import numpy as np
%matplotlib inline
import matplotlib.pyplot as plt


import requests
from bs4 import BeautifulSoup

import json

default_path = 'https://www.topuniversities.com'
r = requests.get(default_path +'/sites/default/files/qs-rankings-data/357051.txt?_=1507995842896')
result_json = r.json()

result = pd.DataFrame.from_dict(result_json['data']).head(200)

for index, row in result.iterrows():
        r_ = requests.get(default_path + result.iloc[index]['url'])
        soup = BeautifulSoup(r_.text, 'html.parser')
        university = result.iloc[index]['title']
        try:
            total_faculty = soup.find('div', class_='total faculty')
            result.loc[index, 'Staff total number'] = int(total_faculty.find('div', class_='number').text.split()[0].replace(',', ''))
        except:
            print(university + ' has no values for TOTAL_STAFF')
        try:
            total_student = soup.find('div', class_='total student')
            result.loc[index, 'Students total number'] = int(total_student.find('div', class_='number').text.split()[0].replace(',', ''))
        except:
            print(university + ' has no values for TOTAL_STUDENTS')
        try:
            inter_faculty = soup.find('div', class_='inter faculty')
            result.loc[index, 'International Staff number'] = int(inter_faculty.find('div', class_='number').text.split()[0].replace(',', ''))
        except:
            print(university + ' has no values for INTERNATIONAL_STAFF')
        try:
            inter_student = soup.find('div', class_='total inter')
            result.loc[index, 'International Students number'] = int(inter_student.find('div', class_='number').text.split()[0].replace(',', ''))
        except:
            print(university + ' has no values for INTERNATIONAL_STUDENTS')
            print(default_path + result.iloc[index]['url'])

result.fillna(0)
useless_columns = ['core_id','guide','nid','url','logo']
for column_name in useless_columns:
    del result[column_name]

df = result.copy()

df['Ratio Staff/Student']=df['Staff total number']/df['Students total number']
df['Ratio International/National Students']=df['International Students number']/df['Students total number']

df_international = df.sort_values('Ratio International/National Students', ascending=0)
df_staffstud = df.sort_values('Ratio Staff/Student', ascending=0)

df_international.head(3)

df_staffstud.head(3)


df_international_by_country_or_region = df_international.copy()
other_useless_columns = ['rank_display','score','stars','cc','Ratio International/National Students','Ratio Staff/Student','title']
for useless_column in other_useless_columns:
    del df_international_by_country_or_region[useless_column]
df_international_by_country_or_region.head(5)

df_international_by_country = df_international_by_country_or_region.groupby(['country']).sum()
df_international_by_region = df_international_by_country_or_region.groupby(['region']).sum()
df_international_by_country['Ratio Staff/Student'] = df_international_by_country['Staff total number']/df_international_by_country['Students total number']
df_international_by_country['Ratio International/National Students'] = df_international_by_country['International Students number']/df_international_by_country['Students total number']
df_international_by_country['Ratio International/National Students'] = df_international_by_country['International Students number']/df_international_by_country['Students total number']

df_international_by_country_staffstudent = df_international_by_country.copy()
df_international_by_country_staffstudent.sort_values('Ratio Staff/Student', ascending=0).head(5)

df_international_by_country_intstudent = df_international_by_country.copy()
df_international_by_country_intstudent.sort_values('Ratio International/National Students', ascending=0).head(5)

df_international_by_country_intstudent.head(5).plot(kind = 'bar', figsize = (15, 5))
