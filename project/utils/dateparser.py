import dateutil.parser
import numpy as np
import pandas as pd


def is_date_before(date_, div_date):
    return date_ <= div_date


def categorize_2013(row, event, delimiter, lower_date, upper_date):
    if isinstance(row[event], pd.Timestamp):
        date = row[event].to_pydatetime()
    else:
        return np.nan
    if (is_date_before(date, lower_date)):
        return np.nan
    elif (is_date_before(upper_date, date)):
        return np.nan
    elif (is_date_before(date, delimiter)):
        return True
    else:
        return False


def parse_date(row, column):
    if isinstance(row[column], str):
        date = dateutil.parser.parse(row[column])
        return date
    else:
        return np.nan


def parse_dates(dataframe, leak_data, bounded_data_bottom, bounded_data_up):
    date_events = [["incorporation_date", "incorporation_before_leak"],
                   ["inactivation_date", "inactivation_before_leak"],
                   ["struck_off_date", "struck_off_before_leak"],
                   ["dorm_date", "dorm_date_before_leak"]]
    for date_event in date_events:
        dataframe[date_event[0]] = dataframe.apply(lambda row: parse_date(row, date_event[0]), axis=1)
        dataframe[date_event[1]] = dataframe.apply(lambda row: categorize_2013(row, date_event[0], leak_data, bounded_data_bottom, bounded_data_up), axis=1)
    return dataframe
