import dateutil.parser
import numpy as np


def __parse_year_of_date(row, column, from_year, to_year):
    """
    !private function - This function is used by parse_dates function to parse the date 
    present in the dataset to a standard datetime format.
    :param row: row of the dataset
    :param column: column of the dataset
    :param from_year: bottom bound for the years
    :param to_year: upper bound for the years
    :return: the date in a standard datetime format.
    """
    if isinstance(row[column], str):
        date = dateutil.parser.parse(row[column])
        if date.year <= to_year and date.year >= from_year:
            return date.year
        else:
            return np.nan
    else:
        return np.nan    


def parse_dates(dataframe, from_year, to_year): #leak_data, bounded_data_bottom, bounded_data_up
    """
    This function is used to parse the dates in the original dataframe. It's possible to specify
    bounding for the years that we want to analyze
    :param dataframe: original dataframe.
    :param from_year: bottom bound
    :param to_year: upper bound
    :return: the parsed dataframe.
    """
    date_events = [["incorporation_date","incorporation_before_leak"],
                   ["inactivation_date","inactivation_before_leak"], 
                   ["struck_off_date","struck_off_before_leak"],
                   ["dorm_date", "dorm_date_before_leak"]]
    for date_event in date_events:
        dataframe[date_event[0]] = dataframe.apply(lambda row: __parse_year_of_date(row,date_event[0], from_year, to_year), axis=1) 
    return dataframe