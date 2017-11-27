import dateutil.parser
import numpy as np
import pandas as pd

def __parse_year_of_date(row, column, from_year, to_year):
    if isinstance(row[column], str):
        date = dateutil.parser.parse(row[column])
        if date.year <= to_year and date.year >= from_year:
            return date.year
        else:
            return np.nan
    else:
        return np.nan    
    
def parse_dates(dataframe, from_year, to_year): #leak_data, bounded_data_bottom, bounded_data_up
    date_events = [["incorporation_date","incorporation_before_leak"],
                   ["inactivation_date","inactivation_before_leak"], 
                   ["struck_off_date","struck_off_before_leak"],
                   ["dorm_date", "dorm_date_before_leak"]]
    for date_event in date_events:
        dataframe[date_event[0]] = dataframe.apply(lambda row: __parse_year_of_date(row,date_event[0], from_year, to_year), axis=1) 
    return dataframe