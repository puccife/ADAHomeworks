import pandas as pd
import numpy as np
import collections
import seaborn as sns

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
    total_jurisdiction_country = total_jurisdiction_country.reset_index()
    # Visualizing the data.
    g = sns.factorplot(x='Count',
                      y='countries',
                      data = total_jurisdiction_country,
                      kind='bar',
                      size = 15,
                      aspect = 1)

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

    # Visualizing the data.
    sns.heatmap(correlations,
        xticklabels=correlations.columns,
        yticklabels=correlations.columns,
        vmin=0,
        cmap="YlGnBu",
        annot = True)

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
