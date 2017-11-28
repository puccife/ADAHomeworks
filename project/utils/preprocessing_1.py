import pandas as pd
import numpy as np

## Cleaning Economical Dataframe
#The Index of economic freedom dataset comes in 5 years [ 2013,2014,2015,2016,2017 ]. The structure of the dataset in 2017 is different from the structure of those in the previous years.
#The function below matches all the years' structures and the countries names to be identical to that present in the Panama Papers.

def cleaning_index_data(df,year):
    ## Input:
        # df : dataframe
        # year : a string called year used to filter columns.
    ## Output:
        # df : cleaned dataframe

    # Variables needed to manipulate through the data.
    int_year = int(year) + 1
    string_year = str(int_year)
    score = string_year + ' Score'

    # Changing those columns from objects to float
    change_type_columns = ['Public Debt (% of GDP)','FDI Inflow (Millions)','Inflation (%)',\
                           'Unemployment (%)','GDP per Capita (PPP)','5 Year GDP Growth Rate (%)',\
                           'GDP Growth Rate (%)','GDP (Billions, PPP)','Gov\'t Expenditure % of GDP ',\
                           'Tax Burden % of GDP','Corporate Tax Rate (%)','Income Tax Rate (%)','Tariff Rate (%)',\
                           'Judical Effectiveness','Property Rights','Government Integrity']

    # Fix the country name to match that in Panama papers.
    if (int_year == 2013):
        # Extract the indexes of the dataframe to a list.
        as_list = df.index.tolist()
        # Get the index number of the country needed.
        idx = as_list.index('Bahamas, The')
        # Change country name to the one desired.
        as_list[idx] = 'Bahamas'
        # Make the new list the index of the dataframe.
        df.index = as_list

    # Fix the country name to match that in Panama papers.
    if (int_year != 2013):
        # Extract the indexes of the dataframe to a list.
        as_list = df.index.tolist()
        # Get the index number of the country needed.
        idx = as_list.index('Hong Kong SAR')
        # Change country name to the one desired.
        as_list[idx] = 'Hong Kong'
        # Make the new list the index of the dataframe.
        df.index = as_list

    # Cleaning the dataframe of 2017.
    if(int_year == 2017):
        # Columns to get rid of.
        columns = ['CountryID','WEBNAME','Country']
        # change the column name score to Score to match others.
        df = df.rename(columns={score:'Score'})
        # Drop the columns we don't need.
        df = df.drop(columns,axis=1)
        # Change object type to float and fill with 0 where there is full strings.
        df[change_type_columns] = df[change_type_columns].apply(pd.to_numeric, errors='coerce')
        df = df.fillna(0)
        return df

    # Cleaning all the other dataframe years.
    # Renaming the columns
    df = df.rename(columns={score:'Score','Fiscal Freedom ':'Tax Burden', 'Freedom from Corruption':'Government Integrity'})

    # Columns to get rid of.
    column_name_1 = 'Change in Yearly Score from ' + year
    column_name_2 = 'Change in Property Rights from ' + year
    column_name_3 = 'Change in Freedom from Corruption from ' + year
    column_name_4 = 'Change in Fiscal Freedom from ' + year
    column_name_5 = 'Change in Gov\'t Spending from ' + year
    column_name_6 = 'Change in Business Freedom from ' + year
    column_name_7 = 'Change in Labor Freedom from ' + year
    column_name_8 = 'Change in Monetary Freedom from ' + year
    column_name_9 = 'Change in Trade Freedom from ' + year
    column_name_10 = 'Change in Investment Freedom from ' + year
    column_name_11 = 'Change in Financial Freedom from ' + year

    # Putting the columns in an array
    columns = ['CountryID','WEBNAME','Country',column_name_1,column_name_2,column_name_3,\
               column_name_4,column_name_5,column_name_6,\
               column_name_7,column_name_8,column_name_9,column_name_10,column_name_11]

    # Removing Judical Effectiveness as it was only included in 2017.
    change_type_columns.remove('Judical Effectiveness')
    # Change object type to float and fill with 0 where there is full strings.
    df[change_type_columns] = df[change_type_columns].apply(pd.to_numeric, errors='coerce')
    df = df.drop(columns,axis=1)
    df = df.fillna(0)

    return df
