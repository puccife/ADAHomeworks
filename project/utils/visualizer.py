import pandas as pd
import seaborn as sns
import numpy as np

from utils import preprocessing

from plotly.offline import init_notebook_mode, plot, iplot
import plotly.graph_objs as go
from plotly.graph_objs import *
init_notebook_mode(connected=True)


def visualize_countries_situation(most_involved_leak, divide_by='Country', selected_jurisdiction=None):
    """
    This function is used to display the country situation. If a jurisdiction is specified, then the
    analysis is focused on that jurisdiction - otherwise it's based on all the jurisdictions involved.
    :param most_involved_leak: dataframe for all the most involved countries.
    :param divide_by: plot divide by. Default 'Country' since it's used to display investments details
    and differences between countries.
    countries.
    :param selected_jurisdiction: if None the analysis is based on all the involved jurisdictions,
    otherwise it's based on the specific jurisdiction.
    """
    if(selected_jurisdiction != None):
        leaks = []
        for country in most_involved_leak:
            leak = country.copy()
            leak = leak.reset_index()
            leak = leak[leak['jurisdiction'] == selected_jurisdiction]
            leaks.append(leak)
    else:
        leaks = most_involved_leak

    # For each country this function displays a seaborn factorplot.
    for index_, country_result in enumerate(leaks):
        sns.factorplot(x='date',
                   y='offshores',
                   row=divide_by,
                   data=country_result,
                   hue='action',
                   kind='bar',
                   sharey=True,
                   sharex=False,
                   size=4,
                   aspect=4
                   )


def visualize_flow_by_country(country, year, feat):
    """
    This function is used to display an interactive map with the interactive widget. It displays the
    flows from Country to jurisdiction of inactivations - incorporations and actives account in each
    jurisdiciton.
    :param country: selected country to analyse the flow
    :param year: the specific year in which is computed the analysis
    :param feat: the feature over which is computed the analysis (inactivations - incorporations or actives offshores)
    """

    # Reading csv files and obtaining JSON with get request via RESTful API
    url = 'https://restcountries.eu/rest/v2/'
    actives_path = r'csv/cash_flows_'+feat+'.csv'
    restcountries, nametoid = preprocessing.build_json_from_api(url)
    actives_flows = pd.read_csv(actives_path,low_memory=False)

    # Parsing the original dataframe
    actives_flows = preprocessing.parse_countries(actives_flows)
    actives_flows_by_country = actives_flows.groupby('Country').sum().reset_index()

    # Adding details obtained via GET() request
    actives_flows_by_country = preprocessing.add_details(actives_flows_by_country, restcountries)

    # Filtering only the analysed country
    country_df = actives_flows[actives_flows['Country'] == nametoid[country]]
    total_offshores = 0
    labels = []
    values = []
    flows_path = []
    max_value = country_df[str(year)].max()

    # Displaying arcs that start from the filtered country to all the involved jurisdiction in the
    # selected year.
    for i, row in country_df.iterrows():

        # Checking if values are not null.
        if not pd.isnull(row['Country']) and not pd.isnull(row['jurisdiction']) and not pd.isnull(row[str(year)]):
            coord = [restcountries[int(row['Country'])]['latlng'], restcountries[int(row['jurisdiction'])]['latlng']]
            total_offshores = total_offshores + row[str(year)]
            labels.append(restcountries[int(row['jurisdiction'])]['name'])
            values.append(row[str(year)])

            # Drawing arc with custom style
            # Opacity of arcs is based on their strength.
            flows_path.append(
                    dict(
                        type = 'scattergeo',
                        lon = [ coord[0][1], coord[1][1] ],
                        lat = [ coord[0][0], coord[1][0] ],
                        mode = 'lines',
                        line = dict(
                            width = 1,
                            color = 'red',
                        ),
                        opacity = max(float(row[str(year)] / max_value), 0.3),
                        showlegend = False,
                        name=restcountries[int(row['jurisdiction'])]['name'],
                    )
                )

    # Drawing choropleth and arcs on the map layout.
    ok_data = __get_data(actives_flows_by_country, year)
    fig = dict( data=flows_path + ok_data, layout=__get_layout(year) )

    # Inline plotting figure
    iplot( fig, validate=False, filename='d3-world-map.html')

    # Drawing pie chart showing the composition and strength of the connections (arcs).
    trace = go.Pie(labels=labels,
                   values=values,
                  textfont=dict(size=20),)

    # Inline plotting chart
    iplot([trace], filename='basic_pie_chart.html')
    print("Total offshores in " + str(year) + " = " + str(total_offshores))


def __get_data(dataframe, year):
    """
    ! private function. This function is used to parse and get data json object based on
    a specific year dataframe.
    :param dataframe: the dataframe to analyse
    :param year: the year to use to display details on the map
    :return: the a json object representing the details of one country -> jurisdiction in one
    specific year passed as argument.
    """

    # Wrapping the values of the filter dataframe (per year) into a json file.
    data = [ dict(
        type = 'choropleth',
        locations = dataframe['CODE'],
        z = dataframe[str(year)],
        text = dataframe['Name'],
        colorscale = [[0,"#b10026"],[0.35,"#e31a1c"],[0.5,"#fc4e2a"],\
            [0.6,"#fc4e2a"],[0.7,"#fc4e2a"],[1,"#ffeda0"]],
        autocolorscale = False,
        reversescale = True,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(
            autotick = False,
            tickprefix = '$',
            title = 'Active offshores per country<br>In ' + str(year)),
      ) ]
    return data


def __get_layout(year):
    """
    ! private function. This function is created to obtain the layout of the choropleth map
    :return: the layout of the choropleth map.
    """
    sliders_dict = {
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 20},
            'prefix': 'Year:',
            'visible': True,
            'xanchor': 'right'
        },
        'transition': {'duration': 300, 'easing': 'cubic-in-out'},
        'pad': {'b': 10, 't': 50},
        'len': 0.9,
        'x': 0.1,
        'y': 0,
        'steps': []
    }
    slider_step = {'args': [
        [year],
        {'frame': {'duration': 300, 'redraw': True},
         'mode': 'immediate',
       'transition': {'duration': 300}}
     ],
     'label': year,
     'method': 'animate'}
    sliders_dict['steps'] = slider_step

    # Getting layout as json object for the map.
    layout = dict(
        title = 'Active offshores per country <br> <br> Source:\
                <a href="https://www.icij.org/">\
                International Consortium of Investigative Journalists</a>',
        geo = dict(
            projection = dict(
                type = 'Mercator'
            ),
            resolution='50',
        ),
        sliders=sliders_dict
    )
    return layout

def visualize_slider_jurisdiction(countries_frame2, label):
    jurisd = pd.concat(countries_frame2)
    jurisd = jurisd.reset_index() 
    jurisdictions = jurisd.jurisdiction.unique()
    countries_frame = []
    for jur in jurisdictions:
        countries_frame.append(jurisd[jurisd['jurisdiction'] == jur])
    for i, es_country in enumerate(countries_frame):
        test = countries_frame[i][countries_frame[i]['action'] == label].copy()
        test = test.sort_values('date')
        test = test.set_index(['date'])
        juri = test.jurisdiction.unique()
        countries = test.Country.unique()
        traces = []
        for country in countries:
            tmp_df = test[test['Country'] == country]
            tmp_trace = go.Scatter(x=tmp_df.index,
                                  y=tmp_df.offshores,
                                  name=country)
            traces.append(tmp_trace)
        data = go.Data(traces)
        layout = dict(
            title=juri[0] + " " + label + ' account distribution by Country with time series',
            xaxis=dict(
                rangeslider=dict(),
                type='date'
            )
        )

        fig = dict(data=data, layout=layout)
        iplot(fig)

def visualize_slider_country(countries_frame, label):
    for i, es_country in enumerate(countries_frame):
        test = countries_frame[i][countries_frame[i]['action'] == label].copy()
        test = test.reset_index()
        test = test.sort_values('date')
        test = test.set_index(['date'])
        jurisdictions = test.jurisdiction.unique()
        country = test.Country.unique()
        traces = []
        for jurisdiction in jurisdictions:
            tmp_df = test[test['jurisdiction'] == jurisdiction]
            tmp_trace = go.Scatter(x=tmp_df.index,
                                  y=tmp_df.offshores,
                                  name=jurisdiction)
            traces.append(tmp_trace)
        data = go.Data(traces)
        layout = dict(
            title=country[0] + " " + label + ' account distribution by jurisdiction with time series',
            xaxis=dict(
                rangeslider=dict(),
                type='date'
            )
        )

        fig = dict(data=data, layout=layout)
        iplot(fig)

def visualize_time_series(countries_frame):
    for time_frame in countries_frame:
        c = time_frame['Country'][0]
        dataset = time_frame.copy().reset_index()
        years_from_col = set(dataset['date'])
        years_ints = sorted(list(years_from_col))
        years = [str(year) for year in years_ints]
        years = years[:-1]
        continents = []
        for continent in dataset['jurisdiction']:
            if continent not in continents: 
                continents.append(continent)
        # make figure
        figure = {
            'data': [],
            'layout': dict(title = '<b>'+ c +' offshores account by jurisdictions</b>'),
            'frames': []
        }

        # fill in most of layout

        #figure['layout']['xaxis'] = {'range':[int(min(years)) - 3, int(max(years)) + 3],'title': 'Jurisdictions'}
        figure['layout']['xaxis'] = {'range':[-100, max(dataset['inactivations']) + 500],'title': 'Inactivations'}
        figure['layout']['yaxis'] = {'range':[-100, max(dataset['incorporations']) + 500],'title': 'Incorporations'}
        figure['layout']['hovermode'] = 'compare'
        figure['layout']['sliders'] = {
            'args': [
                'transition', {
                    'duration': 400,
                    'easing': 'cubic-in-out'
                }
            ],
            'initialValue': '1980',
            'plotlycommand': 'animate',
            'values': years,
            'visible': True
        }
        figure['layout']['updatemenus'] = [
            {
                'buttons': [
                    {
                        'args': [None, {'frame': {'duration': 500, 'redraw': False},
                                 'fromcurrent': True, 'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}],
                        'label': 'Play',
                        'method': 'animate'
                    },
                    {
                        'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate',
                        'transition': {'duration': 0}}],
                        'label': 'Pause',
                        'method': 'animate'
                    }
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 87},
                'showactive': False,
                'type': 'buttons',
                'x': 0.1,
                'xanchor': 'right',
                'y': 0,
                'yanchor': 'top'
            }
        ]

        sliders_dict = {
            'active': 0,
            'yanchor': 'top',
            'xanchor': 'left',
            'currentvalue': {
                'font': {'size': 20},
                'prefix': 'Year:',
                'visible': True,
                'xanchor': 'right'
            },
            'transition': {'duration': 300, 'easing': 'cubic-in-out'},
            'pad': {'b': 10, 't': 50},
            'len': 0.9,
            'x': 0.1,
            'y': 0,
            'steps': []
        }

        # make data
        year = 1980
        for continent in continents:
            dataset_by_year = dataset[dataset['date'] == year]
            dataset_by_year_and_cont = dataset_by_year[dataset_by_year['jurisdiction'] == continent]

            data_dict = go.Scatter(
                    x= list(dataset_by_year_and_cont['inactivations']),
                    y= list(dataset_by_year_and_cont['incorporations']),
                    mode= 'markers',
                    text= list(dataset_by_year_and_cont['jurisdiction']),
                    marker = dict (
                        sizemode= 'area',
                        size= list(dataset_by_year_and_cont['active offshores'])
                    ),
                    name= continent
                )
            figure['data'].append(data_dict)

        # make frames
        for year in years:
            frame = {'data': [], 'name': str(year)}
            for continent in continents:
                dataset_by_year = dataset[dataset['date'] == int(year)]
                dataset_by_year_and_cont = dataset_by_year[dataset_by_year['jurisdiction'] == continent]
                data_dict = go.Scatter(
                    x= list(dataset_by_year_and_cont['inactivations']),
                    y= list(dataset_by_year_and_cont['incorporations']),
                    mode= 'markers',
                    text= list(dataset_by_year_and_cont['jurisdiction']),
                    marker = dict (
                        sizemode= 'area',
                        size= list(dataset_by_year_and_cont['active offshores'])
                    ),
                    name= continent
                )
                frame['data'].append(data_dict)

            figure['frames'].append(frame)
            slider_step = {'args': [
                [year],
                {'frame': {'duration': 300, 'redraw': True},
                 'mode': 'immediate',
               'transition': {'duration': 300}}
             ],
             'label': year,
             'method': 'animate'}
            sliders_dict['steps'].append(slider_step)


        figure['layout']['sliders'] = [sliders_dict]
        iplot(figure)

def visualize_time_series2(countries_frame2):
    jurisd = pd.concat(countries_frame2)
    jurisd = jurisd.reset_index() 
    jurisdictions = jurisd.jurisdiction.unique()
    countries_frame = []
    for jur in jurisdictions:
        countries_frame.append(jurisd[jurisd['jurisdiction'] == jur])
    for time_frame in countries_frame: 
        dataset = time_frame.copy().reset_index()
        c = dataset['jurisdiction'][0]
        years_from_col = set(dataset['date'])
        years_ints = sorted(list(years_from_col))
        years = [str(year) for year in years_ints]
        years = years[:-1]
        continents = []
        for continent in dataset['Country']:
            if continent not in continents: 
                continents.append(continent)
        # make figure
        figure = {
            'data': [],
            'layout': dict(title = '<b>'+ c +' offshores account by Country</b>'),
            'frames': []
        }

        # fill in most of layout

        #figure['layout']['xaxis'] = {'range':[int(min(years)) - 3, int(max(years)) + 3],'title': 'Jurisdictions'}
        figure['layout']['xaxis'] = {'range':[-50, max(dataset['inactivations']) + 50],'title': 'Inactivations'}
        figure['layout']['yaxis'] = {'range':[-50, max(dataset['incorporations']) + 50],'title': 'Incorporations'}
        figure['layout']['hovermode'] = 'compare'
        figure['layout']['sliders'] = {
            'args': [
                'transition', {
                    'duration': 400,
                    'easing': 'cubic-in-out'
                }
            ],
            'initialValue': '1980',
            'plotlycommand': 'animate',
            'values': years,
            'visible': True
        }
        figure['layout']['updatemenus'] = [
            {
                'buttons': [
                    {
                        'args': [None, {'frame': {'duration': 500, 'redraw': False},
                                 'fromcurrent': True, 'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}],
                        'label': 'Play',
                        'method': 'animate'
                    },
                    {
                        'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate',
                        'transition': {'duration': 0}}],
                        'label': 'Pause',
                        'method': 'animate'
                    }
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 87},
                'showactive': False,
                'type': 'buttons',
                'x': 0.1,
                'xanchor': 'right',
                'y': 0,
                'yanchor': 'top'
            }
        ]

        sliders_dict = {
            'active': 0,
            'yanchor': 'top',
            'xanchor': 'left',
            'currentvalue': {
                'font': {'size': 20},
                'prefix': 'Year:',
                'visible': True,
                'xanchor': 'right'
            },
            'transition': {'duration': 300, 'easing': 'cubic-in-out'},
            'pad': {'b': 10, 't': 50},
            'len': 0.9,
            'x': 0.1,
            'y': 0,
            'steps': []
        }

        # make data
        year = 1980
        for continent in continents:
            dataset_by_year = dataset[dataset['date'] == year]
            dataset_by_year_and_cont = dataset_by_year[dataset_by_year['Country'] == continent]

            data_dict = go.Scatter(
                    x= list(dataset_by_year_and_cont['inactivations']),
                    y= list(dataset_by_year_and_cont['incorporations']),
                    mode= 'markers',
                    text= list(dataset_by_year_and_cont['Country']),
                    marker = dict (
                        sizemode= 'area',
                        size= list(dataset_by_year_and_cont['active offshores'])
                    ),
                    name= continent
                )
            figure['data'].append(data_dict)

        # make frames
        for year in years:
            frame = {'data': [], 'name': str(year)}
            for continent in continents:
                dataset_by_year = dataset[dataset['date'] == int(year)]
                dataset_by_year_and_cont = dataset_by_year[dataset_by_year['Country'] == continent]
                data_dict = go.Scatter(
                    x= list(dataset_by_year_and_cont['inactivations']),
                    y= list(dataset_by_year_and_cont['incorporations']),
                    mode= 'markers',
                    text= list(dataset_by_year_and_cont['Country']),
                    marker = dict (
                        sizemode= 'area',
                        size= list(dataset_by_year_and_cont['active offshores'])
                    ),
                    name= continent
                )
                frame['data'].append(data_dict)

            figure['frames'].append(frame)
            slider_step = {'args': [
                [year],
                {'frame': {'duration': 300, 'redraw': True},
                 'mode': 'immediate',
               'transition': {'duration': 300}}
             ],
             'label': year,
             'method': 'animate'}
            sliders_dict['steps'].append(slider_step)


        figure['layout']['sliders'] = [sliders_dict]
        iplot(figure)


def visualize_time_series3(countries_frame2):
    jurisd = pd.concat(countries_frame2)
    jurisd = jurisd.reset_index() 
    jurisdictions = jurisd.jurisdiction.unique()
    countries_frame = []
    for jur in jurisdictions:
        countries_frame.append(jurisd[jurisd['jurisdiction'] == jur])
    for time_frame in countries_frame: 
        dataset = time_frame.copy().reset_index()
        c = dataset['jurisdiction'][0]
        years_from_col = set(dataset['date'])
        years_ints = sorted(list(years_from_col))
        years = [str(year) for year in years_ints]
        years = years[:-1]
        continents = []
        for continent in dataset['Country']:
            if continent not in continents: 
                continents.append(continent)
        # make figure
        figure = {
            'data': [],
            'layout': dict(title = '<b>'+ c +' offshores account by Country</b>'),
            'frames': []
        }

        # fill in most of layout
        figure['layout']['xaxis'] = {'range':[-3, len(continents)],'title': 'Countries', 'ticktext':continents, 'showticklabels':True, 'type':'category'}
        figure['layout']['yaxis'] = {'range':[-50, max(dataset['incorporations']) + 50],'title': 'Incorporations', 'separatethousands':True}
        figure['layout']['hovermode'] = 'compare'
        figure['layout']['sliders'] = {
            'args': [
                'transition', {
                    'duration': 400,
                    'easing': 'cubic-in-out'
                }
            ],
            'initialValue': '1980',
            'plotlycommand': 'animate',
            'values': years,
            'visible': True
        }
        figure['layout']['updatemenus'] = [
            {
                'buttons': [
                    {
                        'args': [None, {'frame': {'duration': 500, 'redraw': False},
                                 'fromcurrent': True, 'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}],
                        'label': 'Play',
                        'method': 'animate'
                    },
                    {
                        'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate',
                        'transition': {'duration': 0}}],
                        'label': 'Pause',
                        'method': 'animate'
                    }
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 87},
                'showactive': False,
                'type': 'buttons',
                'x': 0.1,
                'xanchor': 'right',
                'y': 0,
                'yanchor': 'top'
            }
        ]

        sliders_dict = {
            'active': 0,
            'yanchor': 'top',
            'xanchor': 'left',
            'currentvalue': {
                'font': {'size': 20},
                'prefix': 'Year:',
                'visible': True,
                'xanchor': 'right'
            },
            'transition': {'duration': 300, 'easing': 'cubic-in-out'},
            'pad': {'b': 10, 't': 50},
            'len': 0.9,
            'x': 0.1,
            'y': 0,
            'steps': []
        }

        # make data
        year = 1980
        for i, continent in enumerate(continents):
            dataset_by_year = dataset[dataset['date'] == year]
            dataset_by_year_and_cont = dataset_by_year[dataset_by_year['Country'] == continent]

            data_dict = go.Scatter(
                    x= list(dataset_by_year_and_cont['Country']),
                    y= list(dataset_by_year_and_cont['incorporations']),
                    mode= 'markers',
                    text= list(dataset_by_year_and_cont['Country']),
                    marker = dict (
                        sizemode= 'area',
                        size= list(dataset_by_year_and_cont['active offshores'])
                    ),
                    name= continent,
                    xaxis='x'+str(i), 
                    yaxis='y'+str(i)
                )
            
            figure['data'].extend(go.Data([data_dict]))

        # make frames
        # for year in years:
        #     frame = {'data': [], 'name': str(year)}
        #     for continent in continents:
        #         dataset_by_year = dataset[dataset['date'] == int(year)]
        #         dataset_by_year_and_cont = dataset_by_year[dataset_by_year['Country'] == continent]
        #         data_dict = go.Scatter(
        #             x= list(dataset_by_year_and_cont['Country']),
        #             y= list(dataset_by_year_and_cont['incorporations']),
        #             mode= 'markers',
        #             text= list(dataset_by_year_and_cont['Country']),
        #             marker = dict (
        #                 sizemode= 'area',
        #                 size= list(dataset_by_year_and_cont['active offshores'])
        #             ),
        #             name= continent
        #         )
        #         frame['data'].append(data_dict)

        #     figure['frames'].append(frame)

            slider_step = {'args': [
                [year],
                {'frame': {'duration': 300, 'redraw': True},
                 'mode': 'immediate',
               'transition': {'duration': 300}}
             ],
             'label': year,
             'method': 'animate'}
            sliders_dict['steps'].append(slider_step)

        # The graph's yaxis2 MUST BE anchored to the graph's xaxis2 and vice versa
        # Update the margins to add a title and see graph x-labels. 
        # Update the height because adding a graph vertically will interact with
        # the plot height calculated for the table
        figure['layout']['height'] = 800
        figure['layout']['sliders'] = [sliders_dict]
        iplot(figure)


def visualize_time_series4(countries_frame2):
    jurisd = pd.concat(countries_frame2)
    jurisd = jurisd.reset_index() 
    jurisdictions = jurisd.jurisdiction.unique()
    countries_frame = []
    for jur in jurisdictions:
        countries_frame.append(jurisd[jurisd['jurisdiction'] == jur])
    for time_frame in countries_frame: 
        dataset = time_frame.copy().reset_index()
        c = dataset['jurisdiction'][0]
        years_from_col = set(dataset['date'])
        years_ints = sorted(list(years_from_col))
        years = [str(year) for year in years_ints]
        years = years[:-1]
        continents = []
        for continent in dataset['Country']:
            if continent not in continents: 
                continents.append(continent)
        # make figure
        figure = {
            'data': [],
            'layout': dict(title = '<b>'+ c +' offshores account by Country</b>'),
            'frames': []
        }

        # fill in most of layout

        #figure['layout']['xaxis'] = {'range':[int(min(years)) - 3, int(max(years)) + 3],'title': 'Jurisdictions'}
        figure['layout']['xaxis'] = {'range':[-300, max(dataset['inactivations']) + 300],'title': 'Inactivations'}
        figure['layout']['yaxis'] = {'range':[-300, max(dataset['incorporations']) + 300],'title': 'Incorporations'}
        figure['layout']['hovermode'] = 'compare'
        figure['layout']['sliders'] = {
            'args': [
                'transition', {
                    'duration': 400,
                    'easing': 'cubic-in-out'
                }
            ],
            'initialValue': '1980',
            'plotlycommand': 'animate',
            'values': years,
            'visible': True
        }
        figure['layout']['updatemenus'] = [
            {
                'buttons': [
                    {
                        'args': [None, {'frame': {'duration': 500, 'redraw': False},
                                 'fromcurrent': True, 'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}],
                        'label': 'Play',
                        'method': 'animate'
                    },
                    {
                        'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate',
                        'transition': {'duration': 0}}],
                        'label': 'Pause',
                        'method': 'animate'
                    }
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 87},
                'showactive': False,
                'type': 'buttons',
                'x': 0.1,
                'xanchor': 'right',
                'y': 0,
                'yanchor': 'top'
            }
        ]

        sliders_dict = {
            'active': 0,
            'yanchor': 'top',
            'xanchor': 'left',
            'currentvalue': {
                'font': {'size': 20},
                'prefix': 'Year:',
                'visible': True,
                'xanchor': 'right'
            },
            'transition': {'duration': 300, 'easing': 'cubic-in-out'},
            'pad': {'b': 10, 't': 50},
            'len': 0.9,
            'x': 0.1,
            'y': 0,
            'steps': []
        }

        # make data
        year = 1980
        for continent in continents:
            dataset_by_year = dataset[dataset['date'] == year]
            dataset_by_year_and_cont = dataset_by_year[dataset_by_year['Country'] == continent]

            data_dict = go.Scatter(
                    x= list(dataset_by_year_and_cont['inactivations']),
                    y= list(dataset_by_year_and_cont['incorporations']),
                    mode= 'markers',
                    text= list(dataset_by_year_and_cont['Country']),
                    marker = dict (
                        sizemode= 'area',
                        sizeref=30,
                        size= list(dataset_by_year_and_cont['active offshores'])
                    ),
                    name= continent
                )
            figure['data'].append(data_dict)

        # make frames
        for year in years:
            frame = {'data': [], 'name': str(year)}
            for continent in continents:
                dataset_by_year = dataset[dataset['date'] == int(year)]
                dataset_by_year_and_cont = dataset_by_year[dataset_by_year['Country'] == continent]
                data_dict = go.Scatter(
                    x= list(dataset_by_year_and_cont['inactivations']),
                    y= list(dataset_by_year_and_cont['incorporations']),
                    mode= 'markers',
                    text= list(dataset_by_year_and_cont['Country']),
                    marker = dict (
                        sizemode= 'area',
                        sizeref=30,
                        size= list(dataset_by_year_and_cont['active offshores'])
                    ),
                    name= continent
                )
                frame['data'].append(data_dict)

            figure['frames'].append(frame)
            slider_step = {'args': [
                [year],
                {'frame': {'duration': 300, 'redraw': True},
                 'mode': 'immediate',
               'transition': {'duration': 300}}
             ],
             'label': year,
             'method': 'animate'}
            sliders_dict['steps'].append(slider_step)


        figure['layout']['sliders'] = [sliders_dict]
        div = plot(figure, output_type='div')
        f = open(c+'.html','w')
        f.write(div)
        f.close()