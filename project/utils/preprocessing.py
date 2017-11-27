import pandas as pd
import numpy as np

from functools import reduce

from utils import dateparser
import pycountry

def process_countries(entities, first_involved_countries, analisys_on='jurisdiction', from_year=1990, to_year=2017):
    most_involved_leak = []
    for index, involved_country in enumerate(first_involved_countries):
        testing_entities = entities.copy()
        involved_leak = testing_entities[testing_entities['Country'].isin([involved_country])].copy()
        involved_leak = dateparser.parse_dates(involved_leak, from_year, to_year)
        total_incorporation = involved_leak.groupby(['Country','jurisdiction_description', 'incorporation_date']).count()
        total_inactivation = involved_leak.groupby(['Country','jurisdiction_description', 'inactivation_date']).count()
        total_struck = involved_leak.groupby(['Country','jurisdiction_description', 'struck_off_date']).count()
        incorporation = total_incorporation.reset_index().rename(columns={'incorporation_date': 'date', 'node_id': 'incorporations'}).set_index(['Country','jurisdiction_description','date'])
        inactivation = total_inactivation.reset_index().rename(columns={'inactivation_date': 'date', 'node_id': 'inactivations'}).set_index(['Country','jurisdiction_description','date'])
        struck = total_struck.reset_index().rename(columns={'struck_off_date': 'date', 'node_id': 'strucks'}).set_index(['Country','jurisdiction_description','date'])
        incorporation = incorporation.loc[:, ['incorporations']]
        inactivation = inactivation.loc[:, ['inactivations']]
        struck = struck.loc[:, ['strucks']]
        country_res = pd.merge(incorporation.reset_index(),
                                           inactivation.reset_index(), 
                                           on=['Country','jurisdiction_description', 'date'],
                                           how='outer').set_index(['Country','jurisdiction_description','date'])
        country_res = pd.merge(country_res.reset_index(),
                                           struck.reset_index(), 
                                           on=['Country','jurisdiction_description', 'date'],
                                           how='outer').set_index(['Country','jurisdiction_description','date'])
        involved = involved_leak.copy()
        for index, row in country_res.iterrows():
            number_of_offshores = involved[
                ((involved['inactivation_date'] > int(index[2])) | 
                (pd.isnull(involved['inactivation_date']))) &
                (involved['incorporation_date'] <= int(index[2])) & 
                (involved['Country'] == index[0]) &
                (involved['jurisdiction_description'] == index[1])].count()['node_id'] 
            country_res.loc[index, 'active offshores'] = number_of_offshores 
        country_result = country_res.loc[:, ['incorporations','inactivations','active offshores','strucks']]
        country_result = country_result.reset_index()
        country_result = country_result.set_index(['Country','jurisdiction_description','date'])
        country_result = pd.DataFrame(country_result.stack())
        country_result = country_result.reset_index()
        country_result = country_result.rename(columns={'level_3': 'action', 0: 'offshores', 'jurisdiction_description':'jurisdiction'})
        country_result["date"] = country_result["date"].astype(int)
        most_involved_leak.append(country_result.set_index(analisys_on))
    return most_involved_leak

def process_countries_with_code(entities, first_involved_countries, analisys_on='jurisdiction', from_year=1990, to_year=2017, feature='incorporations'):
    most_involved_leak = []
    for index, involved_country in enumerate(first_involved_countries):
        testing_entities = entities.copy()
        involved_leak = testing_entities[testing_entities['Country'].isin([involved_country])].copy()
        involved_leak = dateparser.parse_dates(involved_leak, from_year, to_year)
        total_incorporation = involved_leak.groupby(['Country','jurisdiction', 'incorporation_date']).count()
        total_inactivation = involved_leak.groupby(['Country','jurisdiction', 'inactivation_date']).count()
        total_struck = involved_leak.groupby(['Country','jurisdiction', 'struck_off_date']).count()
        incorporation = total_incorporation.reset_index().rename(columns={'incorporation_date': 'date', 'node_id': 'incorporations'}).set_index(['Country','jurisdiction','date'])
        inactivation = total_inactivation.reset_index().rename(columns={'inactivation_date': 'date', 'node_id': 'inactivations'}).set_index(['Country','jurisdiction','date'])
        struck = total_struck.reset_index().rename(columns={'struck_off_date': 'date', 'node_id': 'strucks'}).set_index(['Country','jurisdiction','date'])
        incorporation = incorporation.loc[:, ['incorporations']]
        inactivation = inactivation.loc[:, ['inactivations']]
        struck = struck.loc[:, ['strucks']]
        country_res = pd.merge(incorporation.reset_index(),
                                           inactivation.reset_index(), 
                                           on=['Country','jurisdiction', 'date'],
                                           how='outer').set_index(['Country','jurisdiction','date'])
        country_res = pd.merge(country_res.reset_index(),
                                           struck.reset_index(), 
                                           on=['Country','jurisdiction', 'date'],
                                           how='outer').set_index(['Country','jurisdiction','date'])
        involved = involved_leak.copy()
        for index, row in country_res.iterrows():
            number_of_offshores = involved[
                ((involved['inactivation_date'] > int(index[2])) | 
                (pd.isnull(involved['inactivation_date']))) &
                (involved['incorporation_date'] <= int(index[2])) & 
                (involved['Country'] == index[0]) &
                (involved['jurisdiction'] == index[1])].count()['node_id']             
            country_res.loc[index, 'active offshores'] = number_of_offshores 
        country_result = country_res.loc[:, ['incorporations','inactivations','active offshores','strucks']]
        country_result = country_result.reset_index()
        country_result["date"] = country_result["date"].astype(int)
        country_result = country_result.set_index(['Country','jurisdiction','date'])
        most_involved_leak.append(country_result)
        print("Country done:" + involved_country)
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
                cou = int(pycountry.countries.get(name=cou).numeric)

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
        
    return countries_frame