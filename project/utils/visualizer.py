import pandas as pd
import seaborn as sns

from utils import preprocessing

from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go
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
    url = 'https://restcountries.eu/rest/v2/'
    actives_path = r'csv/cash_flows_'+feat+'.csv'
    restcountries, nametoid = preprocessing.build_json_from_api(url)
    actives_flows = pd.read_csv(actives_path,low_memory=False)
    actives_flows = preprocessing.parse_countries(actives_flows)
    actives_flows_by_country = actives_flows.groupby('Country').sum().reset_index()
    actives_flows_by_country = preprocessing.add_details(actives_flows_by_country, restcountries)
    country_df = actives_flows[actives_flows['Country'] == nametoid[country]]
    total_offshores = 0
    labels = []
    values = []
    flows_path = []
    max_value = country_df[str(year)].max()
    for i, row in country_df.iterrows():
        if not pd.isnull(row['Country']) and not pd.isnull(row['jurisdiction']) and not pd.isnull(row[str(year)]):
            coord = [restcountries[int(row['Country'])]['latlng'], restcountries[int(row['jurisdiction'])]['latlng']]
            total_offshores = total_offshores + row[str(year)]
            labels.append(restcountries[int(row['jurisdiction'])]['name'])
            values.append(row[str(year)])
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

    fig = dict( data=flows_path + __get_data(actives_flows_by_country, year), layout=__get_layout() )
    iplot( fig, validate=False, filename='d3-world-map.html')
    trace = go.Pie(labels=labels, 
                   values=values,
                  textfont=dict(size=20),)
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


def __get_layout():
    """
    ! private function. This function is created to obtain the layout of the choropleth map
    :return: the layout of the choropleth map.
    """
    layout = dict(
        title = 'Active offshores per country <br> <br> Source:\
                <a href="https://www.icij.org/">\
                International Consortium of Investigative Journalists</a>',
        geo = dict(
            projection = dict(
                type = 'Mercator'
            ),
            resolution='50',
        )
    )
    return layout