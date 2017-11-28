import pandas as pd
import numpy as np
import collections

def jurisdiction_country_data(df,min_jurisdction_count,min_country_count,condition):

    ## Input :
        # df : input dataframe.
        # min_jurisdction_count : minimum number of offshores in the tax haven to be considered.
        # min_country_count : minimum number of offshores created from the origin country to be considered.
        # Condition : 1 - include NaNs
        #             otherwise: remove NaNs

    ## Output :
        # Filtered Dataframe

    entities = df
    # Remove the columns not needed in extracting our data
    entities_c = df.drop(['former_name','company_type','incorporation_date', \
                          'inactivation_date','struck_off_date','dorm_date','status','ibcRUC','note','internal_id',\
                         'valid_until','jurisdiction','name','address','service_provider','sourceID','country_codes',\
                         'original_name'],axis=1)

    # If the condition is set to 1 then  fill the unknown values with Undefined Origin Country
    # so that we can count the total number of entities in a Jurisdiction regardless knowing
    # the origin country of the entity.
    # This is used to analyze the number of missing data we have, specifcally the data missing in the jurisdiction
    # column.
    if (condition == 1):
        entities_c['countries']=entities_c['countries'].fillna('Undefined Origin Country')

    # Grouping the dataframe by the origin countries and the jurisdiction [a.k.a the "Tax Haven countries"]
    # and getting the number of entities in each country in that jurisdiction.
    jurisdiction_country = entities_c.groupby(['jurisdiction_description','countries']).size()

    # Chaning it to a dataframe .
    jurisdiction_country = jurisdiction_country.to_frame()
    # Renaming the computed column to Count.
    jurisdiction_country = jurisdiction_country.rename(columns={0: 'Count'})
    # Calculating the number count of each jurisdiction.
    jurisdiction_count = collections.Counter(entities.loc[:,'jurisdiction_description'])
    # Filtering the jurisdiction to the threshold set.
    filter_jurisdictions = dict((k, v) for k, v in jurisdiction_count.items() if v < min_jurisdction_count)
    # List of jurisdiction names
    filter_jurisdictions_list = list(filter_jurisdictions.keys())
    # Appending the Undetermined since it is removed by the filter.
    filter_jurisdictions_list.append('Undetermined')
    # Filtering the countries to the threshold set.
    jurisdiction_country = jurisdiction_country.drop(filter_jurisdictions_list , level = 'jurisdiction_description')
    jurisdiction_country = jurisdiction_country.loc[jurisdiction_country['Count'] > min_country_count]

    return jurisdiction_country

def compute_countries_involved(total_jurisdiction_country,offshore_number):
    ## Input :
        # total_jurisdiction_country : dataframe that includes the connection between the
        # jurisdiction and country along with the count.
        # offshore_number : the minimum number of offshore accounts from a certain origin country.
    ## Output :
        # countries_involved : a list of the countries.
    # Summing the frequency of appearance of each country.
    total_jurisdiction_country = total_jurisdiction_country.reset_index()\
    .drop('jurisdiction_description',axis=1)\
    .groupby('countries').aggregate(np.sum)

    # Filtering the count less than the input threshold set.
    total_jurisdiction_country = total_jurisdiction_country.loc[total_jurisdiction_country['Count'] > offshore_number]
    countries_involved = total_jurisdiction_country.reset_index()['countries'].tolist()
    # Editing Taiwan
    index = countries_involved.index('Taiwan')
    countries_involved[index] = 'Taiwan '
    return countries_involved

def compute_countries_involved_data(index_2017,countries_involved):

    countries_involved_data = index_2017.loc[countries_involved]\
    .dropna(axis=0, how='all')\
    .sort_values('Score',ascending = False)
    countries_involved_data = countries_involved_data.drop(countries_involved_data.index[28])

    return countries_involved_data
