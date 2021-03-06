import pandas as pd

from functools import reduce

from utils import dateparser
import pycountry

import requests

def process_countries_unstacked(entities, first_involved_countries, analisys_on='jurisdiction', from_year=1990, to_year=2017):
    """
    This function is used to process the Entities dataset and obtains one detailed dataset for
    each country that we want to analyse.
    :param entities: the dataset we want to process
    :param first_involved_countries: countries over which we want to conduct our analysis
    :param analisys_on: the feature over we want to conduct the analysis, the default value 
    is 'jurisdiction' since we want to analyse the behavior of each country in each tax
    haven jurisdiction.
    :param from_year: bottom bound for the years that we want to analyse
    :param to_year: upper bound for the years that we want to analyse
    :return: a list of parsed dataframes (one for each country).
    """
    most_involved_leak = []

    # Function runned over the specified countries
    for index, involved_country in enumerate(first_involved_countries):
        testing_entities = entities.copy()

        # Getting only the country interested in.
        involved_leak = testing_entities[testing_entities['Country'].isin([involved_country])].copy()

        # Parsing dates in a default datetime format.
        involved_leak = dateparser.parse_dates(involved_leak, from_year, to_year)

        # Getting the amount of incorporations - inactivations - strucks in the specific year.
        total_incorporation = involved_leak.groupby(['Country','jurisdiction_description', 'incorporation_date']).count()
        total_inactivation = involved_leak.groupby(['Country','jurisdiction_description', 'inactivation_date']).count()
        total_struck = involved_leak.groupby(['Country','jurisdiction_description', 'struck_off_date']).count()

        # Renaming columns
        incorporation = total_incorporation.reset_index().rename(columns={'incorporation_date': 'date', 'node_id': 'incorporations'}).set_index(['Country','jurisdiction_description','date'])
        inactivation = total_inactivation.reset_index().rename(columns={'inactivation_date': 'date', 'node_id': 'inactivations'}).set_index(['Country','jurisdiction_description','date'])
        struck = total_struck.reset_index().rename(columns={'struck_off_date': 'date', 'node_id': 'strucks'}).set_index(['Country','jurisdiction_description','date'])

        # Getting specific dataframes
        incorporation = incorporation.loc[:, ['incorporations']]
        inactivation = inactivation.loc[:, ['inactivations']]
        struck = struck.loc[:, ['strucks']]

        # Merging dataframes by columns.
        country_res = pd.merge(incorporation.reset_index(),
                                           inactivation.reset_index(), 
                                           on=['Country','jurisdiction_description', 'date'],
                                           how='outer').set_index(['Country','jurisdiction_description','date'])
        country_res = pd.merge(country_res.reset_index(),
                                           struck.reset_index(), 
                                           on=['Country','jurisdiction_description', 'date'],
                                           how='outer').set_index(['Country','jurisdiction_description','date'])
        involved = involved_leak.copy()
        # Computing the number of actives offshores for each year.
        for index, row in country_res.iterrows():
            number_of_offshores = involved[
                ((involved['inactivation_date'] > int(index[2])) | 
                (pd.isnull(involved['inactivation_date']))) &
                (involved['incorporation_date'] <= int(index[2])) & 
                (involved['Country'] == index[0]) &
                (involved['jurisdiction_description'] == index[1])].count()['node_id'] 
            country_res.loc[index, 'active offshores'] = number_of_offshores 

        # Getting the interesting columns
        country_result = country_res.loc[:, ['incorporations','inactivations','active offshores','strucks']]
        country_result = country_result.reset_index()
        country_result["date"] = country_result["date"].astype(int)
        country_result = country_result.rename(columns={'jurisdiction_description':'jurisdiction'})
        most_involved_leak.append(country_result.fillna(0))
    return most_involved_leak

def process_countries(entities, first_involved_countries, analisys_on='jurisdiction', from_year=1990, to_year=2017):
    """
    This function is used to process the Entities dataset and obtains one detailed dataset for
    each country that we want to analyse.
    :param entities: the dataset we want to process
    :param first_involved_countries: countries over which we want to conduct our analysis
    :param analisys_on: the feature over we want to conduct the analysis, the default value 
    is 'jurisdiction' since we want to analyse the behavior of each country in each tax
    haven jurisdiction.
    :param from_year: bottom bound for the years that we want to analyse
    :param to_year: upper bound for the years that we want to analyse
    :return: a list of parsed dataframes (one for each country).
    """
    most_involved_leak = []

    # Function runned over the specified countries
    for index, involved_country in enumerate(first_involved_countries):
        testing_entities = entities.copy()

        # Getting only the country interested in.
        involved_leak = testing_entities[testing_entities['Country'].isin([involved_country])].copy()

        # Parsing dates in a default datetime format.
        involved_leak = dateparser.parse_dates(involved_leak, from_year, to_year)

        # Getting the amount of incorporations - inactivations - strucks in the specific year.
        total_incorporation = involved_leak.groupby(['Country','jurisdiction_description', 'incorporation_date']).count()
        total_inactivation = involved_leak.groupby(['Country','jurisdiction_description', 'inactivation_date']).count()
        total_struck = involved_leak.groupby(['Country','jurisdiction_description', 'struck_off_date']).count()

        # Renaming columns
        incorporation = total_incorporation.reset_index().rename(columns={'incorporation_date': 'date', 'node_id': 'incorporations'}).set_index(['Country','jurisdiction_description','date'])
        inactivation = total_inactivation.reset_index().rename(columns={'inactivation_date': 'date', 'node_id': 'inactivations'}).set_index(['Country','jurisdiction_description','date'])
        struck = total_struck.reset_index().rename(columns={'struck_off_date': 'date', 'node_id': 'strucks'}).set_index(['Country','jurisdiction_description','date'])

        # Getting specific dataframes
        incorporation = incorporation.loc[:, ['incorporations']]
        inactivation = inactivation.loc[:, ['inactivations']]
        struck = struck.loc[:, ['strucks']]

        # Merging dataframes by columns.
        country_res = pd.merge(incorporation.reset_index(),
                                           inactivation.reset_index(), 
                                           on=['Country','jurisdiction_description', 'date'],
                                           how='outer').set_index(['Country','jurisdiction_description','date'])
        country_res = pd.merge(country_res.reset_index(),
                                           struck.reset_index(), 
                                           on=['Country','jurisdiction_description', 'date'],
                                           how='outer').set_index(['Country','jurisdiction_description','date'])
        involved = involved_leak.copy()
        # Computing the number of actives offshores for each year.
        for index, row in country_res.iterrows():
            number_of_offshores = involved[
                ((involved['inactivation_date'] > int(index[2])) | 
                (pd.isnull(involved['inactivation_date']))) &
                (involved['incorporation_date'] <= int(index[2])) & 
                (involved['Country'] == index[0]) &
                (involved['jurisdiction_description'] == index[1])].count()['node_id'] 
            country_res.loc[index, 'active offshores'] = number_of_offshores 

        # Getting the interesting columns
        country_result = country_res.loc[:, ['incorporations','inactivations','active offshores','strucks']]
        country_result = country_result.reset_index()

        # Setting index in all the columns excepts for OFFSHORES and ACTIONS
        country_result = country_result.set_index(['Country','jurisdiction_description','date'])

        # Stacking columns on actions and offshores.
        country_result = pd.DataFrame(country_result.stack())
        country_result = country_result.reset_index()

        # Renaming columns to meaningful names
        country_result = country_result.rename(columns={'level_3': 'action', 0: 'offshores', 'jurisdiction_description':'jurisdiction'})

        # Parsing date year to int (float before)
        country_result["date"] = country_result["date"].astype(int)
        most_involved_leak.append(country_result.set_index(analisys_on))
    return most_involved_leak


def process_countries_with_code(entities, first_involved_countries, analisys_on='jurisdiction', from_year=1990, to_year=2017, feature='incorporations'):
    """
    This function is used to process the Entities dataset and obtains one detailed dataset for
    each country that we want to analyse.
    :param entities: the dataset we want to process
    :param first_involved_countries: countries over which we want to conduct our analysis
    :param analisys_on: the feature over we want to conduct the analysis, the default value 
    is 'jurisdiction' since we want to analyse the behavior of each country in each tax
    haven jurisdiction.
    :param from_year: bottom bound for the years that we want to analyse
    :param to_year: upper bound for the years that we want to analyse
    :return: a list of parsed dataframes (one for each country) where each country is mapped to its
    ISO 3166-1 numeric code.
    """
    most_involved_leak = []
    for index, involved_country in enumerate(first_involved_countries):
        testing_entities = entities.copy()
        # Getting only the country interested in.
        involved_leak = testing_entities[testing_entities['Country'].isin([involved_country])].copy()
        # Parsing dates in a default datetime format.
        involved_leak = dateparser.parse_dates(involved_leak, from_year, to_year)
        # Getting the amount of incorporations - inactivations - strucks in the specific year.
        total_incorporation = involved_leak.groupby(['Country','jurisdiction', 'incorporation_date']).count()
        total_inactivation = involved_leak.groupby(['Country','jurisdiction', 'inactivation_date']).count()
        total_struck = involved_leak.groupby(['Country','jurisdiction', 'struck_off_date']).count()
        # Renaming columns
        incorporation = total_incorporation.reset_index().rename(columns={'incorporation_date': 'date', 'node_id': 'incorporations'}).set_index(['Country','jurisdiction','date'])
        inactivation = total_inactivation.reset_index().rename(columns={'inactivation_date': 'date', 'node_id': 'inactivations'}).set_index(['Country','jurisdiction','date'])
        struck = total_struck.reset_index().rename(columns={'struck_off_date': 'date', 'node_id': 'strucks'}).set_index(['Country','jurisdiction','date'])
        # Getting specific dataframes
        incorporation = incorporation.loc[:, ['incorporations']]
        inactivation = inactivation.loc[:, ['inactivations']]
        struck = struck.loc[:, ['strucks']]
        # Merging dataframes by columns.
        country_res = pd.merge(incorporation.reset_index(),
                                           inactivation.reset_index(), 
                                           on=['Country','jurisdiction', 'date'],
                                           how='outer').set_index(['Country','jurisdiction','date'])
        country_res = pd.merge(country_res.reset_index(),
                                           struck.reset_index(), 
                                           on=['Country','jurisdiction', 'date'],
                                           how='outer').set_index(['Country','jurisdiction','date'])
        involved = involved_leak.copy()
        # Computing the number of actives offshores for each year.
        for index, row in country_res.iterrows():
            number_of_offshores = involved[
                ((involved['inactivation_date'] > int(index[2])) | 
                (pd.isnull(involved['inactivation_date']))) &
                (involved['incorporation_date'] <= int(index[2])) & 
                (involved['Country'] == index[0]) &
                (involved['jurisdiction'] == index[1])].count()['node_id']             
            country_res.loc[index, 'active offshores'] = number_of_offshores 
        # Getting the interesting columns
        country_result = country_res.loc[:, ['incorporations','inactivations','active offshores','strucks']]
        country_result = country_result.reset_index()

        # Parsing date years into integers (float before)
        country_result["date"] = country_result["date"].astype(int)

        # Setting new index
        country_result = country_result.set_index(['Country','jurisdiction','date'])
        most_involved_leak.append(country_result)
        print("Country done:" + involved_country)

    # For each country add columns with their ISO 3166-1 numeric code - used to match the map
    collection = []
    for f_ in most_involved_leak:
        f_ = pd.DataFrame(f_[feature])
        collection.append(f_.reset_index())
    countries_frame = reduce(lambda x, y: pd.merge(x, y, on = ['Country', 'jurisdiction', 'date',feature], how='outer'), collection)
    countries_frame = countries_frame.set_index(['Country','jurisdiction','date'])
    countries_frame = countries_frame.unstack(level=[2]).reset_index()
    countries_frame.columns = countries_frame.columns.droplevel(0)
    countries_frame.columns.values[0] = 'Country' 
    countries_frame.columns.values[1] = 'jurisdiction'
    countries_frame = countries_frame[(countries_frame['jurisdiction'] != 'Undetermined')]
    for id_, row in countries_frame.iterrows():
        try:
            cou = row['Country']
            if(cou=='Russia'):
                cou = int('643')
            elif (cou == 'Isle Of Man'):
                cou = int('833')
            elif (cou == 'British Virgin Islands'):
                cou = int('92')
            else:
                cou = int(pycountry.countries.get(name=cou).numeric) #library used to get codes
            jur = row['jurisdiction']
            if(jur == 'British Anguilla'):
                jur = int('660')
            elif (jur == 'British Virgin Islands'):
                jur = int('92')
            elif (jur == 'Nevada'):
                jur = int('840')
            elif (jur == 'Wyoming'):
                jur = int('840')
            elif (jur == 'Ras Al Khaimah'):
                jur = int('784')
            elif (jur == 'Isle Of Man'):
                jur = int('833')
            elif (jur == 'United States Of America'):
                jur = int('840')
            elif (jur == 'Dubai'):
                jur = int('784')
            else:
                jur = int(pycountry.countries.get(name=jur).numeric)
        except:
            print(row['Country'])
            print(row['jurisdiction'])
        countries_frame.loc[id_, 'Country_name'] = row['Country']
        countries_frame.loc[id_, 'Country'] = cou
        countries_frame.loc[id_, 'jurisdiction'] = jur

    # returning list of new parsed dataframes
    return countries_frame


def add_details(actives_flows_by_country2, restcountries):
    """
    This function is used to add details to a given dataframe using a json build with a get request of
    a RESTful API.
    :param actives_flows_by_country2: dataframe where to add details
    :param restcountries: the json containing informations about countries.
    :return: a new updated dataframe
    """
    actives_flows_by_country = actives_flows_by_country2.copy()
    # Adding details to each country - alpha3code and their full name.
    for i, row in actives_flows_by_country.iterrows():
        actives_flows_by_country.loc[i, 'CODE'] = restcountries[int(row['Country'])]['alpha3Code']
        actives_flows_by_country.loc[i, 'Name'] = restcountries[int(row['Country'])]['name']
    return actives_flows_by_country


def parse_countries(actives_flows):
    """
    This function is used to parse the dataframe before using it
    :param actives_flows: the dataframe to use
    :return: the parsed dataframe
    """
    cols=[i for i in actives_flows.columns if i not in ["Country_name"]]
    for col in cols:
        actives_flows[col]=pd.to_numeric(actives_flows[col],errors='coerce')
    return actives_flows


def build_json_from_api(url):
    """
    This method is used to perform a get request to a RESTful API service. With this call is possible
    to store informations about each country. In particular we will store name - latlng - codes
    (but there are a plenty more available) of each country based on their ISO 3166-1 numeric code.
    :param url: url for the API request.
    :return: 
    - a json object that maps the ISO 3166-1 numeric code to values for each country. 
    - a json object that maps the name of each country to its numeric code.
    """
    restcountries = {}
    nametoid = {}
    # making request to specific url
    response = requests.get(url)
    for json_country in response.json():
        # For each request - catching exceptions
        try:
            # Saving useful information in 2 different json objects.
            code = int(json_country['numericCode'])
            restcountries[code] = {}
            restcountries[code]['name'] = json_country['name']
            restcountries[code]['latlng'] = json_country['latlng']
            restcountries[code]['name'] = json_country['name']
            restcountries[code]['alpha3Code'] = json_country['alpha3Code']
            nametoid[json_country['name']] = code
        except:
            print(json_country['name'] + " has problem with numeric code " + str(json_country['numericCode']))
    return restcountries, nametoid
