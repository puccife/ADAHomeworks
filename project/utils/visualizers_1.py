import pandas as pd
import numpy as np
import collections
import seaborn as sns

from plotly.offline import init_notebook_mode, plot, iplot
import plotly.graph_objs as go
from plotly.graph_objs import *
init_notebook_mode(connected=True)

def visualize_specific_count(countries,jurisdiction_country,divide_by='Country'):
    ## Input :
        # countries : the list of countries to be visualized
        # jurisdiction_country : dataframe that includes the connection between the jursidiction and
        # country along with the count .
        # divide_by : variable used in visualization, referring to the column in the dataframe
    ## Output :
        # A visualization


    # Creating a new dataframe.
    collection_df = pd.DataFrame()

    # For each country included, compute the number of offshore accounts opened in the jurisdictions.
    for i,country in enumerate(countries):
        # Filter by country.
        country_count = jurisdiction_country.iloc[jurisdiction_country.index.get_level_values('countries') == country]
        # Resetting the index.
        country_count = country_count.reset_index()
        # Renaming the columns.
        country_count = country_count.rename(columns={'jurisdiction_description':'Jurisdictions','countries':'Country'})

        collection_df = collection_df.append(country_count)
    # Visualizing the data.
    g = sns.factorplot(x='Count',
                   y='Jurisdictions',
                   col=divide_by,
                   col_wrap=2,
                   data=collection_df,
                   kind='bar',
                   sharey=False,
                   sharex=False,
                   size=2.5,
                   aspect=3.5)

def visualize_country_count(total_jurisdiction_country):
    ## Input :
        # total_jurisdiction_country : dataframe that includes the connection between the
        # jurisdiction and country along with the count.
    ## Output :
        # A Visualization

    # Summing the frequency of the appearance of each country.
    total_jurisdiction_country = total_jurisdiction_country.reset_index()\
    .drop('jurisdiction_description',axis=1)\
    .groupby('countries').aggregate(np.sum)

    # Filtering the count less than 500.
    total_jurisdiction_country=total_jurisdiction_country.loc[total_jurisdiction_country['Count'] > 500]
    total_jurisdiction_country = total_jurisdiction_country.reset_index().sort_values('Count')
    # Visualizing the data.
    trace0 = go.Bar(
        x=total_jurisdiction_country['Count'],
        y=total_jurisdiction_country['countries'],
        marker=dict(
            color='rgba(50, 171, 96, 0.6)',
            line=dict(
                color='rgba(50, 171, 96, 1.0)',
                width=1),
        ),
        name='Entities registered',
        orientation='h',
    )
    fig = go.Figure(data = [trace0])
    iplot(fig)

def visualize_jurisdiction_count(total_jurisdiction_country):
    ## Input
        # total_jurisdiction_country : dataframe that includes the connection between the
        # jurisdiction and country along with the count.
    ## Output
        # A Visualization

    # Summing the frequency of the appearance of each jurisdiction.
    total_jurisdiction_country = total_jurisdiction_country.reset_index()\
    .drop('countries',axis=1)\
    .groupby('jurisdiction_description').aggregate(np.sum)

    # Filtering the count less than 500.
    total_jurisdiction_country=total_jurisdiction_country.loc[total_jurisdiction_country['Count'] > 500]
    total_jurisdiction_country = total_jurisdiction_country.reset_index()



    # Visualizing the data.
    g = sns.factorplot(x='Count',
                      y='jurisdiction_description',
                      data = total_jurisdiction_country,
                      kind='bar',
                      size = 9,
                      aspect = 1.9)

def visualize_jurisdiction_countly(total_jurisdiction_country):
    total_jurisdiction_country = total_jurisdiction_country.reset_index()\
    .drop('countries',axis=1)\
    .groupby('jurisdiction_description').aggregate(np.sum)
    total_jurisdiction_country=total_jurisdiction_country.loc[total_jurisdiction_country['Count'] > 500]
    total_jurisdiction_country = total_jurisdiction_country.reset_index().sort_values('Count')
    trace0 = go.Bar(
        x=total_jurisdiction_country['Count'],
        y=total_jurisdiction_country['jurisdiction_description'],
        marker=dict(
            color='rgba(50, 171, 96, 0.6)',
            line=dict(
                color='rgba(50, 171, 96, 1.0)',
                width=1),
        ),
        name='Try',
        orientation='h',
    )
    fig = go.Figure(data = [trace0])
    iplot(fig)

def visualize_jurisdiction_countly_mixed(jurisdiction_country, total_jurisdiction_country):
    jurisdiction_country = jurisdiction_country.reset_index()\
    .drop('countries',axis=1)\
    .groupby('jurisdiction_description').aggregate(np.sum)
    jurisdiction_country=jurisdiction_country.loc[jurisdiction_country['Count'] > 500]
    jurisdiction_country = jurisdiction_country.reset_index().sort_values('Count')

    total_jurisdiction_country = total_jurisdiction_country.reset_index()\
    .drop('countries',axis=1)\
    .groupby('jurisdiction_description').aggregate(np.sum)
    total_jurisdiction_country=total_jurisdiction_country.loc[total_jurisdiction_country['Count'] > 500]
    total_jurisdiction_country = total_jurisdiction_country.reset_index().sort_values('Count')

    trace1 = go.Bar(
        x=jurisdiction_country['Count'],
        y=jurisdiction_country['jurisdiction_description'],
        marker=dict(
            color='rgba(000, 000, 255, 0.6)',
            line=dict(
                color='rgba(50, 171, 96, 1.0)',
                width=1),
        ),
        name='Entities with registered origin',
        orientation='h',
    )

    trace0 = go.Bar(
        x=total_jurisdiction_country['Count'],
        y=total_jurisdiction_country['jurisdiction_description'],
        marker=dict(
            color='rgba(50, 171, 96, 0.6)',
            line=dict(
                color='rgba(50, 171, 96, 1.0)',
                width=1),
        ),
        name='Entities without registered origin',
        orientation='h',
    )
    fig = go.Figure(data = [trace0, trace1])
    iplot(fig)

def visualize_feature_correlation(df,columns):
    ## Input
        # df : dataframe containing the features of the index of the economic freedom.
        # columns : the columns we would like to find correlation between.
    ## Output
        # A Visualization.

    # Adding score to the set of input columns ( features ), as that is the main feature we want
    # to compare with.
    columns.append('Score')

    # Find the correlations of those features.
    correlations = df[columns].corr()

    print(correlations)

    matrix_z = correlations.as_matrix()
    trace = go.Heatmap(z=matrix_z,
                      x=correlations.columns.values,
                      y=correlations.index.values,
                      colorscale = 'Reds')
    data=[trace]
    iplot(data, filename='basic-heatmap')

def visualizing_index_data(economical_indexes,lead_countries,data,years):

    # Creating a multi-indexing
    idx = pd.MultiIndex.from_product([lead_countries,
                                  data,years],
                                 names=['Country', 'Data','Years'])
    # Column to add values in.
    col = ['Value']
    # Creating the dataframe to be used.
    df = pd.DataFrame(0, idx, col)

    # Manipulating the data to be used with seaborn.
    for country in lead_countries:
        eco_index = economical_indexes.loc[country]
        for column in data:
            data_list = list(eco_index[column])
            for i,year in enumerate(years):
                df.loc[(country,column,year)] = data_list[i]
    # Visualizing the data.
    g = sns.factorplot(x='Years', y='Value',hue='Country',
                 col='Data', data=df.reset_index(),col_wrap=2,sharey=False,
                   sharex=False,

                    size=3, aspect=3)
