import pandas as pd
import numpy as np
import collections
import seaborn as sns
import networkx as nx
from sklearn import preprocessing, decomposition
import igraph as ig

from plotly.offline import init_notebook_mode, plot, iplot
import plotly.graph_objs as go
from plotly.graph_objs import *
init_notebook_mode(connected=True)


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


def visualize_jurisdiction_countly(total_jurisdiction_country):
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
    total_jurisdiction_country = total_jurisdiction_country.reset_index().sort_values('Count')
    # Visualizing the data.
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
    ## Input
        # total_jurisdiction_country : dataframe that includes the total connections between the
        # jurisdiction and country along with the count.(includes missing data )
        # jurisdiction_country : dataframe that includes the total connection between the 
        # jurisdiction and country along with the count. ( doesn't include missing data )
    ## Output
        # A Visualization
    
    # Summing the frequency of the appearance of each jurisdiction.
    jurisdiction_country = jurisdiction_country.reset_index()\
    .drop('countries',axis=1)\
    .groupby('jurisdiction_description').aggregate(np.sum)
    # Filtering the count less than 500.
    jurisdiction_country=jurisdiction_country.loc[jurisdiction_country['Count'] > 500]
    jurisdiction_country = jurisdiction_country.reset_index().sort_values('Count')
    
    # Summing the frequency of the appearance of each jurisdiction.
    total_jurisdiction_country = total_jurisdiction_country.reset_index()\
    .drop('countries',axis=1)\
    .groupby('jurisdiction_description').aggregate(np.sum)
     # Filtering the count less than 500.
    total_jurisdiction_country=total_jurisdiction_country.loc[total_jurisdiction_country['Count'] > 500]
    total_jurisdiction_country = total_jurisdiction_country.reset_index().sort_values('Count')
    
    # Visualizing the data.
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
    columns.append('Count')
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
    
def visualize_specific_count_2(countries,jurisdiction_country):
    ## Input :
        # countries : the list of countries to be visualized
        # jurisdiction_country : dataframe that includes the connection between the jursidiction and
        # country along with the count .
    ## Output :
        # A visualization
    
    # Tax Havens involved
    tax_havens_plotly= ['Bahamas','British Virgin Islands','Panama','Seychelles','Niue','Samoa','British Anguilla','Hong Kong','Singapore']
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
    
    # Total number of entities in each country
    total_of_each_country = collection_df.groupby('Country').aggregate(np.sum)
    total_of_each_country = total_of_each_country.reset_index()


    values_listoflist_perc = []
    values_listoflist=[]

    # Calculate the percentage of the distribution of entities in each country. 
    for haven in tax_havens_plotly:
        values_list = []
        country_collection = collection_df[collection_df['Jurisdictions']==haven]
        for country in countries:
            try:
                count = country_collection[country_collection['Country']== country]['Count'].values[0]
                total_number = total_of_each_country[total_of_each_country['Country']== country]['Count'].values[0]
                count = count / total_number
                values_list.append(count)
            except IndexError:
                values_list.append(0)
        values_listoflist_perc.append(values_list)
        
    # Calculate the number of entities in each tax haven from each country.
    for haven in tax_havens_plotly:
        values_list = []
        country_collection = collection_df[collection_df['Jurisdictions']==haven]
        for country in countries:
            try:
                count = country_collection[country_collection['Country']== country]['Count'].values[0]
                values_list.append(count)
            except IndexError:
                values_list.append(0)
        values_listoflist.append(values_list)

    data = []
        # Stack the data
    for i,havens in enumerate(tax_havens_plotly):
        trace = go.Bar(
        y=countries,
        x=values_listoflist_perc[i],
        name=havens,
        orientation='h',
        text=values_listoflist[i],
        
        )
        data.append(trace)

    layout = go.Layout(
        barmode='stack',
        hovermode = "closest"
    )

    fig = go.Figure(data=data, layout=layout)
    iplot(fig, filename='stacked-bar')

    
def visualize_pca_top_countries(index_2017,jurisdiction_count):
    ## Input: 
        # index_2017 : Index of economical freedom at 2017
        # jurisdiction_count : The count of each country corresponding to a jurisdiction
    ## Output:
        # A visualization
        
    # Standardizing the features
    index_2017_pca = index_2017.drop(['Region','World Rank','Region Rank'],axis=1)
    index_2017_pca -= index_2017_pca.mean(axis=0)
    index_2017_pca /= index_2017_pca.std(axis=0)
    # Tax Haven countries
    haven_countries = ['Panama','Bahamas','Samoa','Seychelles','Mauritius']
    # Calculating the number of entities for each country
    country_count_ = jurisdiction_count.reset_index()\
    .drop('jurisdiction_description',axis=1)\
    .groupby('countries').aggregate(np.sum)
    index_2017_pca_countries = index_2017_pca.copy()
    # Sorting countries w.r.t number of entities.
    country_count_ = country_count_.sort_values('Count',ascending=False)
    # Adding the count of entities for each country
    count_pca = index_2017_pca_countries.join(country_count_).fillna(0).sort_values('Count',ascending=False)
    # Countries with at least 1 entity.
    count_pca= count_pca[count_pca['Count']>0]
    # Resetting the index
    count_pca_index= count_pca.reset_index()
    # Removing tax haven countries
    count_pca = count_pca_index[~count_pca_index['index'].isin(haven_countries)]
    count_pca = count_pca.set_index('index')
    # Top 12 countries
    label_1 = [0]*12 #grey
    # The rest of the countries
    label_2 = [1]*111 #orange
    label_1.extend(label_2)
    count_pca['label']=label_1
    # Passing the labels
    label = preprocessing.LabelEncoder().fit_transform(label_1)
    # Calculating PCA
    features_pca = decomposition.PCA(n_components=3).fit_transform(count_pca.drop(['Count','label'],axis=1))
    
    # 3D plot
    trace0 = go.Scatter3d(
    x = features_pca[:, 0],
    y = features_pca[:, 1],
    z = features_pca[:, 2],
    name = label,
    mode = 'markers',
    marker = dict(
        size = 10,
        color = label,
        line = dict(
            width = 2,
            color = 'rgb(0, 0, 0)'
        )        
    ),
    text = count_pca.index.values,
    hoverinfo='text'
    )
    data = [trace0]

    layout = dict(title = 'PCA on the Index of Economical Freedom based on clusters',
                  yaxis = dict(zeroline = False),
                  xaxis = dict(zeroline = False),
                  #zaxis = dict(zeroline = False)
                 )

    fig = dict(data=data, layout=layout)
    iplot(fig, filename='styled-scatter')
    
    
def visualize_pca_clusters(index_2017,cluster_country):
    
    ## Input: 
        # index_2017 : Index of economical freedom at 2017
        # cluster_country : Contains the countries and to which cluster they belong to
    ## Output:
        # A visualization
    
    
    # Extracting information needed for pca
    index_2017_pca = index_2017.drop(['Region','World Rank','Region Rank'],axis=1)
    # Normalizing the data
    index_2017_pca -= index_2017_pca.mean(axis=0)
    index_2017_pca /= index_2017_pca.std(axis=0)
    # Getting cluster number corresponding to each country
    cluster_by_country = cluster_country['cluster'].to_frame()
    # Extracting data about countries in the cluster .
    index_2017_pca_available_data = cluster_by_country.join(index_2017_pca).dropna()
    cluster_country_available_data = index_2017_pca_available_data['cluster'].to_frame()
    # Dropping the cluster column to not affect the PCA.
    index_2017_pca_available_data = index_2017_pca_available_data.drop('cluster',axis=1)
    # Passing the labels. 
    label = preprocessing.LabelEncoder().fit_transform(cluster_country_available_data['cluster'])
    # Calculating pca. 
    features_pca = decomposition.PCA(n_components=3).fit_transform(index_2017_pca_available_data)
    # 3D plot
    trace0 = go.Scatter3d(
    x = features_pca[:, 0],
    y = features_pca[:, 1],
    z = features_pca[:, 2],
    name = label,
    mode = 'markers',
    marker = dict(
        size = 10,
        color = label,
        line = dict(
            width = 2,
            color = 'rgb(0, 0, 0)'
        )        
    ),
    text = index_2017_pca_available_data.index.values,
    hoverinfo='text'
    )
    data = [trace0]

    layout = dict(title = 'PCA on the Index of Economical Freedom based on clusters',
                  yaxis = dict(zeroline = False),
                  xaxis = dict(zeroline = False),
                  #zaxis = dict(zeroline = False)
                 )

    fig = dict(data=data, layout=layout)
    iplot(fig, filename='styled-scatter')