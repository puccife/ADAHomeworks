import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn
import json
import folium
import requests

from plotly.offline import init_notebook_mode, plot, iplot
import plotly.graph_objs as go
from plotly.graph_objs import *

def plot_cross_table(matrix):
    '''
    Function used to plot the cross table.
    Params:
        @matrix: crosstable
    '''
    matrix[matrix == 0.0] = np.nan
    fig = plt.figure(figsize=(10, 15))
    plt.clf()
    ax = fig.add_subplot(111)
    ax.set_aspect('auto')
    res = ax.matshow(matrix, cmap='YlOrRd')

    cb = fig.colorbar(res, fraction=0.046, pad=0.04)

    width, height = matrix.shape
    plt.xticks(range(height), matrix.columns.values, rotation=90)
    plt.ylabel('Origin country')
    plt.xlabel('Goal country')
    plt.yticks(range(width), matrix.index.values)

def addChoropleth(dataframe, map_, feature, legend_name, key, scale_color,json_data,object_):
    '''
    Add a cloropleth map to the specified map using specified dataframe and columns
    '''
    map_.choropleth(geo_data=json_data,
             data=dataframe,
             columns=[key, feature],
             key_on='feature.id',
             fill_color=scale_color,
             fill_opacity=0.5,
             line_opacity=0.2,
             highlight=True,
             legend_name=legend_name, topojson = object_)

def buildJsonAPI(url):
    '''
    Build json API of that can be used to match countries with there ID and other information
    '''
    restcountries = {}
    nametoid = {}
    response = requests.get(url)
    for json_country in response.json():
        try:
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



def plot_cross_table_plotly(matrix):  
    matrix[matrix == 0.0] = np.nan
    matrix_z = matrix.as_matrix()
    trace = go.Heatmap(z=matrix_z,
                      x=matrix.columns.values,
                      y=matrix.index.values,
                      colorscale = 'Reds')
    data=[trace]
    iplot(data, filename='basic-heatmap')
