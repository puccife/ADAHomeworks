import datetime as dt

import dateutil.parser
import pandas as pd

from utils.dateparser import *

entities = r'./panama_csv/Entities.csv'

entities = pd.read_csv(entities,index_col='name', header=0, low_memory=False)
entities=entities.rename(columns = {'countries':'Country'})

test = entities.head(10).copy()
df[df['Country'].isin([3, 6])]
leak_data = dateutil.parser.parse('APRIL 2, 2013') # Bahamas Leak
# leak_data = dateutil.parser.parse('DECEMBER 9, 2014') # Lux Leak
# leak_data = dateutil.parser.parse('JANUARY 21, 2014') # China Leak
# leak_data = dateutil.parser.parse('FEBRUARY 8, 2015') # Swiss Leak
# leak_data = dateutil.parser.parse('APRIL 3, 2016') # Panama Leak

month = dt.timedelta(weeks=4)
delta = month*10
bounded_data_bottom = leak_data - delta
bounded_data_up = leak_data + delta

test = parse_dates(test, leak_data, bounded_data_bottom, bounded_data_up)

print(test)
